import os
import sys
import time
import csv
import shutil
import subprocess
import random
import errno
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date
import emailSender.emailSender as EM
import interopGenerator.interopGenerator as IG
import bcl2fastqRunner.bcl2fastqRunner as BR
from bs4 import BeautifulSoup

autoPath = "/home/mecore/Desktop/timp/src/fastq-automation/"
keepPath = "/mnt/heisenberg/"
archivePath = "/mnt/heisenberg/ARCHIVE/"
bigBirdPath = "/mnt/bigbird/"

def bcl2fastqWrapper( subjectRun ):

	 
	successOrNot = BR.bcl2fastqRun(subjectRun)
					
	if successOrNot == 0:
		BR.takeMeToBigBirdLogger(0, "THE RUN FINISHED SUCCESSFULLY", 1)
		
		try:
			BR.dashboardUpdater('currently_running', 'Running FASTQC...', subjectRun) 
			BR.fastQCRunner( subjectRun )
		except Exception as e:
			BR.takeMeToBigBirdLogger(0, "fastQCRunner failed: %s" % str(e), 2)
			EM.errorSender("fastQCRunner failed: %s" % str(e), subjectRun)
							
		try:
			BR.dashboardUpdater('currently_running', 'Generating Interop images...', subjectRun) 
			BR.takeMeToBigBirdLogger(0, "Generating Interop images...", 1)
			IG.interopGenerator(subjectRun)
		except Exception as e:
			BR.takeMeToBigBirdLogger(0, "interopGenerator failed: %s" % str(e), 2)
			EM.errorSender("interopGenerator failed: %s" % str(e), subjectRun)
		else:
			BR.takeMeToBigBirdLogger(0, "interopGenerator succeeded", 2)
							
		try:
			BR.dashboardUpdater('currently_running', 'Moving FASTQ files to ARCHIVE on Heisenberg...', subjectRun) 
			BR.archiveMover(subjectRun)
		except Exception as e:
			BR.takeMeToBigBirdLogger(0, "Moving to archive failed: %s" % str(e), 2)
			EM.errorSender("archiveMover failed: %s" % str(e), subjectRun)
				
		try:
			BR.dashboardUpdater('currently_running', 'Drafting email...', subjectRun)
			BR.takeMeToBigBirdLogger(0, "Drafting email...", 1)
			EM.emailSendingWrapper(subjectRun)
		except Exception as e:
			BR.takeMeToBigBirdLogger(0, "emailSender failed: %s" % str(e), 2)
			EM.errorSender("Could not send email: %s" % str(e), subjectRun)
		else:
			BR.takeMeToBigBirdLogger(0, "emailSender succeeded", 2)
							
		try:
			BR.dashboardUpdater('currently_running', 'Copying folder to Big Bird...', subjectRun)
			BR.bigBirdMover(subjectRun)
		except Exception as e:
			BR.takeMeToBigBirdLogger(0, "directoryMover failed: %s" % str(e), 2)
			EM.errorSender("directoryMover failed: %s" % str(e), subjectRun)			
	else:
		BR.takeMeToBigBirdLogger(0, "THE RUN FAILED!", 2)

	return successOrNot
			
def directoryCheck ( myRun ):
	pth = myRun["Path"]

	folderFiles = [ f.name for f in os.scandir(pth) if f.is_file() ]
	
	#print("I'm checking %s" % pth)
	
	directoryCopyBool = "CopyComplete.txt" in folderFiles or "RTAComplete.txt" in folderFiles
	directoryRunBool = "RunInfo.xml" in folderFiles and "SampleSheet.csv" in folderFiles and "bcl2fastqCheck.txt" not in folderFiles
	directoryFailBool = "lastCheckFailed.txt" not in folderFiles
	directoryTimeBool = True
	directoryBool = directoryCopyBool and directoryRunBool
	
	
	if directoryBool:
		lastModified = datetime.utcfromtimestamp(max(os.path.getmtime(root) for root,_,_ in os.walk(pth))) - timedelta(hours = 4)
		nowTime = datetime.now()
		timeDiff = nowTime - lastModified
		
		if timeDiff.total_seconds()/60.0 < 0.0:
			directoryBool = False
			directoryTimeBool = False
	
	#textName = os.path.join(pth, "lastCheckFailed.txt")
	
	if directoryBool:
		BR.takeMeToBigBirdLogger(0, "Checked %s: can be run!" % pth, 1)
	elif not directoryCopyBool:
		BR.takeMeToBigBirdLogger(0, "Checked %s: CopyComplete.txt not present yet." % pth, 1)
		BR.dashboardUpdater('run_checks', 'Still being uploaded by sequencer.', myRun)
		return directoryBool

	elif not directoryTimeBool:
		BR.takeMeToBigBirdLogger(0, "Checked %s: Modified %s minutes ago so may still be uploading" %(pth, str(round(timeDiff.total_seconds()/60.0))), 1)
		BR.dashboardUpdater('run_checks', 'Folder was modified %s minutes ago. May still be uploading' % str(round(timeDiff.total_seconds()/60.0)), myRun)
		return directoryBool
	elif not directoryRunBool:
		#takeMeToBigBirdLogger(0, "Checked %s: Missing a necessary file!" % pth, 1)
		if "bcl2fastqCheck.txt" in folderFiles:
			BR.takeMeToBigBirdLogger(0, "Checked %s: bcl2fastqCheck file is present!" % pth, 1)
			BR.dashboardUpdater('run_checks', 'Previous run on this folder failed. Please troubleshoot.', myRun)
			return directoryBool
		
		else:
			textName = os.path.join(myRun["Path"], "lastCheckFailed.txt")
			if "RunInfo.xml" not in folderFiles:
				BR.takeMeToBigBirdLogger(0, "Checked %s: no RunInfo.xml" % pth, 1)
				BR.dashboardUpdater('run_checks', 'This folder is missing RunInfo.xml. Cannot be run.', myRun)
				
				if directoryFailBool:
					EM.errorSender("Checked %s: no RunInfo.xml" % pth, {"runName":pth})

					with open(textName, "a+") as textFile:
						textFile.write("NO RUNINFO.XML")
				
			
			elif "SampleSheet.csv" not in folderFiles:
				BR.takeMeToBigBirdLogger(0, "Checked %s: No sample sheet" % pth, 1)
				BR.dashboardUpdater('run_checks', 'This folder is missing RunInfo.xml. Cannot be run.', myRun)
				
				if directoryFailBool:
					EM.errorSender("Checked %s: no sampleSheet.csv" % pth, {"runName":pth})
					
					with open(textName, "a+") as textFile:
						textFile.write("NO SAMPLESHEET.CSV")
		
		
		#return directoryBool
	else:
		BR.takeMeToBigBirdLogger(0, "Checked %s: a mysterious issue has arisen." % pth, 1)
	

	return directoryBool


