import subprocess
import threading
import time
import signal
import sys
import os


def log(msg, service="SYSTEM"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{service}] {msg}")


def monitor_process(name, process, stop_event):
    """Monitors a process and logs its output."""
    for line in process.stdout:
        if stop_event.is_set():
            break
        line = line.strip()
        if line:
            print(f"[{name}] {line}")
    process.stdout.close()


def main():
    stop_event = threading.Event()
    processes = []

    # Change to the directory of the script to ensure paths are correct
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    commands = [
        ("UVICORN", "uvicorn app:app --host 0.0.0.0 --port 8000"),
        ("CLOUDFLARE", "cloudflared tunnel run ultron"),
    ]

    log("Starting Ultron on-device services...")

    for name, cmd in commands:
        log(f"Starting {name}: {cmd}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            bufsize=1,
        )
        processes.append((name, process))
        thread = threading.Thread(
            target=monitor_process, args=(name, process, stop_event), daemon=True
        )
        thread.start()

    def cleanup(sig=None, frame=None):
        log("Shutting down services...")
        stop_event.set()
        for name, process in processes:
            log(f"Stopping {name}...")
            if sys.platform == "win32":
                subprocess.call(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    log("Services are running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
            # Check if any process has exited unexpectedly
            for name, process in processes:
                if process.poll() is not None:
                    log(
                        f"CRITICAL: {name} process exited with code {process.returncode}",
                        "ERROR",
                    )
                    cleanup()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
