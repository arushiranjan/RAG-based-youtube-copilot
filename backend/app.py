from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import create_vector_store, ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    video_id: str

class AskRequest(BaseModel):
    video_id: str
    question: str

@app.get("/")
def home():
    return {
        "message": "YouTube Copilot Backend Running"
    }


@app.post("/process-video")
def process_video(req: VideoRequest):

    create_vector_store(req.video_id)

    return {
        "status":"indexed"
    }


@app.post("/ask")
def ask(req: AskRequest):

    answer = ask_question(
        req.video_id,
        req.question
    )

    return {
        "answer":answer
    }