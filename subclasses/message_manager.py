import json
import os
import tiktoken

class MessageManager:
    
    def __init__(self):
        self.messages = []
        self.user_message_enhancer = ""
        self.total_tokens = 0
        self.debug = False
        # Ensure the old messages file is removed at the start for a clean state
        self._reset_messages_file()

    def count_tokens(self, text):
        encoding = tiktoken.encoding_for_model("gpt-4")
        text = str(text)
        return len(encoding.encode(text))

    def _reset_messages_file(self, filename='messages.json'):
        if os.path.exists(filename):
            os.remove(filename)

    def load_messages_from_file(self, filename='messages.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                self.messages = json.load(json_file)

    def write_message_to_file(self, message, filename='messages.json'):
        pure_message = message.copy() if not self.debug else message
        if not self.debug:
            pure_message['content'] = pure_message['content'].replace(self.user_message_enhancer, '')
        if not os.path.exists(filename):
            with open(filename, 'w') as json_file:
                json.dump([], json_file, indent=4)
        
        with open(filename, 'r+') as json_file:
            data = json.load(json_file)
            data.append(pure_message)
            json_file.seek(0)
            json.dump(data, json_file, indent=4)

    def add_message(self, message, token_limit=100000):
        message_tokens = self.count_tokens(message['content'])
        # Check if a single message exceeds the token limit
        if message_tokens > token_limit:
            raise ValueError("Single message exceeds the token limit. Cannot add to messages.")

        # Remove enough messages to fit the new message if necessary
        while self.total_tokens + message_tokens > token_limit:
            if not self.messages:
                print("Token limit exceeded and no messages to remove. Please increase the token limit.")
                return
            removed_message = self.messages.pop(0)
            removed_tokens = self.count_tokens(removed_message['content'])
            self.total_tokens -= removed_tokens
            print(f"Removed message due to token limit: {removed_message['content']}")

        self.messages.append(message)
        self.total_tokens += message_tokens
        self.write_message_to_file(message)
        #print(f"Total tokens after adding message: {self.total_tokens}")

    def reset_messages(self):
        self.messages = []
        self.total_tokens = 0
        self._reset_messages_file()
