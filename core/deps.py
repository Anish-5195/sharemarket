from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import settings
from utils.utils import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user_role(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        role: str = payload.get("role")
        if role is None:
            raise HTTPException(status_code=401, detail="Role missing in token")
        return role
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_admin(role: str = Depends(get_current_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return role




def require_permission(required_role: str):
    def wrapper(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_role}' required"
            )
        return current_user
    return wrapper
