 Mar 8, 2010
Westergaard/readme4.txt
This continues the work described in 
  readme3.txt, readme2.txt,readme.txt and readme-orig.txt.

* whit directory
 This contains material from Lexical/Funderburk/Whitney.
 See the 'readme.txt' file there for the origin of
 'roots-ids-seq.xml'.

* whit/whitroots0.txt, addprep.txt, whitroots.txt
 sh redo.sh
 whitroots0.txt contains a line for each of the <root> elements in
 roots-ids-seq.xml.
 a. Each <root> element has a 'form' attribute; the value of the form
 attribute has one of two similar forms:
 - the 'representative form of the root' (see Whitney text preface, p. xii)
   represented in SLP1 transliteration.
 - the 'representative form of the root' with a digit suffix (1,2, ...).
   For example, 'gf1' represents a first form of 'gf' and 'gf2', a second:
   <root form="gf1" gloss="sing" id="396" seq="0204" page="38">
   <root form="gf2" gloss="swallow" id="397" seq="0205" page="38,39">

  The spelling of the root is stated to be consistent with that in 
  Whitney's grammar; Whitney specifically mentions certain differences 
  in spelling from Boehtlink-Roth (e.g., 'kf' instead of 'kar', 'kfp' 
  instead of 'krap').  

 b. Some root entries are entirely referential.  These are indicated in
  roots-ids-seq.xml by the presence of a '<see>form</see>' element on the
  line following the <root> element.  For example:
  <root form="gir" id="549" seq="0191" page="36">
  <see>gf2</see>
  </root>

 c. Each <root> element has a 'seq' attribute, whose value, as well as the 
  value of the 'form' attribute, uniquely identifies the particular root 
  element.  The 'seq' element value is a 4-digit, 0-filled integer,
  generally representing the order of the root in the text;  there are a 
  few exceptions to this semantics (e.g., 'uz' and  some 'see' roots).
 d. Each root element (except those with a 'see') has a 'gloss' attribute,
    which gives, usu. in English, a brief definition.
 e. Some root elements have present-system 'class' information, formatted 
  on separate lines, for instance 
  <form class="1" morphid="2sm pre">akzase</form>
 f. Each root element has a 'page' attribute'.

 There is a line in whitroot.txt for each root element in roots-ids-seq.xml.
 This line consists of (7) tab-delimited fields:
 - seq:  the value of the 'seq' attribute of the root
 - form: value of the 'form' attribute
 - key:  value of the 'form' attribute, with any numerical suffixes removed.
   NOTE: 2010-03-17. The value of 'form' and 'key' are adjusted to replace
         'N[Szsh]' by 'M$1'. This affects 17 records:
   aNh => aMh, aNS => aMS, daNS => daMS, daNs => daMs, dfNh => dfMh
   DvaNs => DvaMs, naNS => naMS, niNs => niMs, baNh => baMh, bfNh => bfMh
   BraNS => BraMS, maNh => maMh, raNh => raMh, vfNh => vfMh, SaNs => SaMs
   sraNs => sraMs

 - page: value of the 'page' attribute.
 - gloss: value of the 'gloss' attribute if present; if absent, 'NOG'.
    Roots for which no gloss is present have the value 'NOG' for the gloss;
    There are 205 such NOG root elements. All but 20 of these are
    referential.  These 20 (gloss=NOG, see=NOS; for instance, iw, heW) are
    generally remarked by W. as being 'doubtful' for one reason or another.
 - see: the value of the 'see' element if present, else 'NOS'.
    185 of the root elements are marked as 'NOS'.  
    NOTE: 2010-03-17
    For those with a 'see' element, the value of the see element is of form
     'root,status', where status is 'YES' (154 roots) if the 
     'comma="yes"' attrib of <see> is present,
      and status is 'NO' (31 records) otherwise.
 - classes: a comma-separated list of the values of the class attributes
    present in form elements in the root, or, else 'NOC' (NOTE: Only the
    class attributes in the 'present' groups are collected; class attributes
    elsewhere (e.g. aorist) are ignored.)
    240 roots have multiple classes.
    340 roots have NOC; 159 of these are non-referential (e.g., see='NOS')

