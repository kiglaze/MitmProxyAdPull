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

    # Fetch all results into a variable
    websites_visited_rows = cursor.fetchall()
    #rows_limit = 40
    #websites_visited_rows = cursor.fetchmany(rows_limit)

    commit_interval = 25
    for i, website_visited_row in enumerate(websites_visited_rows, start=1):
        url_index = 0
        html_mitmdump_filepath_index = 2
        url = website_visited_row[url_index]
        html_mitmdump_filepath = website_visited_row[html_mitmdump_filepath_index]

        if html_mitmdump_filepath != None:
            #html_file_path = './https___www.dictionary.com_e_all-the-words_.html'
            with open(os.path.join('html_mitmdumps', html_mitmdump_filepath), 'r', encoding='utf-8') as f:
                html_content = f.read()
                soup = BeautifulSoup(html_content, "html.parser")
                html_title = soup.title.string if soup.title else ""
                html_body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
                prompt_html_contenxt = f"Can you decipher the context of the website represented by this HTML body content and HTML title? Please summarize the result in a maximum length one paragraph. \nHTML body: {json.dumps(html_body)}. HTML title: {json.dumps(html_title)}."
                html_context_summarization_text = make_llm_api_call(api_key_open_ai, prompt_html_contenxt)
                cursor.execute('''
                    UPDATE websites_visited SET website_context_description = ? WHERE website_url = ?
                ''', (html_context_summarization_text, url))
                if i % commit_interval == 0:
                    conn.commit()
    conn.commit()


    # Now comparing image text with website context
    cursor.execute('''
    SELECT
        it.id AS image_text_id,
        it.full_filepath,
        it.text,
        it.context_match_rating,
        wv.website_url,
        wv.website_context_description
    FROM image_texts it
    LEFT JOIN image_saved_data isd ON isd.full_filepath = it.full_filepath
    LEFT JOIN websites_visited wv ON wv.website_url = isd.referrer_url
    WHERE it.context_match_rating IS NULL AND wv.website_context_description IS NOT NULL;
    ''')


    # Fetch all results into a variable
    image_text_website_context_rows = cursor.fetchall()
    # rows_limit = 4
    # image_text_website_context_rows = cursor.fetchmany(rows_limit)
    commit_interval = 25
    for i, image_text_website_context_row in enumerate(image_text_website_context_rows, start=1):
        # image_text_index = 2; website_context_index = 5; image_text_id_index = 0
        image_text_id, _, image_text, _, _, website_context_description = image_text_website_context_row
        prompt_context_similarity_score = f'On a scale from 0 to 4, where 0 means "Not enough information" and 4 means "Strong similarity", how similar is the context of the following website context summarization to the context of the text in the image? Please respond with just a number from 0 to 4. \nHTML context summarization: {json.dumps(website_context_description)} \nImage text: {json.dumps(image_text)}.'
        context_match_rating = make_llm_api_call_to_int(api_key_open_ai, prompt_context_similarity_score)
        print(f"Context match rating: {context_match_rating}")

        cursor.execute('''
            UPDATE image_texts SET context_match_rating = ? WHERE id = ?
        ''', (context_match_rating, image_text_id))

        if i % commit_interval == 0:
            conn.commit()

    conn.commit()
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
        decoded_response = json.loads(result.stdout)
        text_response = decoded_response.get("output", {})[0].get("content", {})[0].get("text", "")
        return text_response
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

if __name__ == "__main__":
    main()
