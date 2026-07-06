from pydantic import BaseModel


class PasswordConfirm(BaseModel):
    password: str
