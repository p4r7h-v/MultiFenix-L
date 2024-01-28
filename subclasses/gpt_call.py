import openai
from termcolor import colored

class GPTSession:
    def __init__(self, model, message_manager, function_definitions, stream=True):
        self.model = model
        self.stream = stream
        self.message_manager = message_manager
        self.function_definitions = function_definitions
        self.client = openai.OpenAI()

    def call_to_gpt(self):
        response = self.client.chat.completions.create(
            model = self.model,
            messages = self.message_manager.messages,
            stream = self.stream,
            functions = self.function_definitions,
            function_call = "auto"
        )

        function_name = None
        function_argument_text = ''
        regular_response_text = ''


        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(colored(chunk.choices[0].delta.content, 'green'), end='', flush=True)
                regular_response_text += chunk.choices[0].delta.content
        

             # Check if function_call exists before accessing its attributes
            if chunk.choices[0].delta.function_call is not None:
                if chunk.choices[0].delta.function_call.name is not None:
                    print(colored(chunk.choices[0].delta.function_call.name, 'yellow'), end='', flush=True)
                    function_name = chunk.choices[0].delta.function_call.name
                if chunk.choices[0].delta.function_call.arguments is not None:
                    function_argument_text += chunk.choices[0].delta.function_call.arguments
                    print(colored(chunk.choices[0].delta.function_call.arguments, 'yellow'), end='', flush=True)

        print()

        return regular_response_text, function_name, function_argument_text
