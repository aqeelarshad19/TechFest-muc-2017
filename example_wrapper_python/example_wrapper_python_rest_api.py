import json
import time
import sys
import csv
import ctypes
sys.path.append("../../../../wrappers/python")
from wrapper_python2 import *
from wrapper_python2.core import *
from wrapper_python2.device import *
from wrapper_python2.color import *
from flask import Flask, jsonify , abort

app = Flask(__name__)

@app.route('/')
def index():
    global pSpecCore,pSpecDevice
    test_val = [['425.576958729', '400.0'], ['362.025757288', '401.0'], ['298.474555848', '402.0']]
    #ret =  (str(get_data()))
    #close_sensor(pSpecCore,pSpecDevice)
    return jsonify(test_val)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
   # task = [task for task in tasks if task['id'] == task_id]
   # if len(task) == 0:
   #     abort(404)
    if str(task_id) is '1':
	print "Task-1"
	return jsonify({'Task':'Task-1'})
    if else str(tasl_id) is '2':
	print "Task-2"
        return jsonify('Task':'Task-2')

    else:
	print "Unknown task"
        return jsonify('Task':'Task-3')
    #print "task id: " + str(task_id)
    #return jsonify({'task': '1'})

#return "Hello, World!

#Initialization
initialize("../Libs/libCrystalBase_RPi.so")
pSpecCore      = initialize_core_api("../Libs/libCrystalCore_RPi.so")
pSpecDevice    = initialize_device_api("../Libs/libCrystalPort_RPi.so")

pSensorInited = False
pSesnorFound  = 0

def close_sensor(pSpecCore,pSpecDevice):
    global pSensorInited
    close_color_api(pSpecCore)
    close_core_object(pSpecCore)
    disconnect_device(pSpecDevice)
    pSensorInited = False

def sensor_init():
    global pSensorInited
    initialize_color_api(pSpecCore)
    connectReturn   = connect_device(pSpecDevice)   # return total num of devices connected with system

    if connectReturn > 0:

        (ret, sensorID) = get_sensor_id_device(pSpecDevice)

	create_core_object(pSpecCore)

	csInit_Return = load_sensor_file(pSpecCore, b"../config/sensor_" + sensorID + b".dat")

	(ret, sensorID) = get_sensor_id_file(pSpecCore)

	get_sensor_parameters_from_device(pSpecDevice)

	(adcGain,adcRange) = get_sensor_parameters_from_calibration_file(pSpecCore)

	settingReturn = set_sensor_parameters_to_device(pSpecDevice,adcGain,adcRange)

	total_num_of_sensors = total_sensors_connected(pSpecDevice)

	get_capacity_sensor_data_list(pSpecCore)
	pSensorInited = True
	return True
    else:
	pSensorInited = False
	return False

def get_data():
    global pSensorInited
    if pSensorInited is False:
        print "Not inited..."
	ret = sensor_init()
	while ret is False:
	    print ("Not inited ... retry ")
	    time.sleep(10)
	    ret = ensor_init()
    print ("Sensor inited...")
    #while pSensorInited is False:
#	print ("Sensor not inited..")#
#	ret = sensor_init()
#	if ret is True:
#	    break
#	print "Sensor not inited... wait 5 sec."
#	time.sleep(5)
#    get_capacity_sensor_data_list(pSpecCore)
    total_num_of_sensors = total_sensors_connected(pSpecDevice)
    for index in range(total_num_of_sensors):

        #activate a specific device(sensor)
        activatingReturn = index_activation(pSpecDevice,index)

        #get sensor id of currently activated device(sensor)
        (ret, sensorID) = get_sensor_id_device(pSpecDevice)

        #get and set shutter speed of device(sensor)
        get_shutter_speed(pSpecDevice)
        set_shutter_speed(pSpecDevice,1)

        #get one filter output (sensor data)
        filterData = get_filter_data(pSpecDevice,20)

        #set background data
        set_background_data(pSpecCore,filterData)

        #get and set shutter speed of device(sensor)
        get_shutter_speed(pSpecDevice)

        valid_filters_num = get_num_of_valid_filters(pSpecCore)
        valid_filters = get_valid_filters(pSpecCore)

        #Get shutter speed with AE
        newSS = get_optimal_shutter_speed(pSpecDevice,valid_filters_num,valid_filters)
        set_shutter_speed(pSpecDevice,newSS)

        #convert shutter speed to exposure time (ms) for your reference
        ss_to_exposure_time(pSpecDevice,5,newSS)

        filterData = get_filter_data(pSpecDevice,20)

        specSize = get_spectrum_length(pSpecCore)
        (ret, specData,wavelengthdata) = calculate_spectrum(pSpecCore,filterData,newSS)

        (Start_Wavelength, End_Wavelength, Interval_Wavelength) = get_wavelength_information(pSpecCore)

       # get_resolution(pSpecCore)
	print  ("Wavelen len Data: "+str(Start_Wavelength) + str(End_Wavelength) +str(Interval_Wavelength))
        print ("Wave Len Data: " + str(wavelengthdata))
	print ("specData: "+str(specData))
	colorData = calculate_color_data(pSpecCore,specData, wavelengthdata,specSize)

        fileName = (r"SpecrtumData2_" + sensorID + ".csv");
        data = []
        data_wav = []
        data_comb = []
        for i in range(get_spectrum_length(pSpecCore)):
	    data.append(str(specData[i]).split(","))
	    data_wav.append(str(wavelengthdata[i]).split(","))
	    data_comb.append([str(specData[i]) , str(wavelengthdata[i])])
	#print (specData[i])
        print ("Data len:" + str(len(data)) + " " + str(len(data_wav)))
        #print (data)
        print (data_comb)
        with open(fileName, "wb") as csv_file:
	   writer = csv.writer(csv_file, delimiter=',')
	   for line in data_comb:
	       writer.writerow(line)
        csv_file.close()
	return data_comb
#print "Start the script"
#sensor_init()
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")

#print "Start the script"
#sensor_init()
#print (get_data())
#time.sleep(5)
#print (get_data())
#time.sleep(5)
#print (get_data())
#time.sleep(5)
#print("Close the sensor")
#close_sensor(pSpecCore,pSpecDevice)
#else:
#    print ("**********************************************************************")
#    print ("[PrismError]Device Not Connected. Please connect Device and try again.")
#    print ("**********************************************************************")
#close_color_api(pSpecCore)
#close_core_object(pSpecCore)
#disconnect_device(pSpecDevice)
