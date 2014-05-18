Racing Line
===========

Racing Line is a simple plugin for Assetto Corsa, it traces the racing line of
the current lap and best lap so you can compare trajectories, etc.

## Features
Right now it supports the following features:
 * Trace the best lap racing line in grey, and the current racing line: segments faster than the best lap are green, and segments slower are in red
 * Zoom in and out the racing line
 * Display the current speed and the speed at the same point of the track in the best lap, as well as the current best recorded lap time
 * Widget to show if any of the wheels are locked (top right corner)
 * Dump all lap data to [JSON](http://en.wikipedia.org/wiki/JSON) file in an *exports* folder where the plugin is installed. This is relatively untested, so beware. Lap data is stored uncompressed for now, so be careful: the dump files can grow pretty large!


![Screenshot](/data/racingline-screenshot.jpg?raw=true)

## Roadmap

Future plans include saving the best lap to file so it can be reused in a future session, and actually doing something with the exported data, possibly through a web interface. You can find a [brain dump](https://github.com/mathiasuk/racingline/wiki/Roadmap) in the wiki.

## Known issues

I use the ac.getLastSplits() call to identify if the previous lap was complete, however there seems to be a bug in multiplayer as it always return 0. So for now the app will work fine in multi, but best laps won't be saved.

## Installation

For now simply download the [latest zip release](https://github.com/mathiasuk/racingline/archive/v0.2.0.zip) and unzip it in:

*Your steam folder*\steamapps\common\assettocorsa\apps\python

You will also need to rename the **racingline-master-0.2.0** folder to **racingline**
for the plugin to be recognised by Assetto Corsa

To quote the GPL: *This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.*

So yeah, it might make a mess in your kitchen, drink your beer and still your wife. But most likely it will just work and if something goes wrong it might crash.
In any case feel free to [submit bug report or suggestions](https://github.com/mathiasuk/racingline/issues).

Have fun!
