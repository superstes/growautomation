<br>
<p align="center">
  <img src="https://www.growautomation.eu/img/svg/ga02c.svg" width="65%"/>
</p>
<br><br>

The goal is to automate activities related to the cultivation of plants.

And thus to minimize the associated repetitive tasks and optimize the process.

It's simple. And should also remain so if you have little time for it.

## Thoughts about growing

- It should not be necessary to check if the plants need water.
  - Watering should be done automatically but only when necessary.

- Nor should there be a need to know if the temperature is optimal.
  - Windows should open when it is too hot and close when it gets colder.

- A storm is coming?
  - The windows should close by themselves.

- Would you like to know what conditions have led to more or less yield?
  - We should analyze the data and find correlations.
  - That's how we can learn from our mistakes.

- Want to know how your plants are doing?
  - Just check the stats on the website - comfortably from your smartphone.

## Contact
<a href="mailto:contact@growautomation.eu">contact@growautomation.eu</a>

## Documentation
<img src="https://readthedocs.org/projects/growautomation/badge/?version=latest&style=plastic"/>
<a href="https://docs.growautomation.eu">docs.growautomation.eu</a>

## Version
__The code is currently not in a stable state !__

Version: 0.8

=> <a href="https://demo.growautomation.at/">DEMO</a> at its current state _(bugs included.. (; )_

### Work in progress
- testing and fixing input-condition-output workflow
- writing ansible-script to set-up the application


### History
- v0.7 _(2020-12 - 2021-03)_
  - created basic _(django)_ web interface => <a href="https://demo.growautomation.at/">DEMO</a>
    - functionality:
      - config management
      - system management _(systemd / logs)_
      - help users test and debug their setup
      - customizable statistics/graphs
  - updated core to use django mysql schema

- v0.6 _(2020-11 - 2020-12)_
  - object-oriented config management
  
- v0.3 - v0.5 _(2020-02 - 2020-10)_
  - optimized code via implementing classes
  - created a systemd service to run the core
  
- v0.1 - v0.2 _(2019-05 - 2020-01)_
  - creating basic code structure _(functional programming)_

- v0.0 _(2018-� - 2019-04)_
  - dark age _(connected scripts)_

### Planned features
- plant monitoring via nfc-tags and harvest-scale => <a href="https://www.youtube.com/watch?v=13X_MqCHwgE">idea source</a>
- documentation via sphinx _(read the docs)_
- documenting clean hardware setup _(easy wiring via patchpanel)_
- implementing more input _(sensors)_, output _(actors)_ and connection devices for native support _(air speed sensor/window opener actor/analog to digital converter)_
- builtin notification tasks
  - *get notified if the temperature is not optimal for growing*
- creating how-to videos on <a href="https://www.youtube.com/channel/UCLJyDlo3Z6eP_X2Pw0-Z8Pw">YouTube</a>

### Maybe future features
- agent/server installation
  - server should be able to run as vm or on dedicated hardware
  - cloud-hosted server component
- create plans for 3d printable parts
