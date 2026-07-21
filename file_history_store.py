from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict
from langchain_core.chat_history import InMemoryChatMessageHistory
import os, json
from langchain_core.messages import BaseMessage
from typing import List, Sequence

# message_to_dict: 将单个message对象（BaseMessage类实例）转换为dict
# messages_from_dict: 将dict转换为message对象[字典、字典、、、]->[message对象、message对象、、、] 

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, file_path):
        self.session_id = session_id  # 会话id
        self.storage_path = file_path # 不同session_id会话 存储文件路径 
        self.file_path = os.path.join(self.storage_path, f"{self.session_id}.json") # 完整 存储文件路径  
        # 确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    # 添加消息
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # messages是序列，类似list tuple 
        all_messages = list(self.messages) # 已有的消息
        all_messages.extend(messages)  # 添加新的消息，将新消息和已有的消息融合

        # 将数据保存到文件中
        # 因为此时的消息是BaseMessage类实例，直接写入文件是乱码，需要转换成dict
        # message_to_dict: 将单个message对象（BaseMessage类实例）转换为dict
        all_messages_dict = [message_to_dict(message) for message in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                all_messages_dict, 
                f,
                ensure_ascii=False,
                indent=4
                )
    
    # 获取消息
    @property  # property装饰器将messages属性变为方法
    def messages(self) -> List[BaseMessage]:
        try:
             # 读取文件，此时文件里的存放格式是list[dict],需要转换为message对象
            with open(self.file_path, "r", encoding="utf-8") as f:
                all_messages_dict = json.load(f)
                # 将dict转换为message对象
                all_messages = messages_from_dict(all_messages_dict)
                return all_messages
        except FileNotFoundError:
            return []
        
    # 删除消息
    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f) 
 # 长期会话的方式
def get_message_history(session_id):
    return FileChatMessageHistory(session_id, "./chat_history/")


if __name__ == "__main__":
    # 添加langchain的配置，为当前程序配置所属session_id
    session_config = {
        "configurable" : {
            "session_id": "session_id"
        }
    }
  
 