/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com) and Roy Mor (roymor.102@gmail.com)
 * @brief Test main that implements a primitive voltage sweep MPPT algorithm to
 *        drive the v3.3.x MPPTs.
 * @version 1.1.0
 * @date 2022-06-04
 * 
 * @copyright Copyright (c) 2022
 * @note Set __MODE__ based on optimizer criteria. Set PCB versioning for
 * correct analog pinout and mapping. Set PWM_FREQ and SWEEP_ITER_DELAY for
 * voltage sweep characteristics.
 */

#include "mbed.h"

#define PCB_MAJOR_VERSION   3
#define PCB_MINOR_VERSION   3
#define PCB_PATCH_VERSION   0
#define BLINKING_RATE       500ms
#define __OPTIMIZE_POWER__  0
#define __OPTIMIZE_EFF__    1
#define __MODE__            __OPTIMIZE_POWER__
#define PWM_FREQ            21000
#define PWM_PERIOD          1000000 / PWM_FREQ
#define SWEEP_ITER_DELAY    50ms
#define POW_THRESHOLD       1 // in watts

static Ticker       tickSweepEvent;
#if PCB_MAJOR_VERSION == 3 && PCB_MINOR_VERSION == 2
    DigitalOut led(D13);    // STM32 Onboard LED
    AnalogIn   battery_i_sense(A3);
    AnalogIn   battery_v_sense(A4);
    AnalogIn   array_i_sense(A5);
    AnalogIn   array_v_sense(A6);
    PwmOut     pwm(A1);

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
    PwmOut     pwm(A1);

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
    PwmOut     pwm(A1);

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

static bool start_sweep = false;

/**
 * @brief Set the sweep event trigger.
 */
void set_sweep_event(void) {
    start_sweep = true;
}

/**
 * @brief Periodically sweep the array I-V curve, and picking an operating point
 * at either max power transfer or max efficiency.
 * 
 * @return int 
 */
int main() {
    printf("HI\n\r");
    /* Initiate a voltage sweep at 20% duty cycle. */
    tickSweepEvent.attach(&set_sweep_event, chrono::seconds(10));
    start_sweep = true;

    pwm.period_us(PWM_PERIOD);
    pwm.pulsewidth_us(0);

    float best_duty_cycle = 0.0;
    float best_power_ratio = 0.0;

    while (true) {
        float arr_voltage = arr_v_cal(array_v_sense.read());
        float arr_current = arr_i_cal(array_i_sense.read());
        float batt_voltage = bat_v_cal(battery_v_sense.read());
        float batt_current = bat_i_cal(battery_i_sense.read());

        if (start_sweep) {
            start_sweep = false;
            best_duty_cycle = 0.0;
            best_power_ratio = 0.0;
            /* Sweep from 0 to 99% duty cycle. */
            printf("SWEEP\n\r");
            for (float duty_cycle = 0.025; duty_cycle <= 0.975; duty_cycle += 0.025) {
                pwm.pulsewidth_us((1-duty_cycle) * PWM_PERIOD);
                ThisThread::sleep_for(SWEEP_ITER_DELAY);
                arr_voltage = arr_v_cal(array_v_sense.read());
                arr_current = arr_i_cal(array_i_sense.read());
                batt_voltage = bat_v_cal(battery_v_sense.read());
                batt_current = bat_i_cal(battery_i_sense.read());
                printf("DUTY: %f, INP: %f, %f %f, OUT: %f, %f, %f, Eff: %f\n\r", 
                    duty_cycle,
                    arr_voltage,
                    arr_current,
                    arr_voltage * arr_current,
                    batt_voltage,
                    batt_current,
                    batt_voltage * batt_current,
                    (batt_voltage * batt_current) / (arr_voltage * arr_current)
                );

                float power_sent = batt_voltage * batt_current;
#if __MODE__ == __OPTIMIZE_EFF__
                if (power_sent > POW_THRESHOLD) {
                    float power_ratio = batt_voltage * batt_current / arr_voltage * arr_current;
                    if (power_ratio > best_power_ratio) {
                        best_duty_cycle = duty_cycle;
                        best_power_ratio = power_ratio;
                    }
                }
#elif __MODE__ == __OPTIMIZE_POWER__
                if (power_sent > POW_THRESHOLD) {
                    if (power_sent > best_power_ratio) {
                        best_duty_cycle = duty_cycle;
                        best_power_ratio = power_sent;
                    }
                }
#endif
            }

            /* Set the best duty cycle for rest of the sweep time. */
            pwm.pulsewidth_us((1-best_duty_cycle) * PWM_PERIOD);
            printf("HOLD\n\r");
        } else {
            printf("DUTY: %f, INP: %f, %f %f, OUT: %f, %f, %f, Eff: %f\n\r", 
                best_duty_cycle,
                arr_voltage,
                arr_current,
                arr_voltage * arr_current,
                batt_voltage,
                batt_current,
                batt_voltage * batt_current,
                (batt_voltage * batt_current) / (arr_voltage * arr_current)
            );
            ThisThread::sleep_for(SWEEP_ITER_DELAY);
        }
    }
}

