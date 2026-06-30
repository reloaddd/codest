from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, oauth2, engine
from app.database import get_db

from app.worker import submission_task

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SubmissionResponse)
def create_submission(
    submission: schemas.SubmissionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user) # <-- The Security Guard!
):
    
    problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Problem with ID {submission.problem_id} does not exist"
        )

    
    new_submission = models.Submission(
        code=submission.code,
        language=submission.language,
        problem_id=submission.problem_id,
        user_id=current_user.id,
        status="Pending"
    )

    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)


    #celery worker
    submission_task.delay(new_submission.id)



    return new_submission

@router.get("/", response_model=List[schemas.SubmissionResponse])
def get_all_submissions(db: Session = Depends(get_db)):
    """
    Get a list of all submissions. (Open to everyone for the leaderboard)
    """
    submissions = db.query(models.Submission).order_by(models.Submission.submitted_at.desc()).all()
    return submissions