from django.db import models
from .validators import validate_file
from django.core.validators import MaxValueValidator, MinValueValidator

import uuid

def user_directory_path(instance, filename):
    '''
    File will be uploaded to MEDIA_ROOT/<filename>/<filename>_<uuid>.pdb
    The unique ID is necessary to assign each job submission to the correct user (reference code)
    '''
    file_uuid = uuid.uuid4()
    ext = filename.split('.')[-1]
    name = filename.split('.')[0]
    new_name = str(name)+"_"+str(file_uuid)+"."+str(ext)
    return '{0}/{1}'.format(name,new_name)

class rsremd(models.Model):
    email = models.EmailField(max_length = 254, blank=False)
    protein_complex_name = models.CharField(max_length=100, blank=False)
    receptor_chain_end = models.IntegerField(blank=False, default=89)
    ligand_chain_end = models.IntegerField(blank=False, default=185)
    pdb = models.FileField(null=True, blank=False, validators=[validate_file], upload_to=user_directory_path)


class cpep(models.Model):
    email = models.EmailField(max_length = 254, blank=False)
    peptide_name = models.CharField(max_length=100, blank=False)
    protein_chain_name = models.CharField(max_length=100, blank=False)
    receptor_chain_name = models.CharField(max_length=100, blank=False)
    pdb = models.FileField(null=True, blank=False, validators=[validate_file], upload_to=user_directory_path)
    cutoff = models.FloatField(blank=True, default=6.0)
    treshold = models.FloatField(blank=True, default=0.7, validators=[MaxValueValidator(2.5), MinValueValidator(0.3)])
    motif = models.IntegerField(blank=True, default=5, validators=[MaxValueValidator(7), MinValueValidator(4)])
    target_hotspots = models.BooleanField(default=False, blank=True)
    residue_numbers = models.CharField(max_length=255, blank=True, null=True)

    
    def __str__(self):
        return self.peptide_name
        return self.protein_chain_name
        return self.receptor_chain_name
        return self.pdb
        return self.residue_numbers