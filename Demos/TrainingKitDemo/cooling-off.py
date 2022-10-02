import time
import config
from pylogix import PLC

with PLC() as comm:
	comm.IPAddress = config.cip["plc"]
	comm.Micro800 = True

	# Find the current temperature
	ret = comm.Read('Temperature_F')
	print("Current temperature:", ret.Value)
	ret = comm.Write('HMI_Cooling_Off', True)
	print("Stop cooling:", ret.Status)

	# Simulate a momentary write
	time.sleep(1)
	comm.Write('HMI_Cooling_Off', False)
	
	# Check cooling status
	ret = comm.Read('Cooling_Run')
	print("Cooling fan on:", ret.Value)
