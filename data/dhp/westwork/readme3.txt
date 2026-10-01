Feb 15, 2010
Westergaard/readme3.txt
This continues the work described in 
  readme2.txt,readme.txt and readme-orig.txt.

* match4/norm-mw-uni.txt, norm-mw-uni0.txt, norm-mw-uni0.log
 norm-mw-uni1.txt, norm-mw-uni1.log
sh norm-mw-uni.sh

 720 lines in norm-mw-uni.txt; 
     These are the lines of norm-mw.txt that contain a unique
     correspondence between msid and L based upon the 'key1-normroot'
     match. For example
gam 01.702-01;63409
     shows that there is one instance in mdp of a normalized root spelled
     'gam' (for sid = 01.702-01), and one record in MW whose key1
     value is spelled 'gam' (for L=63409).

Next, mwroots is used to pull 't="g/a"' and <v></v> using 'L',
  and WestergaardDhP1.xml is used to pull wsid using 'msid'.
Note: 74 'nomdp="yes"' records written to norm-mw-uni0-nomdp.txt;
      It was thought inappropriate to consider wsids matched in such cases.

719 lines from norm-mw-uni.txt
647 records written to file norm-mw-uni0.txt
72 records written to file norm-mw-uni0.log
   All of the records in norm-mw-uni0.log have no wsid. 
   63 of them are marked as pAWAntara.
    9 of them do not match a Westergaard record for some other reason:
<key1>jUz</key1><msid>01.443-01</msid><L>80116</L>noWSID<r t="a"><v>1,p</v></r>
<key1>plI</key1><msid>09.035-01</msid><L>141466</L>noWSID<r t="a"><v>9,p</v></r>
<key1>Parv</key1><msid>01.373-03</msid><L>141716</L>noWSID<r t="a"><v>1,p</v></r>
<key1>mAnT</key1><msid>01.038-05</msid><L>163014</L>noWSID<r t="a"><v>1,p</v></r>
<key1>mreq</key1><msid>01.194-02</msid><L>168896</L>noWSID<r t="a"><v>1,p</v></r>
<key1>mlew</key1><msid>01.194-03</msid><L>168936</L>noWSID<r t="a"><v>1,p</v></r>
<key1>varR</key1><msid>10.018-01</msid><L>187289</L>noWSID<r t="g"><v>10,p</v></r>
<key1>SvaBr</key1><msid>10.075-01</msid><L>224344</L>noWSID<r t="a"><v>10,p</v></r>
<key1>spF</key1><msid>09.020-01</msid><L>256737</L>noWSID<r t="a"><v>9,p</v></r>

  Note1: the removal of the nomdp="yes" cases resulted in 10 extra 
        pAWAntara non-matches.
  Note2: in norm-mw-uni0.txt, there is only 1 wsid for each msid.

Now, norm-mw-uni0.txt is split into 2 files, based upon the presence
or absence of key1 in mwtab/Dha1tupe3.txt (see readme2.txt):
Dha1tupe3 are 'good' matches (without regard to sense matching).

  452 norm-mw-uni1.txt  present in Dha1tupe3.txt
    These do not need to be examined further. 

  195 norm-mw-uni1.log  absent in Dha1tupe3.txt
  
* match3/nonmatch-uni.txt
 sh nonmatch-uni.sh

  Recall: when the records of Dha1tupe3.txt were examined to see if the
  MW-root-sense matched the mdp sense, some  were judged to be non-matches
   (see match3/nonmatch.txt, and disp1-nonmatch.html).
  We will look for overlap between these and norm-mw-uni1.txt;
  sh sense-match-uni1.sh
Statistics:
460 lines from ../match4/norm-mw-uni1.txt
64 lines from nonmatch.txt
30 records written to file nonmatch-uni.txt  
34 records written to file nonmatch-uni.log

  For those in nonmatch-uni.txt, we now have another piece of evidence
  that the correspondence between msid and L should be accepted here,
  despite that fact that the mw root sense seems different than the
  corresponding msid senses.  
  TODO:  How to reconcile?

* match4/uni2a.txt, uni2b.txt, uni2c.txt
 sh uni2.sh
 The records in norm-mw-uni1.log are absent in Dha1tupe3.txt;
 let's examine why.
 First, they might be absent due to having no Dha1tup references at
  all or to having an incomplete Dha1tup reference.
 
195 lines from norm-mw-uni1.log
41 records matching ../mwtab/Dha1tupc.txt written to file uni2a.txt
   uni2a.txt:  records with only 1 L-sid match based on key1-normroot,
               and which have Dha1tup material, but have not thus far
               been considered to match.
