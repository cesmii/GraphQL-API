from flask import Flask
from datamonitorplus import *

app = Flask(__name__)

@app.route("/api/1/data")
def get_data():
	temp = measure_int_temp()
	return {
		"temperature": temp
	}

@app.route("/api/2/data")
def get_data_v2():
	i_temp = measure_int_temp()
	e_temp = measure_ext_temp()
	e_humid = measure_ext_humid()
	return {
		"int-temperature": i_temp,
		"ext-temperature": e_temp,
		"ext-humidity": e_humid
	}
