#!/bin/bash
#run as: throw_harpoon stream.wav signature.wav
STREAM=$1
SIG=$2
RUN="ssh -i wietsche.pem root@$PEQUOD_PUBLIC_IP spark/bin/spark-submit  --master $PEQUOD_SPARK_URL  harpoon.py   $STREAM $SIG $PEQUOD_SPARK_URL"
echo $RUN
$RUN
