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