# MealMind – AI Dietplan Assistant

MealMind is an AI-powered diet planning and meal analysis application designed to help users understand their nutritional intake, maintain health profiles, and follow personalized dietary recommendations.

The application combines artificial intelligence, meal image analysis, nutritional estimation, and health information to provide practical dietary guidance. Users can upload meal photographs, review estimated nutritional values, maintain their meal history, and generate weekly diet plans based on their health profiles and fitness goals.

MealMind is developed as a full-stack web application with a React frontend, a FastAPI backend, and a PostgreSQL database. The system follows a modular architecture to support future development, external application integration, and cloud deployment.

## 1. Project Overview

Maintaining a balanced diet requires understanding daily food consumption, nutritional requirements, and individual health conditions. Manually tracking meals and preparing personalized diet plans can be time-consuming.

MealMind addresses these challenges by providing a centralized platform for meal analysis and diet management.

The application allows users to:

- Create and manage personal accounts.
- Maintain health profiles and dietary goals.
- Upload health reports for AI-assisted information extraction.
- Analyze food photographs using AI.
- Review estimated calories and macronutrients.
- Save analyzed meals to their personal history.
- Generate personalized weekly diet plans.
- Track planned and consumed meals through calendar views.
- Monitor dietary information through an interactive dashboard.

The primary objective is to make nutritional tracking and diet planning more accessible through an integrated AI-assisted workflow.

## 2. Key Features

### User Authentication and Account Management

MealMind provides account registration and login functionality to maintain individual user profiles.

Authentication is handled through the backend, with password hashing and token-based session management.

The application also includes password recovery functionality using email-based verification.

### Health Profile Management

Users can maintain health-related information required for personalized diet planning.

The health profile supports information such as:

- Age and gender
- Height and weight
- Fitness or dietary goals
- Activity level
- Relevant health conditions
- Dietary preferences and restrictions

The stored profile provides context for calculating nutritional requirements and generating personalized recommendations.

### Health Report Analysis

The application supports uploading health reports for AI-assisted extraction of relevant medical information.

The extracted information is presented for user review before being confirmed and stored in the health profile.

This approach helps reduce manual data entry while allowing users to verify the extracted information.

### AI-Powered Meal Analysis

Users can upload a photograph of their meal for AI-based food identification and nutritional estimation.

The meal analysis workflow includes:

1. Uploading a meal photograph.
2. Sending the image to the backend for processing.
3. Using the configured AI service to identify visible food items.
4. Estimating nutritional information for the identified foods.
5. Returning the analysis to the frontend.
6. Displaying the estimated nutritional values and dietary feedback.

The analysis provides estimated information such as calories, carbohydrates, protein, and fats.

Nutritional values are approximate and may vary depending on ingredients, preparation methods, and portion sizes.

### Meal Review and History

MealMind separates meal analysis from permanent meal storage.

Users can review the AI-generated analysis before deciding whether to save the meal.

Once saved, the meal becomes part of the user's dietary history.

The history module supports reviewing previously recorded meals and managing stored meal records.

### Personalized Weekly Diet Planning

The application generates weekly dietary recommendations based on the user's health profile, nutritional requirements, and selected goals.

The planning process considers relevant profile information and uses AI to prepare meal recommendations for the week.

Generated plans can be retrieved and displayed through the frontend for convenient reference.

### Diet and Meal Calendar

MealMind includes calendar-based views for organizing dietary information.

The calendar components help users review scheduled meals, access daily diet recommendations, and navigate meal records by date.

### Dashboard and Nutritional Tracking

The dashboard provides a consolidated view of dietary information.

It brings together meal records, nutritional estimates, and diet-related information to help users monitor their progress.

## 3. Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| React.js | Building the user interface |
| JavaScript | Frontend application logic |
| Vite | Development server and production build tooling |
| CSS | Application styling and responsive layouts |
| Axios | Communication with backend APIs |
| React Router | Client-side navigation |
| Recharts | Data visualization |
| Lucide React | Interface icons |

### Backend

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API development |
| Uvicorn | ASGI application server |
| Pydantic | Request and response validation |
| SQLAlchemy | Database operations and ORM |
| PostgreSQL | Relational database |
| JWT | Token-based authentication |
| ReportLab | PDF document generation |

### AI Services

| Service | Purpose |
|---|---|
| DeepSeek API | AI-assisted meal analysis, nutritional feedback, and diet planning |
| Gemini API | AI-assisted health report processing |

AI services are accessed through the backend to keep API credentials separate from the frontend application.

## 4. System Architecture

MealMind follows a frontend-backend architecture with separate layers for application logic, AI services, and data persistence.

```text
                    USER
                     |
                     v
              REACT FRONTEND
                     |
                     | HTTP / REST APIs
                     v
               FASTAPI BACKEND
                     |
          +----------+----------+
          |                     |
          v                     v
   APPLICATION SERVICES    DATABASE LAYER
          |                     |
    +-----+------+              v
    |            |         POSTGRESQL
    v            v
 DEEPSEEK      GEMINI
   API           API
```

