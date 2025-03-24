from urllib.parse import quote_plus
from urllib.request import urlopen
import requests
from html.parser import HTMLParser
import os
import configparser

global cfg
cfg = configparser.ConfigParser()
cfg.read("config/settings.cfg")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class URLHtmlParser(HTMLParser):
    links = []
    
    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
            
        for attr in attrs:
            if 'href' in attr[0]:
                self.links.append(attr[1])
                break

def extractURLS(content):
    parser = URLHtmlParser()
    parser.feed(content)
    return parser.links

def findValidURLS(urlList):
    blacklist = eval(cfg.get("url", "blacklist"), {}, {})
    newURLList = []
    for url in urlList:
        if "http" in url and not any(b in url for b in blacklist):
            newURLList.append(url)
    
    return newURLList

def getURLStarter(query):
    google = "http://www.google.com/search?ie=UTF-8&q=" + quote_plus(query)
    bing = "https://www.bing.com/search?q=" + quote_plus(query)
    r = requests.get(google)
    print("Google status code: " + str(r.status_code))
    match r.status_code:
        case 200: return google
        case _: 
            print(bcolors.WARNING + "[-] Bing page will be downloaded, not all links could be parsed" + bcolors.ENDC)
            return bing
    
    return "http://www.google.com/search?ie=UTF-8&q=" + quote_plus(query)

def downloadPage(url, filename):
    with urlopen(url) as page:
        content = page.read().decode()
        f = open("pages/" + filename, "w")
        f.write(content)
        print("[~] Downloading page: ", url)
        f.close()

def changeFileName(name):
    newName = ""
    for c in name:
        if c == ':' or c == '"' or c == "'" or c == ' ' or c == '/' or c == '.' or c == '|' or c == '-':
            newName = newName + "_"
        else:
            newName = newName + c
    newName = newName[:-1]
    newName = newName + ".html"

    newName = newName.replace("____", "_").replace("___", "_").replace("__", "_")
    return newName

def downloadDorks():
    with open("dorksData/dorks.dat") as f:
        for line in f:
            filename = changeFileName(line)
            downloadPage(getURLStarter(line), filename)

def getURL(query, s):
    r = requests.get(query)
    if not s: print("Google status code: " + str(r.status_code))
    match r.status_code:
        case 200:
            return query
        case 400:
            print(bcolors.WARNING + "[-] Bad request" + bcolors.ENDC)
            return "skip"
        case 404:
            print(bcolors.WARNING + "[-] Page not found" + bcolors.ENDC)
            return "skip"
        case _:
            print(bcolors.WARNING + "[-] Wrong exit code" + bcolors.ENDC)
            return None

def downloadPages():
    global checkpoint
    with open("outputs/URLList.txt") as f:
        for i, line in enumerate(f):
            if getURL(line, False) == None:
                checkpoint = i
                print(bcolors.FAIL + "[-] Error downloading page: " + line + bcolors.ENDC)
                print(bcolors.WARNING + "[!] Saved checkpoint as " + str(checkpoint) + " line" + bcolors.ENDC)
                return None
            elif getURL(line, True) == "skip":
                print(bcolors.WARNING + "[!] Skipping page: " + line + bcolors.ENDC)
                continue
            else:
                downloadPage(getURL(line, True), changeFileName(line))


def writeURLS():
    outFile = open("outputs/URLList.txt", "w")
    fileList = getFiles()
    for file in fileList:
        f = open("pages/" + file, "r")
        content = f.read()
        urls = findValidURLS(extractURLS(content))
        f.close

        for url in urls:
            print(url)
            outFile.write(url + "\n")
    outFile.close()
    
def getFiles():
    path = "pages/"
    dir_list = os.listdir(path)
    print(dir_list)
    return dir_list

def main():
    # downloadDorks()
    # writeURLS()
    if  downloadPages() == None:
        print(bcolors.FAIL + "[-] Error downloading pages" + bcolors.ENDC)
        print(bcolors.WARNING + "[!] Checkpoint: " + str(checkpoint) + bcolors.ENDC)
        print(bcolors.WARNING + "[!] Will be restarting from checkpoint in a while" + bcolors.ENDC)

if __name__ == "__main__":
    main()

