# Parcare-inteligenta
# Smart Parking System – License Project

This project is a smart parking system developed for a university license thesis. It integrates license plate recognition, hardware control (Arduino), and a web interface with database management.

---

## 🔧 Project Components

### 1. `parcare.py` (Raspberry Pi)
- Uses a camera to detect license plates in real time.
- Recognizes the plate and checks if it exists in the database.
- If the vehicle is authorized, it sends a signal to Arduino via serial communication to open the barrier.

### 2. `arduino.ino` (Arduino Code)
- Controls ultrasonic sensors to detect cars at the entrance and in parking spots.
- Controls LEDs: 
  - Green = available
  - Red = occupied
- Displays the number of available parking spots on an LCD screen.
- Opens the barrier when receiving a signal from Raspberry Pi.

### 3. `app.py` (Web Backend)
- Flask-based backend for the web interface.
- Connects to the database (MySQL).
- Provides the following functionalities:
  - Add/Edit/Delete authorized vehicles.
  - User login with 2FA (6-digit code sent via email).
  - Session management (logout, authentication).

### 4. `templates/` (HTML Files)
- Contains all the HTML files for the web pages:
  - Login
  - Dashboard
  - Vehicle management
  - Parking spot status

### 5. `static/` (CSS & JavaScript)
- `style.css`: Styling for the web interface.
- `script.js`: JavaScript code for interactivity (e.g., form validation, dynamic updates).

---

## 📡 Technologies Used

- **Raspberry Pi** (Python with OpenCV and EasyOCR)
- **Arduino Uno** (C/C++)
- **Flask** (Web framework)
- **HTML/CSS/JavaScript**
- **MySQL / SQLite**
- **Serial Communication** (between Pi and Arduino)
- **SMTP (Email)** for 2FA login

---

## 🧠 How it works

1. A camera detects the vehicle’s license plate using Python and OCR.
2. If the plate is authorized:
   - The Raspberry Pi sends a signal to Arduino.
   - The barrier opens and the LCD updates the available spots.
3. The web interface allows admins to:
   - Manage vehicles.
   - Monitor spots.
   - Authenticate securely with an email code.
     
🚀 Installation and Run Instructions
Raspberry Pi
# Install dependencies
sudo apt update
pip install opencv-python easyocr serial mysql-connector-python flask

# Run the parking script
python3 parcare.py

Arduino
Open arduino.ino in Arduino IDE.
Select the correct board and port.
Upload the code.

Web Interface
# Navigate to project folder
cd webapp

# Install Flask if not already installed
pip install flask

# Run the app
python app.py
Access web interface via: http://<raspberry-pi-ip>:5000/
---



