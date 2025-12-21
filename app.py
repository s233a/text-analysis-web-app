import streamlit as st
import jieba
from collections import Counter

# 页面标题
st.title("简易文本分析Web应用")
st.divider()  # 分割线

# 获取用户输入文本
user_text = st.text_area("请输入需要分析的文本内容", height=200, placeholder="请在此粘贴或输入文本...")

# 分析按钮点击事件
if st.button("开始文本分析"):
    if not user_text.strip():  # 判断是否为空文本
        st.warning("温馨提示：请先输入有效文本再进行分析！")
    else:
        # 1. 基础字符统计
        total_chars = len(user_text)  # 含空格/换行
        total_chars_no_space = len(user_text.replace(" ", "").replace("\n", ""))  # 不含空格/换行
        # 2. 中文分词+高频词统计
        seg_list = jieba.lcut(user_text.replace(" ", "").replace("\n", ""))
        # 简易停用词表（过滤无意义词汇）
        stop_words = ["的", "了", "是", "我", "你", "他", "她", "它", "在", "和", "有", "就", "都", "这", "那"]
        filtered_words = [word for word in seg_list if word not in stop_words and len(word) > 1]
        top10_words = Counter(filtered_words).most_common(10)  # 取前10个高频词

        # 展示分析结果
        st.success("文本分析完成！以下是分析结果：")
        st.subheader("一、 基础统计信息")
        st.write(f"总字符数（含空格/换行）：{total_chars} 个")
        st.write(f"总字符数（不含空格/换行）：{total_chars_no_space} 个")

        st.subheader("二、 高频关键词TOP10")
        for word, count in top10_words:
            st.write(f"{word}：出现 {count} 次")