from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://sarthakgupta150603:Sarthak_Library@cluster0.6kmk3bj.mongodb.net/")


db = client["library"]
collection = db["students"]

app = FastAPI()

# Models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

# API Endpoints
@app.post("/students", status_code=201)
async def create_student(student: Student):
    result = collection.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@app.get("/students", response_model=list[Student])
async def list_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}

    students = collection.find(query, {"_id": 0})
    return list(students)

@app.get("/students/{id}", response_model=Student)
async def get_student(id: str):
    student = collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}")
async def update_student(id: str, student: Student):
    updated_student = student.dict(exclude_unset=True)
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": updated_student})
    if result.modified_count == 1:
        return {"message": "Student updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{id}")
async def delete_student(id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")