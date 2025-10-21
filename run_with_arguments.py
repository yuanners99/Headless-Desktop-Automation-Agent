from desktop_agent_core import DesktopAgent
import argparse
import sys
import time
import os
from datetime import datetime
import signal

class StreamLogger:
    """Redirect stdout to both console and a log file."""
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()

def safe_exit(signal_received=None, frame=None):
    print("\nOperation interrupted by user.")
    sys.exit(130)

def main():
    signal.signal(signal.SIGINT, safe_exit)
    
    parser = argparse.ArgumentParser(description="Desktop agent to automate tasks based on user instructions.")
    parser.add_argument("instruction", type=str, help="Instruction for the desktop agent.")
    parser.add_argument("--session-id", type=str, default=None, help="Optional session ID to reuse an existing session folder.")
    args = parser.parse_args()

    instruction = args.instruction

    # Create a session directory for screenshots and logs
    if args.session_id:
        # Create nested structure: session/session_uniqueID/session_datetime
        parent_session_dir = os.path.join("session", f"session_{args.session_id}")
        os.makedirs(parent_session_dir, exist_ok=True)
        
        # Create datetime subfolder for this specific instruction
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(parent_session_dir, f"session_{session_timestamp}")
    else:
        # No parent session specified, use flat structure as before
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join("session", f"session_{session_timestamp}")

    os.makedirs(session_dir, exist_ok=True)
    log_file_path = os.path.join(session_dir, "session_log.txt")
    logger = StreamLogger(log_file_path)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = logger
    sys.stderr = logger

    try:
        print(f"Session data will be saved in: {session_dir}")
        time.sleep(5)
        agent = DesktopAgent(session_dir=session_dir)
        finished = False
        while not finished:
            try:
                status = agent.step(instruction)
            except Exception as e:
                print(f"Exception from agent.step(): {e}")
                sys.exit(2)

            if status == "finished":
                print("Instruction finished successfully.\n")
                sys.exit(0)
            elif status == "authenticate":
                print("Instruction requested user authentication (OTP/mobile number). Exiting with code 3.\n")
                sys.exit(3)
            elif status == "call_user":
                print("Instruction requested user intervention. Exiting with code 1.\n")
                sys.exit(1)
            else:
                # Continue until agent returns finished, authenticate, or call_user
                time.sleep(0.8)

        print("\nAll instruction blocks completed successfully.")

    finally:
        # restore stdout/stderr and close logger
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        logger.close()


if __name__ == "__main__":
    main()