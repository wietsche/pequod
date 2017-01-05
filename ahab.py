#!/usr/bin/python
import sys
import yaml
import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
import os
import numpy as np
from datetime import datetime,timedelta


AWS_KEY = 'AKIAITC6LDENNQBKSW3A'
AWS_SECRET = '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' 
TWITTER_KEY = 'p3iv6FH7pL7hyOUNh3yygjBCU'
TWITTER_SECRET = 'dJDzSke1Dy7IrnN6FzWvx53JJj6A7v5mVFSCCHwuf24ha3Y4Wz'
ACCESS_TOKEN = '3953960675-6zIeSHd7LbYuzJF5y679oQ25cX9pxvAvbd1q5mV'
ACCESS_TOKEN_SECRET = 'hlJKpdp4mscdasu9jiNhSQ63qEY7aUXMU7eFWDOC86YYz'



s3missionFile = sys.argv[1]
missionFile = '/tmp/'+os.path.basename(s3missionFile)
aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
bucket = aws_connection.get_bucket('za.mission')
key = bucket.get_key(s3missionFile)
key.get_contents_to_filename(missionFile)

with open(missionFile, 'r') as f:
        doc = yaml.load(f)

missionName = doc['mission']['name'] 
houradd = int(doc['mission']['input']['timeadj'])

def getTimeFromFilename(wavfile):
    fileNoPath = wavfile.split("/")[-1:][0].split(".")[0]
    #e.g: kfm_2015-04-14_08-30-01__8kmono.wav
    
    filePart = fileNoPath.split("_")
    datePart = np.asarray(filePart[1].split("-")).astype(int)
    timePart = np.asarray(filePart[2].split("-")).astype(int)
    stDateTime = (datetime(datePart[0],datePart[1],datePart[2]
                       ,timePart[0] ,timePart[1],timePart[2]))
    
    return stDateTime



def workdir():
    #make working directories
    cmd = 'rm -rf /tmp/'+missionName+'/'
    cmd += ';  mkdir /tmp/'+missionName
    #print cmd
    os.system(cmd)
    cmd = 'ssh -i wietsche.pem root@$PEQUOD_PUBLIC_IP "'+cmd+'"'
    #print cmd
    os.system(cmd)
    return

workdir()

#local signature
s3sigFile = doc['mission']['signature']['file']
th = doc['mission']['signature']['score_thresh']
cmd = 'aws s3 cp ' + s3sigFile + ' /tmp/' + missionName
os.system(cmd)
signature = missionName +'/'+os.path.basename(s3sigFile)
cmd = 'scp -i wietsche.pem /tmp/'+ signature + ' root@$PEQUOD_PUBLIC_IP:/tmp/'+signature
os.system(cmd)


#find list of files already processed
procd = []
outputpath = doc['mission']['result']['path']
resultbucket = aws_connection.get_bucket('za.mission')
keys = resultbucket.list(outputpath)
for key in keys:
    infile = os.path.basename(key.name)
    if "csv" in infile:
        filetime = getTimeFromFilename(infile)
        procd.append(filetime)



#configure sqs, twitter queue
conn = boto.sqs.connect_to_region("us-west-2")
twitq = conn.get_queue('twitter')
twitmes = doc['mission']['message']['text'] 


#list files to process
audiopath = doc['mission']['input']['path']
inbucket = aws_connection.get_bucket('za.audio')
keys = inbucket.list(audiopath)
for key in keys:
    #infile = os.path.basename(key.name)
    infile = key.name
    print "Now processing: " + infile
    if "wav" in infile: 
        filetime = getTimeFromFilename(infile)
        #print str(filetime)
        if not (filetime in procd):
            print infile + " will be now be processed"
            #process:
            cmd = 'aws s3 cp s3://za.audio/' + infile + ' /tmp/' + missionName
            os.system(cmd)
            signalfile = missionName +'/'+os.path.basename(infile)
            cmd = 'scp -i wietsche.pem /tmp/'+ signalfile + ' root@$PEQUOD_PUBLIC_IP:/tmp/'+signalfile
            print cmd
            os.system(cmd)
            cmd = "$PEQUOD_HOME/queequeg.sh "+ signalfile + " " + signature
            os.system(cmd)
            #bring results back
            csvfile = signalfile.replace('.wav','.csv')
            try:
                cmd = 'scp -i wietsche.pem root@$PEQUOD_PUBLIC_IP:/tmp/'+csvfile + ' /tmp/' + csvfile
                print cmd
                os.system(cmd)

                #iterate though csv to check for hits
                i=0
                f=open("/tmp/"+csvfile,'r')
                for line in f:
                    vals = line.split(',')
                    print vals
                    if float(vals[3]) > float(th):
                        dt = filetime + timedelta(hours=houradd, minutes=float(vals[1]),seconds=round(float(vals[2]),0))
                        m = Message()
                        msg = twitmes +" @ "+str(dt)[:19]
                        print msg
                        m.set_body(msg)
                        twitq.write(m)

                os.system(cmd)
                cmd = 'aws s3 mv /tmp/'+csvfile + ' s3://za.mission/' + outputpath +  "/"
                print cmd
                os.system(cmd)

            except Exception: 
                  pass
workdir()
print "DONE"
