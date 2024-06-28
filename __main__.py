# import pulumi
# import pulumi_aws as aws

# # Configuration
# config = pulumi.Config()
# instance_type = "t2.micro"
# ami_id = 'ami-003c463c8207b4dfa'

# # Create VPC
# vpc = aws.ec2.Vpc("my-vpc",
#     cidr_block="10.0.0.0/16",
#     enable_dns_support=True,
#     enable_dns_hostnames=True,
# )

# # Create Public Subnet
# public_subnet = aws.ec2.Subnet("public-subnet",
#     vpc_id=vpc.id,
#     cidr_block="10.0.1.0/24",
#     map_public_ip_on_launch=True,
#     availability_zone="ap-southeast-1a",
# )

# # Create Internet Gateway
# igw = aws.ec2.InternetGateway("igw",
#     vpc_id=vpc.id,
# )

# # Create Route Table
# route_table = aws.ec2.RouteTable("route-table",
#     vpc_id=vpc.id,
#     routes=[{
#         "cidr_block": "0.0.0.0/0",
#         "gateway_id": igw.id,
#     }],
# )

# # Associate Route Table with Public Subnet
# rt_assoc_public = aws.ec2.RouteTableAssociation("rt-assoc-public",
#     subnet_id=public_subnet.id,
#     route_table_id=route_table.id,
# )

# # Create Security Group
# security_group = aws.ec2.SecurityGroup("web-secgrp",
#     description='Enable SSH and K3s access',
#     vpc_id=vpc.id,
#     ingress=[
#         {
#             "protocol": "tcp",
#             "from_port": 22,
#             "to_port": 22,
#             "cidr_blocks": ["0.0.0.0/0"],
#         },
#         {
#             "protocol": "tcp",
#             "from_port": 6443,
#             "to_port": 6443,
#             "cidr_blocks": ["0.0.0.0/0"],
#         },
#     ],
#     egress=[{
#         "protocol": "-1",
#         "from_port": 0,
#         "to_port": 0,
#         "cidr_blocks": ["0.0.0.0/0"],
#     }],
# )

# # Create EC2 instances
# master = aws.ec2.Instance("master-node",
#     instance_type=instance_type,
#     vpc_security_group_ids=[security_group.id],
#     ami=ami_id,
#     subnet_id=public_subnet.id,
#     tags={
#         "Name": "master-node",
#     },
# )

# worker1 = aws.ec2.Instance("worker-node-1",
#     instance_type=instance_type,
#     vpc_security_group_ids=[security_group.id],
#     ami=ami_id,
#     subnet_id=public_subnet.id,
#     tags={
#         "Name": "worker-node-1",
#     },
# )

# worker2 = aws.ec2.Instance("worker-node-2",
#     instance_type=instance_type,
#     vpc_security_group_ids=[security_group.id],
#     ami=ami_id,
#     subnet_id=public_subnet.id,
#     tags={
#         "Name": "worker-node-2",
#     },
# )

# # Export the public IP of the instances
# pulumi.export("master_public_ip", master.public_ip)
# pulumi.export("worker1_public_ip", worker1.public_ip)
# pulumi.export("worker2_public_ip", worker2.public_ip)



import pulumi
import pulumi_aws as aws
import os
import subprocess

# Generate SSH key pair
ssh_key_path = os.path.join(os.getcwd(), "id_rsa")
subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", ssh_key_path, "-q", "-N", ""])

# Read the generated private and public key
with open(ssh_key_path, "r") as f:
    private_key = f.read()

with open(f"{ssh_key_path}.pub", "r") as f:
    public_key = f.read()

# Create the EC2 KeyPair
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=public_key)

# Define the VPC and subnet configurations
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True
)

subnet = aws.ec2.Subnet("my-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="ap-southeast-1a"
)

# Create instances in the VPC and subnet
ami_id = "ami-003c463c8207b4dfa"  # Replace with a valid AMI ID for your region
instance_type = "t2.micro"

master_node = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=subnet.id,
    key_name=key_pair.key_name,
    tags={
        "Name": "master-node"
    })

worker_node_1 = aws.ec2.Instance("worker-node-1",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=subnet.id,
    key_name=key_pair.key_name,
    tags={
        "Name": "worker-node-1"
    })

worker_node_2 = aws.ec2.Instance("worker-node-2",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=subnet.id,
    key_name=key_pair.key_name,
    tags={
        "Name": "worker-node-2"
    })

# Export outputs
pulumi.export("master_public_ip", master_node.public_ip)
pulumi.export("worker1_public_ip", worker_node_1.public_ip)
pulumi.export("worker2_public_ip", worker_node_2.public_ip)
pulumi.export("private_key", private_key)
