#Step 4 -- LLM Summarization Logic
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_chunk(chunk: str) -> str:
    time.sleep(0.5)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": f"Summarize this section of a research paper:\n\n{chunk}"}
        ]
    )
    return response.choices[0].message.content

def generate_final_summary(partial_summaries: list[str]) -> str:
    combined = "\n\n".join(partial_summaries)
    prompt = f"""Based on these section summaries, generate a structured summary with:
- Overview
- Methodology
- Key Contributions
- Results
- Limitations
- Future Work

Text:
{combined}"""
    time.sleep(0.5)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content