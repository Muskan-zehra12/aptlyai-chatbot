from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Lead, Appointment, ChatMessage
from schemas import LoginRequest, LeadCreate, LeadUpdate, AppointmentCreate, AppointmentUpdate, StatusUpdate, ChatRequest
from auth import hash_password, verify_password, create_token, require_admin
from chatbot import get_ai_reply
from calendar_service import create_calendar_event
from email_service import send_appointment_confirmation

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AptlyAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_admin(db: Session):
    admin = db.query(User).filter(User.email == "admin@aptlyai.com").first()
    if not admin:
        db.add(User(name="Admin", email="admin@aptlyai.com", password_hash=hash_password("admin123"), role="admin"))
        db.commit()

@app.get("/")
def root(db: Session = Depends(get_db)):
    seed_admin(db)
    return {"message": "AptlyAI backend is running", "admin": "admin@aptlyai.com / admin123"}

@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    seed_admin(db)
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_token({"sub": user.email, "role": user.role}), "user": {"name": user.name, "email": user.email, "role": user.role}}

@app.post("/chat")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    user_msg = ChatMessage(sender="user", message=payload.message)
    db.add(user_msg)
    reply = await get_ai_reply(payload.message)
    bot_msg = ChatMessage(sender="bot", message=reply)
    db.add(bot_msg)
    db.commit()
    return {"reply": reply}

@app.post("/leads")
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@app.get("/leads")
def list_leads(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@app.put("/leads/{lead_id}")
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for appointment in db.query(Appointment).filter(Appointment.lead_id == lead_id).all():
        appointment.lead_id = None
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted"}

@app.post("/appointments")
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    lead = Lead(name=payload.name, email=payload.email, phone=payload.phone, message=payload.message, status="New")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    event_id, calendar_error = create_calendar_event(
        payload.name,
        payload.email,
        payload.service,
        payload.appointment_date,
        payload.appointment_time,
    )
    appointment = Appointment(
        lead_id=lead.id,
        service=payload.service,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        status="Pending",
        google_calendar_event_id=event_id,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    email_sent, email_error = send_appointment_confirmation(
        to_email=payload.email,
        name=payload.name,
        service=payload.service,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
    )
    response = {
        "message": "Appointment request saved",
        "appointment": appointment,
        "lead": lead,
        "email_sent": email_sent,
        "calendar_event_created": bool(event_id),
    }
    if email_error:
        response["email_error"] = email_error
    if calendar_error:
        response["calendar_error"] = calendar_error
    return response

@app.get("/appointments")
def list_appointments(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    return db.query(Appointment).order_by(Appointment.created_at.desc()).all()

@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)
    db.commit()
    db.refresh(appointment)
    return appointment

@app.put("/appointments/{appointment_id}/status")
def update_status(appointment_id: int, payload: StatusUpdate, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted"}

@app.get("/dashboard/stats")
def stats(db: Session = Depends(get_db), admin: dict = Depends(require_admin)):
    total_leads = db.query(Lead).count()
    confirmed = db.query(Appointment).filter(Appointment.status == "Confirmed").count()
    appointments = db.query(Appointment).count()
    return {
        "leads": total_leads,
        "appointments": appointments,
        "pending": db.query(Appointment).filter(Appointment.status == "Pending").count(),
        "confirmed": confirmed,
        "cancelled": db.query(Appointment).filter(Appointment.status == "Cancelled").count(),
        "rescheduled": db.query(Appointment).filter(Appointment.status == "Rescheduled").count(),
        "new_leads": db.query(Lead).filter(Lead.status == "New").count(),
        "conversion_rate": round((confirmed / total_leads) * 100, 1) if total_leads else 0,
    }
