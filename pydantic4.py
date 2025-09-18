# ...existing code...
from pydantic import BaseModel
from typing import List
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    createdAt: datetime
    address: Address
    tags: List[str] = []

# create a user instance
address = Address(street="123 Main St", city="Karachi", zip_code="75500")
user = User(
    id=1,
    name="Muniba",
    email="muni@gmail.com",
    is_active=True,
    createdAt=datetime.utcnow(),
    address=address,
    tags=["pydantic", "agentic-ai"]
)

# print model and serialized forms
print(user)                       # pretty model repr
print(user.model_dump())          # dict representation (Pydantic v2)
print(user.model_dump_json(indent=2))  # JSON representation
# ...existing code...