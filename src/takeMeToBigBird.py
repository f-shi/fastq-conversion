import os
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

autoPath = "/home/mecore/Desktop/timp/src/fastq-automation/"
keepPath = "/mnt/heisenberg/"
archivePath = "/mnt/heisenberg/ARCHIVE/"
bigBirdPath = "/mnt/bigbird/"


def directoryCheck ( myRun ):
	pth = myRun["Path"]

	folderFiles = [ f.name for f in os.scandir(pth) if f.is_file() ]
	
	#print("I'm checking %s" % pth)
	
	directoryCopyBool = "CopyComplete.txt" in folderFiles
	directoryRunBool = "RunInfo.xml" in folderFiles and "SampleSheet.csv" in folderFiles and "bcl2fastqCheck.txt" not in folderFiles
	directoryFailBool = "lastCheckFailed.txt" not in folderFiles
	directoryTimeBool = True
	directoryBool = directoryCopyBool and directoryRunBool and directoryFailBool
	
	
	if directoryBool:
		lastModified = datetime.utcfromtimestamp(max(os.path.getmtime(root) for root,_,_ in os.walk(pth))) - timedelta(hours = 4)
		nowTime = datetime.now()
		timeDiff = nowTime - lastModified
		
		if timeDiff.total_seconds()/60.0 < 30:
			directoryBool = False
			directoryTimeBool = False
	
	
	if directoryBool:
		takeMeToBigBirdLogger(0, "Checked %s: can be run!" % pth, 1)
	elif not directoryFailBool:
		takeMeToBigBirdLogger(0, "Checked %s: A previous run with this folder failed. Please see lastCheckFailed.txt for more details." % pth, 1)
		return directoryBool
	elif not directoryTimeBool:
		takeMeToBigBirdLogger(0, "Checked %s: Modified %s minutes ago so may still be uploading" %(pth, str(round(timeDiff.total_seconds()/60.0))), 1)
	elif not directoryRunBool:
		if "bcl2fastqCheck.txt" in folderFiles:
			takeMeToBigBirdLogger(0, "Checked %s: bcl2fastqCheck file is present!" % pth, 1)
		else:
			textName = os.path.join(myRun["Path"], "lastCheckFailed.txt")
			if "RunInfo.xml" not in folderFiles:
				takeMeToBigBirdLogger(0, "Checked %s: no RunInfo.xml" % pth, 1)
				
				with open(textName, "a+") as textFile:
					textFile.write("NO RUNINFO.XML")
				
			
			elif "SampleSheet.csv" not in folderFiles:
				takeMeToBigBirdLogger(0, "Checked %s: missing necessary files for run" % pth, 1)
				
				with open(textName, "a+") as textFile:
					textFile.write("NO SAMPLESHEET.CSV")
	else:
		takeMeToBigBirdLogger(0, "Checked %s: won't run because of CopyComplete.txt is not present!" % pth, 1)
	

	return directoryBool


def takeMeToBigBirdLogger( num2, massagers, num1 ):

	nowTime = datetime.now()
	date_time = nowTime.strftime("%m/%d/%Y, %H:%M:%S>> ")

	logLine = date_time + massagers
	for i in range(num1):
		logLine = logLine + "\n"
		
	for i in range(num2):
		logLine = "\n" + logLine
	
	with open(keepPath + "takeMeToBigBirdLog.txt", "a+") as text_file:
		text_file.write(logLine)
	
	return


def main():
	
	#print("ok running")
	takeMeToBigBirdLogger(1, "I will take you to Big Bird!", 2)
	waitTime = 900
	n = 0
	
	while True:
		
		n+=1
		
		ngsRawFolders = [ f.path for f in os.scandir(keepPath) if f.is_dir() ]
		takeMeToBigBirdLogger(1, "I'm beginning to scan for new folders. Number of times I've checked this directory: %i" % n, 1)	
		
		for dirName in ngsRawFolders:
			
			subjectRun = {"Path": dirName, "folderName": "", "runName": "", "runInstrument":"", "FlowcellID":"", "outputFolderLocation":"", "outputErrors":[]}
			slashIndex = [i for i, char in enumerate(dirName) if char == "/"]
			subjectRun["folderName"] = dirName[slashIndex[-1]+1:]
			
			if dirName == os.path.join(keepPath, "ARCHIVE"):
				continue
			elif dirName == os.path.join(keepPath, "COVID"):
				continue
			elif directoryCheck(subjectRun):
			
				successOrNot = BR.bcl2fastqRun(subjectRun)
				
				if successOrNot == 0:
					takeMeToBigBirdLogger(0, "THE RUN FINISHED SUCCESSFULLY", 1)
		
					try:
						BR.fastQCRunner( subjectRun )
					except:
						takeMeToBigBirdLogger(0, "fastQCRunner failed", 2)
					
					try:
						takeMeToBigBirdLogger(0, "Generating Interop images...", 1)
						IG.interopGenerator(subjectRun)
					except Exception as e:
						takeMeToBigBirdLogger(0, "interopGenerator failed: %s" % str(e), 2)
					else:
						takeMeToBigBirdLogger(0, "interopGenerator succeeded", 2)
					
					try:
						takeMeToBigBirdLogger(0, "Drafting email...", 1)
						EM.emailSendingWrapper(subjectRun)
					except Exception as e:
						takeMeToBigBirdLogger(0, "emailSender failed: %s" % str(e), 2)
					else:
						takeMeToBigBirdLogger(0, "emailSender succeeded succeeded", 2)
					
					try:
						BR.directoryMover(subjectRun)
					except Exception as e:
						takeMeToBigBirdLogger(0, "directoryMover failed: %s" % str(e), 2)
					
				else:
					takeMeToBigBirdLogger(0, "THE RUN FAILED!", 2)
		
		noTime = datetime.now()
		nextTime = noTime + timedelta(seconds = waitTime)
		sleepMessage = "I'm going to take a nap now...\n                       I will begin scanning again at %s" % nextTime.strftime("%m/%d/%Y, %H:%M:%S")
		takeMeToBigBirdLogger(0, sleepMessage, 2)
		time.sleep(waitTime)
	
	return
	

main()



