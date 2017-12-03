import requests, json, time, grovepi, grove_rgb_lcd, random

post_url = 'https://vehilytics-proto-v2.herokuapp.com/readings'
test_device_id = 'test_device'
pot = 2
button = 3
lcd_text = 'Initializing'

grove_rgb_lcd.setText(lcd_text)
grove_rgb_lcd.setRGB(83, 109, 254) #mobile app accent colour

#JSON templates for the sensor types I'm supporting in this prototype
sensors = ['battery_voltage', 'oil_pressure']
sensor_templates = {}

battery_template = {}
battery_template['sensor_name'] = 'Battery Voltage'
battery_template['range_min'] = 12.7
battery_template['range_max'] = 13.6
battery_template['unit'] = 'V'

oil_template = {}
oil_template['sensor_name'] = 'Oil Pressure'
oil_template['range_min'] = 20
oil_template['range_max'] = 80
oil_template['unit'] = 'PSI'

sensor_templates[sensors[0]] = battery_template
sensor_templates[sensors[1]] = oil_template

#POSTs the reading to the web service
def publishReadings(selection):
  reading = getReading(sensors[selection%2])
  reading['device_id'] = (selection/2) + 1
  postToWebService(reading)
  time.sleep(0.5)

#Mimics getting a sensor reading from the vehicle
def getReading(sensor):
  dict = sensor_templates[sensor].copy()
  dict['value'] = generateValue(dict['range_min'], dict['range_max'])
  return dict

#Generates a random value around the range for the sensor reading
def generateValue(min, max):
  return round(random.uniform(min-3, max+1), 2)

def postToWebService(reading):
  r = requests.post(post_url, data=reading)
  print("content ~> " + str(json.loads(r.content)))
  print("status ~> " + str(r.status_code))

curr_selection = -1

while True:
  try:

    #Using potentiometer to determine the device id used 
    #and the sensor data transmitted
    pot_value = grovepi.analogRead(pot)
    if (pot_value / 256 != curr_selection):
      if (pot_value < 256):
        curr_selection = 0
        grove_rgb_lcd.setText('device_id = 1\n'+str(sensors[0]))
      elif (pot_value >= 256 and pot_value < 512):
        curr_selection = 1
        grove_rgb_lcd.setText('device_id = 1\n'+str(sensors[1]))
      elif (pot_value >= 512 and pot_value < 768):
        curr_selection = 2
        grove_rgb_lcd.setText('device_id = 2\n'+str(sensors[0]))
      else:
        curr_selection = 3
        grove_rgb_lcd.setText('device_id = 2\n'+str(sensors[1]))

    #Button press triggers the data to be published
    if (grovepi.digitalRead(button) == 1):
      publishReadings(curr_selection)

  except KeyboardInterrupt:
    exit(0)
