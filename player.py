# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 18:56:08 2018

@author: Lenovo
"""

class Player:
    def __init__(self,name):
        self.name = name
        self.energy = {'wave':0,'stone':0}
        self.options = ['defense wave','wave energy +1','stone +1']
        self.choice = ''
    
    def update(self):

        if self.choice == 'defense wave':
            pass
        
        elif self.choice == 'wave energy +1':
            self.set_energy('wave',1)
        
        elif self.choice == 'stone +1':
            self.set_energy('stone',1)
        
        elif self.choice == 'wave 1':
            self.set_energy('wave',-1)
        
        elif self.choice == 'stone 1':
            self.set_energy('stone',-1)
        
        elif self.choice == 'wave 2':
            self.set_energy('wave',-2)
        
        elif self.choice == 'stone 2':
            self.set_energy('stone',-2)
            
        elif self.choice == 'wave 3':
            self.set_energy('wave',-3)
        
        elif self.choice == 'stone 3':
            self.set_energy('stone',-3)
        
        self.add_opition()
        
    
    def set_energy(self,kind,change):
        self.energy[kind] += change
    
    def add_opition(self):
        attack = ['stone 1','wave 1','stone 2','wave 2','stone 3','wave 3']
        for i in ['wave','stone']:
            if (self.energy[i] == 1) and (str(i+' 1') not in self.options):
                self.options.append(str(i+' 1')) 
            
            elif (self.energy[i] == 2) and ( str(i+' 2') not in self.options):
                self.options.append(str(i+' 2')) 
            
            elif (self.energy[i] == 3) and (str(i+' 3') not in self.options):
                self.options.append(str(i+' 3')) 
        for i in self.options:
            if i in attack:
                try:
                    value = int(i[-1])
                except:
                    value = 1
                if value > self.energy[i[:5].strip()]:
                    self.options.remove(i)
            
            
    def set_choice(self,num):
        self.choice = self.options[num]
        
    
    def get_option(self):
        return self.options
    
    def clear_choice(self):
        self.choice = ''
    
    def fight(self,enemy):
        non_attack = ['defense wave','wave energy +1','stone +1']
        attack = ['stone 1','wave 1','stone 2','wave 2','stone 3','wave 3']
        if self.choice == enemy.choice:
            return 'tie'
        
        elif (self.choice in non_attack) and (enemy.choice in non_attack):
            return 'tie'
        
        elif self.choice == 'defense wave':
            return 'tie' if enemy.choice == 'wave' else False

        elif (self.choice in attack) and (enemy.choice in attack):
            return True if (attack.index(self.choice) > attack.index(enemy.choice)) else False

        elif self.choice == 'wave' and enemy.choice == 'defense wave':
            return 'tie'  
        
        elif enemy.choice[:5] == 'stone' and self.choice == 'stone +1':
            if (int(enemy.choice[-1]) - 1) <= self.energy['stone']:
                return 'tie'
            else:
                return False

        elif (self.choice in attack) and (enemy.choice in non_attack):
            return True
        
        else:
            return False

a = Player('new')
b = Player('old')      
        
        
        
        
        
            
