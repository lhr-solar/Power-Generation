"""
@file:      profile.py
@author:    Matthew Yu (matthewjkyu@gmail.com)
@brief:     Generates a n-d base of data to extrapolate DC-DC converter
            characteristics. 
@version    0.1.0
@requirements: Python 3, matplotlib
@date:      2022-05-20
@copyright: Copyright (c) 2022.
@note:      Anticipated testing range.

Frequency:
    20 - 30 kHz, 1 khz steps                    (11 iterations)
    0 - 100% duty cycle, 5% steps               (21 iterations)
    0 - 120 V input voltage, 15V steps          (9 iterations)
    0 - 8 A input current, 1A steps             (9 iterations)
    0 - 150 V output voltage load, 15V steps    (11 iterations, 0V is no load)

@note:      Desired output values per iteration. Model every iteration as a step
            response. (PWM = 0% duty cycle, to expected input voltage,
            duty cycle)
            
    - input freq
    - input duty cycle
    - input voltage
    - input current
    
    - Output voltage change (V): absolute voltage change from 0% duty cycle
      (output voltage ~= input voltage) to a given duty cycle after steady state
      is reached.
      
    - Output voltage boost ratio (unitless): ratio of output voltage to input
      voltage after steady state is reached.

    - Overshoot (unitless): ratio of maximum output voltage to steady state
      output voltage.
    
    - Rise time (us): time taken for the output to go from 0% to 100% (first hit) of
      steady state output voltage.
      
    - Settling time 1 (us): time taken for the output to go from 0% to 100% (ringing
      goes to within 5% of steady state output voltage) of steady state output
      voltage. 
      
    - Settling time 2 (us): time taken for the output to go from 0% to 100% (ringing
      goes to within 1% of steady state output voltage) of steady state output
      voltage.
      
    - Ringing frequency (hz): ringing frequency at overshoot/undershoot.

    - Power transfer ratio: ratio of output power versus input power. Efficiency
      metric.
"""
import sys
import csv
import argparse
import matplotlib.pyplot as plt

MIN_FREQ = 20000
MAX_FREQ = 30000
FREQ_STEP = 1000

MIN_DUTY = 0
MAX_DUTY = 100
DUTY_STEP = 5

MIN_INPV = 0
MAX_INPV = 120
INPV_STEP = 15

MIN_INPC = 0
MAX_INPC = 8
INPC_STEP = 1

MIN_OUTV = 0
MAX_OUTV = 150
OUTV_STEP = 15

header = [
    'freq (hz)', 
    'duty cycle (%)', 
    'inp voltage (V)', 
    'inp current (A)', 
    'load voltage (V)', 
    'output voltage (V)',
    'boost ratio',
    'rise time (us)',
    'settling time 5% (us)',
    'settling time 1% (us)',
    'ringing frequency (hz)',
    'power transfer ratio'
]

def generate_db():
    data = []
    
    # Build empty file for expected testing range.
    for freq in range(MIN_FREQ, MAX_FREQ+FREQ_STEP, FREQ_STEP):
        for duty_cycle in range(MIN_DUTY, MAX_DUTY+DUTY_STEP, DUTY_STEP):
            for inp_voltage in range(MIN_INPV, MAX_INPV+INPV_STEP, INPV_STEP):
                for inp_current in range(MIN_INPC, MAX_INPC+INPC_STEP ,INPC_STEP):
                    for out_voltage in range(MIN_OUTV, MAX_OUTV+OUTV_STEP, OUTV_STEP):
                        list = [None] * len(header)
                        list[0] = freq
                        list[1] = duty_cycle
                        list[2] = inp_voltage
                        list[3] = inp_current
                        list[4] = out_voltage
                        data.append(list)

    with open("MPPT_v3_3_0_dc_dc_characteristics.csv", "w", encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        
def parse_db():
    pass

def parse_csv(file_path):
    with open(file_path, "r") as read_file:
        with open("log.csv", "w", encoding='UTF8', newline='') as write_file:
            writer = csv.writer(write_file)
            freq = []
            duty = []
            inp_v = []
            inp_c = []
            out_v = []
            out_c = []
            while True:
                line = read_file.readline()
                if line:
                    line = line.strip().split(',')
                    line = [el.strip() for el in line]
                    try:
                        if len(line) == 6 and int(line[0]) in (20000, 21000, 22000, 23000, 24000, 25000):
                            el_freq = float(line[0])
                            el_duty = float(line[1])
                            el_inp_v = float(line[2])
                            el_inp_c = float(line[3])
                            el_out_v = float(line[4])
                            el_out_c = float(line[5])
                            freq.append(el_freq)
                            duty.append(el_duty)
                            inp_v.append(el_inp_v)
                            inp_c.append(el_inp_c)
                            out_v.append(el_out_v)
                            out_c.append(el_out_c)
                            writer.writerow([el_freq, el_duty, el_inp_v, el_inp_c, el_out_v, el_out_c])

                    except:
                        pass
                else:
                    break


            x = {}
            freq_lut = {
                20000 : 0.000,
                21000 : 0.005,
                22000 : 0.01,
                23000 : 0.015,
                24000 : 0.02,
                25000 : 0.025
            }
            for i in range(len(freq)):
                if freq[i] not in x:
                    x[freq[i]] = {"duty":[], "v_in":[], "v_out":[], "p_in":[], "p_out":[], "p_eff":[]}
                x[freq[i]]["duty"].append(duty[i] + freq_lut[freq[i]])
                x[freq[i]]["v_in"].append(inp_v[i])
                x[freq[i]]["v_out"].append(out_v[i])
                x[freq[i]]["p_in"].append(inp_v[i]*inp_c[i])
                x[freq[i]]["p_out"].append(out_v[i]*out_c[i])
                if (inp_v[i] * inp_c[i]) == 0:
                    x[freq[i]]["p_eff"].append(0)
                else:
                    x[freq[i]]["p_eff"].append((out_v[i]*out_c[i])/(inp_v[i]*inp_c[i]))
            # fig, ax = plt.subplots(len(x.keys()))
            for index, key in enumerate(x.keys()):
                plt.scatter(x[key]["duty"], x[key]["v_in"], s=1, label=f"v_in, {key}Hz")
                plt.scatter(x[key]["duty"], x[key]["v_out"], s=1, label=f"v_out, {key}Hz")
                # ax[index].scatter(x[key]["duty"], x[key]["p_eff"], s=1, label=f"p_eff, {key}")
                # ax[index].legend(loc='upper left')
                # ax[index].set_xlim([0, 1])
                # ax[index].set_ylim([0, 1])
                
                # plt.scatter(x[key]["duty"], x[key]["p_eff"], s=1, label=f"p_eff, {key}")
                plt.legend(loc='upper left')
                plt.xlim([0, 1])
                plt.ylim([0, 250])
            plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populating the DC-DC converter characteristics table.")
    parser.add_argument('--generate_db', default=False, action="store_true", help="Set --generate_db to regenerate the db with the constants defined above.")
    parser.add_argument('--parse_db', default=False, action="store_true", help="Set --parse_db to display DC-DC characteristics.")
    parser.add_argument('--save_characteristic_images')
    parser.add_argument('--parse_csv')
    args = parser.parse_args()
    
    if args.generate_db:
        generate_db()
    
    if args.parse_db:
        """
        Display N graphs:

        """
        pass

    if args.save_characteristic_images:
        pass
    
    if args.parse_csv:
        parse_csv(args.parse_csv)