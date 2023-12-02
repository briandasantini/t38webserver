import sys

receptor_chain = sys.argv[1]
ligand_chain = sys.argv[2]

def write_maskinfo(receptor_chain, ligand_chain):
    rec = int(receptor_chain)
    lig = int(ligand_chain)
    if (rec > lig)==True:
        ligand = ":1-"+str(lig)
        receptor = ":"+str(lig+1)+"-"+str(rec)
    if (lig > rec)==True:
        ligand = ":"+str(rec+1)+"-"+str(lig)
        receptor = ":1-"+str(rec)

    with open('mask.info', 'w') as f:
        f.write(str(ligand)+'\n'+str(receptor))

if __name__ == "__main__":
    write_maskinfo(receptor_chain, ligand_chain)