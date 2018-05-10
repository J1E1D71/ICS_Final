# -*- coding: utf-8 -*-
"""
Created on Thu May 10 14:46:01 2018

@author: Lenovo
"""
import random
def generator():
    with open("fixed_two_2.txt", "r") as f_20:   
        word_22 = f_20.readlines()
    
    with open("fixed_three_2.txt", "r") as f_32:   
        word_32 = f_32.readlines()
        
    return word_22[random.randint(0,100)].strip()+ word_22[random.randint(0,100)].strip() + word_32[random.randint(0,100)].strip()