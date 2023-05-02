import array


class Fifo:
    def __init__(self, size):
        self.data = array.array('H')
        for i in range(size):
            self.data.append(0)
        self.head = 0
        self.tail = 0
        self.size = size
        self.dc = 0
        
    def put(self, value):
        nh = self.head + 1
        if nh >= self.size:
            nh = 0
        if nh != self.tail:
            self.data[self.head] = value
            self.head = nh
        else:
            self.dc = self.dc + 1
            
    def get(self):
        val = self.data[self.tail]
        if not self.empty():
            self.tail = self.tail + 1
            if self.tail >= self.size:
                self.tail = 0
        return val
    
    def average(self):
        N = self.size
        m = 0
        for i in range(N):
            m = m + self.data[i]
        return m/N
        
    def dropped(self):
        return self.dropped
        
                
    def empty(self):
        return self.head == self.tail


