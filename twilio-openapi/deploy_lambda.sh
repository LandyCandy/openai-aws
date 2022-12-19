#! /bin/bash

# Clean previous archive
rm -f openai-twilio-deployment-package.zip

# Navigate to libraries dir
cd ./python/lib/python3.9/site-packages

# Zip libs into new archive
zip -r ../../../../openai-twilio-deployment-package.zip .

# Navigate up to source dir
cd ../../../../

# Zip lambda function file into archive
zip -g openai-twilio-deployment-package.zip lambda_function.py

# Upload to s3 location for automatic deployment to lambda
aws s3 cp openai-twilio-deployment-package.zip s3://myshitbucket/lambda_deployment_zips/openai-twilio-deployment-package.zip

# Deploy code to lambda
aws lambda update-function-code --region us-east-1 --function-name openai-twilio --s3-bucket myshitbucket --s3-key lambda_deployment_zips/openai-twilio-deployment-package.zip