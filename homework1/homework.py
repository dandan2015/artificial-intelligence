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
        print queue
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


def ucs_perpare(index, algorithm):
    start = input[index + 1]
    end = input[index + 2]
    graph = {}
    live_num = int(input[index + 3])
    for i in range(0, live_num):
        live = input[index + i + 4].split(" ")
        edge = []
        edge.append(live[1])
        edge.append(int(live[2]))
        if live[0] in graph.keys():
            graph[live[0]].append(edge)
        else:
            graph[live[0]] = [edge]
    print graph
    sat_num = int(input[index + live_num + 4])
    if algorithm == 'UCS':
        ucs(graph, start, end)
    return index + live_num + sat_num + 5


def ucs(graph, start, end):
    open = [[0, start, 0, 0, None]] # num, state, depth, cost, parent
    num = 0 #initial
    closed = []
    while open:
        current = open.pop(0)
        if current[1] == end:

            path = generate_path(open, closed, current)
            return [path, current[3]]

        if current[1] in graph.keys():
            children = graph[current[1]]
            while children:
                child = children.pop(0)
                exist_in_open = False
                node_in_open_cost = -1
                node_in_open_index = -1
                exist_in_closed = False
                node_in_closed_cost = -1
                node_in_closed_index = -1
                for state in open:
                    if state[1] == child[0]:
                        if exist_in_open:
                            if node_in_open_cost > state[3]:
                                node_in_open_cost = state[3]
                                node_in_open_index = open.index(state)
                        else:
                            exist_in_open = True
                            node_in_open_cost = state[3]
                            node_in_open_index = open.index(state)

                for state in closed:
                    if state[1] == child[0]:
                        if exist_in_closed:
                            if node_in_closed_cost > state[3]:
                                node_in_closed_cost = state[3]
                                node_in_closed_index = closed.index(state)
                        else:
                            exist_in_closed = True
                            node_in_closed_cost = state[3]
                            node_in_closed_index = closed.index(state)

                if not exist_in_open and not exist_in_closed:
                    # add child
                    inserted = False
                    num += 1
                    node = [num, child[0], current[2] + 1, current[3] + child[1], current[0]]
                    for state in open:
                        if state[3] > current[3] + child[1]:
                            open.insert(open.index(state), node)
                            inserted = True
                            break

                    if not inserted:
                        open.insert(len(open), node)

                elif exist_in_open:
                    if current[3] + child[1] < node_in_open_cost:
                        open.pop(node_in_open_index)
                        inserted = False
                        num += 1
                        node = [num, child[0], current[2] + 1, current[3] + child[1], current[0]]
                        for state in open:
                            if state[3] > current[3] + child[1]:
                                open.insert(open.index(state), node)
                                inserted = True
                                break

                        if not inserted:
                            open.insert(len(open), node)

                elif exist_in_closed:
                    if current[3] + child[1] < node_in_closed_cost:
                        closed.pop(node_in_closed_index)
                        inserted = False
                        num += 1
                        node = [num, child[0], current[2] + 1, current[3] + child[1], current[0]]
                        for state in open:
                            if state[3] > current[3] + child[1]:
                                open.insert(open.index(state), node)
                                inserted = True
                                break

                        if not inserted:
                            open.insert(len(open), node)

        closed.append(current)
    return False


def generate_path(open, closed, end):
    path = []
    current = end
    record = [end[1], end[3]]
    path.append(record)

    while current[4] != None:
        parent = current[4]
        in_open = False
        for node in open:
            if node[0] == parent:
                record = [node[1], node[3]]
                path.insert(0, record)
                current = node
                in_open = True
                break
        if not in_open:
            for node in closed:
                if node[0] == parent:
                    record = [node[1], node[3]]
                    path.insert(0, record)
                    current = node
                    break

    for point in path:
        out.write(point[0] + ' ' + str(point[1]) + '\n')



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
        ucs_perpare(i, input[i])
        #ucs(i)
    elif input[i] == 'A*':
        a_search(i)
out.close()