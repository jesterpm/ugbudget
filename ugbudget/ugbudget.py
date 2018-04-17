import argparse
import collections
import csv
import gnucashxml
import os
import sys
from decimal import Decimal

def main():
    parser = argparse.ArgumentParser(description='The Usable GnuCash Budget Tool')

    cmd_group = parser.add_mutually_exclusive_group(required=True)
    cmd_group.add_argument('--create-tags', action='store_true',
                           help='Update tags-file with any unmapped accounts')
    cmd_group.add_argument('--report', action='store_true',
                           help='Produce a budget vs. actuals report')
    parser.add_argument('tags_file', metavar='tags-file',
                        help='The mapping of GnuCash accounts to budget tags')
    parser.add_argument('data_file', metavar='gnucash-file',
                        help='The GnuCash data file to process')

    args = parser.parse_args()

    book = gnucashxml.from_filename(args.data_file)

    if args.create_tags:
        create_tags(book, args.tags_file)
    elif args.report:
        report(book, args.tags_file)

def read_tags(filename):
    '''
    Read a TSV file where each row maps a GnuCash account to a tag. A tag is
    one or more tab-separated values which are treated as budget categories,
    subcategories, etc.
    '''
    tag_header = ('category',)
    tags = {}
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            reader = csv.reader(f, csv.excel_tab)
            for row in reader:
                if row[0] == "account":
                    tag_header = row[1:]
                else:
                    tags[row[0]] = tuple(row[1:])
    return (tag_header, tags)

def write_tags(filename, tag_header, tags):
    '''
    Write a tags file as described by read_tags().
    '''
    with open(filename, 'wb') as f:
        writer = csv.writer(f, csv.excel_tab)
        writer.writerow(['account'] + list(tag_header))
        for account in sorted(tags):
            writer.writerow([account] + list(tags[account]))

def create_tags(book, tags_file):
    '''
    Read a GnuCash data file and add any new, unmapped accounts to tags_file.
    '''
    (tag_header, tags) = read_tags(tags_file)
    for (acc, children, splits) in book.walk():
        if not children:
            if acc.actype == "INCOME" or acc.actype == "EXPENSE":
                acc_name = gnucash_account_fullname(acc)
                if acc_name not in tags:
                    tags[acc_name] = tag_header
    write_tags(tags_file, tag_header, tags)

def report(book, tags_file):
    (tag_header, tags) = read_tags(tags_file)
    report = collections.defaultdict(lambda: collections.defaultdict(Decimal))
    for (acc, children, splits) in book.walk():
        acc_name = gnucash_account_fullname(acc)
        if acc_name in tags:
            mapping = tuple([acc.actype] + list(tags[acc_name]))
            for split in splits:
                date = split.transaction.date.strftime("%Y-%m-01")
                report[date][mapping] += split.value.copy_negate()

    writer = csv.writer(sys.stdout, csv.excel_tab)
    writer.writerow(['month', 'account_type'] + list(tag_header) + ['value'])
    for month in sorted(report):
        for (mapping, value) in report[month].iteritems():
            writer.writerow([month] + list(mapping) + [value])

def gnucash_account_fullname(acc, partial=''):
    if acc.parent:
        if partial:
            partial = "%s:%s" % (acc.name, partial)
        else:
            partial = acc.name
        return gnucash_account_fullname(acc.parent, partial)
    else:
        return partial

main()