0 records matching ../mwtab/Dha1tupc-inc.txt written to file uni2b.txt
154 records matching neither written to file uni2c.txt
   uni2a.txt: records with only 1 L-sid match based on key1-normroot,
              but have thus far been excluded from analysis due to
              lack of Dha1tup reference in MW.

uni2a-nonmatch.txt  and uni2c-nonmatch.txt
 are created manually as lists where the L-def and msid-def differ.

sh uni2_sense.sh
6 senses read from uni2a-nonmatch.txt
41 records read from uni2a.txt
* 35 matching records written to file uni2a_sense.txt
6 non-matching records written to file uni2a_sense.log

11 senses read from uni2c-nonmatch.txt
154 records read from uni2c.txt
* 143 matching records written to file uni2c_sense.txt
 11 non-matching records written to file uni2c_sense.log
sh uni2_disp1.sh
 creates displays:
uni2a_sense.txt => uni2a_disp1.html
uni2a_sense.log => uni2a_disp1_nonmatch.html
uni2c_sense.txt => uni2c_disp1.html
uni2c_sense.log => uni2c_disp1_nonmatch.html

(*) For roots in these two files (uni2a_sense.txt, uni2c_sense.txt),
  it is likely that the msid-L correspondence is good.
  
Caveat re 'class':  For a few of roots in each file, there is an
  inconsistency in the 'class' information from MW and from mdp.
  (For some cases, there is no class information from MW; these are
   deemed 'consistent' since they are not inconsistent.)

 uni2a_sense.txt class incosistencies:
kUR 53919 10.133-01  (cl=1)
Kad 61228 01.042-01  (cl=6)

 uni2c_sense.txt class inconsistencies:
cud 74573 10.049-01  (cl=1)

 uni2a_sense.log  class inconsistencies
kfp 54858 01.495-01  (cl=6,10)

 uni2c_sense.log  class inconsistencies
aG 1348 01.078.01  (cl=10)
kit 50271 01.713-01 (cl=3)
krand 57730 10.170-01 (cl=1)


*  (match4a) summary of matching thus far:
801 match3/Dha1tupe3_sense.txt
    [64 match3/dpe3_sense.log  (match except for sense) (list also in nonmatch.txt)
      30 match3/nonmatch-uni.txt     
      34 match3/nonmatch-uni.log]
 28 match3a/chk2_sense.txt
 12 match3a/chk4_sense.txt
 35 match4/uni2a_sense.txt
143 match4/uni2c_sense.txt
===
1019

> sh gather.sh
 duplicate sid: 04.058-01 219306-../match3/Dha1tupe3_sense.txt 219184-../match3/Dha1tupe3_sense.txt
 duplicate sid: 05.008-01 204040-../match3/Dha1tupe3_sense.txt 203978-../match3/Dha1tupe3_sense.txt
801 lines from ../match3/Dha1tupe3_sense.txt
28 lines from ../match3a/chk2_sense.txt
11 lines from ../match3a/chk4_sense.txt
35 lines from ../match4/uni2a_sense.txt
143 lines from ../match4/uni2c_sense.txt
1018 records written to file gather.txt

 sh disp1.sh
  This creates gather_disp1.html from gather.txt.  It displays some useful
  information.

* mwtab1 (begun Feb 24, 2010)
  The work in this directory reformulates some work appearing in mwtab.
  The starting point is the file mwtab/Dha1tupd.txt, which contains
  the explicit references in MW to Westergaard, but only for records
  L believed to be roots (per mwroots.txt).
  
  Additional work with MW has uncovered several (about 50 at 2010-02-24)
  references to Westergaard which are believed to be implied in MW, but
  given incompletely, without the 'Dha1tup' tag.  These are in file
  Dha1tupd-extra.txt (note: the format here is different than Dha1tupd)
  NOTE (April 27, 2010): a 'local copy' of Dha1tupd.txt is used;  This should
     probably be viewed as distinct from the one in mwtab.

  sh mww_init.sh  creates mww.txt from Dha1tupd.txt and Dha1tupd-extra.txt
   and mwverb/mwroots.txt. 
  There is a line for each line of mwroots.txt
  Each line has three fields, separated by tab:
   L  a given MW record number
   code a 'status' code. Initially = '?'
   wsids  All Westergaard references appearing in record L, represented
      as a comma-separated list of individual references, in decimal form
      NOTE: if there are no Westergaard references, 'NONE' is shown.
