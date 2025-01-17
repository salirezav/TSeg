import os

# Dictionary to hold shared configuration settings
shared_config = {}

# Define the output directory path, which is a folder named 'tseg_output' in the user's home directory
output_dir = os.path.join(os.path.expanduser("~"), "tseg_output")

# Store the output directory path in the shared configuration dictionary
shared_config["output_dir"] = output_dir


class TsegStyles:
    """
    A class to hold style definitions for the TSEG application.
    Currently, it contains styles for a green button.
    """

    BTN_PRIMARY = """
    QPushButton{
    background-color: #007bff;
    border-color: #007bff;
    color: white;
    font-size: 16px;
    }
    QPushButton::hover
    {
    background-color: #0056b3;
    border-color: #0056b3;
    }
    QPushButton::pressed
    {
    background-color: #004085;
    border-color: #004085;
    }
    """
