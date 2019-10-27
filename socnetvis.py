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


if __name__ == '__main__':
    main()
