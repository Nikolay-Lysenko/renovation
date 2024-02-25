[![PyPI version](https://badge.fury.io/py/renovation.svg)](https://pypi.org/project/renovation/)

# Renovation

## Overview

This is a drawing tool that produces floor plans needed to renovate an apartment.

Walls, doors, windows, and dimension arrows are supported. Some other elements can be composed of them. For example, in the next section it is shown how to draw ventilation duct and French balcony.

## Usage

To install a stable version, run:
```bash
pip install renovation
```

To generate floor plans, run:
```bash
python -m renovation -c /path/to/config.yml
```

Here, config in YAML is the place to define what to draw. Please look at a [demo example](https://github.com/Nikolay-Lysenko/renovation/blob/master/docs/demo_config.yml) to see details. With this demo config, below two images are created:

![floor_plan_with_dimensions](https://github.com/Nikolay-Lysenko/renovation/blob/master/docs/images/floor_plan_with_dimensions.png)

![floor_plan_without_dimensions](https://github.com/Nikolay-Lysenko/renovation/blob/master/docs/images/floor_plan_without_dimensions.png)