* whit/whit-mw.txt
  (also computed by redo.sh)
  NOTE: This is analogous to mdp/norm-mw.txt, with whitney roots and
     sequence numbers in place of mdp roots and msids.

  This uses whitroots0.txt and mwverb/mwroots1.txt to construct 
  in whit-mw.txt a list of root names with the associated list of
  whitney sequence numbers and mw L numbers.
  NOWHIT indicates a root doesn't appear in whitroots,
  NOMW indicates a root doesn't appear in mwroots1.
  Samples:
aMS NOWHIT;9
aNg 0004;1492
aNS 0005;NOMW
aS 0023,0024;19412,19416

 addprep.txt is a manually constructed file of what could have been
  synonyms in Whitney.  These were constructed during the process of
  trying to match Whitney with MW.

 whitroots.txt  contains all the records of whitroots0.txt, along
 with synthetic records constructed from the data in addprep.txt
Statistics:
1017 lines , with 933 distinct roots, from whitroots0.txt
1690 lines from ../mwverb/mwroots1.txt
29 lines from addprep.txt
wrote 1046 lines to whitroots.txt
1046 lines , with 959 distinct roots, from whitroots.txt
1690 lines from ../mwverb/mwroots1.txt
1859 records written to file whit-mw.txt
900 records have no whit info
169  records have no mw info

* whit/sense/def_init0.txt, whit_def_init.txt
 sh def_init0.sh
 This constructs def_init0.txt. Samples:
423,0002	to reach	!=	attain
423,0002	to pass through, pervade, embrace	!=	attain
423,0002	to accumulate	!=	attain
423,0003	to reach	!=	mutilate
423,0003	to pass through, pervade, embrace	!=	mutilate
423,0003	to accumulate	!=	mutilate

The first field has all L,seq pairings implicit in whit-mw.txt; for this 
 example: akz 0002,0003;423  
For each such pairing, the whitney definition ('attain' for 0002) is
 compared to each of the MW definitions 
 'to reach OR to pass through, pervade, embrace OR to accumulate'
The comparison status is initially set to '!=' meaning a non-match.

A subjective reset of the comparison status was then done, the result
being in the file 'whit_def_init.txt'.

* whit/sense/whit_sensemap1.txt
 sh redo.sh
 whit_def_init.txt was examined for all distinct definition pairs (the
  L,seq information being ignored).
  The results are put into file whit_sensemap1.txt, for instance
attain	==	to reach
attain	!=	to pass through, pervade, embrace
attain	==	to accumulate


* whit/select3 (superceded)
 sh redo.sh

 match records in whitroots with MW data on the basis of:
  key
  class
  def
 output the results in various files:
1017 lines from whitroots0.txt
575 lines generated 581 lines in whit-mw-match.txt
135 lines generated 156 lines in whit-mw-nomatch.txt
50 lines generated 56 lines in whit-mw-NOG.txt
70 lines generated 73 lines in whit-mw-NOC.txt
63 lines generated 63 lines in whit-mw-NOC-match.txt
124 lines generated 124 lines in whit-mw-NOMW.txt
1198 lines written to whit-mw-all.txt

Then, generate an html display for all these files

* whit/select4 (superceded)
...
* programming note:
  The material in select5 depends on various data sources. When one
  of these sources changes, various updates need to be made of derived
  sources. This note indicates the steps to take.
- when Whitney/roots-ids-seq.xml is changed, re-verify the xml:
  xmllint --noout --valid roots-ids.xml
  Also, document the changes in Whitney/readme.txt
- When either roots-ids-seq.xml changes or whit/addprep.txt changes,
  in whit: sh redo.sh
  in whit/sense: sh redo.sh
- When any of the inputs in mwverb/verb change,
  in mwverb/verb: sh redo.sh
  in mwverb: sh redo.sh
  in mwverb/sense: sh redo.sh
- in mwtab1: sh redo.sh
- in whit/select5:
  sh redo.sh
   There may be a need to modify whitney-mw definition matches in
   whit/sense/whit_def_init.txt; then redo.sh
   There may be a need to redo whit/sense/redo.sh
   

* whit/select5 (1st run)
 sh redo.sh
