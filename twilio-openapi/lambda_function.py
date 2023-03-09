import os
import urllib
import urllib.request
import openai
from twilio.rest import Client
from stable_diffusion import generate_image
from chat_history import ChatHistory

openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_KEY']
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']

def keyword_check(prompt, keyword):
    return (prompt + ":").lower().startswith(keyword)


def lambda_handler(event, context):
    #get twilio number this message was sent to
    twilio_number = urllib.parse.unquote(event['To'], encoding='utf-8', errors='replace')

    #collect other message recipients in phonenumbers_in_received_messages list (in the From and OtherRecipientsN fields)

    #collect number of the query sender
    client_number = urllib.parse.unquote(event['From'], encoding='utf-8', errors='replace')

    #Twilio Client
    client = Client(twilio_account_sid, twilio_auth_token)

    #get prompt from sender and hit openAPI with it
    prompt = urllib.parse.unquote(event['Body'], encoding='utf-8', errors='replace')
    prompt = prompt.replace('+', ' ')

    try:
        if keyword_check(prompt, 'image') or keyword_check(prompt, 'dall-e') or keyword_check(prompt, 'dali'):
            image_prompt = prompt.split(':', 1)[1]


            image_response = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response['data'][0]['url']
            
            #Call to ensure openAi image is available
            print(urllib.request.urlopen(image_url).status)

            message = client.messages.create(
                            from_=twilio_number,
                            media_url=image_url,
                            to=client_number
                        )
        
        elif keyword_check(prompt, 'diffuse'):
            image_prompt = prompt.split(':', 1)[1]
            image_url = generate_image(image_prompt, clip_flag=False)

            message = client.messages.create(
                            from_=twilio_number,
                            media_url=image_url,
                            to=client_number
                        )
            
        elif keyword_check(prompt, 'diffuse-clip'):
            image_prompt = prompt.split(':', 1)[1]
            image_url = generate_image(image_prompt, clip_flag=True)

            message = client.messages.create(
                            from_=twilio_number,
                            media_url=image_url,
                            to=client_number
                        )

        elif keyword_check(prompt, 'code'):
            code_prompt = prompt.split(':', 1)[1]
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

            prompt_response = response["choices"][0]["text"]

            message = client.messages.create(
                            from_=twilio_number,
                            body=prompt_response,
                            to=client_number
                        )

        else:
            chatHistory = ChatHistory(client_number)
            full_prompt = chatHistory.retrieve_append_chat(prompt)

            if len(full_prompt) > 10:
                final_prompt = full_prompt[:3] + full_prompt[-7:]
            else:
                final_prompt = full_prompt

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=final_prompt
            )

            prompt_response = response["choices"][0]["message"]["content"]
            chatHistory.update_chat_remote(full_prompt, prompt_response)

            message = client.messages.create(
                            from_=twilio_number,
                            body=prompt_response,
                            to=client_number
                        )

    except Exception as err:
        prompt_response = repr(err)
        message = client.messages.create(
                from_=twilio_number,
                body=prompt_response,
                to=client_number
            )

    print(message.sid)

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
        'Body': "Is there a term or concept for when your company chronically wastes everyone's time with long meetings where one person speaks and thirty people are expected to listen but of course do not?",
        'FromCountry': 'US',
        'To': os.environ['TWILIO_NUMBER'],
        'ToZip': '',
        'NumSegments': '1',
        'ReferralNumMedia': '0',
        'MessageSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'AccountSid': 'SMs0meR4nd0mnumb3rs4ndL3tt3r5',
        'From': os.environ['TEST_NUMBER'],
        'ApiVersion': '2010-04-01'
    }
    lambda_handler(input_event, {})
