# Copyright (c) 2018 Mingrui Zhang
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Throughput_public.py : calculate throughput from a text transcription json file
# Reference paper:
# Mingrui “Ray” Zhang, Shumin Zhai, Jacob O. Wobbrock. 2019. 
# Text Entry Throughput: Towards Unifying Speed and Accuracy in a Single Performance Metric. 
# In 2019 CHI Conference on Human Factors in Computing Systems Proceedings (CHI 2019)

from WagnerFischer import WagnerFischer as Edit
import json
import string
import numpy as np

str_to_num = {}
for i,j in enumerate(string.ascii_lowercase[:26]):
    str_to_num[j] = i
str_to_num[' '] = 26
str_to_num['0'] = 27 #'0' represents null character

#characcter frequency 'a'-'z' plus 'space', total 27 characters
char_freq = np.array([0.06545420428810268, 0.012614349400134882, 0.022382079660795914, 0.032895839710101495, 0.10287480840814522, \
            0.019870906945619955, 0.01628201251975626, 0.0498866519336527, 0.05679944220647908, 0.0009771967640664421, \
            0.005621008826086285, 0.03324279082953061, 0.020306796250368523, 0.057236004874678816, 0.061720746945911634,\
            0.015073764715016882, 0.0008384527300266635, 0.049980287430261394, 0.05327793252372975, 0.07532249847431097,\
            0.022804128240333354, 0.007977317166161044, 0.017073508770571122, 0.0014120607927983009, 0.014305632773116854,\
            0.0005138874382474097, 0.18325568938199557])

class Throughput(object):
    """Class for Throughput"""
    def __init__(self, filename):
        self.filename = filename
        try:
            self.json = json.load(open(filename))
        except Exception as e:
            raise "can not find the json file"
        # Instances of each transcription trial data
        self.trials = []
        
        # Transmission prob table p(i,j), from 'a-z', space, null to 'a-z', space, null
        self.table = np.zeros((28, 28)) 
        # Character distribution of 'a' to 'z', space and null
        self.prob = np.zeros(28)

        self.totalTime = 0.0 # total transcription time in sec
        self.totalChar = 0.0 # total characters in presented string
        self.cps = 0 # char per second
        self.totalINF = 0 # total incorrect not fixed error characters
        self.totalC = 0 # total correct transmitted characters

        translator = str.maketrans('', '', string.punctuation+'1234567890\n')
        # read data from the file
        for item in self.json:
            #[P, T, time] #time unit: second
            self.trials.append([item["Present"].lower().translate(translator), item["Transcribe"].lower().translate(translator), \
                                (item["Time"]) / 1000.0])

    '''Function for calculating the transmission probability table (P(i,j))'''
    def calErrorTable(self):
        for trial in self.trials:
            #Get edit distance
            diff = Edit(trial[0], trial[1])
            ids = diff.IDS()
            # incorrect : insertion/substitution/deletion(omission) error
            self.totalINF += (ids['I'] + ids['S'] + ids['D'])
            self.totalC += ids['M']
            self.totalChar += len(trial[1])
            self.totalTime += trial[2]

            # Then we add each error instance to its corresponding category
            # We need to take the number of alignments into consideration (because there might be multiple alignments for P and T)
            # For example, P - optimal T - optiacl
            # P1: optimal
            # T1: optiacl
            # P2: optima-l
            # T2: opti-acl
            # And we need to average them
            
            cnt = sum(1.0 for _ in diff.alignments())   # number of alignments
            for align in diff.alignments():
                index_P, index_T = 0, 0
                for j in range(len(align)):
                    if align[j] == 'I':
                        #Insertion error, add an instance to [null][character]
                        self.table[27, str_to_num[ trial[1][index_T] ] ] += 1.0/cnt
                        index_T += 1
                    elif align[j] == 'D':
                        #Deletion(omission) error, add an instance to [character][null]
                        self.table[ str_to_num[trial[0][index_P]], 27] += 1.0/cnt
                        index_P += 1
                    #substitute or equal, add an instance to [character_i][character_j]
                    else: 
                        self.table[ str_to_num[trial[0][index_P]], str_to_num[trial[1][index_T]] ] += 1.0/cnt
                        index_T += 1
                        index_P += 1

        # Count of all transcription instances
        allcount = np.sum(self.table)
        
        #every char's occurence in P (including null)
        rowsum = np.sum(self.table, axis = 1)
        #Normalized Character probability after taking null character into consideration
        self.prob =  rowsum / max(allcount, 1.0)

        #Turn count into probability
        self.table /= max(allcount, 1.0)

    """The function for calculating Throughput"""
    def calThroughput(self):
        # Step 1: the source entropy from English Letter Distribution
        source_entropy = - (char_freq * np.log2(char_freq)).sum()

        # Step 2: calculate transmission probs
        self.calErrorTable()

        prob_table = np.copy(self.table)
        char_prob = np.copy(self.prob)
        freq = np.copy(char_freq)

        # After including the null character 
        # We need to normalize the other character's distribution
        # P`(i) = p(i)*(1-p(null)) 
        # According to formula 5 in the paper
        char_prob[:-1] = (1-self.prob[-1]) * freq/freq.sum()
        # Here, we sum all probs of each error to get the overall error prob
        # According to formula 8, 9, 10 and 11
        # Then average them.
        # According to formula 12
        omit_prob    = self.table.sum(axis=0)[-1]
        insert_prob  = self.table.sum(axis=1)[-1]
        same_prob    = self.table.trace()
        sub_prob     = max(1.0 - (omit_prob+insert_prob+same_prob), 0)

        prob_table[-1, :-1] = insert_prob / 27.0
        prob_table[:-1, -1] = char_prob[:-1] * (omit_prob/(1-insert_prob))
        pt_trans = prob_table.transpose()
        pt_trans[:-1, :-1] = char_prob[:-1] * (sub_prob / (1-insert_prob)) / 26.0
        prob_table[:-1, :-1] = pt_trans[:-1, :-1].transpose()
        for i in range(27):
            prob_table[i, i] = char_prob[i] * (same_prob / (1-insert_prob))

        # After getting the average error prob from each character
        # We can calculate
        # the receiver(transcription) entropy
        # According to formula 6, 7 and 4
        transcribe_entropy = 0
        sum_y = np.sum(prob_table, axis = 0)
        for i in range(28): # every source char
            for j in range(28): # every received char
                p_xy = prob_table[i, j]
                py_x = p_xy / max(sum_y[j], 1e-10)
                if p_xy != 0:
                    transcribe_entropy -= p_xy * np.log2(py_x)  

        # Calculate speed: character per second 
        self.cps = self.totalChar / max(self.totalTime, 0.0001)
        # Throughput is the mutual information * cps
        return (source_entropy-transcribe_entropy) * self.cps

