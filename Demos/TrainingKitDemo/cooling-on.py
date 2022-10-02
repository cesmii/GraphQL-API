import time
import config
from pylogix import PLC

with PLC() as comm:
	comm.IPAddress = config.cip["plc"]
	comm.Micro800 = True

	# Find the current temperature
	ret = comm.Read('Temperature_F')
	print("Current temperature:", ret.Value)
	currTemp = ret.Value

	# Make setpoint colder than current temperature
	ret = comm.Write('Cooling_Setpoint_F', currTemp - 10)
	print("Set target temperature:", ret.Value, ret.Status)

	# Start cooling until setpoint is reached
	ret = comm.Write('HMI_Cooling_On', True)
	print("Start cooling:", ret.Status)
	# Simulate a momentary write
	time.sleep(1)
	comm.Write('HMI_Cooling_On', False)
	
	# Check cooling status
	ret = comm.Read('Cooling_Run')
	print("Cooling fan on:", ret.Value)
