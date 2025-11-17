# Automatic Number Plate Recognition (ANPR) Check-In System

## Introduction
The **Automatic Number Plate Recognition (ANPR) Check-In System** is a computer vision–powered solution designed for **valet and parking services** to automate vehicle identification and fast track the checki-in process

By using cameras and machine learning–based OCR (Optical Character Recognition), the system can automatically detect, read, and log vehicle license plates upon entry or exit. This replaces manual ticketing and data entry, reducing errors, improving speed, and enabling a more contactless experience for customers.

The project aims to create a scalable and modular platform that can be deployed across different environments.

### Design Problem

My Name is Trystan, I am currently studying to become a software engineer. During my studies I work part time at a very busy valet. From my perspective as an emploee, the Valet's current check-in system is old and obsolete, as an engineer I decided to create a functional program that could be implemented seamlessly and provide a more efficient checkin system for both Customer & Employee.

---

## Minimum Viable Product (MVP)
The MVP focuses on delivering the **core functionality** required to demonstrate and validate the system’s concept in a real-world setting.

### MVP Objectives
- **Automatic Plate Detection** – Capture and detect vehicle license plates from a camera feed or uploaded image.
- **OCR Extraction** – Accurately read plate numbers using a pre-trained model (EasyOCR).
- **Check-In Logging** – Store plate number, timestamp, and captured image in a database.
- **Dashboard Display** – Show currently checked-in vehicles with search and filtering options.
- **Simple Check-Out** – Allow attendants to mark vehicles as checked out.

### MVP Deliverables
- Working prototype that identifies license plates from camera input.
- Local database storing check-in and check-out records.
- Basic web interface (Flask/React) for attendants to view and manage records.
- Configuration for running locally or in a Docker container.

---

## Phases for Development

### **Phase 1: Core Functionality (MVP Build) -> COMPLETED**
**Goal:** Deliver a working end-to-end prototype.
- Integrate OpenCV and EasyOCR for Optical Character Recognition (OCR).
- Build REST API to handle plate recognition and logging.
- Create a local SQLite database for vehicle entries and bookings.
- Develop a basic web dashboard to view live entries and bookings.
- Add error handling and basic logging.

**Outcome:** Functional ANPR check-in system running locally.

---

### **Phase 2: Usability & Interface Improvements**
**Goal:** Enhance user experience and operational efficiency.
- Redesign dashboard with search, filters, and image previews.
- Add manual entry fallback for unreadable plates.
- Implement check-out workflow.
- Include time tracking (duration parked).
- Deploy prototype on a local server or Raspberry Pi setup.

**Outcome:** A Basic user-friendly system ready for small-scale real-world implementation.

---

### **Phase 3: Integration & Automation**
**Goal:** Connect system with external services and improve automation.
- Integrate ticket printing or digital ticket issuance.
- Connect to SMS/email APIs for automated notifications.
- Add role-based authentication for attendants and admins.
- Introduce cloud database and remote access to dashboard.

**Outcome:** Semi-automated, connected system with remote monitoring capabilities.

---

### **Phase 4: Advanced Features & Scalability**
**Goal:** Extend functionality using machine learning and advanced analytics.
- Implement vehicle make/model recognition.
- Introduce confidence scoring and adaptive OCR tuning.
- Add multi-camera and multi-location support.
- Deploy system using Docker or Kubernetes for scalability.
- Add analytics dashboard (e.g. peak times).

**Outcome:** Fully scalable and production-ready ANPR solution for valet and parking services.

---

### **Phase 5: Commercial Deployment & Maintenance**
**Goal:** Prepare for production environments.
- Optimize for cloud deployment (AWS or Azure).
- Add continuous monitoring and alerting.
- Conduct field testing and accuracy benchmarking.
- Finalize documentation and maintenance procedures.

**Outcome:** Stable, maintainable, and commercially deployable ANPR platform.

---

## Tech Stack (Proposed)
- **Languages:** Python 
- **Frameworks:** Flask / FastAPI (Backend), React (Frontend)  
- **Libraries:** OpenCV, EasyOCR, SQLAlchemy (Possibly implement YOLOv8) 
- **Database:** SQLite (MVP), PostgreSQL (Production)  
- **Deployment:** Docker
- **UI Tools:** TailwindCSS, Chart.js (for analytics)  

---
## Demonstration

Demonstration of both static image and live images.

---

### Static Image Demonstration

<img src="docs/example3.webp" width="500" alt="Static Test Image">
The number plate image used for testing the program
---
<img src="run_demo.png" width="500" alt="Terminal Output">
Terminal output showing result and confidence reading (0-1).
---
<img src="run_demo.png" width="500" alt="Terminal Output">
The final output on the UI. As you can see it shows a very basic documentation as a part of Phase 1.
---
## License
Licensed under the **MIT License**. Free to use, modify, and distribute.
