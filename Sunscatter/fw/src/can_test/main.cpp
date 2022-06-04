/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com) and Roy Mor (roymor.102@gmail.com)
 * @brief Test main that tests the CAN hardware on the v3.3.0 MPPTs.
 * @version 0.1.0
 * @date 2022-05-07
 * 
 * @copyright Copyright (c) 2022
 * 
 */
#include <stdbool.h>
#include "mbed.h"

#define __LOOPBACK__ 0


#ifdef __LOOPBACK__
Ticker ticker;
CAN can(D10, D2);
char counter = 0;
bool flag = false;

/** Tell the main thread to send a message. */
void send() {
    if (!flag) {
        flag = true;
    }
}

/** This test sets up the CAN driver on the Nucleo and attempts to communicate with itself. */
int main() {
    ticker.attach(&send, 1);
    CANMessage msg;
    can.mode(CAN::LocalTest);
    
    while (true) {
        if (flag) {
            flag = false;
            if (can.write(CANMessage(1337, &counter, 1))) {
                counter++;
                printf("Message sent: %d\n", counter);
            } else {
                printf("Message not sent: %d\n", counter);
            }
        }

        if (can.read(msg)) {
            printf("Message received: %d\n", msg.data[0]);
        } else {
            printf("No message.\n");
            ThisThread::sleep_for(200);
        }
    }
}
#else
#define MODE 0
#if MODE == 0
const uint32_t CAN_ID = 0x01;
#elif MODE == 1
const uint32_t CAN_ID = 0x00;
#endif

Ticker ticker;
CAN can(D10, D2);
char counter = 0;
bool flag = false;

/** Tell the main thread to send a message. */
void send() {
    if (!flag) {
        flag = true;
    }
}

/** This test sets up the CAN driver on the Nucleo and attempts to communicate with another device. */
int main() {
    printf("main()\n");
    ticker.attach(&send, 1);
    CANMessage msg;
    
    while (true) {
        if (flag) {
            flag = false;
            if (can.write(CANMessage(CAN_ID, &counter, 1))) {
                counter++;
                printf("Message sent: %d\n", counter);
            } else {
                printf("Message not sent: %d\n", counter);
            }
        }

        if (can.read(msg)) {
            printf("Message received from %i: %d\n", msg.id, msg.data[0]);
        } else {
            printf("No message.\n");
            ThisThread::sleep_for(200);
        }
    }
}
#undef MODE
#endif

