from fastapi import APIRouter, Depends, HTTPException
import crud,schemas
from database import local_session
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/register/",response_model=schemas.User_Out)
def register_user(user:schemas.User_Create,db:Session= Depends(get_db)):
    user_exists = crud.check_user_by_username(db,user.username)
    if user_exists:
        raise HTTPException(status_code=400,detail="Username already exists")    
    return crud.create_user(db,user)

@router.post("/login/")
def login_user(user:schemas.User_Login,db:Session = Depends(get_db)):
    db_user = crud.check_user_by_username(db,user.username)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=404,detail="Invalid Credentials")
    return {"message":"logged in successfully"}

@router.get("/list_users/",response_model=list[schemas.User_Out])
def list_users(db:Session = Depends(get_db)):
    return crud.get_all_users(db)

@router.delete("/delete_user/{user_id}")
def delete_user(user_id:int, db:Session = Depends(get_db)):
    deleted_user = crud.delete_user_by_id(db,user_id)
    if not deleted_user:
        raise HTTPException(status_code=404,detail="user not found")
    return {"message":"user deleted successfully"}

@router.put("/update_use/{user_id}")
def update_user(user_id:int,updated_user:schemas.User_Create, db:Session = Depends(get_db)):
    update_user = crud.update_user_by_id(db,user_id,updated_user)
    if not update_user:
        raise HTTPException(status_code=404,detail="user not found")
    return update_user