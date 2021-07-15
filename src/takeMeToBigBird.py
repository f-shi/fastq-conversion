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

autoPath = "/home/mecore/Desktop/timp/src/fastq-automation/"
keepPath = "/run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/"
bigBirdPath = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/"

#subprocess.run(["gio", "mount", "smb://heisenberg.local/ngs_raw/"])
#subprocess.run(["gio", "mount", "smb://bigbird.ibb.gatech.edu/ngs/", "<", "~/.servercreds"])

def bcl2fastqRun ( myRun ):
	
	myRun = textCheckGenerator(myRun)
	
	bcl2fastqCheck = open(os.path.join(myRun["Path"], "bcl2fastqCheck.txt"), 'a+')
	
	myRun = sampleSheetReader(myRun)
	myRun = runInfoReader(myRun)
	
	archiveFolderPath = os.path.join(keepPath,"ARCHIVE", "Fangs_Special_Test_Folder", myRun["runInstrument"], myRun["runName"])
	
	try:
    		os.mkdir(archiveFolderPath)
	except OSError as exc:
    		if exc.errno != errno.EEXIST:
        		raise
    		pass
	
	#takeMeToBigBirdLogger(0, "Making a copy of %s" % myRun["Path"], 1)
	
	#shutil.copytree(myRun["Path"], os.path.join(keepPath, "ARCHIVE", myRun["runInstrument"], myRun[""""))
	subprocess.run(["cp", "-r","-v", myRun["Path"], archiveFolderPath], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)

	myRun["outputFolderLocation"] = os.path.join(myRun["Path"],"MEC_FASTQ_Files_" + myRun["runName"], "")
	
	try:
    		os.mkdir(myRun["outputFolderLocation"])
	except OSError as exc:
    		if exc.errno != errno.EEXIST:
        		raise
    		pass
	
	takeMeToBigBirdLogger(1, "STARTING BCL2FASTQ RUN on %s" % myRun["Path"], 1)
	
	successOrNot = subprocess.run(["bcl2fastq", "--ignore-missing-bcls", "--ignore-missing-filter", "--ignore-missing-positions", "--ignore-missing-controls", "--find-adapters-with-sliding-window", "--adapter-stringency", "0.9", "--mask-short-adapter-reads", "35", "--minimum-trimmed-read-length", "35", "-R", myRun["Path"], "-o", myRun["outputFolderLocation"]], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	if successOrNot.returncode != 0:
		takeMeToBigBirdLogger(1, "RUN FAILED, RUNNING AGAIN WITH FEWER ALLOWED MISMATCHES", 1)
		successOrNot = subprocess.run(["bcl2fastq", "-R", myRun["Path"],  "--ignore-missing-bcls", "--ignore-missing-filter", "--ignore-missing-positions", "--ignore-missing-controls", "--find-adapters-with-sliding-window", "--adapter-stringency", "0.9", "--mask-short-adapter-reads", "35", "--minimum-trimmed-read-length", "35", "--barcode-mismatches", "0", "-o", myRun["outputFolderLocation"]], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	bcl2fastqCheck.close()

	if successOrNot.returncode == 0:
		takeMeToBigBirdLogger(0, "THE RUN FINISHED SUCCESSFULLY", 1)
		
		try:
			fastQCRunner( myRun )
		except:
			takeMeToBigBirdLogger(0, "fastQCRunner failed", 2)
		
		try:
			IG.interopGenerator(myRun)
		except:
			takeMeToBigBirdLogger(0, "interopGenerator failed", 2)
		
		try:
			directoryMover(myRun)
		except:
			takeMeToBigBirdLogger(0, "directoryMover failed", 2)
		
		try:
			EM.emailSendingWrapper(myRun)
		except:
			takeMeToBigBirdLogger(0, "EmailSender failed", 2)
		
	else:
		takeMeToBigBirdLogger(0, "THE RUN FAILED!", 2)
	
	return

def directoryCheck ( myRun ):
	pth = myRun["Path"]

	folderFiles = [ f.name for f in os.scandir(pth) if f.is_file() ]
	
	#print("I'm checking %s" % pth)
	
	lastModified = datetime.utcfromtimestamp(max(os.path.getmtime(root) for root,_,_ in os.walk(pth))) - timedelta(hours = 4)
	nowTime = datetime.now()
	timeDiff = nowTime - lastModified
	
	

	directoryCopyBool = timeDiff.total_seconds()/60.0 >= 3 and "CopyComplete.txt" in folderFiles
	directoryRunBool = "RunInfo.xml" in folderFiles and "SampleSheet.csv" in folderFiles and "bcl2fastqCheck.txt" not in folderFiles
	directoryFailBool = "lastCheckFailed.txt" not in folderFiles
	directoryBool = directoryCopyBool and directoryRunBool and directoryFailBool
	
	
	if directoryBool:
		takeMeToBigBirdLogger(0, "Checked %s: can be run!" % pth, 1)
	elif not directoryFailBool:
		takeMeToBigBirdLogger(0, "Checked %s: A previous run with this folder failed. Please see lastCheckFailed.txt for more details." % pth, 1)
		return directoryBool
	elif timeDiff.total_seconds()/15.0 < 3:
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

def directoryMover ( myRun ):
	
	takeMeToBigBirdLogger(1, "The directory is being taken to Big Bird", 1)
	
	#p1 is run folder path
	#p2 is run name
	p2 = os.path.join(bigBirdPath,myRun["runInstrument"],myRun["runName"], "")
	p1 = myRun["Path"]
	p3 = myRun["outputFolderLocation"]

	if not os.path.isdir(p2):
		os.mkdir(p2)
	
	#print(p2)
	
	moveCheck2 = subprocess.run(["scp", "-r","-v", myRun["outputFolderLocation"], p2])
	if moveCheck2 == 0:
		try:
			shutil.rmtree(myRun["outputFolderLocation"])
		except:
			pass
	
	moveCheck1 = subprocess.run(["scp", "-r","-v", myRun["Path"], p2])

	moveCheck = moveCheck1.returncode == 0 and moveCheck2.returncode == 0
	
		
	if moveCheck:
		
		myRun["Path"] = os.path.join(p2, myRun["folderName"], "")
		myRun["outputFolderLocation"] = os.path.join(p2, "MEC_FASTQ_Generation_" + myRun["runName"], "")
		oldFolder = os.path.join(myRun["Path"], "MEC_FASTQ_Generation_" + myRun["runName"], "")
		takeMeToBigBirdLogger(0, "The directory should be in Big Bird at %s" % myRun["Path"], 2)
		
		shutil.rmtree(p1)
		shutil.rmtree(p3)
	
	else:
		takeMeToBigBirdLogger(0, "There was an issue moving the directory to Big Bird.", 2)
	
	return myRun

def fastQCRunner ( myRun ):

	bcl2fastqCheck = open(os.path.join(myRun["Path"], "bcl2fastqCheck.txt"), 'a+')

	takeMeToBigBirdLogger(1, "Running FastQC and multiQC...", 1)
	subprocess.run(["/bin/bash", "/home/mecore/Desktop/timp/fastq-automation/src/fastQCRunner.sh", myRun["outputFolderLocation"], myRun["runName"]], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	takeMeToBigBirdLogger(0, "FastQC and multiQC done!", 1)
	
	return

def runInfoReader ( myRun ):

	#print("I'm reading %s" % pth)
	
	runInstrument = ""

	runInfoTree = ET.parse(os.path.join(myRun["Path"], "RunInfo.xml"))
	runInfoRoot = runInfoTree.getroot()
	instrumentIdent = runInfoRoot[0][1].text.strip()
	myRun["FlowcellID"] = runInfoRoot[0][0].text.strip()
	
	if instrumentIdent == "MN00206":
		myRun["runInstrument"] = "MiniSeq"
	elif instrumentIdent == "NB501662":
		myRun["runInstrument"] = "NextSeq"
	elif instrumentIdent == "A01113":
		myRun["runInstrument"] = "NovaSeq"

	takeMeToBigBirdLogger(0,"It was performed by the %s" % myRun["runInstrument"], 1)

	#print ("This is run on %s" % runInstrument);
	return myRun

def sampleSheetReader ( myRun ):

	sampleSheetPath = os.path.join(myRun["Path"], "SampleSheet.csv")
	
	sampleSheetArray = []
	
	with open(sampleSheetPath, newline='') as csvFile:
		spamreader = csv.reader(csvFile, delimiter=',', quotechar='|')
		for row in spamreader:
			sampleSheetArray.append(row)
	
	secondRow = sampleSheetArray[2]
	runName = secondRow[1]
	runName = runName.strip()
	
	myRun["runName"] = runName
	
	takeMeToBigBirdLogger(1, "The run I'm copying into the archive is called %s" % runName, 1)
	return myRun


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

def textCheckGenerator ( myRun ):
	
	pth = myRun["Path"]
	textName = os.path.join(pth, "bcl2fastqCheck.txt")
	"""
	slashIndex = [i for i, char in enumerate(pth) if char == "/"]
	weirdID = pth[slashIndex[-1]+1:]
	myRun["folderName"] = weirdID
	"""
	
	weirdID = myRun["folderName"]
	
	with open(textName, "a+") as textFile:
		textFile.write(weirdID + "\n")
		
	return myRun


def main():
	
	#print("ok running")
	takeMeToBigBirdLogger(1, "I will take you to Big Bird!", 2)
	waitTime = 5400
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
			
				bcl2fastqRun(subjectRun)
		
		noTime = datetime.now()
		nextTime = noTime + timedelta(seconds = waitTime)
		sleepMessage = "I'm going to take a nap now...\n                       I will begin scanning again at %s" % nextTime.strftime("%m/%d/%Y, %H:%M:%S")
		takeMeToBigBirdLogger(0, sleepMessage, 2)
		time.sleep(waitTime)
	
	return
	

main()



