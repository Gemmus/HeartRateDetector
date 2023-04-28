from piotimer import Piotimer as Timer
from ssd1306 import SSD1306_I2C
from machine import Pin, ADC, I2C, PWM
from fifo import Fifo
import utime
import array
import time

                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                      GPIO                        #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#


# ADC-converter
adc = ADC(26)

# OLED
i2c = I2C(1, scl = Pin(15), sda = Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# LEDs
led_onboard = Pin("LED", Pin.OUT)
led21 = PWM(Pin(21))
led21.freq(1000)
#led = [20, 21, 22]
#list_of_led = []
#for x in range(0,3):
#    list_of_led.append(PWM(Pin(led[x])))
#    list_of_led[x].freq(1000)

# Rotary Encoder
rot_push = Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)
rota = Pin(10, mode = Pin.IN, pull = Pin.PULL_UP)
rotb = Pin(11, mode = Pin.IN, pull = Pin.PULL_UP)


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                     FREQUENCY                    #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#
                                                
# Sample Rate, Buffer
samplerate = 250
samples = Fifo(32)


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                  GLOBAL VARIABLES                #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

# Menu selection variables and switch filtering
mode = 0
count = 0
switch_state = 0

                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                     FUNCTIONS                    #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

########################################
#   Functions for reading the signal   #
########################################
def read_adc(tid):
    x = adc.read_u16()
    samples.put(x)
    
#############################################
#   Functions for displaying welcome text   #
#############################################
def welcome_text():
    oled.fill(1)
    i = 0
    h = 0
    for i in range(8):
        oled.pixel(5+h, 3, 0)
        oled.pixel(9+h, 3, 0)
        oled.pixel(5+h, 54, 0)
        oled.pixel(9+h, 54, 0)
    
        oled.line(4+h, 4, 6+h, 4, 0)
        oled.line(4+h, 55, 6+h, 55, 0)

        oled.line(8+h, 4, 10+h, 4, 0)
        oled.line(8+h, 55, 10+h, 55, 0)

        oled.line(3+h, 5, 11+h, 5, 0)
        oled.line(3+h, 56, 11+h, 56, 0)

        oled.line(4+h, 6, 10+h, 6, 0)
        oled.line(4+h, 57, 10+h, 57, 0)

        oled.line(5+h, 7, 9+h, 7, 0)
        oled.line(5+h, 58, 9+h, 58, 0)

        oled.line(6+h, 8, 8+h, 8, 0)
        oled.line(6+h, 59, 8+h, 59, 0)

        oled.pixel(7+h, 9, 0)
        oled.pixel(7+h, 60, 0)
        
        i += 1
        h += 16

    oled.text("Welcome to", 26, 17, 0)
    oled.text("Group 5's", 29, 27, 0)
    oled.text("project!", 33, 37, 0)
    oled.show()
    utime.sleep_ms(3750)

#######################################################
#   Functions to display press to start measurement   #
#######################################################
def press_to_start():
    oled.fill(0)
    oled.text("Press to start", 4, 7, 1)
    oled.text("the measurement", 4, 17, 1)

    oled.line(45, 53, 60, 53, 1)
    oled.line(60, 53, 63, 50, 1)
    oled.line(63, 50, 66, 53, 1)
    oled.line(66, 53, 68, 53, 1)
    oled.line(68, 53, 70, 57, 1)
    oled.line(70, 57, 73, 31, 1)
    oled.line(73, 31, 76, 64, 1)
    oled.line(76, 64, 78, 53, 1)
    oled.line(78, 53, 80, 53, 1)
    oled.line(80, 53, 84, 47, 1)
    oled.line(84, 47, 88, 53, 1)
    oled.line(88, 53, 89, 53, 1)
    oled.line(89, 53, 91, 51, 1)
    oled.line(91, 51, 93, 53, 1)
    oled.line(93, 53, 124, 53, 1)
    oled.line(118, 48, 124, 53, 1)
    oled.line(118, 58, 124, 53, 1)
    oled.show()
    

                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #         Functions for HRV calculations           #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

###########################
#   Mean PPI Calculator   #
###########################
def meanPPI_calculator(data):
    sumPPI = 0 
    for i in data:
        sumPPI += i
    rounded_PPI = round(sumPPI/len(data), 0)
    return int(rounded_PPI)

