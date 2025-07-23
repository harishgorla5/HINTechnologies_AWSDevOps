import boto3
import os
import sys
from botocore.exceptions import ClientError

def list_key_pairs(ec2):
    response = ec2.describe_key_pairs()
    print("\nExisting Key Pairs:")
    if not response['KeyPairs']:
        print("  None")
    else:
        for kp in response['KeyPairs']:
            print(f"  - {kp['KeyName']}")

def create_key_pair(ec2, key_name):
    try:
        ec2.describe_key_pairs(KeyNames=[key_name])
        print(f"Key Pair '{key_name}' already exists. Using the existing key.")
    except ClientError:
        print(f"Key Pair '{key_name}' does not exist. Creating a new one...")
        key_pair = ec2.create_key_pair(KeyName=key_name)
        with open(f"{key_name}.pem", "w") as file:
            file.write(key_pair['KeyMaterial'])
        os.chmod(f"{key_name}.pem", 0o400)
        print(f"New Key Pair created and saved as {key_name}.pem")

def list_security_groups(ec2):
    response = ec2.describe_security_groups()
    print("\nExisting Security Groups:")
    for sg in response['SecurityGroups']:
        print(f"  - {sg['GroupName']} (ID: {sg['GroupId']})")

def get_or_create_security_group(ec2, group_input):
    security_group_id = None
    try:
        if group_input.startswith("sg-"):
            response = ec2.describe_security_groups(GroupIds=[group_input])
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f"Security Group ID '{group_input}' found. Using the existing group.")
        else:
            response = ec2.describe_security_groups(GroupNames=[group_input])
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f"Security Group Name '{group_input}' found. Using the existing group.")
    except ClientError:
        print(f"Security Group '{group_input}' does not exist. Creating a new one...")
        response = ec2.create_security_group(GroupName=group_input, Description="Security group for EC2 instance")
        security_group_id = response['GroupId']
        ec2.authorize_security_group_ingress(GroupId=security_group_id, IpProtocol="tcp", FromPort=22, ToPort=22, CidrIp="0.0.0.0/0")
        print(f"New Security Group created with ID: {security_group_id}")

    return security_group_id

