from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.features.users.enums import UserRole
from app.shared.validators import validate_password_strength



# --- USER RESPONSES / READ ---
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    email_verified: bool

    full_name: str
    role: UserRole

    is_active: bool
    is_banned: bool
    ban_reason: str | None

    last_login_at: datetime | None
    last_seen_at: datetime 
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- USER CREATION ---
class UserCreate(BaseModel):
    email: EmailStr

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: Literal[UserRole.USER] = Field(
        default=UserRole.USER,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


# ****** USER ACTIONS INSIDE PROFILE ******

# --- USER PROFILE UPDATE ---
class UserUpdateProfile(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )


# --- USER EMAIL CHANGE ---
class UserEmailChangeRequest(BaseModel):
    """Request email change."""
    new_email: EmailStr

class UserEmailChangeWithToken(BaseModel):
    """Confirm email change using a one-time token."""
    token: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="One-time token from the email confirmation link",
    )


# --- USER PASSWORD CHANGE ---
class UserPasswordChangeWithToken(BaseModel):
    """Confirm password change using a one-time token."""

    token: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="One-time token from the email confirmation link",
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str,
    ) -> str:
        return validate_password_strength(value)
     

# ****** AUTH USER ACTIONS ******

# --- LOGIN ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

# --- EMAIL VERIFICATION ---
class VerifyEmailToken(BaseModel):
    token: str = Field(..., description="Secret one-time token from the email verification link")


# --- FORGOTTEN PASSWORD RECOVERY ---
class PasswordRecoveryRequest(BaseModel):
    """Step 1 of password recovery: The user enters their email address to receive a letter."""
    email: EmailStr


class PasswordResetWithToken(BaseModel):
    """Step 2 of password recovery: The user enters a new password using the link from the email."""
    token: str = Field(..., description="Secret one-time token from the link")
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_password_strength(value)

# ****** ADMIN USER ACTIONS ******

# --- ADMIN USER CREATE ---
class AdminUserCreate(UserCreate): 
    role: UserRole = Field(
            default=UserRole.USER,
        )


# --- ADMIN USER UPDATE ---
class AdminUpdateUserStatus(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None
    is_banned: bool | None = None
    ban_reason: str | None = Field(None, max_length=500)


# --- FILTERS ---
class UserFilters(BaseModel):
    # search
    email: EmailStr | None = None
    full_name: str | None = None

    # status
    role: UserRole | None = None
    is_active: bool | None = None
    is_banned: bool | None = None

    # activity dates
    last_seen_from: datetime | None = None
    last_seen_to: datetime | None = None

    last_login_from: datetime | None = None
    last_login_to: datetime | None = None

    # audit dates
    created_from: datetime | None = None
    created_to: datetime | None = None

    updated_from: datetime | None = None
    updated_to: datetime | None = None

    # pagination
    skip: int = Field(
        default=0,
        ge=0,
    )
    
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
    )

    # sorting
    sort_by: Literal['email', 'created_at', 'last_seen_at', 'last_login_at'] | None = Field(
        default=None,
        description="Field to sort by ('email', 'created_at', 'last_seen_at', 'last_login_at')"
    )
    sort_order: Literal['asc', 'desc'] = Field(
        default='asc',
        description="Sort order: 'asc' for ascending, 'desc' for descending"
    )