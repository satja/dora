"""Prepisuje tutorijale sa https://github.com/agrbin/hwop/tree/gh-pages,
koji su klonirani u external/hwop direktorij, u moje templateove.
"""

import os


def prepisi(ime, izvorni_html):
    ciljni_html = os.path.join('zadaci/templates/tutorijali', ime) + '.html'
    cilj = open(ciljni_html, 'w')
    cilj.write("{% extends 'base.html' %}\n")
    cilj.write("{% block title %}" + ime.capitalize() +
               "{% endblock title %}\n")
    cilj.write("{% block content %}\n")

    sadrzaj = False
    with open(izvorni_html) as izvor:
        for line in izvor:
            if "</body>" in line:
                break
            if sadrzaj:
                line = line.replace('href="/', 'href="/tutorijali/')
                line = line.replace("href='/", "href='/tutorijali/")
                line = line.replace('/img/cc_88x31.png', '/static/cc_88x31.png')
                cilj.write(line)
            if "<body" in line:
                sadrzaj = True

    cilj.write("{% endblock content %}")
    cilj.close()


if __name__ == "__main__":
    prepisi('index', 'external/hwop/index.html')
    for path, subdirs, files in os.walk('external/hwop'):
	if not files:
		continue
        izvorni_html = os.path.join(path, files[0])
        ime = os.path.split(path)[-1]
        prepisi(ime, izvorni_html)
