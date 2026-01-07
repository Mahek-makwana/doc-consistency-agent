from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse(content="<h1>Server is LIVE</h1><p>If you see this, the routing is working. Proceeding to restore dashboard logic.</p>")

@app.get("/health")
async def health():
    return {"status": "ok"}
