import requests
import binascii
from bs4 import BeautifulSoup
from os import popen, chdir, system
import base64
import sys


from pprint import pprint
import os
FILE_LIST = []

def swap(i, i2, arr):
    i3 = arr[i]
    arr[i] = arr[i2]
    arr[i2] = i3


def solve(key, encoded):
    t = [i for i in range(256)]

    c = i2 = 0
    bArr = bytearray(key.encode("utf-8"))

    for i in range(256):
        i2 = (((i2 + t[i]) + bArr[i % len(bArr)]) + 256) % 256
        swap(i, i2, t)

    b = base64.b64decode(encoded).decode()

    barr3 = [(int(b[i], 16) << 4) + int(b[i+1], 16)
             for i in range(0, len(b), 2)]

    b = 0
    barr4 = []

    for i in range(len(barr3)):
        b = (b+1) % 256
        c = (c+t[b]) % 256
        swap(b, c, t)
        barr4.append(t[(t[b]+t[c]) % 256] ^ barr3[i])
    return ''.join([chr(x) for x in barr4])


def getkey(filename):
    rt = []
    pivot = popen('grep -rnai https://twitter ' + filename + '-out | head -1  &> /dev/null ').read().split(':')[0]
    twitter = popen(
        'head ' + pivot + ' -n51 | tail -n1 | sed -r  \'s/.*.(")(.*.)(").*$/\\2/\'  &> /dev/null').read()[:-1]
    rt.append(popen(
        'head ' + pivot + ' -n57 | tail -n1 | sed -r  \'s/.*.(")(.*.)(").*$/\\2/\'  &> /dev/null').read()[:-1])
    response = requests.get(twitter)
    rt.append(twitter)
    soup = BeautifulSoup(response.text, "html.parser")
    tweets = soup.findAll('li', {"class": 'js-stream-item'})
    for tweet in tweets:
        if tweet.find('p', {"class": 'tweet-text'}):
            rt.append(str(tweet.find('p',{"class":'tweet-text'}).text.encode('utf8').strip()).split(">")[1].split("<")[0])
            break
    return rt


def adbRun(adb,packageName):
    system(adb + ' push androidDump.out /data/local/tmp')
    system(adb + ' shell \'cd /data/local/tmp && ./androidDump.out ' + packageName +  "' &> /dev/null")
    system(adb + ' pull /data/local/tmp')

def run(d2j,fileName):
    system(d2j + "d2j-dex2smali.sh tmp/"+ fileName +'.dex' + " > /dev/null")
    pprint(os.getcwd())
    fileName = popen("find -maxdepth 1 -type d -name '" + fileName + "-out' &> /dev/null ").read()[:-1][2:]
    print(fileName)

def dexExc():
    filenames = popen("ls tmp/?????  &> /dev/null ").read().split('\n')[:-1]
    for filename in filenames:
        with open(filename, 'rb') as f:
            content = f.read()
        hexoc = binascii.hexlify(content).split(b'6465780a')
        hexoc.pop(0)
        hexoc = b'6465780a' + b''.join(hexoc)
        dex = open(filename+".dex","wb")
        dex.write(binascii.a2b_hex(hexoc[:int.from_bytes(binascii.a2b_hex(hexoc[:72][-8:]),byteorder='little')*2]))
        dex.close()
    pprint(filenames)
    return [ filename.split('/')[len(filename.split('/')) - 1] for filename in filenames]


def main():
    adbPath = sys.argv[1]
    dex2jarPath = sys.argv[2]
    packageName = sys.argv[3]
    #adbPath = '~/platform-tools/adb' 
    #dex2jarPath = '~/apk/d2/'
    #packageName = 'com.mhyspybnfqgl.kcseuel'
    adbRun(adbPath, packageName)

    for dexName in dexExc():
        run(dex2jarPath,dexName)
        try:
            keys = getkey(dexName)
            system("clear")
            print(keys[1])
            print(solve(keys[0], keys[2]))
            break
        except:
            pass    

main()
