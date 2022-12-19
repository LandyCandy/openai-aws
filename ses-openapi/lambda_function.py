import os
import re
import json
import boto3
import email
import base64
import openai
from botocore.exceptions import ClientError

openai.organization = "org-Ba1ocqhhrAabsOlWfoo7zx0V"
openai.api_key = "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"

init_prompt = """The following is a conversation with an AI assistant.
    The assistant is helpful, creative, clever, friendly, funny and very snarky.
    Human: Hello, who are you?
    AI: I am an AI created by OpenAI. How can I help you today?
    Human: %s
    AI:
    """

def lambda_handler(event, context):
    message_body = json.loads(event["Records"][0]["Sns"]["Message"])
    decoded_body = base64.b64decode(message_body["content"])
    msg = email.message_from_bytes(decoded_body)
    print(msg)

    regex_sms = re.compile("Content-Location: text_0.txt" + r"(.*?)--" + msg.get_boundary() + "--", re.S)
    regex_email = re.compile('Content-Type: text/plain; charset="UTF-8"' +  r"(.*?)--" + msg.get_boundary(), re.S)

    prompt_arr = regex_sms.findall(msg.as_string())

    prompt = prompt_arr[0] if len(prompt_arr) > 0 else regex_email.findall(msg.as_string())

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=init_prompt % prompt,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=["\nHuman:", "\nAI:"]
    )

    prompt_response = response["choices"][0]["text"]
    print(prompt)
    print(prompt_response)

    client = boto3.client('ses',region_name="us-east-1")
    CONFIGURATION_SET = "gpt3-test"

    try:
    #Provide the contents of the email.
        response = client.send_raw_email(
            Source="Gpt3 " + "<" + msg.get("To") + ">",
            Destinations=[
                # msg.get("From"),
                "landyrich117@gmail.com"
            ],
            RawMessage={
                'Data':("From: Gpt3 ShatBot <gpt3-test@landycandy.limited> \n" +
                    "To: " + msg.get("From") + "\n" +
                    "In-Reply-To: " + msg.get("Message-ID") + "\n" +
                    "References: " + msg.get("Message-ID") + "\n" +
                    "Subject: Re: " + msg.get("Subject") + "\n" +
                    "Content-Type: text/plain; boundary=\"000000000000ef819e05ed23e402\" \n\n" +
                    prompt_response),
            },
            ConfigurationSetName=CONFIGURATION_SET
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])