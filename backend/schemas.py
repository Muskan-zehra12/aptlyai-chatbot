from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

AppointmentStatus = Literal["Pending", "Confirmed", "Cancelled", "Rescheduled"]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: Optional[str] = ""
    status: Optional[str] = "New"

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None

class AppointmentCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    service: str
    appointment_date: str
    appointment_time: str
    message: Optional[str] = ""

class AppointmentUpdate(BaseModel):
    service: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class StatusUpdate(BaseModel):
    status: AppointmentStatus

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "guest"
