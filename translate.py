import argparse
from socnetvis import *

parser = argparse.ArgumentParser(description="Translate old socnetvis JSON to new format")
parser.add_argument('files', metavar="FILE", nargs='+', help="individual socnetvis JSON to convert")
parser.add_argument('-o', '--output', nargs='?', const='./translate/', default='./translate/', help="output directory")


def load_one(filename):
    try:
        with open(filename, 'r') as file:
            node = json.load(file)
            nodes[node['name']] = node
    except FileNotFoundError as err:
        sys.exit(err)
    except json.decoder.JSONDecodeError as err:
        sys.exit(f"Decode error encountered when loading {filename}\n"
                            f"\t{err.msg} line {err.lineno} column {err.colno}")


def translate():
    for node in nodes.values():
        new_connections = {} # for easy name mapping
        for connection_type in node['connections']:
            for partner in node['connections'][connection_type]:
                new_relation = {'type': connection_type, 'notes': ""}
                if partner not in new_connections:
                    new_connections[partner] = {'name': partner, 'relations': []}
                if new_relation not in new_connections[partner]['relations']:
                    new_connections[partner]['relations'].append(new_relation)
        node['connections'] = list(new_connections.values())


def main(args):
    for filename in args.files:
        load_one(filename)
    translate()
    save(path=args.output)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
