import subprocess
# pip install python-dotenv
from dotenv import load_dotenv
import os

def main():
    # Load the .env file
    load_dotenv()

    # Access the variable
    api_key_open_ai = os.getenv("API_KEY_OPENAI")
    api_key_nytimes = os.getenv("API_KEY_NYTIMES")

    # url = 'https://api.nytimes.com/svc/books/v3/lists/overview.json?api-key=' + api_key_nytimes
    # command = ['curl', url]

    url = 'https://api.openai.com/v1/responses'
    token = api_key_open_ai
    #prompt = '"Tell me a three sentence bedtime story about a unicorn."'
    prompt = '"Tell me a three sentence bedtime story about a unicorn."'

    command = [
        'curl',
        '-H', 'Content-Type: application/json',
        '-H', 'Authorization: Bearer ' + token,
        '-d', ('{"model": "gpt-4.1", "input": %s}' % prompt),
        url
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Success:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

if __name__ == "__main__":
    main()
