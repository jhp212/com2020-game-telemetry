from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database.database import get_db # type: ignore
from database.models import Users
from database import schemas
from database.security import get_password_hash, verify_password, create_access_token, get_current_user, get_current_admin_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password validation function to enforce strong password policies
# Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if " " in password:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for c in password)
    return has_upper and has_lower and has_digit and has_special

# Username validation function to ensure usernames are alphanumeric and of appropriate length
# Usernames must be between 3 and 20 characters long and contain only letters, numbers, and dashes/underscores
def is_valid_username(username: str) -> bool:
    if len(username) < 3 or len(username) > 20:
        return False
    return all(c.isalnum() or c in "-_" for c in username)

# Registration endpoint - creates a new user with hashed password
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not is_valid_username(user.username):
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters long and contain only alphanumeric characters")
    if not is_valid_password(user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character")
    
    existing = db.query(Users).filter(Users.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = get_password_hash(user.password)
    db_user = Users(username=user.username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Login endpoint - verifies credentials and returns User ID and JWT token
@router.post("/token", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"user_id": db_user.id, "access_token": access_token, "token_type": "bearer", "is_admin": db_user.is_admin}

# Endpoint for users to request admin access. Only that user can make this request
@router.post("/request_admin")
def request_admin_access(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if user.is_admin == 1: # type: ignore
        raise HTTPException(status_code=400, detail="User is already an admin")
    if user.is_requesting_admin == 1: # type: ignore
        raise HTTPException(status_code=400, detail="Admin access already requested.")

    user.is_requesting_admin = 1 # type: ignore
    db.commit()
    db.refresh(user)
    return {"username": user.username, "is_requesting_admin": user.is_requesting_admin} # type: ignore

# Admin endpoint to promote a user to admin status. Only accessible by existing admins.
@router.post("/promote/{username}")
def promote_user_to_admin(username: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin == 1: # type: ignore
        raise HTTPException(status_code=400, detail="User is already an admin")
    
    user.is_admin = 1 # type: ignore
    user.is_requesting_admin = 0 # type: ignore
    db.commit()
    db.refresh(user)
    return {"username": user.username, "is_admin": user.is_admin}

# Admin endpoint to reject a user's admin request. Only accessible by existing admins.
@router.post("/reject_admin/{username}")
def reject_admin_request(username: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin == 1: # type: ignore
        raise HTTPException(status_code=400, detail="User is already an admin")
    if user.is_requesting_admin == 0: # type: ignore
        raise HTTPException(status_code=400, detail="User has not requested admin access")

    user.is_requesting_admin = 0 # type: ignore
    db.commit()
    db.refresh(user)
    return {"username": user.username, "is_requesting_admin": user.is_requesting_admin}

# Endpoint to delete the current user's account and all associated data. Only that user can make this request
@router.delete("/delete_account")
def delete_user_account(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"detail": f"User '{current_user.username}' and all associated data have been deleted."}