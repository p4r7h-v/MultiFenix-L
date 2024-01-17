from termcolor import colored
import json
from fenix_agi_classes.voice_control import record_audio

class UserInputManager:
    def __init__(self, message_manager,multi_line_mode=False, model='gpt-4-1106-preview',voice_mode=False):
        self.message_manager = message_manager
        self.multi_line_mode = False
        self.model = model
        self.voice_mode = False

    def show_help(self):
        help_message = """
        Available commands:
        - reset: Reset session messages.
        - multi: Switch to multi-line input mode or back to regular input mode.
        - help: Display this help message.
        - change to gpt-3.5.turbo-16k: Switch to gpt-3.5.turbo-16k model.
        - change to gpt-4: Switch to gpt-4 model.
        - add system message: Add a new system message to the current place in the conversation.
        - remove system message: Remove the last system message.
        - voice: Start voice control mode.
        """
        print(colored(help_message, 'yellow'))

    def get_input(self, system_message=False):
        if self.voice_mode:
            while True:  # Loop for continuous voice input
                print("Voice control mode active. Say 'cancel voice control' to exit.")
                transcript = record_audio()

                # Process voice commands
                if 'cancel voice control' in transcript.lower():
                    self.voice_mode = False
                    print(colored("Exiting voice control mode.", 'red'))
                    return None  # Exit voice mode

                # Handle regular voice input
                user_input = transcript
                if user_input:
                    return user_input
            
        if self.multi_line_mode:
            lines = []
            if not system_message:
                print(colored("Enter your multi-line input. Type 'done' on a new line to finish. Type 'multi input' to switch back to regular input.", 'magenta'))
            while True:
                line = input()
                if line.strip().lower() == 'done':
                    break
                if line.strip().lower() == 'multi':
                    self.multi_line_mode = False  # switch back to regular input mode
                    return None  # signal that we're switching modes
                if line.strip().lower() in ['reset', 'help']:
                    user_input = line.strip().lower()
                    return user_input
                lines.append(line)
            return '\n'.join(lines)
        else:
            return input(colored("> ", 'magenta'))

    def process_input(self):
        user_input = self.get_input()
        
        if user_input is None:
            return None, True

        if user_input == 'reset':
            print(colored("Resetting session messages...", 'red'))
            self.message_manager.reset_messages()
            return None, True
        elif user_input == 'multi':
            self.multi_line_mode = True
            return None, True
        elif user_input == 'help':
            self.show_help()
            return None, True
        elif user_input.lower() == 'switch':
            if self.model == 'gpt-4-1106-preview':
                self.model = 'gpt-3.5-turbo-16k'
                print(colored("Model changed to gpt-3.5-turbo-16k", 'green'))
            else:
                self.model = 'gpt-4-1106-preview'
                print(colored("Model changed to gpt-4-1106-preview", 'green'))
            return None, True
        elif user_input == 'add system message':
            print(colored("Enter your multi-line system message. Type 'done' on a new line to finish.", 'magenta'))
            self.multi_line_mode = True
            system_message = self.get_input(system_message=True)
            self.multi_line_mode = False
            self.message_manager.add_message({"role": "system", "content": system_message})

            print(colored("System message added.", 'green'))
            return None, True
        elif user_input == 'remove system message':
            # remobve the last system message
            for i in range(len(self.message_manager.messages) - 1, -1, -1):
                if self.message_manager.messages[i]['role'] == 'system':
                    self.message_manager.messages.pop(i)
                    # remove the last system message from the messages.json
                    with open('messages.json', 'r') as json_file:
                        data = json.load(json_file)
                    data.pop(i)
                    with open('messages.json', 'w') as json_file:
                        json.dump(data, json_file)
                    break
            print(colored("Last system message removed.", 'green'))
            return None, True
        
        elif user_input.lower() == 'voice':
            self.voice_mode = True
            print("Voice control mode activated.")
            transcript = record_audio()
            if 'cancel voice control' in transcript.lower():
                self.voice_mode = False
                return None, True
            user_input = transcript

        elif self.multi_line_mode:
            self.multi_line_mode = False

        return user_input, False
