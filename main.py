from piotimer import Piotimer as Timer
from ssd1306 import SSD1306_I2C
from machine import Pin, ADC, I2C, PWM
from fifo import Fifo
import utime
import array
import time
import network
import socket
import urequests as requests
import ujson

                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                    GPIO PINS                     #
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

# Rotary Encoder
rot_push = Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                     VARIABLES                    #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

# Sample Rate, Buffer
samplerate = 250
samples = Fifo(32)

# Menu selection variables and switch filtering
mode = 0
count = 0
switch_state = 0

# SSID credentials
ssid = 'KMD758Group5'
password = '105105105M'

# Kubios credentials
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                     FUNCTIONS                    #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

#######################################
#   Function for reading the signal   #
#######################################
def read_adc(tid):
    x = adc.read_u16()
    samples.put(x)

########################################
#   Function to display welcome text   #
########################################
def welcome_text():
    oled.fill(1)
    i = 0
    horizontal1 = 0
    horizontal2 = 0
    
    for i in range(6):
        oled.pixel(4+horizontal1, 3, 0)
        oled.pixel(8+horizontal1, 3, 0)
        oled.pixel(4+horizontal1, 54, 0)
        oled.pixel(8+horizontal1, 54, 0)
    
        oled.line(3+horizontal1, 4, 5+horizontal1, 4, 0)
        oled.line(3+horizontal1, 55, 5+horizontal1, 55, 0)

        oled.line(7+horizontal1, 4, 9+horizontal1, 4, 0)
        oled.line(7+horizontal1, 55, 9+horizontal1, 55, 0)

        oled.line(2+horizontal1, 5, 10+horizontal1, 5, 0)
        oled.line(2+horizontal1, 56, 10+horizontal1, 56, 0)

        oled.line(3+horizontal1, 6, 9+horizontal1, 6, 0)
        oled.line(3+horizontal1, 57, 9+horizontal1, 57, 0)

        oled.line(4+horizontal1, 7, 8+horizontal1, 7, 0)
        oled.line(4+horizontal1, 58, 8+horizontal1, 58, 0)

        oled.line(5+horizontal1, 8, 7+horizontal1, 8, 0)
        oled.line(5+horizontal1, 59, 7+horizontal1, 59, 0)

        oled.pixel(6+horizontal1, 9, 0)
        oled.pixel(6+horizontal1, 60, 0)
        
        horizontal1 += 23
    
    for i in range(2):
        oled.pixel(4+horizontal2, 19, 0)
        oled.pixel(8+horizontal2, 19, 0)
        oled.pixel(4+horizontal2, 37, 0)
        oled.pixel(8+horizontal2, 37, 0)
    
        oled.line(3+horizontal2, 20, 5+horizontal2, 20, 0)
        oled.line(3+horizontal2, 38, 5+horizontal2, 38, 0)

        oled.line(7+horizontal2, 20, 9+horizontal2, 20, 0)
        oled.line(7+horizontal2, 38, 9+horizontal2, 38, 0)

        oled.line(2+horizontal2, 21, 10+horizontal2, 21, 0)
        oled.line(2+horizontal2, 39, 10+horizontal2, 39, 0)

        oled.line(3+horizontal2, 22, 9+horizontal2, 22, 0)
        oled.line(3+horizontal2, 40, 9+horizontal2, 40, 0)

        oled.line(4+horizontal2, 23, 8+horizontal2, 23, 0)
        oled.line(4+horizontal2, 41, 8+horizontal2, 41, 0)

        oled.line(5+horizontal2, 24, 7+horizontal2, 24, 0)
        oled.line(5+horizontal2, 42, 7+horizontal2, 42, 0)

        oled.pixel(6+horizontal2, 25, 0)
        oled.pixel(6+horizontal2, 43, 0)
        
        horizontal2 += 115

    oled.text("Welcome to", 26, 17, 0)
    oled.text("Group 5's", 29, 27, 0)
    oled.text("project!", 33, 37, 0)
    oled.show()
    utime.sleep_ms(3750)
    
########################################
#   Function to display "Start menu"   #
########################################
def press_to_start():
    oled.fill(0)
    oled.text("Press to start", 4, 7, 1)
    oled.text("the measurement", 4, 17, 1)
    oled.line(10, 53, 15, 53, 1)
    oled.line(93, 53, 124, 53, 1)
    oled.line(118, 48, 124, 53, 1)
    oled.line(118, 58, 124, 53, 1)
    oled.line(118, 48, 124, 53, 1)
    oled.line(118, 58, 124, 53, 1)
    oled.line(93, 53, 124, 53, 1)
    oled.line(48, 53, 60, 53, 1)
    horizontal = 0
    
    for i in range(2):
        oled.line(60-horizontal, 53, 63-horizontal, 50, 1)
        oled.line(63-horizontal, 50, 66-horizontal, 53, 1)
        oled.line(66-horizontal, 53, 68-horizontal, 53, 1)
        oled.line(68-horizontal, 53, 70-horizontal, 57, 1)
        oled.line(70-horizontal, 57, 73-horizontal, 31, 1)
        oled.line(73-horizontal, 31, 76-horizontal, 64, 1)
        oled.line(76-horizontal, 64, 78-horizontal, 53, 1)
        oled.line(78-horizontal, 53, 80-horizontal, 53, 1)
        oled.line(80-horizontal, 53, 84-horizontal, 47, 1)
        oled.line(84-horizontal, 47, 88-horizontal, 53, 1)
        oled.line(88-horizontal, 53, 89-horizontal, 53, 1)
        oled.line(89-horizontal, 53, 91-horizontal, 51, 1)
        oled.line(91-horizontal, 51, 93-horizontal, 53, 1)
        
        horizontal += 45
        
    oled.show()

