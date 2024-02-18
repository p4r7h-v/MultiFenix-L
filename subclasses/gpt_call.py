import openai
from termcolor import colored
import time
import json
import tiktoken

class GPTSession:
    def __init__(self, model, message_manager, function_definitions, stream=True):
        self.model = model
        self.stream = stream
        self.message_manager = message_manager
        self.function_definitions = function_definitions
        self.client = openai.OpenAI()

    def log_response(self, response, input_size):
        # Calculate response size
        response_size = len(response)

        # Construct a log entry with timestamp, input size, response size, and response content
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "input_size": input_size,
            "response_size": response_size,
            "response": response  # Assuming response is already in a serializable format
        }
        
        # Append the log entry to the JSON log file
        log_file_path = "gpt_response_log.json"
        
        try:
            with open(log_file_path, "r") as file:
                log_data = json.load(file)
        except FileNotFoundError:
            log_data = []
        
        log_data.append(log_entry)
        
        with open(log_file_path, "w") as file:
            json.dump(log_data, file, indent=4)

    def call_to_gpt(self):
        input_tokens = sum(len(tiktoken.encoding_for_model(self.model).encode(str(message))) for message in self.message_manager.messages)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.message_manager.messages,
            stream=self.stream,
            functions=self.function_definitions,
            function_call="auto"
        )

        function_name = None
        function_argument_text = ''
        regular_response_text = ''

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(colored(chunk.choices[0].delta.content, 'green'), end='', flush=True)
                regular_response_text += chunk.choices[0].delta.content

            if chunk.choices[0].delta.function_call is not None:
                if chunk.choices[0].delta.function_call.name is not None:
                    function_name = chunk.choices[0].delta.function_call.name
                if chunk.choices[0].delta.function_call.arguments is not None:
                    function_argument_text += chunk.choices[0].delta.function_call.arguments

        print()
        # Log the response with the input size
        response_tokens = sum(tiktoken.encoding_for_model(self.model).encode(chunk.choices[0].delta.content) for chunk in response if chunk.choices[0].delta.content)
        
        self.log_response(regular_response_text, input_tokens)
        return regular_response_text, function_name, function_argument_text
