# Floor Planner

## Overview

This is a drawing tool that produces floor plans. It is controlled through YAML config files and has no built-in GUI (only CLI is provided). Although it may look like a drawback, people with technical background may find it more convenient. Compared with drag-and-drop tools, config-based interface simplifies fine-grained control and allows versioning projects with VCSs like Git.

This is a fork of [renovation](https://github.com/Nikolay-Lysenko/renovation)
by Nikolay Lysenko, with additional features added by Krzysztof Bartczak:
- Constants and arithmetic expressions
- Room variables
- External YAML file support
- Floor plan reports
- Enhanced room options

The below figure demonstrates available elements.

![elements.png](https://github.com/krzysztofander/floor-planner/blob/master/examples/images/elements.png)

## Motivation
I needed some tool for drawing floor plans and other schematics.
There is plenty of free or paid drawing tools, but non of free was available offline such that I control the tool and the plans I create.
I found out the original module (base for this fork) but it turned out to be insufficient and difficult to use for bigger projects.

## Usage
Create Python virtual environment, download this module and install all requirements.

To generate floor plans, run:
```bash
python -m floor_planner -c /path/to/config.yml
```

To generate images of templates and other examples use make
```bash
make all
```

The module uses the config in YAML where properties of each element are set. These properties include location, orientation, size, color and so on.
There are also global properties that control appearance of some embedded elements line dimension lines, labels, room area, etc.

The section named `project` defines properties of output such as:
* Extension (multi-page PDF document, directory with PNG images, or both)
* Location
* DPI (dots-per-inch, resolution)

In the section named `default_layout`, below parameters are set for floor plans that do not override them in their `layout` sections:
* Dimensions of area to be drawn (in real-world meters, i.e., meters prior to scaling)
* Scale
* Grid settings

The sections named `default_options` and  `options` allows to modify options for floor plans
In this section it is possible to configure:
* Color of labels. Labels are not printed if color is not specified.
* Adding automatic dimensions to walls.
* Color of element's identifiers. Identifiers are not printed if their color is not specified.

The section named `constants` can be used to define variables that can be later used in definitions of elements.

The section named `reusable_elements` is designed to store arbitrary collections of elements that can be used by individual floor plans. Demo example uses it to define walls, windows, and doors.
Reusable elements can be loaded from separate YAML files. Please see the `examples`.

Finally, settings of individual floor plans are listed. These settings might include:
* Title
* Layout
* Report
* Names of element collections to reuse
* Extra elements for given floor
* Override of options

## Rooms
This fork adds a concept of rooms as an additional level of hierarchy.
Rooms have own `constants` and additionally `variables` where previously defined constants and variables can be used in arithmetic expressions.
Elements defined withing a room are anchored to the room anchor point. This give flexibility in moving or drawing a whole room as there is no longer need to pre-calculate anchor points of individual elements.
It is recommended to work with rooms instead of individual elements.
*Easiest start is to copy room and main project file from `examples/templates/rooms`*

## Capabilities
There are no build in limitations. With this module it is possible to draw a complex plans like below.
Use of rooms in separate YAML files, constants and variables helps in offsetting one peace to another and lets to simulate 'what if' in case one wonder if moving or making a wall or door in given place make sense.

![dom.png](https://github.com/krzysztofander/floor-planner/blob/master/examples/images/dom.png)
