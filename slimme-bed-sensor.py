import serial
import mysql.connector
from datetime import datetime
import time

# Configuratie van Arduino op de laptop qua verbinding 
ARDUINO_PORT = 'COM3'
BAUD_RATE = 9600

# Database verbinding
db_config = {
    'host': '100.118.67.62',
    'database': 'IoT_Database',
    'user': 'admin',
    'password': 'admin'
}

GATEWAY_ID = 2  # Gateway ID voor de database, laat zien op de applicatie welke kamer het zal zijn
SENSOR_IDS = [1, 2, 3]  # Sensor ID voor de database, Welke bedden in kamers


# Verbinding maken van laptop met de arduino
def connect_to_arduino(port, baud_rate, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            print(f"Successfully connected to Arduino on {port}")
            return ser
        except serial.SerialException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None

# Verbinding maken van laptop met de database
def connect_to_database(config, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            db = mysql.connector.connect(**config)
            print("Successfully connected to the database")
            return db
        except mysql.connector.Error as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None


# Foutmeldingen voor troubleshooting bij verbinden
def main():
    ser = connect_to_arduino(ARDUINO_PORT, BAUD_RATE)
    if not ser:
        print("Failed to connect to Arduino. Exiting.")
        return

    db = connect_to_database(db_config)
    if not db:
        print("Failed to connect to database. Exiting.")
        ser.close()
        return

    cursor = db.cursor()

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                if line.startswith("GATEWAY:"):
                    parts = line.split(',')
                    gateway_id = int(parts[0].split(':')[1])
                    sensor_id = int(parts[1].split(':')[1])
                    state = parts[2].split(':')[1]
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    state_bool = state == "1"

                    sql = "INSERT INTO data (Id, GatewayId, SensorId, Timestamp, Value) VALUES (NULL, %s, %s, %s, %s)"
                    val = (gateway_id, sensor_id, timestamp, state_bool)
                    cursor.execute(sql, val)
                    db.commit()

                    print(f"Inserted: GatewayId={gateway_id}, SensorId={sensor_id}, Timestamp={timestamp}, Value={state_bool}")

    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing connections")
        ser.close()
        db.close()

if __name__ == "__main__":
    main()