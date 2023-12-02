import os
import sys

##### Variables #####
filename = sys.argv[1]
starting_file = str(filename)+".pdb"

##### Functions #####
def get_residue_num(starting_file):

    with open("../leap0.in", "r") as inLeap0, open("leapw0.in", "w") as oLeap0:
        for l in inLeap0:
            if "mol = loadpdb XXXX" in l:
                oLeap0.write("mol = loadpdb "+str(starting_file)+"\n")
            else:
                oLeap0.write(l)
    
    #os.system("rm leapw0.out")
    os.system("tleap -f leapw0.in >> leapw0.out")

    with open("leapw0.out", "r") as F:
        for l in F:
            if "residues." in l:
                # e.g "Added 8418 residues."
                residue = float(l.split()[1])
        resid = round(residue*0.002)

    return int(resid)

def write_leap(starting_file, filename):
    
    with open("../leap.in", "r") as inLeap, open("leapw.in", "w") as oLeap:
        for l in inLeap:
            if "mol = loadpdb XXXX" in l:
                oLeap.write("mol = loadpdb "+str(starting_file)+"\n")

            elif "addions mol Na+ XXXX Cl- XXXX" in l:
                resid = get_residue_num(starting_file)
                oLeap.write("addions mol Na+ "+str(resid)+" Cl- "+str(resid)+"\n")
            
            elif "saveamberparm mol XXXX XXXX" in l:
                oLeap.write("saveamberparm mol "+str(filename)+".prmtop "+str(filename)+".rst \n")

            else:
                oLeap.write(l)
    
    os.system("tleap -f leapw.in > leapw.temp")
    os.system("rm leapw*")


##### MAIN ######
write_leap(starting_file, filename)