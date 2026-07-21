md5_path = "./md5.txt "

# Chroma
collection_name = "rag_collection"
persist_directory = "./chroma_db"

# Splitter
chunk_size = 40
chunk_overlap = 0
separators = ['\n', ' ', '', '.', '!', '?', ';', '？', '。', '！', '；', '\n\n'] 
max_split_size = 1

# similarity_search
similarity_threshold = 1

dashscope_embedding_model = "text-embedding-v4"
chat_model = "qwen3-max"
streaming = True      # 是否流式返回

session_config = {
     "configurable" : {
        "session_id": "session_id"
    }
}