from ollama import Client
import requests,pprint,json

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
                field4 = "\n".join(lines_in_block[3:]).strip() if len(lines_in_block) > 3 else ""
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

url = "http://localhost:6333/"
headers = {'api-key': 'hello_qdrant_server','Content-Type': 'application/json'}
cname = "ads"
embModel = Client()


# records = read_txt_file('dd.txt')
# for id, r in enumerate(records) :
#     text = '\n'.join(r)
#     response = embModel.embeddings(
#         model='qwen2.5',#'snowflake-arctic-embed',#'nomic-embed-text',
#         prompt= text
#     )
#     print(id)
#     insert(id, {'v':text}, response['embedding'])
# exit()


def createCollection(size=3584):
    res = requests.get(url+"collections", headers=headers)
    if res.status_code == requests.codes.ok:
        for it in res.json().get('result').get('collections'):  
            if it['name'] == cname:
                return True
        
        pld = {
            "vectors": {
                "size": size,
                "distance": "Cosine"
            }
        }
        res = requests.put(url+f"/collections/{cname}", json=pld, headers=headers)
        if res.status_code == requests.codes.ok:
            # print(res.text)
            # pprint.pp(res.json())  
            return True
        else:
            # print(res.status_code, " : ", res.text)
            return False
# createCollection()
# exit()

def insert(id, m, v):
    pld = {
        "points": [{"id": id,"payload": m,"vector": v}]
    }
    res = requests.put(url+"/collections/test_collection/points", json=pld, headers=headers)
    if res.status_code == requests.codes.ok:
        # print(res.text)
        # pprint.pp(res.json())  
        return True
    else:
        print('insert  ->', res.status_code, " : ", res.text)
        return False

def search(v, limit=10):
    pld = {"vector": v,"limit": limit, "with_payload":True, "score_threshold": 0.2}
    res = requests.post(url+f"/collections/{cname}/points/search", json=pld, headers=headers)
    if res.status_code == requests.codes.ok:
        pprint.pp(res.json().get('result'))
    else:
        print('insert  ->', res.status_code, " : ", res.text)
        return False

response = embModel.embeddings(
    model='qwen2.5',#'snowflake-arctic-embed',#'nomic-embed-text',
    prompt= '''
因为你值得。

    '''
)
search(response['embedding'])
exit() 
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
