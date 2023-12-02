#!/bin/bash

### Repulsive Scaling Replica Exchange
#
# - This script runs via 'bash rsremd.sh $protein_name'
# - Check that your $AMBERHOME variable points to your amber20 directory.
# - You will have multiple output files needed for the next step
# - Your final output file will be remd_1.pdb - remd_16.pdb wich will have water and ions stripped
#
# Original Code by Till Siebenmorgen
# Contributors: Yasmin Saremi (y.saremi@tum.de) - 
# Physics Department T38, Technical University of Munich, Garching, Germany.

#### Variables ####
protein_name=$1
receptor_end=$2
ligand_end=$3

source /home/richard/anaconda3/amber.sh

#### Go To Output Directory ####
cd ${protein_name}

#### Pdb4Amber ####
#pdb4amber -y -i ${protein_name}.pdb -o myprotein.pdb
cp ${protein_name}.pdb myprotein.pdb
#### Tleap ####
python3 ../leap.py myprotein

#### HMass Repartition ####
python3 ../repart.py myprotein.prmtop myprotein_hrpt.prmtop

#### Writing Mask.Info ####
python3 ../writemask.py $receptor_end $ligand_end
l_mask=$( head -1 mask.info)
r_mask=$( tail -1 mask.info)
centermask=$l_mask

#### Creating Parm for Replica Exchange ####
python3 ../lj3.py myprotein_hrpt.prmtop 8 4 -d 0.00 0.02 0.08 0.16 0.24 0.32 0.44 0.68 -e 1.00 0.98 0.96 0.92 0.88 0.84 0.80 0.74 -r ${r_mask} -l ${l_mask} -o syst.top | tee lj.log

#### Energy Minimisation ####
pmemd.cuda -O -i ../min.in -c myprotein.rst -p myprotein_hrpt.prmtop -r min.rst -o min.out -x min.nc 
echo Minimisation Is Done

#### Heating Process #####
pmemd.cuda -O -i ../mdwat2.in -c min.rst -p myprotein_hrpt.prmtop -r mdwat2.rst -o mdwat2.out -ref myprotein.rst -x mdwat2.nc 
echo MDWat2 Is Done
pmemd.cuda -O -i ../mdwat3.in -c mdwat2.rst -p myprotein_hrpt.prmtop -r mdwat3.rst -o mdwat3.out -ref myprotein.rst -x mdwat3.nc 
echo MDWat3 Is Done
pmemd.cuda -O -i ../mdwat4.in -c mdwat3.rst -p myprotein_hrpt.prmtop -r mdwat4.rst -o mdwat4.out -ref myprotein.rst -x mdwat4.nc 
echo MDWat4 Is Done
pmemd.cuda -O -i ../mdwat5.in -c mdwat4.rst -p myprotein_hrpt.prmtop -r mdwat5.rst -o mdwat5.out -ref myprotein.rst -x mdwat5.nc 
echo MDWat5 Is Done
pmemd.cuda -O -i ../mdwat6.in -c mdwat5.rst -p myprotein_hrpt.prmtop -r mdwat6.rst -o mdwat6.out  -ref myprotein.rst -x mdwat6.nc 
echo Heating Is Done

#### Running Replica Exchange ####
remd()
{
    groupfile=remd.groupfile
    for j in {1..8};
    do
        printf -- "-O -rem 3 -i ../remd.in -o remd_${j}.out -c mdwat6.rst -r remd_${j}.rst -x remd_${j}.nc -p syst_${j}.top -inf mdinfo.00${j} -l logfile.00${j}\n" >> "${groupfile}"
    done
    mpirun -np 8 pmemd.cuda_SPFP.MPI -O -ng 8 -groupfile ${groupfile} 
}
remd 
echo RSREMD is Done

#### Stripping Trajectories ####
for trajnum in {1..8};
    do
        cppin=reimage_center.ptraj
        cppout=striped_${trajnum}.nc

        printf "parm syst_${trajnum}.top\n" > $cppin
        echo "trajin remd_${trajnum}.nc" >> $cppin
            
        printf "strip :Na+\n" >> $cppin
        printf "strip :Cl-\n" >> $cppin
        printf "strip :WAT outprefix striped\n" >> $cppin
        printf "trajout $cppout\n" >> $cppin
        printf "center $centermask\n" >> $cppin
        printf "image center familiar\n" >> $cppin
        printf "go" >> $cppin

        cpptraj -i $cppin > cpptrajstrip.temp
            rm $cppin
        cpptraj -p striped.syst_${trajnum}.top -y $cppout -x remd_${trajnum}.pdb > cpptrajpdb.temp
    done
cd ../
echo Made it here
