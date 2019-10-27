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
    nodes['Changyuan Lin']['age'] = 5
    nodes['Changyuan Lin']['list'] = [1, 2, 3, 4]
    nodes['Changyuan Lin']['otherlist'] = ['a', 'b', 'c']
    save()
    nodes.clear()
    load()
    print(nodes)


if __name__ == '__main__':
    main()
