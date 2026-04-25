from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str | None
    username: str
    created_at: datetime
