from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Базовая схема для всех схем приложения.
    """
    model_config = ConfigDict(from_attributes=True)
