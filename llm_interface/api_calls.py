import subprocess
# pip install python-dotenv
from dotenv import load_dotenv
import os
import sqlite3
import json

def main():
    # Load the .env file
    load_dotenv()

    # Access the variable
    api_key_open_ai = os.getenv("API_KEY_OPENAI")
    api_key_nytimes = os.getenv("API_KEY_NYTIMES")

    conn = sqlite3.connect('../extracted_texts.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM image_texts;
    ''')

    # Fetch all results into a variable
    results = cursor.fetchmany(10)

    # Print the results (optional)
    print(results)

    text_index = 2
    for result in results:
        result_text = result[text_index]
        print("-------------------")
        print(result_text)
        # TODO try out different prompts. Not enough information for what (to make a decision)? Define ads? Define scale better.
        prompt = ('"On a scale of 1 (least likely) to 10 (most likely), how likely is it that the following text is from an advertisement? '
                  'Just respond with a number. If there is not enough information, answer with 0. Text: %s"') % json.dumps(result_text)
        make_llm_api_call(api_key_open_ai, prompt)


    # url = 'https://api.nytimes.com/svc/books/v3/lists/overview.json?api-key=' + api_key_nytimes
    # command = ['curl', url]

    # prompt = '"Tell me a three sentence bedtime story about a unicorn."'
    # make_llm_api_call(api_key_open_ai, prompt)


def make_llm_api_call(api_key_open_ai, prompt):
    url = 'https://api.openai.com/v1/responses'
    token = api_key_open_ai
    # prompt = '"Tell me a three sentence bedtime story about a unicorn."'
    payload = json.dumps({
        "model": "gpt-4.1",
        "input": prompt
    })
    command = [
        'curl',
        '-H', 'Content-Type: application/json',
        '-H', 'Authorization: Bearer ' + token,
        '-d', payload,
        url
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        #print(result.stdout)
        decoded_response = json.loads(result.stdout)
        text_response = decoded_response.get("output", {})[0].get("content", {})[0].get("text", "")
        print(text_response)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)


if __name__ == "__main__":
    main()
