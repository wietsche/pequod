#!/bin/bash
: "${CODE?Need to set CODE (Options: 5fm,kfm)}"

#hardcoding to one minute

#export  DUR="00:"$RECMIN":15"
export  DUR="00:00:57"
#export  SLP=$RECMIN"m"
export  SLP=55

export  OUTLOC=/recording
export  FILEPRE=$CODE"_"
export  OCEAN=$TGTFS/$CODE

if [ "$CODE" = "5fm" ]; then 
    export STREAM=$STREAM_5FM 
fi

if [ "$CODE" = "kfm" ]; then 
    export STREAM=$STREAM_KFM 
fi

/scripts/record.sh &
sleep $SLP
/scripts/overlap_record.sh

