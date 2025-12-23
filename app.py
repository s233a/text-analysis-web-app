import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd  # 新增：用于构造数据格式

# 页面配置
st.set_page_config(page_title="网页文本分析工具（多图可视化）", layout="centered")

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
st.title("📝 网页文本分析工具（多图可视化版）")
st.divider()

mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"], horizontal=True)

if mode == "网页URL爬取分析":
    url = st.text_input(
        "请输入有效文章URL（非首页）",
        placeholder="示例：https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml"
    )
    if st.button("🚀 开始爬取网页文本", use_container_width=True):
        crawled_text = crawl_web_text(url)
        if crawled_text:
            st.session_state["target_text"] = crawled_text
            st.success("✅ 爬取成功！可进行文本分析")
        else:
            st.warning("⚠️ 未爬取到有效文本")
else:
    manual_text = st.text_area(
        "请输入待分析文本",
        height=200,
        placeholder="示例：今天天气很好，明天天气也不错，后天适合出门散步，散步能放松心情"
    )
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
            words = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]

            st.subheader("🔤 高频关键词TOP{}".format(top_n))
            for idx, (word, count) in enumerate(top_keywords, 1):
                st.write(f"{idx}. {word}：{count}次")

            st.subheader("📋 关键词统计详情")
            st.table([{"关键词": word, "出现次数": count} for word, count in top_keywords])

            st.subheader("📈 多维度数据可视化")
            # 第一排：柱状图 + 条形图
            col1, col2 = st.columns(2)
            with col1:
                st.caption("柱状图（纵向：关键词词频对比）")
                st.bar_chart({"关键词": words, "出现次数": counts}, x="关键词", y="出现次数", color="#1f77b4")
            with col2:
                st.caption("条形图（横向：长关键词更易读取）")
                st.bar_chart({"关键词": words, "出现次数": counts}, x="出现次数", y="关键词", color="#ff7f0e")

            # 第二排：折线图 + 饼图（改用Streamlit原生组件+pd，彻底解决中文）
            col3, col4 = st.columns(2)
            with col3:
                st.caption("折线图（关键词词频趋势）")
                st.line_chart({"关键词": words, "出现次数": counts}, x="关键词", y="出现次数", color="#2ca02c")
            with col4:
                st.caption("饼状图（关键词词频占比）")
                # 构造DataFrame，用st.plotly_chart（Streamlit内置，原生支持中文）
                pie_df = pd.DataFrame({"关键词": words, "出现次数": counts})
                st.plotly_chart(
                    {
                        "data": [
                            {
                                "labels": pie_df["关键词"],
                                "values": pie_df["出现次数"],
                                "type": "pie",
                                "hole": 0.3,  # 可选：甜甜圈样式
                                "marker": {"colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]}
                            }
                        ],
                        "layout": {"title": None}
                    },
                    use_container_width=True
                )
        else:
            st.info("📌 未提取到有效关键词")
else:
    st.button("📊 开始文本分析", disabled=True, use_container_width=True)
    st.info("ℹ️ 请先爬取/输入文本，再进行分析")