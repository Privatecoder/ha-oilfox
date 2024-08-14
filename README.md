# ha-oilfox
HomeAssistant Sensor for OilFox using the official customer API.

If you habe some problems or ideas just let me know!

## Setup
It is listed in HACS, just search for "OilFox".
If you prefer the manual installation, it is done like other custom components :)

## Configuration
Please use the configuration flow in system - settings - integration

**Important:** the yaml configuration has been removed in version 1.0.1 release! Please use the config flow. 

## Options
Option Flow since version 1.0.1 to modify the http timeout:
<img width="752" alt="image" src="https://github.com/chises/ha-oilfox/assets/10805806/3d698bbb-aee5-4a67-9bb2-416324ab1100">

```
2022-09-17 17:12:31.584 WARNING (MainThread) [custom_components.oilfox.sensor] Import yaml configration settings into config flow
```
## Result
After installing the component and configure the sensor new entities will be added. Something like *sensor.oilfox_hadwareid_sensor*

Multiple Devices on the OilFox account are supported.

  ![image](https://user-images.githubusercontent.com/10805806/194892834-1a8dcb4c-32e9-455b-94cd-aae02347baac.png)

  ![image](https://user-images.githubusercontent.com/10805806/209467761-0445c376-cf6f-477a-8acc-b4f3d9875a49.png)

## Logging
### Option 1 GUI
Enable the Debug Log in the Intergration Menu available in Settings - Integration - OilFox

  ![image](https://github.com/chises/ha-oilfox/assets/10805806/f938acdb-987a-49fb-9e24-023b5e617755)

### Option 2 Config File
For debug log messages you need to adjust the log config for custom_components.oilfox.sensor based on the [HA documentation](https://www.home-assistant.io/integrations/logger/)
Example configuration.yaml
```
logger:
  default: info
  logs:
    custom_components.oilfox: debug
```

## Battery Entity
The [API](https://github.com/foxinsights/customer-api/tree/main/docs/v1) only provides text based battery status. In order to convert them into some numeric values I used the following mapping:
```
FULL = 100%
GOOD = 70%
MEDIUM = 50%
WARNING" = 20%
CRITICAL = 0%
```

These values should work with [Low battery level detection & notification for all battery sensors](https://community.home-assistant.io/t/low-battery-level-detection-notification-for-all-battery-sensors/258664).

## validationError Entity
The [API](https://github.com/foxinsights/customer-api/tree/main/docs/v1) provides text based validationError status. Used the mappings based on the Documentation:
```
NO_METERING =	No measurement yet
EMPTY_METERING = Incorrect Measurement
NO_EXTRACTED_VALUE = No fill level detected
SENSOR_CONFIG = Faulty measurement
MISSING_STORAGE_CONFIG = Storage configuration missing
INVALID_STORAGE_CONFIG = Incorrect storage configuration
DISTANCE_TOO_SHORT = Measured distance too small
ABOVE_STORAGE_MAX = Storage full
BELOW_STORAGE_MIN = Calculated filling level implausible
```


## Background
This component is using the official [OilFox customer Api](https://github.com/foxinsights/customer-api)

As this is my first homeassistant component there is a lot to impove. If I have time I will try to get this component more to the [homeassisant recommendations](https://developers.home-assistant.io/docs/creating_component_code_review/)

## Contributors
<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=chises/ha-oilfox" />
</a>
