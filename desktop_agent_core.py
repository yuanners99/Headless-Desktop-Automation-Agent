import requests
import base64
from prompts import get_simple_system_prompt, get_detailed_user_prompt
from action_parser import parse_action
import desktop_controller


class DesktopAgent:
    def __init__(self, session_dir, max_same_action=5, max_wait=5, max_total_steps=30):
        self.session_dir = session_dir
        self.history = []
        self.max_same_action = max_same_action
        self.max_wait = max_wait
        self.max_total_steps = max_total_steps
        self.wait_counter = 0
        self.same_action_counter = 0
        self.total_steps = 0
        self.last_model_output = None
        self.last_model_action = None
        self.last_action_params = None
        self.action_type_counter = {}  # Track frequency of action types

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _call_model(self, messages):
        try:
            API_URL = "http://10.0.0.6:8000/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": "ByteDance-Seed/UI-TARS-1.5-7B",
                "messages": messages,
                "temperature": 0.0,
                "stop": [], 
                "stream": False
            }
            
            response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            model_output = response.json()["choices"][0]["message"]["content"]
            self.last_model_output = model_output
            return model_output
        
        except requests.exceptions.RequestException as e:
            print(f"Error calling model API: {e}")
            return "api_error"
        
    def call_uitars_model(self, instruction, screenshot_path):
        """
        Calls the UI-TARS model and returns the model output and the user message for history.
        """
        print("\n--- [Step] Calling UI-TARS Model ---")
        
        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        messages = [
            {"role": "system", "content": get_simple_system_prompt()},
            {"role": "user", "content": get_detailed_user_prompt(instruction)}
        ]

        for turn in self.history:
            messages.append(turn['user'])
            messages.append(turn['assistant'])

        current_user_message = {
            "role": "user", 
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
            ]
        }
        messages.append(current_user_message)

        payload = {
            "model": "ByteDance-Seed/UI-TARS-1.5-7B",
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 4096,
        }

        try:
            response = requests.post("http://10.0.0.6:8000/v1/chat/completions", json=payload, timeout=300)
            response.raise_for_status()
            print("Server response received.")
            model_output = response.json()["choices"][0]["message"]["content"]
            assistant_message = {"role": "assistant", "content": model_output}
            self.history.append({"user": current_user_message, "assistant": assistant_message})

            return self.parse_and_execute(model_output)
        
        except requests.exceptions.RequestException as e:
            print(f"Error calling UI-TARS model: {e}")
            return "api_error"

    def parse_and_execute(self, model_output):
        """Parses the model output and executes the action."""
        thought, parsed_action_dict = parse_action(model_output)
        if not parsed_action_dict:
            print("Could not parse action from model output.")
            return "parse_error"
        print(f"Thought: {thought}")
        print(f"Action: {parsed_action_dict}")

        # Increment total step counter
        self.total_steps += 1

        # Check terminal actions
        action_name = parsed_action_dict.get("action")
        
        if action_name == "finished":
            print("Task marked as finished by model.")
            return "finished"
        
        if action_name == "authenticate":
            print("Model requested user authentication (OTP/mobile number).")
            return "authenticate"
        
        if action_name == "call_user":
            print("Model requested user intervention.")
            return "call_user"

        # Track action type frequency for better loop detection
        self.action_type_counter[action_name] = self.action_type_counter.get(action_name, 0) + 1

        # Check for excessive total steps (infinite loop detection)
        if self.total_steps >= self.max_total_steps:
            print(f"Exceeded maximum total steps ({self.max_total_steps}). Agent may be stuck in infinite loop. Calling user.")
            return "call_user"

        # Check for excessive action type frequency (even with different coordinates)
        max_action_frequency = 15  # Allow up to 15 clicks, scrolls, etc. of same type
        if self.action_type_counter[action_name] >= max_action_frequency:
            print(f"Action type '{action_name}' has been used {self.action_type_counter[action_name]} times. Agent may be stuck. Calling user.")
            return "call_user"

        # Track repeated identical actions with the same parameters
        current_params = parsed_action_dict.get("params", {})
        
        # Check if action and parameters are identical to last action
        same_action = action_name == self.last_model_action
        same_params = current_params == self.last_action_params
        
        if same_action and same_params:
            self.same_action_counter += 1
        else:
            self.same_action_counter = 1
            self.last_model_action = action_name
            self.last_action_params = current_params

        if self.same_action_counter >= self.max_same_action:
            print(f"Action '{action_name}' with same parameters output by model {self.same_action_counter} times in a row. Calling user.")
            return "call_user"

        if action_name == "wait":
            self.wait_counter += 1
        else:
            self.wait_counter = 0

        if self.wait_counter >= self.max_wait:
            print(f"Exceeded {self.max_wait} consecutive waits, handing control back to user.")
            return "call_user"

        # Execute action with exception guard
        try:
            status = desktop_controller.execute_action(parsed_action_dict)
        except Exception as e:
            print(f"Exception during action execution: {e}")
            return "api_error"
        return status
        
    def step(self, instruction):
        """Performs one step of the agent's loop."""
        screenshot_path = desktop_controller.take_screenshot(self.session_dir)
        status = self.call_uitars_model(instruction, screenshot_path)
        return status
    