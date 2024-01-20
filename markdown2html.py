#!/usr/bin/python3

"""
Markdown script using Python.
"""

import sys
import os.path
import re
import hashlib


def process_bold_and_italic(line):
    # Process bold and italic syntax
    line = line.replace('**', '<b>', 1)
    line = line.replace('**', '</b>', 1)
    line = line.replace('__', '<em>', 1)
    line = line.replace('__', '</em>', 1)
    return line


def process_md5(line):
    # Process md5 syntax
    md5 = re.findall(r'\[\[.+?\]\]', line)
    md5_inside = re.findall(r'\[\[(.+?)\]\]', line)
    if md5:
        line = line.replace(
            md5[0],
            hashlib.md5(md5_inside[0].encode()).hexdigest()
        )
    return line


def process_remove_c(line):
    # Process remove c syntax
    remove_letter_c = re.findall(r'\(\(.+?\)\)', line)
    remove_c_more = re.findall(r'\(\((.+?)\)\)', line)
    if remove_letter_c:
        remove_c_more = ''.join(
            c for c in remove_c_more[0] if c.lower() != 'c'
        )
        line = line.replace(remove_letter_c[0], remove_c_more)
    return line


if __name__ == '__main__':
    # Check command-line arguments
    if len(sys.argv) < 3:
        print('Usage: ./markdown2html.py '
              'README.md README.html', file=sys.stderr)
        sys.exit(1)

    # Check if the Markdown file exists
    if not os.path.isfile(sys.argv[1]):
        print('Missing {}'.format(sys.argv[1]), file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as read:
        with open(sys.argv[2], 'w') as html:
            unordered_start, ordered_start, paragraph = False, False, False

            for line in read:
                # Process various Markdown syntax
                line = process_bold_and_italic(line)
                line = process_md5(line)
                line = process_remove_c(line)

                length = len(line)
                headings = line.lstrip('#')
                heading_num = length - len(headings)
                unordered = line.lstrip('-')
                unordered_num = length - len(unordered)
                ordered = line.lstrip('*')
                ordered_num = length - len(ordered)

                # headings, lists
                if 1 <= heading_num <= 6:
                    line = (
                            '<h{}>{}</h{}>\n'
                            .format(heading_num, headings.strip(), heading_num)
                            )

                if unordered_num:
                    if not unordered_start:
                        html.write('<ul>\n')
                        unordered_start = True
                    line = '<li>' + unordered.strip() + '</li>\n'
                if unordered_start and not unordered_num:
                    html.write('</ul>\n')
                    unordered_start = False

                if ordered_num:
                    if not ordered_start:
                        html.write('<ol>\n')
                        ordered_start = True
                    line = '<li>' + ordered.strip() + '</li>\n'
                if ordered_start and not ordered_num:
                    html.write('</ol>\n')
                    ordered_start = False

                if not (heading_num or unordered_start or ordered_start):
                    if not paragraph and length > 1:
                        html.write('<p>\n')
                        paragraph = True
                    elif length > 1:
                        html.write('<br/>\n')
                    elif paragraph:
                        html.write('</p>\n')
                        paragraph = False

                if length > 1:
                    html.write(line)

            if unordered_start:
                html.write('</ul>\n')
            if ordered_start:
                html.write('</ol>\n')
            if paragraph:
                html.write('</p>\n')

    sys.exit(0)
