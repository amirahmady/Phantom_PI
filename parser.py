import argparse

parser = argparse.ArgumentParser(description='Respiration code')

parser.add_argument('-c', '--connection', dest='connection', choices=['socketcan', 's', 'pcan', 'p'],
                    help="use socketcan or pcan as connection", required=True)
# parser.add_argument('-s', '--socketcan', action="store_true", default=False, help="use socketcan on raspberry Pi")
# parser.add_argument('-p', '--pcan', action="store_true", default=False, help="use USB peak can device")
# parser.add_argument('-c', action="store", dest="const", type=int)
# parser.add_argument('args', nargs=argparse.REMAINDER)

args = parser.parse_args(args=argparse.sys.argv.lower())

print(args.connection)