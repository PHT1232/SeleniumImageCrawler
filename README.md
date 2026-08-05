# Selenium Image Crawler API

An advanced automation system that acts as an API bridge for Google's Image Generation Flow. Built with FastAPI and Selenium, it bypasses advanced Bot Detection mechanisms using human-like interaction simulations, and implements a robust sequential queueing system for concurrency.

## Core Features
- **API Compatible with Google Gemini**: Request and Response schemas are perfectly modeled after Google Gemini API standard formats, making it a plug-and-play solution.
- **Bot Detection Bypass**: 
  - Uses `undetected-chromedriver` to mask automation signatures.
  - Replaces mechanical clicks with `ActionChains` natural mouse trajectories.
  - Implements rapid CDP (Chrome DevTools Protocol) text injection to bypass synthetic key-event flagging.
- **Concurrency & Queue System**: Safely handles concurrent incoming HTTP requests by organizing them into an asynchronous queue, processing them sequentially through a ThreadPool, and resting 5 seconds between tasks to preserve Trust Score and IP reputation.
- **Background Extraction**: Stealthily extracts generated images via injected JavaScript Fetch logic without interacting with the UI Download buttons.

## Prerequisites
- Python 3.10+
- Google Chrome installed on the host machine.
- Valid Google Account.

## Installation

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize Google Login Session:
Because Google blocks automated logins, you must run this script once to manually log in to your Google Account.
```bash
python3 login.py
```
This will open a browser. Log in to your account. Once done, close the browser. Your session is now saved in the `chrome_profile/` directory.

## Usage

Start the FastAPI server:
```bash
python3 main.py
```
The server will start on `http://127.0.0.1:8989`.

### Testing the API
You can test the queueing mechanism and generation logic using the provided test scripts:
```bash
python3 test_api_1.py
python3 test_api_2.py
```

### API Endpoint (`POST /generate`)
**Request format:**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "A futuristic cyberpunk city at night with neon lights and flying cars, high resolution, photorealistic."
        }
      ]
    }
  ]
}
```

**Response format:**
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "inlineData": {
              "mimeType": "image/png",
              "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
            }
          }
        ]
      }
    }
  ]
}
```

## Deployment on CLI Servers (Fedora/Ubuntu/CentOS)
Running this tool in `--headless` mode will trigger Google's Bot Detection. To run on a CLI-only server without a physical monitor, you must use a virtual framebuffer (`Xvfb`) to run Chrome in standard headed mode (`headless=False`).

1. **Install Xvfb and VNC Tools**
   - On Fedora/CentOS: `sudo dnf install xorg-x11-server-Xvfb x11vnc novnc websockify`
   - On Ubuntu/Debian: `sudo apt-get install xvfb x11vnc novnc websockify`

2. **Initialize Google Login Session via VNC (First Time Only)**
   Google's session cookies are encrypted by the host OS keyring, meaning you cannot reliably transfer a `chrome_profile` from a Windows/Mac machine to a Linux Server. You **must** log in directly on the server.
   
   Run the following commands to start a web-based VNC server:
   ```bash
   killall -9 Xvfb x11vnc websockify chrome chromedriver python3 2>/dev/null; \
   Xvfb :99 -screen 0 1280x720x24 & \
   sleep 2; \
   x11vnc -display :99 -bg -nopw -listen localhost -xkb -forever; \
   websockify --web=/usr/share/novnc/ 6080 localhost:5900 & \
   DISPLAY=:99 google-chrome --user-data-dir=$(pwd)/chrome_profile --no-sandbox "https://accounts.google.com" &
   ```
   - Open your personal web browser and navigate to `http://<YOUR_SERVER_IP>:6080/vnc.html` (or `vnc_lite.html`).
   - Click **Connect** and interact with the server's virtual desktop to log in to your Google Account.
   - After successfully logging in, return to the server terminal and close the processes:
     ```bash
     killall google-chrome
     ```
   - **Crucial Note:** If Chrome ever crashes or is killed forcefully, it will leave behind lock files. You must delete them before restarting the server to prevent the bot from hanging:
     ```bash
     rm -f chrome_profile/Singleton*
     ```

3. **Run the API Server**
   Wrap the main script in `xvfb-run` to run it headlessly inside the virtual buffer:
   ```bash
   xvfb-run -a python3 main.py
   ```
   This creates a virtual monitor in the RAM, allowing the bot to click and type stealthily without triggering headless-bot detection.

## Architecture Details
For a deep dive into the system's inner workings, refer to [system_arch.md](system_arch.md).
For a timeline of bug fixes (specifically regarding Google's Bot Detection), refer to [fix-requirement.md](fix-requirement.md).

## Disclaimer
This project is for educational and research purposes. Heavy usage may result in your IP address or Google Account being flagged by Google. Always use responsibly.
