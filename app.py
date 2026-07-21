"""
这里是app的前端入口
"""
import streamlit as st
import time
from rag import RagService
import config_data as config

# 标题
st.title("购物助手")
# 分隔符
st.divider()

# 在页面最下方添加用户输入框
prompt = st.chat_input()
# 创建rag服务,并保存到session_state中，方便后续使用
if "rag_service" not in st.session_state:
    st.session_state["rag_service"] = RagService()

# 创建消息队列的session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content":"你咋这么有钱么？说吧，又要买啥？"}]

# 显示聊天历史内容
for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
if prompt:
    # 在页面显示用户输入
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content":prompt})
    
    # 因为聊天内容是流式返回的，所以流式输出的数据无法像直接输出那样可以直接存到session_state["messages"].append，需要先将流式内容捕获存在list中，再添加到session_state["messages"]中
    cache_list = []
    with st.spinner("让我想一下哈..."):
        res_stream = st.session_state["rag_service"].chain.stream({"input": prompt}, config.session_config)
        # 通过yield将数据流数据原封不动的返回出去，在这一过程中，将数据流数据保存在cache_list中
        def capture_res(res_stream, cache_list):
            for chunk in res_stream:
                cache_list.append(chunk)
                yield chunk  # yield 迭代器可以将传进来的数据流数据原封不动的再返回出去

        st.chat_message("assistant").write_stream(capture_res(res_stream, cache_list))
        st.session_state["messages"].append({"role": "assistant", "content":"".join(cache_list)})
 