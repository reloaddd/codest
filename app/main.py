from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

from app.routers import problems, users,auth, submissions, test_cases, websockets, leaderboard

# Create all tables in the database
# For production, we will use a tool called Alembic for this
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Codest API",
    description="Backend for the isolated code execution engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(problems.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(submissions.router)
app.include_router(test_cases.router)
app.include_router(websockets.router)
app.include_router(leaderboard.router)

#check
@app.get("/")
def read_root():
    return {"status": "Codest API is running"}

