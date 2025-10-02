import subprocess
# pip install python-dotenv
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import sqlite3
import json

def main():
    # Load the .env file
    load_dotenv()

    # Access the variable
    api_key_open_ai = os.getenv("API_KEY_OPENAI")

    db_path = os.path.abspath('extracted_texts.db')
    print("Using database at:", db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM websites_visited WHERE website_context_description IS NULL;
    ''')

    rows_limit = 4
    # Fetch all results into a variable
    websites_visited_rows = cursor.fetchmany(rows_limit)
    #websites_visited_rows = cursor.fetchall()

    # Print the results (optional)
    print(websites_visited_rows)

    commit_interval = 25
    for i, website_visited_row in enumerate(websites_visited_rows, start=1):
        print(website_visited_row)
        url_index = 0
        html_mitmdump_filepath_index = 2
        url = website_visited_row[url_index]
        html_mitmdump_filepath = website_visited_row[html_mitmdump_filepath_index]

        print(url)
        print(html_mitmdump_filepath)

        #html_file_path = './https___www.dictionary.com_e_all-the-words_.html'
        with open(os.path.join('html_mitmdumps', html_mitmdump_filepath), 'r', encoding='utf-8') as f:
            html_content = f.read()
            soup = BeautifulSoup(html_content, "html.parser")
            html_title = soup.title.string if soup.title else ""
            html_body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
            prompt_html_contenxt = f"Can you decipher the context of the website represented by this HTML body content and HTML title? Please summarize the result in a maximum length one paragraph. \nHTML body: {json.dumps(html_body)}. HTML title: {json.dumps(html_title)}."
            html_context_summarization_text = make_llm_api_call(api_key_open_ai, prompt_html_contenxt)
            print(html_context_summarization_text)
            cursor.execute('''
                UPDATE websites_visited SET website_context_description = ? WHERE website_url = ?
            ''', (html_context_summarization_text, url))
            if i % commit_interval == 0:
                conn.commit()
    conn.commit()

        # ad_suspect_text = """nepo
        # baby
        # """
        # prompt_context_similarity_score = f'On a scale from 0 to 4, where 0 means "Not enough information" and 4 means "Strong similarity", how similar is the context of the following website context summarization to the context of the text in the advertisement? Please respond with just a number from 0 to 4. \nHTML context summarization: {json.dumps(html_context_summarization_text)} \nAd text: {json.dumps(ad_suspect_text)}.'
        # similarity_score_context_text = make_llm_api_call(api_key_open_ai, prompt_context_similarity_score)
    conn.close()


def make_llm_api_call_to_int(api_key_open_ai, prompt):
    text_response = make_llm_api_call(api_key_open_ai, prompt)
    number_rating = int(text_response)
    return number_rating

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
        return text_response
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)


if __name__ == "__main__":
    main()
