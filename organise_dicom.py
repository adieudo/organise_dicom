"""
Script : organize_dicom.py
Description : Organize DICOM files into folders based on patient name, acquisition date, and modality.
Author : Arnaud Dieudonné
Date : 26/06/2025
Version : 1.12

Usage :
    python organise_dicom.py -i <input_folder>
    python organise_dicom.py -i <input_folder> -sim
    python organise_dicom.py -i <input_folder> -fname date, study or accession

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

def organize_dicoms_by_patient(folder_path,simulation_mode,folder_name):
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
                    PatientName = PatientName.zfill(3)
                    AcquisitionDate= str(dicom_data.get("AcquisitionDate"))
                    print(AcquisitionDate)
                    modality = str(dicom_data.Modality)
                    series_folder = os.path.join(folder_path, PatientName,AcquisitionDate,modality)
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
                    PatientName = PatientName.zfill(3)
                    AcquisitionDate= str(dicom_data.get("AcquisitionDate"))
                    StudyDescription = str(dicom_data.get("StudyDescription", ""))
                    AccessionNumber = str(dicom_data.get("AccessionNumber", ""))
                    CorrectedImage = str(dicom_data.get("CorrectedImage",""))
                    modality = str(dicom_data.Modality)
                    if modality=="NM" or modality=="PT":
                        injection_date_time = datetime.datetime.strptime(dicom_data.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime.split('.')[0],'%Y%m%d%H%M%S')
                        scan_date_time = datetime.datetime.strptime(AcquisitionDate + dicom_data.AcquisitionTime.split('.')[0],'%Y%m%d%H%M%S')
                        DelayInDays = round((scan_date_time - injection_date_time).total_seconds() / 3600 / 24,0)
                        parent_folder = os.path.dirname(os.path.dirname(file_path))
                        patient_folder = os.path.dirname(parent_folder)
                        if folder_name == 'date':
                            new_parent_folder = os.path.join(patient_folder,modality+"_J"+str(int(DelayInDays)))
                        if folder_name == 'study':
                            new_parent_folder = os.path.join(patient_folder,StudyDescription)
                        if folder_name == 'accession':
                            new_parent_folder = os.path.join(patient_folder,AccessionNumber)
                        if modality=="NM":
                            new_parent_folder=new_parent_folder+"_"+CorrectedImage
                        new_parent_folder = ''.join(e for e in new_parent_folder if e.isalnum() or e in ('_', '-', '/'))
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
    parser.add_argument('-fname', type=str, help="Name of the timepoint directory (date, study or accession)",default='date',required=False)
    args = parser.parse_args()
    organize_dicoms_by_patient(args.i,args.sim,args.fname)
