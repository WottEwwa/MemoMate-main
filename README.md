# 🤖MemoMate 
Your smart learning buddy on Whatsapp.
A WhatsApp chatbot that helps you learn languages with personalized flashcards – without any additional app or platform.
Simple. Personal. Always available.

Below is an abstract (high‑level overview) of your Translation Trainer system, broken into
modular components, their responsibilities, and the team‑level tasks. After that, you’ll find a
step‑by‑step workflow diagram (in ASCII/UML‑style) illustrating how messages flow through
the system.

## 🚀System Abstract

### Twilio Integration (`twilio_client.py`)

### Class: TwilioClient

#### Responsibilities:
- Connect to **Twilio Conversations** using **API Key SID & Secret**.
- Continuously poll for new messages in a shared conversation (accessible by any user).
- Dispatch incoming messages either as commands (`!START`, `!STOP`) or as answers to the Trainer logic.

## OpenAI Integration (`openai_client.py`)

### Class: OpenAIClient

#### Responsibilities:
- Generate new word lists in the user’s native language upon request.
- Produce content (e.g., text samples) for advanced levels of difficulty.
- Provide methods like `get_word_list(language, difficulty)`.

## DeepL Integration (`deepl_client.py`)

### Class: DeepLClient

#### Responsibilities:
- Translate native-language word lists into the learner’s target language.
- Handle batch or individual translations while preserving unique keys.

## Database Layer

### Files and Classes:
- `models/models.py`: Defines ORM-style classes (e.g., User, WordList, Translation) and database 
  table 
  schemas.
- `app/fast_api_client.py`: A **FastAPI** client exposing CRUD endpoints (with Swagger UI) to manage users, 
  word 
  lists, learning 
   progress, and sessions.

/for root folder .venv:
   - python3 -m venv .venv.    
   - source .venv/bin/activate.     
   - pip3 install -r requirements.txt.    
   - python3 -m pip install --upg
    
to run local server in the venv start main.py (to be in the venv is importend):

    URL: http://127.0.0.1:8000/docs

## Main Orchestrator (`main.py`)

### Class: Main

#### Responsibilities:
- Initialize all clients (**TwilioClient, OpenAIClient, DeepLClient, ServerClient**).
- Coordinate multithreading for polling messages and handling background tasks 
  (e.g., generating lists, saving to database).
- Map commands to workflows, including:
  - `!START`: Register user, fetch or generate word list, translate it, and send quiz.
  -  User answers → validate against expected translation → update progress.
  - `!STOP`: End session and summarize user progress.

## 👨‍💻Team Tasks & Workflow

### Developers:

**Lee Roy, Raffael, Patrick, Nico & Yaroslav**

<pre>
|---------------------------------------------------------------------------------------------------------|
|   Component    |  Type   | Owner     |                        Description                               |
|---------------------------------------------------------------------------------------------------------|
| Twilio Client  | Backend | Dev A     | Implement TwilioClient in twilio_client.py with polling,         |
|  Module        |         |           | command parsing, and message dispatching.                        |
|                |         |           |                                                                  |                                                                                          |
| OpenAI Client  | Backend | Dev B     | Build OpenAIClient in open_ai_client.py to request and           |
|   Module       |         |           | parse word lists from the OpenAI API.                            |
|                |         |           |                                                                  |
| DeepL Client   | Backend | Dev C     | Create DeepLClient in deepl_client.py for translating lists,     |
|   Module       |         |           | handling batch requests, and managing error retries.             |
|                |         |           |                                                                  |
| Database Models| Backend | Dev D     | Define DB schemas in database_tables.py; build FastAPI endpoints |
|   & API        |         |           | in fast_api_client.py.                                           |
|                |         |           |                                                                  |
|    Main        | Backend | Tech Lead | Wire all modules together in main.py, set up threading,          |
| Orchestration  |         |           | and map commands to workflows.                                   |
|                |         |           |                                                                  |
|   Testing      | Backend | QA/DevOps | Write unit/integration tests; configure GitHub Actions           |
| & CI Pipeline  |         |           | for linting, testing, and deployments.                           |
|---------------------------------------------------------------------------------------------------------|
</pre>



## 🔁Step-by-Step Workflow Diagram

<pre>

+-----------------+           +---------------+            +---------------+
|                 |  poll     |               | generate   |               |
|  TwilioClient   |<=========>|  Main         |<==========>| OpenAIClient  |
| (poll messages) |           | Orchestrator  |            |  (new lists)  |
+-----------------+           +---------------+            +---------------+
        |                             |                         |
        |                             |                         |
        |  send                       |  get word               | translate
        |  quiz                       |   lists                 |
        |                             |                         |
        |                             |                         v
        |                             |                     +---------------+                        
        v                             v                     |               |
+----------------+   get()     +----------------+           |  DeepLClient  |
|                |   save      |                |           |  (translate)  |
| ServerClient   |<===========>|    Database    |           +---------------+
| (FastAPI + DB) |   results   |  Tables/Models |<==========| save translation vie serverclient            
+----------------+             +----------------+              

</pre>

### 1️⃣ Polling Loop
 - **TwilioClient** continuously fetches new messages.
 - If message is **!START**, it’s forwarded to Main.
### 2️⃣ Word List Generation
 - Main invokes **OpenAIClient**.get_word_list(...).
### 3️⃣ Translation
 - Main calls **DeepLClient**.translate_dict(...).
### 4️⃣ Persistence
 - The translated list is stored via **ServerClient** into the database.
### 5️⃣ Quiz Delivery
 - Main uses **TwilioClient** to send quiz questions back to the user.
### 6️⃣ Answer Handling
 - Incoming answers are validated by **Main** against DB entries, progress updated.

 This high‑level design keeps each concern in its own module, enables parallel processing via
 threading, and provides a clear roadmap for the team.
/for add .venv in app folder:
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    python3 -m pip install --upg
    
to run the server in the venv (to be in the venv is importend):
    uvicorn fast_api_client:app --reload

    URL: http://127.0.0.1:8000/docs

to start the fast_api_client server in the venv (to be in the venv is importend):
    uvicorn fast_api_client:app --reload