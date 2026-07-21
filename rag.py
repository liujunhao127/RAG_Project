"""
将向量检索器、提示词、模型一起放到chain中
"""
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi   
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableWithMessageHistory
from xml.dom.minidom import Document   
from langchain_core.output_parsers import StrOutputParser 
from file_history_store import get_message_history

class RagService(object):
    def __init__(self):
        self.vector_store = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.dashscope_embedding_model)
            )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个购物助手，请根据参考资料简单明了的回答问题，参考资料：{context}"),
                ("system", "并且我会提供用户的历史会话，需要将历史会话结合起来进行答复"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "请回答{input_question}") 
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model, streaming=config.streaming)
        self.chain = self.__get_chain()

    def __get_chain(self):   
        retrieve_result = self.vector_store.get_retrieve_result()
        def format_documents(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            format_string = ""
            for doc in docs:
                format_string += f"文档片段{doc.page_content}\n文档元数据{doc.metadata}\n"

            return format_string
        
        print_prompt = RunnableLambda(lambda x: print("="*20, "\n", x.to_string(), "\n", "="*20) or x)

        # temp1和temp2是为了测试，测试报错内容
        def format_for_retrieve(value: dict)-> str: 
            return value["input"]
        
        def format_for_prompt_template(value): 
            new_value = {}
            new_value["input_question"] = value["input_question"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input_question"]["history"]
            return new_value
 
        base_chain = (
            {
                "input_question": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retrieve) | retrieve_result | format_documents
            } | RunnableLambda(format_for_prompt_template) | self.prompt | print_prompt | self.chat_model | StrOutputParser()
        )

        # 创建一个新链，在原始链的基础上增加功能：自动获取历史会话
        new_chain = RunnableWithMessageHistory(
            base_chain,  # 基础链
            get_message_history, # 函数，通过会话id获取 InMemoryChatMessageHistory类对象
            input_messages_key="input", # 用户输入在提示词模版中的占位符
            history_messages_key="history", # 历史会话在提示词模版中的占位符
        )
        return new_chain
    
if __name__ == "__main__":

    rag_service = RagService()

    # 此时的chain是一个增强的链，在原始链的基础上增加了自动获取历史会话的功能，所以此时的invoke的参数中，需要传入session_config，同时invoke中input的类型为dict，普通链的invoke中input的类型为str 
    print(rag_service.chain.invoke({"input":"羽绒服如何保养"}, config.session_config))
 