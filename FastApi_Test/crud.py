from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
import schema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()


def add_user(db: Session, user: schema.User):
    login = user.login
    hashed_password = get_password_hash(user.password)
    position = user.position
    user_data = models.User(login=login, password=hashed_password, position=position)
    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    return {'status': 200,
            'message': 'User successfully registered'}
