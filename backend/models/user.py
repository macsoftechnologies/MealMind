from pydantic import BaseModel, EmailStr, Field


# ============================================================
# USER CREATE
# ============================================================

class UserCreate(BaseModel):
    email: EmailStr | None
    password: str
    name: str

    age: int = Field(
        gt=0,
        lt=120
    )

    gender: str

    height_cm: float = Field(
        gt=0
    )

    weight_kg: float = Field(
        gt=0
    )


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    id: int
    email: EmailStr | None
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float

    model_config = {
        "from_attributes": True
    }


# ============================================================
# USER REGISTER
# ============================================================

class UserRegister(BaseModel):
    name: str
    email: EmailStr

    password: str = Field(
        min_length=8
    )

    age: int = Field(
        gt=0,
        lt=120
    )

    gender: str

    height_cm: float = Field(
        gt=0
    )

    weight_kg: float = Field(
        gt=0
    )


# ============================================================
# USER LOGIN
# ============================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# FORGOT PASSWORD
# ============================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# ============================================================
# VERIFY RESET OTP
# ============================================================

class VerifyResetOTPRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6
    )


# ============================================================
# RESET PASSWORD
# ============================================================

class ResetPasswordRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6
    )

    new_password: str = Field(
        min_length=8
    )


# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=8
    )