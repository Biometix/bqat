import subprocess
from bqat import __version__


def test_installation_pip():
    subprocess.call(["pip", "install", f"./dist/bqat-{__version__}-py3-none-any.whl"])
    out = subprocess.call(["bqat", "--help"])
    assert len(str(out)) > 0


def test_module_run():
    out = subprocess.call(["python", "-m", "bqat", "--help"])
    assert len(str(out)) > 0
