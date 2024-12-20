import os
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

SECURE_COOKIE = os.getenv("SECURE_COOKIE", "True").lower() == "true" 

def create_cookie_response(message: str, token: str, max_age: int):
    response = JSONResponse({"message": message})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=max_age,
        secure=SECURE_COOKIE,
        samesite="Strict",
    )
    return response
