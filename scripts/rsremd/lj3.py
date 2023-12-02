#!/usr/bin/env python3
""" Modified from python2 20.08.21 """

# from __future__ import division
import sys
import os
from pprint import pprint
from math import sqrt

import subprocess
import argparse
import numpy as np

import parmed as pmd
import parmed.tools as t
from parmed.amber import AmberMask



def mask_from_atoms(atoms):
    # return "@" + ",".join([ str(a.idx + 1) for a in atoms])
    return "@" + ",".join(map(lambda a: str(a.idx + 1), atoms))


def group_by(atoms, keyfunc):
    """
    Return a dictionary with the following format: {keyfunc(atom): [atoms]}, where the
    atoms are grouped by the return value of keyfunc(atom).
    """
    groups = {}
    for atom in atoms:
        key = keyfunc(atom)
        group = groups.setdefault(key, [])
        group.append(atom)
    return groups


def group_by_ljtype(parm, mask):
    """Group atoms in mask by LJ type index."""
    atoms = parm.view[mask]
    groups = group_by(atoms, lambda atom: atom.nb_idx)
    return groups


def add_lj_types(parm, not_ligand_groups, ligand_groups):
    """
    Add new LJ type for every atom type in the ligand, so that the ligand has no LJ type
    in common with the rest.
    """
    assert len(ligand_groups) > 0
    
    for nb_idx, atoms in ligand_groups.items():
        if not nb_idx in not_ligand_groups:
            # don't create a new type when we don't need to i.e. when this type only 
            # appears in the ligand
            continue
        t.addLJType(parm, mask_from_atoms(atoms)).execute()


def change_lj_pairs(parm, receptor_groups, ligand_groups, interaction_func):
    """
    Change LJ pair interaction parameters between receptor and ligand.
    interaction_func(atom1, atom2):
        a function that returns the new interaction parameters (rmin, epsilon)
    """
    assert len(ligand_groups) > 0 and len(receptor_groups) > 0

    for group_r in receptor_groups.values():
        for group_l in ligand_groups.values():
            # enough to look at first atom (only nb_idx is relevant)
            rmin, epsilon = interaction_func(group_r[0], group_l[0])
            mask_r = "@" + str(group_r[0].idx + 1)
            mask_l = "@" + str(group_l[0].idx + 1)
            t.changeLJPair(parm, mask_r, mask_l, rmin, epsilon).execute()


class InterpolateBase(object):
    def __init__(self, strength, **kwargs):
        self.strength = strength

    method = "no interpolation"
    def __call__(self, atom1, atom2):
        rmin = atom1.rmin + atom2.rmin
        epsilon = sqrt(atom1.epsilon * atom2.epsilon)
        return rmin, epsilon

class InterpolateMultiplicative(InterpolateBase):
    method = "multiplicative linear"
    def __call__(self, atom1, atom2):
        rmin = (atom1.rmin + atom2.rmin) * interpolate_lin(1, 4, self.strength)
        epsilon = sqrt(atom1.epsilon * atom2.epsilon) * interpolate_lin(1, 0.1, self.strength)
        return rmin, epsilon

class InterpolateAdditive(InterpolateBase):
    method = "additive"
    def __init__(self, strength, d_max, e_min, d_fixed, e_fixed, **kwargs):
        if d_fixed:
            self.d = d_max
        else:
            self.d = strength * d_max

        if e_fixed:
            self.e = e_min
        else:
            self.e = interpolate_lin(1, e_min, strength)

        # print "d_max", d_max, "e_min", e_min
        # print "d", self.d, "e", self.e


    def __call__(self, atom1, atom2):
        rmin = (atom1.rmin + atom2.rmin) + self.d
        epsilon = sqrt(atom1.epsilon * atom2.epsilon) * self.e
        return rmin, epsilon

class InterpolateSurfaceScaling(InterpolateBase):
    method = "surface scaling of e"
    def __init__(self, strength, interpolator_prev, d_max, e_min, d_fixed, e_fixed, **kwargs):
        if d_fixed:
            self.d = d_max
        else:
            self.d = strength * d_max
        if e_fixed:
            self.e = e_min
        else:
            self.e = interpolate_lin(1, e_min, strength)

    def __call__(self, atom1, atom2):
        # sometimes happens between two H atoms for example
        if atom1.rmin + atom2.rmin == 0.0:
            return 0.0, 0.0

        new_rmin = (atom1.rmin + atom2.rmin) + self.d

        e_scaling = (atom1.rmin + atom2.rmin)**2 / new_rmin**2
        epsilon = sqrt(atom1.epsilon * atom2.epsilon) * e_scaling * self.e

        return new_rmin, epsilon


