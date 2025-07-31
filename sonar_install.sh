#!/bin/bash

# This script will install Sonarqube required packages on Amazon Linux 2

# Step 1: Update the System
echo "Updating the system..."
sudo yum update -y
# Step 2: Install Java (Required for Jenkins)
echo "Installing Java 17 (Amazon Corretto)..."
sudo yum install java-17-amazon-corretto -y
# Step 3: Verify Java Installation
echo "Verifying Java Installation..."
java -version
#step 5: Download and install git and maven packages 
echo "Download and Install git and maven..."
sudo yum install -y git maven 
#step 6: Download and install docker 
echo "Download and Install docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
