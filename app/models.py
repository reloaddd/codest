from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Text, Boolean, String, DateTime, Integer, ForeignKey
from app.database import Base

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    submissions=relationship("Submission", back_populates="user")

class Problem(Base):
    __tablename__="problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, default="Medium") # e.g., Easy, Medium, Hard
    solved_count = Column(Integer, default=0)
    
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions=relationship("Submission", back_populates="problem")

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=True) 

    problem = relationship("Problem", back_populates="test_cases")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    
    
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False) # e.g., "python", "cpp"
    
    
    status = Column(String, default="Pending") 
    
    # The crucial timestamp for offline contest!
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")