def get_amis_by_os(ec2_client, os_choice):
    filters_map = {
        "1": [  # Amazon Linux 2
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']}
        ],
        "2": [  # Ubuntu 20.04 LTS
            {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']},
            {'Name': 'state', 'Values': ['available']}
        ],
        "3": [  # Windows Server 2019 English Full Base
            {'Name': 'name', 'Values': ['Windows_Server-2019-English-Full-Base-*']},
            {'Name': 'state', 'Values': ['available']}
        ],
        "4": [  # Red Hat Enterprise Linux 8
            {'Name': 'name', 'Values': ['RHEL-8-HVM-*']},
            {'Name': 'state', 'Values': ['available']}
        ],
        "5": [  # SUSE Linux Enterprise Server 15
            {'Name': 'name', 'Values': ['suse-sles-15-sp*']},
            {'Name': 'state', 'Values': ['available']}
        ],
    }
    filters = filters_map.get(os_choice)
    if not filters:
        print("Invalid OS choice.")
        return []

    response = ec2_client.describe_images(
        Filters=filters,
        Owners=['amazon', '099720109477', '137112412989', '125523088429'],  
        # Amazon, Canonical (Ubuntu), Microsoft, RedHat, SUSE owners
    )
    images = response.get('Images', [])
    images.sort(key=lambda x: x['CreationDate'], reverse=True)
    return images

def select_ami(ec2_client):
    print("\nSelect OS for the AMI:")
    print("1 - Amazon Linux")
    print("2 - Ubuntu 20.04 LTS")
    print("3 - Windows Server 2019")
    print("4 - Red Hat Enterprise Linux 8")
    print("5 - SUSE Linux Enterprise Server 15")

    os_choice = input("Enter the number corresponding to your desired OS (default 1): ").strip() or "1"
    images = get_amis_by_os(ec2_client, os_choice)
    if not images:
        print("No AMIs found for selected OS.")
        sys.exit(1)

    print("\nAvailable AMIs:")
    for idx, img in enumerate(images[:10], start=1):
        print(f"{idx}. {img['Name']} - {img['ImageId']} - Created on {img['CreationDate'][:10]}")

    choice = input("Select an AMI by number (default 1): ").strip()
    if not choice or not choice.isdigit() or int(choice) < 1 or int(choice) > len(images[:10]):
        choice = 1
    else:
        choice = int(choice)

    selected_ami = images[choice - 1]['ImageId']
    print(f"Selected AMI: {selected_ami}")
    return selected_ami

def main():
    print("""\n!!! Welcome to HINTechnologies !!!\n
This script will guide you step-by-step to create an EC2 instance.
""")

    # AWS Region
    region_options = {
        "1": "ap-south-1",
        "2": "us-east-1",
        "3": "us-west-2",
        "4": "eu-north-1",
    }
    print("Select AWS Region:")
    for key, value in region_options.items():
        print(f"{key} - {value}")
    region_choice = input("Enter the number corresponding to your desired region: ").strip()
    region = region_options.get(region_choice, "us-east-1")

    session = boto3.Session(region_name=region)
    ec2 = session.client('ec2')

    # List existing Key Pairs
    list_key_pairs(ec2)
    # Key Pair
    key_name = input("\nEnter the name of the Key Pair (if it doesn't exist, it will be created): ").strip()
    create_key_pair(ec2, key_name)

    # List existing Security Groups
    list_security_groups(ec2)
    # Security Group
    group_input = input("\nEnter the Security Group name or ID (if it doesn't exist, it will be created): ").strip()
    security_group_id = get_or_create_security_group(ec2, group_input)

    # Instance Type Selection
    print("\nSelect Instance Type:")
    print("1 - [2vCPU and 2GiB RAM - t3.small] TomcatServer")
    print("2 - [2vCPU and 4GiB RAM - t3.medium] Jenkins_Server | Sonarqube | Jfrog | Docker | K8S")
    print("3 - [2vCPU and 8GiB RAM - t3.large] Kubernetes Setup")
    instance_type_choice = input("Enter the number corresponding to your desired instance type: ").strip()
    instance_type_map = {"1": "t3.small", "2": "t3.medium", "3": "t3.large"}
    instance_type = instance_type_map.get(instance_type_choice, "t3.small")
    print(f"Selected Instance Type: {instance_type}")

    # AMI Selection with OS choice
    ami_id = select_ami(ec2)

    # Root Storage Size
    storage_size = input("\nEnter Root Storage Size in GB (default: 8): ").strip() or "8"

    # Additional EBS volume
    add_volume = input("\nDo you want to add an additional EBS volume? (y/n, default n): ").strip().lower() or "n"
    additional_volume = None
    if add_volume == "y":
        vol_size = input("Enter additional EBS volume size in GB (e.g., 10): ").strip()
        if vol_size.isdigit() and int(vol_size) > 0:
            additional_volume = int(vol_size)
        else:
            print("Invalid size, skipping additional volume.")

    # User Data
    default_user_data_file = "temp-swap-setup-file.txt"
    if os.path.isfile(default_user_data_file):
        user_data_file = default_user_data_file
    else:
        user_data_file = input("\nUser Data file not found. Enter path to the User Data file: ").strip()
        if not os.path.isfile(user_data_file):
            print("Error: Specified User Data file does not exist.")
            sys.exit(1)
    with open(user_data_file, 'r') as file:
        user_data = file.read()

    # Instance Count and Names
    instance_count = int(input("\nEnter the number of instances to create (default: 1): ").strip() or "1")
    if instance_count <= 0:
        print("Instance count must be at least 1.")
        sys.exit(1)

    if instance_count > 1:
        instance_names = []
        for i in range(instance_count):
            instance_name = input(f"Enter the name for instance {i+1}: ").strip()
            if not instance_name:
                print(f"Instance name for instance {i+1} is required.")
                sys.exit(1)
            instance_names.append(instance_name)
    else:
        instance_name = input("Enter the name for the EC2 instance: ").strip()
        if not instance_name:
            print("Instance name is required.")
            sys.exit(1)
        instance_names = [instance_name]

    # Block device mappings
    block_device_mappings = [{
        "DeviceName": "/dev/xvda",
        "Ebs": {
            "VolumeSize": int(storage_size),
            "DeleteOnTermination": True,
            "VolumeType": "gp2"
        }
    }]

    if additional_volume:
        # Attach an extra volume at /dev/sdf (common secondary device)
        block_device_mappings.append({
            "DeviceName": "/dev/sdf",
            "Ebs": {
                "VolumeSize": additional_volume,
                "DeleteOnTermination": True,
                "VolumeType": "gp2"
            }
        })

    print("\nLaunching instances...")
    try:
        instances = ec2.run_instances(
            ImageId=ami_id,
            MinCount=instance_count,
            MaxCount=instance_count,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=[security_group_id],
            BlockDeviceMappings=block_device_mappings,
            UserData=user_data,
        )
        instance_ids = [instance['InstanceId'] for instance in instances['Instances']]
        print(f"\nSuccessfully launched EC2 instances: {', '.join(instance_ids)}")

        # Tag Instances
        for instance_id, name in zip(instance_ids, instance_names):
            ec2.create_tags(Resources=[instance_id], Tags=[{"Key": "Name", "Value": name}])
        print("Instances tagged successfully.")

        # Fetch Instance Details
        response = ec2.describe_instances(InstanceIds=instance_ids)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                print(f"Instance ID: {instance['InstanceId']}, Public IP: {instance.get('PublicIpAddress')}")

    except Exception as e:
        print(f"Error launching instances: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
