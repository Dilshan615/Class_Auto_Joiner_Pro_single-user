# Java Institute Portal - Class Auto-Joiner Pro (single-user)🎓

A modern, automated desktop application designed specifically as a **single-user, personalized tool** for a student of the Java Institute for Advanced Technology. With a single click, it handles the complete routine of logging into the student portal, locating today's lecture from the active timetable, and completing Zoom meeting registration automatically.

> [!NOTE]
> **Single-User Dedicated Architecture:**  
> This software is strictly built and configured for single-user operation. It is designed to manage and automate the workflow of one student at a time, keeping credentials, portal session states, and Zoom registration details bound directly to the active user profile stored in `user_data.txt`.

---

## 👨‍💻 Developed By:
**Manja**

---

## ✨ Key Features:

* **Single-User Dedicated Workflow**: Personalized specifically for individual student routine automation with zero multi-user overhead.
* **One-Click Automation**: Launches Google Chrome, logs into the student portal, and navigates seamlessly to the dashboard.
* **Smart Timetable Scanner**: Automatically identifies and filters today's scheduled lecture card based on the current date and time slot.
* **Zoom Meeting Auto-Registrar**: Detects Zoom registration forms, automatically fills in required student fields, and submits the registration.
* **Session Persistence**: Chrome browser remains open throughout your lecture session so you never get disconnected.
* **Modern Dark-Mode UI**: Built with CustomTkinter featuring a sleek glassmorphism dashboard, dynamic status pill, and 2-column layout.
* **Developer Activity Console**: High-tech color-coded live terminal providing real-time status updates at every stage of execution.
* **Privacy & Data Isolation**: All credentials and user profile information are stored exclusively in an external configuration file (`user_data.txt`). Zero personal data is stored in the source code.

---

## 🚀 How to Run:

### Method 1 (Quick Launcher):
* Simply double-click **`run.bat`** in the project folder.

### Method 2 (Terminal / Command Prompt):
```bash
python app.py
```

---

## ⚙️ Setup & Configuration:

All user-specific configurations are managed through:
* **`user_data.txt`**

When the application is launched, you can view and update your portal login details and Zoom profile directly through the user interface, or edit `user_data.txt` directly. Changes made in the UI are automatically synchronized with the file.

---

## 📁 Project Architecture:

| File | Description |
| :--- | :--- |
| **`app.py`** | Modern graphical user interface (CustomTkinter) with live colored terminal console. |
| **`portal_automation.py`** | Browser automation engine (Selenium) for login, timetable detection, and Zoom registration. |
| **`user_data.txt`** | Dedicated configuration file storing user profile data and portal credentials. |
| **`run.bat`** | Windows one-click executable batch launcher. |
| **`requirements.txt`** | Python package dependencies (`customtkinter`, `selenium`, `webdriver-manager`). |
