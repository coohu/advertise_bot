from openai import OpenAI
import mariadb, json, time


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

def send(msg, target='en'):
    content = f"{msg}.\n\n这是一句广告文案，把它翻译成中文。请先考虑多种翻译法，最后选择一个最传神的翻译返回。不需要其他内容。"
    if target == "cn":
        content = f"{msg}.\n\n这是一句广告文案，把它翻译成英文。请先考虑多种翻译法，最后选择一个最传神的翻译返回。不需要其他内容。"

    try:
        completion = client.chat.completions.create(
        #   extra_headers={
        #     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        #     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        #   },
            # response_format={"type": "json_object"},
            model="google/gemini-2.0-pro-exp-02-05:free",
            temperature=1,
            stream = False,
            messages=[{"role": "user", "content": content}
            # {
            #   "role": "user",
            #   "content": [
            #     {
            #       "type": "text",
            #       "text": "What's in this image?"
            #     },
            #     {
            #       "type": "image_url",
            #       "image_url": {
            #         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            #       }
            #     }
            #   ]
            # }
            ]
        )
    except Exception as e:
        print(f"Error Chat: {e}")
        return ''
    if completion.error:
        print(completion.error.get('message'))
        exit()
    if completion.choices:
        return completion.choices[0].message.content
    return ''

# send("Just do it!", target="en")
# exit()

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
cur.execute('SELECT org, zh, id FROM advertise_768 where org is null or zh is null;')

def tran(id, res, seg):
    try: 
        cur.execute(f'UPDATE `advertise_768` SET `{seg}` = ? WHERE id = ?;', (res,id))
    except mariadb.Error as e: 
        print(f"mariadb Error: {e}")
        return False 
    conn.commit()
    return True

rst = cur.fetchall()
print(rst)
for it in rst:
    if it[0]:
        res = send(it[0], target="en")
        if not len(res):
            continue
        if tran(it[2], res, 'zh'):
            print(f"{it[0]}\t\t->\t\t{res}")
    else:
        res = send(it[1], target="cn")
        if not len(res):
            continue
        if tran(it[2], res, 'org'):
            print(f"{it[1]}\t\t->\t\t{res}")
    time.sleep(3)
