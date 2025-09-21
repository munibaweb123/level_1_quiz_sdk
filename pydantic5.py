#from dataclasses import dataclass
from pydantic.dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id:int
    name:str
    signup_ts:datetime

user1 = {'id': 11, 'name': 'muniba', 'signup_ts': datetime(2025, 9, 21, 11, 30, 33)}
user = User(**user1)

print(user)