Statistics:
read 1523 lines from Dha1tupd.txt
read 52 lines from Dha1tupd-extra.txt
1837 lines in ../mwverb/mwroots.txt
In mww.txt:
 534 records have 0 wsids (marked as NONE)
1079 records have 1 wsids
 176 records have 2 wsids
  37 records have 3 wsids
   5 records have 4 wsids
   5 records have 5 wsids
   1 records have 6 wsids
check: 1837 == 1837 ?

* mwverb:  
  TODO: The following are some notes re marking MW records as roots:
203563	vIr	prob. should mark as root
212482	Sad	prob. should mark as root
222856	Sriz	prob. should mark as root
229023	sajj	prob. should mark as root
236685	samprAv	prefixed root, not root
252041	se	Not a root:  '2. sg. A1 of 1. {sd as}.'
256550	spaS	prob. should mark as root

* mwtab1/mww1.txt
 sh mww1.sh
 Focus on the records in mww.txt with just 1 wsid.
 Use  WestergaardDhP1.xml to get the (sutra-based) association between
  wsid and msid.
 Now, extend the data of mww.txt, putting the results in mww1.txt.
 There is one line in mww1.txt for each line in mww.txt.
 There are tab-separated fields:
  L  MW rec #
  meth : MWSID  (method of matching - later versions will have other codes)
  code : status, same as in mww.txt (= '?')
  wsid :  the same comma-separated list, extended as wsid=msid
          with the msid value coming from WestergaardDhP1x.ml.
  Examples: (only L and wsid values shown)
38410 NONE   same as before, no wsid to match
38696 28.19=06.022-01   wsid of 28.19 is associated only with msid 06.022-01
41598 5.6=01.088-01,19.22=01.518-01  two wsids, with unambiguous msids
42288 13.6=01.297-06,19.32=01.524-01,30.41=NOMSID   wsid 30.41 had no msid
40663 13.11=01.297-    the associated msid is incompletely determined.
50585 28.61=06.060-01|06.060-01p,32.64=10.059-01  28.61 had two assoc. msids

* mwtab1/mww1a.txt
  sh mww1a.sh
  This changes only (some) lines currently marked in mww1.txt as 'NONE';
   i.e., for such an L, the MW record has no (specific) Westergaard reference.
  For such an 'L', we use mdp/norm-mw.txt to attempt a match.
  For example, L=134. In norm-mw.txt, there is 'ak 01.071-01,01.523-01;134'
  which means that there are two msids which have the same norm-root ('ak') as
  the key1 of '134'. From WestergaardDhP1.xml, 4.13 = 01.071-01,
  and 19.30 = 01.523-01 . So, we change the record in mww1a.txt to
  134 KEY ? 4.13=01.071-01,19.30=01.523-01  

  mww1a.txt now has 309 'KEY' matches
  There are still 225 marked as 'NONE' (no sid-L correspondence)

* mwtab1/mww1b.txt
  sh mww1b.sh
  This changes only some lines currently marked in mww1a.txt ;
  The basis of this is match3a/chk1.txt. For example:
  Example 1: L=1408 
   mww1a.txt: 1408	MWSID	?	NONE
   chk1.txt   aNka 10.313-01;NOMW : aNk NOMDP;1408
    Conclusion L=1408 may match  msid=10.313-01 (wsid=35.74 by WestergaardDhP1.xml)
    mww1b.txt: 1408	  AKEY	 ?		35.74=10.313-01
  Example 2: L =45579. Here we already have a match based on MWSID:
   mww1a.txt: 45579	MWSID	?	14.26=01.325-01
   chk1.txt:  kala 10.254-01;NOMW : kal 01.325-01,10.059-01;45579,45580,45581
      This says 45579 may match with 10.254-01. (wsid=35.13 by WestergaardDhP1.xml)
   mww1b.txt: 45579	MWSID,AKEY	?	14.26=01.325-01,35.13=10.254-01
     Note, we have two 'method' values here.

Statistics:
processed 66 lines out of 67 from ../match3a/chk1.txt
1837 lines in mww1a.txt yielded 88 additional sids
However, there are still 220 marked as 'NONE' (no sid-L correspondence).
By searching for ',AKEY' in mww1b, there are 83 additional possible L-msid correspondences,
and only 5 brand new possible L-msid correspondences.

* mwtab1/mww1c.txt
  sh mww1c.sh
  The records in match3a/aroots-mw.txt (33 of them) are unlikely to
  be matchable to anything in mdp, so they are marked, in mmw1c.txt,
  with status code 'NOMDP'.  This will permit exlusion of them in later
  investigation.  The 'data' field, previously 'NONE', is changed to
  'NONE,$key1'. (just so we can see key1 readily).

