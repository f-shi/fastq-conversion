import os
import time
import datetime as DT
import filecmp
import shutil
import subprocess
import smtplib, ssl
from email.message import EmailMessage

archivePath = "/mnt/heisenberg/ARCHIVE/"
bigBirdPath = "/mnt/bigbird/"

def backSlasher(string, holdInt):

	slashIndices = [i for i, ltr in enumerate(string) if ltr == '/']
	string = string[(slashIndices[-holdInt]+1):]
	
	return string

def bigBirdChecker(folder, changeTracker):
	#print(folder)
	
	changeTracker = changeTracker + "\nChecking %s: Old enough to delete.\n" % folder
	folderSlash = backSlasher(folder, 2)
	backEnd = os.path.join(bigBirdPath, folderSlash)

	if os.path.isdir(backEnd):
	
		bbFolderList = [ backSlasher(f.path, 3) for f in os.scandir(backEnd) if f.is_dir() ]
		hFolderList = [ backSlasher(f.path, 3) for f in os.scandir(folder) if f.is_dir() ]
		
		overLap, noOverLap = overLapper(hFolderList, bbFolderList)
		
		noOverLapBool = True
		for noneOver in noOverLap:
			heisenbergLocation = os.path.join(archivePath, noneOver)
			bigBirdLocation = os.path.join(bigBirdPath, noneOver)
			
			moveCheck1 = subprocess.run(["scp", "-r", "-v", heisenbergLocation, bigBirdLocation])
			
			changeTracker = changeTracker + "A folder (%s) was not in Big Bird, so the folder was copied over from Heisenberg.\n" % noneOver
			
			if moveCheck1.returncode == 0:
				changeTracker = changeTracker + "Moving from %s to %s worked!\n" % (heisenbergLocation, bigBirdLocation)
			else:
				noOverLapBool = False
		
		overLapBool = True
		for overOver in overLap:
			result = filecmp.dircmp(os.path.join(archivePath, overOver), os.path.join(bigBirdPath, overOver))
			
			if len(result.left_only) != 0:
				
				#print(overOver, result.left_only)
				
				for fileName in result.left_only:
					changeTracker = changeTracker + "There was a file (%s) on Heisenberg that was not on BigBird.\n" % fileName
					
					if fileName == "bcl2fastqCheck.txt":
						continue
					
					else:
						heisenbergLocation = os.path.join(archivePath, overOver, fileName)
						bigBirdLocation = os.path.join(bigBirdPath, overOver, fileName)
						successCheck = subprocess.run(["scp", "-r", "-v", heisenbergLocation, bigBirdLocation])
						overLapBool = successCheck.returncode == 0
					

		
		if noOverLapBool and overLapBool:
			try:
				changeTracker = changeTracker + "Deleting the folder...\n"
				shutil.rmtree(folder, ignore_errors=True)
				changeTracker = changeTracker + "Deleted successfully!\n"
			except Exception as e:
				changeTracker = changeTracker + "Failed to delete because %s.\n" % e
		
	else:
		#print("Failed:", backEnd)
		changeTracker = changeTracker + "Cannot find a copy of %s on Heisenberg, so copying it to BigBird:" % folder
		moveCheck1 = subprocess.run(["scp", "-r","-v", folder, backEnd])
		
		if moveCheck1.returncode == 0:
			changeTracker = changeTracker + "Success!\n"
			deleteCheck = shutil.rmtree(folder)
			changeTracker = changeTracker + "Successfully removed the directory.\n"
		else:
			changeTracker = changeTracker + "Failure!\n"
	
	
	#deleteCheck1 = shutil.rmtree(folder)
	
	changeTracker = changeTracker + "\n"
	#print(changeTracker)
	return changeTracker

def deleteRecorder():
	
	return

def errorSender(errorMessage):
	
	msg = EmailMessage()
	msg.set_content(errorMessage)
	
	recipientEmails = ["fangshi90@gmail.com", "fangshi@gatech.edu"]
	senderEmail = "molecular.evolution@outlook.com"
	msg["Subject"] = 'Error: '
	msg["From"] = "molecular.evolution@outlook.com"
	msg["To"] = ','.join(recipientEmails)


	port = 587
	password = "MolEvol1@GT"
	
	message = "try this"
	
	context = ssl.create_default_context()
	
	with smtplib.SMTP("smtp.office365.com", port) as server:
		server.starttls(context=context)
		server.login("molecular.evolution@outlook.com", password)
		server.send_message(msg)
		server.quit()
	
	return	

def folderIterator():

	instrumentList = ["iSeq", "MiniSeq", "MiSeq", "NextSeq", "NovaSeq"]
	changeTracker = "Starting to clean Heisenberg.\n"
	
	for folder in instrumentList:
		keepPath = os.path.join(archivePath, folder)
		
		folderList = [ f.path for f in os.scandir(keepPath) if f.is_dir() ]
		
		for folder in folderList:
			changeTracker = folderRipper(folder, changeTracker)
	
	errorSender(changeTracker)
		
def folderRipper(folderName, changeTracker):
	#print(folderName)
	folderList = [ f.path for f in os.scandir(folderName) if f.is_dir() ]
	
	timeDiffOver = 1000000000.0
	
	for folder in folderList:

		timeDiff = lastModifiedCheck(folder)
		#print(timeDiff/(24*3600))
		
		if timeDiff < timeDiffOver:
			timeDiffOver = timeDiff
		

	timeDiffOver = timeDiffOver/(24*3600)
	
	if timeDiffOver > 45:
		changeTracker = bigBirdChecker(folderName, changeTracker)
	else:
		changeTracker = changeTracker + "\nChecked %s: Folder is too recent to delete, because it's only been %s days.\n" % (folderName, round(timeDiffOver, 2))
	
	return changeTracker

def lastModifiedCheck(folder):

	textName = os.path.join(folder, "bcl2fastqCheck.txt")
	
	try:
		textFile = open(textName)
		textLine = textFile.read()
		arrowIndices = [i for i, ltr in enumerate(textLine) if ltr == '>']
		textLine = textLine[0:arrowIndices[0]].strip()
		lastModified = DT.datetime.strptime(textLine, '%m/%d/%Y, %H:%M:%S')
		
		
	except Exception as e:
		#print(e)
		lastModified = DT.datetime.utcfromtimestamp(max(os.path.getmtime(root) for root,_,_ in os.walk(folder))) - DT.timedelta(hours = 4)

	
	nowTime = DT.datetime.now()	
	timeDiff = nowTime.timestamp() - lastModified.timestamp()
	
	#print(folder, timeDiff/(24 * 3600))
		
	return timeDiff

def overLapper(hFolderList, bbFolderList):
	
	noLap = []
	oLap = []
	
	for hFolder in hFolderList:
		if hFolder not in bbFolderList:
			noLap.append(hFolder)
		else:
			oLap.append(hFolder)
			
	return oLap, noLap

def secondsToDays(seconds):
	
	days = seconds/(24 * 3600)

	return days

def main():
	
	folderIterator()
		
main()
