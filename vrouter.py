import socket
import sys
from packet import InitMessage, InitReplyMessage, LSA
from dijkstras_shortest_path import GraphUndirectedWeighted, dijkstra


class Database:

    '''
    database to store 
    1. topology information
    2. routing table maintaining shortest path
    '''

    def __init__(self):
        self.db = []
        self.routing_table = []

    def init_db(self, router_id, neighbour):
        for i in range(len(neighbour)):
            self.db.append([router_id, neighbour[i][0], None, neighbour[i][1]])
    
    def if_edge_exist(self, edge, router_id):
        for i in range(len(self.db)): 
            ver = self.db[i][0]
            other_edge = self.db[i][1]            
            if other_edge == edge:
                if ver != router_id:
                    return i
                else:
                    return -2 # already has this info
        return -1

    def dest_exist(self, d):
        idx = 0
        for row in self.routing_table:
            if row[0] == d:
                return idx
            idx += 1
        return -1

    def add(self, router_link_id, router_id, router_link_cost, my_id):

        # if this edge information exists 
        i = self.if_edge_exist(router_link_id, router_id)

        target = [router_id, router_link_id, self.db[i][0], router_link_cost]
        # already have the information, then drop it
        if target in self.db:
            return False

        if i >= 0:
            # update existing record
            self.db[i][2] = router_id
            self.db[i][3] = router_link_cost
            
            self.db.append(target)

            # update output file
            with open("topology_" + str(router_id) + ".out", "a") as f:
                f.write("\nTOPOLOGY\n")
                for i in range(len(self.db)):
                    if self.db[i][2] != None:
                        f.write("router:%d,router:%d,linkid:%d,cost:%d\n" % (self.db[i][0], self.db[i][2], self.db[i][1], self.db[i][3]))

        elif i == -2:
            return False
        elif i == -1:
            # insert new record
            self.db.append([router_id, router_link_id, None, router_link_cost])

        # update rt  
        self.update_rt_via_dijkstra(router_id, my_id)

        return True
    
    
    def update_rt_via_dijkstra(self, dest, my_id):

        # prepare for graph
        valid_row = [_ for _ in self.db if _[2] != None]
        vertex = set()
        edge = {}

        # separate edge and vetex
        for row in valid_row:
            vertex.add(row[0])
            vertex.add(row[2])
            # filter for edges
            if row[1] not in edge:
                edge[row[1]] = [row[0], row[2], row[3]]

        # build the graph
        if len(vertex) == 0 or not dest in vertex or my_id not in vertex: 
            return 

        map_vertex_to_idx = {}
        map_idx_to_vertex = {}
        counter = 0
        for v in vertex:
            map_vertex_to_idx[v] = counter
            map_idx_to_vertex[counter] = v
            counter += 1

        g = GraphUndirectedWeighted(len(vertex))
        for e in list(edge.values()):
            e1, e2, cost = e
            g.add_edge(map_vertex_to_idx[e1], map_vertex_to_idx[e2], cost)

        
        # compute min cost
        shortest_path, cost = dijkstra(g, map_vertex_to_idx[my_id], map_vertex_to_idx[dest])

        try:
            # if cost is inf, this will fail
            cost = int(cost)
        except:
            return
        
        # get next vertex
        next_vertex = map_idx_to_vertex[shortest_path[0]] if len(shortest_path) == 1 else map_idx_to_vertex[shortest_path[1]]

        # if destination exists, re-calc for a smaller cost. if not exist, insert
        i = self.dest_exist(dest)
        if i != -1:
            # compare cost
            if self.routing_table[i][1] > cost:
                self.routing_table[i] = [dest, cost, next_vertex]
                # update rt output file
                with open("routingtable_" + str(router_id) + ".out", "a") as f:
                    f.write("\nROUTING\n")
                    for record in self.routing_table:
                        f.write("%d:%d,%d\n" % (record[0], record[1], record[2]))
        else: 
            self.routing_table.append([dest, cost, next_vertex])
            # update rt output file
            with open("routingtable_" + str(router_id) + ".out", "a") as f:
                f.write("\nROUTING\n")
                for record in self.routing_table:
                    f.write("%d:%d,%d\n" % (record[0], record[1], record[2]))
        
# read in nfe-ip and nfe-port for connection
nfe_ip = sys.argv[1]
nfe_port = int(sys.argv[2])
router_id = int(sys.argv[3])

# establish UDP socket, no need to bind
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# INIT: send to nfe
udp_socket.sendto(InitMessage(router_id).pkg, (nfe_ip, nfe_port))

# INIT REPLY: decode the pkg from nfe
recv_pkg, _ = udp_socket.recvfrom(4096)
reply_pkg = InitReplyMessage(recv_pkg)

# init the database
db = Database()

db.init_db(router_id, reply_pkg.link_entry)


# send my link information initially as pemutation
for link in reply_pkg.link_entry:
    for link2 in reply_pkg.link_entry:
        to_send = LSA(router_id, link[0], router_id, link2[0], link2[1])
        udp_socket.sendto(to_send.init_pkg(), (nfe_ip, nfe_port))
        
        # print send stdout 
        print("Sending(E):SID(%d),SLID(%d),RID(%d),RLID(%d),LC(%d)" % (router_id, link[0], router_id, link2[0], link2[1]))

# LSA Phase
I_am_awesome = True

# loop to listen for messages
while I_am_awesome:
    
    recv_pkg, _ = udp_socket.recvfrom(4096)

    # parse the received package
    lsa_pkg = LSA()
    lsa_pkg.parse_pkg(recv_pkg)
    # print send stdout 
    print("Received:SID(%d),SLID(%d),RID(%d),RLID(%d),LC(%d)" % (lsa_pkg.sender_id, lsa_pkg.sender_link_id, lsa_pkg.router_id, lsa_pkg.router_link_id, lsa_pkg.router_link_cost))

    # ensures we do not forward info abt myself again
    if lsa_pkg.router_id != router_id:
        # try to add it, get False if information already exist
        result = db.add(lsa_pkg.router_link_id, lsa_pkg.router_id, lsa_pkg.router_link_cost, router_id)

        # result == True ensures we have not forward this before 
        if result == True:
            for link in reply_pkg.link_entry:
                # find the edge to forward
                if link[0] != lsa_pkg.sender_link_id:
                    # create forward pkg
                    forward_pkg = LSA(router_id, link[0], lsa_pkg.router_id, lsa_pkg.router_link_id, lsa_pkg.router_link_cost)
                    # print send stdout 
                    print("Sending(F):SID(%d),SLID(%d),RID(%d),RLID(%d),LC(%d)" % (router_id, link[0], lsa_pkg.router_id, lsa_pkg.router_link_id, lsa_pkg.router_link_cost))
                    # forward  
                    udp_socket.sendto(forward_pkg.init_pkg(), (nfe_ip, nfe_port))

            
        else:
            # print send stdout 
            print("Dropping:SID(%d),SLID(%d),RID(%d),RLID(%d),LC(%d)" % (lsa_pkg.sender_id, lsa_pkg.sender_link_id, lsa_pkg.router_id, lsa_pkg.router_link_id, lsa_pkg.router_link_cost))