Statistics:
processed 33 lines out of 33 from ../match3a/aroots-mw.txt
unexpected mww1b.txt: key1=gAloqaya but line=65006      MWSID   ?       35.86=NOMSID
unexpected mww1b.txt: key1=sAmaya but line=242233       MWSID   ?       35.27=10.266-01
1837 lines in mww1b.txt yielded 31 additional sids
1837 lines written to mww1c.txt

 NOTE that 'gAloqaya' has an MW Westergaard reference, 35.86, but currently
 no accepted corresponding 'msid' (based on Westergaard).
 In the case of 'sAmaya', the WDP root is 'sAma'.
 The 'NOMDP' code was NOT added to these two.  

* mwtab1/mww2.txt, mww2L.txt, mww2dp.txt
 sh mww2.sh
 a) mww2.txt reformats mww1c.txt slightly.
    The fields are tab-delimited.
    The first three fields are the same:
     L  The L-identifier of MW record
     meth  a method code indicating how dp records were associated with L
     code  a 'status' code, currently '?'
    There follow one or more fields identifying dp records associated with L.
    The first (and, in this case, only) field may be 'NONE' indicating
       that there are no dp records associated with L.
    If there are DP records associated with L, then there are as many
       additional fields as there are distinct 'msid' identifiers.
       Each of these dp fields is a semicolon-separated list of two fields:
       wsid and msid.  It is possible that the msid value is 'NOMSID'.
       Currently, there is no analogous situation of 'NOWSID'.

 b) mww2L.txt
    This contains additional data derived from MW via 'L' for each record
    in mww2.txt. There are 5 tab-delimited fields:
    L a repeat of L
    key1  the key1 field (root spelling) for the MW record
    v     a list of class numbers , separated by comma
    type  either 'g' for 'genuine', 'a' for 'artificial', or 'x' for unknown
         according to MW typograpy indicating genuine or artificial roots.
    def  a definition.  This contains a selection of definitions; distinct
         senses are separated by ' OR '.  

  c) mww2dp.txt
     This contains additional information for each of the dp fields.
     The first field is always L.  The second field may be 'NONE', if there
     were no dp records associated with L. If there were dp fields for L 
     in mww2.txt, then there is a field in mww2dp.txt for each dp field
     of mwww.txt.
     Each such field in mww2dp.txt is a semicolon separated list of 4 fields:
      wsid
      msid
      normroot  
      sensedata:
       The sensedata is a '|' separated list corresponding to the sense
       stems in mdp. Each such sense term is, in turn, has two fields,
       separated by ':':
        1) sense stem adjusted:  There are two adjustments that might have
         been made from a sense stem appearing mdp:
         - change of spelling to an MW headword.  For instance,
           saNgAta is changed to saMgAta.  
         - indication of a compound which does not appear in MW, but whose
           components do appear. For instance,
           gatyArTa does not appear, but each of the components 'gati+arTa'
           does appear.
        2) a definition of the sense stem derived from MW.  For a compound
           like 'gati+arTa' the definitions of 'gati' and 'arTa' are also
	   separated by a ' + '.
           For a given definition, multiple senses are separated by ' OR '.

* mwtab1/sense/sensemap1.txt
 sh init1.sh

 This provides a correspondence between definitions of roots from MW
 and definitions of sense terms. 
 The MW root definitions are from mwtab1/mww2L.txt,
 and the mdp sense term definitions are from mwtab1/mww2dp.txt.
 Based on the correspondence between L and msid of mww2.txt, a preliminary
 file def_init0.txt was written showing all root def - sense def pairs.

 For instance, from 134	KEY	?	4.13;01.071-01	19.30;01.523-01,
two lines were generated:
134	to move tortuously	!=	lakzaRa:expressing indirectly OR a mark, sign
134	to move tortuously	!=	kuwila+gati:bent, crooked + going

The != connective means that the two terms were initially considered as different.
There were 5914 lines initially in this def_init0.txt file.

By a subjective process of examination, various of the pairs of definitions were marked
as '==', or equal.  For instance, 
134	to move tortuously	==	kuwila+gati:bent, crooked + going

This process resulted in the file def_init.txt.
Finally, init1.sh slightly simplified def_init.txt into sensemap1.txt, which has 4361 lines.
The first few lines, which include the examples above, are:

