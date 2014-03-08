CSB
-----------------------------------------------------------
## Converts Blogger export to seperate jekyll markdown files.

```
positional arguments:
  Input       The Blogger export file
  JekyllRoot  The root location of your jekyll blog

optional arguments:
  -h, --help  show this help message and exit
  --test      Test Run. Output markdown to console.
```

## Example usage
```
./convert.py blog-02-15-2014.xml ~/blog/progrn.github.io/

./convert.py blog-02-15-2014.xml ~/blog/progrn.github.io/ --test

```
