# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.1] - 2026-11-05

### Added

* New element: labeled rectangle (e.g., for home appliances).

### Changed:

* Door sweep angles are introduced (and sweep arc appearance slightly changed because of this).
* Dependency management migrated from `requirements` to `uv`.
* Releases to PyPI are made with GitHub Actions.

## [0.2.0] - 2026-05-01

### Added

* An element can be anchored to another element up to a shift of its pivot point.
* An element can be anchored to a pair of other elements and, if so, length and/or orientation are also inferred.

### Changed

* Anchor point of an element is renamed to pivot point.
* For `Door` class, definition of pivot point is changed.

## [0.1.1] - 2025-01-03

### Added

* New elements: power outlet, electrical cable, text box, ceiling lamp, wall lamp, LED strip, switch, polygon.

### Changed

* `Door` is drawn with its frame.

## [0.1.0] - 2024-02-26

### Added

* Basic elements: wall, window, door, dimension arrow.
