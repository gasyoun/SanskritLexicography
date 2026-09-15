Feb 1, 2010
Westergaard/readme2.txt
This continues the work described in readme.txt and readme-orig.txt.
* Note of Feb 16, 2010.
  I currently find the method of assigning the 'inferred="yes"' attribute to certain
  <wsid> elements suspect.  The root 'rah' in Dha1tupe.txt supports this lack of confidence.
  In Dha1tupe.txt it occurs 5 times:
<r t="g"><key1>rah</key1><ls>Dha1tup._xvii_,_82<wsid>17.82</wsid></ls><L>175925</L><v>1,p;10,p</v></r>
<r t="g"><key1>rah</key1><ls>Dha1tup.<wsid inferred="yes">17.82</wsid></ls><L>175925</L><v>1,p;10,p</v></r>
<r t="g"><key1>rah</key1><ls>Dha1tup.<wsid inferred="yes">17.83</wsid></ls><L>175925</L><v>1,p;10,p</v></r>
<r t="g"><key1>rah</key1><ls>Dha1tup.<wsid inferred="yes">32.83</wsid></ls><L>175925</L><v>1,p;10,p</v></r>
<r t="g"><key1>rah</key1><ls>Dha1tup.<wsid inferred="yes">33.123</wsid></ls><L>175925</L><v>1,p;10,p</v></r>

  There is, in MW record, only 1 incomplete reference, yet, somehow the process of inference added 4
  addition wsids!  Surely this is not right.
Thus, I amend the process.  For the sake of possibly revisiting this inference process at a later time,
the original work is saved in 'mwtab-version1' directory, and the corresponding notes are saved in
'readme2-version1.txt'.

* mwroots
In the various Dha1tupx files in mwtab, starting with Dha1tup.txt (extracted from MW),
some MW entries containing a Dha1tupada reference are not in fact records for roots.
For instance, 
<key1>uBayatoBAza</key1><ls>Dha1tup._xxx</ls><L>37131</L>
  In this case, section 30 of Westergaard mentions {sd svaritetaH}; the svarita marker accent
  is tantamount to an indication of {sd uBayapadin}, so perhaps MW referenced section 30 as
  an example of {sd uBayatoBAza}.  In any case, the MW record is not a root.
<key1>kusmaya</key1><ls>Dha1tup._xxxiii_,_37</ls><L>51228</L>
  Here 33.37 is {sd kusma nAmno vA}, indicating that {sd kusma} is a {sd nAmaDAtu}; and
  MW marks {sd kusmaya} as <ab>Nom.</ab>.  
Some other records are for prefixed roots, e.g., 
<key1>upadI</key1><ls>Dha1tup._xxvi_,_25</ls><L>34734</L>
in this case, root 26.25 is  'dI', so MW is pointing to

Another situation is exemplified by
<key1>kiw</key1><ls>Dha1tup.</ls><L>50237</L>
 Here, there is no specific root specified in wdp, but 
  'kiwa' is wsid=9.32 (sense = {sd gatO}) which corresponds to one of MW meanings
  and 9.14 (sense = {sd trAse}) which corresponds to another one of MW meanings,
  so it seems reasonable that this MW root should correspond to these two wdp elements.

The above observations suggest it would be useful to consider just those elements of Dha1tup.txt
which correspond to (non-prefixed) roots in MW.


* mwtab/Dha1tupc-inc.txt
 From readme-orig.txt, 
   Dha1tupc.txt along with Dha1tupb-prob-only.txt and Dha1tupb-prob-section.txt comprise
   all the original records of Dha1tup.txt.
   There are 1619 records in Dha1tupc.txt. All these have a wsid translated from the <ls> element.
 

 Dha1tupc-inc.txt is just the merging of 
   Dha1tupb-prob-only.txt and Dha1tupb-prob-section.txt.  It contains the cases where there
   is incompleteness in the Dha1tup references of MW.
   This merging is done by the shell command:
     cat Dha1tupb-prob-only.txt Dha1tupb-prob-section.txt > Dha1tupc-inc.txt
   Dha1tupc-inc.txt has 221 lines.

   Thus, Dha1tupc.txt along with Dha1tupc-inc.txt comprise all the original records of Dha1tup.txt;
   the Westergaard references are complete in Dha1tupc.txt and 'incomplete' in Dha1tupc-inc.txt.

   Note of 2010-02-02:
    Two records from the 'section' file have two sections.
    in Dha1tupc-inc.txt these are split into two records.
    So, after this, there are 223 lines in Dha1tupc-inc.txt.

* mwtab/Dha1tupd.txt
 sh dpd.sh
