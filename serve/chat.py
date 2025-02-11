import streamlit as st
import pprint
import  fmt3

st.title("💬 广告 Bot")
st.markdown("""
<style>
    /* 去除页面的内边距 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .streamlit-expanderHeader {
        padding:0;
        margin:0;
    }
    .chat-message {
        padding:0;
        margin:0;
    }
    .stChatMessage{
        padding:0;
        margin:0;
    }
    h1{
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

if "bot" not in st.session_state:
    st.session_state.bot = fmt3.OllamaBot("mistral")
bot = st.session_state.bot 

col1, col2 = st.columns([3, 3])

if "chat_topic" not in st.session_state:
    st.session_state.chat_topic = "大力水手饮料"
with col1:
    chat_topic = st.text_input("💡 输入产品或行业", "大力水手饮料")
if chat_topic != st.session_state.chat_topic:
    st.session_state.chat_topic = chat_topic
    print(chat_topic)
    bot.onBrand(chat_topic)
bot.onBrand(chat_topic)

if "model_option" not in st.session_state:
    st.session_state.model_option = "Mistral AI"
with col2:
    model_option = st.selectbox("👤 选择模型：", ["Mistral AI", "Gemma2", "通义千问2.5", "羊驼2纯真版", "羊驼3.2", "phi-4"])
if model_option != st.session_state.model_option:
    st.session_state.model_option = model_option
    model = "mistral"
    if model_option == "Mistral AI":
        model = "mistral"
    if model_option == "通义千问2.5":
        model = "qwen2.5"
    if model_option == "羊驼2纯真版":
        model = "llama2-uncensored"
    if model_option == "羊驼3.2":
        model = "llama3.2"
    if model_option == "phi-4":
        model = "phi4"
    if model_option == "Gemma2":
        model = "gemma2"
    bot.setModel(model)
    print(bot.model,">>>>>>>>>>>>>>")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("说说你的要求吧...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("..."):
        response = bot.chat(user_input)
        res = '' 
        placeholder = st.empty() 
        for chunk in response:
            if chunk:
                res += chunk.message.content#.strip()
                placeholder.markdown(res)
        with st.chat_message("assistant"):
            st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        bot.pushCtx({"role": "assistant", "content": res})
        pprint.pp(bot.ctx)
        print('*************************************************')
        placeholder.markdown('')
            

