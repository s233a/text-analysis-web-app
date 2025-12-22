# （仅展示需修改的“高频关键词”部分，其余代码不变）
with col2:
    st.subheader("🔤 高频关键词TOP10")
    if top_keywords:
        # 有有效关键词时，正常生成DataFrame
        keyword_df = pd.DataFrame(
            top_keywords,
            columns=["关键词", "出现次数"]
        )
    else:
        # 无有效关键词时，生成空DataFrame（避免None）
        keyword_df = pd.DataFrame(columns=["关键词", "出现次数"])
    
    # 展示DataFrame，同时补充提示信息
    st.dataframe(keyword_df, index=False, use_container_width=True)
    if not top_keywords:
        st.info("📌 未提取到有效关键词（文本过短或无有效词汇）")