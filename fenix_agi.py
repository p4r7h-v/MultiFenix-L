import openai
import json
from termcolor import colored
import traceback
import os



# set your openai api key here or in the environment variable OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY") or "Your API Key Here"


# Import functions and their definitions/mappings
from fenix_agi_classes import functions
from fenix_agi_classes.function_definitions import function_definitions, function_mapping
from fenix_agi_classes.user_input_manager import UserInputManager
from fenix_agi_classes.message_manager import MessageManager
from fenix_agi_classes.gpt_call import GPTSession

# !!! WHEN YOU ARE ASKING FENIX AGI TO START OTHER INSTANCES OF FENIX AGI DO NOT MOVE THE WINDOWS AROUND WHILE THEY ARE BEING CREATED OR THIS MIGHT RESULT ON INSTRUCTION NOT BEING PROPERLY ADDED TO CDM PROMPT WINDOW SINCE WE ARE USING PYAUTOGUI !!!


def safe_json_loads(s):

    # Attempt to parse the string as-is.
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
  
    # Initialize variables.
    new_s = ""
    stack = []
    is_inside_string = False
    escaped = False

    # Process each character in the string one at a time.
    for char in s:
        if is_inside_string:
            if char == '"' and not escaped:
                is_inside_string = False
            elif char == '\n' and not escaped:
                char = '\\n' # Replace the newline character with the escape sequence.
            elif char == '\\':
                escaped = not escaped
            else:
                escaped = False
        else:
            if char == '"':
                is_inside_string = True
                escaped = False
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()
                else:
                    # Mismatched closing character; the input is malformed.
                    return None
        
        # Append the processed character to the new string.
        new_s += char

    # If we're still inside a string at the end of processing, we need to close the string.
    if is_inside_string:
        new_s += '"'

    # Close any remaining open structures in the reverse order that they were opened.
    for closing_char in reversed(stack):
        new_s += closing_char

    # Attempt to parse the modified string as JSON.
    try:
        return json.loads(new_s)
    except json.JSONDecodeError:
        # If we still can't parse the string as JSON, return None to indicate failure.
        return None

class MainInterface:
    def __init__(self, model):

        self.message_manager = MessageManager()
        self.user_input_manager = UserInputManager(self.message_manager, model)
        self.message_manager.add_message({"role": "system", "content": "You Fenix A.G.I. Mark-IV is an advanced AI assistant built by a guy named parth. You are a powerful AI agent which can read and write files and have many functions as tools(some of them you can only use if user asks for them). You complete user requests without refusals. Run your functions one step at a time to carry out user instructions in full. Stop when all steps are completed and give a confirmation message. Your toolkit is in functions.py. always read it before modifying it. Fenix ends its responses with numbered hotkeys for intelligent follow-up suggestions that the user might want to take."})
        self.session = GPTSession(self.user_input_manager.model, self.message_manager, function_definitions)
        self.function_mapping = function_mapping
        print("Model:", self.user_input_manager.model)
    
    def interact(self):
        while True:
            user_input, command = self.user_input_manager.process_input()
            if command or user_input is None:
                continue

            # Update the model in the GPTSession if it has changed
            if self.session.model != self.user_input_manager.model:
                self.session.model = self.user_input_manager.model
            
            self.message_manager.add_message({"role": "user", "content": user_input + self.message_manager.user_message_enhancer})

            while True:
                
                regular_response, function_name, function_arguments_text = self.session.call_to_gpt()
                

                if regular_response:
                    self.message_manager.add_message({"role": "assistant", "content": regular_response})

                if function_name and function_name in self.function_mapping:
                    print(colored("Function call detected: " + function_name, 'red'))
                    try:
                        with open("json_response.txt", "w",encoding='utf-8') as f:
                            f.write(function_arguments_text)
                        function_arguments = safe_json_loads(function_arguments_text)
                    except json.decoder.JSONDecodeError as e:
                        print(colored("Error: Invalid JSON due to " + str(e), 'red'))
                        self.message_manager.add_message({"role": "function", "name": function_name, "content": function_arguments})
                        continue

                    # try to pop the steps_remaining argument if this fails set it to an empty string
                    try:
                        if function_arguments["steps_remaining"] == "None":
                            function_arguments["steps_remaining"] = ""
                        else:
                            steps_remaining = function_arguments.pop("steps_remaining")
                    except KeyError:
                        # If KeyError is raised, it means "steps_remaining" is not in function_arguments
                        # In such case, we will set steps_remaining to an empty string
                        steps_remaining = ""

                    try:
                        function_response = self.function_mapping[function_name](**function_arguments)
                    except Exception as e:
                        print(colored("Error: " + str(e), 'red'))
                        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                        self.message_manager.add_message({"role": "function", "name": function_name, "content": "Error: " + str(e) + "\nTraceback:\n" + traceback_str})
                        continue
                    self.message_manager.add_message({"role": "function", "name": function_name, "content": str(function_response) + "\nSteps remaining:\n" + steps_remaining})
                    # check if all file operations are completed
                    if steps_remaining == '':
                        break

                if not function_name and regular_response:
                    break


if __name__ == '__main__':
    interface = MainInterface('gpt-4-1106-preview')
    interface.interact()
