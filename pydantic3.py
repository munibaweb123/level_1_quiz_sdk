# todo: create booking model
# fields: user_id:int, room_id:int, nights:int (must be >=1), rate_per_night:float

from pydantic import BaseModel, Field, field_validator

class BookingModel(BaseModel):
    user_id: int
    room_id: int
    nights: int
    rate_per_night: float = Field(..., ge=0)

    @field_validator('nights') # must include field here
    def nights_length(cls,v):
        if (v)<1:
            raise ValueError('nights must be greater than and equal to 1')
        return v
    
booking = {'user_id':11,'room_id':201,'nights':2, 'rate_per_night':2000}
booking1 = BookingModel(**booking)
print("\n===Booking Model===\n")
print(booking1)



# Nested Model
from typing import List, Optional
from pydantic import BaseModel

class Address(BaseModel):
    street:str
    city:str
    postal_code:str

class User(BaseModel):
    id:int
    name:str
    address:Address # class define above

class Comment(BaseModel):
    id:int
    content:str
    replies: Optional[List['Comment']] = None

Comment.model_rebuild() # forward referencing
address = Address(street="123 road", city="Jaipur", postal_code="10001")
user = User(id=1, name="Muni", address=address)
comment = Comment(id=1, content="First Comment", replies=[Comment(id=2, content='reply1')])
print("\n===Nested Model===\n")
print(address)
print(user)
print(comment)

# todo: create course model
# each course has modules
# each modules has lessons

class Lesson(BaseModel):
    lesson_id:int
    topic:str

class Module(BaseModel):
    module_id:int
    name:str
    lessons:List[Lesson]

class Course(BaseModel):
    course_id:int
    title:str
    modules:List[Module]

lesson = Lesson(lesson_id=12,topic="pydantic data structure")
module = Module(module_id=56, name="Agentic patterns", lessons=[lesson])
course = Course(course_id=35,title="openai agents sdk", modules=[module])
print("\n===Course Model===\n")
print(lesson)
print(module)
print(course)