#!/bin/bash
export TIMESTAMP=`date +"%Y-%m-%d_%H-%M-%S"`
export OUTFILE=$OUTLOC/$FILEPRE$TIMESTAMP".wav"
mplayer $STREAM -endpos $DUR -srate $FS -format s16le -af pan=1:0.5:0.5 -vo null -ao pcm:waveheader:file=$OUTFILE
aws s3 mv $OUTFILE $OCEAN/

