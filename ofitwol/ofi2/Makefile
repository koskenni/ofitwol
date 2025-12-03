.SUFFIXES :
.INTERMEDIATE :
.PHONY=build analyse 

ID=sktp
MODE=mphon
ANALYSER=ofi$(MODE).ofst
RULEVAR=../rules/rules-var.fst
RULENORM=../rules/rules-norm.fst
AFF=analy
DATA=../../data

LEX=lexic-s.lexc lexic-a.lexc lexic-v.lexc lexic-p.lexc \
    lexic-special.lexc lexic-n.lexc

LEXM=$(LEX) lexic-r.lexc lexic-firstpart.lexc endings.lexc

LEXE=$(LEX) lexic-r.lexc lexic-firstpart.lexc endings.lexc

#LEXG=guess-s.lexc guess-a.lexc guess-v.lexc lexic-firstpart.lexc \
#     lexic-special.lexc lexic-p.lexc lexic-r.lexc
#LEXG=guess-s.lexc guess-a.lexc lexic-r.lexc
LEXG=guess-s.lexc guess-a.lexc guess-v.lexc \
      lexic-firstpart.lexc endings.lexc \
      lexic-r.lexc lexic-special.lexc lexic-n.lexc lexic-p.lexc
# Append the following, if you want to include all noun, adjective and
# verb entries in addition to the guessing patterns

#     lexic-a.lexc lexic-v.lexc lexic-s.lexc

ANALYSES=$(ID)-corpus-$(MODE).big.analyses

build : $(ANALYSER)

ofimphon : ofimphon.ofst 

guesser : ofiguess.ofst

analyse : $(ANALYSES)

rejected-guesses : $(ID)-rejected-guessed.entries

ofitwol.ofst : ofimphon.fst $(RULENORM) bound-remove.fst # Makefile
	hfst-project -p out -i $< -o ofimphon-out.fst
	hfst-compose-intersect -1 ofimphon-out.fst \
			       -2 $(RULENORM) -o ofitwol-tmp.fst
	hfst-compose -1 ofitwol-tmp.fst -2 delete.fst |\
	hfst-compose -2 bound-remove.fst -o ofitwol-aux.fst
	hfst-compose -1 ofimphon.fst -2 ofitwol-aux.fst -o ofitwol-cps.fst
	hfst-minimize -i ofitwol-cps.fst -o ofitwol.fst
	hfst-fst2fst -w -i ofitwol.fst -o $@

ofimphon.fst : mphon-lex.fst $(RULEVAR) bound-remove.fst delete.fst # Makefile
	hfst-compose-intersect -a -1 $< -2 $(RULEVAR) |\
	hfst-minimize |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize > ofimphon.fst

ofimphon.ofst : ofimphon.fst
	hfst-compose -1 ofimphon.fst -2 bound-remove.fst |\
	hfst-fst2fst -w -o $@

ofimphonemic.fst : mphon-lex-out.fst $(RULEVAR) delete.fst # Makefile
	hfst-compose-intersect -a -1 $< -2 $(RULEVAR) |\
	hfst-minimize |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o $@

ofimphonemic.ofst : ofimphonemic.fst
	hfst-fst2fst -w -i $< -o $@

ofientgues.ofst : ofientry.fst ofiguess.fst
	hfst-union -1 ofientry.fst -2 ofiguess.fst -o ofientgues.fst
	hfst-fst2fst -w -i ofientgues.fst -o $@

ofiguess.ofst : guess-lex.fst cleanlex.fst $(RULEVAR) delete.fst #Makefile
	hfst-compose-intersect -a -1 $< -2 $(RULEVAR) |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o guess.fst
	hfst-fst2fst -i guess.fst -w -o guess.ofst
	hfst-compose -1 guess.fst -2 cleanlex.fst |\
	hfst-minimize -o ofiguess.fst
	hfst-fst2fst -w -i ofiguess.fst -o $@

ofientry.ofst : entry-lex.fst $(RULEVAR) delete.fst # Makefile
	hfst-compose-intersect -a -1 $< -2 $(RULEVAR) |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o ofientry.fst
	hfst-fst2fst -w -i ofientry.fst -o $@

