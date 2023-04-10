from piotimer import Piotimer as Timer # hardware
# from machine import Timer #software
from ssd1306 import SSD1306_I2C
from machine import Pin, ADC, I2C, PWM
from fifo import Fifo
from led import Led
from utime import sleep
import array

pin = Pin(21, Pin.OUT)
adc = ADC(26)

samplerate = 250

samples = Fifo(samplerate)
i2c = I2C(1, scl = Pin(15), sda = Pin(14))
oled = SSD1306_I2C(128, 64, i2c)
    
def read_adc(tid):
    x = adc.read_u16()
    samples.put(x)
    
tmr = Timer(freq = samplerate, callback = read_adc)

x1 = -1
y1 = 32
m0 = 65535 / 2 # moving average
a = 1/10 # weight for adding new data to moving average
disp_div = samplerate / 25
disp_count = 0
buffer = array.array('I')
capture_length = samplerate * 30

while len(buffer) < capture_length:
    if not samples.empty():
        x = samples.get()
        buffer.append(x)

        disp_count += 1
        if disp_count >= disp_div:
            disp_count = 0
            m0 = (1-a)*m0 + a*x # Calculate moving average
            y2 = int(32*(m0-x)/10000 + 32) # Scale the value to fit into OLED
            #y2 = int(64-(x/65535)*64) # Alternative scaling without moving average
            y2 = max(0, min(64, y2)) # Limit the values between 0..64
            x2 = x1 + 1
            oled.line(x2, 0, x2, 64, 0) # Clean up one line
            oled.line(x1, y1, x2, y2, 1) # Draw the new line
            oled.show()
            x1 = x2
            if x1 > 127:
                x1 = -1
            y1 = y2
            #print(x)

        #print("x = " + str(x) + ", m = " + str(m))
        #if x > m:
        #    pin.value(1)
        #else:
        #    pin.value(0)

tmr.deinit()

index = 0
avg_size = samplerate * 1
sample_sum = 0
while(index < avg_size):
    sample_sum = sample_sum + buffer[index]
    index = index + 1

sample_peak = 0
sample_index = 0
previous_peak = 0
previous_index = 0
while(index < len(buffer)):
    sample_avg = sample_sum / avg_size
    sample_val = buffer[index]

    if sample_val > sample_avg * 1.15:
        if sample_val > sample_peak:
            sample_peak = sample_val
            sample_index = index
    else:
        if sample_peak > 0:
            if sample_peak >= (0.9 * previous_peak):
                if previous_peak > 0:
                    interval = sample_index - previous_index
                    print("BPI: " + str((samplerate / interval) * 60))
                previous_peak = sample_peak
                previous_index = sample_index
            print("Sample " + str(sample_index) + " peak: " + str(sample_peak))
        sample_peak = 0

    sample_sum = sample_sum + buffer[index] - buffer[index-avg_size]
    index = index + 1

#tmr.deinit()
        