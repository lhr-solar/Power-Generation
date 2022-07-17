# HOW TO TEST AND CHARACTERIZE THE HARDWARE

v1.0.0

## Testing instructions

In addition to the main, defined in `src/Sunscatter`, several test and
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
- **(*UNDER CONSTRUCTION*)** **Sunscatter**: main program for the Sunscatter PCB.

After building each program and loading them onto the Nucleo, the testing
instructions are as follows. 

---

### Indicator Test

Observe that each LED on the board not controlled by the presence of power
toggles in some sequence. This includes the onboard Nucleo LED. 

---

### CAN Test

Hook up the CAN circuitry with another PCB using the same CAN circuit. Make sure
CANH and CANL are connected to CANH and CANL, respectively. Make sure one device
is flashed with `__USER_ONE__` defined and the other without. This can be done
by commenting out the line `#define __USER_ONE__ 0`. 

The device with USER ONE defined will send `User 0 sent message <COUNTER>` and
the device with USER ONE undefined will send `User 1 send message COUNTER`. Each
should receive messages from the other with the response `Message received from
<ID>: <COUNTER>`. The counter from each side may be different, but they should
both increase incrementally. 

---

### Sensor Test

Hook up a power supply to the Array connector input of the PCB and determine
transformation functions for each sensor on the PCB. See
`/test_data/sunscatter_characterization/sunscatter_characterization.xlsx` for
detailed examples. 

---

#### Voltage Tuning

Apply voltage from 0 - 125V at the array connector. Leave the battery connector
open circuit. Keep the GATE signal LOW and the MOSFETs open. Measure the voltage
at the array and battery side, both with a high accuracy multimeter (+ARR|GND,
+BATT|GND) and with the internal ADCs. 

Record the values and build a mapping function (this is generally a linear
function with a upper cutoff) relating input voltage to observed measurement.
Make sure the transformation error is less than 1% for most inputs. 

---

#### Current Tuning

Apply current from 0 - 8A at the array connector. Make the battery connector
short circuit. Keep the GATE signal LOW and the MOSFETs open. Measure the
current at the array and battery side, both with a high accuracy multimeter
(-ARR|GND, -BATT|GND) and with the internal ADCs. 

Record the values and build a mapping function (this is generally a linear
function with a upper cutoff) relating input current to observed measurement.
Make sure the transformation error is less than 1% for most inputs. 

---

### Step Response Test

Hook up a power supply to the Array connector input of the PCB and determine the
transient response at the gate (GATE|GND) and across the schottky diodes
(+ARR|GND, +SNUB|-SNUB, +BATT|GND). See
`/test_data/sunscatter_characterization/sunscatter_characterization.xlsx` for
formatting. 

Trigger the PWM signal to drive the DRIVE_PWM signal up and down at a fixed
frequency (5 HZ). Observe the time series of the array and battery voltage to
record the transient response of the switching event, including: 
- rise time (ms)
- overshoot (V/V, % ratio of steady state voltage)
- ringing
- settling time (ms) 

Likewise observe the same transient response at the GATE signal.
Make sure that the overshoot ratio at the GATE is not greater than `TBD%` of the
steady state voltage. See TODO: [#1](https://github.com/lhr-solar/Power-Generation/issues/1). 

---

### Boost Characterization Test

Hook up a power supply to the array connector input of the PCB and vary the
following independent variables over time: 
- Source (max input current, max input voltage)
- Load (no load, x batteries at Y voltage, Z voltage, A voltage...)
- PWM frequency (20 - 30 kHz)
- % Duty cycle (0 - 99%)

Measure the boost ratio (+BATT:+ARR voltage), power transfer value (BATT power),
and power efficiency ratio (BATT power:ARR power). 

The ideal MPPT has a power efficiency ratio and power transfer value as high as
possible with a boost ratio closely at the bounds of the array input range and
battery output range.  

---

### Voltage Sweep MPPT Test

Hook up the array or power supply to the array connector and a load the output.
It should perform a successful voltage sweep MPPT algorithm and track to a
PWM/voltage setpoint that is either maximizing power transfer value 
(`#define __MODE__ __OPTIMIZE_POWER__`) or power efficiency ratio 
(`define __MODE__ __OPTIMIZE_EFF__`).
