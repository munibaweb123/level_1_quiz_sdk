from datetime import datetime

from pydantic import BaseModel, PositiveInt


class User(BaseModel):
    id: int  
    name: str 
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt]  


external_data = {
    'id': 420,
    'name':'Muniba',
    'signup_ts': '2025-09-17 10:45',  
    'tastes': {
        'wine': 9,
        b'cheese': 7,  
        'cabbage': '1',  
    },
}

user = User(**external_data)  # dictionary unpacking
user1 = user

print(user.name) 
print(user1.id) 
print(user1.tastes['wine'])
#> 123
#print(user.model_dump())  
