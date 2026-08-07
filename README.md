# Selenium Image Crawler API

An advanced automation system that acts as an API bridge for Google's Image Generation Flow. Built with FastAPI and Selenium, it bypasses advanced Bot Detection mechanisms using human-like interaction simulations, and implements a robust sequential queueing system for concurrency.

## Core Features
- **API Compatible with Google Gemini**: Request and Response schemas are perfectly modeled after Google Gemini API standard formats, making it a plug-and-play solution.
- **Bot Detection Bypass**: 
  - Uses `undetected-chromedriver` to mask automation signatures.
  - Replaces mechanical clicks with `ActionChains` natural mouse trajectories.
  - Implements rapid CDP (Chrome DevTools Protocol) text injection to bypass synthetic key-event flagging.
- **Concurrency & Queue System**: Safely handles concurrent incoming HTTP requests by organizing them into an asynchronous queue, processing them sequentially through a ThreadPool, and resting 30-45 seconds between tasks to preserve Trust Score and IP reputation.
- **Keep-Alive Space Streaming**: Automatically streams space characters (` `) via `Transfer-Encoding: chunked` during long queue waits to prevent Cloudflare/Reverse-Proxy timeout disconnections (100s limit), transparently delivering valid JSON at the end.
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

## Deployment on Linux Servers (Physical GUI Recommended)
Running this tool in `--headless=new` or inside a virtual buffer (`Xvfb`) will trigger Google's advanced Bot Detection leading to "Something went wrong" errors. To completely bypass this, you **must use a physical Desktop Environment (like XFCE) connected to a real monitor (or dummy HDMI plug) to utilize hardware GPU rendering.**

1. **Install XFCE Desktop on your server (e.g., Fedora):**
   ```bash
   sudo dnf groupinstall "Xfce Desktop"
   sudo systemctl isolate graphical.target
   ```

2. **Initialize Google Login Session (First Time Only)**
   Google's session cookies are encrypted by the host OS keyring. You **must** plug in a physical mouse/keyboard and log in directly on the XFCE desktop:
   - Open Terminal on the XFCE desktop and run: `python3 login.py`
   - Log in to your Google Account. Close the browser when done.
   
   **Crucial Note on Zombie Processes & Locks:** If Chrome ever crashes, it will leave behind lock files and zombie processes (`chromium` or `chrome`). You must delete them before restarting the server to prevent `SessionNotCreatedException`:
   ```bash
   killall -9 chrome chromium chromium-browser chromedriver python3 2>/dev/null
   rm -rf chrome_profile/Default/Singleton*
   ```

3. **Run the API Server via SSH (X11 Permission Fix)**
   Because you are running a GUI application from a remote SSH session (likely as `root`), the X11 server will block the connection. To fix this:
   - Physically go to the XFCE Desktop, open Terminal, and run: `xhost +` (This unlocks the display).
   - Then, from your remote SSH terminal, run:
   ```bash
   DISPLAY=:0 python3 main.py
   ```
   The Chrome window will physically pop up on the attached monitor and process requests automatically.

## Architecture Details
For a deep dive into the system's inner workings, refer to [system_arch.md](system_arch.md).
For a timeline of bug fixes (specifically regarding Google's Bot Detection), refer to [fix-requirement.md](fix-requirement.md).

## Disclaimer
This project is for educational and research purposes. Heavy usage may result in your IP address or Google Account being flagged by Google. Always use responsibly.