class InterpolateVolumeScaling(InterpolateBase):
    method = "volume scaling of e"
    def __init__(self, strength, interpolator_prev, d_max, e_min, d_fixed, e_fixed, **kwargs):
        if d_fixed:
            self.d = d_max
        else:
            self.d = strength * d_max
        if e_fixed:
            self.e = e_min
        else:
            self.e = interpolate_lin(1, e_min, strength)

    def __call__(self, atom1, atom2):
        # sometimes happens between two H atoms for example
        if atom1.rmin + atom2.rmin == 0.0:
            return 0.0, 0.0

        new_rmin = (atom1.rmin + atom2.rmin) + self.d
        
        e_scaling = (atom1.rmin + atom2.rmin)**3 / new_rmin**3
        epsilon = sqrt(atom1.epsilon * atom2.epsilon) * e_scaling * self.e

        return new_rmin, epsilon



def interpolate_lin(a, b, fraction):
    return a + (b-a) * fraction


def translate_ligand(parm, receptor_mask, ligand_mask, d):
    """
    Translate the ligand d angstroms away (d>0) or towards (d<0) the receptor.
    """
    atoms_r = parm.view[receptor_mask]
    atoms_l = parm.view[ligand_mask]
    centroid_r = atoms_r.coordinates.mean(axis=0)
    centroid_l = atoms_l.coordinates.mean(axis=0)
    delta = centroid_l - centroid_r
    # print "centroid distance:", np.linalg.norm(delta)
    delta = delta / np.linalg.norm(delta) * d
    for atom in atoms_l:
        atom.xx += delta[0]
        atom.xy += delta[1]
        atom.xz += delta[2]

def translate(parm, args, d):
    if not args.coordinate_file:
        raise ValueError("translating or solvating needs coordinates (the -c option)")

    translate_ligand(parm, args.receptor_mask, args.ligand_mask, d)
    print("translating by {}".format(d))

def solvate(parm, args):
    """
    Return the new parm file after running leap.
    """
    if not args.coordinate_file:
        raise ValueError("solvating / running leep needs coordinates (the -c option)")

    parm.write_pdb("temp.pdb")
    print("running tleap with {}, check leap.log for any errors".format(args.leap))
    stdout = subprocess.check_output(["tleap", "-f", args.leap])
    with open("leap.log", "w") as f:
        f.write(stdout)
    parm = pmd.amber.AmberParm("temp.top", xyz="temp.crd")

    return parm

def write_topology(parm, args, n=None):
    filename = args.output_file
    if n != None:
        filename = filename.replace(".top", "_{}.top".format(n+1))
    print(filename)
    parm.write_parm(filename)
    with open(filename + ".txt", "w") as f:
        f.write(str(t.printLJMatrix(parm, "*")))

def write_coordinates(parm, args):
    if args.translate or args.leap:
        filename = args.coordinate_output_file
        print(filename)
        parm.write_rst7(filename)


