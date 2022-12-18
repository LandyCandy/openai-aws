#! /bin/bash

# Clean previous archive
rm -y open-ai-deployment-package.zip

# Navigate to libraries dir
cd dev-env/lib/python3.9/site-packages

# Zip libs into new archive
zip -r ../../../../open-ai-deployment-package.zip .

# Navigate up to source dir
cd ../../../../

# Zip lambda function file into archive
zip -g open-ai-deployment-package.zip lambda_function.py

# Upload to s3 location for automatic deployment to lambda
aws s3 cp open-ai-deployment-package.zip s3://myshitbucket/lambda_deployment_zips/open-ai-deployment-package.zip