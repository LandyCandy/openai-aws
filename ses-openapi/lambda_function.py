import os
import re
import json
import boto3
import email
import base64
import openai
from botocore.exceptions import ClientError

openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_KEY']

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

    client = boto3.client('ses',region_name="use-east-1")
    CONFIGURATION_SET = "gpt3-test"

    try:
    #Provide the contents of the email.
        response = client.send_raw_email(
            Source="Gpt3 ShatBot " + "<" + msg.get("To") + ">",
            Destinations=[
                msg.get("From")
            ],
            RawMessage={
                'Data':("From: Gpt3 ShatBot " + "<" + msg.get("To") + ">\n" +
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

if __name__ == "__main__":
    input_event = {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-stuff', 'Sns': {'Type': 'Notification', 'MessageId': 'numbers', 'TopicArn': 'arn:aws:sns:topic-details', 'Subject': 'Amazon SES Email Receipt Notification', 'Message': '{"notificationType":"Received","mail":{"timestamp":"2001-10-19T13:05:42.563Z","source":"stuff@place.com","messageId":"numbersletters","destination":["email@place.com"],"headersTruncated":false,"headers":[{"name":"Return-Path","value":"stuff@place.com"},{"name":"Received","value":"from info.place.com (info.place.com [12.34.56.789]) by inbound-smtp.region.amazonaws.com with SMTP id numberLetters for stuff@place.domain; Tue, 19 Jan 2001 16:15:42 +0000 (UTC)"},{"name":"X-SES-Spam-Verdict","value":"PASS"},{"name":"X-SES-Virus-Verdict","value":"PASS"},{"name":"Received-SPF","value":"pass (spfCheck: domain of place.com designates 12.34.56.789 as permitted sender) client-ip=12.34.56.789; envelope-from=stuff@place.com; helo=bleh;"},{"name":"Authentication-Results","value":"amazonses.com; spf=pass (spfCheck: domain of place.com designates 12.23.32.124 as permitted sender) client-ip=12.23.34.234; envelope-from=stuff@place.com; helo=bleh; dmarc=none header.from=place.com;"},{"name":"X-SES-RECEIPT","value":"stuff=="},{"name":"X-SES-DKIM-SIGNATURE","value":"a=rsa-sha256; q=dns/txt; b=stuff=; c=relaxed/simple; s=sdfadgasg; d=amazonses.com; t=asdgasg; v=1; bh=gs/a/sag=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;"},{"name":"Received","value":"from place.com (unknown [12.12.12.12]) by tsafasf.place.com (Postfix) with SMTP id asdgsgsda for <stuff@place.com>; Mon, 22 Jan 2002 18:16:13 +0000 (UTC)"},{"name":"From","value":"stuff@place.com"},{"name":"To","value":"stuff@place.com"},{"name":"Subject","value":""},{"name":"Message-ID","value":"<asf@-sadggh>"},{"name":"Date","value":"Mon, 18 Jul 2013 09:34:33 +0000"},{"name":"MIME-Version","value":"1.0"},{"name":"Content-Type","value":"multipart/mixed; type=\\"application/smil\\"; boundary=\\"__CONTENT_64564_PART_BOUNDARY__33243242__\\""}],"commonHeaders":{"returnPath":"stuff@place.com","from":["stuff@place.com"],"date":"Mon, 28 Jane 2002 18:22:14 +0000","to":["stuff@place.com"],"messageId":"<safd@-sag>","subject":""}},"receipt":{"timestamp":"2002-11-13T15:16:34.563Z","processingTimeMillis":782,"recipients":["stuff@place.com],"spamVerdict":{"status":"PASS"},"virusVerdict":{"status":"PASS"},"spfVerdict":{"status":"PASS"},"dkimVerdict":{"status":"GRAY"},"dmarcVerdict":{"status":"GRAY"},"action":{"type":"SNS","topicArn":"arn:aws:sns:region:acccount_num:some-stuff","encoding":"BASE64"}},"content":"+++"}', 'Timestamp': '2001-11-15T13:03:43.365Z', 'SignatureVersion': '1', 'Signature': '/+//+++++++==', 'SigningCertUrl': 'https://sns.region.amazonaws.com/SimpleNotificationService-.pem', 'UnsubscribeUrl': 'https://sns.regionamazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:region:acccount_num:some-stuff:skadjghlkasdg', 'MessageAttributes': {}}}]}
    print(lambda_handler(input_event, {}))