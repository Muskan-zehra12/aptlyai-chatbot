# AptlyAI – AI Appointment Booking & Lead Capture Chatbot

AptlyAI is a portfolio-ready AI SaaS project built for roles involving AI APIs, chatbot development, appointment booking, CRM/lead capture, client demos, and Google Calendar style integrations.

## Features

- AI chatbot interface for appointment booking conversations
- FastAPI backend with clean REST APIs
- React frontend with professional SaaS dashboard UI
- SQLite database with users, leads, appointments, and chat messages
- Admin login and dashboard analytics
- CRM leads table
- Appointment management with confirm action
- SMTP appointment confirmation emails
- Google Calendar event creation with service account credentials
- OpenAI API-ready chatbot logic with fallback mode
- Responsive design for desktop and mobile

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite, CSS |
| Backend | Python FastAPI |
| Database | SQLite + SQLAlchemy |
| AI | OpenAI API-ready chatbot |
| Auth | JWT-ready admin login |
| Integration | Google Calendar API with service account credentials |

## Folder Structure

```text
aptlyai-chatbot/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── chatbot.py
│   ├── calendar_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── style.css
│   ├── index.html
│   └── package.json
├── screenshots/
└── docs/
```

## Run Backend

```bash
cd backend
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8001
```

Optional email confirmation setup in `backend/.env`:

```text
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=no-reply@example.com
```

When a public appointment is created, the backend saves the appointment first and then tries to send a confirmation email. If SMTP is missing or email delivery fails, the appointment still stays saved and the API returns `email_sent: false`.

Google Calendar setup in `backend/.env`:

```text
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
GOOGLE_CALENDAR_ID=primary
GOOGLE_CALENDAR_TIMEZONE=UTC
APPOINTMENT_DURATION_MINUTES=30
```

Setup steps:

1. Create or choose a Google Cloud project.
2. Enable the Google Calendar API.
3. Create a service account and download its JSON key file.
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the absolute path of that JSON file.
5. Share the target Google Calendar with the service account email, or set `GOOGLE_CALENDAR_ID` to a calendar the service account can access.
6. Restart the FastAPI backend after changing `.env`.

When a public appointment is created, the backend attempts to create a Google Calendar event and saves the returned event ID in `appointments.google_calendar_event_id`. If Calendar credentials are missing or event creation fails, the appointment still stays saved and the API returns `calendar_event_created: false` with `calendar_error`.

Open:

```text
http://127.0.0.1:8001
```

API docs:

```text
http://127.0.0.1:8001/docs
```

## Run Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Admin Login

```text
Email: admin@aptlyai.com
Password: admin123
```

Admin dashboard APIs require the token returned from `/auth/login`.

## Database

SQLite database is created automatically after backend run:

```text
backend/aptlyai.db
```

## Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Backend health check |
| POST | /auth/login | Admin login |
| POST | /chat | Chatbot reply |
| POST | /appointments | Create appointment + lead + confirmation email + Google Calendar event |
| GET | /appointments | List appointments |
| PUT | /appointments/{id}/status | Update appointment status: Pending, Confirmed, Cancelled, Rescheduled |
| GET | /leads | List CRM leads |
| GET | /dashboard/stats | Dashboard cards |

## How This Matches AI Chatbot Jobs

- Experience with AI APIs: OpenAI-ready chatbot file included
- Prompt engineering: chatbot system prompt included
- Chatbot development: full chat UI and backend route
- Appointment booking: booking form and appointment table
- Google Calendar API: service-account event creation with saved event IDs
- SMTP confirmation email: appointment request emails are sent after booking
- CRM/lead capture: lead table and admin dashboard
- Frontend knowledge: professional React SaaS interface

## Future Improvements

- Add full JWT route protection
- Add user registration
- Add Docker deployment
- Deploy frontend on Vercel and backend on Render/Railway

## CV Line

AptlyAI – AI Appointment Booking & Lead Capture Chatbot: Developed a React and FastAPI-based AI chatbot system for appointment booking, CRM lead capture, admin dashboard analytics, and Google Calendar-ready workflow integration.
