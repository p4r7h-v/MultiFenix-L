import json
import os
import tiktoken

class MessageManager:
    
    def __init__(self):
        if os.path.exists('messages.json'):
            os.remove('messages.json')
        self.messages = []
        
        self.user_message_enhancer = ""
        self.total_tokens = 0
        self.debug = False

    def count_tokens(self, text):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        text = str(text)
        return len(encoding.encode(text))


    def load_messages_from_file(self, filename='messages.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                self.messages = json.load(json_file)

    def write_message_to_file(self, message, filename='messages.json'):
        if not self.debug:
            pure_message = message.copy()
            pure_message['content'] = pure_message['content'].replace(self.user_message_enhancer, '')
        if not os.path.exists(filename):
            with open(filename, 'w') as json_file:
                json.dump([], json_file, indent=4)
        
        with open(filename, 'r') as json_file:
            data = json.load(json_file)

        data.append(pure_message if not self.debug else message)

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def add_message(self, message, token_limit=100000):
        while self.total_tokens + self.count_tokens(message['content']) > token_limit:
            if self.messages != []:
                removed_message = self.messages.pop(0)
                print(f"Removed message: {removed_message['content']}")
            else:
                print("No messages to remove.")
            self.total_tokens -= self.count_tokens(removed_message['content'])
            print(f"Dropped message due to token limit.")  # print dropped message

        self.messages.append(message)
        self.total_tokens += self.count_tokens(message['content'])
        print(f"Total tokens after adding message: {self.total_tokens}")  # print token count
        
        self.write_message_to_file(message)

    def reset_messages(self):
        self.messages = []
        self.total_tokens = 0
        if os.path.exists('messages.json'):
            os.remove('messages.json')


