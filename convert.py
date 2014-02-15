#!bin/python

from bs4 import BeautifulSoup
import io, time, re, urllib, urlparse, os, sys, argparse

parser = argparse.ArgumentParser(description= \
                    'Converts Blogger export to seperate xml files.')
parser.add_argument("Input", help="The Blogger export file")
parser.add_argument("DomainName", help="The domain name of the blogs")
parser.add_argument("Destination", default="Export",
                    help="Where the files should be saved")
parser.add_argument("ImagesDestination", default="Images",
                    help="Where the images should be saved")

#/Users/brian/blog/progrn.github.io/_site

args = parser.parse_args()
export_path = args.Destination
import_path = args.Input
domain_name = args.DomainName
images_path = args.ImagesDestination

def format_time(entry, timefield):
    time_obj = time.strptime(entry(timefield)[0].string[0:16], "%Y-%m-%dT%H:%M")
    return time.strftime("%Y-%m-%d", time_obj)

def get_image_and_content(entry):
    content = entry("content")[0].string
    if not os.path.isdir("%s/images" % images_path):
        os.mkdir("%s/images"  % images_path)

    soup = BeautifulSoup(content)
    imgs = soup("img")
    if len(imgs) > 0:
        print "Has images=%s" % entry("title")[0].string

    for img in imgs:
        image_source = img["src"]
        filename = get_name_from_path(image_source, "images")
        urllib.urlretrieve(image_source, "%s/%s" % (images_path, filename))

        content = content.replace(image_source, "/%s" % filename)

    return content

def get_name_from_path(url, rel_path = None):
    path = urlparse.urlparse(url).path
    filename = os.path.split(path)[1]
    if rel_path:
        return "%s/%s" % (rel_path, filename)
    
    return filename

def create_file_name(pub, title):
    title = title if title else "post"
    filename = "%s-%s.markdown" % (pub, title)

    return "%s/%s" % (export_path, filename)

def clean_title(dirty_title, subchar='-'):
    pattern = re.compile('[\W_]+')
    new_title = pattern.sub(subchar, dirty_title).rstrip(subchar)
    return new_title

def get_link_to_me(entry):
    links = entry("link")

    for link in links:
        if link["rel"] == ["alternate"] and domain_name in link["href"]:
            return link["href"]

    return ""

def save_file(filename, title, permalink, body, tags, published_at):
    template = unicode(\
"""---
layout: post
title: {title}
date: {date}
---

{body}
""")
    # print tags
    # return
    blog_file = io.open(filename, "w")
    content = template.format(
                              title=title,
                              date=published_at,
                              #categories="\n- ".join(tags.split(";")),
                              body=body
                              )

    blog_file.write(content)
    blog_file.close()

# title
# permalink
# body
# published_at
# filter (e.g. markdown, textile)

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
            dirty_title = entry("title")[0].string
            title = clean_title(dirty_title,' ')
            filename = create_file_name(pub, clean_title(dirty_title, '-'))
            link_to_me = get_link_to_me(entry)
            content = get_image_and_content(entry)

            save_file(filename, title, link_to_me, content, tags, pub)

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
soup = BeautifulSoup(get_file_contents(import_path))
count = parse_entries(soup("entry"))
print "\nFound %d posts" % count
