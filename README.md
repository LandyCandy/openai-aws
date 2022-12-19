Project to integrate OpenAI models with an AWS backed chatbot.

Helpful deployment doc here: https://aws.amazon.com/premiumsupport/knowledge-center/lambda-python-package-compatible/

Local Dev Instructions:
- `cd` into the lamdba functions subdirectory you want to deploy 
- Run the two pip commands below (in the order they are presented)
    -- NOTE: this is to install openApi and the lamdba compatible binaries for it's pandas dependency
- Run the deploy_lambda.sh script (assuming you already created the corresponding lamdba function in AWS)

Pip install on macOs for lib compatibility with lambda execution environment
```
pip install \               
    --target=./python/lib/python3.9/site-packages \
    --python 3.9 \
    --upgrade \
    openai
pip install \                    
    --platform manylinux2014_x86_64 \
    --target=./python/lib/python3.9/site-packages \
    --implementation cp \
    --python 3.9 \
    --only-binary=:all: --upgrade \
    pandas
```