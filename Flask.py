from flask import Flask, jsonify, request
from openai import OpenAI
import os

client = OpenAI(api_key='')

app = Flask(__name__)

@app.route('/')
def hello_world():
    group = request.args.get('group')
    prompt = request.args.get('prompt')

    response = {
        "group": group,
        "prompt": prompt,
        "text": "Hello world, how are you ?"
    }
    prompt="tell me a story"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
            "content": prompt},
            {"role": "system", "content": ""},
        ]
    )
    response = completion.choices[0].message.content

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/call')
def call_openai():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt parameter is missing"}), 400

    file_name = "pma.txt"
    try:
        # Open and read from the text file
        with open(file_name, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        return jsonify({"error": f"File {file_name} not found"}), 404
    except IOError:
        return jsonify({"error": "An error occurred while reading the file"}), 500

    #r = file_content + 'How will you respond to this in less than 30 words: '
    r = file_content

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
            "content": prompt},
            {"role": "system", "content": r},
        ]
    )

    gpt_response = completion.choices[0].message.content
    response = {
        "group": "pma",
        "prompt": prompt,
        "text": gpt_response
    }

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/call_old')
def call_openai_old():
    group = str(request.args.get('group', ''))
    group = group.replace("\\", "").replace('"', '')
    if not group:
        return jsonify({"error": "Group parameter is missing"}), 400

    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt parameter is missing"}), 400

    memory = request.args.get('memory', 'no').lower()
    memory_content = ''
    file_memory = group + ".log"

    if memory == 'yes':
        try:
            # Open and read from the log file
            with open(file_memory, 'r') as file:
                memory_content = file.read()
        except FileNotFoundError:
            return jsonify({"error": f"File {file_memory} not found"}), 404
        except IOError:
            return jsonify({"error": "An error occurred while reading the file"}), 500
        file.close()

    p = memory_content.splitlines()
    digest = ''

    # Make sure to get the last 20 lines, or all lines if there are fewer than 20
    for i in p[-20:]:
        digest += i + os.linesep

    file_name = group + ".txt"

    try:
        # Open and read from the text file
        with open(file_name, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        return jsonify({"error": f"File {file_name} not found"}), 404
    except IOError:
        return jsonify({"error": "An error occurred while reading the file"}), 500

    #r = file_content + 'How will you respond to this in less than 30 words: '
    r = file_content

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
            "content": r + prompt},
            {"role": "system", "content": 'The past conversation was:'+ digest},
        ]
    )

    gpt_response = completion.choices[0].message.content

    response = {
        "group": group,
        "prompt": prompt,
        "text": gpt_response
    }

    lfile = open(file_memory, "a")
    n = lfile.write("user: "+ prompt+ '\n')
    n = lfile.write(group + ": " + str(response) + '\n')
    lfile.close()

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    app.run(debug=True)