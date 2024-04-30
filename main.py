import streamlit as st
import pandas as pd
from moa_search import moa_query

st.title("政策搜索")
options = st.multiselect("请选择搜索范围", 
                         ["全国", "山东"],
                         ["全国"]
                         )
col1, col2 = st.columns([0.7, 0.3])
with col1:
    query = st.text_input("请输入搜索词")
with col2:
    number = st.number_input("显示条数", value=2, step=1, placeholder="请输入数字")

col1, col2= st.columns(2)
with col1:
    search_button = st.button("搜索")
with col2:
    clear_button = st.button("清空")
if search_button:
    news = moa_query(query, max_pages=number)
    df = pd.DataFrame(news)
    # st.sidebar.text("搜索结果")
    st.dataframe(df,
                column_config={
                    "title": "标题",
                    "link": st.column_config.LinkColumn("链接"),
                    "date": "日期",
                },
                hide_index=True
                )
            
