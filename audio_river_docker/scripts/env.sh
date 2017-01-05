#!/bin/bash
#$CODE specified at runtime...

export  DUR="00:10:15"
export  SLP=10m

export  STREAM_5FM="rtmp://216.246.37.52/5fm/5fm.stream"
export  STREAM_KFM="rtmp://196.33.130.81:1935/kfm_64k/kfm_64k-mobileapp-rtmp.stream" 

export  OUTLOC=/recording
export  FILEPRE=$CODE"_"
export  FS=8000

export  AWS_ACCESS_KEY_ID=AKIAIX5Z7D5FJARYWZSQ
export  AWS_SECRET_ACCESS_KEY=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
export  AWS_DEFAULT_REGION=us-west-2 
export  OCEAN=s3://za.audio/$CODE

if [ "$CODE" = "5fm" ]; then 
    export STREAM=$STREAM_5FM 
fi

if [ "$CODE" = "kfm" ]; then 
    export STREAM=$STREAM_KFM 
fi
