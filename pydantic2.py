# pydantic example 1
# from pydantic import BaseModel
# class User(BaseModel):
#     id:int
#     name:str
#     is_active:bool

# input_data = {'id':'101','name':'muniba', 'is_active':'True'}
# user = User(**input_data)
# print(user)

# example 2

from pydantic import BaseModel
from typing import List,Dict,Optional

class Cart(BaseModel):
    user_id: int
    items:List[str]
    quantities:Dict[str,int]

class BlogPost(BaseModel):
    title:str
    content:str
    image_url:Optional[str] = None

my_cart = {'user_id':111,'items':['orange','banana','apple'],'quantities':{'pizza':2}}
cart1=Cart(**my_cart) # dictionary unpacking
print(cart1)
#print(my_cart)

#todo: create employee model
#Fields: id:int , name:str(min 3 chars)
#department: optional str(default 'General')
#salary: float (must be >= 10000)

from pydantic import BaseModel,Field

class Employee(BaseModel):
    id:int
    name:str = Field(...,min_length=3,max_length=50, description='Employee Name', examples='Muniba')
    department:Optional[str] = 'Agentic AI'
    salary:float = Field(...,ge=10000)

smart_employee = {'id':'420', 'name':'Smart Employee', 'salary':100000}
employee1 = Employee(**smart_employee)
print(employee1)

# custom validators (it runs before)
from pydantic import field_validator,model_validator,computed_field
class User(BaseModel):
    username:str

    @field_validator('username')
    def username_length(cls,v):
        if len(v)<4:
            raise ValueError('Username must be atleast 4 characters long')
        return v

class SignupData(BaseModel):
    password:str
    confirm_password:str

    @model_validator(mode='after')
    def password_match(cls,values):
        if values.password!=values.confirm_password:
            raise ValueError['Password do not match']
        return values

class Product(BaseModel):
    price:float
    quantity:int

    @computed_field
    @property
    def total_price(self)->float:
        return self.price*self.quantity
    
user1 = {'username':'moni'}
print(User(**user1))

signup_user={'password':'moni*0','confirm_password':'moni*0'}
signup_user1= SignupData(**signup_user)
print(signup_user1)

skincare_product={'price':1000,'quantity':3}
skincare_product1 = Product(**skincare_product)
print(skincare_product1)

