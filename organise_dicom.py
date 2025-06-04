"""
Script : organize_dicom.py
Description : Organize DICOM files into folders based on patient name, series date, and modality.
Author : Arnaud Dieudonné
Date : 04/06/2025
Version : 1.1

Usage :
    python organise_dicom.py -i <input_folder>

Arguments :
    -i : Directory containing the NM DICOM files to process (required).

Example :
    python orgnize_dicom.py -i ./dicom_files
"""

import os
import pydicom
import datetime
import argparse
from shutil import move

def organize_dicoms_by_patient(folder_path,simulation_mode):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    def remove_empty_folders(path):
        for root, dirs, _ in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if (file.endswith(".DCM") or file.endswith(".dcm")) and not file.startswith("._"):
                file_path = os.path.join(root, file)
                try:
                    dicom_data = pydicom.dcmread(file_path)
                    PatientName = str(dicom_data.PatientName).replace("^", "_")
                    SeriesDate= str(dicom_data.get("SeriesDate"))
                    print(SeriesDate)
                    modality = str(dicom_data.Modality)
                    series_folder = os.path.join(folder_path, PatientName,SeriesDate,modality)
                    if not simulation_mode:
                        os.makedirs(series_folder, exist_ok=True)
                        move(file_path, os.path.join(series_folder, file))
                    print("Move: ", file_path," to ", os.path.join(series_folder, file))
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if (file.endswith(".DCM") or file.endswith(".dcm")) and not file.startswith("._"):
                file_path = os.path.join(root, file)
                try:
                    dicom_data = pydicom.dcmread(file_path)
                    PatientName = str(dicom_data.PatientName).replace("^", "_")
                    SeriesDate= str(dicom_data.get("SeriesDate"))
                    modality = str(dicom_data.Modality)
                    if modality=="NM":
                        injection_date_time = datetime.datetime.strptime(dicom_data.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime.split('.')[0],'%Y%m%d%H%M%S')
                        scan_date_time = datetime.datetime.strptime(dicom_data.AcquisitionDate + dicom_data.AcquisitionTime.split('.')[0],'%Y%m%d%H%M%S')
                        DelayInDays = round((scan_date_time - injection_date_time).total_seconds() / 3600 / 24,0)
                        parent_folder = os.path.dirname(os.path.dirname(file_path))
                        patient_folder = os.path.dirname(parent_folder)
                        new_parent_folder = os.path.join(patient_folder,"J"+str(int(DelayInDays)))
                        if not simulation_mode:
                            os.rename(parent_folder, new_parent_folder)
                        print("Rename: ", parent_folder," to ", new_parent_folder)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    remove_empty_folders(folder_path)

# Replace 'your_folder_path' with the path to the folder containing DICOM files
if __name__ == "__main__":

    # Configure the argument parser to pass parameters to the script
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, help="Input folder to scan for DICOM files")  # Required input directory for DICOM files
    parser.add_argument("-sim", action="store_true", default=False, required=False)  # Simulation mode flag

    args = parser.parse_args()
    organize_dicoms_by_patient(args.i,args.sim)
