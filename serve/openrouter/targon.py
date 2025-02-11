from openai import OpenAI

client = OpenAI(
    base_url="https://api.targon.com/v1",
    api_key="sn4_iw7faaemk5yv4cw1sbds9qe61cra"
)

try:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        stream=True,
        messages=[
            {"role": "system", "content": "You are a helpful programming assistant."},
            {"role": "user", "content": "Write a bubble sort implementation in Python with comments explaining how it works"}
        ],
        temperature=0.7,
        max_tokens=256,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
except Exception as e:
    print(f"Error: {e}")


from openai import OpenAI
  
  client = OpenAI(
      base_url="https://api.targon.com/v1",
      api_key="sn4_iw7faaemk5yv4cw1sbds9qe61cra"
  )
  
  try:
      response = client.completions.create(
          model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
          stream=True,
          prompt="The x y problem is",
          temperature=0.7,
          max_tokens=256,
          top_p=0.1,
          frequency_penalty=0,
          presence_penalty=0
      )
      for chunk in response:
          if chunk.choices[0].text is not None:
              print(chunk.choices[0].text, end="")
  except Exception as e:
      print(f"Error: {e}")