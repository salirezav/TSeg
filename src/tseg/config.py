import os

shared_config = {}
output_dir = os.path.join(os.path.expanduser("~"), "tseg_output")
shared_config["output_dir"] = output_dir
