import json
from flask import Flask, request, render_template
import requests
from dotenv import load_dotenv
import os
import re

load_dotenv()  # Load environment variables from the .env file

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        gender = request.form.get('gender', '')  # Optional
        age = request.form.get('age', '')  # Optional
        weight = request.form.get('weight', '')  # Optional
        
        # Call the ChatGPT API with user_input and optional criteria
        eating_program = generate_eating_program(user_input, gender, age, weight)
        return render_template('result.html', program=eating_program)
    return render_template('index.html')

import re

def generate_eating_program(user_input, gender='', age='', weight=''):
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('GPT_MODEL')  # Load model from .env
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    example_input = """
    Örnek format:
    {
        "gun": "Pazartesi",
        "kahvalti": ["besin", "besin", "besin"],
        "ara_ogun": ["besin", "besin"],
        "ogun": ["besin", "besin", "besin"],
        "aksam": ["besin", "besin"]
    }
    "Bu program ile ... (Özet, kişiye özel bir cümle. Herkese o kişinin özelliklerine göre farklı bir cümle kur.)"
    """

    prompt = (
        f'Bir hafta boyunca uygulanacak sağlıklı bir beslenme programı hazırla. "{user_input}" diye şikayet eden birine uygun olmalı. '
        f'Programı sadece JSON formatında döndür ve sonunda çok kısa kişiye özel bir yorum ekle. Yanıtın tamamen Türkçe olmalı. Örnek format:\n{example_input}'
    )

    if gender:
        prompt += f' Cinsiyet: {gender}.'
    if age:
        prompt += f' Yaş: {age}.'
    if weight:
        prompt += f' Kilo: {weight} kg.'

    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 1500,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    print("RAW RESPONSE:", response.text)

    if response.status_code != 200:
        return {'error': f"Error: {response.status_code}, {response.text}"}

    try:
        # Extract the content from the response
        program_json = response.json()['choices'][0]['message']['content']

        # Remove leading and trailing triple backticks if they exist
        if program_json.startswith("```json"):
            program_json = program_json[7:]  # Remove ```json
        if program_json.endswith("```"):
            program_json = program_json[:-3]  # Remove ```

        # Separate the JSON and the comment
        json_part = program_json[:program_json.rfind(']') + 1]
        comment_part = program_json[program_json.rfind(']') + 1:].strip()

        # Log the cleaned-up response for debugging
        print("CLEANED RESPONSE:", json_part)
        print("COMMENT:", comment_part)

        # Parse the JSON string into a Python list
        program_list = json.loads(json_part)

        # Wrap the list in a dictionary and add the comment
        eating_program = {
            'program': program_list,
            'comment': comment_part
        }

        return eating_program
    except (KeyError, json.JSONDecodeError) as e:
        return {'error': f"Failed to parse response: {str(e)}. Response: {program_json}"}

if __name__ == '__main__':
    app.run(debug=True)
