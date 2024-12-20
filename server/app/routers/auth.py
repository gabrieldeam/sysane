import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.utils.cookie_service import create_cookie_response
from app.services.auth import create_user, authenticate_user
from app.utils.hashing import hash_password
from app.email.send_email import send_verification_email
from app.models.user import User
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    
    db_user = create_user(db, user)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    verification_token = jwt.encode(
        {"sub": str(db_user.id), "exp": expire}, 
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    verification_url = f"{os.getenv('FRONTEND_URL')}/auth/verify-email?token={verification_token}"
    send_verification_email(db_user.email, db_user.name, verification_url)

    return {"message": "Usuário registrado. Verifique seu email para ativar a conta."}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=400, detail="Token inválido. 'sub' não encontrado no payload.")

        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email já verificado.")

        user.is_verified = True
        db.commit()

        login_token = create_access_token({"sub": str(user.id)})

        return create_cookie_response(
            message="Email verificado com sucesso",
            token=login_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expirado. Solicite um novo email de verificação.")
    except jwt.JWTError as e:
        raise HTTPException(status_code=400, detail=f"Erro no token: {str(e)}")


@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    reset_token = create_access_token({"sub": user.id})
    reset_url = f"{os.getenv('FRONTEND_URL')}/auth/reset-password?token={reset_token}"

    send_verification_email(user.email, user.name, reset_url)

    return {"message": "Email para redefinição de senha enviado com sucesso."}

# Redefinição de senha - Atualização da senha
@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token inválido.")

        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        user.hashed_password = hash_password(new_password)
        db.commit()

        login_token = create_access_token({"sub": str(user.id)})

        return create_cookie_response(
            message="Senha redefinida com sucesso",
            token=login_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expirado. Solicite um novo email de redefinição de senha.")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou malformado.")


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    login_token = create_access_token({"sub": str(db_user.id)})

    return create_cookie_response(
        message="Login realizado com sucesso",
        token=login_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.get("/email-exists")
def email_exists(email: str, db: Session = Depends(get_db)):
    """
    Verifica se o email já está cadastrado.
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        return {"exists": True, "message": "Email já está cadastrado."}
    return {"exists": False, "message": "Email não está cadastrado."}


@router.get("/is-email-verified")
def is_email_verified(email: str, db: Session = Depends(get_db)):
    """
    Verifica se o email está verificado.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {
        "is_verified": user.is_verified,
        "message": "Email verificado." if user.is_verified else "Email não verificado."
    }


@router.post("/resend-verification-email")
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    """
    Reenvia o email de verificação.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.is_verified:
        return {"message": "Email já foi verificado."}

    verification_token = create_access_token({"sub": str(user.id)})
    verification_url = f"{os.getenv('FRONTEND_URL')}/auth/verify-email?token={verification_token}"

    send_verification_email(user.email, user.name, verification_url)

    return {"message": "Email de verificação reenviado com sucesso."}

