from typing import List, Dict, Set, Tuple, NewType

import re
import sys

import twol.twgenerate as twgenerate 

multichar_set: Set[str] = set()
"""Collected for producing Multichar_Symbols for LEXC.  They consist
of morphophonemes enclosed in braces (e.g. {ao}) and of
morphosyntactic features (e.g. +CMP)

"""

defi_name_set: Set[str] = set()

weight_fmt = "¤{}"
weight_set = set()
patnam_fmt = "£{}"
patnam_set = set()

def collect_mphons(expr_str: str):
    mch_lst = re.findall(r"\{[^}]+\}|\+[A-Z0-9]+", expr_str)
    for mch in mch_lst:
        multichar_set.add(mch)

def check_defi_names(expr, line):
    #global defi_name_set
    defi_name_lst = re.findall(r"[A-ZÅÄÖ][a-zåäöA-ZÅÄÖ0-9]+", expr)
    for defi_name in defi_name_lst:
        if defi_name not in defi_name_set:
            print("***", line)
            exit("<<" + defi_name + ">> not defined")

def generated_base(mphon, cont):
    if cont in suffix_dict:
        base_mphon = mphon + suffix_dict[cont]
        base_lst = twtwol.generate(base_mphon)
        if base_lst:
            base_str = min(base_lst, key=len)
        else:
            base_str = "**" + base_mphon + "**"
    else:
        base_str = mphon
    base_str = base_str.replace("Ø", "")
    base_str = base_str.replace("§", "_") ### This line obsolete?
    return base_str