NOTE: April 27, 2010.  This formed the basis of mwtab1/Dha1tupd.txt,
   but the latter should now be viewed as independent of mwtab/Dha1tupd.txt.

  Remove records not corresponding to MW roots (by using mwverb/mwroots.txt),
  in both Dha1tupc.txt.  
   1612 Dha1tupc.txt  (not counting 7 duplicate lines)
      1523 Dha1tupd.txt  present in mwroots.  the 'r' and 'v' elements are added 
                         from mwroots to the data in Dha1tupc
        89 Dha1tupc-nonroot.txt  not present in mwroots

  The records in Dha1tupd.txt contain complete Westergaard references and are known to occur
    in MW records which have been marked as roots.
    Example:
<r t="g"><key1>iNg</key1><ls>Dha1tup._v_,_46<wsid>5.46</wsid></ls><L>28638</L><v>1,p;a;p</v></r>

  TODO: What is the purpose of the  Dha1tup references in  the non-root records
         of Dha1tupc-nonroot.txt? 


* comparing key1 to normroot(overview)
 There is a way to match mdp with mw that does not involve wdp: 
 Correspond 
  'key1' field from 'mw' to the 
  'normalized root' from mdp (if <root> elt has a 'normal' attribute (230 cases), use the
       value of the 'normal' attribute; otherwise, use the text contents of the <root> elt.)
       A good file to use is mdp/mdp.xml.
 Typically, one expects a given value of 'key1' to correspond to 1 or more mdp records.
 Also, due to the presence of 'homonyms' in mw, a given 'key1' (for a root) may have
  multiple records (values of <L>).
 Assuming a match between 'key1' and 'normroot', four possibilites might occur in terms of 
 multiplicites:
  a. one mw and one mdp:  This is the simplest case
  b. one mw and many mdp:  
  c. many mw and one mdp:  
  d. many mw and many mdp.

 There are also the cases 
  e. key1 corresponds to no normroot,
  f. normroot corresponds to no key1.

 In cases a-d, there is additional information in mw:
   <v> element in mwroots
   <def> The 'verbal' definition. Rarely, mw also gives a 'sense' as in dp.
  
   <v> could be used to correspond to class and pada from mdp.
   <def> could be compared to 'sense' from mdp or wdp.
 This additional information could be used to confirm the correspondences in a-d, and,
 in case 'c', to refine the correspondence between 'L' and 'msid' or 'wsid'.

* mdp/norm.txt
 sh norm.sh
 For each record in mdp.xml, compute the normalized root.
 For each normroot value so computed, write one record in norm.txt. This record has form:
 normroot sid1,sid2,...
 where sid1, etc are the sids of the records in mdp with the given normroot.
 Statistics:
 2282 lines in mdp.xml.
 2276 entries (the non-entries were xml-required lines, and two blank lines)
 All entries had a root element
  230 entries had a normal attribute of 'root', whose value was used as the 'norm'.

 1531 lines written to norm.txt
 Note: the records are written in Sanskrit alphabetical order.

* mdp/mdpnorm.xml
  This adds a 'norm' attribute to each relevant 'entry' element of mdp.xml,
  based upon  norm.txt.
  sh mdpnorm.sh
  Example:
  from mdp.xml:
<entry sid="01.001-01" id="0001" vp="2-47"><fullDAtu>BU</fullDAtu><lemma><root>BU</root></lemma><sense senses="sattA"><senseterm>sattAyAm</senseterm></sense></entry>
  from mdpnorm.xml:
<entry sid="01.001-01" id="0001" vp="2-47" norm="BU"><fullDAtu>BU</fullDAtu><lemma><root>BU</root></lemma><sense senses="sattA"><senseterm>sattAyAm</senseterm></sense></entry>



* mwtab/Dha1tupe.txt
 sh dpe_init.sh
 This concatenates Dha1tupd.txt (complete Westergaard root refs from MW),
 and Dha1tupd-additions.txt. 
 Currently, (2010-02-16) there are no additions, so Dha1tupd-additions.txt
 is empty. However, 
 and dpd-inc.txt (Westergaard root refs inferred as described above).
 Dha1tupe.txt has (+ 1523 0) = 1523 lines.
  Note: there is one 'blank' line at the bottom, an artifact of the catenation process.

* mwtab/dpe-classchk.log, Dha1tupe1.txt
  sh dpe-classchk.sh
In the records of Dha1tupe.txt, there are two independent sources of information 
  regarding class-numbers of the roots:
   a. The <v> element gathered directly from MW
   v. The <wsid> value, which implies the class according to the following table;
      (this table is derived from the section headings from wdp/WestergaardDhP1.xml (wdp1)):
   class  sections
    1      1-23
    2      24
    3      25
    4      26
    5      27
    6      28
    7      29
    8      30
    9      31
   10      32-35
   
  dpe-classchk determines if the class implied by each wsid is contained among those
  specified in <v>.
  Those which are inconsistent according to this test are written to dpe-classchk.txt;
     the class implied by wsid is appended to the line in an xml comment.
  Those which are consistent are written to Dha1tupe1.txt

 Statistics:
  1523 lines in Dha1tupe.txt.
  in 1427 of these, wsid class consistent with <v> classes (Dha1tupe1.txt)
  in 96 of these, wsid class NOT consistent with <v> classes (dpe-classchk.txt)

 TODO: What is the explanation for each of the 96 cases in dpe-classchk.txt?

