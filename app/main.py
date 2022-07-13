from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api.v1.api import router as v1_router


app = FastAPI()

origins = [
    "http://cimun.org",
    "https://cimun.org",
    "*-model-un.vercel.app"
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(v1_router, prefix="/api/v1")

handler = Mangum(app)
