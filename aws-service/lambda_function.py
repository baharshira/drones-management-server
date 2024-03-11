import os
import json
from datetime import datetime, timezone
from pymongo import MongoClient

client = MongoClient(os.environ["DATABASE"])
db = client.drones_management


def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    updated_drones = []

    # Find schedules that are currently active
    current_schedules = db.schedules.find({
        "start": {"$lte": now},
        "end": {"$gte": now}
    })

    for schedule in current_schedules:
        # Update the corresponding drone's status to "occupied"
        result = db.drones.update_one(
            {"_id": schedule['drone']},
            {"$set": {"status": "occupied", "currentMission": schedule['mission']}}
        )

        if result.modified_count > 0:
            updated_drones.append(str(schedule['drone']))

    return {
        'statusCode': 200,
        'body': json.dumps(f'Updated drones: {updated_drones}')
    }
