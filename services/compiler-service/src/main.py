from fastapi import FastAPI
from .api.compile import router

app = FastAPI(title="SecureVibe Compiler Service", version="2.0.0")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "compiler"}
