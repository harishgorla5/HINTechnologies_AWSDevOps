import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def list_instances():
    try:
        # Create an EC2 client
        ec2 = boto3.client('ec2')
        
        # Describe instances
        response = ec2.describe_instances()
        
        # Parse the response to get required instance details
        print(f"{'Name':<20}{'Instance ID':<20}{'Public IP':<20}{'Private IP':<20}")
        print("=" * 80)
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Get instance details
                instance_id = instance.get('InstanceId', 'N/A')
                public_ip = instance.get('PublicIpAddress', 'N/A')
                private_ip = instance.get('PrivateIpAddress', 'N/A')
                
                # Get the Name tag if it exists
                name_tag = 'N/A'
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            name_tag = tag['Value']
                            break
                
                # Print instance details
                print(f"{name_tag:<20}{instance_id:<20}{public_ip:<20}{private_ip:<20}")
    
    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_instances()
