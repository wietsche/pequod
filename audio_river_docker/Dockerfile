FROM wietsche/audio_river_base

ENV AWS_ACCESS_KEY_ID       AKIAIX5Z7D5FJARYWZSQ
ENV AWS_SECRET_ACCESS_KEY   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
ENV AWS_DEFAULT_REGION      us-west-2 
ENV TGTFS                   s3://za.audio 

#default recording length in minutes
ENV RECMIN          0.9

#sample rate
#ENV  FS             8000
ENV  FS             16000

ENV STREAM_5FM      rtmp://216.246.37.52/5fm/5fm.stream
ENV STREAM_KFM      rtmp://196.33.130.81:1935/kfm_64k/kfm_64k-mobileapp-rtmp.stream

RUN mkdir /scripts

COPY scripts/record.sh /scripts/ 
RUN chmod a+x /scripts/record.sh

COPY scripts/overlap_record.sh /scripts/
RUN chmod a+x /scripts/overlap_record.sh

ENTRYPOINT /scripts/overlap_record.sh

