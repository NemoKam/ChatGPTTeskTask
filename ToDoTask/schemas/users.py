from datetime import datetime

from schemas.base import BaseSchema 


# Блок для схем аутентификации и регистрации пользователей

class LoginUserRequestSchema(BaseSchema):
    email: str
    password: str

    class ConfigDict:
        from_attributes = True


class RegisterUserRequestSchema(LoginUserRequestSchema):
    pass    


class RegisterUserResponseSchema(BaseSchema):    
    id: int
    email: str


# Блок для схем JWT

class TokenSchema(BaseSchema):
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    token_type: str
