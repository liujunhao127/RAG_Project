"""
streamlit web 框架
""" 
import streamlit as st
from knowledge_base import KnowledgeBaseService
import time

st.title("知识库更新服务")
# 创建一个知识库服务对象，要是用session_state，保证同一个会话下的数据一致性
# 因为streamlit有一个bug，当web页面刷新，当前程序就会重新创建一个对象，导致数据丢失，所以需要session_state来保证数据不重置
if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService() 
# 上传文件
uploaded_file = st.file_uploader(
    "选择文件", 
    type=["txt", "md"],
    help="请上传txt或md文件",
    accept_multiple_files=False # 是否允许上传多个文件
)
if uploaded_file is not None:
    # 提取文件信息
    file_name = uploaded_file.name
    file_size = uploaded_file.size /1024  # KB
    file_type = uploaded_file.type

    st.subheader(f"文件名称: {file_name}")
    st.write(f"格式:{file_size}|文件大小:{file_size:.2f} KB") 
    # 将文件内容读取出来并存储到向量数据库中
    text = uploaded_file.getvalue().decode("utf-8")
    with st.spinner("正在上传文件..."):
        time.sleep(1)
        result = st.session_state["kb_service"].upload_by_srt(text, file_name)
        st.write(result) 