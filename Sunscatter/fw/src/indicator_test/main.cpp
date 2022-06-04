/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Indicator test tests the various LEDs on the Sunscatter PCB.
 * @version 1.0.0
 * @date 2022-06-04
 * @copyright Copyright (c) 2022
 * @note Set PCB versioning for correct LED pinout and mapping.
 */

#include "mbed.h"

#define PCB_MAJOR_VERSION   3
#define PCB_MINOR_VERSION   3
#define PCB_PATCH_VERSION   1
#define BLINKING_RATE       500ms


#if PCB_MAJOR_VERSION == 3 && PCB_MINOR_VERSION == 2        /* Versions 3.2.x */
    #define NUM_LEDS 7
    DigitalOut leds[NUM_LEDS] = {
        DigitalOut(D2),     // CAN TX LED
        DigitalOut(D9),     // BPS FULL LED
        DigitalOut(D10),    // CAN RX LED
        DigitalOut(D11),    // TRACKING LED
        DigitalOut(D12),    // ERROR LED
        DigitalOut(D13),    // STM32 Onboard LED
        DigitalOut(A1),     // PWM LED
    };

#elif PCB_MINOR_VERSION == 3 && PCB_MINOR_VERSION == 3      /* Versions 3.3.x */
    #define NUM_LEDS 7
    DigitalOut leds[NUM_LEDS] = {
        DigitalOut(D0),     // TRACKING LED
        DigitalOut(D1),     // HEARTBEAT LED
        DigitalOut(D2),     // CAN TX LED
        DigitalOut(D3),     // ERROR LED
        DigitalOut(D10),    // CAN RX LED
        DigitalOut(D13),    // STM32 Onboard LED
        DigitalOut(A1),     // PWM LED
    };

#else
    #define NUM_LEDS 1
    DigitalOut leds[NUM_LEDS] = {
        DigitalOut(LED1)    // STM32 Onboard LED
    };

#endif

/**
 * @brief Toggle all the supported LEDs on the board at a fixed blinking rate.
 * 
 * @return int 
 */
int main() {
    while (true) {
        for (uint8_t i = 0; i < NUM_LEDS; ++i) {
            leds[i] = !leds[i];
            ThisThread::sleep_for(BLINKING_RATE);
        }
    }

    return 0;
}
