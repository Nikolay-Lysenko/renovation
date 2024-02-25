"""
Render project.

Author: Nikolay Lysenko
"""


import argparse

import yaml

from renovation.elements import create_elements_registry
from renovation.floor_plan import FloorPlan
from renovation.project import Project


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Rendering of renovation project floor plans.')
    parser.add_argument(
        '-c', '--config_path', type=str, default=None, help='path to configuration file'
    )
    cli_args = parser.parse_args()
    return cli_args


def main() -> None:
    """Parse CLI arguments and run requested tasks."""
    cli_args = parse_cli_args()
    config_path = cli_args.config_path
    with open(config_path) as config_file:
        settings = yaml.load(config_file, Loader=yaml.FullLoader)
    elements_registry = create_elements_registry()

    floor_plans = []
    for floor_plan_params in settings['floor_plans']:
        layout_params = floor_plan_params.get('layout') or settings['default_layout']
        floor_plan = FloorPlan(**layout_params)
        title_params = floor_plan_params.get('title')
        if title_params:
            floor_plan.add_title(**title_params)
        for set_name in floor_plan_params.get('inherited_elements', []):
            for element_params in settings['reusable_elements'].get(set_name, []):
                element_class = elements_registry[element_params.pop('type')]
                floor_plan.add_element(element_class(**element_params))
        for element_params in floor_plan_params.get('elements', []):
            element_class = elements_registry[element_params.pop('type')]
            floor_plan.add_element(element_class(**element_params))
        floor_plans.append(floor_plan)

    project = Project(floor_plans, settings['project']['dpi'])
    pdf_path = settings['project'].get('pdf_file')
    if pdf_path is not None:
        project.render_to_pdf(pdf_path)
    png_path = settings['project'].get('png_dir')
    if png_path is not None:
        project.render_to_png(png_path)


if __name__ == '__main__':
    main()
