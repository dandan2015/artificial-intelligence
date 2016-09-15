f = open("input.txt",'r')
line = f.readline()
input = []
out = open('output.txt','w')
while line:
    line = line.strip()
    if line:
        input.append(line)
    line = f.readline()
f.close()


def bfs_dfs_perpare(index, algorithm):
    start = input[index + 1]
    end = input[index + 2]
    live_num = int(input[index + 3])
    node = {}
    for i in range(0, live_num):
        live = input[index + i + 4].split(" ")
        if live[0] in node.keys():
            node[live[0]].append(live[1])
        else:
            node[live[0]] = [live[1]]
    print node
    sat_num = int(input[index + live_num + 4])
    if algorithm == 'BFS':
        path = bfs(start, end, node)
        output_path(path)
    else:
        path = dfs(start, end, node)
        output_path(path)
    return index + live_num + sat_num + 5


def output_path(path):
    print path
    if path:
        i = 0
        for node in path:
            out.write(node + " " + str(i) + '\n')
            i += 1


def bfs(start, end, graph):
    queue = [[start]]
    if start == end:
        return [start]
    while queue:
        #print queue
        path = queue.pop(0)
        current = path[-1]
        #print current
        if current == end:
            return path
        if current in graph.keys():
            #print 'child'
            #print graph[current]
            for child in graph[current]:
                if path.__contains__(child):
                    continue
                else:
                    new_path = list(path)
                    new_path.append(child)
                    queue.append(new_path)
    return False


def dfs(start, end, graph):
    queue = [[start]]
    if start == end:
        return [start]
    while queue:
        path = queue.pop(0)
        current = path[-1]
        expand = False
        if current == end:
            return path
        for cur in queue:
            if cur[-1] == end:
                if len(cur) <= len(path):
                    expand = True
                else:
                    queue.remove(cur)
        if expand:
            continue
        if current in graph.keys():
            child_list = graph[current]
            queue_keep = []
            equal_insert = []
            for child in child_list:
                for cur in queue:
                    if cur[-1] == child:
                        if int(cur.index(child)) > len(path):
                            queue.remove(cur)
                        elif int(cur.index(child)) == len(path):
                            equal = [queue.index(cur) + 1, child]
                            equal_insert.append(equal)
                        else:
                            queue_keep.append(child)

            for equal_child in equal_insert[::-1]:
                new_path = list(path)
                new_path.append(equal_child[1])
                queue.insert(equal_child[0], new_path)

            for child in child_list[::-1]:
                if path.__contains__(child) or (child in queue_keep) or (child in equal_insert):
                    continue
                else:
                    new_path = list(path)
                    new_path.append(child)
                    queue.insert(0, new_path)
    return False


def ucs(index):
    #print index
    start = input[index + 1]
    end = input[index + 2]
    live_num = int(input[index + 3])
    for i in range(0, live_num):
        print input[index + i + 4]
    sat_num = int(input[index + live_num + 4])
    #for i in range(0,sat_num):
    #    print input[index + live_num + i + 5]
    return index + live_num + sat_num + 5


def a_search(index):
    #print index
    start = input[index + 1]
    end = input[index + 2]
    live_num = int(input[index + 3])
    for i in range(0, live_num):
        print input[index + i + 4]
    sat_num = int(input[index + live_num + 4])
    for i in range(0,sat_num):
        print input[index + live_num + i + 5]
    return index + live_num + sat_num + 5


search_method = {'BFS', 'DFS', 'UCS', 'A*'}
for i in range(0,len(input)):
    if input[i] == 'BFS' or input[i] == 'DFS':
        i = bfs_dfs_perpare(i, input[i])
    elif input[i] == 'UCS':
        ucs(i)
    elif input[i] == 'A*':
        a_search(i)
out.close()