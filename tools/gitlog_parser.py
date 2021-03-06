import os
import sys
import re
import pprint
import urllib
import hashlib

# global vars
commits = {}
messages = {}
inMessage = False
message = ""
i = 1
currenthash = ""
lasthash = ""
email_list = ""
target = ""

class commit:
    def __init__(self):
        self.hash = ""
        self.author = ""
        self.authorEmail = ""
        self.date = ""
        self.fileChanges = dict()
        self.state = dict()
        self.All = dict()
    def updateFileChanges(self, filename, linecount):
        if filename in self.fileChanges:
           self.fileChanges[filename] += linecount
        else:
            self.fileChanges[filename] = linecount

def main(argv):
    # no args given:
    numargs = len(argv)
    if numargs == 0:
        usage()
        return
    # assume a non-empty filepath
    path = argv[0]
    global target
    target = argv[1]
    LoC = []
    if path:
        parselog(path,LoC)
        printLoC(LoC)
    else:
        usage()

def parse(logpath, dir):
    global target
    target = dir   
    LoC = []
    parselog(logpath + "/gitLog.txt",LoC)
    printLoC(LoC,logpath)
    return LoC

# parses only git logs formatted using --numstat flag (and optionally --reverse)			
def parselog (path,LoC):
    global message
    global i
    global currenthash
    global lasthash
    global inMessage

    raw_log = open(path, 'r')
        
    hashpattern = re.compile("commit\s[0-9A-Fa-f]{40}")
    datepattern = re.compile("Date:\s{3}\w{3}\s\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s-\d{4}")


    for line in raw_log:
        if hashpattern.match(line):

            # save commit msg in case commit summary not detected
            saveMsg(lasthash)

            #get the hash
            result = line.split("commit")
            hash = result[1].strip()
            if hash:
                print("\nCommit #: " + str(i))
                LoC.append(commit())
                print(hash)
                LoC[len(LoC)-1].hash = hash
            #do something

            # remember current and previous hashes so we can do stuff
            lasthash, currenthash =  currenthash, hash
            i += 1

        elif 'Author: ' in line and '@' in line:
            result1 = line.split("Author:")
            result2 = result1[1].split("<")
            result3 = result2[1].split(">")

            name = result2[0].strip()
            email = result3[0].strip()
            print(name)
            LoC[len(LoC)-1].author = name
            print(email)
            LoC[len(LoC)-1].authorEmail = email
            addToEmailList(email)
        #do something

        elif datepattern.match(line):
            result = line.split("Date:")
            date = result[1].strip()
            LoC[len(LoC)-1].date = date
            print(date)
            next(raw_log)
            next(raw_log)
            next(raw_log)
        #do something

        elif '/' in line:
            # TODO handle deleted files
            # TODO handle modified files (total lines)

            # check file suffix inside or its passed to else block below...
            if ".java" in line:
                split = re.split(r'\t+', line)
                if (len(split)==3):
                    filename = split[2].split("/")[-1][:-1]

                    addition = int(split[0])
                    deletion = int(split[1])
                    lines_modified = addition - deletion

                    print("Lines changed: " + str(lines_modified) + "  " + filename)
                    LoC[len(LoC)-1].updateFileChanges(filename,lines_modified)
        elif (
            ("file changed" in line or "files changed" in line)
        and
            ("insertions(+)" in line or "deletions(-)" in line)
        ):
            # in a summary line for current commit
            # previous commit message ended when we reach here, save it and reset
            saveMsg(currenthash)
        else:
            if "Merge:" not in line:
                #its a commit message line
                cleanedline = line.strip()
                if inMessage:
                    message += cleanedline
                else:
                    inMessage = True
                    message += cleanedline


                # uncomment to print the messages dictionary
                # printer = pprint.PrettyPrinter()
                # printer.pprint (messages)

# saves non-empty message to dict
def saveMsg (hash):
    global inMessage
    global message
    global messages
    if inMessage:
        inMessage = False
        if message:
            messages[currenthash] = message
            message = "";


def printLoC(LoC,logpath):
    with open(logpath + "/wat.txt", "w") as f:
        for c in LoC:
            f.write("===========================" + "\n")
            f.write("commit: " + c.hash + "\n")
            f.write("author: "+ c.author + "\n")
            f.write("eMail: " + c.authorEmail + "\n")
            f.write("date : " + c.date + "\n")
            f.write("file changes : " + str(c.fileChanges) + "\n")
			
def addToEmailList (email):
	global email_list
	if email not in email_list:
		# just save emails found so we don't download gravatar icons more than once
		email_list += email
		saveGravatar(email)

def saveGravatar (email):
	base_url = 'http://www.gravatar.com/avatar/'
	# trim leading and trailing whitespace and tolowercase
	clean_email = email.strip().lower()
	# get md5
	gravatar_hash = hashlib.md5(clean_email.encode())
	grav_url = base_url + gravatar_hash.hexdigest()
	filename = email+".jpg"
	urllib.urlretrieve(grav_url, "./web/" + target + "/static/gravatars/"+filename)


def usage ():
    print ("Usage: gitlog_parser.py <path>")
    print ("<path> must be absolute filepath to a git log txt file generated using --stat flag and preferably --reverse")


if __name__ == "__main__":
    main(sys.argv[1:])






