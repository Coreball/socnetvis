#!/usr/bin/env python3

import glob
import json
import sys
import os
from pyvis.network import Network

nodes = {}
anonymize_mapping = {}
help_text = """usage: socnetvis <command>
    verify                  Show linkage errors for nodes in current directory
    fix                     Attempt to fix improperly linked nodes or add nonexistent referenced nodes
    add <name>              Add new node file(s) with no connections and specified name(s)
    remove <name>           Remove all occurrences of name(s) and delete corresponding file(s)
    rename <old> <new>      Rename all occurrences of name to a new name and rename file accordingly
    anonymize [seed]        Anonymize names, offset by [seed] if present else fully random; save to a directory
    show [--alphabetize]    Create network visualization as HTML file [and alphabetize connection lists]
    help                    Show help"""


def load():
    json_errors = []
    for filename in glob.glob('*.json'):
        try:
            with open(filename, 'r') as file:
                node = json.load(file)
                nodes[node['name']] = node
        except json.decoder.JSONDecodeError as err:
            json_errors.append(f"Decode error encountered when loading {filename}\n"
                               f"\t{err.msg} line {err.lineno} column {err.colno}")
    if json_errors:
        sys.exit('\n'.join(json_errors))


def save(path='.'):
    if not os.path.isdir(path):
        os.makedirs(path)
    for node in nodes.values():
        filename = f"{node['name'].replace(' ', '_')}.json"
        filepath = os.path.join(path, filename)
        with open(filepath, 'w') as file:
            json.dump(node, file, indent=4)


def save_anonymize_mapping(path='./anonymize.txt'):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as file:
        json.dump(anonymize_mapping, file, indent=4)


def verify_connections(fix=False):
    new_nodes = {}
    first_run = True  # Am I a do-while loop
    no_problems = True
    while first_run or new_nodes:
        new_nodes.clear()  # Loop again if last run had new nodes
        for name, node in nodes.items():
            all_partners = set()
            for connection_type in node['connections']:
                connection_type_partners = set()
                duplicates = []
                for partner in node['connections'][connection_type]:
                    if partner in connection_type_partners:
                        print(f"{name}: {connection_type} {partner} "
                              f"appears more than once in {connection_type}")
                        if fix:
                            print(f"\tRemoving duplicate {partner} from list of {connection_type}")
                            duplicates.append(partner)
                        continue
                    connection_type_partners.add(partner)
                    if partner in all_partners:
                        print(f"{name}: {connection_type} {partner} "
                              f"appears in more than one connection type")
                        if fix:
                            print(f"\tCONFLICT: {partner} exists in multiple connection types!")
                        continue
                    all_partners.add(partner)
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
                if fix and duplicates:
                    for partner in duplicates:
                        node['connections'][connection_type].remove(partner)  # Should deal with > 1 duplicate
        if fix:
            nodes.update(new_nodes)
        first_run = False
        return no_problems


def add_empty_node(new_nodes, name):
    new_nodes[name] = {"name": name, "notes": "",
                       "connections": {"best": [], "good": [],
                                       "friend": [], "acquaintance": []}}
    return new_nodes[name]


def remove_node(remove_name):
    for name, node in nodes.items():
        for connection_type in node['connections']:
            if remove_name in node['connections'][connection_type]:
                print(f"{name}: removing {remove_name} from list of {connection_type}")
                node['connections'][connection_type].remove(remove_name)
    if remove_name in nodes:
        print(f"Removing {remove_name} from list of all nodes")
        del nodes[remove_name]
    else:
        print(f"{remove_name}: was not found in the list of nodes, could not remove")


def rename_node(original_name, rename_name):
    for name, node in nodes.items():
        for connection_type in node['connections']:
            if original_name in node['connections'][connection_type]:
                if rename_name in node['connections'][connection_type]:
                    print(f"{name}: {connection_type} {original_name} "
                          f"replacement {rename_name} already exists, removing {original_name}")
                    node['connections'][connection_type].remove(original_name)
                else:
                    print(f"{name}: renaming {connection_type} {original_name} to {rename_name}")
                    node['connections'][connection_type].remove(original_name)
                    node['connections'][connection_type].append(rename_name)
    if original_name in nodes:
        print(f"Renaming {original_name} in list of all nodes to {rename_name}")
        if rename_name in nodes:
            print(f"\tWARNING: {rename_name} already exists, merging...")
            merge_connections(rename_name, original_name)
        else:
            nodes[original_name]['name'] = rename_name
            nodes[rename_name] = nodes[original_name]
        del nodes[original_name]
    else:
        print(f"{original_name}: was not found in the list of nodes, could not rename")


