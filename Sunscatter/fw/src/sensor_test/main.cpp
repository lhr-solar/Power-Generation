/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Test main that captures measures the various sensors on the Sunscatter PCB.
 * @version 1.1.0
 * @date 2022-06-04
 * @copyright Copyright (c) 2022
 * @note Set PWM_VALUE to 0 or 1 based on whether gate is open or shorted.
 * Mapping depends on PCB version and actual hardware (some gate drivers are
 * inverted).
 * Set PCB versioning for correct analog pinout and mapping.
 */
#include "mbed.h"

#define PCB_MAJOR_VERSION   3
#define PCB_MINOR_VERSION   3
#define PCB_PATCH_VERSION   0
#define BLINKING_RATE       500ms
#define PWM_VALUE           0

#if PCB_MAJOR_VERSION == 3 && PCB_MINOR_VERSION == 2
    DigitalOut led(D13);    // STM32 Onboard LED
    AnalogIn   battery_i_sense(A3);
    AnalogIn   battery_v_sense(A4);
    AnalogIn   array_i_sense(A5);
    AnalogIn   array_v_sense(A6);
    DigitalOut pwm(A1);

    float arr_v_cal(float inp) {
        float out = inp;
        return out;
    }

    float arr_i_cal(float inp) {
        float out = inp;
        return out;
    }

    float bat_v_cal(float inp) {
        float out = inp;
        return out;
    }

    float bat_i_cal(float inp) {
        float out = inp;
        return out;
    }

#elif PCB_MINOR_VERSION == 3 && PCB_MINOR_VERSION == 3 && PCB_PATCH_VERSION == 0
    DigitalOut led(D13);    // STM32 Onboard LED
    AnalogIn   battery_i_sense(A3);
    AnalogIn   battery_v_sense(A4);
    AnalogIn   array_v_sense(A5);
    AnalogIn   array_i_sense(A6);
    DigitalOut pwm(A1);

    float arr_v_cal(float inp) {
        float out = inp * 114.108 + 0.006;
        return out;
    }

    float arr_i_cal(float inp) {
        float out = inp * 8.114754;
        return out;
    }

    float bat_v_cal(float inp) {
        float out = inp * 168.97 + 0.067;
        return out;
    }

    float bat_i_cal(float inp) {
        float out = inp * 8.247;
        return out;
    }

#elif PCB_MINOR_VERSION == 3 && PCB_MINOR_VERSION == 3 && PCB_PATCH_VERSION == 1
    DigitalOut led(D13);    // STM32 Onboard LED
    AnalogIn   array_v_sense(A3);
    AnalogIn   array_i_sense(A4);
    AnalogIn   battery_i_sense(A5);
    AnalogIn   battery_v_sense(A6);
    DigitalOut pwm(A1);

    float arr_v_cal(float inp) {
        float out = inp;
        return out;
    }

    float arr_i_cal(float inp) {
        float out = inp;
        return out;
    }

    float bat_v_cal(float inp) {
        float out = inp;
        return out;
    }

    float bat_i_cal(float inp) {
        float out = inp;
        return out;
    }

#endif

/**
 * @brief Read from each analog voltage and current sensor on the PCB. Check for
 * offset and gain error and calibrate the sensors. 
 * 
 * @return int 
 */
int main() {
    pwm = PWM_VALUE;

    printf("UNCAL ARRV | ARRC | BATV | BATC || CAL ARRV | ARRC | BATV | BATC\n");
    while (true) {
        led = !led;
        
        /* print the raw [0, 1.0] value and calibrated value (V, A). */
        float arr_v = array_v_sense.read();
        float arr_i = array_i_sense.read();
        float bat_v = battery_v_sense.read();
        float bat_i = battery_i_sense.read();
        printf(
            "%f | %f | %f | %f || %f | %f | %f | %f\n",
            arr_v, arr_i, bat_v, bat_i,
            arr_v_cal(arr_v),
            arr_i_cal(arr_i),
            bat_v_cal(bat_v),
            bat_i_cal(bat_i));

        ThisThread::sleep_for(BLINKING_RATE);
    }

    return 0;
}
