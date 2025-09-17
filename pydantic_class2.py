# from pydantic import BaseModel
# from typing import List,Dict,Optional

# class Cart(BaseModel):
#     user_id: int
#     items:List[str]
#     quantities:Dict[str,int] # key and value

# class BlogPost(BaseModel):
#     title:str
#     content:str
#     image_url:Optional[str] = None

# my_cart = {'user_id':1110,'items':['muniba','farzana','fatima'], 'quantities':{'purse':6,'shoes':6}}
# my_cart1 = Cart(**my_cart)
# print(my_cart1)

# blog_post_agenticai = {'title':'openai agents sdk', 'content':'pydantic'}
# blog_post_agenticai1 = BlogPost(**blog_post_agenticai)
# print(blog_post_agenticai1)


#from dataclasses import dataclass

# @dataclass
# class Employee:
#     name:str
#     age:int
#     salary:int

# designer = {'name':'John',"age":20,'salary':'thirty thousand'}
# designer1 = Employee(**designer)
# print(designer1)


# from typing import Optional
# from pydantic import BaseModel,Field

# class Employee(BaseModel):
#     id:int
#     name:str = Field(...,min_length=3,max_length=50, description='Employee Name', examples='Muniba')
#     department:Optional[str] = 'Agentic AI'
#     salary:float = Field(...,ge=10000)

# smart_employee = {'id':'420', 'name':'Smart employee', 'salary':1000}
# employee1 = Employee(**smart_employee)
# print(employee1)

from pydantic import BaseModel, field_validator,model_validator,computed_field
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
    def total_price(self)->float:
        total_price = self.price*self.quantity
        return total_price
    
user1 = {'username':'Muniba'}
print(User(**user1))

signup_user={'password':'moni*0','confirm_password':'moni*0'}
signup_user1= SignupData(**signup_user)
print(signup_user1)

skincare_product={'price':1500,'quantity':30}
skincare_product1 = Product(**skincare_product)
print(f"total price of skin care product is: {skincare_product1.total_price}")

