#!/usr/local/bin/python

# IMPORTS
import time
import glob2
import os.path
import zipfile, lxml.etree
import re
import subprocess
import exifread
from pyPdf import PdfFileReader
from optparse import OptionParser, SUPPRESS_USAGE
from bs4 import BeautifulSoup, Comment

# Get start time
start_time = time.clock()

print \
    """
                                WELCOME TO metaMAMA
                               ivanm@security-net.biz
    
         )))          ___          ===          )))          ___       `  ___  '
        (o o)        (o o)        (o o)        (o o)        (o o)     -  (O o)  -
    ooO--(_)--OooooO--(_)--OooooO--(_)--OooooO--(_)--OooooO--(_)--OooooO--(_)--Ooo-
    
    
    """
print "|-"

# Args
parser = OptionParser(usage=SUPPRESS_USAGE)
parser.add_option("--dir", dest="directory")
parser.add_option("--stringsn", dest="stringsn")
parser.add_option("--stringsc", dest="stringsc")
parser.add_option("--stringso", dest="stringso")
parser.add_option("-v", dest="verbose", default="0", help="")
parser.add_option("--extfilter", dest="extfilter", default="*", help="")
(options, args) = parser.parse_args()

start_path = str(options.directory)
stringsn = str(options.stringsn)
stringsc = str(options.stringsc)
stringso = str(options.stringso)
verbose = str(options.verbose)
extension_filter = str(options.extfilter)


def error():
    print "?"
    exit()


def print_and_log(x, ext):
    if verbose == 1:
        print x

    with open(ext.lstrip(".") + ".mmlog", "a") as myfile:
        myfile.write(str(x) + "\n")


ext_no = {}

'''
try:
    subprocess.check_output('rm ./*.mmlog', shell=True, stderr=subprocess.STDOUT)
except:
    pass
'''

