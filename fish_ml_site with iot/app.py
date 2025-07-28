import serial
import time

# Set up the serial connection (adjust 'COM9' to your system's port)
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)


def read_from_arduino():
    while True:
        try:
            # Read data from Arduino and decode it
            data = arduino.readline().decode('utf-8').strip()

            if data:  # If there's data, print it
                print("Received data:", data)
                # Here, you can process the data or save it to a file if needed.
                # You can parse the dict if you want to break down the values.

            time.sleep(3)  # Wait for the next data (3-second intervals)
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    read_from_arduino()
