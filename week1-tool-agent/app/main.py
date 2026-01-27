# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(question: str):
    result = agent.run(question)
    return {"answer": result}
