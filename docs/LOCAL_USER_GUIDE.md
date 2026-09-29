# 📖 Local User Guide: How to Run & Use Travel Concierge AI Agent on Your Personal Laptop

> **A step-by-step tutorial with screenshots to setup, start, and run the Travel Concierge AI Agent locally.**

---

## 🛠️ 1. Prerequisites

Before starting, ensure your laptop has the following tools installed:

1. **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
2. **Google Cloud SDK (`gcloud`)**: Download from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)
3. **`uv` Package Manager**: Install via terminal:
   ```bash
   pip install uv
   ```
4. **Git**: Download from [git-scm.com](https://git-scm.com/)

---

## 📥 2. Step-by-Step Installation

### Step 2.1 — Clone the GitHub Repository
Open your Terminal (macOS/Linux) or Command Prompt / PowerShell (Windows) and run:

```bash
git clone https://github.com/K-MohanSaiTeja/buildwithgemini-travel-concierge.git
cd buildwithgemini-travel-concierge
```

---

### Step 2.2 — Install Python Dependencies
Install all required libraries using `uv`:

```bash
uv sync
```

---

### Step 2.3 — Authenticate with Google Cloud
Sign in to your Google Cloud account so the agent can access Vertex AI models and Memory Bank:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

---

### Step 2.4 — Configure `.env` File
Create a `.env` file in the root directory:

```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-east1
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
```

---

### Step 2.5 — Seed the Destination Catalog
Populate your local database with initial travel destinations:

```bash
uv run python seed_database.py
```

---

## 🚀 3. Starting the Agent & Web Application

### Step 3.1 — Start the ADK Agent Engine Backend
In your first terminal window, launch the agent backend:

```bash
uv run adk web app
```
*(The backend will start listening at `http://127.0.0.1:8000`)*

---

### Step 3.2 — Start the Custom Web Frontend
Open a **second terminal window**, navigate to the `frontend` folder, and launch the UI web server:

```bash
cd frontend
uv run uvicorn main:app --reload --port 8080
```
*(The web UI will start at `http://localhost:8080`)*

---

## 🌐 4. How to Use the Travel Concierge

Open your browser and navigate to **`http://localhost:8080`**.

### 📸 Application Interface Overview

![App Interface](../assets/app_screenshot.png)

1. **Clickable Quick Prompts**: Click on example prompt buttons above the input box (e.g. `🏖️ Top Beach Destinations`, `📍 Find Attractions in Tokyo`, `🎨 Postcard for Golden Gate`).
2. **Interactive A2UI Cards**: The agent responds with rich interactive card displays, photo galleries, and video previews instead of plain text.

![Rich Card Display](../assets/card_rendering_screenshot.png)

---

## 💡 5. Example Prompts to Try

| Goal | Example Prompt |
| :--- | :--- |
| **Personalized Recommendations** | `"Recommend 3 quiet beach destinations for a family vacation"` |
| **Generative Postcard Image** | `"Generate a postcard for the Eiffel Tower in Paris"` |
| **Video Preview Creation** | `"Generate a short video preview of San Francisco"` |
| **Google Maps Places Lookup** | `"Find top rated ramen restaurants near Tokyo Station"` |
| **Currency & Budget Calculation**| `"Convert $1500 USD to Japanese Yen and compute daily budget for 5 days"` |

---

## ❓ Troubleshooting

- **Error: `403 Permission Denied`**: Ensure `gcloud auth application-default login` has been executed.
- **Missing Images**: Ensure your GCP project has the Vertex AI API enabled.
