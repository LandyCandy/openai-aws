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

    #get prompt from sender and hit openAPI with it
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

    #get twilio number this message was sent to
    twilio_number = event['To']

    #collect other message recipients in phonenumbers_in_received_messages list (in the From and OtherRecipientsN fields)

    #collect number of the query sender
    phonenumbers_in_received_message = [event['From']]

    #collect other message recipients
    OtherRecipientsN = 0
    while 'OtherRecipients' + str(OtherRecipientsN) in event:
        phonenumbers_in_received_message.add(event['OtherRecipients' + str(OtherRecipientsN)])
        OtherRecipientsN += 1

    #individual message template
    message_template = """
        <Message from="%s" to="%s">
            <Body>
                %s
            </Body>
        </Message>
    """ 

    #create list of outgoing messages as a single string
    outgoing_messages = ""
    for phonenumber_in_received_message in phonenumbers_in_received_message:
        outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

    return ("""
            <?xml version=\"1.0\" encoding=\"UTF-8\"?>
            <Response>
                %s
            </Response>
            """ % outgoing_messages)