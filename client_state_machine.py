"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import os
import base64

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                elif my_msg [:12]=="write a poem":
                    mysend(self.s,json.dumps({"action":"write"}))
                    sentence = json.loads(myrecv(self.s))["results"].strip()
                    self.out_msg += sentence

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                elif my_msg[:10] == 'send file:':
                    file_name = my_msg[10:]
                    if os.path.isfile(file_name):
                        with open(file_name, 'rb') as f:
                            data = base64.b64encode(f.read())
                            data = data.decode('utf-8')
                            self.out_msg += 'file read'
                        try:
                            
                            mysend(self.s,json.dumps({"action":"file exchange", "from":"[" + self.me + "]", "file":data,'message':'You should check the new file.'}))
                            self.out_msg += 'file sent'
                        except:
                            self.out_msg += 'no such file'
                elif my_msg == "let's play a game":
                    mysend(self.s,json.dumps({"action":"game", "from":"[" + self.me + "]","connect":False}))
                    self.out_msg += 'waiting for response......'
            
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg['action'] == 'file exchange':
                    save_path = r"C:\Users\Lenovo\desktop"
                    data = peer_msg['file']
                    data = bytes(data,encoding = 'utf-8')
                    try:
                        with open('pic_received.jpg', 'wb') as f:
                            data = base64.b64decode(data)
                            f.write(data)
                        self.out_msg += 'you got a file from' + peer_msg['from']
                    except:
                        self.out_msg += 'can not write'
                elif peer_msg['action'] == 'game':
                    if peer_msg['connect'] == False:
                        self.out_msg += peer_msg['message']
                    else:
                        try:
                            self.out_msg += peer_msg['message']
                            mysend(self.s,json.dumps({'action':'game','connect':True}))
                            self.out_msg += 'changing state'
                            self.state = S_GAME
                        except:
                            self.out_msg += 'something wrong 1'
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                
# =============================================================================
#           GAME STATE!              
# =============================================================================
        elif self.state == S_GAME:
            try:
                if len(peer_msg) > 0:
                    print('got message')
                    peer_msg = json.loads(peer_msg)
#                    print(peer_msg)
                    if peer_msg['connect'] == True:
                        msg = peer_msg['message']
                        self.out_msg += msg + '\n'
                        if 'options' in peer_msg:
                            options = peer_msg['options']
                            for i in range(len(options)):
                                self.out_msg += str(i) + ':' + options[i] + '\t'
                    else:
                        result = peer_msg ['message']
                        self.out_msg += result
                        self.state = S_CHATTING
                
                if len(my_msg) > 0 :
                    mysend(self.s,json.dumps({'action':'game','connect':True, 'choice':int(my_msg)}))
                    self.out_msg += 'message sent, choice is ' + str(my_msg)
            except:
                self.out_msg += 'something wrong 2'
                
                
                
                
            
                
    
                
                                
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
