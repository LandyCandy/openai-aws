import os
import urllib
import openai
from stable_diffusion import generate_image

openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_KEY']

init_prompt = """The following is a conversation with an AI assistant.
    The assistant is helpful, creative, clever, funny and very snarky.
    Human: Hello, who are you?
    AI: Hello Meatbag. I am an AI name Shatbot. How can I be of moderate help to you today?
    Human: %s
    AI:
    """

#Because xml is real dumb
def escape(str_xml: str):
    str_xml = str_xml.replace("&", "&amp;")
    str_xml = str_xml.replace("<", "&lt;")
    str_xml = str_xml.replace(">", "&gt;")
    str_xml = str_xml.replace("\"", "&quot;")
    str_xml = str_xml.replace("'", "&apos;")
    return str_xml


def lambda_handler(event, context):
    #get twilio number this message was sent to
    twilio_number = urllib.parse.unquote(event['To'], encoding='utf-8', errors='replace')

    #collect other message recipients in phonenumbers_in_received_messages list (in the From and OtherRecipientsN fields)

    #collect number of the query sender
    phonenumbers_in_received_message = [urllib.parse.unquote(event['From'], encoding='utf-8', errors='replace')]

    #collect other message recipients
    OtherRecipientsN = 0
    while 'OtherRecipients' + str(OtherRecipientsN) in event:

        phonenumber_in_received_message = urllib.parse.unquote(
            event['OtherRecipients' + str(OtherRecipientsN)],
            encoding='utf-8', 
            errors='replace')

        phonenumbers_in_received_message.append(phonenumber_in_received_message)
        OtherRecipientsN += 1

    outgoing_messages = ""

    #get prompt from sender and hit openAPI with it
    prompt = urllib.parse.unquote(event['Body'], encoding='utf-8', errors='replace')

    try:

        if len(prompt) >= 7 and 'image:' in prompt[:6].lower():
            image_prompt = prompt[5:]

            image_response = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = escape(image_response['data'][0]['url'])

            #individual message template
            message_template = """
                <Message from="%s" to="%s">
                    <Media>%s</Media>
                </Message>
            """ 

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, image_url)
        elif len(prompt) >= 9 and 'diffuse:' in prompt[:8].lower():
            image_url = escape(generate_image(prompt))

            message_template = """
                <Message from="%s" to="%s">
                    <Media>%s</Media>
                </Message>
            """ 

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, image_url)

        elif len(prompt) >= 6 and 'code:' in prompt[:5].lower():
            response = openai.Completion.create(
                model="code-davinci-002",
                prompt=init_prompt % prompt,
                temperature=0,
                max_tokens=1000,
                top_p=0.1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                best_of=3,
                stop=["\nHuman:", "\nAI:"]
            )

            prompt_response = escape(response["choices"][0]["text"])

            #individual message template
            message_template = """
                <Message from="%s" to="%s">
                    <Body>%s</Body>
                </Message>
            """ 

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

        else:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=init_prompt % prompt,
                temperature=0.9,
                max_tokens=300,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                best_of=3,
                stop=["\nHuman:", "\nAI:"]
            )

            prompt_response = escape(response["choices"][0]["text"])

            #individual message template
            message_template = """
                <Message from="%s" to="%s">
                    <Body>%s</Body>
                </Message>
            """ 

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

    except Exception as err:
        message_template = """
            <Message from="%s" to="%s">
                <Body>%s</Body>
            </Message>
        """ 

        prompt_response = escape(repr(err))

        for phonenumber_in_received_message in phonenumbers_in_received_message:
            outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

    return ("""
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                %s
            </Response>
            """ % outgoing_messages)