from pydantic import BaseModel, EmailStr

class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    idToken: str
    email: str
    refreshToken: str
    expiresIn: str
    localId: str
