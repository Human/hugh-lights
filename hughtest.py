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
from lib.hugh.hugh import Hugh

import time

# TODO: use pyunit

def test_1(self):
    """
    A regression test for this bug, with color correction of 1,0, 0.55, 0.55:

    rgb [255, 123, 15]
    current_rgb 255 67 8 <-- OK
    
    rgb [37, 255, 233]
    current_rgb 37 73 120 <-- WRONG: should be 37, 140, 128
    
    only the color furthest from its target reached its target; the others were set to their diffs
    """
    self.fade_to_rgb([0,0,0], fade_through_black=False, instant=False)
    self.fade_to_rgb([255, 123, 15], fade_through_black=False, instant=False) # should end up at 255, 67, 8
    self.fade_to_rgb([37, 255, 233], fade_through_black=False, instant=False) # should end up at 37, 140, 128

def test(self):
    for pin in self.pins:
        #print "pwm pin", pin
        for bright in range (0, 256):
            self.pi.set_PWM_dutycycle(pin, bright)
            #print "pin",pin,"at",bright
            time.sleep(0.03)

        for bright in range (254, -1, -1):
            self.pi.set_PWM_dutycycle(pin, bright)
            #print "pin",pin,"at",bright
            time.sleep(0.03)

myHugh=Hugh("/home/pi/hugh_config.ini", "/home/pi/rgb")
myHugh.test_1()
myHugh.test()
