import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import player

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        self.players = {}
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        #move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        #add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        #load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name]=pkl.load(open(name+'.idx','rb'))
                            except IOError: #chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps({"action":"login", "status":"ok"}))
                    else: #a client under this name has already logged in
                        mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print ('wrong code received')
            else: #client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
#==============================================================================
# handle connect request
#==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"connect", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"connect", "status":"no-user"})
                mysend(from_sock, msg)
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                #said = msg["from"]+msg["message"]
                said2 = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))
#==============================================================================
#                 listing available peers
#==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_sect(poem_indx)
                print('here:\n', poem)
                mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action":"time", "results":ctime}))
#==============================================================================
#                 search
#==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                search_rslt = (self.indices[from_name].search(term)).strip()
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"disconnect"}))
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
            elif msg['action'] == 'file exchange':
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"file exchange", "from":msg["from"], "file":msg["file"]}))
# =============================================================================
#               Try to start a game                
# =============================================================================
            elif msg['action'] == 'game':
                from_name = self.logged_sock2name[from_sock]
                the_other = self.group.list_me(from_name)[1]
                if msg['connect'] == False:
                    if len(self.group.list_me(from_name)) != 2:
                        mysend(from_sock,json.dumps({"action":"game","connect":False,"message":'Too many people here.'}))
                        other_guys = self.group.list_me(from_name)[1:]
                        for g in other_guys:
                            to_sock = self.logged_name2sock[g]
                            print('connection failed')
                            mysend(to_sock,json.dumps({"action":"game","connect":False,"message":'Too many people here.'}))
                    else:
                        try:
                            for g in self.group.list_me(from_name):
                                to_sock = self.logged_name2sock[g]
                                mysend(to_sock,json.dumps({"action":"game","connect":True,"message":'There you go.\n'}))
                                print("Connecting two players")
                        except:
                            print('no way')
                else:
                    try:
                        if from_name not in self.players:
                            print('found a new player')
                            print('creating object')
                            self.players[from_name] = player.Player(str(from_name))
                            print('adding to the list')
                            mysend(from_sock,json.dumps({"action":"game",'options':self.players[from_name].get_option(),'connect':True,'message':"select one option"}))
                            print('sending message')
                        else:
                            print('find'+from_name)
                            print(self.players[from_name].choice)
                            self.players[from_name].set_choice(msg['choice'])
                            print('choice set for '+ str(from_name)+' '+self.players[from_name].choice)
                            if (self.players[the_other].choice != ''):
                                print('both have choice')
#                                two_choice = ''
#                                for k,v in self.players.values():
#                                    two_choice += k + str(v.choice)
#                                result = self.players[from_name].fight(self.players[the_other])
#                                print('got result')
                                
                                while result == 'tie':
                                    print('result is tie')
                                    result = ''
                                    for g in self.group.list_me(from_name):
                                        print(g)
                                        print('updating info')
                                        self.players[g].update()
                                        self.players[g].clear_choice()
                                        print('finding sock')
                                        to_sock = self.logged_name2sock[g]
                                        mysend(to_sock,json.dumps({"action":"game","connect":True,"message":'tie','options':self.players[g].get_option()}))
                                        print('tie, sending msgs to '+ str(g))
                                
                                my_sock = self.logged_name2sock[from_name]
                                to_sock = self.logged_name2sock[the_other]
                                if result == True:
                                    result = ''
                                    mysend(my_sock,json.dumps({"action":"game","connect":False,"message":'you win'}))
                                    mysend(to_sock,json.dumps({"action":"game","connect":False,"message":'you lose'}))
                                    self.players = {}
                                elif result == False:
                                    result = ''
                                    mysend(my_sock,json.dumps({"action":"game","connect":False,"message":'you lose'}))
                                    mysend(to_sock,json.dumps({"action":"game","connect":False,"message":'you win'}))
                                    self.players = {}
                            else:
                                print('NOT both have choice')
                                pass
                    except:
                        print('dont work')
                                
                                        
# =============================================================================
#                 send files via sever    
# =============================================================================

        else:
            #client died unexpectedly
            self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)
def main():
    server=Server()
    server.run()

main()
