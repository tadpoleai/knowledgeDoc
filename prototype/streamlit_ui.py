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
from pathlib import Path
import tempfile
from prompt_repos import prompt_template0 as prompt_template

from dotenv import load_dotenv
load_dotenv()

# docs prefix path
docs_prefix = os.getenv("IMG_PATH_PREFIX", "docs")
print(f'docs_prefix:{docs_prefix}')


QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chat = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0)
chain = load_qa_chain(chat, chain_type="stuff", prompt=QA_PROMPT)

async def main():
    
    async def conversational_chat(query):
        result = qa({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))

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
        
        if uploaded_file:

            with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            with st.spinner("Processing..."):
                from langchain.document_loaders import TextLoader
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

                if 'hybrid_retriever' in locals():
                    print(f'用户的问题是：{user_input}')
                    search_result = hybrid_retriever.search(user_input)
                    
                    # List to store image paths for later rendering
                    img_paths = []
                    
                    if len(search_result) == 0:
                        output = "很抱歉，没有发现与问题相关的原文内容"
                        modified_output = output
                    else:
                        output = chain.run(input_documents=search_result[0:2], question=user_input) 
                        
                        # Assuming 'output' contains the answer in Markdown format
                        # Extract <img> tags from the 'output'
                        soup = BeautifulSoup(output, 'html.parser')
                        img_tags = soup.find_all('img')

                        for index, tag in enumerate(img_tags):
                            # Extract the image path                            
                            img_path = Path(docs_prefix) / tag['src']
                            img_paths.append(str(img_path))
                            
                            # Create a reference link in Markdown format
                            reference_link = f"查看第{index + 1}张图片"
                            
                            # Replace the original <img> tag with the Markdown image link
                            tag.replace_with(reference_link)

                        # Convert the modified soup back to string for display
                        modified_output = str(soup)
                        print(f'AI的答案是：{modified_output}')
                    
                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(modified_output)
                    st.session_state['image_ref'].append(img_paths)
                    

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message('AI', key=str(i), avatar_style="fun-emoji")

                    # Display the modified answer
                    st.markdown(st.session_state["generated"][i])
                    
                    if st.session_state["image_ref"]:
                        img_paths = st.session_state["image_ref"][i]
                        
                    else:
                        img_paths = []

                    # Display images at the end of the answer                    
                    for index, img_path in enumerate(img_paths):
                        # st.image(img_path, use_column_width=True, caption=f"图片 {index + 1}")
                        st.image(img_path, use_column_width=True, width=100, caption=f"图片 {index + 1} (点击右上角查看完整图像)")

                    

if __name__ == "__main__":
    asyncio.run(main())
