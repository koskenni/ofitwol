# affix2analylexc.py:
# builds a lexc file for analysis out of a csv file of affixes

copyright = """Copyright © 2017, Kimmo Koskenniemi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re, csv, sys

multichars = set()

def collect_multichars(str):
    if len(str) < 2: return
    lst = re.findall(r"[{][^}]+[}]", str)
    for mch in lst:
        multichars.add(mch)
    return

def main():
    import argparse
    argparser = argparse.ArgumentParser(
        "python3 root2lexc.py",
        description="""
        Converts a root lexicon CSV file into a LEXC file""")
    argparser.add_argument(
        "-e", "--entries",
        help="""Entries as output of the analysis

        If not set, the morphophonemic representations of the base
        form and the inflection features will be output by the
        resulting analyser.  If set, the output will be entries which
        could be added into an hfst-lexc lexicon.""",
        action="store_true", default=False)
    argparser.add_argument(
        "-d", "--delimiter",
        help="CSV field delimiter (default is ',')",
        default=",")
    argparser.add_argument(
        "-v", "--verbosity",
        help="Level of diagnostic output, (default is 0).",
        default=0, type=int)
    args = argparser.parse_args()

    feature_set = set()
    out_lst = []

    infile = sys.stdin
    rdr = csv.DictReader(infile, delimiter=args.delimiter)
    prevID = args.delimiter
    for r in rdr:
        if args.verbosity >= 10:
            print(r)
        next_lst = r["NEXT"].strip().split()
        if (not next_lst) or r["NEXT"].startswith('!'):
            continue
        ide = prevID if r["ID"] == '' else r["ID"]

        mphon_str = r["MPHON"].strip()
        collect_multichars(mphon_str)

        feature_lst = r['FEAT'].strip().split()
        feature_str = ((('+' + ('+'.join(feature_lst))))
                       if feature_lst else "")
        for feat in feature_lst:
            feature_set.add("+" + feat)

        ### basef_str = "" if args.entries else r["BASEF"].strip()
        basef_str = r["BASEF"].strip()
        collect_multichars(basef_str)

        weight_str = (' "weight: {}"'.format(r["WEIGHT"])
                      if r["WEIGHT"] else "" )
        entry_str = "% " + ide + "%;" if args.entries else ""
        boundary = "" if args.entries else "{_}" ### formerly {§}
        for nxt in next_lst:
            if ("/" in ide) and (not "/" in nxt) and (nxt != "More"):
                feat_str = entry_str + boundary + feature_str
            else:
                feat_str = feature_str
            basefeat_str = basef_str + feat_str
            if basefeat_str == mphon_str:
                lexc_str = "{} {}{} ;".format(basefeat_str,
                                              nxt, weight_str)
            else:
                lexc_str = "{}:{} {}{} ;".format(basefeat_str,
                                                 mphon_str,
                                                 nxt, weight_str)
            if prevID != ide:
                prevID = ide
                out_lst.append("LEXICON %s" % ide)
            out_lst.append(lexc_str)

    if multichars or feature_set:
        print("Multichar_Symbols")
        multichar_lst = sorted(list(multichars))
        multichar_str = " ".join(multichar_lst)
        print(multichar_str)
        features_lst = sorted(list(feature_set))
        print(" ".join(features_lst))
    for line in out_lst:
        print(line)

if __name__ == "__main__":
    main()
