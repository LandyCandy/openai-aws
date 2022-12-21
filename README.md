Project to integrate OpenAI models with an AWS backed chatbot.

Helpful deployment doc here: https://aws.amazon.com/premiumsupport/knowledge-center/lambda-python-package-compatible/

Local Dev Instructions:
- `cd` into the lamdba functions subdirectory you want to deploy 
- Run the pip commands to ensure environment compatibility (covered in each subdir README)
    -- NOTE: this is to install openApi and the lamdba compatible binaries for it's pandas dependency
- Run the deploy_lambda.sh script (assuming you already created the corresponding lamdba function in AWS)