from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import api_router
from app.core.database import create_tables
import os

# 创建数据库表
create_tables()

app = FastAPI(
    title="MetaIgnite AI",
    description="AI Employee for Validating and Implementing Creative Ideas with OAuth Authentication.",
    version="1.0.0"
)

# CORS配置
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to the MetaIgnite AI API V1 with OAuth Authentication!"}