import time
import config
from pylogix import PLC

with PLC() as comm:
	comm.IPAddress = config.cip["plc"]
	comm.Micro800 = True
	
	# Turn light off
	ret = comm.Write('Demo_Switch', True)
	print(ret.TagName, ret.Value, ret.Status)