# Device Compatibility


## PPT 100

Below is shown a PPT 100 type gauge. 

![gauge](https://raw.githubusercontent.com/electronsandstuff/py-pfeiffer-vacuum-protocol/master/assets/gauge.jpg)

To correctly do this, you'll need to make a quick custom cable for the device.  Please follow the pinout in the PPT 100 manual reproduced here.  On this particular gauge, V DC is 24 V.

![pinout](https://raw.githubusercontent.com/electronsandstuff/py-pfeiffer-vacuum-protocol/master/assets/pinout.png)

Cheap RS485 adapters exist that allow the gauge to be directly connected to a PC.  Currently, only functions relevant to the PPT 100 are implemented in the library.  The following is a table of compatibility for other models reproduced from the PPT 100 manual.  If you are interested in other gauges, then please consider contributing.

![compatibility](https://raw.githubusercontent.com/electronsandstuff/py-pfeiffer-vacuum-protocol/master/assets/compatibility.PNG)

To connect the gauge to a computer, you can use something like a USB to RS485 adapter like this: 

## PKR Series gauges

Below is shown a PKR 361 Kf cold/hot Pirani gauge

![activeline](https://raw.githubusercontent.com/electronsandstuff/py-pfeiffer-vacuum-protocol/master/assets/ActivelineGauge.png)

To connect this gauge, first you will need to connect the gauge to the gauge input on the Omnicontrol, DCU, or whatever other pfeiffer analog gauge controller you are using. Then from the back of the controller, you will need to connect to the M12 RS485 port to the computer. 

![controller](https://raw.githubusercontent.com/electronsandstuff/py-pfeiffer-vacuum-protocol/master/assets/Omnicontrol.png)

The M12 RS485 output of the controller will connect to your RS485 adapter and then to your computer. 

