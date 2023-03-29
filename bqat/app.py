import json
from pathlib import Path

import click
import pendulum
import yaml
from rich import print
from rich.console import Console
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn
from rich.text import Text

from bqat import __version__ as version
from bqat.models import JobConfiguration, RuntimeConfiguration
from bqat.utils import CONFIG_TEMPLATE, do_job, get_runtime_info


@click.command()
@click.option(
    "--yml",
    "-Y",
    default="./config.yaml",
    help="Specify path to configuration YAML file.",
)
@click.option(
    "--template",
    "-T",
    is_flag=True,
    default=False,
    help="Request a template of configuration file.",
)
@click.option(
    "--verbose",
    "-V",
    is_flag=True,
    default=True,
    help="Display detail info.",
)
def run(yml, template, verbose):
    if template:
        output = Path("config_template.yaml")
        output.write_text(CONFIG_TEMPLATE)
        print(f"\nTemplate config file generated at: {str(output)}.\n")
        return

    console = Console()
    title = Text("")
    title.append(f"\nWelcome to Biometric Quality Assessment Tool", style="bold dark_red")
    title.append(f" ")
    title.append(f"v{version}\n", style="italic underline")
    console.print(title)

    file = Path(yml)
    if not file.exists():
        print("Please specify YAMl configuration file.")
        return

    try:
        if verbose:
            print("\n>>> Runtime info:")
        info = get_runtime_info()
        if verbose:
            Console().print_json(json.dumps(info))
    except Exception as e:
        print(f"Fail to detect Docker engine: {str(e)}")
        return

    try:
        with open(file) as f:
            config = yaml.safe_load(f)
        runtime = RuntimeConfiguration(**config.get("runtime"))
        job_queue = config["job"]
    except Exception as e:
        print(f"Invalid YAMl configuration file: {str(e)}")
        return

    if verbose:
        print("\n>>> Job config:")
        Console().print_json(json.dumps(runtime))
        print("\n>>> Job queue:")
        Console().print_json(json.dumps(job_queue))

    volume = Path(runtime.volume)
    if not volume.exists():
        volume.mkdir(parents=True, exist_ok=True)
        print(f"Input folder mounted at: {str(volume)}. Put files in it and restart.")
        return

    print(f"\n>>> Start: {pendulum.now()}")

    with Progress(
        SpinnerColumn(), MofNCompleteColumn(), *Progress.get_default_columns()
    ) as p:
        job_progress = p.add_task("[orange]Running...", total=len(job_queue))
        for job in job_queue:
            print(f"\n>> {job.get('name', 'No name')}")
            job = JobConfiguration(**job)
            do_job(runtime, job)
            p.update(job_progress, advance=1)

    print(f"\n>>> End: {pendulum.now()}")
