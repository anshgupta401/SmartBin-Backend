from sqlalchemy.orm import Session
import models,schemas

def create_user(db:Session,user:schemas.User_Create):
    db_user = models.User(username = user.username,password = user.password,role =user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def check_user_by_username(db:Session,username:str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db:Session):
    return db.query(models.User).all()

def delete_user_by_id(db:Session, id:int):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def update_user_by_id(db:Session, id:int,updated_user:schemas.User_Create):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        user.username = updated_user.username
        user.password = updated_user.password
        user.role = updated_user.role
        db.commit()
        db.refresh(user)
        return user