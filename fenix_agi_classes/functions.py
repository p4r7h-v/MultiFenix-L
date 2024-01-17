import os
from interpreter import interpreter
import pyautogui
import time
from termcolor import colored
from swarmGPT import GPTSwarm, OpenAIApiCaller
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# Initialize the OpenAI client
client = OpenAI()

def get_current_time() -> str:
    """Returns the current date and time and present it "it is january 1st 2021 12:00:00 am" format"""
    return time.strftime("%c")

def move_file(file_path: str, new_file_path: str) -> str:
    """Moves a file from one location to another and returns a confirmation message"""
    os.rename(file_path, new_file_path)
    return f'File {file_path} was successfully moved to {new_file_path}. move on to the next step. stop if all steps are completed.'

def read_file(file_path: str) -> str:
    """Reads the contents of a file and returns it as a string"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f'contents of {file_path}:{f.read()}'

def write_file(file_path: str, content: str) -> str:
    """Writes the contents of a file and returns a confirmation message.
    Respond with a JSON-encoded string only.
    Return only plain strings without any control characters, such as newline ('\n') or tab ('\t').
    """
    abs_working_dir = os.path.abspath(os.getcwd())
    abs_file_path = os.path.abspath(file_path)
    if not abs_file_path.startswith(abs_working_dir):
            return 'Error: Invalid file path. Writing outside of working directory is not permitted.'
    with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    return f'File {file_path} was successfully written. move on to the next step. stop if all steps are completed. '

def append_file(file_path: str, content: str) -> str:
    """Appends content to the end of a file and returns a confirmation message"""
    with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    return f'Content was successfully appended to {file_path}. move on to the next step. stop if all steps are completed.'

def create_directory(dir_path: str) -> str:
    """Creates a directory and returns a confirmation message"""
    os.mkdir(dir_path)
    return f'Directory {dir_path} was successfully created. move on to the next step. stop if all steps are completed.'

def list_files(dir_path: str) -> str:
    """Lists the files in a directory and returns a confirmation message"""
    return f'Files in {dir_path}:\n' + '\n'.join(os.listdir(dir_path))

def code_interpreter(message: str) -> str:
    """Use this to start an instance of the python code interpreter with the task. You are prohibited from calling this unless the user asks for you to call this function specifically."""
    
    response = ""
    for chunk in interpreter.chat(message, display=True, stream=True):
        # Check if the chunk is of type 'message' and has 'content'
        if chunk.get('type') == 'message' and 'content' in chunk:
            message_content = chunk['content']
            response += message_content

    # reset the interpreter after each use
    interpreter.reset()
    return f'Code interpreter response is: {response}. Move on to the next step. Stop if all steps are completed.'

def start_fenix_agi(system_message: str) -> str:
    """Use this to start an instance of the fenix agi with the given system_message. System message is the first message that fenix will receive upon startup. If there is no system message then pass "None" as the system_message. ONLY USE THIS FUNCTION IF THE USER ASKS FOR IT.
    """
    # Open the command prompt with the desired command
    os.system("start cmd /k python fenix_agi.py")
    
    # Wait for a brief moment to ensure the script is ready to receive input
    time.sleep(8)  # Adjust this sleep duration as needed

    # Use pyautogui to type the input
    if not system_message == "None":
        pyautogui.write("multi")
        time.sleep(0.5)
        pyautogui.press('enter')
        pyautogui.write("You are Fenix. This session is for: "+system_message  + "\n" + "done")
        time.sleep(0.5)
        pyautogui.press('enter')
    return f'fenix_agi.py script for "{system_message[:30]}..." was successfully started. move on to the next step. stop if all steps are completed.'

def call_swarm(user_message: str) -> str:
    '''Use this only when user has asked you to utilize the swarm or swarm gpt to complete a task. You are prohibited from calling this unless the user asks for you to call this function specifically.'''
    print(colored("...INITIALIZING SWARM...", "red"))
    user_message = user_message
    gpt_api_caller = OpenAIApiCaller()
    swarm = GPTSwarm(user_message, gpt_api_caller)
    # exit()
    synthesized_response = swarm.generate_response()
    print(synthesized_response)
    return f'Swarm responds as: {synthesized_response}. move on to the next step. stop if all steps are completed.'

def bing_search_save(file_name, query):
    '''Use this only when user has asked you to utilize a web search engine to complete a task. You are prohibited from calling this unless the user asks for you to call this function specifically'''
    subscription_key = os.getenv("BING_SEARCH_KEY")
    base_url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query, "count": 50, "offset": 0, "freshness": "Month"}
    file_path = "./web_searches/"+file_name
    response = requests.get(base_url, headers=headers, params=params)
    # if 401, then return error
    if response.status_code == 401:
        return "Error: Invalid Bing Search Key"
    
    response.raise_for_status()
    search_results = response.json()

    folder_path = "."+os.path.dirname(file_path)

    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except OSError as e:
            return f"Error creating directory: {str(e)}"

    with open(file_path, 'w', encoding='utf-8') as file:

        if 'webPages' in search_results:
            for result in search_results["webPages"]["value"]:
                file.write(f"- [{result['name']}]({result['url']})\n")
        else:
            print("'webPages' not in search results")
    return f"Response saved to: {file_path}, {len(search_results['webPages']['value'])} results found. Content: {search_results['webPages']['value']}"

def scrape_website(url):
    """Scrape a website and return the data"""
    target_tag = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p')
    try:
        # Access the website
        response = requests.get(url)
        response.raise_for_status()

        # Fetch and parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all(target_tag)

        # Extract and print the data
        data = [tag.get_text() for tag in tags]
        return data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing the website: {e}")
        return None
