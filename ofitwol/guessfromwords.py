
from collections import defaultdict

entry_set_dict = defaultdict(set)  # entry_set_dict[wrd] == {ent1, ..., entn}
word_set_dict = defaultdict(set)   # word_set_dict[entr] == {word1, ..., wordk}
weight_sum = defaultdict(int) # weight_sum[entr] == sum(we1, we2, ...)
entriesofwords = defaultdict(set) # entriesofwords["w1 w2 ... wn"] == {e1, .., ek}

def delete_entry(entry):
    """Delete an entry and and the words it would analyse from the dicts"""
    global entry_set_dict, word_set_dict
    for word in word_set_dict[entry]:
        entry_set_dict[word].discard(entry)
    # del word_set_dict[entry]
    word_set_dict[entry] = set()
    # del weight_sum[entry]
    weight_sum[entry] = float("inf")
    return

def delete_all_words(entry):
    """Delete from dicts its words from remaining entry candidates"""
    global entry_set_dict, word_set_dict
    siz = len(word_set_dict[entry])
    for word in word_set_dict[entry]:
        for entr in entry_set_dict[word]:
            if entr in word_set_dict and siz > len(word_set_dict[entr]):
                word_set_dict[entr].discard(word)
        if not entry_set_dict[word]:
            del entry_set_dict[word]
    return

def redundant_entry(entry):
    """Whether some other entry generates all words this one does and more"""
    global entry_set_dict, word_set_dict
    word_lst = list(word_set_dict[entry])
    if not word_lst:
        return True
    u_set = entry_set_dict[word_lst[0]]
    for word in word_lst[1:]:
        e_set = entry_set_dict[word]
        u_set = u_set & e_set
    for e in u_set:
        if ((word_set_dict[e] > word_set_dict[entry]) and
            (weight_sum[entry] > 0)):
            ###print("***", e, weight_sum[e],
            ###      "superset of", entry, weight_sum[entry])
            ###if weight_sum[e] < weight_sum[entry]:
            return True
    return False