* mwtab/Dha1tupe2.txt Dha1tupe2-msidchk.txt 
  dpe2-classchk.txt dpe2-classchk-msidchk.txt
 sh dpe-msidchk.sh
 This function assigns msid (using wdp/WestergaardDhP1.xml).
 When there is difficulty determining 'the' msid, the record is written
   to the '-msidchk' file.  Note that supplementary pAWAntara msids
   (such as with  06.060-01,01p) are ignored (e.g., ',01p' is stripped).
 Statistics:
1427 lines in Dha1tupe1.txt.
1335 had a unique msid-wsid correspondence (see Dha1tupe2.txt)
92 had some problem with msid (see Dha1tupe2-msidchk.txt)
  49 had no msid
  5 had multiple msid
  30 had incomplete msid
   8 had multiple wsid for msid
wsid multiple in wdp: 4.40 01.081-01 01.080-03,01.081-01
wsid multiple in wdp: 7.74 01.155-03 01.155-02,01.155-03
wsid multiple in wdp: 7.72 01.156-01 01.155-01,01.156-01
msid multiple in wdp: 01.282-13 11.35 11.30,11.35
msid multiple in wdp: 01.526-02 19.39 19.38,19.39
msid multiple in wdp: 01.639-01,02 22.14a 22.14,22.14a
96 lines in dpe-classchk.txt.
81 had a unique msid (see dpe2-classchk.txt)
15 had some problem with msid (see dpe2-classchk-msidchk.txt)
  13 had no msid
  0 had multiple msid
  2 had incomplete msid
  0 had multiple wsid for msid

So, in particular, Dha1tupe2.txt now has wsid, msid and the
 class implied by wsid is known to be compatible with class info encoded in
 the <v> element from MW.
Also, wsid is associated with no other msid, and msid is associated with
 no other wsid.

* mwtab/Dha1tupe3.txt
 sh dpe-keychk.sh

 The records in Dha1tupe2 have both a key1 field and a wsid field and an msid
 From the msid, there is a normroot (using mdp/norm.txt).
 In this check, we compare key1 with normroot.
 And, if key1 appears as one of the normalized roots, we check that
  msid appears as one of the msids associated with normroot in mdp/norm.txt.
 
Statistics:
1335 lines in Dha1tupe2.txt.
 865 had match of key1 with msid's normroot (see Dha1tupe3.txt)
470 had some problem (see Dha1tupe3-keychk.txt)
   in 304 cases, there was no normroot in norm.txt matching key1
   in 166 cases, there was a normroot matching key1,
      but the given msid was not among the normroot's sids

81 lines in dpe2-classchk.txt.
44 had match of key1 with msid's normroot (see dpe3-classchk.txt)
37 had some problem (see dpe3-classchk-keychk.txt)
   in 10 cases, there was no normroot in norm.txt matching key1
   in 27 cases, there was a normroot matching key1,
      but the given msid was not among the normroot's sids

To recapitulate, we started with 1523 records in Dha1tupe.txt;
these are records corresponding to MW records for roots, with one 
record for each fully-qualified Westergaard reference in the MW record.
In Dha1tupe1.txt, we put aside 96 records because the conjugation class
implied by the Westergaard reference is not mentioned in the MW record.
In Dha1tupe2.txt, we put aside an additional 92 records where, using data
from wdp/WestergaardDhP1.xml, there is some problem in associating the
wsid with a single msid (Madhaviya record).
In Dha1tupe3.txt, we put aside an additional 470 records where there
is some problem in associating the MW key1 root spelling with the
normalized root associated with msid.

In Dha1tupe3.txt, we are left with  865 cases where the association between MW and Madhaviya
is well-confirmed by a path through Westergaard.
As the next step, I would like to examine these cases on the basis of 'sense'.
The result of this is in match3/Dha1tupe3_sense.txt.
The next steps deal with getting 'good' sense data with which to do the comparison.

