"""Populates a Moto sandbox with test data.

Called on at chatbot startup from inside the @mock_aws context in main.py.
"""

import json

import boto3

REGION = "us-east-1"

_EC2_INSTANCES: list[dict] = []


def populate_all() -> None:
    _populate_s3()
    _populate_ec2()
    _populate_iam()


def summary() -> str:
    """Readable summary of the test account, shown at startup."""
    lines = [
        "S3 buckets: cd-prod-logs (public), tigoue-customers, cd-runbooks",
        "IAM users:  et-admin (admin), et-analyst (readonly + inline)",
    ]
    for inst in _EC2_INSTANCES:
        lines.append(
            f"EC2:        {inst['name']} ({inst['instance_type']}) at {inst['private_ip']}"
        )
    return "\n".join(f"  - {ln}" for ln in lines)


def ec2_ip(name: str) -> str:
    """Return the private IP that Moto generated for a named EC2 instance."""
    for inst in _EC2_INSTANCES:
        if inst["name"] == name:
            return inst["private_ip"]
    raise KeyError(name)


def _populate_s3() -> None:
    s3 = boto3.client("s3", region_name=REGION)

    s3.create_bucket(Bucket="cd-prod-logs")
    public_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicRead",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::cd-prod-logs/*",
            }
        ],
    }
    s3.put_bucket_policy(Bucket="cd-prod-logs", Policy=json.dumps(public_policy))
    s3.put_object(
        Bucket="cd-prod-logs", Key="2026-04-20-access.log", Body=b"GET /home 200 14ms"
    )
    s3.put_object(
        Bucket="cd-prod-logs", Key="2026-04-19-access.log", Body=b"GET /login 200 22ms"
    )

    s3.create_bucket(Bucket="tigoue-customers")
    s3.put_object(
        Bucket="tigoue-customers",
        Key="users.csv",
        Body=b"id,email\n1,alice@example.com\n2,bob@example.com\n",
    )
    s3.put_object(
        Bucket="tigoue-customers",
        Key="addresses.csv",
        Body=b"user_id,city\n1,Atlanta\n2,Seattle\n",
    )

    s3.create_bucket(Bucket="cd-runbooks")
    s3.put_object(
        Bucket="cd-runbooks",
        Key="runbook.md",
        Body=b"# On-Call Runbook\nStep 1: check Datadog.\nStep 2: page secondary.\n",
    )


def _populate_ec2() -> None:
    ec2 = boto3.client("ec2", region_name=REGION)

    specs = [
        ("brand-web", "t3.micro", "ami-12345678"),
        ("brand-analytics", "m5.large", "ami-87654321"),
    ]
    for name, instance_type, ami in specs:
        resp = ec2.run_instances(
            ImageId=ami,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": name}],
                }
            ],
        )
        inst = resp["Instances"][0]
        _EC2_INSTANCES.append(
            {
                "name": name,
                "instance_type": inst["InstanceType"],
                "private_ip": inst.get("PrivateIpAddress"),
            }
        )


def _populate_iam() -> None:
    iam = boto3.client("iam", region_name=REGION)

    admin_policy = iam.create_policy(
        PolicyName="CDAdminAccess",
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
            }
        ),
    )["Policy"]["Arn"]

    read_only_policy = iam.create_policy(
        PolicyName="CDReadOnlyAccess",
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:Get*", "s3:List*", "ec2:Describe*", "iam:Get*"],
                        "Resource": "*",
                    }
                ],
            }
        ),
    )["Policy"]["Arn"]

    iam.create_user(UserName="et-admin")
    iam.attach_user_policy(UserName="et-admin", PolicyArn=admin_policy)

    iam.create_user(UserName="et-analyst")
    iam.attach_user_policy(UserName="et-analyst", PolicyArn=read_only_policy)
    iam.put_user_policy(
        UserName="et-analyst",
        PolicyName="RunbooksRead",
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:GetObject"],
                        "Resource": "arn:aws:s3:::cd-runbooks/*",
                    }
                ],
            }
        ),
    )
