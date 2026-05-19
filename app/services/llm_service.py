from openai import OpenAI
import os
from app.base_prompts import SYSTEM_CONTEXT
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def llm_call(prompt, temperature=0):
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",  
        messages=[
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        extra_headers={
            "HTTP-Referer": "http://localhost", 
            "X-Title": "RAG API Assistant"      
        }
    )

    return response.choices[0].message.content

def format_messages(messages):
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])