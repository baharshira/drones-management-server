from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from pymongo.collection import Collection
from pymongo.results import UpdateResult
from bson import ObjectId
from pymongo import MongoClient
from models.schedule_model import ScheduleCreate
import os

load_dotenv()
client = MongoClient(os.getenv("DATABASE"))
db = client.drones_management


# Perform an update operation on a given collection using the provided ID and update data.
def perform_update(collection: Collection, document_id: str, update_data: dict) -> dict:
    try:
        oid = ObjectId(document_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId format: {e}")

    # Sanitize the update_data to remove fields that should not be updated
    update_data.pop("_id", None)

    update_result: UpdateResult = collection.update_one({"_id": oid}, {"$set": update_data})

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    if update_result.modified_count == 0:
        return {"message": "No changes made to the document", "id": document_id}

    return {"message": "Document updated successfully", "id": document_id, "new data": update_data}


def convert_object_id_to_str(item):
    if isinstance(item, list):
        return [convert_object_id_to_str(subitem) for subitem in item]
    elif isinstance(item, dict):
        return {key: convert_object_id_to_str(value) for key, value in item.items()}
    elif isinstance(item, ObjectId):
        return str(item)
    return item


def fetch_data(collection, query):
    try:
        drones_cursor = collection.find(query)
        drones = [convert_object_id_to_str(drone) for drone in drones_cursor]
        return drones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch drones: {e}")


# Generic function to create a document in the database
async def create_document(collection, document_data):
    document_dict = document_data.dict(by_alias=True)
    result = collection.insert_one(document_dict)

    if not result.acknowledged:
        raise HTTPException(status_code=500, detail=f"Failed to create document in {collection.name} collection")

    new_document = collection.find_one({"_id": result.inserted_id})
    if new_document is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve the newly created document from database")

    # Convert the ObjectId to a string for JSON
    new_document["_id"] = str(new_document["_id"])
    return new_document


# Checks for any scheduling conflicts for the given drone within the specified time range.
# Returns True if a conflict is found, otherwise False.
def check_schedule_conflicts(drone_id: str, start_time: datetime, end_time: datetime) -> bool:
    conflict_query = {
        "drone": drone_id,
        "$or": [
            {"start": {"$lte": end_time}, "end": {"$gte": start_time}},
        ]
    }
    count = db.schedules.count_documents(conflict_query)
    return count > 0


async def create_new_schedule(schedule: ScheduleCreate = Body(...)):
    # Check for scheduling conflicts before creating a new schedule
    if check_schedule_conflicts(schedule.drone, schedule.start, schedule.end):
        raise HTTPException(status_code=400, detail="Scheduling conflict detected for the given drone and time range.")

    # Proceed with schedule creation if no conflicts are found
    schedule_dict = schedule.dict(by_alias=True)
    result = db.schedules.insert_one(schedule_dict)
    if result.acknowledged:
        return {"message": "Schedule created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create schedule")