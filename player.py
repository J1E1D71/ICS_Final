# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 18:56:08 2018

@author: Lenovo
"""

class Player:
    def __init__(self,name):
        self.name = name
        self.energy = {'cut':0,'wave':0}
        self.options = ['defense','wave e','cut e']
        self.choice = ''
    
    def update(self):

        if self.choice == 'defense':
            pass
        
        elif self.choice == 'wave e':
            self.set_energy('wave',1)
        
        elif self.choice == 'cut e':
            self.set_energy('cut',1)
        
        elif self.choice == 'wave':
            self.set_energy('wave',-1)
        
        elif self.choice == 'cut':
            self.set_energy('cut',-1)
        
        elif self.choice == 'wave 2':
            self.set_energy('wave',-2)
        
        elif self.choice == 'cut 2':
            self.set_energy('cut',-2)
            
        elif self.choice == 'wave 3':
            self.set_energy('wave',-3)
        
        elif self.choice == 'cut 3':
            self.set_energy('cut',-3)
        
        self.add_opition()
        
    
    def set_energy(self,kind,change):
        self.energy[kind] += change
    
    def add_opition(self):
        for i in ['wave','cut']:
            if (self.energy[i] == 1) and (i not in self.options):
                self.options.append(i) 
            
            elif (self.energy[i] == 2) and ( str(i+' 2') not in self.options):
                self.options.append(str(i+' 2')) 
            
            elif (self.energy[i] == 3) and ((i+' 3') not in self.options):
                self.options.append(str(i+' 3')) 
            
            
    def set_choice(self,num):
        self.choice = self.options[num]
        
    
    def get_option(self):
        return self.options
    
    def clear_choice(self):
        self.choice = ''
    
    def fight(self,enemy):
        non_attack = ['defense','wave e','cut e']
        attack = ['cut','wave','cut 2','wave 2','cut 3','wave 3']
        if self.choice == enemy.choice:
            return 'tie'
        
        elif (self.choice in non_attack) and (enemy.choice in non_attack):
            return 'tie'
        
        elif self.choice == 'defense':
            return 'tie' if enemy.choice == 'wave' else False

        elif (self.choice in attack) and (enemy.choice in attack):
            return True if (attack.index(self.choice) > attack.index(enemy.choice)) else False

        elif self.choice == 'wave' and enemy.choice == 'defense':
            return 'tie'  
        
        elif enemy.choice[:3] == 'cut' and self.choice == 'cut e':
            if (int(self.choice[-1]) - 1) <= self.energy['cut e']:
                return 'tie'
        elif (self.choice in attack) and (enemy.choice in non_attack):
            return True
        
        else:
            return False

a = Player('new')
      
        
        
        
            