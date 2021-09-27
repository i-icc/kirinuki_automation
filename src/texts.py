def read_timestamp():
    path = './timestamp.txt'
    timestamp = []
    with open(path) as f:
        r = f.readlines()
    for line in r:
        timestamp.append(line.split())
    return timestamp

if __name__ == '__main__':
    print(read_timestamp())