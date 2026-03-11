import streamlit as st
import requests

st.title("Knowledge Base Chatbot")

question = st.text_input("Ask a question")

if st.button("Ask"):

    response = requests.post(
        "http://localhost:8000/ask",
        json={"question": question}
    )

    data = response.json()
    if "answer" in data:
        st.write(data["answer"])
    else:
        st.error(data.get("error", "Something went wrong"))