Feb 4, 2010
* mdp/sense/senselist.txt
 sh senselist.sh
 The entries of mdp/mdp.xml are read; all but two of the 2276 entries
 have a senses attribute of a sense element.
 Recall that the value of the sense attribute is a comma-space delimited
 list of sense-stems; compound structure in a sense-stem is indicated by the
 use of '-' and '=' characters.

 A list of the distinct senses is made (each with multiplicity of
 occurence); there are 719 distinct senses (total multiplicity 2748).
 Each sense is used to generate a final stem, by resolving the
 sandhis at the '-' and '=' (if any).  This is done by the program
 'jfunderburk/util/sandhi/sandhiTest.pl' with options 'CNS' (compound sandhi).

 The senselist.txt output file has 719 lines, each of which is a
  semicolon-separated list of three items, the original sense-value,
  the multiplicity of occurence of the sense-value, and the
  sense-value with sandhis resolved.
  Note: there are cases where the sense is not a single word (e.g.,
   where the sense value has a space).

* mdp/sense/senselist_entries.txt
 sh senselist_entries.sh
 The program reads mdp.xml, and looks for the senses attribute of the
  sense element in each field. The value of the senses attribute is
  a comma-separated list of sense stems.  The program accumulates a list
  of all sense stems and, for each sense stem, accumulates the list of sids
 (entry-identifiers) in which the sense stem occurs.
 senselist_entries.txt shows 719 lines for the distinct senses. 
  Each line has 2 fields,
  separated by a semicolon.  The first field is the sense, as it appears in
  the senses attribute value.  The second field contains a comma separated
  list of entry-sids where the sense occurs. 
 senselist_entries.log shows two entries for which no sense element occurs.
   TODO:  why no sense element for these?

 We now want to derive, for each sense stem, a 'definition' drawn from MW.
 The result of this appears in the file sensemw.txt, whose construction is
 described next. There are several independent inputs to sensemw.txt:
  senselista_entries.txt
  mwquery_dump.txt : a simplified dump of MW. This is the file used
     in the 'advanced search' for Monier Williams on Cologne website.
     It consists of two tab-delimited fields, 'key1' and 'definition'.
     (data for consecutive records of MW with same key1 are combined,
     being separated by ' :: '.

  senselista.txt  needed since not all sense stems are directly present
     as MW headwords. This can be due to differences between sense-stem
     spellings and MW headword spellings, and to absence of given stems
     as MW headwords.
  sensepart.txt   needed to 'select' from multiple MW definitions.  The
     aim of the selection is to find definitions that are comparable to
     the MW definitions of roots.

* mdp/sense/senselista.txt
  By means of sensemw (see below) it was discovered that about 160 of
  the sandhied-senses were not present as mw entries, nor were the
  compound-components available.
  This list was copied into file senselist.chg. 
  Manually, a fourth item was added to the lines of senselist.chg;
  This addition provides an alternate word (or compound) so that a 
  definition from mw is available.
  Then, using 'sh senselista.sh', the lines from senselist.chg replace
  the corresponding lines from senselist.txt, yielding
  senselista.txt.

  TODO: 
   - 'atisparSane' prob. should be 'atisparSana' in Madhaviya data.
   - There may be better alternate choices for some words in senselist.chg
     than the ones ejf chose.

* mdp/sense/sensemw.txt
  sh sensemw.sh
  Read the senselist.txt file, and find a definition for the sense using
  mwquery/mwquery_dump.txt.
  The 'sandhied' sense is used.
Statistics:
722 lines read from senselist.txt
556 of these had a definition in mwquery (see sensemw.txt)
165 of these had no definition(see sensemw.log)

Sample line:
a-darSana;5;adarSana; non-vision not seeing  ::  disregard neglect non-appearance latent condition disappearance  ::  invisible latent

sensemw.txt may be used as follows:
1. Consider the first record of mdp.xml, with sid="01.001-01" (root BU)
<entry sid="01.001-01" id="0001" vp="2-47"><fullDAtu>BU</fullDAtu><lemma><root>BU</root></lemma><sense senses="sattA"><senseterm>sattAyAm</senseterm></sense></entry>
2. Choose the (only) value of the 'senses' attribute of the 'sense' element,
   namely, 'sattA'
3. in sensemw.txt, choose the record whose first entry is 'sattA':
sattA;2;sattA;<def>existence being</def>

Thus, a  meaning for BU can be taken as
'in the sense of ' + 'existence being'

* discussion of sense stems (obscure)

  For instance, the two senses whose meaning I have not found are
vetinA tulya;1;vetinA tulya;
zasana;1;zasana;zasana
 Using senselist_entries, I see each occurs just once:
 vetinA tulya <-> 02.085-01
 zasana <-> 02.087-01p
 Using these as keys into mdp.xml, we retrieve the records:
 <entry sid="02.085-01" id="1246" vp="381"><fullDAtu>vevIN</fullDAtu><lemma><root>vevI</root><marker>N</marker></lemma><sense senses="vetinA tulya"><senseterm>vetinA tulye</senseterm></sense></entry>
<entry sid="02.087-01p" id="1247" vp="381-382" pA="1"><fullDAtu>sasa</fullDAtu><lemma><root normal="sas">zas</root><marker>a</marker></lemma><sense senses="zasana"><senseterm>zasane</senseterm></sense></entry>

Seeing that the normal root is 'sas' for
the second, and that 'sasa' is 'sleeping' is in MW, I changed the entry in
senselist.chg for zasana to 
zasana;1;zasana;sasa

The first one is still a mystery.  'tulya' is clear (compareable to),
and 'vetinA' is 3s of something, but I can't find the something; I tried
'vetin' and 'veti'.   Another possibility is a made-up compound 'vA + iti',
but this still doesn't make sense to me.
 TODO: what is 'vetinA'?


* mwverb/sense/root_mwquery_dump.txt
 Our aim is to construct root definitions to which the mdp sense definitions
 (from sensemw.txt and senselist_entries.txt) may be compared.
  The end result is 'rootsense.txt', a sample line of which is
<key1>aMS</key1><L>9</L><def><d>to divide , distribute</d></def>

 root_mwquery_dump.txt was constructed on ejf computer from MW database:

 C:/server2go/htdocs/sanskrit/init/init_root_mwquery.php.
 http://127.0.0.1:4001/sanskrit/init/init_verb_mwquery.php

 It contains entries only where '<vlex type="root"></vlex>' is found
  (1842 such).
 For these, it tries to use clauses marked by <to/> to generate
  definitions. These are present in 1661 of the 1842 cases.
  Otherwise, it creates a typical mwquery type of definition.
  For the <to/> clauses, the definitions are presented as a
  sequence of <d> elements. 
 There are 3 tab-delimited fields: L, key1, definition.
 NOTE: 2010-02-17. Added 'cull' as a root; it was not marked as
   a root.  Added manually to root_mwquery_dump.txt.  It was referenced
   by the definition of 'cuqq'.
  TODO: Alter things so this is an (artificial) root.

* mwverb/sense/root_mwquery_chg.txt, rootalt.txt
  This contains alternate definitions for many of the non-<to/> cases.
  These have 'to x', but not marked with <to/>
  TODO: Modify these records in MW database by inserting <to/> 

  rootalt.txt: 
  In the process of examining these, 80 new candidates were added to 
  rootalt.txt.  These are cases where the MW definition refers to 
  another different root. For instance,
  L=30535 (Uc) refers the reader to the 3rd homonym of 'vas' (L=188997);
     Thus, we use L=188997 for the definition of L=30535.
  A variant is:
  L=16336 (arpaya) which says 'Caus. of {sd f}'.  The phrase [Caus, to go]
     is inserted as the phrase to use for L=16336.

  Note: sh chgonce.sh 
    reads orig_root_mwquery_chg.txt, orig_rootalt.txt
          (these are copies of original mwquery_chg.txt and rootalt.txt)
    writes root_mwquery_chg.txt (70) and rootalt.txt (111 records, 
          80 of which are new and need to be manually adjusted.

  mwquery_chg.txt contains overrides to certain records of mwquery_dump.txt.

* mwverb/sense/root_mwquery_dumpa.txt
  sh roota.sh
  This combines root_mwquery_dump.txt and
  root_mwquery_chg.txt
  and outputs root_mwquery_dumpa.txt.
  The 'chg' records override the 'dump' records.

* mwverb/sense/rootsense.txt

  sh rootsense.sh

 Read mwroots.txt.  
 Use root_mwquery_dumpa.txt for definitions.
 A provision was made to install the definition for an alternate record
 number. The file rootalt.txt contains these pairings (two give explicit
 definitions (onomat.).  These occur when MW gives no definition, but
 provides a reference to another root.

Sample output lines:
1. alt not used
<key1>aMS</key1><L>9</L><def><d>to divide , distribute</d></def>
2. alt used - type 1
<key1>arpaya</key1><L>16336</L><def inferred="yes">[Caus, to go]</def>
3. alt used - type 2
<key1>uC</key1><L>30535</L><def inferred="yes" Lref="188997"><d>to love</d><d>to cut off</d><d>to accept , take</d><d>to offer</d><d>to kill</d></def>


 TODO: in case of {sd SvaW} (L=224192), the reference in MW is to
   2nd homonym of {sd SAT}, which doesn't exist.  This appears to be a
   typo, the correct reference being to {sd SaW}.
   Perhaps this should be put into the list of 'factual errors' in MW, and
   the correction made to online record.


* Example of comparing  mwverb/sense/rootsense.txt and mdp/sense/sensemw.txt.
sense 'sattA' of BU from sensemw.txt =
'in the sense of ' + 'existence being ' 

sense of BU from rootsense.txt =
<def><d>to become , be</d><d>to fall into a hundred pieces</d><d>to keep aloof.</d><d>to occur to the mind of any one</d><d>to fall to the share or become the property of , belong to</d><d>to be on the side of , assist </d><d>to serve for , tend or conduce to</d><d>to be occupied with or engaged in , devote one's self to </d><d>to thrive or prosper in</d><d>to be of consequence or useful</d><d>to fall , or get into , attain to , obtain</d><d>to obtain it</d><d>to cause to be or become , call into existence or life , originate , produce , cause , create</d><d>to cherish , foster , animate , enliven , refresh , encourage , promote , further</d><d>to addict or devote one's self to , practise</d><d>to subdue , control</d><d>to obtain</d><d>to manifest , exhibit , show , betray</d><d>to purify</d><d>to present to the mind , think about , consider , know , recognize as or take for </d><d>to mingle , mix , saturate , soak , perfume</d><d>to wish to cause to be </d><d>to strive to be quickly possessed</d><d>to want to get on , strive to prosper or succeed</d><d>to want to have , care for , strive after , esteem , honour</d><d>to want to take revenge</d><d>to be transformed into</d><d>to keep anything</d></def>

Are these two 'definitions' of BU the same?
A reader of English will say that the first rootsense meaning 
  'to become , be'
is similar in meaning to
  'in the sense of ' + 'existence being ' 
However, a programmatic comparison of these two English phrases is beyond
the scope of my programming tools. 


* match3/Dha1tupe3_sense.txt, dpe3_sense.log ,disp1.html, disp1-nonmatch.html (Feb 11, 2009)
 Note: sh redo.sh does both (a) and (b)
 (a) sh dpe3_sense.sh
 This provides a datatable showing the sensemw meaning and the rootsense 
 meaning for selected entries of mdp.xml.
 
 We use mwtab/Dha1tupe3.txt as the list.
 Each record has an L (MW record id) and an msid (mdp record id).
 We use 'L' to pull a root definition from mwverb/sense/rootsense.txt.
   In this run, only the first definition is used.
 We use msid to pull a collection of sense terms from mdp/sense/senselist_entries.txt,
   and then, for each of these senseterms, pull a definition from mdp/sense/sensemw.txt
 We also use a hand-picked list (nonmatch.txt) of records (key + L + sid) where observation
   suggests that the msid-definition does NOT match the MW defn from corresponding 'L'.
   Those not mentioned in nonmatch.txt have been judged, by a subjective examination,
   to be matches with respect to sense.
 We then  append the two sense information gathered to the Dha1tupe3 record.
   For matching records, the new record is written to Dha1tupe3_sense.txt (939 records)
   For non-matching records, the new record is written to dpe3_sense.log.
Statistics:
64 key/L/sid read from nonmatch.txt
865 records read from ../mwtab/Dha1tupe3.txt
801 matching records written to file Dha1tupe3_sense.txt
 64 non-matching records written to file dpe3_sense.log

 (b) sh disp1.sh  
 The two output files Dha1tupe3_sense.txt and  dpe3_sense.log are put into an html format
  to help reading.
 To summarize, the records in Dha1tupe3_sense.txt match in all the ways thus far considered:
   L matches wsid via Dha1tup reference in MW
   wsid class present in MW <v> element
   wsid matches clearly to msid
   msid normroot matches MW key1
   msid senses match MW root sense

* mwverb/mwroots1.txt
  sh mwroots1.txt
  This is constructed from mwroots.txt.
  Each line of mwroots1.txt has two space-separated fields:
   - key
   - comma-separated list of L-identifiers where the 'key' occurs.
Statistics:
1837 lines from mwroots.txt
1695 records written to file mwroots1.txt
5 records written to file mwroots1.log
file mwroots1.log:
1 1576   records where key1 occurs in only one MW record
2 100    key1 occurs in exactly two MW records
3 16     etc.
5 1
4 2

* mdp/norm-mw.txt
 sh norm-mw.sh

 Recall that norm.txt has, for each normalized-root in mdp, a line showing all the sid's 
  where the root occurs.
  normroot  sid1,....,sidn

 mwverb/mwroots1.txt is similar:
  key1  L1,L2,...Ln

 norm-mw.txt merges these two files, matching on the first field (normroot vs. key1)
  key1  sid1,...,sidn;L1,...,Ln
 
Statistics:
1531 lines from norm.txt
1693 lines from ../mwverb/mwroots1.txt
2059 records written to file norm-mw.txt
528 records have no mdp info
366  records have no mw info

The records are written in Sanskrit-alphabetical order.
The various cases of records are illustrated by the first 4 lines:
aMS NOMDP;9
aMsa 10.304-01;NOMW
aMh NOMDP;107
ak 01.071-01,01.523-01;134


* match3a/aroots-mw.html, aroots.txt, etc.
 Background observation:  It is known that some of the class 10 roots in mdp
   have normroot ending in 'a'.  However, it is believed that MW never represents
   class 10 roots with a headword ending in 'a'.  Thus, given an 'msid' with normroot 'xa' where
   and an 'L' for MW root 'x', it might be that 'msid' and 'L' correspond.
 The conclusion of this analysis will be that the correspondence is reasonable for
   records in chk2.txt and in chk4_sense.txt (currently with 35 and 11 records).

 130 aroots.txt roots in norm-mw.txt which end in 'a'
      (grep 'a ' ../mdp/norm-mw.txt > aroots.txt)
  33 aroots-mw.txt   records in aroots.txt which have MW data
     aroots-mw.html  A display of the MW info for aroots-mw.txt
  97 aroots-mdp.txt  records in aroots.txt which have mdp data.
                     As expected, all of these are class 10.
 Note: there is no overlap in these two sets; this is not tautological,
     but rather an independent datum.
 
 Some observations about aroots-mw:
 11  onomat.  KawaKawAya KaRaKaRAya KalaKalAya gaNgUya cawacawa damadamAya
               makamakAya rawarawAya SakaSakAya SirisirAya simasimAya 
  8  derivative roots
       arpaya Caus. of f
       iyasya Intens. of yas
       irajya Intens. of raj
       kzApaya Caus. kzE
       pAraya Caus. pf
       BuYjApaya Caus. 3 Buf
       mApaya  Caus. 3 mA
       SraTAya Caus. of SraT
  14 others
       anyaTaya  to alter
       izUya  to strive for
       kowAya  fr. 'kowA'
       gAloqaya to examine,
       gDa ?{sd Gas}
       candrikAya  to represent the moonlight
       pAWAntaraya to have a [{pAWAntara}}
       maDvasya  to long for honey
       mEtrAya  to be kind or friendly
       SIkAya to rain in fine drops (SIk = same meaning and in wdp)
       sajjIya  to make one's self ready
       samaya to level
       sAmaya Nom. from sAman
       simisimAya to quiver (with irritability, itch).

  It seems unlikely that, for the roots in aroots-mw.txt, any correspondence to
  roots in mdp is likely.

* match3a/chk1.txt, chk1.log
 Some analysis of aroots-mdp.txt
  For some of these, it is expected that there is an MW root spelled
  identically except for the absence of the final 'a'.
  By further searching in norm-mw.txt this question can be answered.
  This examination is done by chk1.sh.
  67 chk1.txt   the matches . Sample record:
     example1: gaRa
   gaRa 10.245-01;NOMW : gaR NOMDP;62523
     gaRa = root ending in 'a' in mdp
     10.245-01 = sid of gaRa
     gaR = matching root
     NOMDP = gaR is not a root in mdp
     62523 = L number of gaR
     Preliminary conclusion: gaRa 10.245-01 62523  match

     example2: Dvana
   Dvana 10.276-01;NOMW : Dvan 01.540-01,01.540-03p,01.557-03;102497
     Dvana = root ending in 'a' in mdp
     10.276-01 = sid of Dvana
     Dvan = matching root
     01.540-01, etc - various sid's of Dvan
     102497 = L of Dvan
     Preliminary conclusion: Dvana 10.276-01 102497 match
     
     example3: gfha
   gfha 10.282-01;NOMW : gfh 01.421-01,01.421-01p;NOMW
     gfha = root ending in 'a' in mdp
     10.282-01 = sid of gfha
     gfh = matching root
     01.421-01,etc = various sids of gfh
     NOMW = There is no MW root spelled 'gfh'.
     Preliminary conclusion:  'gfha' in mdp has no match in mw.
       NOTE: no other example is like 'gfha'; i.e., all others have an L

     example4: kala
   kala 10.254-01;NOMW : kal 01.325-01,10.059-01;45579,45580,45581
     kala = root ending in 'a' in mdp 
     10.254-01 = sid of kala
     kal = matching root
     01.325-01, etc = various sids of 'kal'
    45579, etc = various L's of 'kal'
  30 chk1.log   the non-matches  
   Sample record: aMsa 10.304-01;NOMW   (there is no root 'aMs' in norm-mw.txt)
   Possible conclusions for a root in chk1.log: 
     (a) There is no MW root matching  the root
     (b) There is an differently spelled MW root which matches. 
     (c) There is some additional 'normalization' of mdp spelling which would yield a match,
         as exemplified by saNgrAma.
    Note (2010-02-15).
    saNgrAma 10.308-01;NOMW  There IS 'saMgrAm' with wdp=35.68 and sense 'to make war, fight'
       which, in WestergaardDhP1.xml, corresponds to 10.308-01.  Possibly, the normalized form
       in mdp should be put to 'saMgrAma'. 

* match3a/chk2.txt, chk2.log
  There is a potential for matching with msid based upon all but one of the 
  records in chk1.txt (the one:  gfha 10.282-01;NOMW : gfh 01.421-01,01.421-01p;NOMW )
  Except for this one, there is one or more L numbers that might be matches. Example:
  katra 10.295-01;NOMW : katr NOMDP;42690

  From mwtab/Dha1tupe2.txt, there is a record
  <r t="g"><key1>katr</key1><ls>Dha1tup._xxxv_,_60<wsid>35.60</wsid><msid>10.295-01</msid></ls><L>42690</L><v>10,p</v></r>
  which shows that there is already a correspondence between 10.295-01 and 42690, based upon wsid.
  We now have a reason to identify the 'katra' spelling of mdp with the 'katr' spelling
  of MW.

  sh chk2.sh

  chk2.txt has the records of chk1.txt which can be so identified, 
    and the corresponding record of Dha1tupe2.txt.
    To reiterate, to be in chk2.txt, the msid-L of the root-without-a must be in Dha1tupe,
    and, therefore, be matched to wsid based upon a Dha1tup. reference in MW.
    Recall that we know also that, in Dha1tupe2, the class (from MW and sid) matches .
  chk2.log has the rest of the chk1.txt records.
    In particular, the aNka record of chk1.txt is written to chk2.log:
    aNka 10.313-01;NOMW : aNk NOMDP;1408  Here L=1408 might match msid=10.313-01.
    This is because 1408 does not appear in Dha1tupe2.txt 
    (There is no Dha1tup reference in MW for the root 'aNk').
Statistics from chk2.sh:
skipping line: gfh 01.421-01,01.421-01p;NOMW
67 lines from chk1.txt
35 lines written to chk2.txt, for 35 input records
31 lines written to chk2.log


The 35 in chk2.txt should probably be considered very likely matches; 
  By manual observation, the '<v>' element in each record of chk2.txt contains
  a class 10 reference, which is consistent with 'msid'.
  I will do a senses comparison next.
  nonmatch_chk2.txt has records where the two definitions appear different.
 sh chk2_sense.sh   creates chk2_sense.txt, chk2_sense.log
 sh chk2_disp1.sh   creates chk2_disp1.html (28), chk2_disp1_nonmatch.html (7)
   
As to the 31 in chk2.log, I will confirm that there is no (thus far hidden)
  Dha1tup information in MW;  the other thing to do is to compare the
  senses, and, in some cases (probably as with aNka) decide that the 
  correspondence is justified, even though not made for us by MW.
  TODO: confirm that there is no (thus far hidden) Dha1tup information in MW

* match3a/chk3  (Feb 15, 2010)
  The 31 records in chk2.log were separated (manually) into 
  12 chk3a.txt  only 1 L for the root (with 'a' removed),
                 the L has a 'class 10' reference in MW
                no class 10 mdp for the root (with 'a' removed), or else no mdp.
                For these, it is reasonable that the mdp for the root (with 'a')
                might be associated with the L for the root (without 'a').
                An examination of senses will be further done.
                Note:  correction to MW for {sd mfg} (L=166791):
                       class 10 added; also, ref to Dha1tup 35.46
  19 chk3b.txt  the rest of the records.
                There is currently no clear way to associate an mw record to
		these mdp roots ending in 'a'.
                TODO: don't forget these

* match3a/chk4
  This further analyzes chk3a.txt.
  The question examined is whether, on the basis of 'sense', the correspondence between msid and L
  displayed is reasonable.
  1.  sh chk4.sh
    chk4.txt adds data from mwverb/mwroots.txt to each record of chk3a.txt, using 'L'.
  2.  sh chk4_sense.sh
    retrieves the sense data 
    (a) from ../mwverb/sense/rootsense.txt  using L,
    (b) from ../mdp/sense/sensemw.txt  using msid.
    Also uses manually edited 'nonmatch-chk4.txt' to distribute the outputs to
      chk4_sense.txt (11 of the 12 records in chk4.txt)
      chk4_sense.log (1, 'Kow')  Here the senses in (a) and (b) appear non-matching.
  3. sh chk4_disp1.sh
    Displays the data from chk4_sense.txt in chk4_disp1.html,
    and from chk4_sense.log in chk4_disp1_nonmatch.html.

  So for the 11 in chk4_sense.txt, the correspondence seems reasonable.
  
  Note: devaSabda in MW refers to Westergaard 35.8, whose root is 'gadI' ('gada' is mentioned as
        pAWAntara). As seen in wdp/WestergaardDhP1.xml, this supports the as-yet-unmade
        correspondence between wsid 35.8 and msid 10.249-01:

<sutra msid="10.249"><root wsid="35.7" mdp="stanagadI" mdp1="stana" msid="10.249-02">stana</root><root wsid="35.8" nomdp="yes" msid="10.249-">gadI</root><sense>devaSabde</sense></sutra>

      
