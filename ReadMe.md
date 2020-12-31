<br>
<p align="center">
  <img src="https://www.growautomation.eu/img/png/ga02.png" width="65%"/>
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
<a href="mailto:contact@growautomation.at">contact@growautomation.at</a>

## Version

__The code is currently not in a stable state !__

Version: 0.7

### Work in progress
- creating _(django)_ web interface for easy user interactions
    - <a href="https://test.growautomation.at/">DEMO LINK</a>
    - updating growautomation core to work with django database schema


### History
- v0.6 _(2020-11 - 2020-12)_
  - object-oriented config management
  
- v0.3 - v0.5 _(2020-02 - 2020-10)_
  - optimized code via implementing classes
  - created a systemd service to run the core
  
- v0.1 - v0.2 _(2019-05 - 2020-01)_
  - creating basic code structure _(functional programming)_

### Planned features
- implementing unit and integration tests
- documentation via sphinx _(read the docs)_
- web interface for easy user interactions
  - customizable statistics/graphs for data visualization
- documenting clean hardware setup _(easy wiring via patchpanel)_
- implementing more input _(sensors)_, output _(actors)_ and connection devices for native support _(air speed sensor/window opener actor/analog to digital converter)_
- builtin notification tasks
  - *get notified if the temperature is not optimal for growing*
 
### Maybe future features
- agent/server installation
  - server should be able to run as vm or on dedicated hardware
  - cloud-hosted server component
- create plans for 3d printable parts
