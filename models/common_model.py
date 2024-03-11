from bson import ObjectId
from pydantic import BaseModel


class PyObjectId(str):
    # Custom type to represent MongoDB ObjectIds in Pydantic models
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values, **kwargs):
        # Validates and converts input to a MongoDB ObjectId string representation
        try:
            oid = ObjectId(v) # Attempts to create ObjectId, ensuring `v` is a valid ObjectId format
            return str(oid) # Returns the string representation of the ObjectId
        except Exception:
            # If conversion to ObjectId fails, raise a ValueError
            raise ValueError(f"Not a valid ObjectId: {v}")


class CommonModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True # Allows for arbitrary types, such as ObjectId from MongoDB
        json_encoders = {
            ObjectId: lambda oid: str(oid), # Converts ObjectId types to their string representation for JSON serialization
        }

