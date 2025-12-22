import streamlit as st
import jieba
from collections import Counter

# 页面配置
st.set_page_config(page_title="简易文本分析工具", page_icon="📝", layout="centered")

# 停用词表
STOP_WORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它",
    "在", "和", "有", "就", "都", "这", "那", "其"
}

# ---------------------- 核心函数（返回列表，避免DataFrame类型问题） ----------------------
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
    """返回列表，而非DataFrame，彻底规避类型错误"""
    word_list = jieba.lcut(pure_text)
    valid_words = [
        word for word in word_list
        if word not in STOP_WORDS and len(word) > 1
    ]
    if not valid_words:
        return []
    word_count = Counter(valid_words)
    return word_count.most_common(top_n)

# ---------------------- 页面交互（用原生组件展示） ----------------------
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
        top_keywords = get_top_keywords(text_stats["纯文本内容"])

        # 展示结果（全用原生组件，无DataFrame）
        st.success("✅ 分析完成")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 基础统计")
            st.write(f"含空格换行总字符数：{text_stats['含空格换行总字符数']}")
            st.write(f"无空格换行纯字符数：{text_stats['无空格换行纯字符数']}")
        
        with col2:
            st.subheader("🔤 高频关键词TOP10")
            if top_keywords:
                for idx, (word, count) in enumerate(top_keywords, 1):
                    st.write(f"{idx}. {word}：{count}次")
            else:
                st.info("📌 无有效关键词")