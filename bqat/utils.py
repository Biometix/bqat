import subprocess
from pathlib import Path

from bqat.models import RuntimeConfiguration, JobConfiguration
import docker
from rich.console import Console


def get_runtime_info() -> dict:
    client = docker.from_env()
    info = client.info()
    version = client.version()
    runtime = {
        "Platform": version["Platform"]["Name"],
        "Engine": version["Version"],
        "OS": version["Os"],
        "Architecture": version["Arch"],
        "CPUs": info["NCPU"],
        "RAM": get_ram(info["MemTotal"]),
    }
    return runtime


def get_ram(byte) -> str:
    factor = 1024
    for order in ["", "K", "M", "G", "T", "P"]:
        ram = f"{byte:.2f} {order}B"
        if byte < factor:
            break
        byte /= factor
    return ram


def do_job(runtime: RuntimeConfiguration, job: JobConfiguration) -> None:
    Console().print(job)
    cmd = [
        "docker",
        "run",
        "--rm",
        "-it",
        "--shm-size=8G",
        "-v",
        f"{Path.cwd()}/{runtime.volume}:/app/data",
    ]
    if "cpus" in list(runtime.dict().keys()):
        cmd.append(f"--cpus={runtime.cpus}")
    if "memory" in list(runtime.dict().keys()):
        cmd.append(f"--memory={runtime.memory}")
    if "pull" in list(runtime.dict().keys()):
        if runtime.pull:
            cmd.append("--pull=always")
    cmd.append(runtime.image)
    entrypoint = runtime.entrypoint
    for flag, value in job.dict().items():
        entrypoint += f" --{flag} {value}"
    cmd.append(entrypoint)
    subprocess.call(cmd)


CONFIG_TEMPLATE = """# Docker engine runtime configuration.
runtime:
  shm: 8G
  cpus: 6
  memory: 10G
  pull: YES
  volume: data
  image: "qa:latest"
  entrypoint: "python3.8 -m qa"

# Job list with flags for each run.
job:
  - name: Iris Dataset 1
    flags:
      mode: iris
      input: data/iris

  - name: Face Dataset 2
    flags:
      mode: face
      input: data/face
      filename: "*FACE*"

  - name: Fingerprint Dataset 1
    flags:
      mode: finger
      input: data/finger
      attributes: "NFIQ2"
      query: "NFIQ2>40"
"""