##########################
#   Mean HR Calculator   #
##########################
def meanHR_calculator(meanPPI):
    rounded_HR = round(60*1000/meanPPI, 0)
    return int(rounded_HR)

#######################
#   SDNN Calculator   #
#######################
def SDNN_calculator(data, PPI):
    summary = 0
    for i in data:
        summary += (i-PPI)**2
    SDNN = (summary/(len(data)-1))**(1/2)
    rounded_SDNN = round(SDNN, 0)
    return int(rounded_SDNN)

########################
#   RMSSD Calculator   #
########################
def RMSSD_calculator(data):
    i = 0
    summary = 0
    while i < len(data)-1:
        summary += (data[i+1]-data[i])**2
        i +=1
    rounded_RMSSD = round((summary/(len(data)-1))**(1/2), 0)
    return int(rounded_RMSSD)

#######################
#   SDSD Calculator   #
#######################
def SDSD_calculator(data):
    PP_array = array.array('l')
    i = 0
    first_value = 0
    second_value = 0
    while i < len(data)-1:
        PP_array.append(int(data[i+1])-int(data[i]))
        i += 1
    i = 0
    while i < len(PP_array)-1:
        first_value += float(PP_array[i]**2)
        second_value += float(PP_array[i])
        i += 1
    first = first_value/(len(PP_array)-1)
    second = (second_value/(len(PP_array)))**2
    rounded_SDSD = round((first - second)**(1/2), 0)
    return int(rounded_SDSD)

######################
#   SD1 Calculator   #
######################     
def SD1_calculator(SDSD):
    rounded_SD1 = round(((SDSD**2)/2)**(1/2), 0)
    return int(rounded_SD1)

######################
#   SD2 Calculator   #
######################   
def SD2_calculator(SDNN, SDSD):
    rounded_SD2 = round(((2*(SDNN**2))-((SDSD**2)/2))**(1/2), 0)
    return int(rounded_SD2)

########################
#   RMSSD Calculator   #
########################
def RMSSD_calculator(data):
    i = 0
    summary = 0
    while i < len(data)-1:
        summary += (data[i+1]-data[i])**2
        i +=1
    rounded_RMSSD = round((summary/(len(data)-1))**(1/2), 0)
    return int(rounded_RMSSD)

#######################
#   SDSD Calculator   #
#######################
def SDSD_calculator(data):
    PP_array = array.array('l')
    i = 0
    first_value = 0
    second_value = 0
    while i < len(data)-1:
        PP_array.append(int(data[i+1])-int(data[i]))
        i += 1
    i = 0
    while i < len(PP_array)-1:
        first_value += float(PP_array[i]**2)
        second_value += float(PP_array[i])
        i += 1
    first = first_value/(len(PP_array)-1)
    second = (second_value/(len(PP_array)))**2
    rounded_SDSD = round((first - second)**(1/2), 0)
    return int(rounded_SDSD)

######################
#   SD1 Calculator   #
######################     
def SD1_calculator(SDSD):
    rounded_SD1 = round(((SDSD**2)/2)**(1/2), 0)
    return int(rounded_SD1)

######################
#   SD2 Calculator   #
######################   
def SD2_calculator(SDNN, SDSD):
    rounded_SD2 = round(((2*(SDNN**2))-((SDSD**2)/2))**(1/2), 0)
    return int(rounded_SD2)


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                  MAIN PROGRAMME                  #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

welcome_text()
capture_length = samplerate * 5
buffer = array.array('H',[0]*capture_length)

