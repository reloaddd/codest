from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/testcases",
    tags=["Test Cases"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TestCaseResponse)
def create_test_case(
    testcase: schemas.TestCaseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user) # Locked Door!
):
   
    # Verify the problem exists before adding a test case to it
    problem = db.query(models.Problem).filter(models.Problem.id == testcase.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Problem with ID {testcase.problem_id} does not exist"
        )
    
    # 2. Build the SQLAlchemy Model
    new_testcase = models.TestCase(
        problem_id=testcase.problem_id,
        input_data=testcase.input_data,
        expected_output=testcase.expected_output,
        is_hidden=testcase.is_hidden
    )
    
    
    db.add(new_testcase)
    db.commit()
    db.refresh(new_testcase)
    
    return new_testcase

@router.get("/problem/{problem_id}", response_model=List[schemas.TestCaseResponse])
def get_test_cases_for_problem(
    problem_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Fetches all test cases for a specific problem.
    """
    test_cases = db.query(models.TestCase).filter(models.TestCase.problem_id == problem_id).all()
    return test_cases