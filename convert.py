from bs4 import BeautifulSoup
import io, time, re, urllib, urlparse, os, sys

def format_time(entry, timefield):
    time_obj = time.strptime(entry(timefield)[0].string[0:16], "%Y-%m-%dT%H:%M")
    return time.strftime("%Y%m%d%H%M%S", time_obj)

def get_image_and_content(entry):
    content = entry("content")[0].string
    if not os.path.isdir("Export/images"):
        os.mkdir("Export/images")

    soup = BeautifulSoup(content)
    imgs = soup("img")
    for img in imgs:
        image_source = img["src"]
        filename = get_name_from_path(image_source, "images")
        urllib.urlretrieve(image_source, "Export/%s" % filename)
        content = content.replace(image_source, filename)

    return content

def get_name_from_path(url, rel_path = None):
    path = urlparse.urlparse(url).path
    filename = os.path.split(path)[1]
    if rel_path:
        return "%s/%s" % (rel_path, filename)
    
    return filename

def create_file_name(pub, title):
    if title:
        pattern = re.compile('[\W_]+')
        clean_title = pattern.sub('-', title).rstrip("-")
        filename_xml = "%s-%s.xml" % (pub, clean_title)
    else:
        filename_xml = "%s.xml" % (pub)

    return "Export/" + filename_xml

def get_link_to_me(entry):
    links = entry("link")

    for link in links:
        if link["rel"] == ["alternate"] and "fountaincitycode.com" in link["href"]:
            return link["href"]

    return ""

def save_file(filename_xml, title, link_to_me, content, tags):
    blog_file = io.open(filename_xml, "w")
    blog_file.write("<blog>\n\t<title>%s</title>\n\t<ref>%s</ref>\n\t<tags>%s</tags>\n\t<content><![CDATA[%s]]></content>\n</blog>" % (title, link_to_me, tags, content))
    blog_file.close()

def parse_categories(entry):
    categories = entry("category")
    tags = []
    is_post = False
    for category in categories:
        if category["term"] == "http://schemas.google.com/blogger/2008/kind#post":
            is_post = True
        if category["scheme"] == "http://www.blogger.com/atom/ns#" and category["term"]:
            tags.append(category["term"])

    return is_post, "; ".join(tags)

def parse_entries(entries):
    count = num_posts = 0
    for entry in entries:
        count += 1
        is_post, tags = parse_categories(entry)

        if is_post:
            pub = format_time(entry, "published")
            updated = format_time(entry, "updated")
            title = entry("title")[0].string
            filename_xml = create_file_name(pub, title)
            link_to_me = get_link_to_me(entry)
            content = get_image_and_content(entry)

            save_file(filename_xml, title, link_to_me, content, tags)

            num_posts += 1

        progress(count, len(entries))
            

    return num_posts

def get_file_contents(file_path):
    file = io.open(file_path)
    return file.read(-1)

def progress(count, total):
    sys.stdout.write("\r%d of %d entries" % (count, total))
    sys.stdout.flush()

#main
soup = BeautifulSoup(get_file_contents("Import/blog-03-03-2013.xml"))
count = parse_entries(soup("entry"))
print "\nFound %d posts" % count
