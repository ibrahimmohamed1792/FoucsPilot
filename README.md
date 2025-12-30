# FocusPilot

FocusPilot is an IoT project driven by Computer Vision, designed to monitor driver states and enhance road safety. The system uses a YOLO deep learning model to detect drowsiness and communicates real-time alerts to an Arduino-based hardware module via Bluetooth.

---

## 🚀 Key Features
* **Real-Time Detection**: Utilizes YOLO to identify "Drowsiness" or "awake" states from a live camera feed.
* **Bluetooth Integration**: Bidirectional communication between the Python AI engine and an Arduino hardware module.
* **Safety Gatekeeper**: Includes a manual confirmation step ('y'/'n') to arm the system before activating the camera and engine commands.
* **Emergency Listener**: A background thread listens for hardware warning signals ('w') from the Arduino to trigger local PC alerts.

---

## 🛠️ Configuration
The following settings in `AI_code.py` can be adjusted to match your hardware setup:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SERIAL_PORT` | `COM19` | The Bluetooth COM port for Arduino communication |
| `BAUD_RATE` | `9600` | Standard serial baud rate |
| `CONFIDENCE_THRESHOLD` | `0.5` | Minimum confidence for YOLO detections |
| `send_delay` | `0.3` | Frequency (seconds) of state updates sent to Arduino |

---

## 📡 Communication Protocol
The system uses byte-coded commands to interact with the hardware:

| Command | Byte | Meaning |
| :--- | :--- | :--- |
| **Start** | `Y` | Sent to Arduino to start the engine/system |
| **Stop** | `N` | Sent to Arduino to stop the engine/system |
| **Drowsy** | `s` | Sent when drowsiness or no face is detected |
| **Awake** | `n` | Sent when the driver is detected as awake |
| **Warning** | `w` | Received from Arduino to trigger a PC beep alarm |
| **Confirmation**| `c` | Received from Arduino to prompt for user manual input |

---

## 🔧 Installation & Usage

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/ibrahimmohamed1792/foucspilot.git](https://github.com/ibrahimmohamed1792/foucspilot.git)
    cd FocusPilot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the System**:
    * Ensure your Bluetooth module is paired and connected to the correct COM port.
    * Place your model file `Drowsnessmodel.pt` in the project root.
    * Execute the script:
        ```bash
        python AI_code.py
        ```
    * Follow the terminal prompts: Type `y` to open the camera and arm the system.
    * Press `q` in the camera window to stop the system safely.

---

## 📄 License
This project is licensed under the terms provided in the [LICENSE](LICENSE) file.
