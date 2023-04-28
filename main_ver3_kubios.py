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
                                                #                     VARIABLES                    #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

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

# Variables related to peak detection and peak-to-peak intervals
#x1 = -1
#y1 = 32
#m0 = 65535 / 2
#a = 1/10

#disp_div = samplerate / 25
#disp_count = 0
#buffer = []
#capture_length = samplerate * 10

#index = 0
#avg_size = int(samplerate * 0.5)
#sample_sum = 0

#min_bpm = 30
#max_bpm = 200
#sample_peak = 0
#sample_index = 0
#previous_peak = 0
#previous_index = 0
#PPI_array = []

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
    
########################################
#   Functions for connecting to WLAN   #
########################################
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    ip = wlan.ifconfig()[0]
    print(f"The IP address is : {ip}")
    return ip
    


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
    PPI = sumPPI/len(data)
    rounded_PPI = round(PPI, 0)
    #print('Mean PPI value:', int(rounded_PPI), 'ms')
    return int(rounded_PPI)

##########################
#   Mean HR Calculator   #
##########################
def meanHR_calculator(meanPPI):
    HR = 60*1000/meanPPI
    rounded_HR = round(HR, 0)
    #print('Mean HR value:', int(rounded_HR), 'bpm')
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
    #print('SDNN value:', int(rounded_SDNN), 'ms')
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
    RMSSD = (summary/(len(data)-1))**(1/2)
    rounded_RMSSD = round(RMSSD, 0)
    #print('RMSSD value:', int(rounded_RMSSD), 'ms')
    return int(rounded_RMSSD)

#######################
#   SDSD Calculator   #
#######################
def SDSD_calculator(data):
    i = 0
    PP_array = array.array('l')
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
    SDSD = (first - second)**(1/2)
    rounded_SDSD = round(SDSD, 0)
    #print('SDSD value:', int(rounded_SDSD))
    return int(rounded_SDSD)

######################
#   SD1 Calculator   #
######################     
def SD1_calculator(SDSD):
    SD1 = ((SDSD**2)/2)**(1/2)
    rounded_SD1 = round(SD1, 0)
    #print('SD1 value:', int(rounded_SD1))
    return int(rounded_SD1)

######################
#   SD2 Calculator   #
######################   
def SD2_calculator(SDNN, SDSD):
    SD2 = ((2*(SDNN**2))-((SDSD**2)/2))**(1/2)
    rounded_SD2 = round(SD2, 0)
    #print('SD2 value:', int(rounded_SD2))
    return int(rounded_SD2)



                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                   WELCOME TEXT                   #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

oled.fill(1)
oled.text("Welcome to", 23, 17, 0)
oled.text("Group 5's", 26, 27, 0)
oled.text("project!", 30, 37, 0)
oled.show()
utime.sleep_ms(2500)
oled.fill(0)
oled.show()

                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.#
                                                #                                                  #
                                                #                  MAIN PROGRAMME                  #
                                                #                                                  #
                                                #*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*:*.*.*.*.*.*.*.*.*.#

capture_length = samplerate * 110
buffer = array.array('H',[0]*capture_length)

while True:
    new_state = rot_push.value()
    oled.fill(0)
    oled.text("Press to start", 0, 22, 1)
    oled.text("the measurement", 0, 32, 1)
    oled.text("        ------->", 0, 55, 1)
    oled.show()

    if new_state != switch_state:
        count += 1
        if count > 3:
            if new_state == 0:
                if mode == 0:
                    mode = 1
                else:
                    mode = 0
            switch_state = new_state
            count = 0
    else:
        count = 0
    utime.sleep(0.01)
    
    if mode == 1:
        mode = 0
        count = 0
        switch_state = 0

        oled.fill(0)
        oled.show()
        x1 = -1
        y1 = 32
        m0 = 65535 / 2
        a = 1/10

        disp_div = samplerate / 25
        disp_count = 0
        #capture_length = samplerate * 110
        #buffer = []
        #buffer = array.array('H',[0]*capture_length)

        index = 0
        avg_size = int(samplerate * 0.5)
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
                #comes_here
        
                if disp_count >= disp_div:
                    disp_count = 0
                    #print('nu3')
                    m0 = (1-a)*m0 + a*x
                    y2 = int(32*(m0-x)/10000 + 32)
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
            
        ################
        #   Analysis   #
        ################
        
        #PPI_array = array.array('H', [754, 854, 968, 796, 785, 983, 1012, 879, 846, 794, 689, 987, 834, 821, 768, 895])
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
                #print(response)
    
                SNS = round(response['analysis']['sns_index'], 2)
                PNS = round(response['analysis']['pns_index'], 2)
    
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
            oled.text('SD1:'+str(int(SD1))+'  SD2:'+str(int(SD2)), 0, 36, 1)
            oled.text('PNS:'+str(PNS), 0, 45, 1)
            oled.text('SNS:'+str(SNS), 0, 54, 1)
            oled.show()
        else:
            oled.text('Error', 45, 10, 1)
            oled.text('Please restart', 8, 30, 1)
            oled.text('measurement', 20, 40, 1)
        oled.show()
        utime.sleep_ms(4500)
        #print(buffer, PPI_array)
        #print(PPI_array)

