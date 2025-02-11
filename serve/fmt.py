import mariadb
import sys

try:
    conn = mariadb.connect(
        user="root",
        password="v",
        host="127.0.2.1",
        port=3306,
        database="ads"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

def read_txt_file(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n\n')  # 用空行分隔
        for block in lines:
            # 用换行符分割每个块
            lines_in_block = block.splitlines()
            if len(lines_in_block) >= 3:
                field1 = lines_in_block[0].strip()
                field2 = lines_in_block[1].strip()
                field3 = lines_in_block[2].strip()
                field4 = "\n".join(lines_in_block[3:]).strip() if len(lines_in_block) > 3 else None
                f1 = field1
                if field1 =='-':
                    f1=''
                f2 = field2
                if field2 =='-':
                    f2=''
                f3 = field3
                if field3 =='-':
                    f3=''

                records.append((f1, f2, f3, field4))

    return records

# 将数据写入MySQL数据库
def write_to_db(records):

    iq = "INSERT INTO v_advertise (org, zh, brand, comment) VALUES (%s, %s, %s, %s)"
    cur.executemany(iq, records)
    conn.commit() 
    conn.close()

# file_path = 'dd.txt'  # 输入txt文件路径
# records = read_txt_file(file_path)
# write_to_db(records)
# print("数据已成功导入到数据库！")
# ALTER TABLE advertise AUTO_INCREMENT = 1;
from llama_index.core.schema import Document
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,StorageContext,Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from ollama import Client
from llama_index.llms.ollama import Ollama
client = Client(
  host='http://localhost:11434',
  headers={'x-some-header': 'some-value'}
)

# ollama_embedding = OllamaEmbedding(
#     model_name="qwen2.5",
#     base_url="http://localhost:11434",
# )

# pass_embedding = ollama_embedding.get_text_embedding_batch(
#     ["This is a passage!", "This is another passage"], show_progress=True
# )
# print(pass_embedding)

# query_embedding = ollama_embedding.get_query_embedding("Where is blue?")
# print(query_embedding)

Settings.embed_model = OllamaEmbedding(
    model_name="qwen2.5",
    base_url="http://localhost:11434",
)
Settings.llm = Ollama(model="llama3.2:latest", request_timeout=1200.0)

def load_data_from_mariadb():
    cur.execute("SELECT org, zh, brand,comment FROM advertise")
    documents = [Document(text=f"{org}\n{zh}\n{brand}\n{comment}") for org, zh, brand,comment in cur.fetchall()]
    conn.close()
    return documents

qc = QdrantClient(host="localhost", port=6333)
# vector_store = QdrantVectorStore(client=qc, collection_name="paul_graham")
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
# documents = load_data_from_mariadb()
# index = VectorStoreIndex.from_documents(
#     [],#documents,
#     storage_context=storage_context,
# )
# query_engine = index.as_query_engine()
# response = query_engine.query("写一个芬达饮料的广告文案")
# print("RAG Answer:", response)

# exit() 
# 基于 RAG 结果生成回答
def generate_answer(query):
    retrieved_documents = qc.search(
        collection_name=self.collection_name,
        query_vector=query_vector,
        limit=limit
    )
    return retrieved_documents
    context = "\n".join([doc.text for doc in retrieved_documents])
    response = client.chat(model='llama3.2:latest', messages=[{
        'role': 'user',
        'content': f"Context: {context}\nQuestion: {query}\nAnswer:",
    }])

    return response

query = "写一个芬达饮料的广告文案"
answer = generate_answer(query)
print("Final Answer:", answer)
