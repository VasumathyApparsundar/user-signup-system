from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import db, models, kafka_producer

models.Base.metadata.create_all(bind=db.engine)

app = FastAPI()

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    address_line: str
    city: str
    state: str
    zip: str

@app.post("/signup")
def signup(user: SignupRequest):
    session = db.SessionLocal()
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    new_address = models.Address(
        user_id=new_user.id,
        address_line=user.address_line,
        city=user.city,
        state=user.state,
        zip=user.zip
    )
    session.add(new_address)
    session.commit()

    kafka_producer.send_signup_event(user.email)

    return {"message": "Signup successful"}
