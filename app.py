import streamlit as st
import jieba
from collections import Counter
import pandas as pd

# 页面配置
st.set_page_config(page_title="简易文本分析工具", page_icon="📝", layout="centered")

# 停用词表
STOP_WORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它",
    "在", "和", "有", "就", "都", "这", "那", "其"
}

# ---------------------- 核心函数（确保返回DataFrame） ----------------------
def calculate_text_stats(input_text):
    total_with_space = len(input_text)
    pure_text = input_text.replace(" ", "").replace("\n", "")
    total_without_space = len(pure_text)
    return {
        "含空格换行总字符数": total_with_space,
        "无空格换行纯字符数": total_without_space,
        "纯文本内容": pure_text
    }

def get_top_keywords(pure_text, top_n=10):
    """强制返回DataFrame，避免类型错误"""
    try:
        word_list = jieba.lcut(pure_text)
        valid_words = [
            word for word in word_list
            if word not in STOP_WORDS and len(word) > 1
        ]
        if not valid_words:
            return pd.DataFrame(columns=["关键词", "出现次数"])
        word_count = Counter(valid_words)
        return pd.DataFrame(
            word_count.most_common(top_n),
            columns=["关键词", "出现次数"]
        )
    except Exception as e:
        # 捕获任何异常，返回空DataFrame
        return pd.DataFrame(columns=["关键词", "出现次数"])

# ---------------------- 页面交互 ----------------------
st.title("📝 简易文本分析Web应用")
st.divider()

user_input = st.text_area(
    "请输入待分析文本",
    height=200,
    placeholder="示例：今天天气很好，适合出门散步..."
)

if st.button("🚀 开始分析", use_container_width=True):
    if not user_input.strip():
        st.warning("⚠️ 请输入有效文本")
    else:
        text_stats = calculate_text_stats(user_input)
        keyword_df = get_top_keywords(text_stats["纯文本内容"])

        # 验证keyword_df类型（额外保障）
        if not isinstance(keyword_df, pd.DataFrame):
            keyword_df = pd.DataFrame(columns=["关键词", "出现次数"])

        # 展示结果
        st.success("✅ 分析完成")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("基础统计")
            st.metric("含空格总字符数", text_stats["含空格换行总字符数"])
            st.metric("纯字符数", text_stats["无空格换行纯字符数"])
        with col2:
            st.subheader("高频关键词TOP10")
            # 确保传入DataFrame
            st.dataframe(keyword_df, index=False, use_container_width=True)
            if keyword_df.empty:
                st.info("📌 无有效关键词")