import os
import re
import email
import openai
openai.organization = "org-Ba1ocqhhrAabsOlWfoo7zx0V"
openai.api_key = "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"

init_prompt = """The following is a conversation with an AI assistant.
    The assistant is helpful, creative, clever, and very friendly.
    Human: Hello, who are you?
    AI: I am an AI created by OpenAI. How can I help you today?
    Human: %s
    AI:
    """

def lambda_handler(event, context):
    prompt = "What should I do with my dog tomorrow?"

    message_body = json.loads(event["Records"][0]["Sns"]["Message"])
    decoded_body = base64.b64decode(message_body["content"])
    msg = email.message_from_bytes(decoded_body)

    prompt = re.compile("Content-Location: text_0.txt" + r"(.*?)--" + msg.get_boundary() + "--", re.S).findall(msg.as_string())[0]


    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=init_prompt % prompt,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=["\nHuman:", "\nAI:"]
    )

    print(response)