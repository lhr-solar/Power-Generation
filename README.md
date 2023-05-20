# Power-Generation

PCB designs, firmware, simulation and control software, and data models for the
LHR Solar Power Generation subteam are stashed here.

- [Power-Generation](#power-generation)
  - [Usage](#usage)
  - [Projects](#projects)
    - [Sunscatter](#sunscatter)
    - [PV Curve Tracer](#pv-curve-tracer)
    - [Blackbody](#blackbody)
    - [Sunspot](#sunspot)
    - [Eclipse](#eclipse)
    - [Models](#models)
    - [Data](#data)

---

## Usage

When cloning this repo, please use the `git clone --recurse-submodules
https://github.com/lhr-solar/Power-Generation.git` command. This will pull in
relevant subdependencies. Each project folder has their own README.md describing
usage and any relevant information.

---

## Projects

There are several projects contained in the power generation repo. They are
outlined below.

- Sunscatter
- PV Curve Tracer
- Blackbody
  - Blackbody A
  - Blackbody B
  - Blackbody C
- Sunspot
- Eclipse
- Models
- Data

### Sunscatter

Sunscatter is the maximum power point tracking (MPPT) board used for power
transformation and delivery from the solar array to the vehicle battery
management system. It consists of a microcontroller actuating a DC-DC boost
converter, armed with sensors to run a closed loop feedback control consisting
of both PID controllers and MPPT algorithms to optimize power delivery.

### PV Curve Tracer

The PV Curve Tracer is the measurement board used for characterizing solar cells,
modules, and arrays. It has the ability to capture the I-V and P-V curves of the
particular PV configuration and visualize it in real time on a user PC with
detailed measurements and statistics.

### Blackbody

Blackbody is a set of sensor boards for measuring the irradiance and temperature
of various parts of the solar array on the car. There are currently three
variants: **Blackbody A**, **Blackbody B**, and **Blackbody C**.

- **Blackbody A** measures both light sensors (TSL2591) and temperature sensors
  (RTDs). This board is installed into the solar vehicle for data collection and
  informing the operation of Sunscatter.

- **Blackbody B** manages a sole light sensor (TSL2591). It is primarily used
  for testing and normalization of solar cell/module/array results. It talks to
  the PV Curve Tracer.

- **Blackbody C** is breakout board of the light sensor (TSL2591) optimized for
  placement on the topshell on the solar vehicle. This board talks to Blackbody
  A during the race.

### Sunspot

Sunspot is a proposed laminator PCB used to automate the process of the solar
cells. It monitors temperature and vacuum pressure, and provides real-time
display of the temperature distribution experienced by the laminated cells.

### Eclipse

Eclipse is the name of the simulation, analysis, and control software written in
Python and Qt to optimize the design and assembly of the solar array. It has the
ability to model the power generation system, from the photovoltaic
configuration to the DC-DC converter and the MPPT algorithms. It also has the
ability to capture logs from the PV Curve Tracer and visualize them, presenting
detailed analysis of the photovoltaic being characterized.

The former functionality is used for simulating and testing novel MPPT
algorithms and the latter is used for binning and evaluating photovoltaic cells
and their assembled modules and arrays.

### Models

The Models repository contains python/cython models used for simulating and
characterizing the power generation system. It consists of the following
components:

- Environment (irradiance, temperature)
- Photovoltaics (cells, modules, arrays)
- MPPT (hardware and MPPT algorithms)
- Load (battery loads or elsewise)

Since these models are used in various parts of the system design process
(characterizing cell parameters, binning modules, simulating MPPT performance,
etc), it gets its own repository separate from Eclipse.

### Data

The Data repository contains relevant characterization and modeling data used
for Power Generation activities.