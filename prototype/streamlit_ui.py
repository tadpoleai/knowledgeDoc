import streamlit as st
from streamlit_chat import message
import io
import asyncio
from weaviate_search import HybridSearchByWeaviate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import re
import os
from bs4 import BeautifulSoup

import tempfile

from dotenv import load_dotenv
load_dotenv()

# prompt_template = """你是一个有用的 AI 助手。请使用以下上下文信息回答最后的问题。
# 如果你不知道答案，只需说你不知道。不要试图编造答案。
# 以 markdown 形式输出答案

# {context}

# 问题：{question}
# 回答:"""

# prompt_template = """你是一个有用的 AI 助手。请使用以下上下文信息回答最后的问题。
# 如果你不知道答案，只需说你不知道。不要试图编造答案。
# 以 markdown 形式输出答案, 你的回答中保留context中的图像超链接

# {context}

# 问题：{question}
# 图片：{images}
# 回答:"""


prompt_template = """
您是一个专业的AI助手，专门为用户提供详细、结构化的答案。请根据以下文档内容回答用户的问题：“{question}”。请尽量按照以下示例答案的格式进行组织，‘查看图片'部分一定保留<img>：

示例答案：
生产订单余额检查：
- 使用事务代码：S_ALR_87013127
- 查看图片：<img src="./9/media/image103.png"/>
- 订单类型限制为HP*，期间输入当期，格式选择/Z001.
- 查询输出中的“总的实际成本”应该等于在制品金额。如果不存在未完工订单，该金额应该等于零。

科目余额检查：
- 使用事务代码：ZFI020
- 查看图片：<img src="./9/media/image105.png"/>
- 输入相关字段信息，如公司代码、年度、会计期间等。
- 点击执行，查看图片：<img src="./9/media/image106.png"/>
- 查看列“本期金额”的合计数等于零，则生产成本和制造费用全部结清，生产成本月结完成无误。

{context}

问题：“{question}”
"""

QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chat = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0)
chain = load_qa_chain(chat, chain_type="stuff", prompt=QA_PROMPT)

