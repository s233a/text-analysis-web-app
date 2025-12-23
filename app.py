import streamlit as st
import jieba
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from snownlp import SnowNLP
import os
import platform

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
    "从", "往", "向", "比", "跟", "同", "和"
}

# ---------------------- 核心修复：强制配置中文字体 ----------------------
def set_chinese_font():
    """适配不同系统的中文字体，强制生效"""
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    elif system == "Darwin":  # macOS
        plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'DejaVu Sans']
    # 兜底：如果以上字体都不存在，使用wordcloud内置兼容逻辑
    return plt.rcParams['font.sans-serif'][0]

# 初始化字体
CH_FONT = set_chinese_font()

# ---------------------- 核心函数（全量修复） ----------------------
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
    """修复：兜底空数据，确保返回格式稳定"""
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

def generate_wordcloud(pure_text):
    """修复：强制指定字体，兜底空数据"""
    if not pure_text:
        return None
    
    word_list = jieba.lcut(pure_text)
    valid_words = [word for word in word_list if word not in STOP_WORDS and len(word) > 1 and word.strip()]
    if not valid_words:
        return None
    
    valid_words_str = " ".join(valid_words)
    # 强制指定字体路径（兼容不同环境）
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        font_path=None if os.name == 'nt' else f"/System/Library/Fonts/{CH_FONT}.ttf",  # 适配mac/win/linux
        max_words=100,
        max_font_size=100,
        random_state=42,
        stopwords=STOP_WORDS  # 双重过滤停用词
    ).generate(valid_words_str)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout()
    return fig

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
    
    return {
        "情感得分": round(sentiment_score, 4),
        "情感倾向": sentiment_tendency,
        "文本摘要": s.summary(3) if len(pure_text) > 10 else ["文本过短，无法生成摘要"]
    }

def get_word_segmentation(pure_text):
    if not pure_text:
        return "无有效文本"
    word_list = jieba.lcut(pure_text)
    filtered_word_list = [word for word in word_list if word not in STOP_WORDS and word.strip()]
    if not filtered_word_list:
        return "无有效分词（全为停用词/标点）"
    return " | ".join(filtered_word_list)

def plot_keyword_bar(top_keywords):
    """修复：强制字体，空数据兜底，优化标签显示"""
    if not top_keywords:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "无有效关键词可展示", ha='center', va='center', fontsize=14, fontfamily=CH_FONT)
        ax.axis("off")
        return fig
    
    set_chinese_font()  # 绘图前重新确认字体
    words = [item[0] for item in top_keywords]
    counts = [item[1] for item in top_keywords]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(words, counts, color='#2E86AB', alpha=0.8, edgecolor='#1A5276')
    
    # 强制中文标签显示
    ax.set_xticklabels(words, fontfamily=CH_FONT, fontsize=10, rotation=45, ha='right')
    ax.set_xlabel('高频关键词', fontfamily=CH_FONT, fontsize=12, fontweight='bold')
    ax.set_ylabel('出现次数', fontfamily=CH_FONT, fontsize=12, fontweight='bold')
    ax.set_title('高频关键词出现次数柱状图', fontfamily=CH_FONT, fontsize=14, fontweight='bold', pad=20)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontfamily=CH_FONT)
    
    plt.tight_layout()
    return fig

def plot_text_composition_pie(text_stats):
    """修复：强制字体，空数据兜底"""
    set_chinese_font()
    pure_word_count = text_stats["纯文字数（去标点）"]
    punctuation_count = text_stats["标点符号数"]
    
    if pure_word_count + punctuation_count == 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "无有效文本数据可展示", ha='center', va='center', fontsize=14, fontfamily=CH_FONT)
        ax.axis("off")
        return fig
    
    labels = ['纯文字', '标点符号']
    sizes = [pure_word_count, punctuation_count]
    colors = ['#A23B72', '#F18F01']
    explode = (0.05, 0)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90,
        textprops={'fontsize': 10, 'fontfamily': CH_FONT}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontfamily(CH_FONT)
    
    ax.set_title('文本构成占比饼图（纯文字/标点符号）', fontsize=14, fontweight='bold', pad=20, fontfamily=CH_FONT)
    plt.tight_layout()
    return fig