mphon-lex-out.fst: mphon-lex.fst
	hfst-project -i $< -o $@ -p output

mphon-lex.fst : root-mphon.lexc $(LEXM) # Makefile
	hfst-lexc -E -f openfst-tropical -o $@ $< $(LEXM)

guess-lex.fst : root-guess.lexc $(LEXG) # Makefile
	hfst-lexc -E -f openfst-tropical -o $@ $< $(LEXG)
	python3 cleanlex.py < $@ > cleanlex.fst

entry-lex.fst : root-entry.lexc $(LEXE) # Makefile
	hfst-lexc -E -f openfst-tropical -o $@ $< $(LEXE)

root-mphon.lexc : ofi-root-mphon.csv root2lexc.py # Makefile
	python3 root2lexc.py  < $< > $@

root-entry.lexc : ofi-root-entry.csv root2lexc.py # Makefile
	python3 root2lexc.py -e  < $< > $@

root-guess.lexc : root-guess.csv root2lexc.py # Makefile
	python3 root2lexc.py -e  < $< > $@

endings.lexc : ofi-endings.csv endings2lexc.py # Makefile
	python3 endings2lexc.py -z < $< > $@

guess-s.lexc : guess-s.entries guess-def.entries entries2lexc.py # Makefile
	python3 entries2lexc.py -p -i guess-def.entries $< > $@

guess-a.lexc : guess-a.entries guess-def.entries entries2lexc.py # Makefile
	python3 entries2lexc.py -p -i guess-def.entries $< > $@

guess-v.lexc : guess-v.entries guess-def.entries entries2lexc.py # Makefile
	python3 entries2lexc.py -p -i guess-def.entries $< > $@

lexic-firstpart.lexc : lexic-firstpart.words entries2lexc.py # Makefile
	python3 entries2lexc.py -n FirstPart -c More -i $< > $@

lexic-r.lexc : lexic-r.entries entries2lexc.py
	python3 entries2lexc.py -c End -i $< > $@

$(LEX) : lexic-%.lexc : lexic-%.entries entries2lexc.py
	python3 entries2lexc.py -i $< > $@

$(ANALYSES) : $(DATA)/$(ID)-corpus.words $(ANALYSER)
	hfst-lookup -b 15 -i $(ANALYSER) -I $< | \
		egrep '..' > $@

delete.fst :
	echo "Ø -> 0" | hfst-regexp2fst -o $@

#bound-intro.fst : Makefile
#	echo '0 -> %{§%} || \§ _ [%+N | %+A | %+V | %+P | %+PRON | %+NUM]' | hfst-regexp2fst -o $@

bound-remove.fst : Makefile
	echo '[%{§%}+ | § -> 0 || _ [%+N | %+A | %+V | %+P | %+PRON | %+NUM]] .o. [%{§%} | § -> %_]' | hfst-regexp2fst -o $@

guesses : sktp-corpus-base.big.analyses
	egrep 'inf$$' sktp-corpus-base.big.analyses | \
	cut -f 1 > sktp-rejected.big.words
	hfst-lookup -i ofiguess.ofst -I sktp-rejected.big.words -o sktp-guessed.big.analyses
	python3 ../guessfromwords.py < sktp-guessed.big.analyses > sktp-guessed.big.entries

$(ID)-rejected.words : ofientry.ofst
	hfst-lookup -i $< -I $(DATA)/$(ID)-corpus.words | egrep 'inf$$' | cut -f 1 | sort > $@

$(ID)-rejected.analyses : $(ID)-rejected.words ofiguess.ofst
	hfst-lookup -i ofiguess.ofst -I $< -o $@

$(ID)-rejected-guessed.entries : $(ID)-rejected.analyses ../guessfromwords.py
	 python3 ../guessfromwords.py -d 1 -b 10 -m 3 -a $< > $@

$(ID)-compo-by-secd.analyses : $(ANALYSES)
	cut -f 2 $< | \
	egrep '§' | \
	cut -d ';' -f 1 | \
	sort -k 2 -t '}' | \
	tr '§' ' ' | \
	uniq -c > $@

clean:
	rm -f *.fst
	rm -f *.ofst
	rm -f *.lexc

distclean : clean 
	rm -f $(ID)-corpus.big.analyses