def tests(parm, receptor_mask, ligand_mask, not_ligand_mask):
    receptor_groups = group_by_ljtype(parm, receptor_mask)
    ligand_groups = group_by_ljtype(parm, ligand_mask)
    not_ligand_groups = group_by_ljtype(parm, not_ligand_mask)
    water_groups = group_by_ljtype(parm, ":WAT")
    add_lj_types(parm, not_ligand_groups, ligand_groups)

    # check if we didn't accidentally change the lj type of an atom not in the ligand
    for nb_idx, group in not_ligand_groups.items():
        for atom in group:
            assert(atom.nb_idx == nb_idx)
            assert(parm.LJ_radius[atom.nb_idx-1] == atom.rmin)
            assert(parm.LJ_depth[atom.nb_idx-1] == atom.epsilon)
    # groups are still correct
    for nb_idx, group in ligand_groups.items():
        for atom in group:
            assert(atom.nb_idx == group[0].nb_idx)
            assert(parm.LJ_radius[atom.nb_idx-1] == atom.rmin)
            assert(parm.LJ_depth[atom.nb_idx-1] == atom.epsilon)

    # recalculate the interation paramters in the the orignial way
    # and check that nothing changed
    parm_data_old = [
        parm.parm_data["LENNARD_JONES_ACOEF"][:],
        parm.parm_data["LENNARD_JONES_BCOEF"][:]
    ]

    # interpolator = InterpolateBase(0)
    def fn(atom1, atom2):
        # don't change any interactions with water
        assert(atom1.residue.name != "WAT")
        assert(atom2.residue.name != "WAT")
        rmin = atom1.rmin + atom2.rmin
        epsilon = sqrt(atom1.epsilon * atom2.epsilon)
        return rmin, epsilon
    change_lj_pairs(parm, receptor_groups, ligand_groups, fn)
    parm_data_new = [
        parm.parm_data["LENNARD_JONES_ACOEF"][:],
        parm.parm_data["LENNARD_JONES_BCOEF"][:]
    ]

    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    for old, new in zip(parm_data_old, parm_data_new):
        assert(len(old) == len(new))
        assert(all(isclose(a, b, 1e-7, 1e-7) for a, b in zip(old, new)))


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="amber topology file")
    parser.add_argument("num_replicas", type=int)
    
    parser.add_argument("method", type=int, help="lennard-jones interpolation method (see source code), '4' for volume scaling")
    parser.add_argument("-d", "--distances", nargs="*", type=float, help="max distance that gets added to rmin or list of floats", default=[0])
    parser.add_argument("-e", "--epsilons", nargs="*", type=float, help="min fraction of epsilon or list of floats", default=[1])
    parser.add_argument("--d_fixed", action="store_true")
    parser.add_argument("--e_fixed", action="store_true")

    parser.add_argument("-o", "--output_file", required=False, help="amber topology file", default="fk_replica.top")
    parser.add_argument("-r", "--receptor_mask", required=False, help="receptor mask", default="@1-1984")
    parser.add_argument("-l", "--ligand_mask", required=False, help="ligand mask", default=":LIG")

    parser.add_argument("-c", "--coordinate_file", required=False, help="input .inpcrd or .rst file for translating or solvating", default=None)
    parser.add_argument("-co", "--coordinate_output_file", required=False, help="output .inpcrd file after translating or solvating", default="fk.crd")
    parser.add_argument("-t", "--translate", help="translate ligand distance_max away from receptor", action="store_true")
    # to not create collisions with water, we can only solvate after translation, not before
    parser.add_argument("--leap", required=False, help="leap input file that will be run after translating (input will be called temp.pdb and outputs should be called temp.top and temp.crd)", default=None)
    parser.add_argument("--elstat", action="store_true", help="linearely scale charges to 0 across replicas")
    args = parser.parse_args()


    args.not_ligand_mask = "!" + args.ligand_mask
    print("receptor mask", args.receptor_mask)
    print("ligand mask", args.ligand_mask)
    print("not-ligand mask", args.not_ligand_mask)


 
    # with open(args.input_file + ".txt", "w") as f:
    #     f.write(str(t.printLJMatrix(parm, "*")))
    # tests(parm, args.receptor_mask, args.ligand_mask, args.not_ligand_mask); sys.exit(0)


    interpolation_methods = [
        InterpolateBase,
        InterpolateMultiplicative,
        InterpolateAdditive,
        InterpolateSurfaceScaling,
        InterpolateVolumeScaling
    ]
    Method = interpolation_methods[args.method]

    # don't interpolate (d_fixed) when we got multiple ds
    # when only one, both d_fixed == True and d_fixed == False is possible
    # same for epsilon
    ds = args.distances
    es = args.epsilons
    assert(len(ds) == 1 or len(ds) == args.num_replicas)
    assert(len(es) == 1 or len(es) == args.num_replicas)
    if len(ds) > 1:
        args.d_fixed = True
    if len(es) > 1:
        args.e_fixed = True

    print("interpolation method:", Method.method)
    print("max distance that gets added:", args.distances)
    print("min fraction of epsilon:", args.epsilons)
    print("d fixed / not interpolated:", args.d_fixed)
    print("e fixed / not interpolated:", args.e_fixed)

    # load parameter and possibly coordinate file
    parm = pmd.amber.AmberParm(args.input_file, xyz=args.coordinate_file)
    if args.translate:
        translate(parm, args, max(ds))
    if args.leap:
        parm = solvate(parm, args)
    write_coordinates(parm, args)

    # change the lj types
    receptor_groups = group_by_ljtype(parm, args.receptor_mask)
    ligand_groups = group_by_ljtype(parm, args.ligand_mask)
    not_ligand_groups = group_by_ljtype(parm, args.not_ligand_mask)
    add_lj_types(parm, not_ligand_groups, ligand_groups)

    # go through each replica and change lj parameters
    interpolator_prev = None
    parms = []
    orig_charge = parm.parm_data['CHARGE']
    for n, fraction in enumerate(np.linspace(0, 1, args.num_replicas)):
        d = ds[n] if len(ds) > 1 else ds[0]
        e = es[n] if len(es) > 1 else es[0]

        interpolator = Method(fraction, interpolator_prev=interpolator_prev, 
                              d_max=d, e_min=e,
                              d_fixed=args.d_fixed, e_fixed=args.e_fixed)
        interpolator_prev = interpolator
        print("{}: d={}, e={}".format(n+1, interpolator.d, interpolator.e))

        if args.elstat:
            # todo: improve
            for i in range(len(orig_charge)):
                parm.parm_data['CHARGE'][i] = orig_charge[i] * (1 - fraction)
            # needed? dunno
            parm.load_atom_info()
        
        
        # change lj parameters
        change_lj_pairs(parm, receptor_groups, ligand_groups, interpolator)
        write_topology(parm, args, n)

    
    
    # openmm Modeller.addSolvent() http://docs.openmm.org/7.1.0/api-python/generated/simtk.openmm.app.modeller.Modeller.html
    # parmed.openmm.load_topology
    # https://github.com/ParmEd/ParmEd/pull/170
    # https://github.com/ParmEd/ParmEd/pull/170/commits/557311f04815082d4049c6159a1471684f02db45#diff-45490d4d659603f6d2782fed99b9e183R119
