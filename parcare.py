import mysql.connector
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
from paddleocr import PaddleOCR
import numpy as np
import subprocess
import time
import threading
import queue
import serial

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

model = YOLO('best_float32.tflite')
ocr = PaddleOCR()
image_queue = queue.Queue(maxsize=50)

detected_numbers = set()
stop_processing = False
capture_done_event = threading.Event()
processing_done_event = threading.Event()

max_masini = 4
nr_masini_detectate = 0

def load_freespots():
    try:
        with open("freespots.txt", "r") as f:
            return int(f.read())
            return max(0, value)  # prevenim valori negative
    except FileNotFoundError:
        return 4  # valoare default dacă fișierul nu există

def save_freespots():
    with open("freespots.txt", "w") as f:
        f.write(str(freeSpots))

# Citește numărul de locuri libere din fișier când pornește programul
freeSpots = load_freespots()
print(f"Locuri libere la pornire: {freeSpots}")

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="parcare"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Eroare conexiune MySQL: {err}")
        return None

def check_number_in_db(number_plate):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masini WHERE nrinmatriculare = %s", (number_plate,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def perform_ocr(image_array):
    if image_array is None:
        return ""

    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    results = ocr.ocr(image_rgb, rec=True)
    detected_text = ""

    if results[0] is not None:
        for result in results[0]:
            detected_text += result[1][0]

    return detected_text.replace(" ", "")

with open("coco1.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

def capture_images():
    global stop_processing
    while True:
        if stop_processing:
            time.sleep(1)
            continue

        print("Capturare imagine...")
        subprocess.run("libcamera-jpeg -o temp_image.jpg", shell=True)

        im = cv2.imread("temp_image.jpg")
        if im is not None:
            if not image_queue.full():
                image_queue.put(im)
            else:
                print("Coada este plină, se ignoră imaginea capturată.")
        else:
            print("Eroare la citirea imaginii!")

        capture_done_event.set()
        capture_done_event.clear()

        time.sleep(3)

def process_images():
    global detected_numbers, stop_processing, nr_masini_detectate, freeSpots

    while True:
        if stop_processing:
            time.sleep(1)
            continue

        if not image_queue.empty():
            im = image_queue.get()
            im = cv2.flip(im, -1)

            results = model.predict(im, imgsz=256)

            if results[0].boxes.data.shape[0] == 0:
                print("Nicio plăcuță detectată. Continuare...")
                continue

            px = pd.DataFrame(results[0].boxes.data).astype("float")

            for index, row in px.iterrows():
                x1, y1, x2, y2, d = map(int, row[:5])
                c = class_list[d]

                crop = im[y1:y2, x1:x2]
                if crop.size == 0:
                    print("Eroare: Plăcuța decupată nu conține date!")
                    continue

                crop = cv2.resize(crop, (400, 200))
                crop = cv2.rotate(crop, cv2.ROTATE_180)

                text = perform_ocr(crop)
                text = text.replace('(', '').replace(')', '').replace(',', '').replace(']', '').replace('-', ' ')

                print(f"Număr detectat: {text}")

                if text in detected_numbers:
                    print(f"{text} a fost deja detectat recent. Aștept altă mașină...")
                    continue

                detected_numbers.add(text)
                if len(detected_numbers) > 5:
                    detected_numbers.clear()

                if check_number_in_db(text):
                    if freeSpots > 0 and nr_masini_detectate < max_masini:
                        print("Numărul este în baza de date și mai sunt locuri. Se deschide bariera!")
                        arduino.write(b"OPEN\n")
                        freeSpots -= 1  # Scade locurile libere
                        freeSpots = max(freeSpots, 0)  # Siguranță: nu lăsăm sub 0
                        save_freespots()  # Salvează în fișier
                        nr_masini_detectate += 1
                    else:
                        print("Parcarea este plină! Nu se deschide bariera.")
                        arduino.write(b"CLOSE\n")
                else:
                    print("Numărul NU este în baza de date. Nu se deschide bariera.")
                    arduino.write(b"CLOSE\n")

                if nr_masini_detectate >= max_masini:
                    print("S-au detectat toate cele 4 mașini.")
                    stop_processing = True
                    reset_system_later()
                    break

def reset_system_later():
    def reset():
        global stop_processing, detected_numbers, nr_masini_detectate
        print("Se resetează sistemul în 10 secunde...")
        time.sleep(10)
        detected_numbers.clear()
        nr_masini_detectate = 0
        stop_processing = False
        with image_queue.mutex:
            image_queue.queue.clear()
        print("Sistem resetat. Gata pentru un nou set de mașini.")
    threading.Thread(target=reset).start()

def listen_from_arduino():
    global stop_processing, freeSpots
    while True:
        if arduino.in_waiting:
            mesaj = arduino.readline().decode().strip()
            
            
            if mesaj == "EXIT":
                freeSpots = load_freespots()  # ← sincronizare
                freeSpots += 1
                freeSpots = min(freeSpots, max_masini)  # nu mai mult decât maximul
                save_freespots()
                print(f"Mașină ieșită  ")
            
            elif mesaj.isdigit():
                freeSpots = int(mesaj)
                save_freespots()
            
            
            
            
            if mesaj == "INTRARE":
                print("S-a detectat o mașină ...")
                stop_processing = False  # permite procesarea

# PORNEȘTE FIRELE O SINGURĂ DATĂ LA START
threading.Thread(target=capture_images, daemon=True).start()
threading.Thread(target=process_images, daemon=True).start()

# ASCULTĂ ÎN CONTINUU DE LA ARDUINO
listen_from_arduino()
