#!/bin/bash
# rc-update add docker boot

source .env

# sudo aws ecr get-login-password --region $AWS_DEFAULT_REGION 

# docker login --username aw --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

docker build -t awsrc .

docker tag awsrc:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/awsrc:latest

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/awsrc:latest
