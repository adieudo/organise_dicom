"""
Script : organize_dicom.py
Description : Organize DICOM files into folders based on patient name, study date, and modality.
Author : Arnaud Dieudonné
Date : 02/05/2025
Version : 1.0

Usage :
    python organise_dicom.py -i <input_folder> -s <sensitivity> -n <number_of_detectors> -a <activity> -d <injection_date> [-sim]

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

def organize_dicoms_by_patient(folder_path):
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
            if file.endswith(".DCM") or file.endswith(".dcm"):
                file_path = os.path.join(root, file)
                try:
                    dicom_data = pydicom.dcmread(file_path)
                    PatientName = str(dicom_data.PatientName).replace("^", "_")
                    StudyDate= str(dicom_data.get("StudyDate"))
                    modality = str(dicom_data.Modality)
                    study_folder = os.path.join(folder_path, PatientName,StudyDate,modality)
                    os.makedirs(study_folder, exist_ok=True)
                    move(file_path, os.path.join(study_folder, file))
                    print("Move: ", file_path," to ", os.path.join(study_folder, file))
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".DCM") or file.endswith(".dcm"):
                file_path = os.path.join(root, file)
                try:
                    dicom_data = pydicom.dcmread(file_path)
                    PatientName = str(dicom_data.PatientName).replace("^", "_")
                    StudyDate= str(dicom_data.get("StudyDate"))
                    modality = str(dicom_data.Modality)
                    if modality=="NM":
                        injection_date_time = datetime.datetime.strptime(dicom_data.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime.split('.')[0],'%Y%m%d%H%M%S')
                        scan_date_time = datetime.datetime.strptime(dicom_data.AcquisitionDate + dicom_data.AcquisitionTime.split('.')[0],'%Y%m%d%H%M%S')
                        DelayInDays = round((scan_date_time - injection_date_time).total_seconds() / 3600 / 24,0)
                        parent_folder = os.path.dirname(os.path.dirname(file_path))
                        patient_folder = os.path.dirname(parent_folder)
                        new_parent_folder = os.path.join(patient_folder,"J"+str(int(DelayInDays)))
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
     
    args = parser.parse_args()
    organize_dicoms_by_patient(args.i)