227 records adjusted with seestatus='YES'
1061 lines from whitroots.txt generate 1264 lines in prep.txt
835 groups found
546 groups of length 1
198 groups of length 2
 61 groups of length 3
 17 groups of length 4
  9 groups of length 5
  3 groups of length 6
  1 groups of length 8
466 matching groups with 1 element written to nosyn-match.txt
80 non-matching groups with 1 element written to nosyn-nomatch.txt
261 matching groups with > 1 element (658 lines) written to syn-match.txt
28 non-matching groups with > 1 element (60 lines) written to syn-nomatch.txt
201 records adjusted with seestatus='YES'
1264 records read from prep.txt
outarr has 1264 entries
1124 records ok 
201 records adjusted with seestatus='YES'
466 records read from nosyn-match.txt
outarr has 466 entries
466 records ok 
201 records adjusted with seestatus='YES'
658 records read from syn-match.txt
outarr has 658 entries
658 records ok 
201 records adjusted with seestatus='YES'
80 records read from nosyn-nomatch.txt
outarr has 80 entries
0 records ok 
201 records adjusted with seestatus='YES'
60 records read from syn-nomatch.txt
outarr has 60 entries
0 records ok 
* whit/select5 (2nd run)
 sh redo.sh
231 records adjusted with seestatus='YES'
1067 lines from whitroots.txt generate 1274 lines in prep.txt
837 groups found
545 groups of length 1
196 groups of length 2
 66 groups of length 3
 17 groups of length 4
  9 groups of length 5
  3 groups of length 6
  1 groups of length 8
468 matching groups with 1 element written to nosyn-match.txt
77 non-matching groups with 1 element written to nosyn-nomatch.txt
271 matching groups with > 1 element (681 lines) written to syn-match.txt
21 non-matching groups with > 1 element (48 lines) written to syn-nomatch.txt
205 records adjusted with seestatus='YES'
1274 records read from prep.txt
outarr has 1274 entries
1149 records ok 
205 records adjusted with seestatus='YES'
468 records read from nosyn-match.txt
outarr has 468 entries
468 records ok 
205 records adjusted with seestatus='YES'
681 records read from syn-match.txt
outarr has 681 entries
681 records ok 
205 records adjusted with seestatus='YES'
77 records read from nosyn-nomatch.txt
outarr has 77 entries
0 records ok 
205 records adjusted with seestatus='YES'
48 records read from syn-nomatch.txt
outarr has 48 entries
0 records ok 

April 1, 2010 (ejf local computer)
* whit/select6
C:/php/php.exe prep.php
231 records adjusted with seestatus='YES'
1067 lines from whitroots.txt generate 1274 lines in prep.txt
837 groups found
545 groups of length 1
196 groups of length 2
 66 groups of length 3
 17 groups of length 4
  9 groups of length 5
  3 groups of length 6
  1 groups of length 8
468 matching groups with 1 element written to nosyn-match.txt
77 non-matching groups with 1 element written to nosyn-nomatch.txt
272 matching groups with > 1 element (681 lines) written to syn-match.txt
20 non-matching groups with > 1 element (48 lines) written to syn-nomatch.txt
-----------
770 matching records written to file prep_match.txt
382 non-matching records written to file prep_nomatch_known.txt
122 non-matching records written to file prep_nomatch_prob.txt

* April 2, 2010  select6/
 php finalmatch.php
C:/php/php.exe finalmatch.php
 constructs 3 files:
 827 lines in match.txt
 402 lines in nomatch_known.txt
  45 lines in nomatch_prob.txt
----
1274 lines (matches prep.txt)

 796 whitney groups in match.txt
  41 whitney groups in nomatch_prob.txt
 ---
 837 whitney groups (matches prep.txt)

122 lines read from prep_nomatch_prob.txt
770 lines read from prep_match.txt
17 lines read from notes_match_group.txt
40 lines read from notes_match_nogrp.txt
827 lines written to match.txt
--------------------
382 lines read from prep_nomatch_known.txt
20 lines read from notes_nomatch_group_known.txt
402 lines written to nomatch_known.txt
--------------------
8 lines read from notes_nomatch_group_prob.txt
37 lines read from notes_nomatch_nogrp.txt
45 lines written to nomatch_prob.txt
------------------
0 unused preps

