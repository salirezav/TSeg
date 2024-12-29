import shutil
from pathlib import Path

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from tseg._reader import napari_get_reader
from tseg._widget import PreProcessingWidget
from tseg._writer import write_multiple, write_single_image
# from io import InputOutputWidget

# Ensure the temporary folder exists and is empty
temp_dir = Path.home() / ".tseg"
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir()

__all__ = (
    "napari_get_reader",
    "write_single_image",
    "write_multiple",
    "InputOutputWidget",
    "PreProcessingWidget",
    "SegmentationWidget"
)
