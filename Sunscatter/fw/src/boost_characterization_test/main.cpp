/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com) and Roy Mor (roymor.102@gmail.com)
 * @brief Test main that looks at boost characteristics for a given set of input parameters. 
 * @version 0.1
 * @date 2022-05-07
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#include "mbed.h"

#define PWM_FREQ 21000
#define PWM_PERIOD 1000000/PWM_FREQ

AnalogIn   arrayVoltage(A3);
AnalogIn   arrayCurrent(A4);
AnalogIn   batteryVoltage(A6);
AnalogIn   batteryCurrent(A5);
DigitalOut led1(D11);
DigitalOut led2(D12);
PwmOut pwm(A1);

Timer t;
CircularBuffer<float, 10> stable;
bool isStable = false;


float stdDev(float lastTen[]) {
    float sum = 0.0;
    for(int i = 0; i < 10; i++) {
        sum = sum + (100*lastTen[i]);
    }
    float avg = sum/10;
    sum = 0.0;
    for(int i = 0; i < 10; i++) {
        sum = sum + (100*lastTen[i]-avg)*(100*lastTen[i]-avg);
    }
    return sqrt(sum / 9);
}

int main() {
    float minDutyCycle = 0.0;
    float maxDutyCycle = 0.9;
    
    pwm.write(1-minDutyCycle);
    ThisThread::sleep_for(10s);
    pwm.write(1-maxDutyCycle);
    t.start();

    int timerCurrent;
    int timerPrev = t.elapsed_time().count();
    //float mean;
    float temp;
    float lastTen[10];
    float stdDevi;
    while(!isStable) {
        timerCurrent = t.elapsed_time().count();
        if(timerCurrent-timerPrev>=1) {
            stable.push(batteryVoltage.read()*168.97+0.067);
        }
        timerPrev = timerCurrent;
        if(stable.full()) {
            for(int i = 0; i < 10; i++) {
                stable.pop(temp);
                lastTen[i] = temp;
                //mean += temp;
            }
            //mean /= 10;
            stdDevi = stdDev(lastTen);
            if(stdDevi<=.05&&stdDevi>=-.05) {
                isStable = true;
            }
        }
    }
    t.stop();

    printf("Duration: %lldl", t.elapsed_time().count());
    while (1);
}