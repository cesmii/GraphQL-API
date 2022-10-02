import os

def measure_int_temp():
	temp = os.popen("vcgencmd measure_temp").readline()
	temp = temp.replace("temp=", "")
	temp = temp.replace("'C", "")
	temp = temp.replace("\n", "")
	return float(temp)

if __name__ == "__main__":
	print(measure_int_temp())