* match.html,  nomatch_known.html, nomatch_prob.html

 disp1.bat
  creates the html files from the .txt files.  The display
  is basically the same as for disp.bat, except that a comment 
  column is added.
  The comment currently just shows for those that were 'manually' forced
  to match.


April 7, 2010
* whit/select7
 php whitgenuine.php
31 duplicate whitkeys in ../select6/mwwhitmap.xml
827 records whitney matches
619 records written to mwwhitmap-gen.txt
208 records written to mwwhitmap-art.txt
136 records written to mwgenuine_notwhit.txt
963 records written to whitmatch-or-genuine.txt

* whit/select7
 This is an attempt to correspond roots with prefixes 
  with the whitney roots. There is also information regarding those
  roots which MW marks as 'genuine'.

c:/php/php.exe mwkeyspfx.php
6153 records read from verb-prep4-gati2-complete-chk.out
715 distinct roots found
963 records read from whitmatch-or-genuine.txt
890 distinct roots found
There are 963 distinct roots from both sources
642 roots are preroots occurring in wg
73 roots are preroots not occurring in wg
248 roots are not preroots but occur in wg
No mw data found for aMs
No mw data found for art
No mw data found for arz
No mw data found for iD
No mw data found for in
No mw data found for und
No mw data found for kFt
No mw data found for kzvid
No mw data found for gulP
No mw data found for granT
No mw data found for grAm
No mw data found for GAtaya
No mw data found for Cand
No mw data found for jaMh
No mw data found for truq
No mw data found for damB
No mw data found for dIdi
No mw data found for DIr
No mw data found for Du
No mw data found for DUp
No mw data found for DmA
No mw data found for paYcaya
No mw data found for parA-i
No mw data found for baD
No mw data found for bfMh
No mw data found for BUzati
No mw data found for maTAy
No mw data found for manT
No mw data found for mUtr
No mw data found for mUrC
No mw data found for mfkz
No mw data found for mlup
No mw data found for luRW
No mw data found for vat
No mw data found for vfMh
No mw data found for vfh
No mw data found for vyUh
No mw data found for SAntv
No mw data found for Scyut
No mw data found for SvaYc
No mw data found for skaB
No mw data found for skf
No mw data found for skF
No mw data found for stF
No mw data found for sramB
No mw data found for svaYj
No mw data found for svAra
No mw data found for hel
1037 records (963 roots) written to file whitmatch-or-genuine-preverb.txt
671 records (603 roots) written to file whit-preverb.txt
48 roots (with preverbs but not in mwwhit) had no mw data!

NOTE1: 
  there are 28 instances of NOWHIT in whit-preverb.txt.
  These seem to occur in cases where there are multiple variants
  of the roots in MW, and not all of the variants were involved in
  matching with whitney.

NOTE2:
 'kal' illustrates an interesting case.  Here, there is are three
  homophones listed in MW, but the first is not present in 
  whit-preverb.  This is puzzling.

NOTE3: 111 lines in whit-preverb are marked by MW as artificial.
  Possibly, this suggests some arbitrariness in MW's marking; see,
  for instance, 'KyA', which is shown to occur in 28 different prefixed
  forms, or 'ci' in 28 prefixed forms. If one is trying to determine
  'important' roots, surely 'KyA' qualifies.  So, whereas I had hoped
  'genuine' roots were 'important', this does not seem quite the 
  distinction MW is making.

* select7/whit_mw.txt, mw_whit.txt
c:/php/php.exe mwwhitkeys.php
31 duplicate whitkeys in ../select6/mwwhitmap.xml
56 duplicate mwkeys in ../select6/mwwhitmap.xml
796 records written to whit_mw.txt
771 records written to mw_whit.txt

Each file consists of lines with 2 tab-separated fields,
  a 'key' and a 'value'
In whit_mw.txt, there is a line for each distinct whitney key;
  The 'key' is the whitney key, the 'value' is a comma-delimited 
  list of associated mw keys (without duplicates).
In mw_whit.txt, there is a line for each distinct mw key;
  The 'key' is the mw key, the 'value' is a comma-delimited list
  of associated whitney keys (without duplicates).

