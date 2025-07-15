from pydantic import BaseModel
from sqlalchemy import DateTime


class User_Create(BaseModel):
    username: str
    password: str
    role: str

class User_Login(BaseModel):
    username: str
    password: str

class User_Out(BaseModel):
    id: int
    username: str
    password: str
    role: str

# class Reports_Filter(BaseModel):
#     from_date: DateTime
#     to_date: DateTime
#     time_range: DateTime
#     location_filter: str
#     bin_type_filter: str
