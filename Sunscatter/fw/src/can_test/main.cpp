/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com) and Roy Mor (roymor.102@gmail.com)
 * @brief Test main that tests the CAN hardware on the v3.3.0 MPPTs.
 * @version 1.1.0
 * @date 2022-06-04
 * @copyright Copyright (c) 2022
 * @note Leave _LOOPBACK__ commented in to do loopback mode. Leave __USER_ONE__
 * commented in to transmit can_id = 0x0. Comment __USER_ONE__ out to transmit
 * can_id = 0x01.
 */
#include "mbed.h"

#define PCB_MAJOR_VERSION   3
#define PCB_MINOR_VERSION   3
#define PCB_PATCH_VERSION   1
#define BLINKING_RATE       500ms
// #define __LOOPBACK__        0
#define __USER_ONE__        0


Ticker ticker;
CAN can(D10, D2);           // D2 (TX), D10 (RX)
DigitalOut led(D13);        // STM32 Onboard LED
char counter = 0;
bool flag = false;

/**
 * @brief Tell the main thread to send a message and toggle the LED.
 */
void send() {
    led = !led;
    if (!flag) {
        flag = true;
    }
}

/**
 * @brief Communicate with itself or another PCB via CAN.
 * 
 * @return int 
 */
int main() {
    ticker.attach(&send, 1000us);
    CANMessage msg;

#ifdef __LOOPBACK__
    can.mode(CAN::LocalTest);
#endif

#ifdef __USER_ONE__
    const uint32_t can_id = 0x00;
#else
    const uint32_t can_id = 0x01;
#endif

    while (true) {
        if (flag) {
            flag = false;
            if (can.write(CANMessage(can_id, &counter, 1))) {
                ++counter;
                printf("User %i sent message: %d\n", can_id, counter);
            } else {
                printf("No message sent.\n");
            }
        }

        if (can.read(msg)) {
            printf("Message received from %i: %d\n", msg.id, msg.data[0]);
        } else {
            printf("No message received.\n");
            ThisThread::sleep_for(200ms);
        }
    }

    return 0;
}
