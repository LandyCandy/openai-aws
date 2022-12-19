import openai

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
    print(event)
    prompt = event['Body']

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

    return ('<?xml version=\"1.0\" encoding=\"UTF-8\"?>' +
           '<Response><Message><Body>' +
           prompt_response +
           '</Body></Message></Response>')