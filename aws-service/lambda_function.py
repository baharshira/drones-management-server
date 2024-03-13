from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.environ.get('DATABASE')
DB_NAME = 'drones_management'

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
schedules_collection = db.schedules
drones_collection = db.drones


def lambda_handler(event, context):
    current_time = datetime.utcnow()

    # Find schedules that have arrived but not yet processed
    arrived_schedules = schedules_collection.find({"start": {"$lte": current_time},
                                                   "end": {"$get": current_time},
                                                   "status": "available"})

    for schedule in arrived_schedules:
        # Update the corresponding drone status and missionId
        update_result = drones_collection.update_one(
            {"_id": schedule["drone"]},
            {
                "$set": {
                    "status": "occupied",
                    "current_mission_id": schedule["mission"]
                }
            }
        )

        # Optionally, mark the schedule as processed to avoid duplicate processing
        if update_result.modified_count > 0:
            schedules_collection.update_one(
                {"_id": schedule["_id"]},
                {"$set": {"processed": True}}
            )

    # Return a response or log output
    return {
        "statusCode": 200,
        "body": "Drone statuses updated based on schedules."
    }
