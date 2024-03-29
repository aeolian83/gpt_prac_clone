import streamlit as st

from langchain.chat_models import ChatOllama
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings, CacheBackedEmbeddings

# 벡터 스토어에 따라 성능이 달라지기도 한다.
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.callbacks.base import BaseCallbackHandler

st.set_page_config(page_title="PrivateGPT", page_icon="😶‍🌫️")


# st.session_state["messages"] = []
# if "messages" not in st.session_state:
#     st.session_state["messages"] = []
class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)


# falcon model is not work
with st.sidebar:
    model = st.selectbox("Choose your model", ("mistral:latest", "falcon:latest"))

llm = ChatOllama(
    model=model,
    temperature=0.1,
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ],
)


@st.cache_data(show_spinner="Embedding file...")
def embed_file(file):
    file_content = file.read()
    file_path = f"./.cache/private_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    cache_dir = LocalFileStore(f"./.cache/private_embeddings/{file.name}")
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OllamaEmbeddings(model=model)
    cache_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings,
        cache_dir,
    )
    vectorstore = FAISS.from_documents(docs, cache_embeddings)
    retriever = vectorstore.as_retriever()

    return retriever


def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


def paint_history():
    for message in st.session_state["messages"]:
        send_message(message["message"], message["role"], save=False)


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             """
# Answer the question using ONLY the followin context. If you don't know the answer
# just say you don't know. DON'T make anything up.

# Context: {context}
# """,
#         ),
#         ("human", "{question}"),
#     ]
# )

# st.title("DocumentGPT")

# st.markdown(
#     """
# Welcome!

# Use this chatbot to ask question to an AI about your files!

# Upload your files on the sidebar.
# """
# )

prompt = ChatPromptTemplate.from_template(
    """Answer the question using ONLY the followin context and not your training data. 
        If you don't know the answer just say you don't know. DON'T make anything up.

Context: {context}
Question: {question}
"""
)

st.title("DocumentGPT")

st.markdown(
    """
Welcome!
            
Use this chatbot to ask question to an AI about your files!

Upload your files on the sidebar.
"""
)


with st.sidebar:
    file = st.file_uploader(
        "Upload a .txt .pdf .docx file", type=["pdf", "txt", "docx"]
    )

if file:
    retriever = embed_file(file)

    send_message("I'm ready Ask away!", "ai", save=False)
    paint_history()

    message = st.chat_input("Ask anythin about your file....")

    if message:
        send_message(message, "human")
        chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
        )
        with st.chat_message("ai"):
            response = chain.invoke(message)
else:
    st.session_state["messages"] = []