def takeMeToBigBirdLogger( num2, massagers, num1 ):

	nowTime = datetime.now()
	date_time = nowTime.strftime("%m/%d/%Y, %H:%M:%S>> ")

	logLine = date_time + massagers
	for i in range(num1):
		logLine = logLine + "\n"
		
	for i in range(num2):
		logLine = "\n" + logLine
	
	with open(os.path.join(archivePath, "takeMeToBigBird_logs", "takeMeToBigBirdLog.txt"), "a+") as text_file:
		text_file.write(logLine)
	
	return


def main():
	
	
	if len(sys.argv) == 3 and sys.argv[1] == 'force':
		
		dirName = os.path.join(keepPath, sys.argv[2])
		
		subjectRun = {"Path": dirName, "folderName": sys.argv[2], "runName": "", "runInstrument":"", "FlowcellID":"", "outputFolderLocation":"", "outputErrors":[], "libraryType":"UNKNOWN"}
		
		BR.takeMeToBigBirdLogger(2, "Running folder %s by force." % sys.argv[2], 1)
		
		try:
			bcl2fastqWrapper(subjectRun)
		except Exception as e:
			BR.takeMeToBigBirdLogger(1, "Failed to run folder %s: %s" % (sys.argv[2], e), 1)
		
		return
		
	elif len(sys.argv) == 1:
		#print("ok running")
		BR.takeMeToBigBirdLogger(1, "I will take you to Big Bird!", 2)
		EM.errorSender("takeMeToBigBird has restarted!",{"runName":"N/A"})
		waitTime = 900
		n = 0
		
		while True:
			
			n+=1
			
			ngsRawFolders = [ f.path for f in os.scandir(keepPath) if f.is_dir() ]
			BR.dashboardUpdater('run_clear', '', '')
			BR.dashboardUpdater('currently_running', 'Checking folders to determine if they are ready to be converted.', {"runName": ""})
			BR.takeMeToBigBirdLogger(1, "I'm beginning to scan for new folders. Number of times I've checked this directory: %i" % n, 1)	
			
			for dirName in ngsRawFolders:
				
				subjectRun = {"Path": dirName, "folderName": "", "runName": "", "runInstrument":"", "FlowcellID":"", "outputFolderLocation":"", "outputErrors":[], "libraryType":"UNKNOWN"}
				slashIndex = [i for i, char in enumerate(dirName) if char == "/"]
				subjectRun["folderName"] = dirName[slashIndex[-1]+1:]
				
				if dirName == os.path.join(keepPath, "ARCHIVE"):
					continue
				elif dirName == os.path.join(keepPath, "COVID"):
					continue
				elif dirName == os.path.join(keepPath, "MyRun"):
					shutil.rmtree(dirName)
					continue
				elif directoryCheck(subjectRun):
					bcl2fastqWrapper(subjectRun)
			
			noTime = datetime.now()
			nextTime = noTime + timedelta(seconds = waitTime)
			nextTime = nextTime.strftime("%m/%d/%Y, %H:%M:%S")
			sleepMessage = "I'm going to take a nap now...\n                       I will begin scanning again at %s" % nextTime
			BR.takeMeToBigBirdLogger(0, sleepMessage, 2)
			BR.dashboardUpdater('currently_waiting', 'Waiting...', {"runName": nextTime}) 
			time.sleep(waitTime)
	
	return
	

main()