lakzaRa:expressing indirectly OR a mark, sign	!=	to move tortuously
lakzaRa:expressing indirectly OR a mark, sign	!=	to move in a curve
lakzaRa:expressing indirectly OR a mark, sign	==	to mark, stamp, brand
lakzaRa:expressing indirectly OR a mark, sign	==	to mark
kuwila+gati:bent, crooked + going	==	to move tortuously
kuwila+gati:bent, crooked + going	==	to move tortuously, wind


Note that the 'L' number is now removed, and duplicates are removed.  This file makes it possible
to analyze programmatically the correspondences based on the definitions.


* mwtab1/select/d.txt
  sh d.sh

This uses sensemap1.txt to assign status codes to the correspondences of mmw2.txt.
For instance, for L=134, the record of d.txt is
134	ak	YES	n	y
This says
(a) the sense term definition(s) for 01.071-01 does not match the root definition for 'ak' from MW.
(b) the sense term definitions for 01.523-01 does match.
(c) the 'YES' indicates the (somewhat weak) matching requirement that one of the msids correpsonding
    to L=134 (namely, 01.523-01) has a sense stem whose definition is deemed to match that of the root.

* mwtab1/select/v.txt
 sh v.sh

 v.txt provides an analysis of the mmw2.txt correspondences based upon root 'class'. 
Example 1:
mww2.txt 134	KEY	?	4.13;01.071-01	19.30;01.523-01
mww2L.txt 134	ak	1	g	to move tortuously
v.txt 134	1	YES	y:1	y:1

Example 2:
mww2.txt  423	KEY	?	17.2;01.425-01
mww2L.txt 423	akz	1,5	g	to reach OR to pass through, pervade, embrace OR to accumulate
v.txt     423	1,5	PART:5	y:1
  Here the 'PART' indicates 
  (a) all the classes implied by the associated msids (here, just '1') were
      included in classes from MW at L=423.
  (b) Class 5 from MW at L=423 did not appear as a class among the associated msids.

Example 3:
mww2.txt  1348	KEY	?	4.35;01.078-01
mww2L.txt 1348	aG	10	g	to go wrong, sin
v.txt     1348	10	NO:10	n:1
  Here the 'NO' indicates
  that one of the msid classes (here, '1') does not appear among the L classes (here just '10').
  The '10' after the 'NO' ('NO:10') further indicates the L classes (here just '10') that fail to appear
  among any of the associated msids.


* mwtab1/select/k.txt
  sh k.sh

  This evaluates the correspondence between L and associated msids based upon whether the L headword 
  (key1) corresponds to the msid normalized roots.
134	ak	YES	y:ak	y:ak   key1 = ak, both msids have normroot = ak.
28637	iNK	NO	n:iK	n:iK   key1 = iNK, one (or more) msids have different normroots.
45580	kal	YES	y:kal	y:kal	a:kala
  In this case, 'kala' was marked as a:kala,  but this was deemed to be ok.
The mww2.txt entry is:
45580	KEY,AKEY	?	14.26;01.325-01	32.64;10.059-01	35.13;10.254-01
'KEY' indicates that there was a match by kal = kal
'AKEY' indicates there was (also) a match by 'kal' ~ 'kala'.
The absence of 'MWSID' indicates that MW had no explicit Westergaard references for L=45580.


* mwtab1/mww2.html
  sh disp.sh

  This display summarizes the information for all the 1800+ records in mww2.txt.
  The use of color helps the reader identify points of confirmation in the correspondences,
  and points of difference that may indicate the purported correspondence is not useful.


* mwtab1/mdpother.txt
 sh mdpother.sh

 There are some msids in mdp.xml which have not been mentioned at all
 in mww2.txt.  mdpother.txt contains a list of these (632).
 (NOTE: there are 2276 entries in mdp.xml. There are 1644 distinct msids
  mww2.txt. 1644 + 632 = 2276, so we have accounted for all the entries
  in mdp.xml. Hurray!)

 The program actually uses the msids as presented in the file 
  mdp/norm-mw.txt: samples
aMsa 10.304-01;NOMW
ag 01.091-19,01.523-02;762
 
 each msid in norm-mw.txt is checked for its presence in mww2.txt. 
 If the msid is absent in mww2.txt, then a line is written to mdpother.txt
 Samples:
aMsa	10.304-01	35.64	NOMW
aNga	10.314-01	NOWSID	NOMW
ac	01.123-01p	NOWSID	1767
ac	01.595-01p	NOWSID	1767
gup	01.688-01	NOWSID	65898,65899
There are 4 tab-delimited fields:
 key:  from norm-mw
 msid: from norm-mw
 wsid: from WestergaardDhP1.xml. If not found, then 'NOWSID'
 L:    from norm-mw.txt : A comma-separated list of mw L record numbers.

