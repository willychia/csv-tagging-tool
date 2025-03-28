import streamlit as st

def get_filtered_df(keyword, exclude_keywords, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special):
    _df = st.session_state['df'].copy()

    # 多關鍵字交集篩選（處理 NaN 並忽略大小寫）
    keywords = [k.strip() for k in keyword.split(",") if k.strip()]
    for kw in keywords:
        _df = _df[_df['title'].fillna("").str.contains(kw, case=False)]
        
    exclude_keywords = [k.strip() for k in exclude_keywords.split(",") if k.strip()]
    for kw in exclude_keywords:
        _df = _df[~_df['title'].fillna("").str.contains(kw, case=False)]

    if selected_brands:
        _df = _df[_df['brand'].isin(selected_brands)]
    if filter_empty_feature:
        _df = _df[_df['Feature'].isna() | (_df['Feature'].str.strip() == '')]
    if filter_empty_subject:
        _df = _df[_df['Subject'].isna() | (_df['Subject'].str.strip() == '')]
    if filter_empty_special:
        _df = _df[_df['Special'].isna() | (_df['Special'].str.strip() == '')]
    return _df
