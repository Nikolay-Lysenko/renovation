PYTHON = .venv/bin/python3
PYSRC = $(wildcard floor_planner/*.py)
PYSRC += $(wildcard floor_planner/elements/*.py)

.PHONY: all clean room_templates playground elements simple

all: room_templates elements playground simple

# ==========================================

# ROOM TEMPLATES
# --------------
## Root directory for room templates
ROOM_TEMPLATES_ROOT = examples/templates/rooms
## List of room template folders
ROOM_TEMPLATES = room_north room_south room_east room_west play_with_doors

## Generate paths for each room template
ROOM_TEMPLATE_MAINS = $(foreach ex,$(ROOM_TEMPLATES),$(ROOM_TEMPLATES_ROOT)/$(ex)/project_main.yml)
ROOM_TEMPLATE_OUTPUTS = $(foreach ex,$(ROOM_TEMPLATES),$(ROOM_TEMPLATES_ROOT)/$(ex)/output/some_floor.png)

# Main target to build all room templates
room_templates: $(ROOM_TEMPLATE_OUTPUTS)

# Pattern rule: build output for each example by processing its project_main.yml
$(ROOM_TEMPLATES_ROOT)/%/output/some_floor.png: $(ROOM_TEMPLATES_ROOT)/%/project_main.yml $(ROOM_TEMPLATES_ROOT)/%/*.yml $(PYSRC)
	@echo "Processing $<"
	$(PYTHON) -m floor_planner -c $<

# INDIVIDUAL ELEMENTS
# -------------------
ELEMENTS_PNG = examples/elements/Individual\ elements.png
elements: $(ELEMENTS_PNG)

$(ELEMENTS_PNG): examples/elements/all_elements.yml $(PYSRC)
	@echo "Processing $<"
	$(PYTHON) -m floor_planner -c $<

# PLAYGROUND
# ----------
DOORS_AND_WINDOWS_PNG = examples/playground/Doors\ and\ windows.png
playground: $(DOORS_AND_WINDOWS_PNG)

$(DOORS_AND_WINDOWS_PNG): examples/playground/doors_and_windows.yml $(PYSRC)
	@echo "Processing $<"
	$(PYTHON) -m floor_planner -c $<

#OTHER
#-----
SIMPLE_PNG = examples/simple_no_rooms/Plain\ floor\ plan.png
simple: $(SIMPLE_PNG)

$(SIMPLE_PNG): examples/simple_no_rooms/simple_floor_plan.yml $(PYSRC)
	@echo "Processing $<"
	$(PYTHON) -m floor_planner -c $<


# Clean generated outputs
clean:
	rm -f $(ROOM_TEMPLATE_OUTPUTS)
	rm -f $(ELEMENTS_PNG)
	rm -f $(DOORS_AND_WINDOWS_PNG)
	rm -f $(SIMPLE_PNG)

