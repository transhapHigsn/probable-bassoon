# from operator import itemgetter
import boto3
from botocore.exceptions import ClientError

"""
    Instead of getting client in every request, client should be passed
    as context to every function call which is either getting, creating
    or destroying resources.

    Create security group and key pair should be done once for a user, solving
    was getting more out of context so skipped that for now. Key pair creation will
    be optional if no access to instance is required, which is hardly the case.
"""


def get_client(resource_type="ec2"):
    return boto3.client(resource_type)


def get_instances(client):
    response = client.describe_instances()
    return response


def get_images(client):
    response = client.describe_images(
        Filters=[
            {
                "Name": "name",
                "Values": [
                    "amzn2-ami-hvm-2.0.????????.?-x86_64-gp2",
                ],
            },
            {
                "Name": "state",
                "Values": [
                    "available",
                ],
            },
        ],
        Owners=[
            "amazon",
        ],
    )
    return response["Images"]


def get_latest_ami():
    # client = get_client()
    # images = get_images(client=client)
    # images_ = [{"date": image["creation_date"], "id": image["ImageId"]} for image in images]
    # return sorted(images_, key=itemgetter("date"), reverse=True)[0]["id"]
    return "ami-068d43a544160b7ef"


def install_docker_and_run_nginx(instance_type):
    script = f"""
#!/bin/bash
set -e

### installing essentials

sudo yum update -y
sudo yum install git -y

### install docker.

sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

### write html content

cd /home/ec2-user/
mkdir html
cat << EOF >> /home/ec2-user/html/index.html
<html>
    <head>
        <title>Machine Type</title>
    </head>
    <body>
        <h1>Hi, this is instance type {instance_type} </h1>
    </body>
</html>
EOF

sudo chmod -R 755 /home/ec2-user/html/
sudo docker run -p 80:80 -v /home/ec2-user/html:/usr/share/nginx/html nginx:alpine

"""
    return script


def create_instance(instance_type):
    client = get_client()
    ami = get_latest_ami()

    """
        for production use case, you would probably like to set following things as well:
            - vpc
            - subnet
            - iam instance profile
            - ebs info
            - tags
            - monitoring, etc.,
    """

    check_if_available(instance_type=instance_type)

    response = client.run_instances(
        ImageId=ami,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1,
        Monitoring={"Enabled": False},
        UserData=install_docker_and_run_nginx(instance_type=instance_type),
        KeyName="segmind",
        SecurityGroups=[
            "segmind_sg",
        ],
    )
    return response


def get_instance_info(instance_id):
    client = get_client()
    response = client.describe_instances(
        InstanceIds=[
            instance_id,
        ],
    )

    reservations = response["Reservations"]
    if not reservations:
        return 404, response

    instances = reservations[0]["Instances"]
    if not instances:
        return 404, response

    assert instances[0]["InstanceId"] == instance_id
    return 200, instances[0]


def terminate_instance(instance_id):
    client = get_client()
    response = client.terminate_instances(InstanceIds=[instance_id])
    return response


def get_instance_type_available():
    client = get_client()
    response = client.describe_instance_type_offerings(
        LocationType="region",
    )
    return response


def check_if_available(instance_type):
    client = get_client()
    response = client.describe_instance_types(
        InstanceTypes=[instance_type],
    )
    return response


def create_key_pair():
    client = get_client()
    response = client.create_key_pair(
        KeyName="segmind",
    )
    return response


def create_security_group():
    client = get_client()
    response = client.describe_vpcs(
        Filters=[
            {"Name": "isDefault", "Values": ["true"]},
        ]
    )
    vpc_id = response.get("Vpcs", [{}])[0].get("VpcId", "")

    try:
        response = client.create_security_group(
            GroupName="segmind_sg", Description="DESCRIPTION", VpcId=vpc_id
        )
        security_group_id = response["GroupId"]
        print("Security Group Created %s in vpc %s." % (security_group_id, vpc_id))

        data = client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
            ],
        )
        print("Ingress Successfully Set %s" % data)
        return response, data
    except ClientError as e:
        print(e)
        return (None, None)


def get_security_group():
    client = get_client()
    response = client.describe_security_groups(
        GroupNames=[
            "segmind_sg",
        ],
    )
    return response


def check_if_instance_already_exists():
    client = get_client()
    response = client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["pending", "running"]}]
    )

    reservations = response["Reservations"]
    if not reservations:
        return

    instances = reservations[0]["Instances"]
    if not instances:
        return

    return instances[0]
