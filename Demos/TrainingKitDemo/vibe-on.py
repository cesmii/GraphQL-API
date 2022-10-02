import time
import config
from pylogix import PLC

with PLC() as comm:
	comm.IPAddress = config.cip["plc"]
	comm.Micro800 = True

	# Turn motor on
	ret = comm.Write('HMI_Motor_On', True)
	print(ret.TagName, ret.Value, ret.Status)
	# Simulate momentary write
	time.sleep(1)
	comm.Write('HMI_Motor_On', False)
	
	# Check motor status
	ret = comm.Read('Motor_Run')
	print("Running:", ret.Value)