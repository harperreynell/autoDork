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

def getURL(query):
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

def downloadAllPages():
    with open("dorksData/dorks.dat") as f:
        for line in f:
            filename = changeFileName(line)
            downloadPage(getURL(line), filename)

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

# def goThroughFilesAndGetURLS():
#     fileList = getFiles()
#     for file in fileList:
#         writeURLS("pages/" + file)
    
def getFiles():
    path = "pages/"
    dir_list = os.listdir(path)
    print(dir_list)
    return dir_list

def main():
    # downloadAllPages()
    writeURLS()

if __name__ == "__main__":
    main()

# config files (maybe, just for fun)