from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from docx import Document

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← allows ALL origins (okay for dev, restrict in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    user_input: str

def load_about_me_from_docx(path="About Tati.docx"):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

about_me_text = load_about_me_from_docx("About Tati.docx")

@app.get("/")
def read_root():
    return {"message": "BrimmBot is running!"}  # ✅ FIXED HERE

@app.post("/chat")
def chat_with_brimmbot(message: Message):
    system_prompt = f"""
    You are BrimmBot, a chill and friendly portfolio assistant for Tatiana Brimm.

    Tatiana is a Clinical Informatics major with strong backend coding skills, self-taught in tech.
    She is passionate about AI, automation, and game development.
    She's working on data analysis, AI agents, full-stack development, and building tools to help small businesses.
    She loves animals and plays guitar.
    You help visitors learn more about Tatiana, her skills, her projects, and her goals.
    You keep replies under 3 sentences unless more is requested.

    If needed, here’s extra context pulled from her personal notes:
    ---
    {about_me_text}
    ---
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message.user_input}
        ],
        max_tokens=150  # 🔹 Add this to control reply length
    )

    return {"reply": response.choices[0].message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
