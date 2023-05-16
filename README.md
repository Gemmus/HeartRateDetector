# Heart Rate Detector and Stress Meter
<br />Heart rate detector implemented using <a href="https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html">Raspberry Pi Pico W</a> and <a href="https://www.elecrow.com/wiki/index.php?title=Crowtail-_Pulse_Sensor">Crowtail - Pulse Sensor</a>.
<br />MicroPython as programming language and Thonny as IDE.
<br />
<br /><b>Components:</b>
<ul>
      <li>Raspberry Pi Pico W</li>
      <li>Crowtail - Pulse Sensor (photoplethysmography - PPG)</li>
      <li>OLED (SSD1306)</li>
      <li>Rotary knob</li>
</ul>

![image](https://github.com/Gemmus/HeartRateDetector/assets/112064697/11d28d8e-db03-4a4a-a67b-511f73e9224f)



<h2> Operating Principle </h2>
The Crowtail optical sensor detects the heart rate as an analog signal and transmits it to the Raspberry Pico Pi W. This analog signal is converted into digital by the AD-converter of the microcontroller and using own  peak-detection related algorithms, the device is capable of measuring the peak-to-peak interval (PPI) of the heart signal. 

<br />Using the gathered interval data, the mean peak-to-peak interval (PPI), mean heart rate (HR), standard deviation of successive interval differences (SDNN), root mean square of successive differences (RMSSD) and Poincare plot shape parameters (SD1, SD2) are analysised with own algorithms.

From Raspberry Pi Pico the collected peak-to-peak interval data is also transmitted wirelessly to the Kubios Cloud Service, where the data is further analysed to receive the recovery and stress indexes. The outcome of this analysis is then returned to the device and the results are presented through the OLED display for the user along with the locally calculated parameters.

During the measurement, the rotary knob functions as the controller for this operation, that provides the user interaction for the hardware. The user can choose the activity respectively based on to the information displayed on the OLED, such as initialisation or restart of the measurement. 

![image](https://github.com/Gemmus/HeartRateDetector/assets/112064697/490c977d-00bf-4335-b7e6-882ecf23c73b)

<a href="https://github.com/Gemmus/HeartRateDetector/blob/main/HeartRateDetector_Documentation.pdf">More Information</a>
