import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter

# 优化后的网页文本爬取函数
def crawl_web_text(url):
    try:
        # 模拟浏览器请求头，避免被反爬
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 捕获HTTP错误
        response.encoding = response.apparent_encoding  # 自动识别编码
        
        # 使用BeautifulSoup提取正文（针对新闻类网页的通用规则）
        soup = BeautifulSoup(response.text, "html.parser")
        # 过滤非正文标签（导航、广告、脚本等）
        for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
            tag.decompose()
        # 提取正文（优先取article标签，无则取p标签）
        article = soup.find("article")
        if article:
            text = article.get_text(strip=True, separator="\n")
        else:
            text = "\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
        
        # 过滤空文本
        return text.strip() if len(text.strip()) > 10 else None
    except Exception as e:
        st.error(f"爬取失败：{str(e)}")
        return None

# 页面逻辑示例
st.title("网页文本分析工具")
mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"])

if mode == "网页URL爬取分析":
    url = st.text_input("请输入有效文章URL", "https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml")
    if st.button("开始爬取网页文本"):
        crawled_text = crawl_web_text(url)
        if crawled_text:
            st.session_state["text"] = crawled_text  # 存储爬取的文本
            st.success("爬取成功！可点击下方按钮分析")
        else:
            st.warning("未爬取到有效文本")

# 文本分析逻辑
if "text" in st.session_state and st.session_state["text"]:
    top_n = st.slider("选择高频关键词展示数量", 3, 20, 6)
    if st.button("开始文本分析"):
        # 执行文本分析（分词、统计等）
        words = jieba.lcut(st.session_state["text"])
        # 后续分析逻辑...