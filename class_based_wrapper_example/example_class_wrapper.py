import os,csv,json,sys
sys.path.append("../../../../wrappers/python/python_class_based_wrapper/")

from CrystalBase import *
from CrystalCore import *
from CrystalPort import *
from CrystalColor import *

def main():

	try:
		base    = CrystalBase()
		device  = CrystalPort()
		core    = CrystalCore()
		color   = CrystalColor()

		json_data = {}

		if sys.platform == 'win32':
		    base.initialize_base_api("..\Libs\CrystalBase.dll")
		    core.initialize_core_api("..\Libs\CrystalCore.dll")
		    device.initialize_device_api("..\Libs/CrystalPort.dll")
		    color.initialize_color_api("..\Libs\CrystalCore.dll")
		else:
		    base.initialize_base_api("../Libs/libCrystalBase_RPi.so")
		    core.initialize_core_api("../Libs/libCrystalCore_RPi.so")
		    device.initialize_device_api("../Libs/libCrystalPort_RPi.so")
		    color.initialize_color_api("../Libs/libCrystalCore_RPi.so")

		connectReturn   = device.connect_device()   # return total num of devices connected with system

		if connectReturn > 0:

			(ret, sensorID) = device.get_sensor_id_device()

			core.create_core_object()

			if sys.platform == 'win32':
				calibration_file_path = b"..\config\sensor_" + sensorID + b".dat";

				if os.path.exists(calibration_file_path):
					csInit_Return = core.load_sensor_file(calibration_file_path)

				else:
					print ('*'*50)
					print ('[ERROR] Sensor Calibration file does not exists: ', calibration_file_path )
					print ('*'*50)
					return -1
			else:
				calibration_file_path = b"../config/sensor_" + sensorID + b".dat";

				if os.path.exists(calibration_file_path):
					csInit_Return = core.load_sensor_file(calibration_file_path)
				else:
					print ('*'*50)
					print ('[ERROR] Sensor Calibration file does not exists: ', calibration_file_path )
					print ('*'*50)
					return -1

			(ret, sensorID) = core.get_sensor_id_file()

			device.get_sensor_parameters_from_device()

			(adcGain,adcRange) = core.get_sensor_parameters_from_calibration_file()

			settingReturn = device.set_sensor_parameters_to_device(adcGain,adcRange)

			total_num_of_sensors = device.total_sensors_connected()

			core.get_capacity_sensor_data_list()

			for index in range(total_num_of_sensors):

				#activate a specific device(sensor)
				activatingReturn = device.index_activation(index)

				#get sensor id of currently activated device(sensor)
				(ret, sensorID) = device.get_sensor_id_device()

				#get and set shutter speed of device(sensor)
				device.get_shutter_speed()
				device.set_shutter_speed(1)

				#get one filter output (sensor data)
				filterData = device.get_filter_data(20)

				#set background data
				core.set_background_data(filterData)

				#get and set shutter speed of device(sensor)
				device.get_shutter_speed()

				valid_filters_num = core.get_num_of_valid_filters()
				valid_filters = core.get_valid_filters2()

				#Get shutter speed with AE
				newSS = device.get_optimal_shutter_speed(valid_filters,valid_filters_num)
				json_data['OptimalSS'] = newSS

				device.set_shutter_speed(newSS)

				#convert shutter speed to exposure time (ms) for your reference
				device.ss_to_exposure_time(newSS,5)

				filterData = device.get_filter_data(20)

				json_data['RawFilterData'] = list(filterData)

				core.get_resolution()

				specSize = core.get_spectrum_length()
				(ret, specData,wavelengthdata) = core.calculate_spectrum(filterData,newSS)


				json_data['SpectrumData'] = list(specData)
				json_data['WavelengthData'] = list(wavelengthdata)

				(Start_Wavelength, End_Wavelength, Interval_Wavelength) = core.get_wavelength_information()
				wavelengthDataDict = {}

				wavelengthDataDict['Start WL'] = Start_Wavelength
				wavelengthDataDict['End WL'] = End_Wavelength
				wavelengthDataDict['Internal WL'] = Interval_Wavelength

				json_data['Wavelength_Information'] = wavelengthDataDict

				colorData = color.calculate_color_data(specData, wavelengthdata,specSize)
				colorDict = {}

				colorDict['Red']     = colorData[0]
				colorDict['Green']   = colorData[1]
				colorDict['Blue']    = colorData[2]
				colorDict['large_X'] = colorData[3]
				colorDict['large_Y'] = colorData[4]
				colorDict['large_Z'] = colorData[5]
				colorDict['small_x'] = colorData[6]
				colorDict['small_y'] = colorData[7]
				colorDict['small_z'] = colorData[8]
				colorDict['CCT']     = colorData[9]
				json_data['Color'] =colorDict

				if sys.version_info[0] < 3:
					fileName = (r"SpecrtumData2_" + sensorID + ".csv");
					data = []
					for i in range(core.get_spectrum_length()):
					    data.append(str(specData[i]).split(","))

					with open(fileName, "wb") as csv_file:
					    writer = csv.writer(csv_file, delimiter=',')
					    for line in data:
					        writer.writerow(line)
					csv_file.close()

				else:
					fileName = (b"SpecrtumData3_" + sensorID + b".csv");
					data = []
					for i in range(core.get_spectrum_length()):
					    data.append(str(specData[i]).split(","))

					with open(fileName, 'w', newline='') as csvfile:
					    filewriter = csv.writer(csvfile, delimiter=',',
					                quotechar='|', quoting=csv.QUOTE_MINIMAL)
					    for line in data:
					        filewriter.writerow(line)

					csvfile.close()
			with open('SpectrumData.json', 'w') as outfile:
				json.dump(json_data, outfile,indent=4)

		else:
			print ("**********************************************************************")
			print ("[PrismError]Device Not Connected. Please connect Device and try again.")
			print ("**********************************************************************")

		color.close_color_api()
		core.close_core_object()
		device.disconnect_device()	
		#print(json_data)

	except (NameError,RuntimeError,TypeError,OSError,KeyError):
		print ("**********************************************************************")
		print ("[PrismException] Exception Happened")
		print ("**********************************************************************")
		color.close_color_api()
		core.close_core_object()
		device.disconnect_device()

if __name__=='__main__':
	main()
