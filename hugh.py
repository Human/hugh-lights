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

myHugh = Hugh("/home/pi/hugh/hugh_config.ini", "/home/pi/hugh/rgb", "/home/pi/hugh/logging.conf")
myHugh.daemon()
#myHugh.rainbow_demo()
#myHugh.christmas_demo()
