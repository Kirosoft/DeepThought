import json
import logging
import urllib3
import requests
from colorama import init, Fore, Style

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

headers = {
    'Content-Type': 'application/json',
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

base_url = "http://localhost:7071/api"
#base_url = "https://deepthought-app.azurewebsites.net/api"

url = f"{base_url}/request_auth"
response = requests.get(url, headers=headers)
token = json.loads(response.content.decode('utf-8'))

headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }

azure_function_url = f"{base_url}/run_agent"

def call_azure_function(user_input):
    # Azure Function URL (replace with your actual function URL)
    
    # Prepare the request payload
    payload = json.dumps({"input": user_input, "role":"auto", "session_token":"test_session_token_must_be_16"}, ensure_ascii=False).encode('utf8')
    
    try:
        # Make a POST request to the Azure Function
        response = requests.post(azure_function_url, payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling Azure Function: {str(e)}"

def main():
    print(Fore.CYAN + Style.BRIGHT + "Welcome to the AI Assistant Console App!")
    print(Fore.YELLOW +  "Type 'exit' to quit the application.")
    
    while True:
        user_input = input(Fore.GREEN + "\nEnter your message: "+ Style.RESET_ALL)
        
        if user_input.lower() == 'exit':
            print("Thank you for using the AI Assistant. Goodbye!")
            break
        
        result = call_azure_function(user_input)
        print(f"AI Assistant: {result}")

if __name__ == "__main__":
    main()

