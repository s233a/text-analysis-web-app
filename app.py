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

# ---------------------- 核心功能函数封装（结构更清晰，缩进正确） ----------------------
def calculate_text_stats(input_text):
    """计算文本基础统计信息"""
    # 函数内代码统一缩进4个空格
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
    """提取文本高频关键词，返回DataFrame"""
    # 函数内代码统一缩进4个空格
    # 中文分词
    word_list = jieba.lcut(pure_text)
    # 过滤无意义词汇（停用词 + 单字）
    valid_words = [
        word for word in word_list
        if word not in STOP_WORDS and len(word) > 1
    ]
    # 统计词频并处理空值
    if not valid_words:
        # 无有效关键词时返回空DataFrame（避免报错）
        return pd.DataFrame(columns=["关键词", "出现次数"])
    word_count = Counter(valid_words)
    top_keywords = word_count.most_common(top_n)
    # 转换为DataFrame返回
    return pd.DataFrame(top_keywords, columns=["关键词", "出现次数"])

# ---------------------- 页面布局与交互（无变量未定义错误） ----------------------
# 页面标题与描述
st.title("📝 简易文本分析Web应用")
st.divider()
st.caption("支持中文文本字符统计与高频关键词提取，轻量高效！")

# 文本输入区域
with st.container(border=True):
    user_input = st.text_area(
        label="请输入待分析的文本内容",
        height=200,
        placeholder="示例：今天天气很好，适合出门散步，天气好的时候，心情也会跟着变好...",
        label_visibility="collapsed"
    )

# 分析按钮
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
        keyword_df = get_top_keywords(text_stats["纯文本内容"])

        # 3. 展示分析结果（先定义列变量，再使用with）
        st.success("✅ 文本分析完成！以下是详细结果：")
        st.divider()

        # 基础统计信息 + 高频关键词（分栏展示，无col2未定义错误）
        col1, col2 = st.columns(2)  # 先创建列变量

        with col1:
            st.subheader("📊 基础字符统计")
            st.metric(label="含空格换行总字符数", value=text_stats["含空格换行总字符数"])
            st.metric(label="无空格换行纯字符数", value=text_stats["无空格换行纯字符数"])

        with col2:
            st.subheader("🔤 高频关键词TOP10")
            # 直接展示DataFrame（无需额外判断，已处理空值）
            st.dataframe(keyword_df, index=False, use_container_width=True)
            # 无关键词时给出提示
            if keyword_df.empty:
                st.info("📌 未提取到有效关键词（文本过短或无有效词汇）")