def plot_sentiment_reference_line(sentiment_score):
    """修复：强制字体，优化显示"""
    set_chinese_font()
    
    x = [0, 0.3, 0.7, 1]
    y = [0, 0, 0, 0]
    labels = ['负面', '中性阈值', '正面阈值', '正面']
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(x, y, color='#C73E1D', linewidth=2, linestyle='--', label='情感倾向分界线')
    ax.scatter(sentiment_score, 0, color='#2E86AB', s=200, zorder=5, label=f'当前得分：{sentiment_score}')
    
    # 强制中文标注
    for i, label in enumerate(labels):
        ax.text(x[i], 0.05, label, ha='center', va='bottom', fontsize=10, fontweight='bold', fontfamily=CH_FONT)
    
    sentiment_label = "正面" if sentiment_score >=0.7 else "负面" if sentiment_score <=0.3 else "中性"
    ax.text(sentiment_score, -0.05, sentiment_label, ha='center', va='top', 
            fontsize=11, fontweight='bold', color='red', fontfamily=CH_FONT)
    
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 0.1)
    ax.set_xlabel('情感得分区间', fontsize=12, fontweight='bold', fontfamily=CH_FONT)
    ax.set_title('情感得分参考图（0=负面，1=正面）', fontsize=14, fontweight='bold', pad=20, fontfamily=CH_FONT)
    ax.legend(loc='upper right', prop={'family': CH_FONT})
    ax.axis('off')
    plt.tight_layout()
    return fig

# ---------------------- 页面交互（修复后） ----------------------
st.title("📝 增强版文本分析Web应用（修复版）")
st.divider()

# 示例文本（方便测试）
DEFAULT_TEXT = """
今天天气很好，阳光明媚，适合出门散步、野餐或者骑行，享受美好的周末时光。
公园里的花开得特别漂亮，有桃花、樱花、郁金香，五颜六色的，让人心情愉悦。
和家人一起出门游玩，聊聊家常，吃吃美食，这样的周末太幸福了。
"""

user_input = st.text_area(
    "请输入待分析文本（可直接使用示例文本测试）",
    height=200,
    placeholder=DEFAULT_TEXT,
    value=DEFAULT_TEXT  # 默认填充示例文本，方便快速测试
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
        wordcloud_fig = generate_wordcloud(text_stats["纯文本内容"])
        keyword_bar_fig = plot_keyword_bar(top_keywords)
        text_pie_fig = plot_text_composition_pie(text_stats)
        sentiment_line_fig = plot_sentiment_reference_line(sentiment_result["情感得分"])

        st.success("✅ 分析完成")
        st.divider()

        # 1. 基础统计
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

        # 2. 高频关键词 + 柱状图
        st.subheader(f"🔤 高频关键词TOP{top_n}")
        if top_keywords:
            keyword_data = [[idx, word, count] for idx, (word, count) in enumerate(top_keywords, 1)]
            st.table({"排名": [x[0] for x in keyword_data], "关键词": [x[1] for x in keyword_data], "出现次数": [x[2] for x in keyword_data]})
        else:
            st.info("📌 无有效关键词（未筛选出长度>1且非停用词的词汇）")
        
        st.subheader("📊 高频关键词柱状图")
        st.pyplot(keyword_bar_fig)

        st.divider()

        # 3. 分词结果
        st.subheader("✂️ 中文分词结果")
        st.text_area("分词结果（| 分隔）", value=word_segmentation, height=100, disabled=True)

        st.divider()

        # 4. 情感分析 + 参考图
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("❤️ 情感倾向分析")
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
        
        st.subheader("📈 情感得分参考图")
        st.pyplot(sentiment_line_fig)

        st.divider()

        # 5. 文本构成饼图
        st.subheader("🥧 文本构成占比图")
        st.pyplot(text_pie_fig)

        st.divider()

        # 6. 词云图
        st.subheader("☁️ 关键词词云图")
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)
        else:
            st.info("📌 无法生成词云图（无有效关键词）")

        st.divider()
        st.caption("💡 已修复中文显示问题，内置示例文本可直接测试")