import pulumi
import pulumi_aws as aws

# Configuration
config = pulumi.Config()
instance_type = config.get("instance_type") or "t2.medium"
ami_id = config.get("ami_id") or "ami-0abcdef1234567890"

# Create VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
)

# Create Public Subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="us-west-2a",
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
)

# Create Route Table
route_table = aws.ec2.RouteTable("route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
)

# Associate Route Table with Public Subnet
rt_assoc_public = aws.ec2.RouteTableAssociation("rt-assoc-public",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id,
)

# Create Security Group
security_group = aws.ec2.SecurityGroup("web-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
    }],
)

# Create EC2 instances
master = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    vpc_security_group_ids=[security_group.id],
    ami=ami_id,
    subnet_id=public_subnet.id,
    tags={
        "Name": "master-node",
    },
)

worker1 = aws.ec2.Instance("worker-node-1",
    instance_type=instance_type,
    vpc_security_group_ids=[security_group.id],
    ami=ami_id,
    subnet_id=public_subnet.id,
    tags={
        "Name": "worker-node-1",
    },
)

worker2 = aws.ec2.Instance("worker-node-2",
    instance_type=instance_type,
    vpc_security_group_ids=[security_group.id],
    ami=ami_id,
    subnet_id=public_subnet.id,
    tags={
        "Name": "worker-node-2",
    },
)

# Export the public IP of the instances
pulumi.export("master_public_ip", master.public_ip)
pulumi.export("worker1_public_ip", worker1.public_ip)
pulumi.export("worker2_public_ip", worker2.public_ip)