def main():
    global entry_set_dict, word_set_dict
    import argparse
    arpar = argparse.ArgumentParser("python3 guessfromwords.py")
    arpar.add_argument(
        "-a", "--analysed",
        help="file of analyzed word forms in a format "
        "compatible with hfst-lookup output")
    arpar.add_argument(
        "-b", "--beam",
        help="""Entry candidates for identical sets of words
        but with a weight sum higher than the best plus this beam
        are discarded.  Default is 10""",
        type=float, default=0.2)
    arpar.add_argument(
        "-d", "--delta",
        help="Default is 3",
        type=int, default=3)
    arpar.add_argument(
        "-m", "--minimum",
        help="""Ignore entry candidates with fewer words than this. 
        Default is 4""",
        type=int, default=3)
    arpar.add_argument(
        "-v", "--verbosity",
        help="level of  diagnostic output, default is 0.",
        type=int, default=0)
    args = arpar.parse_args()

    if not args.analysed:
        import sys
        ana_fil = sys.stdin
    else:
        ana_fil = open(args.analysed, "r")
    #
    # First pass: Collect word_set_dict (set of words analysed by an
    # entry), entry_set_dict (set of entries that analyse a word) and
    # weight_sum (sum of the weights of all words analysed by an
    # entry) dicts from the words analysed with xxxguess.ofst
    #
    for line_nl in ana_fil:
        line = line_nl.strip()
        if not line:
            continue
        if line.count("\t") != 2:
            print("***", line)
            continue
        word, entry_and_feats, weight = line.split("\t")
        if weight == "inf":
            continue
        else:
            weight = float(weight.strip().replace(",", "."))
        entry, semicol, feats = entry_and_feats.partition(";")
        if not semicol:
            entry, plus, feats = entry.partition("+")

        word_set_dict[entry].add(word)
        entry_set_dict[word].add(entry)
        weight_sum[entry] += weight
        #print("weight_sum", weight_sum)###

    ana_fil.close()
    for entry, ws in weight_sum.items():
        nw = len(word_set_dict[entry])
        weight_sum[entry] = (weight_sum[entry] / (nw)
                             if nw > 0 else float("inf"))
    #
    # Second pass: Delete inferior entry candidates i.e. any entry
    # whose all words are analysed by a better entry which even
    # analyses some additonal words of the corpus.
    #
    for entry in word_set_dict.keys():
        if redundant_entry(entry):
            delete_entry(entry)
    for entry in sorted(word_set_dict.keys(),
                        key=lambda en: len(en),
                        reverse=True):
        if ((len(word_set_dict[entry]) < args.minimum) and
            (weight_sum[entry] > 0)):
            delete_entry(entry)
            continue
        for word in word_set_dict[entry]:
            for e in entry_set_dict[word]:
                if ((word_set_dict[entry] < word_set_dict[e]) and
                    (weight_sum[entry] > 0)):
                    delete_entry(entry)
                    print("deleting", entry, "which is inferior to", e)###
                    break # the innermost loop
                if (weight_sum[entry] == 0) and (weight_sum[e] > 0):
                    word_set_dict[e].discard(word)
            else:
                continue # the middle loop
            break # the middle loop
    #
    # Third pass: Select best candidate for non-compound entries
    #
    for entry, w_set in word_set_dict.items():
        words_str = " ".join(sorted(w_set))
        entriesofwords[words_str].add(entry)

    for words_str, ent_set in entriesofwords.items():
        best_weight = min(weight_sum[ent] for ent in ent_set)
        for ent in ent_set:
            w = weight_sum[ent]
            if ('_' not in ent) and w > best_weight + args.beam:
                print("entry", ent, "with weight", w, "for", words_str,
                      "deleted, best was" , best_weight)###
                delete_entry(ent)

    single_entry_set = set()
    for entry in word_set_dict.keys():
        if not '_' in entry:
            single_entry_set.add(entry)
    #
    # Fourth pass: Select the best entry candidate with the smallest
    # weight out of compounds competing of the same set of words with
    # a penalty for compounds where the second part does not occur as
    # a single entry
    #

    for entry in weight_sum.keys():
        if '_' in entry:
            head, uc, tail = entry.partition('_')
            if uc and tail not in single_entry_set:
                weight_sum[entry] += 20 + args.beam
        
    for words_str, ent_set in entriesofwords.items():
        # print(words_str) ###
        best_weight = min(weight_sum[ent] for ent in ent_set)
        for ent in ent_set:
            w = weight_sum[ent]
            if w > best_weight + args.beam:
                print("entry", ent, "with weight", w, "for", words_str,
                      "deleted, best was" , best_weight)###
                delete_entry(ent)

    #
    # Fifth pass: Select most likely entries first and remove their
    # words from the entries coming later in the queue
    #
    if not word_set_dict:
        return
    sz = max([len(word_set_dict) for entry, word_set_dict
              in word_set_dict.items()])
    #print("largest set of word_set_dict", sz)

    delta = args.delta
    while sz > args.minimum:
        del_ent_lst = []
        for entry in word_set_dict:
            #print(sz, entry, word_set_dict[entry])###
            lgt = len(word_set_dict[entry])
            if lgt < args.minimum:
                del_ent_lst.append(entry)
                continue
            wght = weight_sum[entry]
            if (entry in word_set_dict and
                len(word_set_dict[entry]) >= sz - delta):
                print("{} ; ! {:.2f} {}".
                      format(entry,
                             wght,
                             " ".join(sorted(list(word_set_dict[entry])))))
                delete_all_words(entry)
                del_ent_lst.append(entry)
        for ent in del_ent_lst:
            del word_set_dict[ent]
        sz = sz - delta
    return

if __name__ == "__main__":
    main()
    
