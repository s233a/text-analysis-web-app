import streamlit as st
import jieba
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from snownlp import SnowNLP

# 页面配置
st.set_page_config(page_title="增强版文本分析工具", page_icon="📝", layout="centered")

# 扩充停用词表（更全面的中文停用词）
STOP_WORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它",
    "在", "和", "有", "就", "都", "这", "那", "其",
    "之", "于", "以", "为", "而", "也", "吗", "呢",
    "吧", "啊", "哦", "嗯", "着", "过", "还", "将",
    "要", "会", "能", "可", "对", "与", "或", "及",
    "所", "把", "被", "让", "给", "使", "得", "到",
    "从", "往", "向", "比", "跟", "同", "和", "的"
}

# ---------------------- 核心函数（扩充功能） ----------------------
def calculate_text_stats(input_text):
    total_with_space = len(input_text)
    pure_text = input_text.replace(" ", "").replace("\n", "")
    total_without_space = len(pure_text)
    
    # 新增统计项：句子数（按。！？分割）
    sentence_end_chars = "。！？；"
    sentence_count = 1  # 默认至少1个句子
    for char in sentence_end_chars:
        sentence_count += pure_text.count(char)
    
    # 新增统计项：标点符号数
    punctuation_chars = '，。！？；：""''（）【】《》,.!?;:\'"()[]{}<>、'
    punctuation_count = sum(1 for char in pure_text if char in punctuation_chars)
    
    # 新增统计项：纯文字数（去除标点）
    pure_word_count = total_without_space - punctuation_count
    
    return {
        "含空格换行总字符数": total_with_space,
        "无空格换行纯字符数": total_without_space,
        "纯文本内容": pure_text,
        "句子数": sentence_count,
        "标点符号数": punctuation_count,
        "纯文字数（去标点）": pure_word_count
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

def generate_wordcloud(pure_text):
    """生成中文词云图"""
    # 分词并过滤停用词
    word_list = jieba.lcut(pure_text)
    valid_words = " ".join([word for word in word_list if word not in STOP_WORDS and len(word) > 1])
    
    if not valid_words:
        return None
    
    # 设置词云参数（支持中文显示）
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'WenQuanYi Zen Hei']  # 兼容不同环境字体
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        font_path=None,  # 自动适配系统中文字体
        max_words=100,
        max_font_size=100,
        random_state=42
    ).generate(valid_words)
    
    # 转换为图片格式供Streamlit展示
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")  # 隐藏坐标轴
    plt.tight_layout()
    return fig

def analyze_sentiment(pure_text):
    """文本情感倾向分析（基于SnowNLP）"""
    if not pure_text:
        return {"情感得分": 0.5, "情感倾向": "中性"}
    
    s = SnowNLP(pure_text)
    sentiment_score = s.sentiments  # 得分范围0-1，越接近1越正面，越接近0越负面
    
    # 判断情感倾向
    if sentiment_score >= 0.7:
        sentiment_tendency = "正面"
    elif sentiment_score <= 0.3:
        sentiment_tendency = "负面"
    else:
        sentiment_tendency = "中性"
    
    return {
        "情感得分": round(sentiment_score, 4),
        "情感倾向": sentiment_tendency,
        "文本摘要": s.summary(3)  # 生成3句文本摘要
    }

def get_word_segmentation(pure_text):
    """返回中文分词结果（带分隔符）"""
    word_list = jieba.lcut(pure_text)
    # 过滤停用词，同时保留原始分词展示
    filtered_word_list = [word for word in word_list if word not in STOP_WORDS]
    return " | ".join(filtered_word_list)

# ---------------------- 页面交互（扩充展示） ----------------------
st.title("📝 增强版文本分析Web应用")
st.divider()

user_input = st.text_area(
    "请输入待分析文本",
    height=200,
    placeholder="示例：今天天气很好，阳光明媚，适合出门散步、野餐或者骑行，享受美好的周末时光..."
)

# 新增：调整分析参数
top_n = st.slider("选择高频关键词展示数量", min_value=5, max_value=20, value=10, step=1)
st.divider()

if st.button("🚀 开始分析", use_container_width=True):
    if not user_input.strip():
        st.warning("⚠️ 请输入有效文本")
    else:
        # 核心分析
        text_stats = calculate_text_stats(user_input)
        top_keywords = get_top_keywords(text_stats["纯文本内容"], top_n=top_n)
        sentiment_result = analyze_sentiment(text_stats["纯文本内容"])
        word_segmentation = get_word_segmentation(text_stats["纯文本内容"])
        wordcloud_fig = generate_wordcloud(text_stats["纯文本内容"])

        # 展示结果
        st.success("✅ 分析完成")
        st.divider()

        # 1. 基础统计（扩充后）
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 基础文本统计")
            st.write(f"含空格换行总字符数：{text_stats['含空格换行总字符数']}")
            st.write(f"无空格换行纯字符数：{text_stats['无空格换行纯字符数']}")
            st.write(f"纯文字数（去标点）：{text_stats['纯文字数（去标点）']}")
        with col2:
            st.subheader("📋 扩展统计信息")
            st.write(f"句子数：{text_stats['句子数']}")
            st.write(f"标点符号数：{text_stats['标点符号数']}")
            st.write(f"平均每句字符数：{round(text_stats['无空格换行纯字符数']/text_stats['句子数'], 2)}")

        st.divider()

        # 2. 高频关键词（支持自定义数量）
        st.subheader(f"🔤 高频关键词TOP{top_n}")
        if top_keywords:
            # 用表格展示更清晰
            keyword_data = [[idx, word, count] for idx, (word, count) in enumerate(top_keywords, 1)]
            st.table({"排名": [x[0] for x in keyword_data], "关键词": [x[1] for x in keyword_data], "出现次数": [x[2] for x in keyword_data]})
        else:
            st.info("📌 无有效关键词（未筛选出长度>1且非停用词的词汇）")

        st.divider()

        # 3. 中文分词结果展示
        st.subheader("✂️ 中文分词结果")
        if word_segmentation:
            st.text_area("分词结果（| 分隔）", value=word_segmentation, height=100, disabled=True)
        else:
            st.info("📌 无有效分词内容")

        st.divider()

        # 4. 情感分析与文本摘要
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("❤️ 情感倾向分析")
            st.write(f"情感得分：{sentiment_result['情感得分']}（0=负面，1=正面）")
            st.write(f"情感倾向：{sentiment_result['情感倾向']}")
            # 根据情感倾向显示不同样式
            if sentiment_result['情感倾向'] == "正面":
                st.success(f"✅ 文本整体偏向{sentiment_result['情感倾向']}")
            elif sentiment_result['情感倾向'] == "负面":
                st.error(f"❌ 文本整体偏向{sentiment_result['情感倾向']}")
            else:
                st.info(f"ℹ️ 文本整体为{sentiment_result['情感倾向']}")
        with col4:
            st.subheader("📝 文本自动摘要")
            summary_list = sentiment_result['文本摘要']
            if summary_list:
                for idx, summary in enumerate(summary_list, 1):
                    st.write(f"{idx}. {summary}")
            else:
                st.info("📌 无法生成有效摘要")

        st.divider()

        # 5. 词云图展示
        st.subheader("☁️ 关键词词云图")
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)
        else:
            st.info("📌 无法生成词云图（无有效关键词）")

        st.divider()
        st.caption("💡 提示：停用词已优化，支持中文分词、情感分析、词云生成等增强功能")