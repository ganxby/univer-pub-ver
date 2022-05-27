from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from database import engine, SessionLocal

from passlib.context import CryptContext

import models
import crud
import schema


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def auth_user(db: Session, login: str, password: str):
    user = crud.get_user_by_login(db, login)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


@app.post('/add_user')
async def create_user(user: schema.User, db: Session = Depends(get_db)):
    check_user = crud.get_user_by_login(db, login=user.login)
    if check_user:
        raise HTTPException(status_code=400, detail='Login already registered')

    return crud.add_user(db=db, user=user)


@app.post("/check_user")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = auth_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {
        "login": user.login,
        "position": user.position
    }
