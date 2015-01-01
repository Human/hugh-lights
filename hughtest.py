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

import time, unittest

class AllTests(unittest.TestCase):

    def setUp(self):
        print "setUp"
        self.myHugh = Hugh("/home/pi/hugh/hugh_config.ini", "/home/pi/hugh/rgb")

    def _get_rgb(self):
        return [ self.myHugh.pi.get_PWM_dutycycle(pin) for pin in self.myHugh.pins ]

    def _check_rgb(self, expected):
        self.assertEqual(expected, self._get_rgb())

    def _test_targets(self, targets):
        for target in targets:
            expected = [ int(self.myHugh.color_correction[i] * target[i]) for i in range (0, 3) ]
            print "expect",expected,"from target",target
            self.myHugh.fade_to_rgb(target, fade_through_black=False, instant=False)
            self._check_rgb(expected)

    def test_target_1(self):
        """
        A regression test for this bug, with color correction of 1,0, 0.55, 0.55:
        
        rgb [255, 123, 15]
        current_rgb 255 67 8 <-- OK
        
        rgb [37, 255, 233]
        current_rgb 37 73 120 <-- BUG: should be 37, 140, 128
        
        Observation: Only the color furthest from its target reached its target; the others were set to their diffs.
        """
        print "target_1"
        self.myHugh.color_correction = [ 1.0, 0.55, 0.55 ]
        self.myHugh.increment_count = 255

        targets = [ [0,0,0], [255,123,15], [37,255,233] ]
        self._test_targets(targets)

    def test_transitions(self):
        """
        A very long test that picks many combinations of color correction, increment count, and color targets,
        and verifies that transitions to the color targets result in the expected values of each color.
        """
        print "transitions"

        for red_correction in range (0, 101, 25):
            for green_correction in range (0, 101, 25):
                for blue_correction in range (0, 101, 25):

                    self.myHugh.color_correction = [ red_correction / 100.0, green_correction / 100.0, blue_correction / 100.0 ]
                    print "color_correction",self.myHugh.color_correction

                    for increment_count in range (1, 256, 51):
                        self.myHugh.increment_count = increment_count
                        print "increment_count",increment_count

                        self._test_targets([[0,0,0],[127,127,127],[255,255,255]])
                    

    def test_range(self):
        """
        A simple test that each pin can be set to any brightness, from 0-255. Color correction is not involved here.
        """
        print "range"
        for pin in self.myHugh.pins:
            print " pwm pin", pin
            for bright in range (0, 256):
                self.myHugh.pi.set_PWM_dutycycle(pin, bright)
                self.assertEqual(bright, self.myHugh.pi.get_PWM_dutycycle(pin))
                #print "pin",pin,"at",bright
                time.sleep(0.03)

            for bright in range (254, -1, -1):
                self.myHugh.pi.set_PWM_dutycycle(pin, bright)
                self.assertEqual(bright, self.myHugh.pi.get_PWM_dutycycle(pin))
                #print "pin",pin,"at",bright
                time.sleep(0.03)

if __name__ == '__main__':
    unittest.main()