def merge_connections(destination, merge):
    for connection_type in nodes[merge]['connections']:
        for partner in nodes[merge]['connections'][connection_type]:
            if partner not in nodes[destination]['connections'][connection_type]:
                # This should deal with duplicates
                nodes[destination]['connections'][connection_type].append(partner)


def add_node_json(name):
    filename = f"{name.replace(' ', '_')}.json"
    with open(filename, 'w') as file:
        print(f"Creating {filename}")
        node = {"name": name, "notes": "",
                "connections": {"best": [], "good": [],
                                "friend": [], "acquaintance": []}}
        json.dump(node, file, indent=4)


def remove_node_json(remove_name):
    filename = f"{remove_name.replace(' ', '_')}.json"
    if os.path.exists(filename):
        print(f"Removing {filename}")
        os.remove(filename)
    else:
        print(f"{filename} was not found and could not be removed")


def anonymize(use_offset=False, name_offset=""):
    try:
        from faker import Faker
        fake = Faker()
        anonymize_mapping.clear()
        original_names = list(nodes.keys())
        for original_name in original_names:
            if use_offset:                                  # Basing seed on name stops list order interference
                fake.seed(f"{name_offset}{original_name}")  # Otherwise just uses a random seed and does not change it
            anonymous = fake.name()
            anonymize_mapping[original_name] = anonymous
            rename_node(original_name, anonymous)
            # Warning: does not remove notes from nodes
        print(f"Name Mapping: {anonymize_mapping}")
    except ImportError:
        sys.exit("The Faker package is not installed and is required for anonymize")


def network_visualization(path='./socnetvis.html', alphabet=False):
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
        net_node['title'] += f"<br>{net_node['value']} Connections<br>"
        if node['notes']:
            net_node['title'] += f"<i>{node['notes']}</i><br>"
        for connection_type in node['connections']:
            if node['connections'][connection_type]:
                connections = node['connections'][connection_type]
                net_node['title'] += f"<br>{connection_type.capitalize()} " \
                                     f"({len(connections)})<br>&nbsp&nbsp"
                net_node['title'] += "<br>&nbsp&nbsp".join(sorted(connections) if alphabet else connections) + "<br>"
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    net.show(path)


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
    elif sys.argv[1] == 'remove':
        if len(sys.argv) > 2:
            load()
            verify_connections(fix=True)
            for remove_name in sys.argv[2:]:
                remove_node(remove_name)
                remove_node_json(remove_name)
            save()
        else:
            print("Please specify a name or names to be removed")
    elif sys.argv[1] == 'rename':
        if len(sys.argv) == 4:
            load()
            rename_node(sys.argv[2], sys.argv[3])
            remove_node_json(sys.argv[2])
            save()
        else:
            print("Please specify a name and its replacement only")
    elif sys.argv[1] == 'anonymize':
        if len(sys.argv) == 2:
            load()
            anonymize()
            save(path='./anonymize/')
            save_anonymize_mapping(path='./anonymize/anonymize_mapping.txt')
            network_visualization(path='./anonymize/socnetvis.html')
        elif len(sys.argv) == 3:
            load()
            anonymize(use_offset=True, name_offset=sys.argv[2])
            save(path='./anonymize/')
            save_anonymize_mapping(path='./anonymize/anonymize_mapping.txt')
            network_visualization(path='./anonymize/socnetvis.html')
        else:
            print("Please give one argument for the seed offset")
    elif sys.argv[1] == 'show':
        load()
        if verify_connections(fix=False):
            if len(sys.argv) > 2 and sys.argv[2] == '--alphabetize':
                network_visualization(alphabet=True)
            else:
                network_visualization(alphabet=False)
        else:
            print("Nodes failed to verify, not generating visualization!")
    else:
        print(f"socnetvis: {sys.argv[1]} is not an a socnetvis command. Use 'help'")


if __name__ == '__main__':
    main()
