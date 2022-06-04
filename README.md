# Power-Generation
PCB designs, simulation software, and firmware for LHR Solar Power Generation
subteam are stashed here.

## Usage

When cloning this repo, please use the `git clone --recurse-submodules
https://github.com/lhr-solar/Power-Generation.git` command. This will pull in
relevant subdependencies.

### Dependencies

The firmware uses `Mbed OS 6.15.1`. These are indicated as git submodules in the
`fw/lib` folders of each project. If `fw/lib/mbed-os` does not exist in the
repo or is empty, call `git submodule init` and `git submodule update` to populate it.


## Projects

There are several projects contained in the power generation repo. They are outlined below.

### Blackbody
Blackbody is a sensor board for measuring the irradiance and temperature of
various parts of the solar array on the car. There are currently three variants:
Blackbody A, Blackbody B, and Blackbody C.

- **Blackbody A**: This sensor board measures both light sensors (TSL2591) and
  temperature sensors (RTDs). This board is installed into the solar vehicle
  for data collection and informing the operation of Sunscatter, the MPPT.

- **Blackbody B**: This sensor board manages a sole light sensor (TSL2591). It is
  primarily used for testing and normalization of solar cell/module/array
  results. It talks to the Curve Tracer board.

- **Blackbody C**: This sensor board is breakout board of the light sensor
  (TSL2591) optimized for placement on the topshell on the solar vehicle. This
  board talks to Blackbody A during the race.

### Curve Tracer
Curve Tracer is the measurement board used for characterizing solar cells,
modules, and arrays. It has the ability to capture the I-V and P-V curves of the
particular PV configuration and visualize it in real time on a user PC with
detailed measurements.

### Sunscatter
Sunscatter is the maximum power point tracking (MPPT) board used for power
transformation and delivery from the solar array to the vehicle battery
management system.

### Eclipse
Eclipse is the name of the simulation and analysis software written in Python to
optimize the design and assembly of the power generation system. It has the
ability to model the power generation system, from the photovoltaic
configuration to the DC-DC converter and the MPPT algorithms. It also has the
ability to capture logs from the Curve Tracer and visualize them, presenting
detailed analysis of the PV being characterized.

The former functionality is used for simulating and testing novel MPPT
algorithms and the latter is used for binning and evaluating photovoltaic cells
and their assembled modules and arrays.
