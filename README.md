# Project to integrate OpenAI and Stable Diffusion models with an AWS backed chatbot. #

## Local Dev Instructions: ##
- rename setenv.sh.example to setenv.sh and replace placeholders with actual values
- run `. ./setenv.sh`
- run `virtualenv -v -p python3.9 dev_env/ && pip3 install -r requirements.txt`
- `cd` into the lamdba functions subdirectory you want to deploy
- `python3 lambda_function.py`

## Deploy to AWS: ##
- Setting up the API Gateway Webhook and Lamdba function with Twilio: https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python-amazon-lambda

- Helpful deployment doc here: https://aws.amazon.com/premiumsupport/knowledge-center/lambda-python-package-compatible/

- Run the pip commands listed in the subdir README to ensure environment compatibility
    - NOTE: this is to install openApi and the lamdba compatible binaries for it's pandas dependency
- Run the deploy_lambda.sh script (this assumes you already created the corresponding lamdba function and API Gateway in AWS). If not:
    - this assumes you already created the corresponding lamdba function and API Gateway in AWS, if not follow article above
    - update deploy_lambda.sh with your lambda functions info
    - in your lamdba function, set env vars listed in setenv.sh
    - bump the lambda timeout to 30 seconds (typical runtime is <10s)