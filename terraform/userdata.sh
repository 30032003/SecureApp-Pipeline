#!/bin/bash

apt-get update -y

apt-get install -y docker.io git

systemctl start docker

systemctl enable docker

usermod -aG docker ubuntu

cd /home/ubuntu

git clone https://github.com/30032003/SecureApp-Pipeline.git

cd SecureApp-Pipeline

docker build -t secureapp .

docker run -d \
-p 5000:5000 \
--name secureapp \
secureapp