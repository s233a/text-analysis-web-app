import streamlit as st
import jieba
from collections import Counter
import pandas as pd

# ---------------------- 配置项抽离（更易维护） ----------------------
# 页面基础配置
st.set_page_config(page_title="简易文本分析工具", page_icon="📝", layout="centered")
# 扩展停用词表（提升过滤效果）
STOP_WORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它",
    "在", "和", "有", "就", "都", "这", "那", "其",
    "及", "与", "于", "对", "哦", "呢", "啊", "吧",
    "吗", "呀", "而", "也", "还", "将", "会", "要"
}

# ---------------------- 核心功能函数封装（结构更清晰） ----------------------
def calculate_text_stats(input_text):
    """计算文本基础统计信息"""
    # 含空格和换行的总字符数
    total_with_space = len(input_text)
    # 去除空格、换行后的纯文本字符数
    pure_text = input_text.replace(" ", "").replace("\n", "")
    total_without_space = len(pure_text)
    # 返回统计结果
    return {
        "含空格换行总字符数": total_with_space,
        "无空格换行纯字符数": total_without_space,
        "纯文本内容": pure_text
    }

def get_top_keywords(pure_text, top_n=10):
    """提取文本高频关键词"""
    # 中文分词
    word_list = jieba.lcut(pure_text)
    # 过滤无意义词汇（停用词 + 单字）
    valid_words = [
        word for word in word_list
        if word not in STOP_WORDS and len(word) > 1
    ]
    # 统计词频并取前N个
    if not valid_words:
        return None
    word_count = Counter(valid_words)
    top_keywords = word_count.most_common(top_n)
    return top_keywords

# ---------------------- 页面布局与交互（更美观直观） ----------------------
# 页面标题与描述
st.title("📝 简易文本分析Web应用")
st.divider()
st.caption("支持中文文本字符统计与高频关键词提取，轻量高效！")

# 文本输入区域
with st.container(border=True):  # 带边框容器，视觉更整洁
    user_input = st.text_area(
        label="请输入待分析的文本内容",
        height=200,
        placeholder="示例：今天天气很好，适合出门散步，天气好的时候，心情也会跟着变好...",
        label_visibility="collapsed"  # 隐藏标签，更简洁
    )

# 分析按钮（独立一行，更醒目）
analyze_btn = st.button("🚀 开始文本分析", use_container_width=True)

# 分析逻辑执行
if analyze_btn:
    # 校验输入是否为空
    if not user_input.strip():
        st.warning("⚠️ 请先输入有效文本再进行分析哦！")
    else:
        # 1. 计算文本统计信息
        text_stats = calculate_text_stats(user_input)
        # 2. 提取高频关键词
        top_keywords = get_top_keywords(text_stats["纯文本内容"])

        # 3. 展示分析结果（分栏布局，更清晰）
        st.success("✅ 文本分析完成！以下是详细结果：")
        st.divider()

        # 基础统计信息（左侧栏）
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 基础字符统计")
            for key, value in text_stats.items():
                if key != "纯文本内容":  # 不展示纯文本内容，避免冗余
                    st.metric(label=key, value=value)

        # 高频关键词（右侧栏）
        with col2:
            st.subheader("🔤 高频关键词TOP10")
            if top_keywords:
                # 转换为DataFrame展示，更美观
                keyword_df = pd.DataFrame(
                    top_keywords,
                    columns=["关键词", "出现次数"]
                )
                st.dataframe(keyword_df, index=False, use_container_width=True)
            else:
                st.info("📌 未提取到有效关键词（文本过短或无有效词汇）")