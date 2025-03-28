import streamlit as st
import pandas as pd

def upload_files():
    upload_left, upload_right = st.columns(2)

    with upload_left:
        st.markdown("### 📂 上傳新檔案")
        new_file = st.file_uploader("請上傳新檔案", type=["csv", "xlsx"], key="new")
        if new_file:
            st.session_state['new_df'] = pd.read_csv(new_file) if new_file.name.endswith(".csv") else pd.read_excel(new_file)

    with upload_right:
        st.markdown("### 📂 上傳舊檔案")
        old_file = st.file_uploader("請上傳舊檔案", type=["csv", "xlsx"], key="old")
        if old_file:
            st.session_state['old_df'] = pd.read_csv(old_file) if old_file.name.endswith(".csv") else pd.read_excel(old_file)

def normalize_columns():
    for df_part in [st.session_state['new_df'], st.session_state['old_df']]:
        if df_part is not None:
            for col in ['title', 'brand']:
                if col in df_part.columns:
                    df_part[col] = df_part[col].astype(str).str.lower()

def merge_data():
    new_df = st.session_state['new_df']
    old_df = st.session_state['old_df']

    if new_df is not None:
        for col in ['Feature', 'Subject', 'Special']:
            if col not in new_df.columns:
                new_df[col] = ""

    if new_df is not None and old_df is not None:
        merged_df = new_df.copy()
        old_lookup = old_df.set_index('asin')

        for idx, row in merged_df.iterrows():
            asin = row['asin']
            if asin in old_lookup.index:
                for col in ['Feature', 'Subject', 'Special']:
                    merged_df.at[idx, col] = old_lookup.at[asin, col]
                old_df = old_df[old_df['asin'] != asin]

        st.session_state['df'] = pd.concat([merged_df, old_df], ignore_index=True)
    elif new_df is not None:
        st.session_state['df'] = new_df.copy()
    elif old_df is not None:
        st.session_state['df'] = old_df.copy()