if start_path != "" and start_path != "None":

    if stringsn == "" or stringsn == "None":
        stringsn = "15"

    if stringsc == "" or stringsc == "None":
        stringsc = 1

    if stringso == "" or stringso == "None":
        stringso = 0

    print "|- Starting metaMAMA on: " + start_path
    print "|-"

    cdx = []
    skip_ext = ['.tmp', '.delay', '.delaye', '.dela']
    skip_strings_on_txt = ['.txt', '.html', '.htm', '.js', '.css', '.xml']
    skip_exif_info = ['JPEGThumbnail']

    d = glob2.iglob(start_path + "**/*.*")

    for out in d:

        rank = 0

        out = out.strip()
        extension = os.path.splitext(out)[1].lower()

        if extension_filter != "*" and extension != extension_filter:
            continue

        if extension not in skip_ext and out != "" and out != start_path and os.path.isdir(out) == False:

            if extension in ext_no:
                ext_no[extension] += 1
            else:
                ext_no[extension] = 1

            print_and_log("|-", extension)
            print_and_log("|- FILE " + out, extension)

            # EXIF
            try:
                f = open(out, 'rb')
                tags = exifread.process_file(f)
                if tags != {}:
                    print_and_log("|-   EXIF", extension)
                    for t in tags:
                        if t not in skip_exif_info:
                            print_and_log(t + "\t" + tags[t], extension)
                            rank += 1
                f.close()
            except:
                pass

            # PDF
            try:
                pdf_toread = PdfFileReader(open(out, "rb"))
                pdf_info = pdf_toread.getDocumentInfo()
                print_and_log("|-   PDF", extension)
                for a in pdf_info:
                    print_and_log(a + "\t" + pdf_info[a], extension)
                    rank += 1
            except Exception as e:
                if str(e) != "EOF marker not found":
                    print_and_log("|-   PDF ERROR", extension)
                    print_and_log(e, extension)
                pass

            # Comments
            try:
                f = open(out, "rb").read()
                soup = BeautifulSoup(f, "lxml")
                comments = soup.findAll(text=lambda text: isinstance(text, Comment))
                for c_x in comments:
                    if u"HTTrack" not in c_x and u"if lt IE" not in c_x:
                        print_and_log("|-   COMMENTS", extension)
                        print_and_log(c_x.encode('utf-8'), extension)
                        rank += 1
            except:
                pass

            # OFFICE
            try:
                if extension == '.docx':
                    '''
                    print_and_log("|-   OLE", extension)
                    output = subprocess.check_output('olemeta ' + out, shell=True)
                    print_and_log(output, extension)
                    '''

                    zf = zipfile.ZipFile(out)
                    # use lxml to parse the xml file we are interested in
                    doc = lxml.etree.fromstring(zf.read('docProps/core.xml'))
                    # retrieve creator
                    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                    # creator = doc.xpath('//dc:creator', namespaces=ns)[0].text
                    creator = doc.xpath('//dc:*', namespaces=ns)[0].text
                    print_and_log("|-   OFFICE", extension)
                    print_and_log("|-   OFFICE " + str(creator), extension)
                    rank += 1
            except:
                pass

            # URLS/HOSTS
            p = "(?P<url>http?://[^\s]+)"
            m = re.findall(p, open(out, "rb").read())
            if str(m) != 'None' and m != []:
                print_and_log("|- URL " + str(m), extension)
                rank += 1

            # STRINGS
            if rank == 0 or stringso == 1:
                if extension not in skip_strings_on_txt:
                    try:
                        output = subprocess.check_output('/usr/bin/strings -n ' + stringsn + ' "' + out + '"',
                                                         shell=True)
                        print_and_log("|-   STRINGS", extension)
                        if stringsc == 0:
                            print_and_log(output, extension)
                        else:
                            for oc in output.split("\n"):
                                if output != [] and "00000" not in output and "<</Filter/" not in output and "word/media/" not in output:
                                    print_and_log(output.strip(), extension)
                    except:
                        pass

            print_and_log("|-", extension)


    print "|- " + str(time.clock() - start_time), "seconds"
    print "|- " + str(ext_no)

    print "|- STARTING FILTERS "

    yyy_a = []
    yyy_p = []
    d = glob2.iglob("./*.mmlog")

    for out in d:

        out = out.strip();
        print_and_log('|- FILEL ' + out, "filter1")
        f = open(out, "rb").read()

        for line in f.split("\n"):
            xline = ""
            if "|- FILE " in line:
                print_and_log('|- FILE ' + line, "filter1")
                xline = line

            if "|-   OFFICE " in line:
                print_and_log(xline, "filter1")
                print_and_log(line, "filter1")

            if "|- URL " in line:
                print_and_log(xline, "filter1")
                print_and_log(line, "filter1")

            if "Producer" in line or "Author" in line or "Creator" in line:
                print_and_log(xline, "filter1")
                print_and_log(line, "filter1")

        p = "<dc:creator>(.*?)<\/dc:creator>"
        m = re.search(p, f, re.DOTALL)
        if str(m) != 'None' and m != []:
            print_and_log("|- CREATOR " + str(m.group(0)), "filter1")

    f = open("./filter1.mmlog", "rb").read()

    for line in f.split("\n"):

        if "/Author" in line and line[0] == "/":
            yyy_a.append(line.replace("/Author", "").strip())

        if "/Producer" in line and line[0] == "/":
            yyy_p.append(line.replace("/Producer", "").strip())

        if "/Creator" in line and line[0] == "/":
            yyy_p.append(line.replace("/Creator", "").strip())

    yyy_a = list(set(yyy_a))
    for y_a in yyy_a:
        print_and_log(y_a, "filter2")

    yyy_p = list(set(yyy_p))
    for y_p in yyy_p:
        print_and_log(y_p, "filter2")

    print "|- That's all folks, check *.mmlog files."
    print "|- "


else:
    print "|- Please give me some --dir /file/system/path/"



