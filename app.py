# app.py
import streamlit as st
import pandas as pd

from modules.page import set_page, init_session_state
from modules.data_io import upload_files, normalize_and_add_columns, merge_data
from modules.data_ops import get_filtered_df
from modules.display_export import render_table, export_data

# === 初始化頁面與狀態 ===
set_page()
init_session_state()

# === 上傳與合併資料 ===
upload_files()
normalize_and_add_columns()

if st.button("🔄 載入新舊檔案並合併"):
    merge_data()
    st.success("✅ 新舊資料已成功合併！")


if st.session_state['df'] is None:
    st.info("請先上傳並載入檔案後再進行操作。")
    st.stop()

df = st.session_state['df']

# === 篩選條件 ===
left, right = st.columns(2)

with left:
    left_title_1, left_title_2 = st.columns(2)
    with left_title_1:
        st.markdown("### 🔍 篩選資料")
    with left_title_2:
        if st.button("🔄 清除篩選"):
            st.session_state["filter_empty_feature"] = False
            st.session_state["filter_empty_subject"] = False
            st.session_state["filter_empty_special"] = False
            st.session_state["filter_keyword"] = ""
            st.session_state["exclude_keyword"] = ""
            st.session_state["filter_feature"] = ""
            st.session_state["filter_subject"] = ""
            st.session_state["filter_special"] = ""
            st.session_state["filter_brands"] = []
    keyword = st.text_input("Title 篩選", key="filter_keyword").lower()
    exclude_keywords = st.text_input("Title 排除", key="exclude_keyword").lower()
    feature_filter = st.text_input("Feature 篩選", key="filter_feature")
    subject_filter = st.text_input("Subject 篩選", key="filter_subject")
    special_filter = st.text_input("Special 篩選", key="filter_special")
    selected_brands = st.multiselect("Brand 篩選", df['brand'].dropna().unique(), key="filter_brands")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_empty_feature = st.checkbox("No Feature", key="filter_empty_feature")
    with col2:
        filter_empty_subject = st.checkbox("No Subject", key="filter_empty_subject")
    with col3:
        filter_empty_special = st.checkbox("No Special", key="filter_empty_special")

filtered_df = get_filtered_df(keyword, exclude_keywords, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special, feature_filter, subject_filter, special_filter)
selected_rows = pd.DataFrame()

# === 標籤新增/刪除 ===
with right:
    st.markdown("### 🏷️ 新增或刪除標籤")
    tag_column = st.selectbox("選擇要新增/刪除的標籤欄位", ['Feature', 'Subject', 'Special'], key = "tag_column")
    new_tags_input = st.text_input("輸入要新增的標籤（可多個，用逗號分隔）", key=f"add_{tag_column}")
    remove_tags_input = st.text_input("（可選）輸入要刪除的標籤（可多個，用逗號分隔）", key=f"remove_{tag_column}")

    if st.button("✔️ 套用標籤變更"):
        add_tags = set(t.strip() for t in new_tags_input.split(",") if t.strip())
        remove_tags = set(t.strip() for t in remove_tags_input.split(",") if t.strip())

        def modify(cell):
            existing = set(map(str.strip, str(cell).split(","))) if pd.notna(cell) and cell.strip() else set()
            updated = (existing.union(add_tags)).difference(remove_tags)
            sorted_tags = sorted(updated)
            return ", ".join(sorted_tags) if sorted_tags else ""

        for idx in filtered_df.index:
            original_value = st.session_state['df'].at[idx, tag_column]
            new_value = modify(original_value)
            st.session_state['df'].at[idx, tag_column] = new_value

        filtered_df = get_filtered_df(keyword, exclude_keywords, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special, feature_filter, subject_filter, special_filter)
        st.success(f"已更新 {tag_column} 標籤")

    # === 快速標籤功能 ===
    st.markdown("### ⚡ 快速新增標籤")
    quick_col, quick_input = st.columns([1, 3])
    with quick_col:
        quick_tag_column = st.selectbox("選擇標籤欄位", ['Feature', 'Subject', 'Special'], key="quick_tag_column")
    with quick_input:
        quick_tag_value = st.text_input("輸入關鍵字並套用為標籤（會自動套用到 title 含該字詞的資料）", key="quick_tag_value")

    if quick_tag_value.strip():
        keyword = quick_tag_value.strip().lower()
        match_df = st.session_state['df'][st.session_state['df']['title'].str.contains(keyword, na=False)]

        def add_quick_tag(cell):
            existing = set(map(str.strip, str(cell).split(","))) if pd.notna(cell) and cell.strip() else set()
            existing.add(keyword)
            return ", ".join(sorted(existing))

        for idx in match_df.index:
            original = st.session_state['df'].at[idx, quick_tag_column]
            st.session_state['df'].at[idx, quick_tag_column] = add_quick_tag(original)

        filtered_df = get_filtered_df(keyword, exclude_keywords, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special, feature_filter, subject_filter, special_filter)
        st.success(f"已將 '{keyword}' 新增至 {quick_tag_column} 中，共 {len(match_df)} 筆")

    # === 刪除目前篩選資料 ===
    st.markdown("### 🪚 刪除目前篩選結果")
    if st.button("🗑️ 刪除目前篩選結果中所有資料"):
        asins_to_delete = filtered_df['asin']
        st.session_state['df'] = st.session_state['df'][~st.session_state['df']['asin'].isin(asins_to_delete)]
        filtered_df = get_filtered_df(keyword, exclude_keywords, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special, feature_filter, subject_filter, special_filter)
        filtered_df.insert(0, "✔", False)
        st.success(f"已刪除 {len(asins_to_delete)} 筆資料")

st.markdown("---")
st.subheader(f"📊 篩選與更新結果（共 {len(filtered_df)} 筆）")
edited_df = render_table(filtered_df)

# === 標籤統計顯示模組 ===
st.markdown("### 🧮 標籤統計")

def get_tag_count_series(column_name):
    all_tags = st.session_state['df'][column_name].dropna().astype(str).str.split(",")
    flat_tags = [tag.strip() for sublist in all_tags for tag in sublist if tag.strip()]
    return pd.Series(flat_tags).value_counts()

def render_tag_table(tag_series, column_title, session_key_prefix):
    tags_df = tag_series.reset_index()
    tags_df.columns = ["標籤", "出現次數"]

    total_pages = (len(tags_df) - 1) // 10 + 1
    current_page = st.session_state.get(f"{session_key_prefix}_page", 1)

    col = st.container()
    with col:
        st.markdown(f"#### {column_title}")
        start_idx = (current_page - 1) * 10
        end_idx = start_idx + 10
        st.table(tags_df.iloc[start_idx:end_idx])

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if total_pages > 1:
                new_page = st.slider("頁碼", 1, total_pages, current_page, key=f"{session_key_prefix}_slider")
                st.session_state[f"{session_key_prefix}_page"] = new_page
            else:
                st.markdown("頁數：1")
                st.session_state[f"{session_key_prefix}_page"] = 1


# 三欄並排顯示
col_feature, col_subject, col_special = st.columns(3)

with col_feature:
    feature_counts = get_tag_count_series("Feature")
    render_tag_table(feature_counts, "Feature 標籤統計", "feature")

with col_subject:
    subject_counts = get_tag_count_series("Subject")
    render_tag_table(subject_counts, "Subject 標籤統計", "subject")

with col_special:
    special_counts = get_tag_count_series("Special")
    render_tag_table(special_counts, "Special 標籤統計", "special")

st.markdown("---")
export_data()
