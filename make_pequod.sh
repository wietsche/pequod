#!/bin/bash
spark-ec2 -k wietsche -i wietsche.pem --region=us-west-2  -s 1  --copy-aws-credentials  --user-data=bootstrap_pequod.sh launch pequod
