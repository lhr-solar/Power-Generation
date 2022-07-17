# Sunscatter Firmware

This repository contains all relevant firmware and documentation files for the
Sunscatter MPPT FW.

A couple other important sections for programmers who are working with this
board are below. 

- [Repository Structure](#Repository-Structure)
- [Maintainers](#Maintainers)
- [Versioning](#Versioning)
- [Changes and Errata](#Changes-and-Errata)
- [List of TODOs](#TODO)

---

## Repository Structure
- **inc**: Includes additional files and libraries made by external sources,
  like MBED from ARM.
- **lib**: Includes additional files and libraries developed by internal sources.
- **src**: Includes all projects, including test programs. The main program is
  typicalnamed after the root directory name. E.g. Sunscatter.
- **documentation**: Contains documentation for building, flashing, testing, and
  characterizing the HW.
  - [IMPROVEMENT.md](documentation/IMPROVEMENT.md): Suggestions for improving
    the software, libraries, and/or tests.
  - [BUILDING.md](documentation/BUILDING.md): Instructions for installing all
    prerequisites and building the program. Also how to flash onto the board.
  - [TESTING.md](documentation/TESTING.md): Instructions for testing the board
    hardware (past the basic electrical tests found in
    pcb/documentation/ASSEMBLY_AND_TESTING.md) and characterizing the hardware. 

---

## Maintainers

The current maintainer of this project is Matthew Yu as of 07/15/2022. His email
is [matthewjkyu@gmail.com](matthewjkyu@gmail.com). 

Also a useful point of contact is Professor Gary Hallock, who advised Matthew
and worked with the several former senior design teams and solar car class
groups who developed this board.

Other contributors of this FW are as follows:
- Afnan Mir (v0.1.0)
- Roy Moore (v0.1.0)
- Gary Hallock (v0.1.0)
- And many others...

---

## Versioning

Each FW program has an internal version number located at the header. The
current FW version of the main program, `MPPT` is `0.1.0`. It is still in beta.
We use [semantic versioning](https://semver.org/) to denote between versions.

---

## Changes and Errata

### Release 0.1.0

- Initial formatting of the repository structure
- Added the following tests:
  - boost_characterization_test
  - can_test
  - indicator_test
  - sensor_test
  - step_response_test
  - voltage_sweep_mppt_test
- Added main program Sunscatter.
- Versioning for each test based on hardware revision.

---

## TODO
- [#1. Figure out switching node requirements on overshoot and ringing.](https://github.com/lhr-solar/Power-Generation/issues/1) 
- Add libraries for Sunscatter program.
- Update Sunscatter program to use on MPPT.
- Clean up Boost Characterization Test.
