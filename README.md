#### Shortest Path Routing using Link-State Algorithms 

> In this project, a shortest path routing algorithm has been implemented (Open Shorted Path First), and we have simulated the network topology routes through a JSON file. The network traffic is simulated by Network Forwarding Emulator or NFE via UDP connection.



##### How to run?

The environment to run this program is through python3.x. You will need to execute `nfe.py` first which reads in a topology graph and listens for all required routers for connection. You can simply run `nfe` and `router` on the same network.

`python3 nfe.py <IP> <port> <topo_filepath> `

For example:

`python3 nfe.py localhost 2000 topo.json`

Assume there are 7 routers/vertices needed in the `topo.json`, then you will need to open 7 more terminals and each enters the below command. `idx` is an index that will accumulates from 1 to 7 in this case.

`./virtualrouter <nfe-ip> <nfe-port> <virtual-router-id>`

For example:

`./vrouter.sh localhost 2000 <idx>`



##### Output 

1. Output Files:

   • topology_<routerID>.out_

   _• routingtable_<routerID>.out

   The first file is used to store database which represents the intermediate package exchange. The second file is to store the shortest path cost and next step from source, using Dijkstra's Algorithm

2. Standard Output:

   The standard output represents if the current router is sending initially, forwarding, receiving or dropping any packages. For example: with 3 triangle vertices

   ```
   Sending(E):SID(1),SLID(5),RID(1),RLID(5),LC(5) Sending(E):SID(1),SLID(5),RID(1),RLID(7),LC(7) Sending(E):SID(1),SLID(7),RID(1),RLID(5),LC(5) Sending(E):SID(1),SLID(7),RID(1),RLID(7),LC(7) Received:SID(2),SLID(5),RID(2),RLID(5),LC(5) Received:SID(2),SLID(5),RID(2),RLID(6),LC(6) Sending(F):SID(1),SLID(7),RID(2),RLID(5),LC(5) Sending(F):SID(1),SLID(7),RID(2),RLID(6),LC(6) Received:SID(3),SLID(7),RID(3),RLID(7),LC(7) Received:SID(3),SLID(7),RID(3),RLID(6),LC(6) Sending(F):SID(1),SLID(5),RID(3),RLID(7),LC(7) Sending(F):SID(1),SLID(3),RID(3),RLID(6),LC(6) Received:SID(2),SLID(5),RID(3),RLID(6),LC(6) Received:SID(2),SLID(5),RID(3),RLID(7),LC(7) Dropping:SID(2),SLID(5),RID(3),RLID(6),LC(6) Dropping:SID(2),SLID(5),RID(3),RLID(7),LC(7) Received:SID(3),SLID(7),RID(2),RLID(5),LC(5) Received:SID(3),SLID(7),RID(2),RLID(6),LC(6) Dropping:SID(3),SLID(7),RID(2),RLID(5),LC(5) Dropping:SID(3),SLID(7),RID(3),RLID(6),LC(6)
   ```

   #### Demo

   ![image-20200805202314299](C:\Users\gugab\AppData\Roaming\Typora\typora-user-images\image-20200805202314299.png)

   <i> picture is a reference from CS456 @ University of Waterloo</i>



##### Algorithm Citation:

The source code for Dijkstra's Algorithm is referenced from `https://startupnextdoor.com/dijkstras-algorithm-in-python-3/`	

