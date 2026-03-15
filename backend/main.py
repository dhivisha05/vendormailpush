from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
import asyncio

app = FastAPI(title="RFQ Procurement API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup():
    print("Backend started in Fallback Mode (No Database).")

@app.get("/")
def read_root():
    return {"message": "RFQ Procurement API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
