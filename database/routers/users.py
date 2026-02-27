from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db # type: ignore
from models import Users
import schemas
from security import get_current_admin_user

router = APIRouter(prefix="/users", tags=["Users"])

# Get all users (Admin only)
@router.get("", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    return db.query(Users).all()

# Delete a user by username (Admin only)
@router.delete("/{username}")
def delete_user(username: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin == 1: # type: ignore
        raise HTTPException(status_code=400, detail="Cannot delete an admin user")
    db.delete(user)
    db.commit()
    return {"detail": f"User '{username}' has been deleted."}

# Get all users who have requested admin access (Admin only)
@router.get("/admin_requests", response_model=list[schemas.UserResponse])
def get_admin_requests(db: Session = Depends(get_db), current_user: Users = Depends(get_current_admin_user)):
    return db.query(Users).filter(Users.is_requesting_admin == 1).all()