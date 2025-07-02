# JCR FastAPI Project

## Features

- **/save**: Save user data (id, name, skill, resume, certificates) to MySQL.
- **/parsing**: Upload and parse a resume PDF, saving extracted text to the database.
- **/jobsuggestion/{user_id}**: Suggest a job title for a user using Gemini API (integration placeholder).

## Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
2. **MySQL Setup:**

   - Create a database named `jcr_db`.
   - Create a table:
     ```sql
     CREATE TABLE users (
       id INT PRIMARY KEY,
       name VARCHAR(255),
       skill VARCHAR(255),
       resume TEXT,
       certificates TEXT
     );
     ```
   - Update DB credentials in `main.py` if needed.

3. **Run the server:**
   ```
   uvicorn main:app --reload
   ```

## Endpoints

- **POST /save**: Form data (id, name, skill, resume, certificates)
- **POST /parsing**: Form data (id), file upload (PDF)
- **GET /jobsuggestion/{user_id}**: Returns suggested job title (dummy response until Gemini API is added)

## Notes

- Ensure MySQL server is running.
- For Gemini API, update the placeholder in `main.py` when you have the API details.
