import re

def _parse_action_string(action_str):
    """
    Parses a single action string like "click(start_box='(x,y)')" into a dictionary.
    """
    action_str = action_str.strip()
    
    match = re.match(r'(\w+)\((.*)\)', action_str)
    if not match:
        return None

    action_name, params_str = match.groups()
    params = {}

    if not params_str:
        return {"action": action_name, "params": {}}

    param_matches = re.finditer(r"(\w+)\s*=\s*'([^']*)'", params_str)
    
    for match in param_matches:
        key, value_str = match.groups()
        key = key.strip()
        
        if 'box' in key or 'point' in key:
            coord_match = re.search(r'\((\d+,\s*\d+)\)', value_str)
            if coord_match:
                coords = [int(c.strip()) for c in coord_match.group(1).split(',')]
                params[key] = coords
            else:
                 params[key] = None
        else:
            params[key] = value_str

    return {"action": action_name, "params": params}

def parse_action(model_output: str):
    """
    Parses the full output from the model to extract the thought and the action.
    Returns a tuple (thought, action_data).
    """
    thought = ""
    action_data = None

    thought_match = re.search(r'Thought:(.*?)(?=Action:|$)', model_output, re.DOTALL)
    if thought_match:
        thought = thought_match.group(1).strip()

    action_match = re.search(r'Action:(.*)', model_output, re.DOTALL)
    if action_match:
        action_str = action_match.group(1).strip()
        
        if action_str.startswith("```") and action_str.endswith("```"):
            action_str = action_str[3:-3].strip()
            
        action_data = _parse_action_string(action_str)
        
        if not action_data:
            if "wait()" in action_str:
                action_data = {"action": "wait", "params": {}}
            elif "finished()" in action_str:
                action_data = {"action": "finished", "params": {}}
            elif "authenticate()" in action_str:
                action_data = {"action": "authenticate", "params": {}}
            elif "call_user()" in action_str:
                action_data = {"action": "call_user", "params": {}}

    return thought, action_data 