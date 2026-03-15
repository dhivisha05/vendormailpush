import subprocess
import time
import sys
import os

def run_system():
    # Get the directory where run_app.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Start Backend
    print(f"Starting Backend (FastAPI) in {base_dir}...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=base_dir
    )
    
    time.sleep(3) # Wait for backend to initialize
    
    # Check if backend is still running
    if backend_process.poll() is not None:
        print("Error: Backend failed to start.")
        return

    # 2. Start Frontend
    print(f"Starting Frontend (Streamlit) in {base_dir}...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/dashboard/app.py"],
        cwd=base_dir
    )
    
    try:
        while True:
            time.sleep(1)
            # Monitor processes
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\nStopping system...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    run_system()
