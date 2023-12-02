import bleach
import os
import threading
import time

from django.views.generic import FormView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from .forms import * 
from .models import *

from .tasks import run_rsremd_simulation, run_cpep_simulation  # Import the Celery tasks
from .utils import exec_script
from .utils import find



class RSREMDView(SuccessMessageMixin, FormView):
    template_name = 'rsremd.html'
    model = rsremd
    form_class = RSREMDForm
    success_url = reverse_lazy('home')
    success_message = "Your Job has been submitted successfully"
    def form_valid(self, form):
        form.save()
        protein_file_name, receptor_chain, ligand_chain, reference_name, email = form.clean_rsremd_data()
        #file_path = '/home/web_service/b-zacharias-website/scripts/rsremd/' # File Path to the RSREMD Simulation
        
        pdb_name = find('/home/web_service/b-zacharias-website/media/' + protein_file_name + "/")
        cmd = "bash rsremd.sh " + pdb_name + " " + str(receptor_chain) + " " + str(ligand_chain) + " 2> " + pdb_name + "_errors.txt"
        run_rsremd_simulation.delay('rsremd', pdb_name, protein_file_name, cmd, reference_name, email)
        return super().form_valid(form)




class cPEPView(SuccessMessageMixin, FormView):
    template_name = 'cpep.html'
    model = cpep
    form_class = cPEPForm
    success_url = reverse_lazy('home')
    success_message = "Your Job has been submitted successfully"
    def form_valid(self, form):
        form.save()
        protein_file_name, protein_chain_name, receptor_chain_name, cutoff, treshold, motif, reference_name, email, target_hotspots, residue_numbers = form.clean_data()
        file_path = '/home/web_service/b-zacharias-website/scripts/cpep/' # File Path to the cPEP Simulation
        pdb_name = find('/home/web_service/b-zacharias-website/media/' + protein_file_name + "/")
        
        
        # Build the command
        
        cutoff = int(cutoff)
        frmsd_threshold = float(treshold)
        motif = int(motif)
        cmd = f"python cPEPmatch.py -ft {treshold} -wl {file_path+pdb_name}/ -ms {motif} -p {protein_chain_name} -t {receptor_chain_name} -n {pdb_name} -ens true"
        
         # Check if residue_numbers contains anything
        if residue_numbers and target_hotspots:
            cmd += f" -cs false -psr '{residue_numbers}' "
        else:
            cmd += f" -cs true -ic {cutoff}"  
            
        cmd += f" 2> {pdb_name}_errors.txt | tee {file_path+pdb_name}/cpepmatch.log"


        run_cpep_simulation.delay('cpep', pdb_name, protein_file_name, cmd, reference_name, email)
        return super().form_valid(form)
    
