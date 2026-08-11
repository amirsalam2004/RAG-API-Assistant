from openai import OpenAI
import os
from app.base_prompts import translate_text_prompt, Description_Summarizer, detect_language_prompt
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def llm_call(state, prompt, temperature=0):
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",  
        messages=[
            {"role": "system", "content": state.SYSTEM_CONTEXT},
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

def generate_api_info(description, temperature=0):
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",  
        messages=[
            {"role": "system", "content": Description_Summarizer},
            {"role": "user", "content": description}
        ],
        temperature=temperature,
        extra_headers={
            "HTTP-Referer": "http://localhost", 
            "X-Title": "RAG API Assistant"      
        }
    )

    return response.choices[0].message.content

def detect_language(text):
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        messages=[
            {"role": "system", "content": detect_language_prompt},
            {"role": "user", "content": text }
        ],
        temperature=0,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "RAG API Assistant"
        }
    )
    return response.choices[0].message.content.strip().lower()

def translate_text(text, target_lang):

    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        messages=[
            {"role": "system", "content": translate_text_prompt(target_lang)},
            {"role": "user", "content": text}
        ],
        temperature=0,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "RAG API Assistant"
        }
    )
    return response.choices[0].message.content