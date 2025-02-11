import mariadb, ollama
import requests, pprint, json, sys
import streamlit as st
class OllamaBot:
    def __init__(self, model):
        self.model = model
        self.brand = [] 
        if "start" not in st.session_state:
            st.session_state.start = True
        self.start = st.session_state.start
        
        if "ctx" not in st.session_state:
            st.session_state.ctx = [{
                'role': 'system',
                'content': '你是一个广告文案写作assistant，根据user提供的案例，写出类似风格的广告文案。'
            }]
        self.ctx = st.session_state.ctx
        res = ollama.embeddings(model='shaw/dmeta-embedding-zh', prompt="hi")
        self.tSize = len(res['embedding'])
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
            sys.exit(1)

        self.cur = self.conn.cursor()

    def setModel(self, model):
        self.model = model

    def onBrand(self, brand):
        qs ='''SELECT id FROM advertise_768 where brand is not null and zh is not null
        ORDER BY VEC_Distance_Euclidean(v_brand, Vec_FromText(%s)) limit 30;'''
        self.cur.execute(qs, [self.embed(brand)])
        self.brand = [id[0] for id in self.cur]
        # print(self.brand)

        self.start = True
        self.ctx = [{
            'role': 'system',
            'content': '你是一个广告文案写作assistant，根据user提供的案例，写出类似风格的广告文案。'
        }]

    def pushCtx(self, msg):
        self.ctx.append(msg)

    def embed(self, text):
        res = ollama.embeddings(model='shaw/dmeta-embedding-zh', prompt=text)
        return str(res['embedding'])


    def read_txt_file(self, file_path):
        records = []
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

    def chat(self, query):
        context = query
        print('\n\n\tstart: ',self.start, '\tmodel: : ',self.model, '\tlen(ctx): ', len(self.ctx))
        if self.start == True:
            self.start = False
            qs =f'''SELECT id FROM advertise_768 where brand is not null and zh is not null
            ORDER BY VEC_Distance_Euclidean(v_zh, Vec_FromText('%s')) limit 30;'''
            self.cur.execute(qs, self.embed(query))
            words = [id[0] for id in self.cur]

            ids = tuple(set(self.brand) & set(words))
            if len(ids)>0:
                qs =f'''SELECT zh FROM advertise_768 where id in {str(ids)};'''
                self.cur.execute(qs)
                ads = [zh[0] for zh in self.cur]
                context =  f"{"\n".join(ads)}\n\n以上共{len(ids)}则优秀的广告文案案例，每行一则。请参考他们,写一则风格以及长度和案例相似的广告。具体要求如下: \n {query}"

        self.ctx.append({'role': 'user','content': context})
        pprint.pp(self.ctx )
        print('-------------------------------')
        return ollama.chat(model=self.model, stream=True, messages=self.ctx)

# query = "写一个芬达饮料的广告文案，要求突出家庭元素"
# answer = generate_answer(query,'饮料')
# # if answer.status_code != 200:
# #     raise Exception(f"Error: {response.status_code} - {response.text}")
# for chunk in answer:
#     if chunk:
#         # data = chunk.decode("utf-8")
#         print(chunk.message.content, end="", flush=True)



# print("数据已成功导入到数据库！")
# ALTER TABLE advertise AUTO_INCREMENT = 1;
# CREATE TABLE IF NOT EXISTS `v_advertise` (
#   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
#   `org` text DEFAULT NULL,
#   `zh` text DEFAULT NULL,
#   `brand` text DEFAULT NULL,
#   `comment` text DEFAULT NULL,
#   `v_org` VECTOR(768) DEFAULT NULL,
#   `v_zh` VECTOR(768) DEFAULT NULL,
#   `v_brand` VECTOR(768) DEFAULT NULL,
#   `v_comment` VECTOR(768) DEFAULT NULL,
#   `created` timestamp NOT NULL DEFAULT current_timestamp(),
#   PRIMARY KEY (`id`)
# ) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;