import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter

# 页面配置
st.set_page_config(page_title="网页文本分析工具（多图可视化）", layout="centered")

# ---------------------- 核心函数 ----------------------
def crawl_web_text(url):
    try:
        # 模拟浏览器请求头，避免反爬
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 捕获HTTP错误
        response.encoding = response.apparent_encoding  # 自动识别编码，解决中文乱码

        # 解析并清洗HTML，提取正文
        soup = BeautifulSoup(response.text, "html.parser")
        # 过滤非正文标签
        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe"]):
            tag.decompose()
        # 优先提取article标签（新闻正文常用标签）
        article = soup.find("article")
        if article:
            text = article.get_text(strip=True, separator="\n")
        else:
            # 无article标签则提取所有p标签文本
            text = "\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
        
        # 过滤过短文本
        return text.strip() if len(text.strip()) > 50 else None
    except Exception as e:
        st.error(f"爬取失败：{str(e)}")
        return None

def analyze_text(text, top_n=6):
    # 停用词表（过滤无意义词汇）
    stop_words = {"的", "了", "是", "我", "你", "他", "在", "和", "有", "就", "都", "这", "那"}
    # 中文分词
    words = jieba.lcut(text)
    # 过滤停用词和单字
    valid_words = [word for word in words if word not in stop_words and len(word) > 1]
    if not valid_words:
        return []
    # 统计高频关键词
    return Counter(valid_words).most_common(top_n)

# ---------------------- 页面逻辑 ----------------------
st.title("📝 网页文本分析工具（多图可视化版）")
st.divider()

# 分析模式选择
mode = st.radio("请选择分析模式", ["网页URL爬取分析", "手动输入文本分析"], horizontal=True)

# URL爬取分析流程
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
            st.warning("⚠️ 未爬取到有效文本（请更换具体文章URL）")
# 手动输入文本分析流程
else:
    manual_text = st.text_area(
        "请输入待分析文本",
        height=200,
        placeholder="示例：今天天气很好，明天天气也不错，后天适合出门散步，散步能放松心情，心情好做事效率高"
    )
    if st.button("✅ 确认输入文本", use_container_width=True):
        if manual_text.strip():
            st.session_state["target_text"] = manual_text.strip()
            st.success("✅ 文本已就绪！可进行文本分析")
        else:
            st.warning("⚠️ 请输入有效文本")

# 文本分析与多图表展示
if "target_text" in st.session_state:
    # 调整高频关键词展示数量
    top_n = st.slider("选择高频关键词展示数量", 3, 20, 6)
    if st.button("📊 开始文本分析", use_container_width=True):
        top_keywords = analyze_text(st.session_state["target_text"], top_n)
        if top_keywords:
            # 拆分关键词和次数列表（供所有图表使用）
            words = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]

            # 1. 文字展示高频关键词
            st.subheader("🔤 高频关键词TOP{}".format(top_n))
            for idx, (word, count) in enumerate(top_keywords, 1):
                st.write(f"{idx}. {word}：{count}次")

            # 2. 表格展示统计详情
            st.subheader("📋 关键词统计详情")
            st.table([{"关键词": word, "出现次数": count} for word, count in top_keywords])

            # 3. 多图表可视化展示（分栏布局，无无效参数）
            st.subheader("📈 多维度数据可视化")
            # 第一排：柱状图（纵向） + 条形图（横向）
            col1, col2 = st.columns(2)
            with col1:
                st.caption("柱状图（纵向：关键词词频对比）")
                st.bar_chart({"关键词": words, "出现次数": counts}, x="关键词", y="出现次数", color="#1f77b4")
            with col2:
                st.caption("条形图（横向：长关键词更易读取）")
                # 交换x/y轴实现横向条形图
                st.bar_chart({"关键词": words, "出现次数": counts}, x="出现次数", y="关键词", color="#ff7f0e")

            # 第二排：折线图 + 饼状图（修复后，无color参数）
            col3, col4 = st.columns(2)
            with col3:
                st.caption("折线图（关键词词频趋势）")
                st.line_chart({"关键词": words, "出现次数": counts}, x="关键词", y="出现次数", color="#2ca02c")
            with col4:
                st.caption("饼状图（关键词词频占比）")
                # 构造饼图数据（字典格式）
                pie_data = dict(zip(words, counts))
                # 直接传入字典，Streamlit自动渲染饼图
                st.pie_chart(pie_data)
        else:
            st.info("📌 未提取到有效关键词（文本过短或无有效词汇）")
else:
    # 无文本时禁用分析按钮
    st.button("📊 开始文本分析", disabled=True, use_container_width=True)
    st.info("ℹ️ 请先爬取/输入文本，再进行分析")