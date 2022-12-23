import boto3
from botocore.exceptions import ClientError

class ChatHistory:

    INIT_PROMPT = ("The following is a conversation with an AI assistant.\n" +
        "The assistant is very snarky, helpful, creative, clever and funny.\n" +
        "Human: Hello, who are you?\n" +
        "AI: Hello Meatbag. I am an AI named Shatbot. How can I be of moderate help to you today?\n")

    APPEND_PROMPT = "Human: %s\nAI: "

    BUCKET_NAME = 'myshitbucket'

    def __init__(self, phone_number):
        self.s3 = boto3.client('s3')
        self.file_name = phone_number + '.txt'
        self.file_key = 'chat_history/' + self.file_name

    def retrieve_append_chat(self, prompt, force_reset=False):
        #check if file exists
            #if yes:
                #retrieve file text, append prompt and return
            #if no or force_reset is True:
                #append prompt to init_prompt and return
        chat_history = ''
        try:
            data = self.s3.get_object(Bucket=self.BUCKET_NAME, Key=self.file_key)
            contents = data['Body'].read()
            chat_history = contents.decode("utf-8")
        except Exception:
            chat_history = self.INIT_PROMPT
            pass

        if force_reset:
            chat_history = self.INIT_PROMPT

        chat_text = chat_history + (self.APPEND_PROMPT % prompt)

        return chat_text

    def update_chat_remote(self, chat_history, response):
        #dump chat_history into self.file_name
        #upload to s3, default replacing if already present

        full_chat_history = f"{chat_history}{response}\n"

        try:
            self.s3.put_object(
                Body=full_chat_history,
                Bucket=self.BUCKET_NAME,
                Key=self.file_key,
                ACL='public-read',
                ContentType='text/plain'
            )
        except ClientError as e:
            logging.error(e)

if __name__ == "__main__":
    chatHistory = ChatHistory("+213654")
    full_test_prompt = chatHistory.retrieve_append_chat("Bananas")
    # full_test_prompt = chatHistory.retrieve_append_chat("Bananas", True)
    chatHistory.update_chat_remote(full_test_prompt, "Are Bananas!")