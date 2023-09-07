from pydantic import BaseModel, EmailStr


class UserSingUp(BaseModel):
    login: str
    password: str
    email: EmailStr
    first_name: str = ""
    last_name: str = ""

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


