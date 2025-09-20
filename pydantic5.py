from datetime import datetime
from typing import Optional
from pydantic.dataclasses import dataclass

@dataclass
class User:
    id:int
    name:str = 'John Doe'
    signup_ts: Optional[datetime] = None

user = User(id='23',signup_ts='2025-09-20 03:45',name='Muniba')
print(user)