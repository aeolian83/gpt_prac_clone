import streamlit as st
from datetime import datetime

today = datetime.today().strftime("%H:%M:%S")

st.title(today)

st.write("hello")

a = [1, 2, 3, 4]

b = {"x": 1}


a

b


model = st.selectbox("Choose your model", ("GPT-3", "GPT-4"))

if model == "GPT-3":
    st.write("cheap")
else:
    st.write("Not cheap")
    name = st.text_input("What is your name?")
    st.write(name)

    value = st.slider(
        "temperature",
        min_value=0.1,
        max_value=1.0,
    )
    st.write(value)
