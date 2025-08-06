#!/bin/bash

# Function to list EC2 instances with required details
list_instances() {
    echo "Fetching instance details..."

    # AWS CLI command to fetch instance details
    aws ec2 describe-instances --query "Reservations[*].Instances[*].{Name: Tags[?Key=='Name']|[0].Value, InstanceID: InstanceId, PublicIP: PublicIpAddress, PrivateIP: PrivateIpAddress}" --output table
}

# Run the function
list_instances
