import streamlit as st

def get_filtered_df(keyword, selected_brands, filter_empty_feature, filter_empty_subject, filter_empty_special):
    _df = st.session_state['df'].copy()
    if keyword:
        _df = _df[_df['title'].str.contains(keyword, na=False)]
    if selected_brands:
        _df = _df[_df['brand'].isin(selected_brands)]
    if filter_empty_feature:
        _df = _df[_df['Feature'].isna() | (_df['Feature'].str.strip() == '')]
    if filter_empty_subject:
        _df = _df[_df['Subject'].isna() | (_df['Subject'].str.strip() == '')]
    if filter_empty_special:
        _df = _df[_df['Special'].isna() | (_df['Special'].str.strip() == '')]
    return _df
