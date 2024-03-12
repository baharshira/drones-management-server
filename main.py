from bson.objectid import ObjectId
from models.drone_model import DroneCreate, Status
from models.mission_model import MissionCreate
from models.schedule_model import ScheduleCreate
from fastapi import FastAPI, HTTPException
from utils import fetch_data, create_document, perform_update, create_new_schedule, check_schedule_conflicts
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware

host_ip = os.getenv("HOST_IP", "default_ip")
port = os.getenv("PORT", "8000") 

load_dotenv()
app = FastAPI()
client = MongoClient(os.getenv("DATABASE"))
db = client.drones_management

# A middleware to allow request arrive from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Drone scheduler service is running."}


@app.get("/drones/")
def get_drones():
    return fetch_data(db.drones, {})


# Endpoint to get all drones by availability status
# I changed this endpoint to return all available drones
# I had an issue with overlapping endpoint of /drones/{status} and /drones/{id}
@app.get("/drones/status")
def get_drones_by_status():
    return fetch_data(db.drones, {"status": Status.available})


# Endpoint to get a specific drone by ID
@app.get("/drones/{id}")
async def get_drone_by_id(id):
    return fetch_data(db.drones, {"_id": ObjectId(id)})


# Endpoint to update a drone's data
# This function is a mixture of update status and update mission
# This function also includes general object update
# I changed this API to /drones/{id} and this function to be more general
# This function will now update not only the status, but other params also
@app.put("/drones/{id}")
async def update_drone(id: str, update_request: dict):
    return perform_update(db.drones, id, update_request)


# Endpoint to create a new drone
@app.post("/drones/")
async def create_drone(drone: DroneCreate):
    new_drone = await create_document(db.drones, drone)
    return {"message": "Drone inserted successfully", "drone": new_drone}


# Endpoint to get all missions
@app.get("/missions/")
def get_missions():
    return fetch_data(db.missions, {})


# Endpoint to create a new mission
@app.post("/missions/")
async def create_mission(mission: MissionCreate):
    new_mission = await create_document(db.missions, mission)
    return {"message": "Mission inserted successfully", "mission": new_mission}


# Endpoint to get all schedules
@app.get("/schedules/")
async def get_schedules():
    return fetch_data(db.schedules, {})


# Endpoint to create a new schedule
@app.post("/schedules/")
async def create_schedule(schedule: ScheduleCreate):
    return await create_new_schedule(schedule)


# Endpoint to update a schedule's status
@app.put("/schedules/{id}")
async def update_schedule_status(id: str, update_request: dict):
    return perform_update(db.schedules, id, update_request)


# Endpoint to get schedules date range
# This is how I would implement it, but there's an overlapping with get id function
@app.get("/schedules/{start_date}/{end_date}")
async def get_schedules_date_range(start_date, end_date):
    return fetch_data(db.schedules, {"start": start_date, "end": end_date})


# Endpoint to get schedules by drone
@app.get("/schedules/{drone_id}")
async def get_schedules_by_drone(drone_id):
    return fetch_data(db.schedules, {"drone": drone_id})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=host_ip, port=int(port), log_level="info")
