from fastapi import APIRouter, Depends, status, HTTPException
from app import schemas, models, utils, oauth2
from app.database import get_db
from sqlalchemy.orm import Session


router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/",response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)

def create_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    # check existings
    existing=db.query(models.User).filter(models.User.email == user.email).first()
    if(existing):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    existing_username=db.query(models.User).filter(models.User.username == user.username).first()
    if(existing_username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    # hash password
    #Pydantic
    hashed_pwd=utils.hashed(user.password)

    #create user
    #SQLAlchemy Model
    new_user=models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=schemas.UserResponse)
def get_user_profile(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user

    
    