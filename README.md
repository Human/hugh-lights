#Purpose

* This program lets your Raspberry Pi control control RGB LEDs.

#Features

1. **Color correction.** Some RGB LED strips have imbalanced LEDs, and this program allows you compensate by reducing brightness on any color channel.

2. **Simple file-based API.** During continuous operation, simply put your desired target color into a CSV file containing RGB values ranging from 0-255, and the program will implement your target color. Change it as often as you like.

3. **Transition options.** You can fade from the current color to the target color directly, by fading to black and then fading to the target color, or by changing to the target color instantaneously. You can change these preferences on the fly.

4. **Integration with [openHAB](http://www.openhab.org/)** via the ```exec``` binding.

#HOWTO

##What You Need

1. **Raspberry Pi** (Rev B tested, but any revision should work.)

2. **An RGB LED strip** (I bought [this one](http://www.amazon.com/gp/product/B00AQT2G9S), but any 4-pin common-anode RGB LED strip will work. Deviations will work, but you'll need to come up with your own wiring diagram.)

3. **A DC power supply** (My strip is 12VDC, with a maximum current of 0.6A, and I have a 12VDC 8.5A power supply.)

4. **Three MOSFETs** (I used [these](http://www.digikey.com/product-search/en?KeyWords=497-2765-5-ND) N-channel MOSFETs. Deviations can work, but you'll need to come up with your own wiring diagram.)

5. **Three free GPIO pins**

6. **At least 60% available CPU on your Pi**

7. **Basic Linux skills** (package installing, file copying and editing, running commands)

##Hardware Setup

1. Wire up your MOSFETs and RGB LED strip as you see on the first diagram in [this Adafruit tutorial for the Arduino](https://learn.adafruit.com/rgb-led-strips/usage), except that:

    1. You have a Pi, not an Arduino, but the basic principle is the same.
    
    1. You power the LED strip with your dedicated power supply, not any pin from the Pi.
    
    1. You will run a ground wire from your Pi to the ground terminal of the power supply.
    
    1. Pick three GPIO pins to control red, green, and blue. Read the [pigpio](http://abyz.co.uk/rpi/pigpio/) documentation carefully before picking your pins. **If you get this wrong, various bad things can happen.**
    
##Software Setup

1. As shown [here](http://abyz.co.uk/rpi/pigpio/download.html), download, build, and install ```pigpio``` on your Raspberry Pi, then start the ```pigpio``` daemon.

    1. Download, build, and install.
    
             wget abyz.co.uk/rpi/pigpio/pigpio.zip
             unzip pigpio.zip
             cd PIGPIO
             make
             make install
    
    1. Start the pigpio daemon.

             sudo pigpiod

1. Install, configure, and run Hugh.

    1. Copy the Hugh directory tree to your Pi. Mine is in ```/home/pi/hugh```
    
    1. Edit ```hugh_config.ini``` to match the BCM-indexed GPIO pins that you chose above.
    
    1. Run Hugh from its directory:
    
             cd /home/pi/hugh
             sudo python ./hugh.py
             
    1. Any edits to the files ```hugh_config.ini``` or ```rgb``` will be loaded and quickly implemented by Hugh.



##[openHAB](http://www.openhab.org/) Integration (optional)

* My solution builds on [this example for KNX](https://github.com/openhab/openhab/wiki/Samples-Rules#how-to-use-colorpicker-widget-with-knxdali-rgb-led-stripe) and [this example using MQTT](http://blue-pc.net/2014/10/21/nachtlicht-mit-arduino-und-mqtt-ueber-openhab-steuern/).

###items

1. Add this ```Color``` item to any of your *```.items``` files, which gives you a color picker UI.
    
        Color  HSB   "Color Light"   <slider>  (Lights)
        
1. Add a ```String``` item to any of your *```.items``` files, as your interface to the Hugh software running on your Pi.

    1. If the Pi running Hugh is _also_ your openHAB server, add this:

        String RGB   "RGB Value"  { exec=">[*:echo %2$s > /home/pi/hugh/rgb]" }
        
    1. Otherwise, add this entry:
    
        String RGB   "RGB Value"   { exec=">[*:ssh pi@pi2 echo %2$s > /home/pi/hugh/rgb]" }


1. **DON'T** put ```RGB``` item into any groups or sitemaps. It's not something that users should directly interact with.
    
1. Put the ```HSB``` item into any groups and sitemaps you prefer. The reference example assumes you want it in the ```Lights``` group.

1. Edit the ```RGB``` item to match the device name, username, and target directory for Hugh's RGB file.

###rules

1. Add this rule to any of your *```.rules``` files. This converts the HSB (hue, saturation, brightness) color to comma-separated RGB (red, green, blue) values, and puts them into the ```RGB``` ```String``` item, which in turn gives the RGB values to Hugh.

        rule "Set RGB Value from HSB"
        when
        	Item HSB changed
        then
        	var HSBType hsbValue = HSB.state as HSBType 
        
        	// scale the values to 256 levels
        	var int red = Math::round(hsbValue.red.floatValue * 2.55)
        	var int green = Math::round(hsbValue.green.floatValue * 2.55)
        	var int blue = Math::round(hsbValue.blue.floatValue * 2.55)
        
        	sendCommand(RGB, red+","+green+","+blue)
        	postUpdate(RGB, red+","+green+","+blue)
        end
        
###SSH

1. If the Pi running Hugh is _also_ your openHAB server, then you can skip this step. Otherwise:

    1. As the ```root``` user, [generate an SSH keypair on your openHAB server](https://help.ubuntu.com/community/SSH/OpenSSH/Keys#Generating_RSA_Keys) with an empty passphrase.
    
    1. On the Pi, as a regular user (e.g. ```pi```), _append_ the _public_ key to ```~/.ssh/authorized_keys``` in the user account on the Pi (e.g. ```/home/pi/.ssh/authorized_keys```) to allow your openHAB server to automatically log in when it runs ```ssh``` via the ```exec``` binding in the ```RGB``` item.
    
###usage

* openHAB will pick up on the ```items``` and ```rules``` changes. You should be able to interact with the ```HSB``` color picker in any openHAB UI and see the color reproduced by your RGB LEDs.
    