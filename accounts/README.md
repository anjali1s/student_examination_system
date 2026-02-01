# Online Examination System

## Description
A Django-based web application for managing online exams, including teacher and student interfaces. Teachers can create exams, and students can take them securely.

## Features
- Teacher dashboard to create and manage exams
- Student dashboard to view and take exams
- Role-based authentication (Teacher / Student)
- Results tracking and reports
- Secure login system

## Tech Stack
- Python 3.14
- Django 6.0
- HTML / CSS / Bootstrap
- SQLite (development)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/online-exam-system.git

2. Create a virtual environment:
python -m venv venv

3. Activate the environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

4. Install dependencies:
pip install -r requirements.txt

5. Run migrations:
python manage.py migrate
Start the server:
python manage.py runserver