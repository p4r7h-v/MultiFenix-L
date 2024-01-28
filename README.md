# MultiFenix-L(ong Context)

## Overview
MultiFenix-L is an Advanced AI Assistant capable of a wide range of tasks such as reading and writing files, creating directories, listing files, and much more. It is designed to carry out user instructions one step at a time until all steps are completed, after which it returns a confirmation message. Inspired by [EchoHive's AutoAGI](https://www.youtube.com/watch?v=zErt3Tp7srY) and [parth's FenixAGI](https://github.com/p4r7h-v/FenixAGI-MkIII) running a basic multi-agent system on GPT-4. This variant can use [Killian Lucas's Open Interpreter](https://github.com/KillianLucas/open-interpreter), and features a significantly longer context window, as it defaults to [GPT-4-0125-preview, also known as GPT-4-turbo](https://openai.com/blog/new-models-and-developer-products-announced-at-devday).
## Main Components
- **fenix_agi.py**: Entry point to the application. It provides an interface to interact with the user, manage user input and messages, and maintains the GPT session.

### fenix_agi_classes
- **functions.py**: Contains the definitions of the actions performed by the AI assistant.
- **function_definitions.py**: Maps function names to their actual implementations.
- **gpt_call.py**: Manages the interaction with OpenAI's GPT models.
- **message_manager.py**: Handles the management and storage of messages within a session.
- **user_input_manager.py**: Processes and handles user input.
- **voice_control.py**: Handles any voice interactions if they are part of this project.

## Usage
Fenix A.G.I operates using a chat-based user interface. As the user, you communicate with the assistant by inputting your directions in the form of chat messages.

### Available Tasks:
Fenix A.G.I is capable of performing a variety of tasks including but not limited to:
- Reading and writing files
- Creating directories
- Listing files in a directory
- Interacting with code interpreter
- Initiating multiple instances of Fenix A.G.I
- Utilizing swarm GPT for task completion

These tasks are initiated either by a direct request from you, or as a part of the process to fulfill a broader instruction.

### Open Interpreter:
Fenix A.G.I is capable of interacting with [Open Interpreter](https://github.com/KillianLucas/open-interpreter) to perform coding related tasks. This function is only activated if you (the user) specifically request it.

### Initiating Instances of Fenix A.G.I:
Fenix A.G.I can start new instances of itself on your request. This may be necessary for larger tasks where separate processes might be beneficial.

### Swarm GPT:
Fenix A.G.I can utilize Swarm GPT to complete a task. This function is only activated if you (the user) specifically request it.

This project is a WIP. Expect bugs.