import os
import time
import csv
import shutil
import subprocess
import random
import errno
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date


autoPath = "/home/mecore/Desktop/timp/src/fastq-automation/"
keepPath = "/mnt/heisenberg/"
archivePath = "/mnt/heisenberg/ARCHIVE/Fangs_Special_Test_Folder/"
bigBirdPath = "/mnt/bigbird/"

def bcl2fastqRun ( myRun ):
	
	myRun = textCheckGenerator(myRun)
	
	myRun = sampleSheetReader(myRun)
	myRun = runInfoReader(myRun)
	
	archiveFolderPath = os.path.join(archivePath, myRun["runInstrument"], myRun["runName"])
	
	try:
    		os.mkdir(archiveFolderPath)
	except OSError as exc:
    		if exc.errno != errno.EEXIST:
        		raise
    		pass
	
	#takeMeToBigBirdLogger(0, "Making a copy of %s" % myRun["Path"], 1)
	
	#shutil.copytree(myRun["Path"], os.path.join(keepPath, "ARCHIVE", myRun["runInstrument"], myRun[""""))
	subprocess.run(["cp", "-r","-v", myRun["Path"], archiveFolderPath])

	myRun["outputFolderLocation"] = os.path.join(myRun["Path"],"FASTQ_Files_" + myRun["runName"], "")
	
	try:
    		os.mkdir(myRun["outputFolderLocation"])
	except OSError as exc:
    		if exc.errno != errno.EEXIST:
        		raise
    		pass
	
	bcl2fastqCheck = open(os.path.join(myRun["Path"], "bcl2fastqCheck.txt"), 'a+')
	takeMeToBigBirdLogger(1, "STARTING BCL2FASTQ RUN on %s" % myRun["Path"], 1)
	
	successOrNot = subprocess.run(["bcl2fastq", "--ignore-missing-bcls", "--ignore-missing-filter", "--ignore-missing-positions", "--ignore-missing-controls", "--find-adapters-with-sliding-window", "--adapter-stringency", "0.9", "--mask-short-adapter-reads", "35", "--minimum-trimmed-read-length", "35", "-R", myRun["Path"], "-o", myRun["outputFolderLocation"]], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	if successOrNot.returncode != 0:
		takeMeToBigBirdLogger(1, "RUN FAILED, RUNNING AGAIN WITH FEWER ALLOWED MISMATCHES", 1)
		successOrNot = subprocess.run(["bcl2fastq", "-R", myRun["Path"],  "--ignore-missing-bcls", "--ignore-missing-filter", "--ignore-missing-positions", "--ignore-missing-controls", "--find-adapters-with-sliding-window", "--adapter-stringency", "0.9", "--mask-short-adapter-reads", "35", "--minimum-trimmed-read-length", "35", "--barcode-mismatches", "0", "-o", myRun["outputFolderLocation"]], stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	bcl2fastqCheck.close()
	
	return successOrNot.returncode
	
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
	
	moveCheck2 = subprocess.run(["scp", "-r", myRun["outputFolderLocation"], p2])
	moveCheck3 = subprocess.run(["scp", "-r", myRun["outputFolderLocation"], os.path.join(keepPath,"ARCHIVE", "Fangs_Special_Test_Folder", myRun["runInstrument"], myRun["runName"])])
	moveCheck4 = subprocess.run(["scp", "-r", os.path.join(myRun["Path"], "Interop"), os.path.join(keepPath,"ARCHIVE", "Fangs_Special_Test_Folder", myRun["runInstrument"], myRun["runName"])])
	
	try:
		archivePath = os.path.join(keepPath,"ARCHIVE", "Fangs_Special_Test_Folder", myRun["runInstrument"], myRun["runName"], "")
		os.rename(os.path.join(archivePath, "Interop", ""), os.path.join(archivePath, "Interop_" + myRun["runName"], ""))
		subprocess.run(["scp", "-r", os.path.join(archivePath, "Interop_"+myRun["runName"], ""), p2])
	except:
		pass
	
	if moveCheck2.returncode == 0:
		try:
			shutil.rmtree(myRun["outputFolderLocation"])
		except:
			pass
	
	moveCheck1 = subprocess.run(["scp", "-r","-v", myRun["Path"], p2])

	moveCheck = moveCheck1.returncode == 0 and moveCheck2.returncode == 0
	
		
	if moveCheck:
		
		myRun["Path"] = os.path.join(p2, myRun["folderName"], "")
		myRun["outputFolderLocation"] = os.path.join(p2, "FASTQ_Files_" + myRun["runName"], "")
		oldFolder = os.path.join(myRun["Path"], "FASTQ_Files_" + myRun["runName"], "")
		takeMeToBigBirdLogger(0, "The directory should be in Big Bird at %s" % myRun["Path"], 2)
		
		shutil.rmtree(p1)
	
	else:
		takeMeToBigBirdLogger(0, "There was an issue moving the directory to Big Bird.", 2)
	
	return myRun

def fastQCRunner ( myRun ):

	bcl2fastqCheck = open(os.path.join(myRun["Path"], "bcl2fastqCheck.txt"), 'a+')

	takeMeToBigBirdLogger(1, "Running FastQC and multiQC...", 1)
	
	#keepPath = "/mnt/heisenberg/ARCHIVE/Fangs_Special_Test_Folder/fastqc_tests/MW59_basespace_unpacked/"
	Results = os.path.join(myRun["outputFolderLocation"], "FASTQC_Results")

	try:
		os.mkdir(Results)
	except:
		pass
	
	numbEr = 16

	allFastqFiles = [ f.path for f in os.scandir(myRun["outputFolderLocation"]) if not f.is_dir() ]
	littleContainer = []
	bigContainer = []

	for index, fastqPath in enumerate(allFastqFiles):
	
		littleContainer.append(fastqPath)
	
		if index % numbEr == numbEr - 1:
			bigContainer.append(littleContainer)
			littleContainer = []
		
	
	if littleContainer:
		bigContainer.append(littleContainer)
		
	for index, fastqFiles in enumerate(bigContainer):
		
		command = ["fastqc", "-q", "--threads", str(numbEr + 8), "--outdir", Results]
		commands = command + fastqFiles
		
		subprocess.run(commands, stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	multiqcCommands = ["/home/mecore/.local/bin/multiqc", Results, "-o", os.path.join(myRun["outputFolderLocation"], "MultiQC_results")]
	subprocess.run(multiqcCommands, stdout=bcl2fastqCheck, stderr=subprocess.STDOUT)
	
	bcl2fastqCheck.close()
	takeMeToBigBirdLogger(0, "FastQC and multiQC done!", 2)
	
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
	elif instrumentIdent == "M01562":
		myRun["runInstrument"] = "MiSeq"
	else:
		myRun["runInstrument"] = "UNKNOWN"

	takeMeToBigBirdLogger(0,"It was performed by the %s" % myRun["runInstrument"], 1)

	#print ("This is run on %s" % runInstrument);
	return myRun

def sampleSheetReader ( myRun ):

	sampleSheetPath = os.path.join(myRun["Path"], "SampleSheet.csv")
	
	sampleSheetArray = []
	sampleStart = 0
	
	with open(sampleSheetPath, newline='') as csvFile:
		spamreader = csv.reader(csvFile, delimiter=',', quotechar='|')
		for index, row in enumerate(spamreader):

			if row:
				if row[0] == '[Data]':
					sampleStart = index + 1
		
			sampleSheetArray.append(row)
	
	try:
		tenXIndexCheck(sampleSheetArray, sampleSheetPath, sampleStart)
	except Exception as e:
		print(e)
	
	
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

def tenXIndexCheck (sampleSheetArray, sampleSheetPath, sampleStart):

	with open('10x_indices.json', 'r', encoding='utf-8') as f:
    		dict_of_indices = json.load(f)

	I7_Index_ID = sampleSheetArray[sampleStart].index('I7_Index_ID')
	I5_Index_ID = sampleSheetArray[sampleStart].index('I5_Index_ID')
	index2 = sampleSheetArray[sampleStart].index('index2')
	

	#print(sampleSheetArray)

	with open('10x_indices.json', 'r', encoding='utf-8') as f:
    		dict_of_indices = json.load(f)

	tenx_test = sampleSheetArray[sampleStart + 1]
	
	if dict_of_indices[tenx_test[I7_Index_ID]]:
		takeMeToBigBirdLogger(0, 'I think this maybe a 10x run. Generating workflow_b indices for sample sheet.', 1)

	for ooh in range(sampleStart + 1, len(sampleSheetArray)):
		gash = sampleSheetArray[ooh]
	

		if dict_of_indices[gash[I7_Index_ID]]:
			sampleSheetArray[ooh][I5_Index_ID] = dict_of_indices[gash[I7_Index_ID]]
			sampleSheetArray[ooh][index2] = dict_of_indices[gash[I7_Index_ID]]


	#print(sampleSheetArray)

	newName = 'SampleSheet.csv'

	with open(sampleSheetPath, 'w', newline='', encoding='utf-8') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
		for row in sampleSheetArray:
			spamwriter.writerow(row)


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

def main() :
	
	subjectRun = {"Path": "/mnt/heisenberg/210721_NB501662_0305_AHGN3HBGXJ", "folderName":"210721_NB501662_0305_AHGN3HBGXJ", "runName": "", "runInstrument":"", "FlowcellID":"", "outputFolderLocation":"", "outputErrors":[]}

	runCheck = sampleSheetReader(subjectRun)
	'''
	print(runCheck)
	
	fastQCRunner(subjectRun)
	directoryMover(subjectRun)
	
	return
	'''
main()
