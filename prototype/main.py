import click
from langchain.schema import Document
from weaviate_search import HybridSearchByWeaviate

from dotenv import load_dotenv
load_dotenv()


# markdown file loader
def markdown_loader(dir):
    from langchain.document_loaders import DirectoryLoader
    from langchain.document_loaders import TextLoader

    loader = DirectoryLoader(dir, glob="*.md", loader_cls=TextLoader)

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
    
    return md_header_splits

def ingest_data(directory, prefix="*.md"):
    # load document from makedown files
    docs = markdown_loader(directory)
    
    # ingest document to retrieval engine
    hybrid_retriever = HybridSearchByWeaviate()
    hybrid_retriever.ingest_docments(docs)
    
    return hybrid_retriever

def qna_with_data(question):
    
    # chat with the retrieval
    hybrid_retriever = HybridSearchByWeaviate()
    search_result = hybrid_retriever.search(question)
    if len(search_result) == 0:
        return "没有发现与问题相关的原文内容"
    print(search_result)

    # answer the question
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import Document
    from langchain.chains.question_answering import load_qa_chain
    
    chat = ChatOpenAI(model_name='gpt-3.5-turbo-16k')
    chain = load_qa_chain(chat, chain_type="stuff")
    
    #TODO only first one be leveraged
    answer = chain.run(input_documents=search_result[0:2], question=question)            
    
    print(answer)
    
    return answer
    
    pass

@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(["ingest", "query"], case_sensitive=False),
)

@click.option("--content", "-c")
def main(task:str, content:str):
    # retriever = None
    if task == "ingest":
        ingest_data(content)
    elif task == "query":
        qna_with_data(content)
        pass
    else:
        print("Please add '-t ingest' or '-t query' to your command")

if __name__ == '__main__' :
    
    main()
    
    pass    