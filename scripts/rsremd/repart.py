import sys
import os
import argparse

try:
    from parmed import tools
    from parmed.amber import AmberParm
except ImportError:
    print("Unable to import parmed module. Exiting...")
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description="Apply hydrogen mass repartitioning to an Amber topology")
    parser.add_argument("parm_in", help="Path to an Amber topology")
    parser.add_argument("parm_out", nargs="?", help="Output path. If not given, use [parm_in]_reparted.[ext] instead")

    args = parser.parse_args()

    parmout = args.parm_out
    if parmout is None:
        base, ext = os.path.splitext(args.parm_in)
        parmout = "".join([base, "_reparted", ext])

    if os.path.exists(parmout):
        print("Output %s already exists.\nPlease enter another path." % parmout)
        sys.exit(1)

    # print(parmout)
    repart(args.parm_in, parmout)


def repart(parmin, parmout):
    top = AmberParm(parmin)

    action_repartition = tools.HMassRepartition(top)
    action_repartition.execute()
    print(str(action_repartition))

    action_output = tools.outparm(top, parmout)
    action_output.execute()
    print(str(action_output))


if __name__ == "__main__":
    main()

