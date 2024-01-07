# from dotenv import load_dotenv

# load_dotenv()

import time
import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings

# 벡터 스토어에 따라 성능이 달라지기도 한다.
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

st.set_page_config(page_title="DcumentGPT", page_icon="📜")

st.title("DocumentGPT")

st.markdown(
    """
Welcome!
            
Use this chatbot to ask question to an AI about your files!
"""
)

file = st.file_uploader("Upload a .txt .pdf .docx file", type=["pdf", "txt", "docx"])

if file:
    st.write(file)
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    st.write(file_content, file_path)
    with open(file_path, "wb") as f:
        f.write(file_content)

    cache_dir = LocalFileStore(f"./.cache/embeddings/{file.name}")

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader("./files/chapter_one.txt")
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings()
    cache_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings,
        cache_dir,
    )
    vectorstore = FAISS.from_documents(docs, cache_embeddings)
    retriever = vectorstore.as_retriever()
    docs = retriever.invoke("ministry of truth")
    st.write(docs)
