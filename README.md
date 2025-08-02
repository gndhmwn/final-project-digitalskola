wedding-invitation/
├── app/
│   ├── core/
│   │   ├── config.py
│   ├── database/
│   │   ├── db.py
│   │   ├── models.py
│   ├── routers/
│   │   ├── home.py
│   ├── services/
│   │   ├── security_service.py
│   ├── main.py
│   ├── schemas.py
├── static/
│   ├── css/
│   │   ├── style.css
│   ├── images/
│   │   ├── background.jpg
├── templates/
│   ├── index.html
│   ├── rsvp.html
│   ├── error.html
├── .env
├── requirements.txt


uvicorn app.main:app --host '0.0.0.0' --reload

http://127.0.0.1:8080/?name=John+Doe&security_code=nikah2025