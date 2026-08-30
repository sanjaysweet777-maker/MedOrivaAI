# MedOriva AI — MVP Setup Guide

## What you need
- Python 3.8 or above (free download: https://python.org)
- Internet connection (for Google Translate API via deep-translator)
- Any modern browser (Chrome, Firefox, Edge)

---

## Step-by-step setup

### Step 1 — Open a terminal / command prompt
- Windows: Press Win + R, type `cmd`, press Enter
- Mac: Press Cmd + Space, type `Terminal`, press Enter

### Step 2 — Go into the medoriva folder
```
cd path/to/medoriva
```
Replace `path/to/medoriva` with the actual folder location.
Example on Windows: `cd C:\Users\YourName\Desktop\medoriva`
Example on Mac:     `cd ~/Desktop/medoriva`

### Step 3 — Create a virtual environment (recommended)
```
python -m venv venv
```

### Step 4 — Activate the virtual environment
Windows:
```
venv\Scripts\activate
```
Mac / Linux:
```
source venv/bin/activate
```
You will see `(venv)` appear at the start of your terminal line.

### Step 5 — Install dependencies
```
pip install -r requirements.txt
```
This installs Flask and deep-translator. Takes about 30 seconds.

### Step 6 — Run the app
```
python app.py
```
You will see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 7 — Open in your browser
Go to: http://127.0.0.1:5000

MedOriva AI is now running on your laptop.

---

## How to use
1. Select a context (Reception / Appointment / Basic Symptoms)
2. Select the patient's language
3. Click "Start session"
4. Use guided prompts (sidebar) or type a free-text message
5. Enter patient's response in the "Patient response" tab to translate back to English
6. Click "End session" when done — all data is cleared

---

## To stop the app
Press Ctrl + C in the terminal.

## To run again next time
```
cd path/to/medoriva
venv\Scripts\activate      (Windows)
source venv/bin/activate   (Mac)
python app.py
```
Then open http://127.0.0.1:5000

---

## Troubleshooting
- "python not found" → Install Python from https://python.org and tick "Add to PATH"
- "pip not found" → Try `python -m pip install -r requirements.txt`
- Translation not working → Check your internet connection
- Port already in use → Change port in app.py: `app.run(port=5001)`
