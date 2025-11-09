# 📘 LingQ Practice Platform

This is a Django-based project for managing and practicing vocabulary, phrases, and lessons.  
It supports text and audio uploads, automatic data extraction, and user-specific progress tracking.

---

## 🚀 Features

- User authentication with Django’s built-in system.  
- Upload and process text/audio files.  
- Extract words, phrases, and meanings automatically.  
- Classify and track word/phrase learning status.  
- Clean project structure following Django best practices.  
- Easily extensible for future AI-assisted learning features.

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | **Django 5.2.7** |
| Database | **MySQL** |
| Audio Processing | **pydub**, **simpleaudio** |
| Document Parsing | **EbookLib**, **pdfminer.six**, **python-docx**, **BeautifulSoup4** |
| Video/Audio Download | **yt-dlp** |

## 📂 Project Structure
---
lingq/
│
├── core/ # Main app (models, views, signals)
├── utils/ # Utility functions (text/audio extraction, grouping)
├── run.ps1 # PowerShell script to run server and manage setup
├── requirements.txt # Python dependencies
└── manage.py # Django project entry point


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/lingq.git
cd lingq
pip install -r requirements.txt
.\run.ps1
