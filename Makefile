PYTHON = .venv/bin/python3

.PHONY: all examples room_templates clean

all:
	@echo "Run 'make examples' to generate example output"

examples: room_templates #todo: add building of all yml files in the example folders

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
$(ROOM_TEMPLATES_ROOT)/%/output/some_floor.png: $(ROOM_TEMPLATES_ROOT)/%/project_main.yml $(ROOM_TEMPLATES_ROOT)/%/*.yml
	@echo "Processing example: $*"
	$(PYTHON) -m renovation -c $<

# xxx
# --------------


# yyy
# --------------




# Clean generated outputs
clean:
	rm -f $(ROOM_TEMPLATE_OUTPUTS)

