import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="网页文本分析工具（多图可视化版）", layout="wide")

def crawl_web_text(url, timeout=15):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe"]):
            tag.decompose()
        
        article = soup.find("article")
        if article:
            text = article.get_text(strip=True, separator="\n")
        else:
            paragraphs = soup.find_all("p")
            text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        
        return text.strip() if len(text.strip()) > 50 else None
    except requests.Timeout:
        st.error(f"⏰ 请求超时！URL: {url}")
        return None
    except requests.RequestException as e:
        st.error(f"❌ 请求失败：{str(e)}")
        return None
    except Exception as e:
        st.error(f"⚠️ 处理失败：{str(e)}")
        return None

def analyze_text(text, top_n=10):
    stop_words = {"的", "了", "是", "我", "你", "他", "在", "和", "有", "就", "都", "这", "那", "着", "也", "但", "而", "与", "或", "以"}
    words = jieba.lcut(text)
    valid_words = [word for word in words if word not in stop_words and len(word) > 1 and not word.isdigit()]
    if not valid_words:
        return []
    return Counter(valid_words).most_common(top_n)

def create_word_cloud(keywords):
    words = [item[0] for item in keywords]
    counts = [item[1] for item in keywords]
    sizes = [count * 8 + 10 for count in counts]
    
    fig = go.Figure()
    for i, (word, count, size) in enumerate(zip(words, counts, sizes)):
        fig.add_trace(go.Scatter(
            x=[i % 5],
            y=[i // 5],
            mode='text',
            text=[word],
            textfont=dict(
                size=size,
                color=px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)]
            ),
            name=f"{word}: {count}"
        ))
    
    fig.update_layout(
        title="☁️ 词云可视化",
        showlegend=True,
        height=400,
        xaxis=dict(visible=False, range=[-0.5, 4.5]),
        yaxis=dict(visible=False, range=[-0.5, 3.5]),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

st.title("📝 网页文本分析工具（多图可视化版）")
st.markdown("---")

mode = st.radio("请选择分析模式", ["🌐 网页URL爬取分析", "📝 手动输入文本分析"], horizontal=True)

if mode == "🌐 网页URL爬取分析":
    url = st.text_input(
        "请输入有效文章URL（非首页）",
        placeholder="示例：https://news.sina.com.cn/c/2025-06-20/doc-iahfyqhi8678342.shtml",
        help="建议使用新闻文章、博客等文本丰富的页面"
    )
    if st.button("🚀 开始爬取网页文本", use_container_width=True, type="primary"):
        if url:
            with st.spinner("🕵️ 正在抓取网页..."):
                crawled_text = crawl_web_text(url)
                if crawled_text:
                    st.session_state["target_text"] = crawled_text
                    st.session_state["source_url"] = url
                    st.success("✅ 爬取成功！可进行文本分析")
                    
                    with st.expander("📄 查看抓取的文本内容", expanded=False):
                        st.text_area("文本内容", crawled_text[:3000] + "..." if len(crawled_text) > 3000 else crawled_text, height=200)
                else:
                    st.warning("⚠️ 未爬取到有效文本，请检查URL是否正确")
        else:
            st.warning("⚠️ 请输入有效的URL")
else:
    manual_text = st.text_area(
        "请输入待分析文本",
        height=200,
        placeholder="示例：今天天气很好，明天天气也不错，后天适合出门散步，散步能放松心情"
    )
    if st.button("✅ 确认输入文本", use_container_width=True, type="primary"):
        if manual_text.strip():
            st.session_state["target_text"] = manual_text.strip()
            st.session_state["source_url"] = None
            st.success("✅ 文本已就绪！可进行文本分析")
        else:
            st.warning("⚠️ 请输入有效文本")

if "target_text" in st.session_state:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        top_n = st.slider("选择高频关键词展示数量", 3, 20, 10)
    with col2:
        chart_style = st.selectbox("选择图表配色", ["专业蓝", "活力橙", "自然绿", "彩虹色"])
    
    color_palettes = {
        "专业蓝": ["#1f77b4", "#3182ce", "#6baed6", "#9ecae1", "#c6dbef"],
        "活力橙": ["#ff7f0e", "#fd8d3c", "#fdbe85", "#fdd0a2", "#fee6ce"],
        "自然绿": ["#2ca02c", "#31a354", "#74c476", "#a1d99b", "#c7e9c0"],
        "彩虹色": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    }
    colors = color_palettes[chart_style]

    if st.button("📊 开始文本分析", use_container_width=True, type="primary"):
        top_keywords = analyze_text(st.session_state["target_text"], top_n)
        if top_keywords:
            words = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]
            total_count = sum(counts)

            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("文本长度", f"{len(st.session_state['target_text'])} 字")
            with col_stats2:
                st.metric("分词数量", f"{len(jieba.lcut(st.session_state['target_text']))} 个")
            with col_stats3:
                st.metric("关键词总数", f"{total_count} 次")

            st.subheader("🔤 高频关键词TOP{}".format(top_n))
            keyword_df = pd.DataFrame(top_keywords, columns=["关键词", "出现次数"])
            keyword_df["占比"] = keyword_df["出现次数"] / total_count * 100
            keyword_df["占比"] = keyword_df["占比"].round(2)
            st.dataframe(keyword_df, use_container_width=True, hide_index=True)

            st.subheader("📈 多维度数据可视化")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.caption("📊 柱状图（关键词词频对比）")
                fig_bar = px.bar(
                    x=words, y=counts,
                    color=counts,
                    color_continuous_scale=colors,
                    labels={"x": "关键词", "y": "出现次数"},
                    title=None
                )
                fig_bar.update_layout(height=350, margin=dict(t=0))
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_chart2:
                st.caption("🥧 饼图（关键词词频占比）")
                fig_pie = px.pie(
                    names=words, values=counts,
                    color_discrete_sequence=colors,
                    hole=0.4,
                    title=None
                )
                fig_pie.update_layout(height=350, margin=dict(t=0))
                st.plotly_chart(fig_pie, use_container_width=True)

            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.caption("📉 折线图（关键词趋势）")
                fig_line = px.line(
                    x=words, y=counts,
                    markers=True,
                    color_discrete_sequence=colors,
                    labels={"x": "关键词", "y": "出现次数"},
                    title=None
                )
                fig_line.update_layout(height=350, margin=dict(t=0))
                st.plotly_chart(fig_line, use_container_width=True)
            
            with col_chart4:
                st.caption("☁️ 词云可视化")
                st.plotly_chart(create_word_cloud(top_keywords), use_container_width=True)

            csv_data = keyword_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 下载关键词数据",
                csv_data,
                "keywords.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("📌 未提取到有效关键词，请尝试输入更长的文本")
else:
    st.button("📊 开始文本分析", disabled=True, use_container_width=True)
    st.info("ℹ️ 请先爬取/输入文本，再进行分析")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>📊 网页文本分析工具 | 支持中文分词、多维度可视化</p>
</div>
""", unsafe_allow_html=True)
