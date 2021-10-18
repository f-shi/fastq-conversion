#!/bin/bash

LOGNAME="takeMeToBigBirdLog_$(date +"%Y_%m_%d_%I_%M_%p").txt"

mv /mnt/heisenberg/ARCHIVE/takeMeToBigBird_logs/takeMeToBigBirdLog.txt  /mnt/heisenberg/ARCHIVE/takeMeToBigBird_logs/$LOGNAME
echo $(date +"%Y_%m_%d_%I_%M_%p") >> /mnt/heisenberg/ARCHIVE/takeMeToBigBird_logs/takeMeToBigBirdLog.txt
mv /mnt/heisenberg/ARCHIVE/takeMeToBigBird_logs/$LOGNAME /mnt/heisenberg/ARCHIVE/takeMeToBigBird_logs/log_archive/