async def main():
    
    async def conversational_chat(query):
        result = qa({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        # print("Log: ")
        # print(st.session_state['history'])
        return result["answer"]

    if 'history' not in st.session_state:
        st.session_state['history'] = []
        
    if 'image_ref' not in st.session_state:
        st.session_state['image_ref'] = []


    #Creating the chatbot interface
    st.title("SAP insights")
    st.write("""
             本问答系统已初步训练某大型制造企业内部SAP操作手册，可支持您直接问答 \n \n
             同时，可支持您上传新的文档，训练后可实现更准确的问答""")


    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    # 默认选择“否”
    upload_option = st.selectbox("您想上传SAP操作手册吗?", ["否", "是"], index=0)
    
    if upload_option == "是":
        uploaded_file = st.file_uploader("选择一个SAP操作手册", type="md")
        
        # hybrid_retriever = HybridSearchByWeaviate()

        if uploaded_file:

            with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            with st.spinner("Processing..."):
                from langchain.document_loaders import TextLoader
                #uploaded_file.seek(0)
                # file = uploaded_file.read()
                loader = TextLoader(tmp_path)
                markdown_document = loader.load()

                headers_to_split_on = [
                    ("#", "Header_1"),
                    # ("##", "Header_2"),
                    # ("###", "Header_3"),
                ]

                # MD splits
                from langchain.text_splitter import MarkdownHeaderTextSplitter
                markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
                print(f'markdown_document: {markdown_document[0]}')
                
                #TODO Only support the first document 
                md_header_splits = markdown_splitter.split_text(markdown_document[0].page_content)
                
                hybrid_retriever = HybridSearchByWeaviate()
                hybrid_retriever.ingest_docments(md_header_splits)
                
                #qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=hybrid_retriever.as_retriever(), return_source_documents=True)


            st.session_state['ready'] = True
    elif upload_option == "否":
        hybrid_retriever = HybridSearchByWeaviate()
        st.session_state['ready'] = True

    st.divider()

    if 'ready' in st.session_state and st.session_state['ready']:

        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["准备就绪! 让AI来帮助您更好地使用SAP系统"]
            st.session_state['image_ref'] = []
            st.session_state['image_ref'].append([])
            

        if 'past' not in st.session_state:
            st.session_state['past'] = ["你好!"]

        if st.session_state['generated']:
            # container for chat history
            response_container = st.container()

            # container for text box
            container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                default_question = "怎么判断生产成本月结完成无误"
                user_input = st.text_input("Query:", placeholder=default_question, key='input')
                submit_button = st.form_submit_button(label='发送')
                if not user_input:
                    user_input = default_question

            if submit_button and user_input:
                #output = await conversational_chat(user_input)
                # chain = load_qa_chain(chat, chain_type="stuff")
                # answer = chain.run(input_documents=search_result[0:2], question=question)    
                print(f'locals:{locals()}')
                if 'hybrid_retriever' in locals():
                    print(f'用户的问题是：{user_input}')
                    search_result = hybrid_retriever.search(user_input)
                    if len(search_result) == 0:
                        output = "很抱歉，没有发现与问题相关的原文内容"
                    else:
                        print(search_result)
                        
                        # 提取所有的<img>标签
                        # img_tags = []
                        # for doc in search_result[0:2]:
                        #     img_tags.extend(re.findall(r'(<img[^>]+>)', doc.page_content))
                        # print(img_tags)

                        # 将<img>标签合并为一个字符串
                        #img_str = "\n\n".join(img_tags)
                        output = chain.run(input_documents=search_result[0:2], question=user_input) 
                        
                        # 提取所有的<img>标签
                        # img_tags = []
                        # for doc in search_result:
                        #     img_tags.extend(re.findall(r'(<img[^>]+>)', doc.page_content))
                        
                        # # 将<img>标签添加到OpenAI返回的答案中
                        # output += "\n\n" + "\n".join(img_tags)
                        
                        # Assuming 'output' contains the answer in Markdown format
                        # Extract <img> tags from the 'output'
                        soup = BeautifulSoup(output, 'html.parser')
                        img_tags = soup.find_all('img')

                        # List to store image paths for later rendering
                        img_paths = [tag['src'] for tag in img_tags]

                        # Replace <img> tags in the 'output' with "查看图片" text
                        # for tag in img_tags:
                        #     tag.replace_with("查看图片")

                        # Convert the modified soup back to string for display
                        modified_output = str(soup)
                        

                        print(f'output:{output}') 
                        
                        print(f'modified_output:{modified_output}') 
                            
                    
                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(modified_output)
                    st.session_state['image_ref'].append(img_paths)
                    

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    #message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")
                    # 使用st.markdown来显示OpenAI返回的Markdown
                    # st.markdown(st.session_state["generated"][i])

                    # Display the modified answer
                    st.markdown(st.session_state["generated"][i])
                    
                    if st.session_state["image_ref"]:
                        img_paths = st.session_state["image_ref"][i]
                        
                    else:
                        img_paths = []

                    # Display images at the end of the answer
                    for img_path in img_paths:
                        # Use streamlit to display the image, you can adjust the width and use_caption as needed
                        st.image(img_path, use_column_width=True, caption="点击放大")
                    
                    # 使用BeautifulSoup解析Markdown内容
                    # soup = BeautifulSoup(st.session_state["generated"][i], 'html.parser')
                    
                    # # 查找所有的<img>标签
                    # for img_tag in soup.find_all('img'):
                    #     # 获取图片的相对路径
                    #     img_path = img_tag['src']
                    #     # 使用st.image显示图片
                    #     st.image(os.path.join(os.getcwd(), img_path))
                    #     # 从Markdown内容中移除<img>标签
                    #     img_tag.decompose()
                    
                    # # 使用st.markdown显示剩余的Markdown内容
                    # st.markdown(str(soup))


if __name__ == "__main__":
    asyncio.run(main())
