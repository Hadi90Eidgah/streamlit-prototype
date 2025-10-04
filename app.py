import streamlit as st

st.title("🚀 Streamlit Prototype App")
st.write("This app is running on Streamlit Cloud — no local setup needed!")

name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! 👋")
