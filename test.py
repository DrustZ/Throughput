from throughput import *
from os import listdir
from os.path import isfile, join

def cleanNres(fn):
	res(clean(fn))

def clean(fn):
	js = json.load(open("exp_mobile\\"+fn))
	new1 = js[10:]
	with open("exp_mobile\cleaned\\"+fn, "w") as f:
		json.dump(new1, f, indent=4)
	return "exp_mobile\cleaned\\"+fn

def res(fn):
    t = Throughput(fn)
    t.calErrorTable()

    print ('[original]:  %.3f' % t.calThroughput())
    print ('[equalProb]: %.3f' % t.calThroughput(True)) # seeking for
    print ('[equalEntr]: %.3f' % t.calThroughput(sameEntropy = True)) 
    print ('[bothEqual]: %.3f' % t.calThroughput(True, True)) # seeking for
    print ('WPM:	%.3f' % (t.cps*12) )
    print ('UER:	%.3f' % (t.totalINF/(t.totalINF+t.totalC)) )

def pilot2(sub):
	for i in range(-2,3):
		print("sub: %d, cs: %d" % (sub, i))
		res("pilot2/sub"+str(sub)+"_cs"+str(i)+".json")
		
def exp1(sub):
	for i in range(-2,3):
		print("sub: %d, cs: %d" % (sub, i))
		res("exp/session1/sub"+str(sub)+"_cs"+str(i)+".json")
		
def exp2(sub):
	for i in range(-2,3):
		print("sub: %d, cs: %d" % (sub, i))
		res("exp/session2/sub"+str(sub)+"_cs"+str(i)+".json")

def combine(sub):
	mypath = "exp"
	files1 = [f for f in listdir(mypath+"\session1") if (isfile(join(mypath+"\session1", f)) and ('json' in f) and ('test' not in f))]
	for fn in files1:
		if sub not in fn:
			continue
		print (fn)
		json1 = json.load(open("exp\session1\\"+fn))
		json2 = json.load(open("exp\session2\\"+fn))
		new1 = json1[10:]
		new2 = json2[10:]
		with open("exp\cleaned\\"+fn.split(".")[0]+"_1.json", "w") as f:
			json.dump(new1, f, indent=4)
		with open("exp\cleaned\\"+fn.split(".")[0]+"_2.json", "w") as f:
			json.dump(new2, f, indent=4)
		new1.extend(new2)
		with open("exp\cleaned\\"+fn.split(".")[0]+".json", "w") as f:
			json.dump(new1, f, indent=4)

def exp(session, sub):
	for i in range(-2,3):
		print("sub: %d, cs: %d" % (sub, i))
		res("exp/cleaned/sub"+str(sub)+"_cs"+str(i)+session+".json")

def exportExpToCsv(session, sub):
	cont = "CS, TP_original, TP_equalProb, TP_equalEntr, TP_bothEqual\n"
	for i in range(-2,3):
		print("sub: %d, cs: %d" % (sub, i))
		t = Throughput("exp/cleaned/sub"+str(sub)+"_cs"+str(i)+session+".json")
		t.calErrorTable()
		cont += '%d, %.3f, %.3f, %.3f, %.3f\n' % (i, t.calThroughput(), t.calThroughput(True), t.calThroughput(sameEntropy = True), t.calThroughput(True, True) )
	with open("data_"+str(sub)+session+".csv", 'w') as f:
		f.write(cont)

def countN():
	mypath = "exp_mobile"
	files1 = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and ('json' in f) and ('test' in f))]
	W = 0
	for fn in files1:
		print (fn)
		json1 = json.load(open("exp_mobile\\"+fn))
		W += int(json1[-1]["Trial"])
	print (W)
		