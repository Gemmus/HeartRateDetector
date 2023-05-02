import rp2

# A simple class 
class Piotimer:
    PERIODIC = 1

    def __init__(self, *, mode=PERIODIC, freq=- 1, period=- 1, callback=None):
        # Instantiate StateMachine(0) 
        self.sm = rp2.StateMachine(0, self.pio_timer, freq = 1000000)
        # set interrupt handler
        self.sm.irq(callback, hard = True)
        # Start the StateMachine's running.
        if freq > 0:
            interval = int(1000000 / freq)
        elif period > 0:
            interval = int(period * 1000)
        else:
            raise RuntimeError('Must specify \'freq\' or \'period\'')

        if interval < 100:
            raise RuntimeError('Too high timer frequency')

        self.sm.put(interval - 5)
        self.sm.active(1)
        
    def __del__(self):
        self.sm.active(0)
    
    def deinit(self):
        self.sm.active(0)
    
    @rp2.asm_pio()
    def pio_timer():
        wrap_target()
        pull(noblock)
        mov(x, osr)
        mov(y,x)
        label("loop")
        jmp(y_dec, "loop")
        irq(0)
        wrap()


