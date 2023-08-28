from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    token: str

class Login(BaseModel):
    email: EmailStr
    password: str


class Register(Login):
    name: str

class Venue(BaseModel):
    name: str
    description: str
    image: str
    city: str
    address: str

class VenueWithId(Venue):
    id: int


class Show(BaseModel):
    name: str
    description: str
    image: str
    tags: str


class ShowWithId(Show):
    id: int


class Allocation(BaseModel):
    venue_id: int
    show_id: int
    time: datetime
    capacity: int
    base_price: float
    max_multiplier: float

    @validator("time")
    def is_later(cls, val: datetime):
        if val <= datetime.utcnow():
            raise ValueError("Shows cannot be scheduled in the past.")
        print(val.isoformat())
        return val


class AllocationWithId(Allocation):
    id: int


class Booking(BaseModel):
    allocation_id: int
    quantity: int
    gross_price: float


class Review(BaseModel):
    booking_id: int
    review: str
    rating: int

    @validator("rating")
    def clamp(cls, val: int):
        return max(0, min(5, val))
    
class DeleteReview(BaseModel):
    id: int

class Promise(BaseModel):
    promise_id: str

class ExportVenue(BaseModel):
    id: int

class GetVenues(BaseModel):
    id: Optional[int] = None

class GetShows(BaseModel):
    id: Optional[int] = None

class GetAllocations(BaseModel):
    id: Optional[int] = None
    venue_id: Optional[int] = None
    show_id: Optional[int] = None

class MyBookings(BaseModel):
    id: Optional[int] = None

class GetReviews(BaseModel):
    id: Optional[int] = None
    venue_id: Optional[int] = None
    show_id: Optional[int] = None
    allocation_id: Optional[int] = None

class DeleteVenue(BaseModel):
    id: int

class DeleteShow(BaseModel):
    id: int

class DeleteAllocation(BaseModel):
    id: int

class GetFilledStatus(BaseModel):
    id: int

class GetPrice(BaseModel):
    id: int