while True:
    press_to_start()
    new_state = rot_push.value()
    
    if new_state != switch_state:
        count += 1
        if count > 3:
            if new_state == 0:
                if mode == 0:
                    mode = 1
                else:
                    mode = 0
                led_onboard.value(1)
                time.sleep(0.15)
                led_onboard.value(0)
            switch_state = new_state
            count = 0
    else:
        count = 0
    utime.sleep(0.01)
    
    if mode == 1:
        count = 0
        switch_state = 0

        oled.fill(0)
        oled.show()
        
        x1 = -1
        y1 = 32
        m0 = 65535/2
        a = 1/10

        disp_div = samplerate/25
        disp_count = 0

        index = 0
        avg_size = int(samplerate*0.5)
        sample_sum = 0

        min_bpm = 30
        max_bpm = 200
        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        PPI_array = []

        tmr = Timer(freq = samplerate, callback = read_adc)
        
        #####################################
        #   Plotting the signal, Sampling   #
        #####################################
        #while len(buffer) < capture_length:
        while index < len(buffer):
            if not samples.empty():
                x = samples.get()
                #buffer.append(x)
                buffer[index] = x
                index += 1
                disp_count += 1
        
                if disp_count >= disp_div:
                    disp_count = 0
                    m0 = (1-a)*m0+a*x
                    y2 = int(32*(m0-x)/10000+32)
                    y2 = max(0, min(64, y2))
                    x2 = x1 + 1
                    oled.line(x2, 0, x2, 64, 0)
                    oled.line(x1, y1, x2, y2, 1)
                    oled.show()
                    x1 = x2
                    if x1 > 127:
                        x1 = -1
                    y1 = y2
            
        tmr.deinit()
        
        while not samples.empty():
            x = samples.get()
        
        ######################
        #   Peak Detection   #
        ######################

        index = 0
        
        while(index < avg_size):
            sample_sum = sample_sum + buffer[index]
            index += 1

        while(index < len(buffer)):
            sample_avg = sample_sum / avg_size
            sample_val = buffer[index]

            if sample_val > sample_avg * 1.05:
                if sample_val > sample_peak:
                    sample_peak = sample_val
                    sample_index = index
            else:
                if sample_peak > 0:
                    if (sample_index - previous_index) > (60 * samplerate / min_bpm):
                        previous_peak = 0
                        previous_index = 0
                    else:
                        if sample_peak >= (0.8 * previous_peak):
                            if (sample_index - previous_index) > (60 * samplerate / max_bpm):
                                if previous_peak > 0:
                                    interval = sample_index - previous_index
                                    interval_ms = int(interval * 1000 / samplerate)
                                    PPI_array.append(interval_ms)
                                    #print("BPM: " + str((samplerate / interval) * 60))
                                previous_peak = sample_peak
                                previous_index = sample_index
                        #print("Sample " + str(sample_index) + " peak: " + str(sample_peak))
                sample_peak = 0

            sample_sum = sample_sum + buffer[index] - buffer[index-avg_size]
            index += 1
            
        #######################
        #   HRV calculation   #
        #######################
        
        #PPI_array2 = array.array('H', [754, 854, 968, 796, 785, 983, 1012, 879, 846, 794, 689, 987, 834, 821, 768, 895])
        oled.fill(0)
        if len(PPI_array) >= 3:
            mean_PPI = meanPPI_calculator(PPI_array)
            mean_HR = meanHR_calculator(mean_PPI)
            SDNN = SDNN_calculator(PPI_array, mean_PPI)
            RMSSD = RMSSD_calculator(PPI_array)
            SDSD = SDSD_calculator(PPI_array)
            SD1 = SD1_calculator(SDSD)
            SD2 = SD2_calculator(SDNN, SDSD)
         
            oled.text('MeanPPI:'+ str(int(mean_PPI)) +'ms', 0, 0, 1)
            oled.text('MeanHR:'+ str(int(mean_HR)) +'bpm', 0, 9, 1)
            oled.text('SDNN:'+str(int(SDNN)) +'ms', 0, 18, 1)
            oled.text('RMSSD:'+str(int(RMSSD)) +'ms', 0, 27, 1)
            oled.text('SD1:'+str(int(SD1))+'  SD2:'+str(int(SD2)), 0, 36, 1)
            #oled.text('PNS:'+str(PNS), 0, 45, 1)
            #oled.text('SNS:'+str(SNS), 0, 54, 1)

        else:
            oled.text('Error', 45, 10, 1)
            oled.text('Please restart', 8, 30, 1)
            oled.text('measurement', 20, 40, 1)
        oled.show()
            
        while mode == 1:
            new_state = rot_push.value()
            if new_state != switch_state:
                count += 1
                if count > 3:
                    if new_state == 0:
                        if mode == 0:
                            mode = 1
                        else:
                            mode = 0
                        led_onboard.value(1)
                        time.sleep(0.15)
                        led_onboard.value(0)
                    switch_state = new_state
                    count = 0
            else:
                count = 0
            utime.sleep(0.01)
