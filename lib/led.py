from machine import Pin, PWM


class Led: 
    def __init__(self, pin, brightness = 1, value = None):
        self._pin = Pin(pin, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(1000)
        self.brightness(brightness)
        if value != None:
            self.value(value)
        
    def on(self):
        self._pwm.duty_u16(self._on_val)

    def off(self):
        self._pwm.duty_u16(0)
        
    def low(self):
        self.off()

    def high(self):
        self.on()

    def toggle(self):
        if self._pwm.duty_u16():
            self.off()
        else:
            self.on()
            
    def __call__(self, *args):
        return self.value(*args)

    def value(self, *args):
            if len(args) > 1:
                raise TypeError("Too many arguments. Only one argument allowed")
            elif len(args):
                if args[0]: self.on()
                else: self.off()
            else:
                if self._pwm.duty_u16():
                    return 1
                else:
                    return 0
            
    def brightness(self, brightness):
        brightness = min(100, max(0.5, brightness)) # limit val to range [0-100]
        self._on_val = int(65535 * brightness/100)
        if self._pwm.duty_u16():
            self.on()

