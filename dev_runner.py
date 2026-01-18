import subprocess
import threading
import time
import os
import signal
import sys
import re
import json
import http.client
from pathlib import Path

# --- CONFIGURATION ---
ONDEVICE_DIR = "ondevice"
SERVER_DIR = "server"
EXTERNAL_DIR = "external"
NGROK_PORT = 8000
SERVER_PORT = 8001
EXTERNAL_PORT = 8002
ENV_FILE = Path(SERVER_DIR) / ".env"

processes = []
stop_event = threading.Event()
is_cleaning_up = False


def log(msg, service="SYSTEM"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{service}] {msg}")


def run_service(name, cmd, cwd=None):
    """Runs a service in a separate process."""
    log(f"Starting {name}...", name)
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        bufsize=1,
    )
    processes.append(process)

    def monitor():
        for line in process.stdout:
            if stop_event.is_set():
                break
            line = line.strip()
            if line:
                # Specialized parsing for key events
                if "Received prompt from chat_id" in line:
                    log(f"Incoming Telegram Message: {line}", "TELEGRAM")
                elif "Received generation from laptop service" in line:
                    log("Laptop generation received", "SERVER")
                elif "Generation successful" in line:
                    log("Ollama generation complete", "ONDEVICE")
                elif "Payload:" in line:
                    log(f"External API Payload: {line}", "EXTERNAL")
                else:
                    print(f"[{name}] {line}")
        process.stdout.close()

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return process


def wait_for_health(url, name, timeout=30):
    """Waits for a service health check to return OK."""
    log(f"Waiting for {name} health check...", name)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection(url.replace("http://", ""))
            conn.request("GET", "/health")
            resp = conn.getresponse()
            if resp.status == 200:
                log(f"{name} is healthy!", name)
                return True
        except:
            pass
        time.sleep(1)
    log(f"Timeout waiting for {name}", name)
    return False


def get_ngrok_url():
    """Extracts ngrok URL from local API."""
    log("Fetching ngrok public URL...", "NGROK")
    time.sleep(5)  # Give it time to start
    try:
        conn = http.client.HTTPConnection("localhost:4040")
        conn.request("GET", "/api/tunnels")
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        log(f"Failed to get ngrok URL from API: {e}", "NGROK")
    return None


def update_env(ngrok_url):
    """Updates .env file with ngrok URL."""
    if not ngrok_url:
        log("No ngrok URL found, skipping .env update", "SYSTEM")
        return

    log(f"Updating {ENV_FILE} with ngrok URL: {ngrok_url}", "SYSTEM")
    lines = []
    updated = False
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    with open(ENV_FILE, "w") as f:
        for line in lines:
            if line.startswith("LAPTOP_API_URL="):
                f.write(f"LAPTOP_API_URL={ngrok_url}/generate\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"LAPTOP_API_URL={ngrok_url}/generate\n")


def trigger_mock_query(prompt="explain quantum mechanics"):
    """Sends a mock query to the gateway server."""
    log(f"Triggering mock query: '{prompt}'", "TEST_TRIGGER")
    try:
        conn = http.client.HTTPConnection(f"localhost:{SERVER_PORT}", timeout=None)
        payload = json.dumps(
            {
                "update_id": 999,
                "message": {"message_id": 1, "chat": {"id": 12345}, "text": prompt},
            }
        )
        headers = {"Content-Type": "application/json"}
        conn.request("POST", "/telegram/webhook", body=payload, headers=headers)
        resp = conn.getresponse()
        log(f"Response Status: {resp.status} {resp.reason}", "TEST_TRIGGER")
        log(f"Response Data: {resp.read().decode()}", "TEST_TRIGGER")
    except Exception as e:
        log(f"Failed to trigger mock query: {e}", "TEST_TRIGGER")


def cleanup(sig=None, frame=None):
    """Stops all processes."""
    global is_cleaning_up
    if is_cleaning_up:
        return
    is_cleaning_up = True

    log("Shutting down Ultron services...", "SYSTEM")
    stop_event.set()
    # Reverse to stop in dependency order
    for p in reversed(processes):
        try:
            log(f"Stopping process {p.pid}")
            if sys.platform == "win32":
                subprocess.call(
                    ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                p.terminate()
        except:
            pass
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    log("--- ULTRON LOCAL ORCHESTRATOR (DIRECT QUERY MODE) ---")

    # 1. Start External Mock API
    run_service("EXTERNAL", "node index.js", cwd=EXTERNAL_DIR)

    # 2. Start On-Device Service
    run_service("ONDEVICE", "uvicorn app:app --port 8000", cwd=ONDEVICE_DIR)
    if not wait_for_health("localhost:8000", "ONDEVICE"):
        cleanup()

    # 3. Start ngrok
    run_service("NGROK", f"ngrok http {NGROK_PORT}")
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        log(f"CAPTURE: Public ngrok URL: {ngrok_url}", "NGROK")
        update_env(ngrok_url)
    else:
        log(
            "CRITICAL: Could not capture ngrok URL. Gateway might use old URL.",
            "SYSTEM",
        )

    # 4. Start Server Gateway
    run_service("SERVER", "uvicorn main:app --port 8001", cwd=SERVER_DIR)
    if not wait_for_health("localhost:8001", "SERVER"):
        cleanup()

    log("ALL SERVICES RUNNING.", "SYSTEM")

    # 5. Trigger Mock Query
    time.sleep(2)  # Final buffer
    trigger_mock_query("explain quantum mechanics")

    log(
        "TEST COMPLETE. Press Ctrl+C to stop services or send more Telegram messages.",
        "SYSTEM",
    )

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
