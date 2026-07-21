from langchain_chroma import Chroma
import config_data as config

class VectorStoreService(object):
    def __init__(self, embedding):
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
        )

    def get_retrieve_result(self):
        """
        返回向量检索器，方便加入chain
        """
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})  
    
if __name__ == "__main__":
    from langchain_community.embeddings import DashScopeEmbeddings
    retriever = VectorStoreService(DashScopeEmbeddings(model="text-embedding-v4")).get_retrieve_result()
    res=retriever.invoke("我的体重135斤，身高180cm，性别男，年龄18岁，推荐尺码是多少？")
    print(res)