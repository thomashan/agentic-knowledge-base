from unittest.mock import MagicMock, patch

import pytest

# The main function to be tested
from runner.__main__ import main


@patch("runner.__main__.Settings")
@patch("runner.__main__.Runner")
@patch("argparse.ArgumentParser")
def test_main_runner_workflow(mock_arg_parser, mock_runner_class, mock_settings_class):
    """
    Test that the main function in __main__.py correctly initializes Settings,
    instantiates the Runner, calls the run method, and prints the result.
    """
    # Arrange: Configure mocks
    # Mock for argparse
    mock_args = MagicMock()
    mock_args.query = "Test query about Docker"
    mock_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock for Settings
    mock_settings_instance = MagicMock()
    mock_settings_class.return_value = mock_settings_instance

    # Mock for Runner instance
    mock_runner_instance = MagicMock()
    mock_runner_instance.run.return_value = "This is the final result."
    mock_runner_class.return_value = mock_runner_instance

    # Act: Call the main function
    with patch("builtins.print") as mock_print:
        main()

        # Assert
        # 1. Check if Settings was instantiated
        mock_settings_class.assert_called_once()

        # 2. Check if Runner was instantiated with the settings object
        mock_runner_class.assert_called_once_with(
            settings=mock_settings_instance,
            orchestrator_config={"verbose": True},
        )

        # 3. Check if the run method was called with the query
        mock_runner_instance.run.assert_called_once_with("Test query about Docker")

        # 4. Check if the result was printed to the console
        mock_print.assert_called_once_with("This is the final result.")


if __name__ == "__main__":
    pytest.main([__file__])
