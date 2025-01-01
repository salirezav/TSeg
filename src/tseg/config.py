import os

shared_config = {}
output_dir = os.path.join(os.path.expanduser("~"), "tseg_output")
shared_config["output_dir"] = output_dir


class TsegStyles:
    BTN_GREEN = """
    QPushButton{
    background-color: #198754;
    border-color: #28a745;
    }
    QPushButton::hover
    {
    background-color: #218838;
    border-color: #1e7e34;
    }
    QPushButton::pressed
    {
    background-color: #1e7e34;
    border-color: #1c7430;
    }
    """
