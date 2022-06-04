/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com) and Roy Mor (roymor.102@gmail.com)
 * @brief Test main that implements a primitive voltage sweep MPPT algorithm to
 *        drive the v3.3.x MPPTs.
 * @version 0.1.0
 * @date 2022-06-04
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#include "mbed.h"

#define __OPTIMIZE_POWER__  0
#define __OPTIMIZE_EFF__    1
#define __MODE__            __OPTIMIZE_POWER__

#define PWM_FREQ            21000
#define PWM_PERIOD          1000000 / PWM_FREQ
#define SWEEP_ITER_DELAY    50ms
#define POW_THRESHOLD       1 // in watts

static Ticker       tickSweepEvent;
static AnalogIn     array_voltage(A3);
static AnalogIn     array_current(A4);
static AnalogIn     battery_voltage(A6);
static AnalogIn     battery_current(A5);
static DigitalOut   led1(D1);
static DigitalOut   led2(D0);
static PwmOut       pwm(A1);

static bool start_sweep = false;
void set_sweep_event(void) {
    start_sweep = true;
}

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
        float arr_voltage = array_voltage.read() * 114.108 + 0.006;
        float arr_current = array_current.read() * 8.114754;
        float batt_voltage = battery_voltage.read() * 168.97 + 0.067;
        float batt_current = battery_current.read() * 8.247;

        if (start_sweep) {
            start_sweep = false;
            best_duty_cycle = 0.0;
            best_power_ratio = 0.0;
            /* Sweep from 0 to 99% duty cycle. */
            printf("SWEEP\n\r");
            for (float duty_cycle = 0.025; duty_cycle <= 0.975; duty_cycle += 0.025) {
                pwm.pulsewidth_us((1-duty_cycle) * PWM_PERIOD);
                ThisThread::sleep_for(SWEEP_ITER_DELAY);
                arr_voltage = array_voltage.read() * 114.108 + 0.006;
                arr_current = array_current.read() * 8.114754; 
                batt_voltage = battery_voltage.read() * 168.97 + 0.067;
                batt_current = battery_current.read() * 8.247;
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

