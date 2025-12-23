import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter

# 页面配置
st.set_page_config(page_title="网页文本分析工具", layout="centered")

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
    """文本分析（分词+高频词统计）"""
    # 分词+过滤停用词
    stop_words = {"的", "了", "是", "我", "你", "他", "在", "和", "有", "就", "都", "这", "那"}
    words = jieba.lcut(text)
    valid_words = [word for word in words if word not in stop_words and len(word) > 1]
    # 统计高频词
    if not valid_words:
        return None
    return Counter(valid_words).most_common(top_n)

# ---------------------- 页面逻辑（补全流程+数据存储） ----------------------
st.title("网页文本分析工具")

# 1. 选择分析模式
mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"])

# 2. 网页URL爬取流程
if mode == "网页URL爬取分析":
    url = st.text_input("请输入有效文章URL", "https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml")
    
    # 爬取按钮：点击后存储文本到session_state
    if st.button("开始爬取网页文本"):
        crawled_text = crawl_web_text(url)
        if crawled_text:
            st.session_state["target_text"] = crawled_text  # 存储文本
            st.success("✅ 爬取成功！可点击下方按钮分析")
        else:
            st.warning("⚠️ 未爬取到有效文本（建议更换具体文章URL）")

# 3. 手动输入文本流程
else:
    manual_text = st.text_area("请输入待分析文本", height=200)
    if st.button("确认输入文本"):
        if manual_text.strip():
            st.session_state["target_text"] = manual_text.strip()
            st.success("✅ 文本已就绪！可点击下方按钮分析")
        else:
            st.warning("⚠️ 请输入有效文本")

# 4. 文本分析流程（只有存在目标文本时才可用）
if "target_text" in st.session_state:
    top_n = st.slider("选择高频关键词展示数量", 3, 20, 6)
    if st.button("开始文本分析"):
        result = analyze_text(st.session_state["target_text"], top_n)
        if result:
            st.subheader("📊 分析结果")
            st.write("高频关键词TOP{}：".format(top_n))
            for idx, (word, count) in enumerate(result, 1):
                st.write(f"{idx}. {word}：{count}次")
        else:
            st.info("📌 未提取到有效关键词")
else:
    # 无文本时禁用分析按钮（或提示）
    st.button("开始文本分析", disabled=True)
    st.info("请先爬取/输入文本，再进行分析")