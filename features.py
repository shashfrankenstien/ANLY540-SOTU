from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import json, collections, requests, sys
import animation
import matplotlib

POS=['NN', 'JJ', 'PR', 'RB', 'VB']

def rate(sent):
	return requests.post('http://twirates.com/rate', json={'sentence':sent}, headers={'Auth':'MyRaterAuthKey'}).json()

def round(x):
	if x-int(x) < 0.5:
		return int(x)
	else: return int(x)+1

def posCount(taggedSent, POSCount):
	for word, tag in taggedSent:
		if tag[:2] in POS:
			POSCount[tag[:2]] +=1
	return POSCount 

def posAndRate(listOfSents):
	end = len(listOfSents)
	listofTaggedSents = []
	POSCount = {p:0 for p in POS}
	ratingStats = {'1':0, '2':0, '3':0, '4':0, '5':0, 'totalRated': 0, 'posit':0, 'neg':0}
	for sent in listOfSents:
		try: 
			raterOut = rate(sent)
			if (raterOut['polarity'] =='posit' and int(raterOut['rating'])>=3) or (raterOut['polarity'] =='neg' and int(raterOut['rating'])<3):
				ratingStats[str(raterOut['rating'])] += 1
				ratingStats['totalRated'] += 1
				ratingStats[raterOut['polarity']] += 1
			else: pass
			# print sent, json.dumps(raterOut, indent=4)
			# raw_input()
		except Exception, e:
			print e
		taggedSent = pos_tag(word_tokenize(sent))
		listofTaggedSents.append(taggedSent)
		POSCount = posCount(taggedSent, POSCount)

	for key, value in ratingStats.iteritems():
		if key != 'totalRated':
			ratingStats[key] = value*100.0/ratingStats['totalRated']

	return listofTaggedSents, POSCount, ratingStats

# @animation.wait('bar')
def splitStats(listOfSents):
	start=0
	out={}
	tenPercent = int(len(listOfSents)/10)
	for checkPoint in xrange(tenPercent, len(listOfSents), tenPercent):
		_, POSCount, ratingStats = posAndRate(listOfSents[start:checkPoint])
		out[round(checkPoint*10.0/len(listOfSents))*10] = {'POSCount':POSCount, 'rating': ratingStats}
		start = checkPoint
	return collections.OrderedDict(sorted(out.items()))


with open('./Obama-SOTU-2015.txt', 'r') as o2015:
	obama2015 = o2015.read().decode('ascii','ignore').replace('\r', '')

with open('./Obama-SOTU-2016.txt', 'r') as o2016:
	obama2016 = o2016.read().decode('ascii','ignore').replace('\r', '')


obama = {'obama2015':{
			'fullText':obama2015
			}, 
		'obama2016':{
			'fullText':obama2016
			}
		}
wait = animation.Wait('spinner')
print "Extracting features"
wait.start()
for key, obiwan in obama.iteritems():
	sents = sent_tokenize(obiwan['fullText'])
	obiwan['sentCount'] = len(sents)
	words = word_tokenize(obiwan['fullText'])
	obiwan['wordCount'] = len(words)
	obiwan['averageWPS'] = obiwan['wordCount']/obiwan['sentCount']
	# obiwan['POSTagged'], obiwan['POSCount'], obiwan['ratingStats'] = posAndRate(sents)
	obiwan['POSStats'] = splitStats(sents)
	obama[key] = obiwan


wait.stop()
for key,value in obama.iteritems():
	print '---------'
	print key
	print '---------'
	for inKey, inValue in value.iteritems():
		if inKey!='fullText' and inKey!='POSTagged':
			if type(inValue)==dict or type(inValue)==collections.OrderedDict: 
				print '{}:\t\t{}'.format(inKey, json.dumps(inValue, indent = 4))
			else: print '{}:\t\t{}'.format(inKey, inValue)
	print "========================"



	

