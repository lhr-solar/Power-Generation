# Sunscatter Firmware

## Maintainer

- Matthew Yu

## Prerequisites

When first initializing this repo, please make sure the `mbed-os` library is in
`lib`. The current version is `6.15.1`. [Mbed
Studio](https://os.mbed.com/studio/) should also be installed.

## Building

When building this project, switch the open workspace to `src`. Mbed Studio will
not recognize that the projects exist without the program folder being at the
root of the workspace.

The appropriate target is the `NUCLEO-L432KC`. This is autopopulated if the
nucleo is plugged into the PC via a USB cable. On the first build, the compile
time will take a while.

An `mbed_app.json` can be added to the program folder. Additional options can be
specified, such as the UART baud rate or the printf precision. See the provided
`mbed_app.json` file in the src subfolders for details.

## Viewing UART/virtual COM serial output

Assuming the HW has the correct UART peripheral pins available to talk via the
USB-UART chip, Mbed Studio has a built in serial monitor for viewing any debug
output.

It is preferred to use PuTTy or a custom serial viewer, however, since the
serial monitor in Mbed Studio may time out after a certain amount of lines.

## Tests

In addition to the main, defined in `src/MPPT`, several test and
characterization programs have been created. They are noted briefly here.

- **Indicator Test**: tests LEDs on Sunscatter PCB.
- **CAN Test**: tests CAN peripheral and HW on Sunscatter PCB.
- **Sensor Test**: tests sensor HW and sensor calibration on Sunscatter PCB.
- **Step Response Test**: characterizes the transients for voltage and current
  across the DC-DC converter on the Sunscatter PCB.
- **(*UNDER CONSTRUCTION*)** **Boost Characterization Test**: Characterizes unloaded
  and loaded boost parameters of the DC-DC converter.
- **(*USE FOR ARRAY TESTING*)** **Voltage Sweep MPPT Test**: sweeps across the input
  source and sets a reference 
  at the PWM duty cycle that maximizes either efficiency or power transmission.
- **(*UNDER CONSTRUCTION*)** **MPPT**: main program for the Sunscatter PCB.
