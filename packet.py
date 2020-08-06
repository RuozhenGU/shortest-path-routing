import socket
import sys

'''
    create interface for messages
'''

class InitMessage:
    '''
    interface for initial hello message
    '''
    def __init__(self, router_id):
        self.message_type = 1
        self.router_id = router_id
        self.pkg = self.init_pkg()

    def init_pkg(self):
        pkg = bytearray()
        pkg.extend(self.message_type.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.router_id.to_bytes(length=4, byteorder="big"))
        return pkg


class InitReplyMessage:
    '''
    interface for initial reply message
    '''
    def __init__(self, pkg):
        self.message_type = 4
        self.num_of_link, self.link_entry = self.parse_pkg(pkg)

    def parse_pkg(self, pkg):
        num_of_link = int.from_bytes(pkg[4:8], byteorder="big")
        link_entry = []
        for i in range(num_of_link):
            start = i * 8 + 8
            mid = start + 4
            end = start + 8
            id = int.from_bytes(pkg[start: mid], byteorder="big")
            cost = int.from_bytes(pkg[mid: end], byteorder="big")
            link_entry.append((id, cost))

        return num_of_link, link_entry

class LSA:
    '''
    interface for LSA package exchange, support encode/decode
    '''
    def __init__(self, 
                 send_id=None, 
                 sender_link_id=None,
                 router_id=None,
                 router_link_id=None,
                 router_link_cost=None
                 ):
        self.message_type = 3
        self.sender_id = send_id
        self.sender_link_id = sender_link_id
        self.router_id = router_id
        self.router_link_id = router_link_id
        self.router_link_cost = router_link_cost

    def init_pkg(self):
        pkg = bytearray()
        pkg.extend(self.message_type.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.sender_id.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.sender_link_id.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.router_id.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.router_link_id.to_bytes(length=4, byteorder="big"))
        pkg.extend(self.router_link_cost.to_bytes(length=4, byteorder="big"))
        
        return pkg

    def parse_pkg(self, pkg):
        self.sender_id = int.from_bytes(pkg[4:8], byteorder="big")
        self.sender_link_id = int.from_bytes(pkg[8:12], byteorder="big")
        self.router_id = int.from_bytes(pkg[12:16], byteorder="big")
        self.router_link_id = int.from_bytes(pkg[16:20], byteorder="big")
        self.router_link_cost = int.from_bytes(pkg[20:24], byteorder="big")

    def __eq__(self, other): 
        if isinstance(other, LSA):
            return (
                self.sender_id == other.sender_id and \
                self.sender_link_id == other.sender_link_id and \
                self.router_id == other.router_id and \
                self.router_link_id == other.router_link_id and \
                self.router_link_cost == other.router_link_cost
            )
        return False