from Throughput_public import *

def TP(fn):
    t = Throughput(fn)
    print ('TP : 	%.3f' % t.calThroughput())
    print ('WPM:	%.3f' % (t.cps*12) ) 
    print ('UER:	%.3f' % (t.totalINF/(t.totalINF+t.totalC)) ) # uncorrected error rate

TP("example.json")
