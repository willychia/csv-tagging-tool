import streamlit as st

def set_page():
    st.set_page_config(page_title="多選標籤工具", layout="wide")
    st.title("📌 CSV / Excel 多選標籤工具")

def init_session_state():
    for key in ['new_df', 'old_df', 'df']:
        if key not in st.session_state:
            st.session_state[key] = None
