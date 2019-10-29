#!/usr/bin/env python3

import glob
import json
import sys
from pyvis.network import Network

nodes = {}
help_text = """usage: socnetvis <command>
    verify    Show linkage errors for nodes in current directory
    fix       Attempt to fix improperly linked nodes or add referenced nodes that don't exist
    add       Add new node file with no connections and specified name
    show      Create network visualization as HTML file
    help      Show help"""


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
    no_problems = True
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
                        else:
                            no_problems = False
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
                        else:
                            no_problems = False
        if fix:
            nodes.update(new_nodes)
        first_run = False
        return no_problems


def add_empty_node(new_nodes, name):
    new_nodes[name] = {"name": name, "notes": "",
                       "connections": {"best": [], "good": [],
                                       "friend": [], "acquaintance": []}}
    return new_nodes[name]


def add_node_json(name):
    filename = f"{name.replace(' ', '_').upper()}.json"
    with open(filename, 'w') as file:
        print(f"creating {filename}")
        node = {"name": name, "notes": "",
                "connections": {"best": [], "good": [],
                                "friend": [], "acquaintance": []}}
        json.dump(node, file, indent=4)


def network_visualization():
    weights = {'best': 4, 'good': 2, 'friend': 1, 'acquaintance': 0.5}
    net = Network('100%', '100%', bgcolor='#222', font_color='white')
    net.barnes_hut()
    for name, node in nodes.items():
        for connection_type in node['connections']:
            for partner in node['connections'][connection_type]:
                net.add_node(name, name, title=name)
                net.add_node(partner, partner, title=partner)
                net.add_edge(name, partner, value=weights[connection_type])
    for net_node in net.nodes:
        node = nodes[net_node['id']]
        net_node['value'] = len(net.get_adj_list()[net_node['id']])
        net_node['title'] += f" <br>{net_node['value']} Connections<br>"
        for connection_type in node['connections']:
            if node['connections'][connection_type]:
                net_node['title'] += f"<br>{connection_type.capitalize()}<br>&nbsp&nbsp"
                net_node['title'] += "<br>&nbsp&nbsp".join(node['connections'][connection_type]) + "<br>"
    net.show('socnetvis.html')


def main():
    if len(sys.argv) == 1 or sys.argv[1] == 'help':
        print(help_text)
    elif sys.argv[1] == 'verify':
        load()
        verify_connections(fix=False)
    elif sys.argv[1] == 'fix':
        load()
        verify_connections(fix=True)
        save()
    elif sys.argv[1] == 'add':
        if len(sys.argv) > 2:
            for name in sys.argv[2:]:
                add_node_json(name)
        else:
            print("Please specify a name or names to be added")
    elif sys.argv[1] == 'show':
        load()
        if verify_connections(fix=False):
            network_visualization()
        else:
            print("Nodes failed to verify, not generating visualization!")
    else:
        print(f"socnetvis: {sys.argv[1]} is not an a socnetvis command. Use 'help'")


if __name__ == '__main__':
    main()
