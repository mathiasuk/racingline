Racing Line
===========

Racing Line is a simple plugin for Assetto Corsa, it traces the racing line of
the current lap and best lap so you can compare trajectories, etc.

## Features
Right now it supports the following features:
 * Trace the current racing line (in red) and the best lap racing line (in green)
 * Display the current speed and the speed at the same point of the track in the best lap
 * Widget to show if any of the wheels are locked (top right corner)
 * Dump all lap data to [JSON](http://en.wikipedia.org/wiki/JSON) file in an *exports* folder where the plugin is installed. This is relatively untested, so beware. Lap data is stored uncompressed for now, so be careful: the dump files can grow pretty large!


![Screenshot](/data/racingline-screenshot.jpg?raw=true)

## Roadmap

Future plans include saving the best lap to file so it can be reused in a future session, and actually doing something with the exported data, possibly through a web interface. You can find a [brain dump](wiki/Roadmap) in the wiki.

## Installation

For now simply download the [latest zip](https://github.com/mathiasuk/racingline/archive/master.zip) and unzip it in:

*Your steam folder*\steamapps\common\assettocorsa\apps\python

You will also need to rename the **racingline-master** folder to **racingline**
for the plugin to be recognised by Assetto Corsa

To quote the GPL: *This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.*

So yeah, it might make a mess in your kitchen, drink your beer and still your wife. Bust most likely it will just work and if something goes wrong it will crash.
In any case feel free to [submit bug report or suggestions](https://github.com/mathiasuk/racingline/issues).

Have fun!