def main():
    #global defi_name_set
    import argparse

    argparser = argparse.ArgumentParser(
        "python3 entries2lexc.py",
        description="""Convert a list of mphonemic entries and
        continuations into a lexc lexicon.  Each line in the input may
        have a comment starting with '!' which is discarded.  Each
        line may be either a regexp entry in angle brackets '<', '>'
        and a continuation, or an ordinary entry and a continuation
        plus an optional weight.  Multicharacters in entries must
        either be enclosed in curly brackets '{', '}' or be capital
        letter feature names preceded by a plus sign (e.g. '+GEN')""")
    argparser.add_argument(
        "-i", "--input_files", nargs="+",
        help="""One or more names of entry files.  The first can be
        definitions for patterns and the second a file containing
        the patterns themselves.""")
    argparser.add_argument(
        "-n", "--lexname",
        help="""Name of the lexicon to be made out of the input
        entries if not given by a LEXICON line in the input file.""",
        default="")
    argparser.add_argument(
        "-c", "--continuation",
        help="A default name of the continuation lexicon if the entry has none",
        default="")
    argparser.add_argument(
        "-p", "--pattern-names",
        help="Add the pattern names of reg exp entries",
        action="store_true")
    argparser.add_argument(
        "-s", "--base-suffixes",
        help="""Dict of mophophonemic suffixes for base form generation
        of each continuation clas""",
        default="base-suffixes.json")
    argparser.add_argument(
        "-r", "--rules",
        help="Rule FST for generating base forms, default is None",
        default="")
    args = argparser.parse_args()
    lexicon_name = args.lexname

    definition_lst: List[str] = []
    """List of definitions to be written into the LEXC file.
The definitons in the input file need some quoting and reformatting."""
    
    entry_lst = []

    if args.rules:

        import hfst as hfst
        
        twgenerate.init(args.rules)

    if args.base_suffixes:
        import json
        suffix_file = open(args.base_suffixes, "r")
        suffix_dict = json.load(suffix_file)
    else:
        suffix_dict = {}

    ent_pat = re.compile(
        r"""
        (?P<entry> \S +)
        (\s+ (?P<cont> [/A-ZÅÄÖŠŽa-zšžåäö] \S +))?
        (\s + (?P<weight> [0-9] +))?
        (\s*;)?
        """, re.X)

    rege_pat = re.compile(
        r"""
        < (?P<re_entry> [^>]+ ) > # reg exp pattern
        \s*                       #
        (?P<cont> \S+ )           # continuation lexicon name
        (
          \s+                     #
          (?P<weight> \d+ )       # weight
          ( \s+
            (?P<name> [A-ZŠŽÅÄÖ]+ ) # name of the pattern
          )?
        )?
        """, re.X)

    defi_pat = re.compile(r"^\s*[A-ZÅÄÖa-zåäö][A-ZÅÄÖa-zåäö0-9]+\s*=")

    import fileinput

    allfiles = fileinput.input(args.input_files)

    defi_line_lst: List[str] = []
    rege_line_lst = []

    for line_nl in allfiles:
        line, exclam, comment = line_nl.partition("!")
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if line.startswith("LEXICON"):
            lexicon_keyword, space, lexicon_name = line.partition(" ")
            if not lexicon_name:
                exit("*** LEXICON NAME MISSING")
            entry_lst.append(line)
            continue

        # print("line:", line) ###

        if defi_line_lst or " = " in line:
            # A definition may consist of several lines.  Lines are
            # first collected to a list and they are processed only
            # after all have been read in.
            defi_line_lst.append(line)
            if line.endswith(";"):
                line_str = " ".join(defi_line_lst)
                line_str = line_str.strip(" \t\n;")
                collect_mphons(line_str)
                defi_name, equal, expr = line_str.partition("=")
                check_defi_names(expr, line_str)
                defi_name_set.add(defi_name.strip())
                line_str = re.sub(r"([{}])", r"%\1", line_str)
                definition_lst.append(line_str)
                defi_line_lst = []

        elif rege_line_lst or line.startswith("<"):
            # A regular expression entry enclosed in <...> may consist
            # of several lines which are first processed and collected
            # to a list.  A complete definiton is output it has been
            # fully read in (i.e. ; is encountered).
            rege_line_lst.append(line)
            if line.endswith(";"):
                line_str = " ".join(rege_line_lst)
                orig_line_str = line_str.strip(" \t\n;")
                collect_mphons(orig_line_str)
                line_str = re.sub(r"([{}])", r"%\1", orig_line_str)
                rege_mat = m_regent = rege_pat.fullmatch(line_str)
                if not rege_mat:
                    exit(line_str)
                r = rege_mat.group("re_entry").strip()
                check_defi_names(r, orig_line_str)
                c = rege_mat.group("cont")
                w = rege_mat.group("weight")
                if w:
                    w = weight_fmt.format(w)
                    weight_set.add(w)
                    multichar_set.add(w)
                n = rege_mat.group("name")
                n = patnam_fmt.format(n) if n and args.pattern_names else ""
                if n:
                    patnam_set.add(n)
                    multichar_set.add(n)
                if w and n:
                    entry_lst.append(f"< {r} {n}:0 {w}:0 > {c} ;")
                elif w:
                    entry_lst.append(f"< {r} {w}:0 > {c} ;")
                elif n:
                    entry_lst.append(f"< {r} {n}:0 > {c} ;")
                else:
                    entry_lst.append(f"< {r} > {c} ;")
                rege_line_lst = []

        else:
            ent_mat = ent_pat.fullmatch(line)
            if not ent_mat:
                exit("!!!!!!!!!!!!!!!!!!" + line)
            #### print(ent_mat.groups()) ####
            # e = ent_mat.group("entry").replace("_", "{_}")
            e = re.sub(r"(?![{])_(?![}])", "{_}", ent_mat.group("entry"))
            collect_mphons(e)
            c = ent_mat.group("cont")
            if not c:
                c = args.continuation
                if ":" not in e and args.rules:
                    e = generated_base(e, c) + ":" + e
            w = ent_mat.group("weight")
            w = f' "weight {w}"' if w else ""
            ## w = f'W{w}' if w else ""
            ## entry = f"{e} {c}{w} ;"
            entry = f"{e} {c}{w} ;"
            entry_lst.append(entry)


    if multichar_set:
        print("Multichar_Symbols")
        mch_lst = sorted(list(multichar_set))
        print(" ".join(mch_lst))

    if definition_lst:
        print("Definitions")
    for definition in definition_lst:
        print(definition, ";")

    if not entry_lst[0].startswith("LEXICON"):
        print("LEXICON", args.lexname)

    for line in entry_lst:
        print(line)

if __name__ == "__main__":
    main()
