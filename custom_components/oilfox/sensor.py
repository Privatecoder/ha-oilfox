"""Platform for sensor integration."""

from __future__ import annotations
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.sensor import (
    SensorEntity,
    PLATFORM_SCHEMA
)

from homeassistant.const import (
    PERCENTAGE,
    VOLUME_LITERS,
    TIME_DAYS
)

import requests
import logging
import time  
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
DOMAIN = "OilFox_api"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
SCAN_INTERVAL = timedelta(minutes=10)
TOKEN_VALID = 900
SENSORS = {
    "fillLevelPercent": [
        "fillLevelPercent",
        PERCENTAGE,
        "mdi:percent",
    ],
    "fillLevelQuantity": [
        "fillLevelQuantity",
        VOLUME_LITERS,
        "mdi:hydraulic-oil-level",
    ],
    "daysReach": [
        "daysReach",
        TIME_DAYS,
        "mdi:calendar-range",
    ],
    "batteryLevel": [
        "batteryLevel",
        PERCENTAGE,
        "mdi:battery"
    ],
    "validationError": [
        "validationError",
        None,
        "mdi:message-alert"
    ]
}

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    email = config[CONF_EMAIL]
    _LOGGER.info("OilFox: Setup User:"+email)
    password = config[CONF_PASSWORD] 

    OilFoxs_items = OilFoxApiWrapper(email,password).getItems()
    if OilFoxs_items == False:
        _LOGGER.error("OilFox: Could not fetch information through API, invalid credentials?")
        return False

    entities = [ ]
    for item in OilFoxs_items:
        _LOGGER.info("OilFox: Found Device in API:"+item['hwid'])
        for key in SENSORS.keys():
            if not item.get(key) == None:
                _LOGGER.info("OilFox: Create Sensor "+SENSORS[key][0]+" for Device"+item['hwid'])
                entities.append(OilFoxSensor(OilFox(email, password, item['hwid']),SENSORS[key]))
            elif key == "validationError":
                _LOGGER.info("OilFox: Create empty Sensor "+SENSORS[key][0]+" for Device"+item['hwid'])
                SENSORS["validationError"][0]="validationError"
                entities.append(OilFoxSensor(OilFox(email, password, item['hwid']),SENSORS[key]))
            else:
                _LOGGER.info("OilFox: Device "+item['hwid']+" missing sensor "+SENSORS[key][0])

    add_entities(entities, True)



class OilFoxSensor(SensorEntity):
    OilFox = None
    sensor = None
    battery_mapping = {
        "FULL": 100,
        "GOOD": 70,
        "MEDIUM": 50,
        "WARNING": 20,
        "CRITICAL": 0
    }
    validationError_mapping = {
        "NO_METERING": "No measurement yet",
        "EMPTY_METERING": "Incorrect Measurement",
        "NO_EXTRACTED_VALUE": "No fill level detected",
        "SENSOR_CONFIG": "Faulty measurement",
        "MISSING_STORAGE_CONFIG":"Storage configuration missing",
        "INVALID_STORAGE_CONFIG": "Incorrect storage configuration",
        "DISTANCE_TOO_SHORT": "Measured distance too small",
        "ABOVE_STORAGE_MAX": "Storage full",
        "BELOW_STORAGE_MIN": "Calculated filling level implausible"
    }

    def __init__(self, element, sensor):
        self.sensor = sensor
        self.OilFox = element
        self.OilFox.updateStats()
        self._state = None

    @property
    def icon(self) -> str:
        """Return the name of the sensor."""
        return self.sensor[2]

    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return "OilFox-"+self.OilFox.hwid+"-"+self.sensor[0]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "OilFox-"+self.OilFox.hwid+"-"+self.sensor[0]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self.sensor[1]

    @property
    def extra_state_attributes(self):
        """Return the attributes of the sensor."""
        additional_attributes={
            "Last Measurement": self.OilFox.state.get("currentMeteringAt"),
            "Next Measurement": self.OilFox.state.get("nextMeteringAt"),
            "Battery": self.OilFox.state.get("batteryLevel")
        }
        return additional_attributes

    def update(self) -> None:
        if self.OilFox.updateStats() == False:
            _LOGGER.error("OilFox: Error Updating Values for "+self.sensor[0]+" from Class!:"+str(self.OilFox.state))
        elif not self.OilFox.state == None and not self.OilFox.state.get(self.sensor[0]) == None:   
            _LOGGER.debug("OilFox: Update Values for "+self.sensor[0])    
            if self.sensor[0] == "batteryLevel":
                self._state = self.battery_mapping[self.OilFox.state.get(self.sensor[0])]
            elif self.sensor[0] == "validationError":
                self._state = self.validationError_mapping[self.OilFox.state.get(self.sensor[0])] 
            else:
                self._state = self.OilFox.state.get(self.sensor[0])
        elif self.sensor[0] == "validationError":
            self._state = "No Error"
        else:
            _LOGGER.error("OilFox: Error Updating Values!:"+str(self.sensor)+" "+str(self.OilFox.state))



class OilFoxApiWrapper:
    ## Wrapper to collect all Devices attached to the Account and Create OilFox 
    loginUrl = "https://api.oilfox.io/customer-api/v1/login"
    deviceUrl = "https://api.oilfox.io/customer-api/v1/device"
    
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
    def getItems(self):
        items = [ ]
        headers = { 'Content-Type': 'application/json' }
        json_data = {
            'password': self.password,
            'email': self.email,
        }

        response = requests.post(self.loginUrl, headers=headers, json=json_data)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
            headers = { 'Authorization': "Bearer " + self.access_token }
            response = requests.get(self.deviceUrl, headers=headers)
            if response.status_code == 200:
                items = response.json()['items']
                return items
        return False

        

class OilFox:
    #https://github.com/foxinsights/customer-api
    hwid = None
    password = None
    email = None
    access_token = None
    refresh_token = None
    update_token = None
    loginUrl = "https://api.oilfox.io/customer-api/v1/login"
    deviceUrl = "https://api.oilfox.io/customer-api/v1/device/"
    tokenUrl = "https://api.oilfox.io/customer-api/v1/token"

    def __init__(self,email, password, hwid):
        self.email = email
        self.password = password
        self.hwid = hwid
        self.state = None
        self.getTokens()
    
    def updateStats(self):
        notError = True
        if self.refresh_token is None:
            notError = self.getTokens()
            _LOGGER.debug("Update Refresh Token: "+str(notError))
        
        if int(time.time())-self.update_token > TOKEN_VALID:
            notError = self.getAccessToken()
            _LOGGER.debug("Update Access Token: "+str(notError))
        
        if notError:
            headers = { 'Authorization': "Bearer " + self.access_token }
            response = requests.get(self.deviceUrl+self.hwid, headers=headers)
            if response.status_code == 200:
                self.state = response.json()
                return True
        return False

    def getTokens(self):
        headers = { 'Content-Type': 'application/json' }
        json_data = {
            'password': self.password,
            'email': self.email,
        }

        response = requests.post(self.loginUrl, headers=headers, json=json_data)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
            self.update_token = int(time.time())
            return True
        _LOGGER.error("Get Refresh Token: failed")
        return False

    def getAccessToken(self):  
        data = {
            'refresh_token': self.refresh_token,
        }
        response = requests.post(self.tokenUrl, data=data)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
            self.update_token = int(time.time())
            return True
        _LOGGER.error("Get Access Token: failed")
        return False