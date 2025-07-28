import streamlit as st
import requests

st.set_page_config(page_title="Indium Chatbot", layout="centered")
st.title("🤖 Indium Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post("http://localhost:8000/ask", json={"question": user_input})
        response.raise_for_status()
        answer = response.json().get("answer", "No response received.")
    except Exception as e:
        answer = f"❌ Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})