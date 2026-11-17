from ollama import chat
from groq import Groq
from dotenv import load_dotenv
import os 

load_dotenv()
MODEL = 'qwen3:4b-instruct-2507-q4_K_M'
MODE = "api" # "local"

class ModelError(Exception):
    pass

client = None

if MODE == "api":
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ModelError("GROQ_API_KEY is missing")

    client = Groq(api_key=api_key)



def ask(messages):
    if not MODE in ["api","local"]: 
        raise ModelError(f"Invalid mode: {MODE}")
    if MODE == "local":
        try:
            response = chat(
                model=MODEL,
                messages= messages,
                # options={"num_ctx":5016},  # uncomment if need to change the context length ; DEFAULT:4096
                think=False
            )
            return response.message.content
        except Exception as e: 
            raise ModelError(str(e)) from e
    else:
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=1,
                max_completion_tokens=2048,
                top_p=1,
                reasoning_effort="medium",
                stream=False,
                stop=None
            )

            return completion.choices[0].message.content
        except Exception as e : 
            raise ModelError(str(e)) from e


print(ask([{"role":"user", "content":"Whats 9+10?(meme version)"}]))