### Frontend Layer

The React application handles user interactions, page navigation, forms, image uploads, and presentation of results.

### Backend Layer

The FastAPI backend manages authentication, request validation, user information, meal processing, diet planning, and database operations.

### AI Service Layer

The AI service modules communicate with external model APIs to process meal images, generate dietary recommendations, and extract relevant information from health reports.

### Database Layer

PostgreSQL stores structured application information, including user accounts, health profiles, meal records, diet plans, and calendar-related data.

## 5. Project Structure

The repository is organized into separate frontend and backend directories.

```text
AI-Dietplan-Assistant/
|
|-- backend/
|   |-- main.py
|   |-- database.py
|   |-- requirements.txt
|   |
|   |-- db_models/
|   |   |-- user.py
|   |   |-- health_profile.py
|   |   |-- health_report.py
|   |   |-- meal.py
|   |   |-- meal_food.py
|   |   |-- diet_plan.py
|   |   |-- calendar_event.py
|   |   |-- password_reset_otp.py
|   |
|   |-- models/
|   |   |-- user.py
|   |   |-- health_profile.py
|   |   |-- health_report.py
|   |   |-- meal.py
|   |   |-- diet_plan.py
|   |   |-- calendar_event.py
|   |
|   |-- services/
|       |-- auth_service.py
|       |-- calorie_service.py
|       |-- deepseek_service.py
|       |-- diet_plan_service.py
|       |-- email_service.py
|       |-- gemini_service.py
|       |-- health_report_service.py
|       |-- password_reset_service.py
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- components/
|   |   |-- context/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- App.jsx
|   |   |-- App.css
|   |   |-- main.jsx
|   |
|   |-- package.json
|   |-- package-lock.json
|   |-- vite.config.js
|
|-- README.md
```

The backend separates database entities, validation models, and business logic into dedicated modules. The frontend uses reusable components and page-level modules to organize application functionality.

## 6. Local Installation and Setup

### Prerequisites

Ensure the following are installed before running the application:

- Python 3.10 or later
- Node.js and npm
- PostgreSQL
- Git
- A code editor such as Visual Studio Code

Valid API credentials are also required for the configured AI services.

### Clone the Repository

```bash
git clone https://github.com/macsoftechnologies/MealMind.git
cd MealMind
```

### Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Configure the backend environment variables for the database connection, authentication, email service, and AI providers.

The exact variable names must match those used in the backend configuration.

A local environment file may include settings for:

```text
DATABASE_URL
SECRET_KEY
DEEPSEEK_API_KEY
GEMINI_API_KEY
```

Additional email and authentication settings may be required depending on the enabled features.

Environment files containing credentials must not be committed to the repository.

### Database Configuration

Create a PostgreSQL database and configure the backend connection string.

Example format:

```text
postgresql://username:password@localhost:5432/database_name
```

The backend uses SQLAlchemy to communicate with PostgreSQL.

Ensure the database is accessible and the required schema is initialized before using the application.

### Start the Backend

From the backend directory, run:

