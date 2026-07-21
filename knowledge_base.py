"""知识库"""
import os
import config_data as config
import hashlib
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
def check_md5(md5_str: str):
    """检查知识是否重复,return True(已包含该知识)/False"""
    if not os.path.exists(config.md5_path):
        open(config.md5_path, "w", encoding="utf-8").close()
        return False    
    else:
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip() # 去除str前后的换行符和空格，只保留核心内容
            if line == md5_str:
                return True
        return False

def save_md5(md5_str:str):
    """将传入的字符串记录到md5文件中保存"""
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n") 

def   get_string_md5(input_str: str, encoding="utf-8"):
    """将传入的字符串转换为md5字符串"""
    # 将字符串转换为bytes
    input_str = input_str.encode(encoding) 

    # 创建md5对象
    md5_obj = hashlib.md5()
    md5_obj.update(input_str) # 传入bytes对象,进行转换
    return md5_obj.hexdigest() # 返回md5 十六进制 字符串

class KnowledgeBaseService:
    """知识库服务"""
    def __init__(self):
        # 如果持久化文件不存在，则创建
        os.makedirs(config.persist_directory, exist_ok=True)
         
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory # 向量库持久化文件
        ) # 向量存储的实例，Chroma向量库对象

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, # 切割的块大小
            chunk_overlap=config.chunk_overlap, # 块之间的重叠大小
            separators=config.separators, # 切割的分隔符
            length_function=len # 获取字符串长度的函数
        ) # 文本切割器对象

    def upload_by_srt(self, data, file_name):
        """上传srt文件，将传入的字符串进行向量化，并存储到向量库中"""
        md5_hex = get_string_md5(data) # 获取md5值
        if check_md5(md5_hex):
            return "已包含该知识"
        else:
            # 创建md5文件
            save_md5(md5_hex)

            # 判断文本大小来决定是否进行切割
            if len(data) > config.max_split_size:
                knowledge_chunks:list[str] = self.spliter.split_text(data)
            else:
                knowledge_chunks = [data]
            
            # 向量化
            matedata = {
                "source": file_name,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "operator": "knowledge_base.py"
            }
            self.chroma.add_texts(
                texts=knowledge_chunks,
                metadatas=[matedata] * len(knowledge_chunks)
            )
            return "上传成功"

if __name__ == "__main__":
    service = KnowledgeBaseService()
    print(service.upload_by_srt("""
     1
     00:00:01,000 --> 00:00:03,000
     欢迎来到我的世界

     2
     00:00:03,000 --> 00:00:05,000
     这是一个测试
     """, "testfilename"))

    