########################################
#   Functions for connecting to WLAN   #
########################################
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    ip = wlan.ifconfig()[0]
    return
      
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


                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                  MAIN PROGRAMME                  #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

welcome_text()
avg_size = 128  # originally: int(samplerate * 0.5)
buffer = array.array('H',[0]*avg_size)

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
        m0 = 65535 / 2
        a = 1 / 10

        disp_div = samplerate / 25
        disp_count = 0
        capture_length = samplerate * 60  # 60 = 60s, changable respectively

        index = 0
        capture_count = 0
        subtract_old_sample = 0
        sample_sum = 0

        min_bpm = 30
        max_bpm = 200
        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        interval_ms = 0
        PPI_array = []
        
        brightness = 0

        tmr = Timer(freq = samplerate, callback = read_adc)

        #####################################
        #   Plotting the signal, Sampling   #
        #####################################
        
        while capture_count < capture_length:
            if not samples.empty():
                x = samples.get()
                disp_count += 1
        
                if disp_count >= disp_div:
                    disp_count = 0
                    m0 = (1 - a) * m0 + a * x
                    y2 = int(32 * (m0 - x) / 14000 + 35)
                    y2 = max(10, min(53, y2))
                    x2 = x1 + 1
                    oled.fill_rect(0, 0, 128, 9, 1)
                    oled.fill_rect(0, 55, 128, 64, 1)
                    if len(PPI_array) > 3:
                        actual_PPI = meanPPI_calculator(PPI_array)
                        actual_HR = meanHR_calculator(actual_PPI)
                        oled.text(f'HR:{actual_HR}', 2, 1, 0)
                        oled.text(f'PPI:{interval_ms}', 60, 1, 0)
                    oled.text(f'Timer:  {int(capture_count/samplerate)}s', 18, 56, 0)
                    oled.line(x2, 10, x2, 53, 0)
                    oled.line(x1, y1, x2, y2, 1)
                    oled.show()
                    x1 = x2
                    if x1 > 127:
                        x1 = -1
                    y1 = y2

                if subtract_old_sample:
                    old_sample = buffer[index]
                else:
                    old_sample = 0
                sample_sum = sample_sum + x - old_sample

                ######################
                #   Peak Detection   #
                ######################

                if subtract_old_sample:
                    sample_avg = sample_sum / avg_size
                    sample_val = x
                    if sample_val > (sample_avg * 1.05):
                        if sample_val > sample_peak:
                            sample_peak = sample_val
                            sample_index = capture_count

                    else:
                        if sample_peak > 0:
                            if (sample_index - previous_index) > (60 * samplerate / min_bpm):
                                previous_peak = 0
                                previous_index = sample_index
                            else:
                                if sample_peak >= (previous_peak*0.8):
                                    if (sample_index - previous_index) > (60 * samplerate / max_bpm):
                                        if previous_peak > 0:
                                            interval = sample_index - previous_index
                                            interval_ms = int(interval * 1000 / samplerate)
                                            PPI_array.append(interval_ms)
                                            brightness = 5
                                            led21.duty_u16(4000)
                                        previous_peak = sample_peak
                                        previous_index = sample_index
                        sample_peak = 0

                    if brightness > 0:
                        brightness -= 1
                    else:
                        led21.duty_u16(0)

                buffer[index] = x
                capture_count += 1
                index += 1
                if index >= avg_size:
                    index = 0
                    subtract_old_sample = 1

        tmr.deinit()
        
        while not samples.empty():
            x = samples.get()

        #######################
        #   HRV calculation   #
        #######################

        oled.fill(0)
        if len(PPI_array) >= 3:
            try:
                connect()
            except KeyboardInterrupt:
                machine.reset()
                
            try:
                response = requests.post(
                    url = TOKEN_URL,
                    data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
                    headers = {'Content-Type':'application/x-www-form-urlencoded'},
                    auth = (CLIENT_ID, CLIENT_SECRET))
    
                response = response.json()
                access_token = response["access_token"]
                
                data_set = {
                    "type": "RRI",
                    "data": PPI_array,
                    "analysis": {"type": "readiness"}
                    }
      
                response = requests.post(
                    url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
                    headers = { "Authorization": "Bearer {}".format(access_token),
                                "X-Api-Key": APIKEY },
                    json = data_set)
    
                response = response.json()
    
                SNS = round(response['analysis']['sns_index'], 2)
                PNS = round(response['analysis']['pns_index'], 2)
                oled.text('PNS:'+str(PNS), 0, 45, 1)
                oled.text('SNS:'+str(SNS), 0, 54, 1)
    
            except KeyboardInterrupt:
                machine.reset()
                
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
            oled.text('SD1:'+str(int(SD1))+' SD2:'+str(int(SD2)), 0, 36, 1)
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
