from fastapi import APIRouter, Depends
from app import schemas, models
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

# any router in this file will have /problems/route
router=APIRouter(prefix="/problems", tags=["Problems"])

@router.post("/",response_model=schemas.ProblemResponse)

def create_problem(problem: schemas.ProblemCreate, db:Session=Depends(get_db)):
    db_problem=models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty
    )

    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)

    return db_problem

@router.get("/", response_model=List[schemas.ProblemResponse])

def get_problems(skip: int=0, limit: int=100, db:Session=Depends(get_db),search: Optional[str] = "",
    difficulty: Optional[str] = None
):
    query=db.query(models.Problem)
    if search:
        query=query.filter(models.Problem.title.ilike(f"%{search}%"))
    if difficulty:
        query=query.filter(models.Problem.difficulty==difficulty)
    problems=query.offset(skip).limit(limit).all()
    return problems