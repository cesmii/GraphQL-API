import os
from smbus2 import SMBus
import time

#bus = SMBus(1)

def measure_int_temp():
	temp = os.popen("vcgencmd measure_temp").readline()
	temp = temp.replace("temp=", "")
	temp = temp.replace("'C", "")
	temp = temp.replace("\n", "")
	return float(temp)

def measure_ext_temp():
	with SMBus(1) as bus:
		temp = bus.read_i2c_block_data(0x40, 0xE3,2)
	time.sleep(0.1)
	cTemp = ((temp[0] * 256 + temp[1]) * 175.72 / 65536.0) - 46.85
	return round(cTemp, 1)

def measure_ext_humid():
	with SMBus(1) as bus:
		rh = bus.read_i2c_block_data(0x40, 0xE5, 2)
	time.sleep(0.1)
	humidity = ((rh[0] * 256 + rh[1]) * 125 / 65536.0) - 6
	return round(humidity, 1)

if __name__ == "__main__":
	print("Internal Temp:     " + str(measure_int_temp()))
	print("External Temp:     " + str(measure_ext_temp()))
	print("External Humidity: " + str(measure_ext_humid()))
