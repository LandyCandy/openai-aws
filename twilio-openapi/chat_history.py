import json
import logging

import boto3
from botocore.exceptions import ClientError

class ChatHistory:

    INIT_PROMPT = [
        {"role": "system", "content": "You are a snarky, helpful, creative, clever and funny assistant."},
        {"role": "user", "content": "Hello, who are you?"},
        {"role": "assistant", "content": "Hello Meatbag. I am an AI named Shatbot. How can I be of moderate help to you today?"}
    ]

    APPEND_PROMPT = {"role": "user", "content": ""}

    BUCKET_NAME = 'myshitbucket'

    def __init__(self, phone_number):
        self.s3 = boto3.client('s3')
        self.file_name = phone_number + '.json'
        self.file_key = 'chat_history/' + self.file_name

    def retrieve_append_chat(self, prompt, force_reset=False):
        #check if file exists
            #if yes:
                #retrieve file text, append prompt and return
            #if no or force_reset is True:
                #append prompt to init_prompt and return
        chat_history = []
        try:
            data = self.s3.get_object(Bucket=self.BUCKET_NAME, Key=self.file_key)
            contents = json.loads(data['Body'].read())
            chat_history = contents
            # chat_history = contents.decode("utf-8")
        except Exception:
            chat_history = self.INIT_PROMPT
            pass

        if force_reset:
            chat_history = self.INIT_PROMPT

        chat_prompt = self.APPEND_PROMPT.copy()
        chat_prompt['content'] = prompt
        chat_history.append(chat_prompt)

        return chat_history

    def update_chat_remote(self, chat_history, response):
        #dump chat_history into self.file_name
        #upload to s3, default replacing if already present

        chat_history.append({"role": "assistant", "content": response})

        try:
            self.s3.put_object(
                Body=json.dumps(chat_history),
                Bucket=self.BUCKET_NAME,
                Key=self.file_key,
                ACL='public-read',
                ContentType='text/json'
            )
        except ClientError as e:
            logging.error(e)

if __name__ == "__main__":
    chatHistory = ChatHistory("+213654")
    full_test_prompt = chatHistory.retrieve_append_chat("Bananas")
    # full_test_prompt = chatHistory.retrieve_append_chat("Bananas", True)
    chatHistory.update_chat_remote(full_test_prompt, "Are Bananas!")