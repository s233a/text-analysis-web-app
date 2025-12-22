import streamlit as st
import jieba
from collections import Counter
import pandas as pd

# 页面配置
st.set_page_config(page_title="简易文本分析工具", page_icon="📝")

# 核心函数（省略，与之前一致）
def calculate_text_stats(input_text):
    # ...（函数内容不变）

def get_top_keywords(pure_text, top_n=10):
    # ...（函数内容不变）

# 页面交互
st.title("📝 简易文本分析Web应用")
user_input = st.text_area("请输入文本", height=200)

if st.button("开始分析"):
    if user_input.strip():
        text_stats = calculate_text_stats(user_input)
        top_keywords = get_top_keywords(text_stats["纯文本内容"])
        
        # 先创建列变量，再使用with语句
        col1, col2 = st.columns(2)  # 必须先执行这行！
        with col1:
            st.subheader("基础统计")
            # ...（col1内容）
        with col2:  # 此时col2已定义，不会报错
            st.subheader("高频关键词")
            # ...（col2内容）
    else:
        st.warning("请输入文本")