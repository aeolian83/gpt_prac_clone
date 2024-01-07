import time
import streamlit as st

st.set_page_config(page_title="DcumentGPT", page_icon="📜")

st.title("DocumentGPT")

# with st.chat_message("human"):
#     st.write("Helloooooooooo")

# with st.chat_message("ai"):
#     st.write("how are you")

# with st.status("Embedding file....", expanded=True) as status:
#     time.sleep(2)
#     st.write("Getting the file")
#     time.sleep(2)
#     st.write("Embedding the file")
#     time.sleep(2)
#     st.write("Caching the file")
#     status.update(label="Error", state="error")

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})


# st.write(st.session_state["messages"])
for message in st.session_state["messages"]:
    send_message(message["message"], message["role"], save=False)


message = st.chat_input("Send a message to the ai")

if message:
    send_message(message, "human")
    time.sleep(2)
    send_message(f"You said: {message}", "ai")
