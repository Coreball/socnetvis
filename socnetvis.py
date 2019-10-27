import glob
import json

nodes = {}


def load():
    for filename in glob.glob('*.json'):
        with open(filename, 'r') as file:
            node = json.load(file)
            nodes[node['name']] = node


def save():
    for node in nodes.values():
        filename = f"{node['name'].replace(' ', '_').upper()}.json"
        with open(filename, 'w') as file:
            json.dump(node, file, indent=4)


def verify_connections(fix=False):
    new_nodes = {}
    first_run = True  # Am I a do-while loop
    while first_run or new_nodes:
        new_nodes.clear()  # Loop again if last run had new nodes
        for name, node in nodes.items():
            for connection_type in node['connections']:
                for partner in node['connections'][connection_type]:
                    if partner not in nodes:
                        print(f"{name}: {connection_type} {partner} "
                              f"is not in list of all nodes")
                        if fix:
                            if partner not in new_nodes:
                                print(f"\tAdding {partner} to new nodes")
                                add_empty_node(new_nodes, partner)
                            else:
                                print(f"\t{partner} was already added to new nodes")
                            print(f"\tAdding {name} to {partner}'s list of {connection_type}")
                            new_nodes[partner]['connections'][connection_type].append(name)
                    elif name not in nodes[partner]['connections'][connection_type]:
                        print(f"{name}: is not in {partner}'s "
                              f"list of {connection_type}")
                        if fix:
                            conflict = False
                            for other_connections in nodes[partner]['connections']:
                                if name in nodes[partner]['connections'][other_connections]:
                                    print(f"\tCONFLICT: {name} already exists in "
                                          f"{partner}'s list of {other_connections}")
                                    conflict = True
                            if not conflict:
                                print(f"\tAdding {name} to {partner}'s list of {connection_type}")
                                nodes[partner]['connections'][connection_type].append(name)
        if fix:
            nodes.update(new_nodes)
        first_run = False


def add_empty_node(new_nodes, name):
    new_nodes[name] = {"name": name, "notes": "",
                       "connections": {"best": [], "good": [],
                                       "friend": [], "acquaintance": []}}
    return new_nodes[name]


def main():
    nodes['Changyuan Lin'] = {}
    nodes['Changyuan Lin']['name'] = 'Changyuan Lin'
    nodes['Changyuan Lin']['notes'] = ""
    nodes['Changyuan Lin']['connections'] = {}
    nodes['Changyuan Lin']['connections']['best'] = []
    nodes['Changyuan Lin']['connections']['good'] = []
    nodes['Changyuan Lin']['connections']['friend'] = ['A Person', 'B Person']
    nodes['Changyuan Lin']['connections']['acquaintance'] = []
    save()
    nodes.clear()
    load()
    print(nodes)
    verify_connections(fix=True)
    print(nodes)


if __name__ == '__main__':
    main()
