# Project Explanation

AptlyAI is a full-stack AI chatbot system. The user can chat with the bot or manually book an appointment. The backend saves the user details as a lead and creates an appointment record. The admin can log in and view dashboard statistics, leads, and appointment records.

## Main Flow

1. User opens frontend.
2. User chats with AI chatbot or fills appointment form.
3. React frontend sends request to FastAPI backend.
4. Backend saves details in SQLite database.
5. Admin logs in and views leads and appointments.
6. Appointment status can be confirmed from the dashboard.

## Important Files

- `backend/main.py`: API routes
- `backend/models.py`: Database tables
- `backend/chatbot.py`: AI chatbot logic and prompt
- `backend/calendar_service.py`: Google Calendar placeholder
- `frontend/src/main.jsx`: React pages and UI logic
- `frontend/src/style.css`: Professional UI styling
