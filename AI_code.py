import cv2
import time
import serial
import threading
import sys
from collections import Counter
from ultralytics import YOLO
import winsound

# --- CONFIGURATION ---
SERIAL_PORT = 'COM19'   
BAUD_RATE = 9600
CONFIDENCE_THRESHOLD = 0.5
send_delay = 0.3 # Send command every n seconds

# --- COMMANDS ---
CMD_START = b'Y'       # Sent to Arduino when you type 'y'
CMD_STOP = b'N'       # Sent to Arduino when you type 'n'
CMD_DROWSY = b's'      # Stop command
CMD_AWAKE = b'n'       # Normal command
CMD_NO_FACE = b's'     # Lost face command

# Global flag to stop threads safely
running = True
sending = True

# --- 1. BLUETOOTH HANDLER ---
def connect_bluetooth():
    try:
        bt = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[Success] Connected to {SERIAL_PORT}")
        return bt
    except Exception as e:
        print(f"[Error] Bluetooth failed: {e}")
        return None

# --- 2. EMERGENCY LISTENER THREAD ---
# This runs in background ONLY to listen for Arduino warnings
def listen_for_arduino(bluetooth_serial):
    global running
    print(" -> Listener Thread Active")
    
    while running:
        if bluetooth_serial and bluetooth_serial.in_waiting:
            try:
                # Read data from Arduino
                incoming = bluetooth_serial.read().decode().strip()
                
                # If Arduino sends 'w' (warning)
                if incoming == 'w':
                    print("\n[ALARM] Arduino sent Warning Signal!")
                    winsound.Beep(1000, 500) # Frequency, Duration
                elif incoming == 'c':
                    print("\n[confirmation massage] arduino sent confirmation massege")
                    confirmation_massege(bluetooth_serial)

            
            except Exception as e:
                print(f"Serial Error: {e}")
        time.sleep(0.1)

def confirmation_massege(bluetooth):
    global sending
    global running
    sending = False
    while True:
        user_input = input("Command (y/n): ").strip().lower()
        if user_input == 'y':
            print("Confirmation received. Sending 'Y' to Arduino...")
            bluetooth.write(CMD_START) # Tell Arduino to wake up
            sending = True
            break
        elif user_input == 'n':
            bluetooth.write(CMD_STOP)
            running = False
        else:
            print("Invalid. Type 'yes' to start or 'exit'.")


# --- 3. MAIN PROGRAM ---
def main():
    global running
    global sending
    
    # A. CONNECT BLUETOOTH
    print("--- SYSTEM BOOTING ---")
    bluetooth = connect_bluetooth()

    if not bluetooth:
        print("Cannot proceed without Bluetooth. Exiting.")
        return

    # B. THE GATEKEEPER (Waits for your input)
    print("\n" + "="*40)
    print(" SYSTEM ARMED. WAITING FOR CONFIRMATION.")
    print(" Type 'y' to open camera and start engine.")
    print("="*40)
    print("\n[1/3] Loading YOLO Model...")
    model = YOLO('Drowsnessmodel.pt')

    confirmation_massege(bluetooth)

    # C. START AI & CAMERA (Only happens after break above)
    
    print("[2/3] Starting Listener Thread...")
    t1 = threading.Thread(target=listen_for_arduino, args=(bluetooth,), daemon=True)
    t1.start()

    print("[3/3] Opening Camera...")
    cap = cv2.VideoCapture(0)
    
    # Timing variables for sending data (don't spam Arduino)
    last_send_time = time.time()
    current_state = CMD_AWAKE

    print("\n--- AI SYSTEM RUNNING (Press 'q' to stop) ---")

    try:
        while running:
            ret, frame = cap.read()
            if not ret:
                print("Camera error.")
                break

            # --- AI INFERENCE ---
            results = model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)
            
            detected_class = "No Detection"
            
            # Check results
            if len(results[0].boxes) > 0:
                cls_id = int(results[0].boxes.cls[0])
                detected_class = results[0].names[cls_id]

            # --- LOGIC MAPPING ---
            if detected_class == 'Drowsiness':
                new_state = CMD_DROWSY
            elif detected_class == 'awake':
                new_state = CMD_AWAKE
            else:
                new_state = CMD_NO_FACE

            #print(str(new_state)  , detected_class)

            # --- VISUALIZATION ---
            # Draw the box on the frame
            annotated_frame = results[0].plot()
            
            # Add status text
            color = (0, 255, 0) if new_state == CMD_AWAKE else (0, 0, 255)
            cv2.putText(annotated_frame, f"Status: {detected_class}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            cv2.imshow("Driver Monitor", annotated_frame)

            # --- SEND TO ARDUINO ---
            # We send data based on time (every 0.5s) to prevent lag
            if (((time.time() - last_send_time) > send_delay) and sending):
                if bluetooth.is_open:
                    bluetooth.write(new_state)
                    print('sending'+str(new_state)+"to the arduino at " + time.ctime(time.time()))
                    # print(f"Sent to Arduino: {new_state}") # Uncomment to debug
                last_send_time = time.time()

            # --- EXIT KEY ---
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        # Cleanup
        running = False # Stops the thread
        cap.release()
        bluetooth.close()
        cv2.destroyAllWindows()
        print("System Shutdown.")

if __name__ == "__main__":
    main()