"""Entry point. Starts a Moto sandbox, populates test data,
and runs an interactive chat loop against the agent.

    ./.venv/bin/python main.py
"""
from moto import mock_aws

from agent import ask, build_router
from moto_setup import populate_all, summary


@mock_aws
def run() -> None:
    print("Loading test AWS account...")
    populate_all()
    print("\nTest account ready:")
    print(summary())

    router = build_router()

    print("\nChat started. Type 'exit' to quit.\n")
    while True:
        try:
            question = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            break

        answer = ask(router, question)
        print(f"\nbot > {answer}\n")


if __name__ == "__main__":
    run()
