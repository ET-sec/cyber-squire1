"""Scripted demo that runs the four sample questions and prints a
clean transcript. Used to generate sample_output.txt.

    ./.venv/bin/python demo.py
"""
from moto import mock_aws

from agent import ask, build_router
from moto_setup import ec2_ip, populate_all, summary


@mock_aws
def run() -> None:
    print("=" * 70)
    print("AWS Q&A Chatbot | Demo Run")
    print("=" * 70)
    print()

    print("Loading test AWS account...")
    populate_all()
    print("\nTest account:")
    print(summary())
    print()

    router = build_router()
    web_ip = ec2_ip("brand-web")

    questions = [
        "How many S3 buckets are exposed to the public?",
        "What data does the S3 bucket tigoue-customers hold?",
        f"What is the size of the EC2 instance with IP {web_ip}?",
        "What permissions does the user et-analyst have?",
    ]

    for i, q in enumerate(questions, 1):
        print("-" * 70)
        print(f"Q{i}: {q}")
        print(f"A{i}: {ask(router, q)}")
        print()


if __name__ == "__main__":
    run()
