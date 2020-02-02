_ga_version0.2.1_

# Supported sensors
+ Air humidity and temperature
    + [adafruit dht22](https://www.adafruit.com/product/385): pip module [Adafruit_DHT](https://pypi.org/project/Adafruit_Python_DHT/), amazon [link](https://www.amazon.de/AZDelivery-AM2302-Temperatursensor-Luftfeuchtigkeitssensor-Arduino/dp/B074MY32RX/)
+ Earth humidity
    + capacitive sensor:<br>
     analog-digital-converter needed, amazon [link](https://www.amazon.de/AZDelivery-Bodenfeuchtesensor-Hygrometer-kapazitiv-Arduino/dp/B07V6M5C4H/),<br>
     note: only analog output -> adc needed

# To test
+ Wind
    + analog wind sensor:<br>
    analog-digital-converter needed, amazon [link](https://www.amazon.de/Duokon-Windgeschwindigkeitssensor-aus-Aluminiumlegierung/dp/B07QL18J3T/)

# Unsupported sensors
+ Earth humidity
    + electrolysis sensor:<br>
    analog-digital-converter needed, amazon [link](https://www.amazon.de/AZDelivery-Hygrometer-Feuchtigkeit-Bodenfeuchtesensor-Arduino/dp/B07V4KXZ35/),<br>
    note: you need to switch off power to the sensor when not needed or else it will die quickly, digital output is useless