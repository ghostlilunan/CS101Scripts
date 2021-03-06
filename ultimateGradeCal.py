# coding= latin-1
import glob, sys
import string
from nbgrader.api import Gradebook

def getCollabs(labSec, labNo):
    collabs = {} # to return
    files = glob.glob("/class/cs101/grading/AY"+labSec+"/submitted/*/lab"+labNo+"/lab"+labNo+".ipynb")
    from string import whitespace as w
    from string import punctuation as p
    from string import printable
    featureTxt = "Double-click here to list collaborators' or partners' **NetIDs** here:"
    for f in files:
        with open(f) as openF:
            data = openF.read()
            cell=data[data.find(featureTxt):data.find('lab'+labNo)]
            names=cell[len(featureTxt):cell.find(']')][:-1]
            label='write them here'
            if label in names:
                names=names[names.find(label)+ len(label) :]
            for c in w + p:
                names = names.replace(c, " ")       
            names = names.split(' ')
            names = [x for x in names if x != '']
            collabsList = ' '.join(names)
            sanitized=""
            for letter in collabsList:
                if letter in printable:
                    sanitized+=letter
            submitter = f.split("/")[1]
            collabsList = sanitized.split(' ')
            for i in range(len(collabsList)):
                collabsList[i] = collabsList[i].strip()
            collabs[submitter] = collabsList
    return collabs

'''
No longer need to generate extract_grades file.
'''
def getGrade(section, labNo):
    # labSec = sys.argv[1]
    print (section, labNo)
    labSec = "AY"+section
    gb = Gradebook('sqlite:////class/cs101/etc/sxns/'+labSec+'/gradebook.db')
    ourIds = []
    aNo = "lab" + labNo
    grades = {}
    for s in gb.assignmentni_submissions(aNo):
        if s.student_id not in ourIds:
            grades[s.student_id] = s.score
            # print(s.student_id, s.score)#, s.timestamp.isoformat())
    return grades
'''
getGradeFromFile(filename) opens a file given by extract_grades.py
in the format where each line is
netid,score
and return the grades as a dictionary.
'''
def getGradeFromFile(filename):
    grades = {} #Use a dictionary
    with open(filename) as f:
        for line in f.readlines():
            line = line.split()
            grades[line[0]] = float(line[1])
        collabs = {}
        if len(sys.argv)==5: # Using collabs
            collabs = getCollabs(sys.argv[3], sys.argv[4])
        for submitter in collabs:
            netidlist = collabs [submitter]
            if submitter in grades: # They should be, if not, print error I guess
                for netid in netidlist:
                    if netid in grades:
                        grades[netid] = grades[submitter]
    return grades

'''
getCollabs(filename) opens a file given by collabs.py
in the format where each line is
netid [netid netid ...]
and return a dictionary where the submitter is the key
'''
def getCollabsFromFile(filename):
    collabs = {}
    with open(filename) as f:
        for line in f.readlines():
            if (line==''):
                continue
            line2 = ""
            line = line.strip()
            for c in line:
                if c in string.printable:
                    line2 += c
            line = line2.split(' ')
            submitter = line[0]
            collabsList = line[1:]
            for i in range(len(collabsList)):
                collabsList[i] = collabsList[i].strip()
            collabs[submitter] = collabsList
    return collabs

def parseGrades(grades):
    format = {}
    if len(format) == 0:
        return grades
    for key in grades:
        grades[key] = format[float(grades[key])]
    return grades

def parseCollabs(content, collabs,colNo):
    if len(collabs)==0:
        pass
    # print (collabs)
    for collab in collabs:
        for word in collabs[collab]:
            if word in content:
                if content[word][colNo]!='':
                    if float(content[word][colNo])>float(content[collab][colNo]):
                        content[collab][colNo] = content[word][colNo]
                        continue
                else:
                    content[word][colNo] = content[collab][colNo] = "2.0" #unable it so that everyone gets 2.0
                # print(content[word][colNo],content[collab][colNo])

if __name__ == "__main__":
    if len(sys.argv)<4:
        print ("Usage: python ultimateGradeCal.py compassScores.csv labSec({A,B,..,Q}) labNo({00,01...15}) [collabs:Y/N]")
        exit(1)
    csvfilename = sys.argv[1]
    labSec = sys.argv[2]
    aNo = sys.argv[3]
    from extract_grades import extract_grades
    grades = extract_grades(labSec,aNo)
    # from relate_grade import readFileAndGrade
    # grades = readFileAndGrade(glob.glob("/home/hcheng17/cs101-fa17/lab01/subs/*"))
    # print (grades)
    # grades = parseGrades(grades)

    collabs = {}
    if len(sys.argv)==5 and sys.argv[-1] != 'N':
        collabs = getCollabs(labSec, aNo)
        # print (collabs)
    with open(csvfilename,'r') as f:
        fileContent = f.readlines()
        headers = fileContent[0].strip().split(',')
        colNo = 0
        netidNo = 0
        sectionNo = 0
        fileOutput = {} # dict of lists
        for i in range(len(headers)):
            # print(str(aNo[3:]))
            if headers[i].find("lab "+str(aNo))>-1:
                colNo = i
            if headers[i].find("Username")>-1:
                netidNo = i
            if headers[i].find("Section")>-1:
                sectionNo = i
        for line in fileContent[1:]:
            line = line.strip().split(',')
            netid = line[netidNo].strip('"')
            # print (netid)
            if netid in grades:
                line[colNo] = str(grades[netid])
                # print (line[colNo])
                fileOutput[netid]=(line.copy())
            else:
                line[colNo] = '0' # Set empty ones to 0
                fileOutput[netid]=(line.copy())
        parseCollabs(fileOutput, collabs,colNo)
        print (headers[netidNo]+','+headers[colNo])
        # print (fileOutput)
        for netid in fileOutput:
            section = fileOutput[netid][sectionNo].strip()[-2]
            if section == labSec:
                line = ','.join([fileOutput[netid][netidNo], fileOutput[netid][colNo]])
                print (line)

