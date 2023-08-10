

import streamlit as st
from streamlit_chat import message
import io
import asyncio
from weaviate_search import HybridSearchByWeaviate


async def main():
    
    async def conversational_chat(query):
        result = qa({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        # print("Log: ")
        # print(st.session_state['history'])
        return result["answer"]

    if 'history' not in st.session_state:
        st.session_state['history'] = []


    #Creating the chatbot interface
    st.title("SAP insights")

    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    uploaded_file = st.file_uploader("选择一个SAP操作手册", type="md")
    
    hybrid_retriever = HybridSearchByWeaviate()

    if uploaded_file is not None:

        with st.spinner("Processing..."):
        # Add your code here that needs to be executed
            # uploaded_file.seek(0)
            # file = uploaded_file.read()
            # # pdf = PyPDF2.PdfFileReader()
            # vectors = await getDocEmbeds(io.BytesIO(file), uploaded_file.name)
            # qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=vectors.as_retriever(), return_source_documents=True)
            
            from langchain.document_loaders import TextLoader
            loader = TextLoader(uploaded_file)
            markdown_document = loader.load()

            headers_to_split_on = [
                ("#", "Header_1"),
                # ("##", "Header_2"),
                # ("###", "Header_3"),
            ]

            # MD splits
            from langchain.text_splitter import MarkdownHeaderTextSplitter
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            
            #TODO Only support the first document 
            md_header_splits = markdown_splitter.split_text(markdown_document[0].page_content)
            
            hybrid_retriever.ingest_docments(md_header_splits)
            
            qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=hybrid_retriever.as_retriever(), return_source_documents=True)


        st.session_state['ready'] = True

    st.divider()

    if st.session_state['ready']:

        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["准备就绪! 让AI来帮助您更好的使用SAP系统" + uploaded_file.name]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["你好!"]

        # container for chat history
        response_container = st.container()

        # container for text box
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="财务预支应该如何处理", key='input')
                submit_button = st.form_submit_button(label='发送')

            if submit_button and user_input:
                output = await conversational_chat(user_input)
                # chain = load_qa_chain(chat, chain_type="stuff")
                # answer = chain.run(input_documents=search_result[0:2], question=question)            
                
                
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


if __name__ == "__main__":
    asyncio.run(main())