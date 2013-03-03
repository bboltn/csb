from bs4 import BeautifulSoup
import io
import markdown2
import time
import codecs

file = io.open("Import/blog-03-03-2013.xml")
file_contents = file.read(-1)

#lxml xpath doesn't seem to understand blogger export
soup = BeautifulSoup(file_contents)

entries = soup("entry")
count = 0

def formatTime(timefield):
    time_obj = time.strptime(entry(timefield)[0].string[0:16], "%Y-%m-%dT%H:%M")
    return time.strftime("%Y%m%d%H%M%S", time_obj)
    
for entry in entries:
    categories = entry("category")
    tags = []
    post = False
    for category in categories:
        if category["term"] == "http://schemas.google.com/blogger/2008/kind#post":
            post = True
        if category["scheme"] == "http://www.blogger.com/atom/ns#" and category["term"]:
            tags.append(category["term"])

    if post:
        pub = formatTime("published")
        updated = formatTime("updated")
        filename_xml = "%s.blogger.xml" % pub
        title = entry("title")[0].string
        content = entry("content")[0].string

        blog_file = io.open("Export/" + filename_xml, "w")
        blog_file.write("<blog>\n\t<title>%s</title>\n\t<content><![CDATA[%s]]></content>\n</blog>" % (title, content))
        blog_file.close()
        
        count += 1

print "Found %d posts" % count
print "done!"