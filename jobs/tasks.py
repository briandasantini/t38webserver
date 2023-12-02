# tasks.py in your Django app

from celery import shared_task
from .utils import exec_script

@shared_task
def run_rsremd_simulation(simtype, pdb_name, protein_file_name, cmd, reference_name, email):
    exec_script(simtype, pdb_name, protein_file_name, cmd, reference_name, email)

@shared_task
def run_cpep_simulation(simtype, pdb_name, protein_file_name, cmd, reference_name, email):
    exec_script(simtype, pdb_name, protein_file_name, cmd, reference_name, email)