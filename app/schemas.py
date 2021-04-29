from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "satoshin@gmx.com",
                "password": "cd5b1e4947e304476c788cd474fb579a",
            }
        }


class Message(BaseModel):
    content: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "content": "hodl",
            }
        }