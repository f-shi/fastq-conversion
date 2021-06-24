#!/bin/bash

LOGNAME="takeMeToBigBirdLog_$(date +"%Y_%m_%d_%I_%M_%p").txt"

mv /run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/takeMeToBigBirdLog.txt /run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/$LOGNAME
echo $(date +"%Y_%m_%d_%I_%M_%p") >> /run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/takeMeToBigBirdLog.txt
mv /run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/$LOGNAME /run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/ARCHIVE/log_archive/