```bash
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI automatically generates interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI specification is available at:

```text
http://127.0.0.1:8000/openapi.json
```

### Frontend Setup

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Configure the frontend API base URL according to the application configuration.

For local development, the frontend should communicate with the FastAPI server running on port 8000.

Start the development server:

```bash
npm run dev
```

The frontend is typically available at:

```text
http://localhost:5173
```

Open this address in a browser to access the application.

## 7. Application Workflow

The main application workflow consists of the following stages.

### Stage 1: User Authentication

The user creates an account or signs in to access the application.

### Stage 2: Health Profile Setup

The user enters health information and dietary preferences. Available health reports can also be processed to assist with profile completion.

### Stage 3: Nutritional Requirement Calculation

The backend uses the stored profile information to calculate estimated nutritional requirements.

### Stage 4: Diet Plan Generation

The application generates a weekly diet plan using the user's health information, nutritional targets, and configured AI service.

### Stage 5: Meal Analysis

The user uploads a meal image. The backend processes the image through the AI analysis service and returns estimated food and nutritional information.

### Stage 6: Meal Confirmation

The user reviews the analysis and chooses whether to save it to the database.

### Stage 7: Progress Review

Saved meals, dietary information, and generated plans are accessible through the dashboard, history, and calendar interfaces.

## 8. API Overview

The backend exposes REST APIs for communication between the frontend and application services.

The major API groups include:

| API Group | Functionality |
|---|---|
| Authentication | Registration, login, account information, and password recovery |
| User Profile | Create, retrieve, and update health information |
| Health Reports | Analyze uploaded reports and confirm extracted information |
| Meal Analysis | Analyze uploaded meal images |
| Meal Management | Save, retrieve, and delete meal records |
| Diet Planning | Generate and retrieve weekly diet plans |
| Calendar | Retrieve date-based dietary information |

### API Documentation

FastAPI provides Swagger UI for exploring available endpoints and testing requests.

Local documentation:

```text
http://127.0.0.1:8000/docs
```

The documentation includes endpoint definitions, supported HTTP methods, request parameters, and response schemas.

Refer to the generated OpenAPI documentation for the current API contract.

## 9. Database Design

MealMind uses a relational database to organize user information and dietary records.

The primary database entities include:

| Entity | Description |
|---|---|
| User | Account and authentication information |
| HealthProfile | Personal health information and dietary preferences |
| HealthReport | Uploaded report information and extracted health data |
| Meal | Saved meal records |
| MealFood | Individual food items associated with meals |
| DietPlan | Generated dietary plans |
| CalendarEvent | Date-based diet and meal information |
| PasswordResetOTP | Verification data used for password recovery |

SQLAlchemy models define the database entities and their relationships.

The database structure supports storing user-specific information and retrieving it across the application's modules.

## 10. AI Integration

### DeepSeek Integration

DeepSeek is used for AI-assisted meal understanding and dietary recommendations.

The backend prepares the required input, communicates with the configured model API, processes the generated response, and returns structured information to the application.

The AI workflow supports food identification, nutritional estimation, and personalized dietary feedback.

### Gemini Integration

Gemini is used for processing health report information.

The service assists with extracting relevant information from uploaded reports so that it can be reviewed and incorporated into the user's health profile.

### Limitations of AI-Generated Results

AI-generated nutritional estimates and dietary recommendations are not guaranteed to be medically accurate.

Meal analysis accuracy can be affected by image quality, portion size, hidden ingredients, and preparation methods.

Health report extraction may also require correction or confirmation.

MealMind is intended to assist dietary awareness and planning. It is not a replacement for professional medical diagnosis or treatment.

## 11. Security Considerations

The application handles account information and potentially sensitive health-related data.

The following practices are important for secure operation:

- Store passwords using appropriate password hashing.
- Keep API keys and database credentials in environment variables.
- Protect authenticated endpoints using access-token validation.
- Validate user ownership before returning or modifying stored records.
- Use HTTPS for publicly accessible deployments.
- Restrict cross-origin access to trusted frontend origins.
- Validate uploaded files and enforce appropriate upload limits.
- Avoid exposing sensitive information through application logs.
- Apply access controls and database backup procedures in production.

Public deployment should include verification of authentication, authorization, and user data isolation across all relevant endpoints.

## 12. Deployment

MealMind is structured to support separate deployment of the frontend, backend, and database.

The intended cloud architecture is:

| Component | Hosting Platform |
|---|---|
| React Frontend | Render Static Site |
| FastAPI Backend | Render Web Service |
| PostgreSQL Database | Neon PostgreSQL |

The frontend communicates with the deployed FastAPI backend through HTTPS.

The backend connects to the PostgreSQL database and external AI providers using securely configured environment variables.

Deployment requires configuring the production API URL, database connection, CORS settings, authentication secrets, and AI service credentials.

Production resource limits, service availability, database backups, and AI API usage costs should be reviewed before making the application available to external users.

## 13. External Application Integration

MealMind is designed with a REST API backend, allowing its functionality to be integrated into other applications.

The frontend and backend can be deployed independently, enabling external systems to consume the available APIs.

Integration requirements include:

- A publicly accessible backend API.
- Documented request and response structures.
- Secure authentication and authorization.
- Appropriate user identification and data isolation.
- Configuration of permitted frontend origins.
- Error handling and API response validation.

External applications are responsible for implementing their own integration workflows and any additional access or subscription requirements.

## 14. Future Enhancements

Potential areas for further development include:

- Improved food identification and portion estimation.
- More accurate nutritional analysis using structured food databases.
- Advanced dietary progress tracking.
- Additional personalization of weekly diet plans.
- Expanded support for dietary preferences and restrictions.
- Improved AI response validation and evaluation.
- Integration with external health and fitness applications.
- Enhanced monitoring and scalability for production deployment.

## 15. Project Status

MealMind includes the core functionality for user authentication, health profile management, AI-assisted meal analysis, meal history, personalized diet planning, and calendar-based dietary tracking.

The application is being prepared for cloud deployment and integration with external platforms.

Further testing, security validation, and production configuration are required before wider deployment.

## 16. Development and Maintenance

**Organization:** Macsof Technologies

**Project:** MealMind – AI Dietplan Assistant

**Application Type:** Full-stack AI-powered web application

**Repository:** https://github.com/macsoftechnologies/MealMind

The project is maintained as part of ongoing application development and integration activities.

---

**Note:** This repository contains the application source code. Environment-specific credentials, database passwords, and external API keys are not included and must be configured separately.
