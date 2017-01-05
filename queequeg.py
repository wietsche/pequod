### bring files over from s3########################
missionFile = sys.argv[1]
s3scanFile = sys.argv[2]

locMissionFile = '/tmp/'+os.path.basename(missionFile)

AWS_KEY = 'AKIAITC6LDENNQBKSW3A'
AWS_SECRET = '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' 

aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
bucket = aws_connection.get_bucket('za.mission')
key = bucket.get_key(missionFile)
key.get_contents_to_filename(locMissionFile)

with open(locMissionFile, 'r') as f:
        doc = yaml.load(f)

#local signature
s3sigFile = doc['mission']['signature']['file']
bucket = aws_connection.get_bucket('za.audio')
key = bucket.get_key(missionFile)
key.get_contents_to_filename(locMissionFile)



signature = '/tmp/' + os.path.basename(s3sigFile)
cmd = 'aws s3 cp ' + s3sigFile + ' ' + signature
os.system(cmd)

#local file to be scanned
signalfile = '/tmp/' + os.path.basename(s3scanFile)
cmd = 'aws s3 cp ' + s3scanFile + ' ' + signalfile
os.system(cmd)
################################################


