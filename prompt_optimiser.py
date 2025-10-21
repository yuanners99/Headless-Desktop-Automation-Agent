
"""
Prompt Engineering Module for user instructions

This standalone script accepts user's  instructions and
uses the UI-TARS model to optimise them for automation.

Usage:
  python prompt_optimiser.py "Your instructions here"
  python prompt_optimiser.py --file input.txt
"""

import argparse
import requests
import sys
import re
import json


# System prompt for instruction refinement
SYSTEM_PROMPT = """
You are a task breakdown assistant. Break down user instructions into simple, step-by-step actions.

RULES:
1. Each action goes on its own line
2. Put an empty line between each action
3. Keep exact text unchanged (emails, passwords, names, numbers)
4. Make each step clear and simple
5. Break down ALL parts of the instruction

EXAMPLES:

Example 1:
Input: "Launch the calculator app and add 5 plus 3"
Output:
Launch the calculator application.

Click on the number 5.

Click the plus button.

Click on the number 3.

Click the equals button to get the result.

Example 2:
Input: "Open browser, go to google.com, search for 'python tutorial'"
Output:
Open the web browser.

Navigate to google.com.

Click on the search box.

Type python tutorial in the search field.

Press Enter or click the search button.

Example 3:
Input: "Fill out the form with name 'John Doe' and email 'john@company.com', then submit"
Output:
Locate the name field in the form.

Enter John Doe in the name field.

Click on the email field.

Enter john@company.com in the email field.

Click the submit button.

Now break down this instruction:
"""

def ensure_proper_formatting(text):
    """
    Ensures output follows the required format with empty lines between steps.
    """
    lines = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if line:  # Non-empty line
            lines.append(line)
            lines.append('')  # Add empty line after each step
    
    return '\n'.join(lines).strip()

def sanitise_instruction(text):
    """
    Sanitises the instruction text by removing quotation marks but preserving special characters.
    """
    # Remove quotation marks but preserve everything else
    text = text.replace('"', '').replace("'", "")
    
    # Don't remove special characters - they might be important for passwords, emails, etc.
    return text

def call_uitars_model(instruction):
    """
    Calls the UI-TARS model with the given instruction and system prompt.
    Returns the model's response.
    """
    API_URL = "http://10.0.0.6:8000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "ByteDance-Seed/UI-TARS-1.5-7B",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction}
        ],
        "temperature": 0.0,  
        "max_tokens": 2048
    }
    
    print("\n" + "="*60)
    print("DEBUG: PAYLOAD BEING SENT TO SERVER")
    print("="*60)
    print(json.dumps(payload, indent=2))
    print("="*60 + "\n")
    
    try:
        print("Calling UI-TARS model...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        print("Response received.")
        
        model_output = response.json()["choices"][0]["message"]["content"]
        
        print("\n" + "="*60)
        print("DEBUG: RAW MODEL OUTPUT (before sanitization)")
        print("="*60)
        print(repr(model_output))
        print("="*60 + "\n")
        
        return model_output
    except requests.exceptions.RequestException as e:
        print(f"Error calling UI-TARS model: {e}")
        return None

def save_output(original, new_instruction):
    """
    Saves the original and new instructions to a simple text file.
    Returns the path to the saved file.
    """
    output_file = "new_instruction.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_instruction)
    
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description="Generate new UI automation instructions using UI-TARS model.",
        epilog="Note: For instructions with special characters (like $, @, etc.), use --file argument instead of direct command line input to avoid shell interpretation issues."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("instruction", nargs="?", help="Instruction text to transform into new instructions (use --file for special characters)")
    group.add_argument("--file", help="Path to a file containing instructions (recommended for special characters)")
    parser.add_argument("--output", help="Path to save new instructions (default: new_instruction.txt)")

    args = parser.parse_args()
    
    # Get instruction from command line or file
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                instruction = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(2)  
    else:
        instruction = args.instruction

    # Validate instruction is not empty
    if not instruction or not instruction.strip():
        print("Error: Empty instruction provided.")
        sys.exit(2)  

    # Call model
    new_instruction = call_uitars_model(instruction)
    if not new_instruction:
        print("Failed to generate new instructions.")
        sys.exit(1) 

    new_instruction = sanitise_instruction(new_instruction)
    new_instruction = ensure_proper_formatting(new_instruction)
    
    # Save output
    if args.output:
        output_file = args.output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(new_instruction)
    else:
        output_file = save_output(instruction, new_instruction)
    
    print(f"\nNew instructions saved to: {output_file}")
    print("\nNew Instructions:")
    print("-" * 40)
    print(new_instruction)
    print("-" * 40)

if __name__ == "__main__":
    main()