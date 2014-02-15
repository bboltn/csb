#!bin/python


from bs4 import BeautifulSoup


import argparse
import io
import os
import re
import sys
import time
import urllib
import urlparse


parser = argparse.ArgumentParser(description= \
                'Converts Blogger export to seperate jekyll markdown files.')
parser.add_argument("Input", help="The Blogger export file")
parser.add_argument("JekyllRoot", help="The root location of your jekyll blog")
parser.add_argument("--test", action="store_true", help="Test Run. " \
                    "Output markdown to console.")

args = parser.parse_args()
import_path = args.Input
export_path = args.JekyllRoot + "/_posts"
images_path = args.JekyllRoot
is_test = args.test


def main():
    soup = BeautifulSoup(get_file_contents(import_path))
    count = parse_entries(soup("entry"))
    if is_test:
        print "Running Test!"

    print "\nFound %d posts" % count


def format_time(entry, timefield):
    time_obj = time.strptime(entry(timefield)[0].string[0:16], "%Y-%m-%dT%H:%M")
    return time.strftime("%Y-%m-%d", time_obj)


def get_image_and_content(entry):
    content = entry("content")[0].string
    if not os.path.isdir("%s/images" % images_path) and not is_test:
        os.mkdir("%s/images"  % images_path)

    soup = BeautifulSoup(content)
    imgs = soup("img")

    for img in imgs:
        image_source = img["src"]
        filename = get_name_from_path(image_source, "images")

        if not is_test:
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


def save_file(filename, title, body, tags, published_at):
    template = unicode(\
"""---
layout: post
title: {title}
date: {date}
---

{body}
""")

    content = template.format(
                              title=title,
                              date=published_at,
                              categories="\n- ".join(tags.split(";")),
                              body=body
                              )
    if is_test:
        print "---------POST----------"
        print content
    else:
        blog_file = io.open(filename, "w")
        blog_file.write(content)
        blog_file.close()


def parse_categories(entry):
    categories = entry("category")
    tags = []
    is_post = False
    for category in categories:
        if category["term"] == "http://schemas.google.com/blogger/2008/kind#post":
            is_post = True
        if category["scheme"] == "http://www.blogger.com/atom/ns#" \
            and category["term"]:
            tags.append(category["term"])

    return is_post, "; ".join(tags)


def parse_entries(entries):
    count = num_posts = 0
    for entry in entries:
        count += 1
        is_post, tags = parse_categories(entry)

        if is_post:
            pub = format_time(entry, "published")
            dirty_title = entry("title")[0].string
            title = clean_title(dirty_title,' ')
            filename = create_file_name(pub, clean_title(dirty_title, '-'))
            content = get_image_and_content(entry)

            save_file(filename, title, content, tags, pub)

            num_posts += 1

        progress(count, len(entries))

    return num_posts


def get_file_contents(file_path):
    file = io.open(file_path)
    return file.read(-1)


def progress(count, total):
    sys.stdout.write("\r%d of %d entries" % (count, total))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
