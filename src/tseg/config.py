import os

shared_config = {}
output_dir = os.path.join(os.path.expanduser("~"), "tseg_output")
shared_config["output_dir"] = output_dir


class TsegStyles:
    BTN_GREEN = """
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
