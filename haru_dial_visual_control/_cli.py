"""CLI."""

import click
from loguru import logger

from haru_dial_visual_control._phidget_manager import PhidgetDialSensorManager

@click.group()
def cli():
    pass


@cli.command()
def expressions():
    """Run haru expression control from cli."""
    logger.info("Test")
    sensor = PhidgetDialSensorManager()
    sensor.wait()
    

