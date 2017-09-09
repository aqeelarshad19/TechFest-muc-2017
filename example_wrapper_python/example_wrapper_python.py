import sys
import csv
import ctypes
sys.path.append("../../../../wrappers/python")
if(sys.version_info[0] < 3):
    from wrapper_python2 import *
    from wrapper_python2.core import *
    from wrapper_python2.device import *
    from wrapper_python2.color import *
    print ("**********************************************************************")
    print ("[Python-2]        Python Version : ", sys.version_info.major, "." ,sys.version_info.minor , " Detected")
    print ("**********************************************************************")
else:
    from wrapper_python3 import *
    from wrapper_python3.core import *
    from wrapper_python3.device import *
    from wrapper_python3.color import *
    print ("**********************************************************************")
    print ("[Python-3]        Python Version : ", sys.version_info.major, "." ,sys.version_info.minor , " Detected")
    print ("**********************************************************************")

#Initialization
if sys.platform == 'win32':
    initialize("..\Libs\CrystalBase.dll")
    pSpecCore      = initialize_core_api("..\Libs\CrystalCore.dll")
    pSpecDevice    = initialize_device_api("..\Libs/CrystalPort.dll")
else:
    initialize("../Libs/libCrystalBase_RPi.so")
    pSpecCore      = initialize_core_api("../Libs/libCrystalCore_RPi.so")
    pSpecDevice    = initialize_device_api("../Libs/libCrystalPort_RPi.so")

initialize_color_api(pSpecCore)


connectReturn   = connect_device(pSpecDevice)   # return total num of devices connected with system

if connectReturn > 0:

    (ret, sensorID) = get_sensor_id_device(pSpecDevice)

    create_core_object(pSpecCore)

    if sys.platform == 'win32':
        csInit_Return = load_sensor_file(pSpecCore, b"..\config\sensor_" + sensorID + b".dat")
    else:
        csInit_Return = load_sensor_file(pSpecCore, b"../config/sensor_" + sensorID + b".dat")

    (ret, sensorID) = get_sensor_id_file(pSpecCore)

    get_sensor_parameters_from_device(pSpecDevice)

    (adcGain,adcRange) = get_sensor_parameters_from_calibration_file(pSpecCore)

    settingReturn = set_sensor_parameters_to_device(pSpecDevice,adcGain,adcRange)

    total_num_of_sensors = total_sensors_connected(pSpecDevice)

    get_capacity_sensor_data_list(pSpecCore)

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

        if sys.version_info[0] < 3:
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
        else:
            fileName = (b"SpecrtumData3_" + sensorID + b".csv");
            data = []
            for i in range(get_spectrum_length(pSpecCore)):
                data.append(str(specData[i]).split(","))

            with open(fileName, 'w', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for line in data:
                    filewriter.writerow(line)
            csvfile.close()
else:
    print ("**********************************************************************")
    print ("[PrismError]Device Not Connected. Please connect Device and try again.")
    print ("**********************************************************************")
close_color_api(pSpecCore)
close_core_object(pSpecCore)
disconnect_device(pSpecDevice)
