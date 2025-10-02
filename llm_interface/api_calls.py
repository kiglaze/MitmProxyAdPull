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

    conn = sqlite3.connect('../extracted_texts.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM image_texts;
    ''')

    rows_limit = 10
    # Fetch all results into a variable
    results = cursor.fetchmany(rows_limit)

    # Print the results (optional)
    print(results)

    text_index = 2
    image_text_ad_rating_index = 3
    id_index = 0
    for result in results:
        result_text = result[text_index]
        image_text_ad_rating = result[image_text_ad_rating_index]
        id_value = result[id_index]
        print("-------------------")
        print(result_text)

        if image_text_ad_rating is None:
            # TODO (Iris -- addressed) try out different prompts. Not enough information for what (to make a decision)? Define ads? Define scale better.
            prompt = ('"How likely is it that the following text is from an advertisement? '
                      'Just respond with a number from 0 to 4, and use the following scale definition: '
                      '0 = Not enough information, 1 = Clearly not an advertisement, 2 = Low likelihood of being an advertisement, 3 = Moderate likelihood of being an advertisement, 4 = Strong likelihood of being an advertisement.'
                      'Text: %s"') % json.dumps(result_text)
            image_text_ad_rating = make_llm_api_call_to_int(api_key_open_ai, prompt)
            # Update the image_text_ad_rating for the row with the given id_value
            cursor.execute('''
                UPDATE image_texts
                SET image_text_ad_rating = ?
                WHERE id = ?
            ''', (image_text_ad_rating, id_value))




            # Commit the changes to the database
            conn.commit()

    # url = 'https://api.nytimes.com/svc/books/v3/lists/overview.json?api-key=' + api_key_nytimes
    # command = ['curl', url]


    cursor.execute('''
        SELECT * FROM image_texts it
        LEFT JOIN image_saved_data isd ON isd.full_filepath = it.full_filepath
        WHERE isd.source_url_rating IS NULL
    ''')
    results = cursor.fetchall()
    print(results)
    for result in results:
        id_index = 9
        id_img_saved_data = result[id_index]
        source_url_idx = 12
        source_url = result[source_url_idx]
        referrer_url_idx = 14
        referrer_url = result[referrer_url_idx]
        source_url_rating_prompt = (f'"How likely is it that the following source URL is from an advertisement server? '
                                    f'The main website URL is {json.dumps(referrer_url)}. '
                                    f'Just respond with a number from 0 to 4, and use the following scale definition: '
                                    f'0 = Not enough information, 1 = Clearly not from an ad server, 2 = Low likelihood of being from an ad server, 3 = Moderate likelihood of being from an ad server, 4 = Strong likelihood of being from an ad server.'
                                    f'Image source URL: {json.dumps(source_url)}"')
        source_url_rating = make_llm_api_call_to_int(api_key_open_ai, source_url_rating_prompt)
        print(source_url)
        print(source_url_rating)
        cursor.execute('''
            UPDATE image_saved_data
            SET source_url_rating = ?
            WHERE id = ?
        ''', (source_url_rating, id_img_saved_data))
        conn.commit()

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
