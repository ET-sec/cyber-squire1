"""LangChain tools for answering AWS account questions.

Each @tool is a thin boto3 wrapper. Keep docstrings tight; the LLM
reads them to pick which tool to call.

Clients are created inside each function, not at module load, so Moto
can intercept the boto3 calls.
"""

import ipaddress
import json
import re

import boto3
from botocore.exceptions import ClientError
from langchain_core.tools import tool

REGION = "us-east-1"

_BUCKET_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]$")
_IAM_USERNAME_RE = re.compile(r"^[A-Za-z0-9+=,.@\-_]{1,64}$")


@tool
def count_public_s3_buckets() -> str:
    """Count S3 buckets that allow public access.

    A bucket counts as public if its policy grants Principal '*' with
    Effect Allow, or its ACL grants AllUsers/AuthenticatedUsers.
    """
    s3 = boto3.client("s3", region_name=REGION)
    try:
        buckets = s3.list_buckets().get("Buckets", [])
    except ClientError as e:
        return f"Error listing buckets: {_err_code(e)}"

    public = [b["Name"] for b in buckets if _is_public(s3, b["Name"])]
    if not public:
        return f"Scanned {len(buckets)} bucket(s). None are public."
    return (
        f"Scanned {len(buckets)} bucket(s). {len(public)} are public: "
        f"{', '.join(public)}."
    )


@tool
def list_s3_bucket_contents(bucket_name: str) -> str:
    """List the objects in an S3 bucket. Returns keys and sizes.

    Rejects bucket names that do not match AWS naming rules.
    """
    if not _BUCKET_NAME_RE.match(bucket_name):
        return f"'{bucket_name}' is not a valid S3 bucket name."

    s3 = boto3.client("s3", region_name=REGION)
    try:
        resp = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as e:
        code = _err_code(e)
        return f"Error listing '{bucket_name}': {code}"

    objects = resp.get("Contents", [])
    if not objects:
        return f"Bucket '{bucket_name}' is empty."

    lines = [f"Bucket '{bucket_name}' holds {len(objects)} object(s):"]
    for obj in objects:
        lines.append(f"  - {obj['Key']} ({obj['Size']} bytes)")
    return "\n".join(lines)


@tool
def get_ec2_instance_by_ip(ip_address: str) -> str:
    """Find an EC2 instance by its public or private IPv4 address.
    Returns name, type, state, and ID.
    """
    try:
        ipaddress.IPv4Address(ip_address)
    except ValueError:
        return f"'{ip_address}' is not a valid IPv4 address."

    ec2 = boto3.client("ec2", region_name=REGION)
    try:
        reservations = ec2.describe_instances(
            Filters=[{"Name": "private-ip-address", "Values": [ip_address]}]
        ).get("Reservations", [])

        if not reservations:
            reservations = ec2.describe_instances(
                Filters=[{"Name": "ip-address", "Values": [ip_address]}]
            ).get("Reservations", [])
    except ClientError as e:
        return f"Error querying EC2 for '{ip_address}': {_err_code(e)}"

    if not reservations:
        return f"No EC2 instance found with IP {ip_address}."

    inst = reservations[0]["Instances"][0]
    name = _tag(inst.get("Tags", []), "Name") or "(unnamed)"
    return (
        f"Instance '{name}': type={inst['InstanceType']}, "
        f"state={inst['State']['Name']}, id={inst['InstanceId']}."
    )


@tool
def get_iam_user_permissions(username: str) -> str:
    """Return the managed and inline policies attached to an IAM user."""
    if not _IAM_USERNAME_RE.match(username):
        return f"'{username}' is not a valid IAM username."

    iam = boto3.client("iam", region_name=REGION)
    try:
        attached = iam.list_attached_user_policies(UserName=username).get(
            "AttachedPolicies", []
        )
        inline = iam.list_user_policies(UserName=username).get("PolicyNames", [])
    except ClientError as e:
        return f"Error querying IAM for '{username}': {_err_code(e)}"

    lines = [f"Permissions for '{username}':"]
    if attached:
        lines.append(f"  Managed ({len(attached)}):")
        for p in attached:
            lines.append(f"    - {p['PolicyName']}  ({p['PolicyArn']})")
    else:
        lines.append("  Managed: none")

    if inline:
        lines.append(f"  Inline ({len(inline)}):")
        for n in inline:
            lines.append(f"    - {n}")
    else:
        lines.append("  Inline: none")
    return "\n".join(lines)


def _is_public(s3, bucket: str) -> bool:
    try:
        doc = json.loads(s3.get_bucket_policy(Bucket=bucket)["Policy"])
        for stmt in doc.get("Statement", []):
            if stmt.get("Effect") == "Allow" and _is_wildcard(stmt.get("Principal")):
                return True
    except ClientError as e:
        if _err_code(e) != "NoSuchBucketPolicy":
            raise

    try:
        acl = s3.get_bucket_acl(Bucket=bucket)
        for grant in acl.get("Grants", []):
            uri = grant.get("Grantee", {}).get("URI", "")
            if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                return True
    except ClientError as e:
        if _err_code(e) not in {"AccessDenied", "NoSuchBucket"}:
            raise

    return False


def _is_wildcard(principal) -> bool:
    if principal == "*":
        return True
    if isinstance(principal, dict) and principal.get("AWS") == "*":
        return True
    return False


def _tag(tags: list, key: str) -> str | None:
    for t in tags:
        if t.get("Key") == key:
            return t.get("Value")
    return None


def _err_code(e: ClientError) -> str:
    return e.response.get("Error", {}).get("Code", "UnknownError")


ALL_TOOLS = [
    count_public_s3_buckets,
    list_s3_bucket_contents,
    get_ec2_instance_by_ip,
    get_iam_user_permissions,
]
