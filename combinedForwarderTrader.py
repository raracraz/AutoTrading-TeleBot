import time
import subprocess
import signal

# List to keep track of subprocesses
processes = []

def terminate_processes(signum, frame):
    """Terminate subprocesses when SIGINT is received."""
    for process in processes:
        process.terminate()
    exit(0)

# Set up the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, terminate_processes)

# Run messageForwarder.py
processes.append(subprocess.Popen(["py", "messageForwarder.py"]))

time.sleep(5)

# Run goldTradingGenius.py
processes.append(subprocess.Popen(["py", "goldTradingGenius.py"]))

# Wait forever
while True:
    time.sleep(1)
