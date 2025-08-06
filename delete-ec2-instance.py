import boto3
import time

def list_ec2_instances():
    # Create a session using your AWS credentials
    ec2 = boto3.client('ec2')

    try:
        # Retrieve a list of EC2 instances
        print("Fetching EC2 instances...")
        response = ec2.describe_instances()
        
        # Loop through the instances and collect their details
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_name = "No Name"
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                
                instance_state = instance['State']['Name']
                
                instances.append({
                    'InstanceName': instance_name,
                    'State': instance_state,
                    'InstanceId': instance['InstanceId']
                })
        
        # If no instances are found
        if not instances:
            print("No EC2 instances found.")
            return None
        
        # Display the instances with name and state
        print("\nList of EC2 Instances:")
        for idx, instance in enumerate(instances):
            print(f"{idx + 1}. Name: {instance['InstanceName']}, State: {instance['State']}")
        
        return instances

    except Exception as e:
        print(f"Error fetching EC2 instances: {e}")
        return None

def delete_ec2_instances(instance_ids, instances):
    # Create a session using your AWS credentials
    ec2 = boto3.client('ec2')

    try:
        # Terminate the EC2 instances
        print(f"\nAttempting to terminate EC2 instances: {', '.join(instance_ids)}...")
        response = ec2.terminate_instances(InstanceIds=instance_ids)

        # Output the state change of the instances after termination
        print("\nTermination initiated for the following EC2 Instances:")
        for instance in response['TerminatingInstances']:
            instance_id = instance['InstanceId']
            current_state = instance['CurrentState']['Name']
            instance_name = next(inst['InstanceName'] for inst in instances if inst['InstanceId'] == instance_id)
            print(f"- Name: {instance_name}, State: {current_state}")

        # Wait for the instances to terminate and then update their state
        print("\nWaiting for instances to terminate...")
        terminated_instances = []
        
        # Poll the instance status until they are terminated
        while len(terminated_instances) < len(instance_ids):
            time.sleep(10)  # Check every 10 seconds
            
            # Describe the instances to check their current state
            status = ec2.describe_instances(InstanceIds=instance_ids)
            
            # Collect the instance statuses
            for reservation in status['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] == 'terminated':
                        instance_name = next(inst['InstanceName'] for inst in instances if inst['InstanceId'] == instance['InstanceId'])
                        terminated_instances.append(instance['InstanceId'])
                        print(f"- Name: {instance_name}, State: terminated")
        
        print("\nAll selected instances have been terminated.")

    except Exception as e:
        print(f"Error terminating EC2 instances: {e}")

if __name__ == "__main__":
    # List EC2 instances
    instances = list_ec2_instances()
    
    if instances:
        # Ask user if they want to delete all instances
        user_input = input("\nDo you want to delete all EC2 instances? (yes/no): ").strip().lower()
        
        if user_input == 'yes':
            # Get all instance IDs to delete
            instance_ids = [instance['InstanceId'] for instance in instances]
            delete_ec2_instances(instance_ids, instances)
        else:
            # Ask user which instances they want to delete
            try:
                selected_instances = input("\nEnter the numbers of the EC2 instances you want to delete, separated by commas (e.g., 1, 3, 5): ")
                selected_indexes = [int(i.strip()) - 1 for i in selected_instances.split(',')]

                # Validate selection
                if all(0 <= idx < len(instances) for idx in selected_indexes):
                    instance_ids_to_delete = [instances[idx]['InstanceId'] for idx in selected_indexes]
                    print(f"\nYou selected the following instances to delete:")
                    for idx in selected_indexes:
                        print(f"- Name: {instances[idx]['InstanceName']}, State: {instances[idx]['State']}")
                    delete_ec2_instances(instance_ids_to_delete, instances)
                else:
                    print("Invalid selection. Please ensure the numbers are within the list of instances.")
            except ValueError:
                print("Invalid input. Please enter a list of numbers separated by commas.")
