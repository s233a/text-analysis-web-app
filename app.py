import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter

st.set_page_config(page_title="网页文本分析工具", layout="centered")

# ---------------------- 核心函数 ----------------------
def crawl_web_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe"]):
            tag.decompose()
        article = soup.find("article")
        text = article.get_text(strip=True, separator="\n") if article else "\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
        return text.strip() if len(text.strip()) > 50 else None
    except Exception as e:
        st.error(f"爬取失败：{str(e)}")
        return None

def analyze_text(text, top_n=6):
    stop_words = {"的", "了", "是", "我", "你", "他", "在", "和", "有", "就", "都", "这", "那"}
    words = jieba.lcut(text)
    valid_words = [word for word in words if word not in stop_words and len(word) > 1]
    if not valid_words:
        return []
    return Counter(valid_words).most_common(top_n)

# ---------------------- 页面逻辑 ----------------------
st.title("📝 网页文本分析工具")
st.divider()

mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"], horizontal=True)

if mode == "网页URL爬取分析":
    url = st.text_input("请输入有效文章URL（非首页）", placeholder="示例：https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml")
    if st.button("🚀 开始爬取网页文本", use_container_width=True):
        crawled_text = crawl_web_text(url)
        if crawled_text:
            st.session_state["target_text"] = crawled_text
            st.success("✅ 爬取成功！可进行文本分析")
        else:
            st.warning("⚠️ 未爬取到有效文本")
else:
    manual_text = st.text_area("请输入待分析文本", height=200, placeholder="示例：今天天气很好...")
    if st.button("✅ 确认输入文本", use_container_width=True):
        if manual_text.strip():
            st.session_state["target_text"] = manual_text.strip()
            st.success("✅ 文本已就绪！可进行文本分析")
        else:
            st.warning("⚠️ 请输入有效文本")

if "target_text" in st.session_state:
    top_n = st.slider("选择高频关键词展示数量", 3, 20, 6)
    if st.button("📊 开始文本分析", use_container_width=True):
        top_keywords = analyze_text(st.session_state["target_text"], top_n)
        if top_keywords:
            # 1. 文字展示高频关键词
            st.subheader("🔤 高频关键词TOP{}".format(top_n))
            for idx, (word, count) in enumerate(top_keywords, 1):
                st.write(f"{idx}. {word}：{count}次")
            
            # 2. 柱状图（用原生列表构造数据）
            st.subheader("📈 关键词出现次数柱状图")
            # 拆分关键词和次数为两个列表
            words = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]
            # 用Streamlit原生柱状图，传入字典格式数据
            st.bar_chart({"关键词": words, "出现次数": counts}, x="关键词", y="出现次数", color="#1f77b4")
            
            # 3. 表格展示（用原生列表构造）
            st.subheader("📋 关键词统计详情")
            st.table([{"关键词": word, "出现次数": count} for word, count in top_keywords])
        else:
            st.info("📌 未提取到有效关键词")
else:
    st.button("📊 开始文本分析", disabled=True, use_container_width=True)
    st.info("ℹ️ 请先爬取/输入文本，再进行分析")