#utils.py
import bleach
import os
import shutil
import time
import glob
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms.widgets import Widget
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from .models import *


############################################################## FUNCTIONS FOR ALL SCRIPTS #####################################################

class cd:
    """
    Context manager for changing the current working directory
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def delete():
    import time
    '''
    Deletes any old results folders that have been kept for more than 30 days.
    '''
    # initializing the count
    deleted_folders_count = 0
    deleted_files_count = 0
    
    path = "./media/"
    days = 30
    # converting days to seconds
    # time.time() returns current time in seconds
    seconds = time.time() - (days * 24 * 60 * 60)

    # checking whether the file is present in path or not
    if os.path.exists(path):
        # iterating over each and every folder and file in the path
        for root_folder, folders, files in os.walk(path):
            # comparing the days
            if seconds >= os.stat(root_folder).st_ctime:
                # removing the folder
                shutil.rmtree(root_folder)
                deleted_folders_count += 1 # incrementing count

                # breaking after removing the root_folder
                break
            else:
                # checking folder from the root_folder
                for folder in folders:
                    # folder path
                    folder_path = os.path.join(root_folder, folder)
                    # comparing with the days
                    if seconds >= os.stat(folder_path).st_ctime:
                        # invoking the remove_folder function
                        shutil.rmtree(folder_path)
                        deleted_folders_count += 1 # incrementing count
                # checking the current directory files
                for file in files:
                    # file path
                    file_path = os.path.join(root_folder, file)
                    # comparing the days
                    if seconds >= os.stat(file_path).st_ctime:
                        # invoking the remove_file function
                        os.remove(file_path)
        else:
            # if the path is not a directory
            # comparing with the days
            if seconds >= os.stat(path).st_ctime:
                # invoking the file
                os.remove(path)
                deleted_files_count += 1 # incrementing count
    else:
        # file/folder is not found
        print(f'"{path}" is not found')
        deleted_files_count += 1 # incrementing count

    print(f"Total folders deleted: {deleted_folders_count}")
    print(f"Total files deleted: {deleted_files_count}")

# def find(path):
#     # find the name of the uploaded file which was renamed - django automatically adds a unique id if there are duplicates
#     with cd(path):
#         pdb_filenames_list = glob.glob('*.pdb')
#     # [0] chooses the most recent upload
#     pdb_name = pdb_filenames_list[0].replace('.pdb', '')
#     return pdb_name

def find(path):
    # find the name of the uploaded file which was renamed - django automatically adds a unique id if there are duplicates
    print(f"Searching for .pdb files in directory: {path}")
    
    with cd(path):
        pdb_filenames_list = glob.glob('*.pdb')
    
    print(f"Found .pdb files: {pdb_filenames_list}")
    
    if pdb_filenames_list:
        # [0] chooses the most recent upload
        pdb_name = pdb_filenames_list[0].replace('.pdb', '')
        print(f"Selected PDB file name: {pdb_name}")
        return pdb_name
    else:
        print("No .pdb files found in the directory.")
        return None

def send_mail(reference_name, pdb_name, email, file_path):
    '''
    Sends an email to the user
    if successful, it sends a reference code for downloading the results
    if unsuccessful, it sends an apologetic email with the errors.txt
    '''
    # expected_working_directory = '/home/web_service/b-zacharias-website'

    # # Check if the current working directory matches the expected directory
    # if os.getcwd() != expected_working_directory:
    #     # Change the current working directory to the expected directory
    #     os.chdir(expected_working_directory) 
        
    # Error Text File Made During Simulation
    error = pdb_name+'/'+pdb_name+'_errors.txt'
    # Email Subject
    subject="Zacharias Web Services - Submission Results of "+str(reference_name)
    result_folder_path = '/home/web_service/b-zacharias-website/media/'

    # If a folder containing the results is located in the media directory, the simulation was successful, and the reference code (pdb name variable) will be written in the mail.
    if os.path.exists(result_folder_path+pdb_name)==True:
        with open('./templates/results_email.html', 'r') as file:  # r to open file in READ mode
            message = file.read().format(protein_name=pdb_name)
        mail = EmailMessage(subject, message, 'Zacharias Web Services <'+settings.EMAIL_HOST_USER+'>', [email])
    
    # If the result folder cannot be located, something went wrong and no results are available. So it attaches the error.text file to the mail to send to the user.
    else:
        with open('./templates/error_email.html', 'r') as file:  # r to open file in READ mode
            message = file.read()
            zipfile = os.path.abspath(error)
        mail = EmailMessage(subject, message, 'Zacharias Web Services <'+settings.EMAIL_HOST_USER+'>', [email])
        mail.attach_file(zipfile)

    # Sends mail to user
    mail.content_subtype = "html"
    mail.send()

    # Delete Leftover Files and Delete Old Result Files
    # if os.path.exists(file_path+pdb_name+'/')==True:
    #     shutil.rmtree(file_path+pdb_name+"/")
    # delete()
    


def exec_script(simtype, pdb_name, protein_file_name, cmd, reference_name, email):
    '''
        The job is submitted and the simulation is performed. 
        First, it creates a folder in which all simulation results will be kept. 
        When the simulation is finished, it checks to see if the simulation was successful and if the results are accessible. 
        If they are, the result folder is moved to the media folder.
    '''
    # Script Specific Names
    file_path = '/home/web_service/b-zacharias-website/scripts/'+str(simtype)+'/'
    result_folder_path = '/home/web_service/b-zacharias-website/media/'
    error = pdb_name+'_errors.txt'
    
    
    with cd(file_path):
        
        # Create A Specific Folder for this Job
        directory = os.path.dirname(os.path.abspath(__file__))
        os.mkdir(file_path+pdb_name)
        shutil.move("/home/web_service/b-zacharias-website/media/"+protein_file_name+"/"+pdb_name+".pdb", file_path+pdb_name+"/"+pdb_name+".pdb")
        shutil.rmtree("/home/web_service/b-zacharias-website/media/"+protein_file_name+"/")
        
        
        # Execute the Script
        os.system(cmd)
        
        # Move the Error Text File into the Result Folder
        shutil.move(error, pdb_name+"/"+error)
    
        # See if the Simulation was Successfull
        if simtype=='rsremd':
            # Is the final replica exchange file remd_8.pdb present?
            result_condition=(os.path.exists(file_path+pdb_name+"/remd_8.pdb"))
        elif simtype=='cpep':
            # Is the simulation error-free, and hence the error text file is empty?
            result_condition=(os.stat(pdb_name+'/'+error).st_size == 0)
        else:
            result_condition=False
            
        # If the simulation was successful, transfer it to the Media Directory.
        if result_condition==True:
            shutil.move(file_path+pdb_name, result_folder_path+pdb_name)
            

    # Send Mail to User
    send_mail(reference_name, pdb_name, email, file_path) 