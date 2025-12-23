import streamlit as st
import jieba
from collections import Counter
import numpy as np
from snownlp import SnowNLP
import pandas as pd

# 页面配置
st.set_page_config(page_title="增强版文本分析工具", page_icon="📝", layout="centered")

# 扩充停用词表
STOP_WORDS = {
    "的", "了", "是", "我", "你", "他", "她", "它",
    "在", "和", "有", "就", "都", "这", "那", "其",
    "之", "于", "以", "为", "而", "也", "吗", "呢",
    "吧", "啊", "哦", "嗯", "着", "过", "还", "将",
    "要", "会", "能", "可", "对", "与", "或", "及",
    "所", "把", "被", "让", "给", "使", "得", "到",
    "从", "往", "向", "比", "跟", "同", "和"
}

# ---------------------- 核心函数（移除复杂Matplotlib依赖，改用原生组件） ----------------------
def calculate_text_stats(input_text):
    total_with_space = len(input_text)
    pure_text = input_text.replace(" ", "").replace("\n", "")
    total_without_space = len(pure_text)
    
    sentence_end_chars = "。！？；"
    sentence_count = 1
    for char in sentence_end_chars:
        sentence_count += pure_text.count(char)
    
    punctuation_chars = '，。！？；：""''（）【】《》,.!?;:\'"()[]{}<>、'
    punctuation_count = sum(1 for char in pure_text if char in punctuation_chars)
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
    if not pure_text:
        return []
    word_list = jieba.lcut(pure_text)
    valid_words = [
        word for word in word_list
        if word not in STOP_WORDS and len(word) > 1 and word.strip()
    ]
    if not valid_words:
        return []
    word_count = Counter(valid_words)
    return word_count.most_common(top_n)

def analyze_sentiment(pure_text):
    if not pure_text:
        return {"情感得分": 0.5, "情感倾向": "中性", "文本摘要": []}
    s = SnowNLP(pure_text)
    sentiment_score = s.sentiments
    if sentiment_score >= 0.7:
        sentiment_tendency = "正面"
    elif sentiment_score <= 0.3:
        sentiment_tendency = "负面"
    else:
        sentiment_tendency = "中性"
    summary_list = s.summary(3) if len(pure_text) > 10 else ["文本过短，无法生成摘要"]
    return {
        "情感得分": round(sentiment_score, 4),
        "情感倾向": sentiment_tendency,
        "文本摘要": summary_list
    }

def get_word_segmentation(pure_text):
    if not pure_text:
        return "无有效文本"
    word_list = jieba.lcut(pure_text)
    filtered_word_list = [word for word in word_list if word not in STOP_WORDS and word.strip()]
    if not filtered_word_list:
        return "无有效分词（全为停用词/标点）"
    return " | ".join(filtered_word_list)

# 替换Matplotlib饼图：用Streamlit原生表格+进度条展示文本构成
def show_text_composition(text_stats):
    pure_word_count = text_stats["纯文字数（去标点）"]
    punctuation_count = text_stats["标点符号数"]
    total = pure_word_count + punctuation_count
    
    if total == 0:
        st.info("📌 无有效文本数据可展示")
        return
    
    # 计算占比
    word_ratio = round((pure_word_count / total) * 100, 1)
    punctuation_ratio = round((punctuation_count / total) * 100, 1)
    
    # 用表格展示占比
    comp_data = pd.DataFrame({
        "文本类型": ["纯文字", "标点符号"],
        "数量": [pure_word_count, punctuation_count],
        "占比(%)": [word_ratio, punctuation_ratio]
    })
    st.table(comp_data)
    
    # 用进度条可视化占比
    st.write("### 占比可视化")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"纯文字（{word_ratio}%）")
        st.progress(word_ratio / 100)
    with col2:
        st.write(f"标点符号（{punctuation_ratio}%）")
        st.progress(punctuation_ratio / 100)

# 替换Matplotlib情感参考图：用原生文字+标签展示情感区间
def show_sentiment_reference(sentiment_score):
    st.write("### 情感得分区间说明")
    # 用markdown展示区间，天然支持中文
    st.markdown("""
    | 得分区间 | 情感倾向 |
    |----------|----------|
    | 0.0 - 0.3 | 负面 |
    | 0.3 - 0.7 | 中性 |
    | 0.7 - 1.0 | 正面 |
    """)
    
    # 展示当前得分和倾向
    sentiment_label = "正面" if sentiment_score >=0.7 else "负面" if sentiment_score <=0.3 else "中性"
    st.write(f"#### 当前文本：{sentiment_label}（得分：{sentiment_score}）")
    
    # 用彩色标签突出显示
    if sentiment_label == "正面":
        st.success(f"✅ 情感倾向：{sentiment_label}")
    elif sentiment_label == "负面":
        st.error(f"❌ 情感倾向：{sentiment_label}")
    else:
        st.info(f"ℹ️ 情感倾向：{sentiment_label}")

