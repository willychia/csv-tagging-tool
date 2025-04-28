import streamlit as st
import pandas as pd
import io

def calculate_keyword_count(df):
    def count_tags(cell):
        if pd.isna(cell) or cell.strip() == '':
            return 0
        return len([tag.strip() for tag in str(cell).split(",") if tag.strip()])
    
    feature_count = df['Feature'].apply(count_tags)
    subject_count = df['Subject'].apply(count_tags)
    special_count = df['Special'].apply(count_tags)
    
    df['Keyword Count'] = (feature_count * subject_count) + special_count
    return df

def render_table(filtered_df):
    return st.data_editor(
        calculate_keyword_count(filtered_df),
        use_container_width=True,
        disabled=["asin", "title", "brand", "Feature", "Subject", "Special"],
        key="selectable_table"
    )

def export_data():
    output_format = st.radio("選擇匯出格式", ["CSV", "Excel"], horizontal=True)
    if output_format == "CSV":
        csv = st.session_state['df'].to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ 下載 CSV", data=csv, file_name="updated.csv", mime="text/csv")
    else:
        excel_io = io.BytesIO()
        with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
            st.session_state['df'].to_excel(writer, index=False)
        st.download_button("⬇️ 下載 Excel", data=excel_io.getvalue(), file_name="updated.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
