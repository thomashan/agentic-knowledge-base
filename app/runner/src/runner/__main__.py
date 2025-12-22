import argparse

from runner.config import Settings
from runner.runner import Runner


# --- Main CLI logic ---
def main():
    parser = argparse.ArgumentParser(description="Run an agentic workflow using the Runner.")
    parser.add_argument("query", type=str, help="The query or input for the workflow.")
    args = parser.parse_args()

    # Instantiate Settings to load from environment
    settings = Settings()

    # Instantiate the Runner with the settings object
    runner = Runner(
        settings=settings,
        orchestrator_config={"verbose": True},
    )

    # Run the workflow and print the result
    result = runner.run(args.query)
    print(result)


if __name__ == "__main__":
    main()
