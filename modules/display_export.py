import streamlit as st
import pandas as pd
import io

def render_table(filtered_df):
    return st.data_editor(
        filtered_df,
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