# 简化词云图：若无法显示中文，替换为关键词权重列表
def show_wordcloud_alternative(pure_text):
    st.subheader("☁️ 关键词权重展示（替代词云图，中文清晰显示）")
    top_keywords = get_top_keywords(pure_text, top_n=20)
    if not top_keywords:
        st.info("📌 无有效关键词可展示")
        return
    
    # 用带样式的列表展示关键词（按出现次数排序，字体大小区分权重）
    for word, count in top_keywords:
        # 出现次数越多，字体越大
        font_size = min(12 + count * 2, 20)  # 限制最大字体
        st.markdown(f"<span style='font-size:{font_size}px; color:#2E86AB; font-weight:bold;'>{word}</span> （出现{count}次）", unsafe_allow_html=True)

# ---------------------- 页面交互（全模块中文正常显示） ----------------------
st.title("📝 增强版文本分析工具（全中文显示版）")
st.divider()

DEFAULT_TEXT = """
今天天气很好，阳光明媚，适合出门散步、野餐或者骑行，享受美好的周末时光。
公园里的花开得特别漂亮，有桃花、樱花、郁金香，五颜六色的，让人心情愉悦。
和家人一起出门游玩，聊聊家常，吃吃美食，这样的周末太幸福了。
工作中遇到了一些挑战，不过在同事的帮助下，终于顺利完成了项目任务，收获满满。
学习编程虽然有点难，但坚持下来就能掌握很多技能，对未来的职业发展很有帮助。
"""

user_input = st.text_area(
    "请输入待分析文本（可直接使用示例文本测试）",
    height=200,
    placeholder=DEFAULT_TEXT,
    value=DEFAULT_TEXT
)

top_n = st.slider("选择高频关键词展示数量", min_value=5, max_value=20, value=10, step=1)
st.divider()

if st.button("🚀 开始分析", use_container_width=True):
    if not user_input.strip():
        st.warning("⚠️ 请输入有效文本")
    else:
        text_stats = calculate_text_stats(user_input)
        top_keywords = get_top_keywords(text_stats["纯文本内容"], top_n=top_n)
        sentiment_result = analyze_sentiment(text_stats["纯文本内容"])
        word_segmentation = get_word_segmentation(text_stats["纯文本内容"])

        st.success("✅ 分析完成")
        st.divider()

        # 1. 基础统计（中文清晰显示）
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

        # 2. 高频关键词 + Streamlit原生柱状图（中文完美显示）
        st.subheader(f"🔤 高频关键词TOP{top_n}")
        if top_keywords:
            keyword_dict = {"关键词": [item[0] for item in top_keywords], "出现次数": [item[1] for item in top_keywords]}
            st.table(keyword_dict)
            
            # 原生柱状图（中文无压力）
            st.subheader("📊 高频关键词柱状图")
            st.bar_chart(
                data=keyword_dict,
                x="关键词",
                y="出现次数",
                color="#2E86AB",
                use_container_width=True
            )
        else:
            st.info("📌 无有效关键词（未筛选出长度>1且非停用词的词汇）")

        st.divider()

        # 3. 中文分词结果（中文清晰显示）
        st.subheader("✂️ 中文分词结果")
        st.text_area("分词结果（| 分隔）", value=word_segmentation, height=100, disabled=True)

        st.divider()

        # 4. 情感分析 + 原生参考展示（替代Matplotlib图，中文正常）
        st.subheader("❤️ 情感倾向分析")
        col3, col4 = st.columns(2)
        with col3:
            st.write(f"情感得分：{sentiment_result['情感得分']}（0=负面，1=正面）")
            st.write(f"情感倾向：{sentiment_result['情感倾向']}")
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
        
        # 原生情感参考展示
        show_sentiment_reference(sentiment_result["情感得分"])

        st.divider()

        # 5. 文本构成展示（替代Matplotlib饼图，中文正常）
        st.subheader("🥧 文本构成占比")
        show_text_composition(text_stats)

        st.divider()

        # 6. 关键词权重展示（替代词云图，中文清晰显示）
        show_wordcloud_alternative(text_stats["纯文本内容"])

        st.divider()
        st.caption("💡 全模块采用Streamlit原生组件，彻底解决中文显示问题，无字体依赖")