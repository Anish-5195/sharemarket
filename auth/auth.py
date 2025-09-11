from fastapi import APIRouter, Depends, HTTPException,Body, Request, Form
from sqlalchemy.orm import Session
from schemas.user import UserCreate,Token,UserUpdate,UserOut
from crud.user import get_user_by_email, create_user
from utils.utils import get_current_user
from db.session import get_db
from core.security import verify_password, create_access_token,hash_password,create_refresh_token
from models.user import User, RoleEnum
from core.deps import require_admin,oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta,datetime
from utils.email_service import send_reset_email
from core.config import settings
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import secrets, datetime
from core.deps import require_permission
from core.config import Settings

router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="templates")
@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # check if email already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # check if mobile already exists
    existing_mobile = db.query(User).filter(User.mobile == user.mobile).first()
    if existing_mobile:
        raise HTTPException(status_code=400, detail="User with this mobile already exists")

    # backend mein token generate hoga
    verification_token = secrets.token_urlsafe(32)

    # create user
    new_user = create_user(
        db=db,
        email=user.email,
        name=user.name,
        mobile=user.mobile,
        password=user.password,
        verified=False,
        verification_token=verification_token,
    )

    return new_user



# for webhook handler
# @router.post("/webhook-handler")
# async def webhook_handler(request: Request):
#     try:
#         payload = await request.json()
#     except Exception:
#         payload = {}
#     print("Webhook received:", payload)  
#     return {"status": "ok"}


from models.user import WebhookData
@router.post("/webhook-handler",include_in_schema=False)
async def webhook_handler(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    
    # Print in terminal
    print("Webhook received:", payload)
    
    # Save in DB
    if payload:
        webhook_entry = WebhookData(
            stocks=payload.get("stocks"),
            trigger_prices=payload.get("trigger_prices"),
            triggered_at=payload.get("triggered_at"),
            scan_name=payload.get("scan_name"),
            scan_url=payload.get("scan_url"),
            alert_name=payload.get("alert_name"),
            webhook_url=payload.get("webhook_url"),
        )
        db.add(webhook_entry)
        db.commit()
        db.refresh(webhook_entry)
        print(f"Saved to DB with id: {webhook_entry.id}")
    
    return {"status": "ok"}




@router.post("/verify")
def send_verification_email(email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.verified:
        return {"msg": "User already verified"}

    token = secrets.token_urlsafe(32)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)

    user.verification_token = token
    user.token_expiry = expiry
    db.commit()

    # link for user
    link = f"{settings.BACKEND_URL}/verify-page?token={token}"
    body = f"Click here to verify your account: {link}\nThis link is valid for 1 minutes."
    send_reset_email(user.email, "Verify your account", body)

    return {"msg": "Verification email sent"}


# 2) Update GET /verify-page to directly verify
@router.get("/verify-page", response_class=HTMLResponse, include_in_schema=False)
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user or user.token_expiry < datetime.datetime.utcnow():
        return HTMLResponse("<h3>Invalid or expired link</h3>", status_code=400)

    user.verified = True
    user.verification_token = None
    user.token_expiry = None
    db.commit()

    return HTMLResponse("<h3>Email verified successfully! Now you can login</h3>")



@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.verified:
        raise HTTPException(status_code=403, detail="First verify your email, then login")

    # 1 Access token generate
    access_token = create_access_token(
        data={"sub": db_user.email},
        role=db_user.role.value
    )

    # 2 Refresh token automatically generate
    refresh_token = create_refresh_token(
        data={"sub": db_user.email}
    )

    # 4 Return both tokens in response
    return {
        "access_token": access_token,
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }



@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # New access token
    access_token = create_access_token(
        data={"sub": db_user.email},
        role=db_user.role.value
    )

    # Optionally new refresh token
    new_refresh_token = create_refresh_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }





#  Admin can promote (admin) of any user
@router.put("/promote/{user_email}")
def promote_user(user_email: str, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == RoleEnum.admin:
        raise HTTPException(status_code=400, detail="User is already an admin")
    
    user.role = RoleEnum.admin
    db.commit()
    db.refresh(user)
    return {"msg": f"User {user.email} promoted to admin"}



token_blacklist = set()

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    #  Add token to blacklist
    token_blacklist.add(token)

    #  Decode token to get user email
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        user_email = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from DB
    db_user = get_user_by_email(db, user_email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"msg": "Logged out successfully"}




#  User/Admin Can check his profile
@router.get("/profile",dependencies=[Depends(require_permission("user"))])
def read_profile(current_user: User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "mobile": current_user.mobile,
        "role": current_user.role
    }



#  User/admin can update his profile
@router.put("/Updateprofile")
def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update only fields that are provided
    if updates.name is not None:
        current_user.name = updates.name
    if updates.email is not None:
        existing_user = db.query(User).filter(User.email == updates.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = updates.email
    if updates.mobile is not None:
        current_user.mobile = updates.mobile
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "name": current_user.name,
        "email": current_user.email,
        "mobile": current_user.mobile,
    }


import random, datetime
reset_codes = {}  # { "user@email.com": {"code": "123456", "expiry": datetime } }


# 1. Request Password Reset
@router.post("/request-password-reset")
def request_password_reset(email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    code = str(random.randint(100000, 999999))
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    reset_codes[email] = {"code": code, "expiry": expiry}

    send_reset_email(
        user.email,
        "Password Reset Code",
        f"Your password reset code is: {code}\nThis code is valid for 10 minutes."
    )

    return {"msg": "Password reset code sent to your email"}


# 2. Reset Password with OTP
@router.post("/reset-password")
def reset_password(
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if email not in reset_codes:
        raise HTTPException(status_code=400, detail="No reset request found")

    otp_data = reset_codes[email]
    if otp_data["code"] != code:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    if otp_data["expiry"] < datetime.datetime.utcnow():
        del reset_codes[email]
        raise HTTPException(status_code=400, detail="Reset code expired")

    # Update password
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)

    # cleanup
    del reset_codes[email]

    return {"msg": "Password reset successful"}

