import time
import streamlit as st

st.title("DocumentGPT")

with st.chat_message("human"):
    st.write("Hellooooooo")

with st.chat_message("AI"):
    st.write("how are you")

with st.status("Embedding file..."):
    time.sleep(3)
    st.write("Getting the file")

st.chat_input("Send a message to the AI")
