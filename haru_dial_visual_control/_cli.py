"""CLI."""

import click
from loguru import logger

from haru_dial_visual_control._phidget_manager import PhidgetDialSensorManager
from haru_dial_visual_control._expression_ui import haru_expression_gui

@click.group()
def cli():
    pass


@cli.command()
def expressions():
    """Run haru expression control from cli."""
    # sensor = PhidgetDialSensorManager()
    # sensor.wait()
    haru_expression_gui()
    

