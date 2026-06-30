from pydantic import BaseModel, ConfigDict
from typing import List,Optional
from datetime import datetime


# user schema (outgoing)
class UserBase(BaseModel):
    username:str
    email:str

class UserCreate(UserBase):
    password:str

# incoming
class UserResponse(UserBase):
    id:int
    is_admin:bool

    model_config=ConfigDict(from_attributes=True)


# Problem
class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: str = "Medium"


class ProblemCreate(ProblemBase):
    pass


class ProblemResponse(ProblemBase):
    id: int
    solved_count:int
    # "If you are given a SQLAlchemy Object, read it like a Dictionary."
    model_config = ConfigDict(from_attributes=True)


# Test Cases
class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_hidden: bool = True

class TestCaseCreate(TestCaseBase):
    problem_id: int

class TestCaseResponse(TestCaseBase):
    id: int
    problem_id: int

    model_config = ConfigDict(from_attributes=True)



# Submission
class SubmissionBase(BaseModel):
    language: str
    code: str

class SubmissionCreate(SubmissionBase):
    problem_id: int

class SubmissionResponse(SubmissionBase):
    id: int
    problem_id: int
    user_id: int
    status: str
    submitted_at: datetime # Fastapi will automatically format this to a standard ISO date string
    
    model_config = ConfigDict(from_attributes=True)