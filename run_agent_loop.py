import subprocess
import os
import time
import sys
import signal
import uuid
import argparse

def safe_exit(signal_received=None, frame=None):
    """Handle Ctrl+C gracefully"""
    print("\nOperation interrupted by user.")
    sys.exit(130) 

def main():
    signal.signal(signal.SIGINT, safe_exit)

    if len(sys.argv) < 2:
        print("Usage: python run_agent_loop.py <instructions_file> [--otp OTP_VALUE] [--mobile MOBILE_NUMBER]")
        sys.exit(2)

    # Set up OTP and mobile number arguments
    parser = argparse.ArgumentParser(description='Run agent loop with instructions file and optional OTP/mobile number')
    parser.add_argument('instructions_file', help='Path to the instructions file')
    parser.add_argument('--otp', help='OTP value to replace $Number in instructions')
    parser.add_argument('--mobile', help='Mobile number to replace $Mobile in instructions')
    
    args = parser.parse_args()
    
    instructions_file = args.instructions_file
    otp_value = args.otp
    mobile_value = args.mobile

    instructions_file = sys.argv[1]

    if not os.path.exists(instructions_file):
        print(f"Instructions file not found: {instructions_file}")
        sys.exit(2)

    try:
        # Read and split instructions by empty lines
        with open(instructions_file, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        print(f"Error reading instructions file:{e}")
        sys.exit(2)
        
    #Replace $Number with OTP value if provided
    if otp_value is not None:
        raw = raw.replace("$Number", otp_value)
        print(f"Replaced $Number with OTP value: {otp_value}")
    
    #Replace $Mobile with mobile number if provided
    if mobile_value is not None:
        raw = raw.replace("$Mobile", mobile_value)
        print(f"Replaced $Mobile with mobile number: {mobile_value}")

    instructions = [block.strip() for block in raw.split("\n\n") if block.strip()]

    if not instructions:
        print("No instructions found in the file. Exiting.")
        sys.exit(2)

    time.sleep(2)

    # Create a single parent session ID for all instructions in this batch
    parent_session_id = uuid.uuid4().hex
    print(f"\n--- [Batch Session] All instructions will be grouped under: session_{parent_session_id} ---\n")

    # Run each instruction sequentially
    for idx, instr in enumerate(instructions, start=1):
        print(f"\n--- [Instruction {idx}/{len(instructions)}] Sending instruction ---\n{instr}\nUsing parent session: session_{parent_session_id}\n")
        time.sleep(2)
        result = subprocess.run(
            ["python", "run_with_arguments.py", instr, "--session-id", parent_session_id],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        if result.returncode == 3:
            print(f"\n--- [Authentication Required] Instruction {idx} requested authentication (OTP/mobile number) ---")
            print("Exit code 3 returned. You can now execute the OTP/mobile number instructions.")
            print("Note: Use --otp and --mobile arguments if you have OTP/mobile values to pass.\n")
            sys.exit(3)
        elif result.returncode != 0:
            print("Stopping execution of remaining instructions.")
            sys.exit(result.returncode)

    print("\nAll instructions completed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
