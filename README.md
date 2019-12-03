# Quietpaper - Smart Home Display Project

![The display front view](doc/front.jpg)

This is a passion project that realizes an Raspberry-Pi-based smart home display 
using the [3-color Waveshare e-Paper Display 7.5 inch](https://www.waveshare.com/w/upload/b/b6/7.5inch-e-paper-specification.pdf).
I wanted to make a device my smart home control station that does not emit blueish light,
that is quiet and does not listen or talk (unlike Alexa, Google & co.) and generally
provides a zen-like user experience and still integrates well with various APIs. Here
now the code is, ready to be used and extended by you!

The application structure is modular and supports multiple **widgets** (as information
windows) and **displays** (as information projection screen) so integration into other
media is feasible (for example, currently the image is not only shown on the e-paper
display but also saved as PNG and uploaded to Google-Docs for remote-display).

The application is developed as Python application that can be run as a linux
daemon and update the system at regular times (currently multiples of 5 minute steps
which I found best for the slow refresh cycles of the Waveshare display).

The application also talks to a concurrently running NodeJs application 
(called **hafasglue**) in order to interface with the German "Deutsche Bahn" public 
transit API "Hafas". You can forego this concurrently running application and configure 
the corresponding widget to retrieve data from the Google Directions API instead - which
is unfortunately not for free but (given that API calls are not cached) rather pricey.

Here are some other libraries and projects that were helpful and/or whose code I 
ended up incorporating into this project:

* [`rgerganov/py-air-control`](https://github.com/rgerganov/py-air-control/) - Command
  Line App for controlling Philipps Air Purifier - modified version stored at 
  `quietpaper/iot/airctrl.py`
* [`public-transport/hafas-client`](https://github.com/public-transport/hafas-client/blob/4/docs/journeys.md) - 
  Hafas is the German "Deutsche Bahn" system that provides the electronic 
  public transit timetables and this is a NodeJs client of of their
  rather clunky XML Webservice. The client is supplied as a much leaner
  REST-API by my NodeJs servlet in `hafasglue`.
* [`momorientes/istheutefeinstaubalarm`](https://github.com/momorientes/istheutefeinstaubalarm) - 
  my town Stuttgart, Germany provides "Smog Alerts" on which days we should 
  leave our cars at home, use public transit for lower price (in some cases
  even for free) and cannot use "recreational home fireplaces". This project
  provided the inspiration on how to query if such a smog alert is currently
  in effect: by scraping the city's minimalistic mobile-phone widget HTML page.
* [Tado API Guide - updated for 2019](https://shkspr.mobi/blog/2019/02/tado-api-guide-updated-for-2019/) - 
  huge help in understanding how to query the undocumented API of my tado thermostats.

## Install / Run

![The display cabeling](doc/guts.jpg)

1. You need the following prequisites:
* Raspbian Stretch Image
* Python 3 Installation
* Node Version Manager or Node Package Manager
* Display connected to Raspberry

2. Next, if you want to use all widgets exactly in the layout I use you can just copy
the folder `secret.template`, rename it to `secret` and open the config files within
replacing all access keys, passwords and personal data with values that apply to your
situation.

3. If you would like another configuration, you might want to develop own widgets or 
re-arrange them. For this, see the next chapters. You might at least want to edit
the file `quietpaper/config.py` which sets the layout of the widgets on the display.

4. You can then install both the `quietpaper` daemon (Python app which updates the display) 
and the `hafasglue` daemon (Node-JS servlet which talks to Hafas in order to retrieve
public transit information) by calling:
```
./install-and-autorun.bash
```

5. The display will now load! - You can start/stop/restart the daemons by calling
```
sudo service {start|stop|restart} {quietpaper|hafasglue}
```
... or, after stopping the services, run them directly with:
```
./hafasglue.bash
./quietpaper.bash
```

## Widgets

![The picture frame back with all the cabeling](doc/back.jpg)

The core of this project are its "widgets", the different information snippets
displayed. The following widgets are developed (and stored in the subfolder
`quietpaper/widgets`):

* `allergy.py`: air quality as reported by Philipps Air Purifier and
  (potentially sometime) also the air quality reported outdoors on "some" public 
  website
* `cal.py`: the next appointment on some Google calendar
* `clock.py`: time and date
* `commute.py`: upcoming routes from your home into the city assuming a 
  "bus -> train -> city" route (as it is the case in my current home)
* `monitor.py`: small symbols indicating if some of your electronic devices
  are running (Network Attached Storage, VPN, internet connection)
* `office.py`: showing (for work-life-balance-purposes ONLY) the time of your
  first appointment at work in the morning (and hiding the title etc. in order
  not to break you out of your home-sweet-home feel); uses either 
  a Google Docs Sheet (which you can fill by other means) or a Google
  Calendar as source for this information
* `room.py`: room climate information from tado thermostats including 
  temperature, warm-up/cool-down indicator, window-open indicator and 
  humidity as well as humidity "alarm"
* `separator.py`: a straight horizontal line
* `smog.py`: indicates whether the city of Stuttgart currently has a smog alert
  or not
* `trashday.py`: displays whether it is a day where we should put out the
  garbage to be picked up
* `wheather.py`: weather information from https://api.openweathermap.org

## Develop

![The remote development UI](doc/backstage.jpg)

If you want to modify this project and/or adapt it to your need, here are some
pointers about the repo's directory structure:

* `data` - contains static data displayed by some widgets, e.g. the dates used by
  the `trashday.py` widget
* `doc` - contains artifacts for this document
* `fonts` - fonts used on the display
* `hafasglue` - logic for the hafasglue NodeJs servlet
* `icons` - bmps and gifs of the icons displayed on screen (only bmps are actually
  used in the code)
* `log` - directory where log is stored
* `output` - directory where png images are stored for debug purposes
* `quietpaper` - the main python application (python module) with the following 
  submodules
  * `iot` - logic to interface with devices (e-paper display, air purifier, tado
    thermostat)
  * `screens` - classes that provide interfaces for displaying the final image
  * `widgets` - classes that retrieve information from other sources and render
    it onto the screen
* `secret.template` - template of config files that contain all necessary access
  keys, passwords and personal information. Before launching the application
  copy this directory to `secret` and replace all placeholders

For development on Raspberry Pi, I recommend Visual Studio Code with Remote 
Development Extension as well as NoMachine to login to the Raspberry. Happy 
Developing!
