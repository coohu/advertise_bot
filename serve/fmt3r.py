from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import time, pprint, asyncio
from typing import Dict
import mariadb, ollama

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_bots: Dict[str, "OllamaBot"] = {}

class SetupRequest(BaseModel):
    id: str
    brand: str
    model: str

class ChatRequest(BaseModel):
    id: str
    query: str

MODEL = ['mistral','qwen2.5','llama2-uncensored','llama3.2','phi4','gemma2','deepseek-r1']

class OllamaBot:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.brand = {'content':'','id':None}
        self.rags =[]
        self.ctx = [{
            'role': 'system',
            'content': '你是一个广告文案写作assistant，根据user提供的案例，写出类似风格的广告文案。'
        }]
        self.start = True

        try:
            self.conn = mariadb.connect(
                user="root",
                password="v",
                host="127.0.2.1",
                port=3306,
                database="ads"
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        self.cur = self.conn.cursor()

    def ragFile(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n\n') 
            for block in lines:
                lines_in_block = block.splitlines()
                if len(lines_in_block) >= 3:
                    field1 = lines_in_block[0].strip()
                    field2 = lines_in_block[1].strip()
                    field3 = lines_in_block[2].strip()
                    field4 = "\n".join(lines_in_block[3:]).strip() if len(lines_in_block) > 3 else ''

                    iq = '''INSERT INTO advertise_768 ({}) VALUE ({})'''
                    vls = []

                    if len(field1) >5:
                        iq=iq.format('org,v_org,{}','%s,Vec_FromText(%s),{}')
                        vls+=[field1, self.embed(field1)]
                    if len(field2) >5:
                        iq=iq.format('zh,v_zh,{}','%s,Vec_FromText(%s),{}')
                        vls+=[field2, self.embed(field2)]
                    if len(field3) >5:
                        iq=iq.format('brand,v_brand,{}','%s,Vec_FromText(%s),{}')
                        vls+=[field3, self.embed(field3)]

                    if len(field4) >5:
                        iq=iq.format('`comment`,v_comment','%s,Vec_FromText(%s)')
                        vls+=[field4, self.embed(field4)]
                    else:
                        iq=iq.format('','')

                    iq=iq.replace(',)', ')')
                    if len(vls) >1:
                        print(iq,vls[::2])
                        self.cur.execute(iq, vls)
                        self.conn.commit() 
        
        # conn.close()

    def setModel(self, model):
        if model not in MODEL:
            return False
        print(f"set model: {model}")
        self.model = model
        return True 

    async def onBrand(self, brand, user_id):
        try: 
            self.cur.execute("INSERT INTO `brand` (`content`) VALUE (?)", (brand,)) 
        except mariadb.Error as e: 
            print(f"mariadb Error: {e}")
        self.conn.commit()
        self.brand = { 'content':brand, 'id': self.cur.lastrowid }
        print(f"set brand : {self.cur.lastrowid}:{brand}")

        content = '你是一个广告文案写作assistant，根据user提供的案例，写出类似风格的广告文案。'
        params = (int(user_id), self.model, 'system', self.cur.lastrowid, '', '', content)
        system_store = asyncio.create_task(self.storeCtx(params)) 

        qs = '''SELECT id FROM advertise_768 where brand is not null and zh is not null
        ORDER BY VEC_Distance_Euclidean(v_brand, Vec_FromText(%s)) limit 30;'''
        self.cur.execute(qs, [self.embed(brand)])
        self.rags = [id[0] for id in self.cur]
        self.start = True
        self.ctx = [{'role': 'system','content': content}]
        return await system_store


    def pushCtx(self, msg):
        self.ctx.append(msg)

    def embed(self, text):
        res = ollama.embeddings(model='shaw/dmeta-embedding-zh', prompt=text)
        return str(res['embedding'])

    async def storeCtx(self, context):
        try: 
            self.cur.execute('''INSERT INTO `context` (`uid`, `model`, `role`, `brand_id`, `ip`, `user_agent`, `content`) 
            VALUE (?, ?, ?, ?, ?, ?, ?);''', context) 
        except mariadb.Error as e: 
            print(f"mariadb Error: {e}")
            return False
        self.conn.commit()
        return True

    async def chat(self, query, user_id, ip='', user_agent=''):
        context = query
        if self.start:
            self.start = False
            qs = '''SELECT id FROM advertise_768 where brand is not null and zh is not null
            ORDER BY VEC_Distance_Euclidean(v_zh, Vec_FromText(%s)) limit 30;'''
            self.cur.execute(qs, [self.embed(query)])
            words = [id[0] for id in self.cur]
            ids = tuple(set(self.rags) & set(words))
            if len(ids) > 0:
                qs = f'''SELECT zh,brand FROM advertise_768 where id in {str(ids)};'''
                self.cur.execute(qs)
                ads = ["广告文案： "+it[0] +"       品牌或产品： "+it[1] for it in self.cur]
                context = f"\n".join(ads) + f"\n\n上面是{len(ids)}则优秀的广告文案案例。请参考他们,写一则风格以及长度和这些案例相似的{self.brand['content']}广告文案。具体要求如下: \n {query}"
        
        self.ctx.append({'role': 'user', 'content': context})
        params = (int(user_id), self.model, 'user', self.brand['id'], ip, user_agent, context)
        user_store = asyncio.create_task(self.storeCtx(params)) 
        tmp = ""
        shutup = True if self.model=="deepseek-r1" else False
        for chunk in ollama.chat(model=self.model, stream=True, messages=self.ctx):
            if chunk:
                print(chunk.message.content)
                tmp = tmp + chunk.message.content
                if shutup == False:
                    yield chunk.message.content
                if shutup and "</think>" in chunk.message.content:
                    shutup = False
            await asyncio.sleep(0)
            
        self.ctx.append({'role': 'assistant', 'content': tmp})
        # pprint.pp(self.ctx)
        params = (int(user_id), self.model, 'assistant', self.brand['id'], '', '', tmp)
        assistant_store = asyncio.create_task(self.storeCtx(params)) 
        if len(self.ctx)>16:
            self.ctx = self.ctx[-10:]

        await user_store
        await assistant_store

@app.post("/setup")
async def setup(req: SetupRequest):
    if req.model not in MODEL:
        raise HTTPException(status_code=404, detail="该模型暂不支持，请联系管理员!")
    user_id = req.id
    if len(req.id)<4:
        ts = round((datetime.now().timestamp()- 1734480000)*1000000)
        user_id = str(ts)
    if req.id not in user_bots:
        user_bots[user_id] = OllamaBot()
    bot = user_bots[user_id]
    brand_task = asyncio.create_task(bot.onBrand(req.brand, user_id))
    if not bot.setModel(req.model):
        return {"code":2,"msg":"设置模型失败！", "id":user_id}
    if not await brand_task:
        return {"code":1,"msg":"设置产品行业失败！", "id":user_id}
    return {"code":0,"msg":"ok", "id":user_id, "model":bot.model, "brand":req.brand}

@app.post("/chat")
async def chat(request: Request, req: ChatRequest):
    user_id = req.id
    if user_id not in user_bots:
        # return {"code":1,"msg":"User id 错误，请刷新网页重新获取。"}
        raise HTTPException(status_code=404, detail="用户id 错误，请刷新网页重新获取。")
    bot = user_bots[user_id]
    return StreamingResponse(
        bot.chat(req.query, user_id, request.client.host, request.headers.get("user-agent")),
        media_type="text/event-stream" 
    )
class RagRequest(BaseModel):
    borl:str | None = None
    content:str

@app.post("/rag")
def rag(req:RagRequest):
    return {"code":0,"msg":"ok!"}

@app.get("/")
def index(req: Request):
    return {"code":0,"msg":"ok!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


#  uvicorn fmt3r:app --host 0.0.0.0 --port 8000 --reload