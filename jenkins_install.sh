#!/bin/bash

# This script will install Jenkins and its dependencies on Amazon Linux 2

# Step 1: Update the System
echo "Updating the system..."
sudo yum update -y

# Step 2: Install Java (Required for Jenkins)
echo "Installing Java 17 (Amazon Corretto)..."
sudo yum install java-17-amazon-corretto -y

# Step 3: Verify Java Installation
echo "Verifying Java Installation..."
java -version

# Step 4: Download Jenkins GPG Key [https://pkg.jenkins.io/] If the Jenkins GPG key URL changes, always check the official Jenkins repository site for the latest updates and changes to the URL.
echo "Downloading Jenkins GPG key..."
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io-2023.key

#step 5: Download and install git and maven packages 
echo "Download and Install git and maven..."
sudo yum install -y git maven 

#step 6: Download and install docker 
echo "Download and Install docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Step 7: Add Jenkins Repository
echo "Adding Jenkins repository..."
sudo curl -fsSL https://pkg.jenkins.io/redhat/jenkins.repo -o /etc/yum.repos.d/jenkins.repo

# Step 8: Install Jenkins
echo "Installing Jenkins..."
sudo yum install jenkins -y

# Step 9: Start Jenkins and Enable Jenkins to Start on Boot
echo "Starting Jenkins service..."
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Step 10: Access Jenkins
echo "Jenkins installation completed. You can access Jenkins at http://<host-ip>:8080"

# Step 11: Display the Initial Admin Password
echo "Displaying Jenkins Initial Admin Password..."
cat /var/lib/jenkins/secrets/initialAdminPassword

#Step 12 : Add decovker to jenkins group 
echo "adding docker user to jenkins group "
sudo usermod -aG docker jenkins

#Step 13 : Restart jenkins
echo "restart jenkins"
sudo systemctl restart jenkins
