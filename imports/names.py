import urllib2

response = urllib2.urlopen('http://0x80.org/wordlist/fast-names')
lines = response.readlines()
lines = filter(lambda line: len(line) > 0 and line[0] != '#', lines)

names = lines
