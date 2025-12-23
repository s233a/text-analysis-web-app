import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd  # 用于构造柱状图数据

# 页面配置
st.set_page_config(page_title="网页文本分析工具（带柱状图）", layout="centered")

# ---------------------- 核心函数 ----------------------
def crawl_web_text(url):
    """爬取网页文本（优化反爬+正文提取）"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        # 提取正文（过滤非内容标签）
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe"]):
            tag.decompose()
        # 优先取article标签，无则取p标签集合
        article = soup.find("article")
        if article:
            text = article.get_text(strip=True, separator="\n")
        else:
            text = "\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
        
        return text.strip() if len(text.strip()) > 50 else None  # 过滤过短文本
    except Exception as e:
        st.error(f"爬取失败：{str(e)}")
        return None

def analyze_text(text, top_n=6):
    """文本分析（分词+高频词统计，返回统计结果和DataFrame（用于柱状图））"""
    # 分词+过滤停用词
    stop_words = {"的", "了", "是", "我", "你", "他", "在", "和", "有", "就", "都", "这", "那"}
    words = jieba.lcut(text)
    valid_words = [word for word in words if word not in stop_words and len(word) > 1]
    # 统计高频词
    if not valid_words:
        return None, None
    word_count = Counter(valid_words)
    top_keywords = word_count.most_common(top_n)
    # 构造DataFrame（用于柱状图展示）
    keyword_df = pd.DataFrame(top_keywords, columns=["关键词", "出现次数"])
    return top_keywords, keyword_df

# ---------------------- 页面逻辑 ----------------------
st.title("📝 网页文本分析工具（带柱状图可视化）")
st.divider()

# 1. 选择分析模式
mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"], horizontal=True)

# 2. 网页URL爬取流程
if mode == "网页URL爬取分析":
    url = st.text_input(
        "请输入有效文章URL（非首页）",
        placeholder="示例：https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml"
    )
    
    # 爬取按钮：点击后存储文本到session_state
    if st.button("🚀 开始爬取网页文本", use_container_width=True):
        crawled_text = crawl_web_text(url)
        if crawled_text:
            st.session_state["target_text"] = crawled_text  # 存储文本
            st.success("✅ 爬取成功！可进行文本分析")
        else:
            st.warning("⚠️ 未爬取到有效文本（建议更换具体文章URL）")

# 3. 手动输入文本流程
else:
    manual_text = st.text_area(
        "请输入待分析文本",
        height=200,
        placeholder="示例：今天天气很好，适合出门散步，天气好的时候，心情也会跟着变好..."
    )
    if st.button("✅ 确认输入文本", use_container_width=True):
        if manual_text.strip():
            st.session_state["target_text"] = manual_text.strip()
            st.success("✅ 文本已就绪！可进行文本分析")
        else:
            st.warning("⚠️ 请输入有效文本")

# 4. 文本分析流程（含柱状图可视化）
if "target_text" in st.session_state:
    top_n = st.slider("选择高频关键词展示数量", 3, 20, 6)
    analyze_btn = st.button("📊 开始文本分析", use_container_width=True)
    
    if analyze_btn:
        top_keywords, keyword_df = analyze_text(st.session_state["target_text"], top_n)
        if top_keywords and not keyword_df.empty:
            # 分栏展示：文字结果 + 柱状图
            col1, col2 = st.columns(2)
            
            # 左侧：文字形式展示高频关键词
            with col1:
                st.subheader("🔤 高频关键词TOP{}".format(top_n))
                for idx, (word, count) in enumerate(top_keywords, 1):
                    st.write(f"{idx}. {word}：{count}次")
            
            # 右侧：柱状图可视化展示
            with col2:
                st.subheader("📈 关键词出现次数柱状图")
                # 使用st.bar_chart绘制，直接传入DataFrame即可
                st.bar_chart(keyword_df.set_index("关键词"), color="#1f77b4")  # 自定义柱状图颜色
            
            # 可选：展示完整的关键词统计表格
            st.subheader("📋 关键词统计详情")
            st.dataframe(keyword_df, index=False, use_container_width=True)
        else:
            st.info("📌 未提取到有效关键词（文本过短或无有效词汇）")
else:
    # 无文本时禁用分析按钮，并给出提示
    st.button("📊 开始文本分析", disabled=True, use_container_width=True)
    st.info("ℹ️ 请先爬取/输入文本，再进行分析")