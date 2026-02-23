# DocuForge

## Problem Statement
The process of creating dynamic, data-driven PDF reports is frequently complicated and time-consuming. Developers often face challenges when generating documents that incorporate dynamic content, such as charts or customized layouts, while managing a structured background processing pipeline.

## Proposed Solution
DocuForge provides a robust architecture to bridge the gap between rich web interfaces and high-quality PDF generation. It uses a modern front-end library to design templates and a scalable back-end to handle rendering, background processing, and delivery. It offers a complete solution where users can design their reports, trigger generation via an API, and asynchronously receive the finished documents.

## Working Architecture
The system is divided into two main components:
1. **Frontend**: A React application powered by Vite, utilizing Shadcn UI components. It offers an intuitive interface to configure report data and visualize templates.
2. **Backend**: A FastAPI-based service connected to PostgreSQL for data persistence and Redis for task queuing.
    - **PDF Generation Flow**: The backend utilizes Playwright to render the designed HTML/CSS templates in a headless browser, which subsequently prints them to PDF format.
    - **Background Tasks**: Intensive generation tasks are scheduled and processed asynchronously to maintain high API responsiveness.

## Quick Start
To run the project locally, please ensure you have Docker installed.

1. Clone the repository.
2. Navigate to the project root directory.
3. Start the services using Docker Compose:
```bash
docker-compose up --build
```
4. Access the frontend application and the backend API documentation via their respective local ports.

For more detailed setup instructions, please refer to the SETUP_GUIDE.md file.
