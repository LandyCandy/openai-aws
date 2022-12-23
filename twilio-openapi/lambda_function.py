import os
import urllib
import openai
from stable_diffusion import generate_image
from chat_history import ChatHistory

openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_KEY']

#Because xml is real dumb
def escape(str_xml: str):
    str_xml = str_xml.replace("&", "&amp;")
    str_xml = str_xml.replace("<", "&lt;")
    str_xml = str_xml.replace(">", "&gt;")
    str_xml = str_xml.replace("\"", "&quot;")
    str_xml = str_xml.replace("'", "&apos;")
    return str_xml

def keyword_check(prompt, keyword):
    return prompt.lower().startswith(keyword)


def lambda_handler(event, context):
    #get twilio number this message was sent to
    twilio_number = urllib.parse.unquote(event['To'], encoding='utf-8', errors='replace')

    #collect other message recipients in phonenumbers_in_received_messages list (in the From and OtherRecipientsN fields)

    #collect number of the query sender
    client_number = urllib.parse.unquote(event['From'], encoding='utf-8', errors='replace')
    phonenumbers_in_received_message = [client_number]

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
    prompt = prompt.replace('+', ' ')

    try:
        if keyword_check(prompt, 'image'):
            image_prompt = prompt[6:]

            image_response = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = escape(image_response['data'][0]['url'])

            #individual message template
            message_template = ('<Message from="%s" to="%s">\n' +
                                '<Media>%s</Media>\n' +
                                '</Message>')

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, image_url)
        elif keyword_check(prompt, 'diffuse'):
            image_prompt = prompt[8:]
            image_url = escape(generate_image(image_prompt, clip_flag=False))

            message_template = ('<Message from="%s" to="%s">\n' +
                                '<Media>%s</Media>\n' +
                                '</Message>')

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, image_url)

        elif keyword_check(prompt, 'diffuse-clip'):
            image_prompt = prompt[13:]
            image_url = escape(generate_image(image_prompt, clip_flag=True))

            message_template = ('<Message from="%s" to="%s">\n' +
                                '<Media>%s</Media>\n' +
                                '</Message>')

            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, image_url)


        elif keyword_check(prompt, 'code'):
            code_prompt = prompt[5:]
            response = openai.Completion.create(
                model="code-davinci-002",
                prompt=code_prompt,
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
            message_template = ('<Message from="%s" to="%s">\n' +
                                '<Body>%s</Body>\n' +
                                '</Message>')


            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

        else:
            chatHistory = ChatHistory(client_number)
            full_prompt = chatHistory.retrieve_append_chat(prompt)

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=full_prompt,
                temperature=0.9,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                best_of=3,
                stop=["\nHuman:", "\nAI:"]
            )

            prompt_response = escape(response["choices"][0]["text"])
            chatHistory.update_chat_remote(full_prompt, prompt_response)

            #individual message template
            message_template = ('<Message from="%s" to="%s">\n' +
                                '<Body>%s</Body>\n' +
                                '</Message>')


            #create list of outgoing messages as a single string
            for phonenumber_in_received_message in phonenumbers_in_received_message:
                outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

    except Exception as err:
        message_template = ('<Message from="%s" to="%s">\n' +
                            '<Body>%s</Body>\n' +
                            '</Message>')

        prompt_response = escape(repr(err))

        for phonenumber_in_received_message in phonenumbers_in_received_message:
            outgoing_messages += message_template % (twilio_number, phonenumber_in_received_message, prompt_response)

    return (('<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<Response>\n' +
            '%s\n' +
            '</Response>') % outgoing_messages)

if __name__ == "__main__":
    input_event = {
        'ToCountry': 'US',
        'ToState': 'CA',
        'SmsMessageSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'NumMedia': '0',
        'ToCity': '',
        'FromZip': '12345',
        'SmsSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'FromState': 'PA',
        'SmsStatus': 'received',
        'FromCity': 'ALLENSTOWN', 
        'Body': 'Testing+Twilio+2.0',
        'FromCountry': 'US',
        'To': '%2B12345678910',
        'ToZip': '',
        'NumSegments': '1',
        'ReferralNumMedia': '0',
        'MessageSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'AccountSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'From': '%2B10198765432',
        'ApiVersion': '2010-04-01'
    }
    print(lambda_handler(input_event, {}))
