"""
Test rendering end-to-end.

Author: Nikolay Lysenko
"""


import os

import numpy as np
import pytest
import yaml
from PIL import Image

from renovation.__main__ import main


@pytest.mark.parametrize(
    "path_to_input_yml, canonical_results_dir, expected_png_names",
    [
        (
            os.path.join("docs", "demo_configs", "all_elements.yml"),
            os.path.join("docs", "images"),
            ["individual_elements.png"]
        ),
        (
            os.path.join("docs", "demo_configs", "anchors.yml"),
            os.path.join("docs", "images"),
            ["floor_plan_with_anchored_elements.png"]
        ),
        (
            os.path.join("docs", "demo_configs", "simple_floor_plan.yml"),
            os.path.join("docs", "images"),
            ["floor_plan_without_dimensions.png", "floor_plan_with_dimensions.png"]
        ),
    ]
)
def test_main(
        monkeypatch, path_to_tmp_file: str, path_to_tmp_dir: str,
        path_to_input_yml: str, canonical_results_dir: str, expected_png_names: list[str]
) -> None:
    """Test `main` function end-to-end."""
    with open(path_to_tmp_file, 'w') as tmp_yml_file:
        with open(path_to_input_yml) as source_yml_file:
            for line in source_yml_file:
                if line == '  png_dir: "docs/images"\n':
                    line = f'  png_dir: "{path_to_tmp_dir}"\n'
                tmp_yml_file.write(line)

    monkeypatch.setattr("sys.argv", ["__main__", "-c", path_to_tmp_file])
    main()

    with open(path_to_input_yml) as yml_file:
        settings = yaml.load(yml_file, Loader=yaml.FullLoader)
    assert len(settings["floor_plans"]) == len(expected_png_names)
    for floor_plan, expected_png_name in zip(settings["floor_plans"], expected_png_names):
        rendered_png_path = os.path.join(path_to_tmp_dir, f'{floor_plan["title"]["text"]}.png')
        rendered_png_array = np.array(Image.open(rendered_png_path))
        expected_png_path = os.path.join(canonical_results_dir, expected_png_name)
        expected_png_array = np.array(Image.open(expected_png_path))
        share_of_mismatched_elements = (rendered_png_array != expected_png_array).mean()
        assert share_of_mismatched_elements <= 1e-5
