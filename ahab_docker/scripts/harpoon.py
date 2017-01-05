from boto.s3.connection import S3Connection
from datetime import datetime
from features import logfbank
from features import mfcc as mfcc_func
from py4j.java_gateway import java_import
from pyspark import SparkContext
from pyspark.mllib.linalg import DenseVector
from pyspark.mllib.regression import LabeledPoint
import numpy as np
import os
import os.path
import scipy.io.wavfile as wav
import sys
import time
import yaml

#os.environ["SPARK_HOME"] = "/opt/spark/spark-1.4.1-bin-hadoop2.6"
#os.environ["SPARK_HOME"] = "/root/spark"


#SPARK_HOST = sys.argv[1]
signalfile = "/tmp/"+sys.argv[1]   #the audio stream file, relative to /tmp/
signature = "/tmp/"+sys.argv[2]    #the file to match, relative to /tmp/
spark_url = sys.argv[3];           # master url of the spark cluster where processing will happen

sc = SparkContext(spark_url, "Harpoon")
#sc = SparkContext("local", "Harpoon")

java_import(sc._jvm, "org.apache.log4j.Logger")
java_import(sc._jvm, "org.apache.log4j.Level")
sc._jvm.Logger.getLogger("spark").setLevel(sc._jvm.Level.WARN)


wl=  0.025
ws = 0.01
lf = 400
pre = 100


def mfccRDD(wavfile, predictionLabel, sampleSize=0):
    (rate,sigf) = wav.read(wavfile)
    sig = sigf
    if sampleSize > 0:
        sig = sigf[:sampleSize]
    
    sig = sig.astype(float)
    mfcc_feat = mfcc_func(sig,rate,winlen=wl,winstep=ws,lowfreq=lf, preemph=pre)
    time = np.arange(len(mfcc_feat)).astype(float) #/ float(rate)
    
    mfccTime = []
    for i in np.arange(len(mfcc_feat)):
        mfccTime.append((time[i],mfcc_feat[i]))
    
    mfccrdd = sc.parallelize(mfccTime)

    ave = (mfccrdd
           .map(lambda (time,features): features)
           .reduce(lambda x,y: (x+y)) / float(mfccrdd.count()))
    
    mfccNorm = mfccrdd.map(lambda (time,feat): (time,feat-ave))
    mfccTimeLabeledPoint = mfccNorm.map(lambda (time,feat): (time,LabeledPoint(predictionLabel,feat)))
    return mfccTimeLabeledPoint

def getTimeFromFilename(wavfile):
    fileNoPath = wavfile.split("/")[-1:][0].split(".")[0]
    #e.g: kfm_2015-04-14_08-30-01__8kmono.wav
    
    filePart = fileNoPath.split("_")
    datePart = np.asarray(filePart[1].split("-")).astype(int)
    timePart = np.asarray(filePart[2].split("-")).astype(int)
    stDateTime = (datetime(datePart[0],datePart[1],datePart[2]
                       ,timePart[0],timePart[1],timePart[2]))
    
    return stDateTime

#filename = "/Users/wietsche/dev/audio/kfm_2015-04-14_08-30-01__8kmono.wav"
#t = getTimeFromFilename(filename)

#print t
#print t.timetuple()

#signature = "/Users/wietsche/dev/audio/kfm_8kmono.wav"
mfccJingleData = mfccRDD(signature,1,8000) 
#mfccJingleData = mfccRDD("/Users/wietsche/dev/audio/takealot.wav",1)
#mfccJingleData.take(2)


#mfcc_local = np.transpose(np.asarray(mfccJingleData.map(lambda (t,lp):lp.features).collect()))
#tr = mfcc_local
#print tr.shape


from numpy.linalg import eigh
def estimateCovariance(data):
    """Compute the covariance matrix for a given rdd.

    Note:
        The multi-dimensional covariance array should be calculated using outer products.  Don't
        forget to normalize the data by first subtracting the mean.

    Args:
        data (RDD of np.ndarray):  An `RDD` consisting of NumPy arrays.

    Returns:
        np.ndarray: A multi-dimensional array where the number of rows and columns both equal the
            length of the arrays in the input `RDD`.
    """
    sz = float(data.count())
    cormean = data.reduce(lambda x,y: x+y) / sz
    datazm = data.map(lambda x: x - cormean)
    return datazm.map(lambda x: np.outer(np.transpose(x),x)).reduce(lambda x,y: x+y)/sz

def pca(data, k=2):
    """Computes the top `k` principal components, corresponding scores, and all eigenvalues.

    Note:
        All eigenvalues should be returned in sorted order (largest to smallest). `eigh` returns
        each eigenvectors as a column.  This function should also return eigenvectors as columns.

    Args:
        data (RDD of np.ndarray): An `RDD` consisting of NumPy arrays.
        k (int): The number of principal components to return.

    Returns:
        tuple of (np.ndarray, RDD of np.ndarray, np.ndarray): A tuple of (eigenvectors, `RDD` of
            scores, eigenvalues).  Eigenvectors is a multi-dimensional array where the number of
            rows equals the length of the arrays in the input `RDD` and the number of columns equals
            `k`.  The `RDD` of scores has the same number of rows as `data` and consists of arrays
            of length `k`.  Eigenvalues is an array of length d (the number of features).
    """
   
    estCov = estimateCovariance(data)
    eVals, eVecs = eigh(estCov)
    # Return the `k` principal components, `k` scores, and all eigenvalues
    i = np.argsort(eVals[::-1])
    topK = eVecs[:,i[0:k]]
    sortedEVals = eVals[i]
    reducedData = data.map(lambda point: point.dot(topK)) 
    return (topK, reducedData, sortedEVals)

topK, mfccJingleReduced, sortedEVals = pca(mfccJingleData.map(lambda (t,p): p.features),1)

mfccJingleReduced = (mfccJingleData
                     .map(lambda (t,p): (t,p.features.dot(topK)[0]))
                     )
#signalfile = "/Users/wietsche/dev/audio/8k/kfm_2015-04-14_14-00-01.wav"

mfccSignal = mfccRDD(signalfile,0)
#kfm_2015-04-14_08-30-01__8kmono.wav



mfccSignalReduced = (mfccSignal
                     .map(lambda (t,p): (t,p.features.dot(topK)[0]))
                     )

normf = float(mfccJingleReduced.count())
xcor = (mfccSignalReduced
        .cartesian(mfccJingleReduced)
        .map(lambda (sig,jin): (sig[0] - jin[0], sig[1]*jin[1]/normf))
        .reduceByKey(lambda x,y: x+y))
#xcor.take(10)


def getMax(current,new):
    returnval = current
    if new[1] > current[1]:
        returnval = new
    return returnval
        
xcorBin = np.asarray((xcor.map(lambda (sample,val): (int(sample*ws)/60,(sample*ws/60.0,val)))
           .reduceByKey(getMax)
           .map(lambda (timebin,timeval): ((timebin,(timeval[0]-timebin)*60),timeval[1]))
           .takeOrdered(20, lambda (k,v): -v)
            ))

filetime = getTimeFromFilename(signalfile)
content = []
for hit in xcorBin:
    content.append((str(filetime),hit[0][0],hit[0][1],hit[1]))
#    if hit[1] >= threshold:
#        tokenfile = signalfile.replace(".wav",".tok")
#        os.system("touch "+tokenfile)

csvfile = signalfile.replace(".wav",".csv")
np.savetxt(csvfile, content, delimiter=",", fmt="%s") 
#print xcorBin

#locXcor = np.asarray(xcor.collect())
#print np.shape(locXcor)[0]/float(8000)
