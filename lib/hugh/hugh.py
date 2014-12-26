"""
Copyright (C) 2014 Bob Igo, http://bob.igo.name, bob@igo.name

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import pigpio, time, csv, os, ConfigParser

class Hugh():

    def __init__(self, config_file, rgb_csv_file):
        self.pi = pigpio.pi() # local device GPIO

        # Config parsing
        self.timestamps = [0.0, 0.0] # when configuration files were last updated
        self.config_files = [ config_file, rgb_csv_file ]

        self.color_correction = None

        self.fade_through_black = None
        self.instant = None

        self.freq = None
        self.pins = None
        
        self.scp = ConfigParser.SafeConfigParser()
        self.configure()

        self.init_pins()
        self.set_frequency()

    def fade_to_rgb(self, target_rgb, fade_through_black=True, instant=False):
        target_rgb = [ int(target_rgb[i] * self.color_correction[i]) for i in range (0, 3) ]
        print "target_rgb",target_rgb

        if instant: # jump directly to the new color; no fading
            for i in range (0, 3):
                self.pi.set_PWM_dutycycle(self.pins[i], target_rgb[i])
            return
        
        if fade_through_black: # fade to black before fading to the new color
            self.fade_to_rgb([0,0,0], fade_through_black=False)

        source_rgb = [ self.pi.get_PWM_dutycycle(self.pins[i]) for i in range (0, 3) ]
        current_rgb = source_rgb
        increments = [ (target_rgb[i] - current_rgb[i]) / 255.0 for i in range (0, 3) ]

        print "increments",increments
        
        for chg in range (1, 256): # max of 255 levels; normalize fading for this many increments
            # For each tick, the color should change 1/255th of the diff between source and target
            for i in range (0, 3):
                target = source_rgb[i] + int(increments[i] * chg)
                    
                #print i,"changes at",chg,"to",target

                self.pi.set_PWM_dutycycle(self.pins[i], target)

            current_rgb = [ self.pi.get_PWM_dutycycle(self.pins[i]) for i in range (0, 3) ]

        print "current_rgb", current_rgb

    def configure(self):
        """See if the configuration file has changed. If so, parse it and load in its values."""
        new_ts = os.stat(self.config_files[0]).st_mtime
        if new_ts != self.timestamps[0]:
            self.timestamps[0] = new_ts
            self.parse_config()

    def parse_config(self):
        """Parse the configuration file and load in its values."""
        self.scp.read(self.config_files[0])

        # GPIO
        pins = [ self.scp.getint('gpio', 'red'),
                 self.scp.getint('gpio', 'green'),
                 self.scp.getint('gpio', 'blue') ]
        if self.pins is None:
            self.pins = pins
        else:
            if self.pins != pins:
                # release previous GPIO pins from PWM
                for pin in self.pins:
                    self.pi.set_PWM_dutycycle(pin, 0) # PWM off
                    self.pi.set_PWM_frequency(pin, 0) # 0 Hz

                print "WARNING: GPIO pins changed to",pins,"from",self.pins
                self.pins = pins
                self.init_pins()

        freq = self.scp.getint('gpio', 'freq')
        if self.freq is None:
            self.freq = freq
        else:
            if self.freq != freq:
                print "INFO: frequency changed to",freq,"Hz from",self.freq,"Hz"
                self.freq = freq
                self.set_frequency()

        # transition
        instant = self.scp.getboolean('transition', 'instant')
        if self.instant is None:
            self.instant = instant
        else:
            if self.instant != instant:
                print "INFO: instant transition changed to",instant,"from",self.instant
                self.instant = instant
 
        fade_through_black = self.scp.getboolean('transition', 'fade_through_black')
        if self.fade_through_black is None:
           self.fade_through_black = fade_through_black
        else:
            if self.fade_through_black != fade_through_black:
                print "INFO: fade through black transition changed to",fade_through_black,"from",self.fade_through_black
                self.fade_through_black = fade_through_black

        # color correction
        color_correction = [ self.scp.getfloat('color_correction', 'red'),
                             self.scp.getfloat('color_correction', 'green'),
                             self.scp.getfloat('color_correction', 'blue') ]

        for correction in color_correction:
            if correction > 1.0 or correction < 0.0:
                print "ERROR: color correction value of",correction,"is out of range. It must be between 0.0 and 1.0 inclusive."
                return
            
        if self.color_correction is None:
            self.color_correction = color_correction
        else:
            if self.color_correction != color_correction:
                print "INFO: color correction changed to", color_correction, "from", self.color_correction
                self.color_correction = color_correction
                self.parse_rgb_csv()

    def parse_rgb_csv(self):
        """Parse the RGB CSV file and apply the target color."""
        with open(self.config_files[1]) as csvfile:
            rgbreader = csv.reader(csvfile)
            for row in rgbreader:
                rgb = [ int(float(i)) for i in row ]
                #print "row",row
                #print "rgb",rgb
                if len(rgb) == 3:
                    self.fade_to_rgb(rgb, fade_through_black=self.fade_through_black, instant=self.instant)


    def init_pins(self):
        """Initializes the three GPIO pins for output at the configured PWM frequency."""
        for pin in self.pins:
           #print "pin", pin
           self.pi.set_mode(pin, pigpio.OUTPUT)
           self.pi.write(pin, 0)
           self.pi.set_PWM_dutycycle(pin, 0) # PWM off

    def set_frequency(self):
        """Set the PWM frequency."""
        for pin in self.pins:
           self.pi.set_PWM_frequency(pin, self.freq)

    def run(self):
        """Monitor the config files for changes, then parse them and update accordingly."""
        while True:
            for i in (0, 1):
                new_ts = os.stat(self.config_files[i]).st_mtime
                if new_ts != self.timestamps[i]:
                    self.timestamps[i] = new_ts
                    if i==0: # ini file
                        self.parse_config()
                    else: # RGB CSV file
                        self.parse_rgb_csv()

            time.sleep(0.05)

    def rainbow_demo(self):
        rainbow = [[255, 0, 0], [255, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [127, 0, 255], [0, 0, 0]]
        for color in rainbow:
            self.fade_to_rgb(color, False, False)
            time.sleep(3)

    def christmas_demo(self):
        redgreen = [[255, 0, 0], [0, 255, 0]]
        while True:
            for color in redgreen:
                self.fade_to_rgb(color, True, False)

