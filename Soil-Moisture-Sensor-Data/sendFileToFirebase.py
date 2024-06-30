import serial
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

try:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate('authfile.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ayaan-ki-dua-default-rtdb.firebaseio.com/'
    })
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    exit(1)

arduino_port = 'COM9'
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate)
    time.sleep(2)
    print(f"Serial port {arduino_port} opened successfully.")
except serial.SerialException as e:
    print(f"Could not open port {arduino_port}: {e}")
    exit(1)

ref = db.reference('soilMoistureSensor')

try:
    current_value = None

    while True:
        if ser.in_waiting > 0:
            sensor_data = ser.readline().decode('latin-1').strip()
            print(f"Read from Arduino: {sensor_data}")

            if sensor_data.isdigit():
                value = int(sensor_data)
                status = None
            else:
                value = None
                status = sensor_data

            if value is not None:
                current_value = value

            if status is not None and current_value is not None:
                try:
                    ref.push({
                        'timestamp': int(time.time() * 1000),
                        'value': current_value,
                        'status': status
                    })
                    print("Uploaded to Firebase")
                except Exception as e:
                    print(f"Error uploading to Firebase: {e}")

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    ser.close()
    print("Serial port closed.")
