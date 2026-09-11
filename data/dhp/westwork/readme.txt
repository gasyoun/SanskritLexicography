Lexical/Funderburk/Westergaard/readme.txt
Dec 29, 2009
* initialization
 From ejf computer, C:/sanskrit/westergaard/,
 copied directories wdp,mwdp, mwtab (except for monier_dump.txt)
 copied files: readme.txt (renamed to readme-orig.txt),
   scratchwork, Section-root-page.txt, wdpsutras.
 readme-orig.txt has notes on these files.

* mwverb
  This directory contains comparisons between root coverage 
  between all MW roots (whether with a Dha1tup. reference or not) and
  the Westergaard Dhatupatha.
  Several important MW roots were noticed to have no Dha1tup reference,
  so the correspondence to a dhatupatha cannot be made solely on that basis.
  
  As the source of MW roots, I will use data copied from 
  Lexical/Funderburk/verb/ ('verb') directory.

* mwverb/mwroots.txt
  sh mwroots.sh
 mwroots.xml is constructed from three inputs in the 'verb' directory:
  1. preverb-2008/verb-prep4-root.out
<H1><h><hc3>500</hc3><key1>aMS</key1><key2>aMS</key2></h><body><vlex type="root"></vlex><vlex>cl.10. P.</vlex><vlex>A.</vlex></body><tail><pc>1,1</pc><L>9</L></tail></H1>

  2. primaryroots/genuine.txt
MW-0002490.00	at	hom=2	page=12
  3. primaryroots/artificial.txt
MW-0045579.00	kal	hom=1	page=260
 
These files are copied into the mwverb/verb/ directory before processing.

A line is constructed for each line of verb-prep4-root.out (1837 lines).
for instance,
<r t="g"><key1>aMS</key1><L>9</L><v>10,p;a</v></r>
Explanation:
<r t="..."><key1>...</key1><L>...</L><hom>..</hom><v>..</v></r>
key1,L are directly from verb-prep4-root.out. These are present for all lines.
<hom> is also taken from hom element, and may be absent.
<v> is a semicolon-separated list that recodes the <vlex> elements;
  each element of the list is itself a comma-separated list of elements,
  which is one of:
  -  number (a class, or gaRaNum)
  -  p (parasmaipada)
  -  a (atmanepada)

t has value "g" (genuine) when the line (based on L) is in genuine.txt
  or value "a"  (artificial) when the line is in artificial.txt
  or "x" when the line is in neither of these files.

NOTE: MW-0077183.00	jaB	hom=1	page=412	not vlex
is in artifical.txt, but not in verb-prep4-root.out.

*  match1 directory
sh match1.sh
Two files are inputs:
#lines
1837 mwverb/mwroots.txt: the list of roots from mw
1592 mwdp/mwdp.xml : the list of records matching 
        MW references 'Dha1tup._xx,_yy' with <wsid>xx.yy</wsid>.
        None of the subtleties considered in mwpda.xml are involved here.
Three files are outputs.
1280 match1.txt 
  contains the records from mwroots, with an additional 'w' attribute
  to the r element: the value of the 'w' attribute is a comma-separated list
  of the 'wsid' values from lines in mwdp.xml that have the same 'L' value.
  184 of these records have more than 1 match in mwdp;
  there are 225 'extra' wsids.
 557 mw1.txt 
  contains the records from mwroots which have no correspondent in mwdp
  Note1: 1280 + 557 = 1837 (so all lines of mwroots are accounted for)
  Note2: 306 of the records in mw1 are 'genuine' roots, 247 are
         artificial, and 4 are neither.
 87 wdp1.txt  
  contains the records in mwdp with no correspondent in mwroots.
  Ideally, one would expect this file to contain no elements.
  Note: 1280 + 87 + 225 = 1592 (so all lines of mwdp are accounted for)
  TODO:  examine the underlying MW data to understand why a Dha1tup reference
         occurs in these 87 records, but the records are not classified as
         mw roots.

* match1a  (also in match1 directory)
sh match1a.sh
There are some keys that appear in records of both match1.txt and
mw1.txt.  For such an mw key, there are multiple <L> records,
some of which contain a Dha1tup reference (those in match1.txt) and some
of which do not.
109 match1-mw1.txt these contain all records (from both match1.txt
  and mw1.txt) where there is a common value of 'key1'.
  i.e., some records  have a wdp reference and some do not
1224 match1a.txt contains the records from match1 not in match1-mw1
    i.e., keys all of whose records have a wdp reference
504 mw1a.txt contains the records from mw1 not in match1-mw1.
    i.e., keys, none of whose records have a wdp referece.

Note: 109 + 1224 + 504 = 1837 = # records in mwverb/mwroots.txt.

* mdp/mdp.xml
sh mdp.sh
This is a very slightly altered version of
 Lexical/Funderburk/mdhvcanonical/MadhaviyaDhP2_entries.xml
 The entries within a sutra are numbered consecutively, and this 'entry number'
 is appended to the sid attribute to give a sid number to each entry.
 Numbering restarts for the pAWAntara entries, and a 'p' is appended in the sid.
 The 'sid' value is now unique to each entry.  
 The old 'id' attribute is not needed; however, it has not yet been removed.

 TODO: The underlying file MadhaviyaDhP3.xml probably should be modified, 
       but this has not been done.

example: sid="01.028-01p"  (first pAWAntara entry in sutra 01.028)


* wdp/WestergaardDhP1.xml
sh wdp1.sh
This is a modification of WestergaardDhP.xml. 
It adds the entry-sid of mdp/mdp.xml to the root elements, where appropriate.
In WestergaardDhP, we have an association between the sutras of Madhaviya and
a collection of roots (with wsid values) from Westergaard.  However, there is
no correspondence between the Westergaard roots and the particular entries of
the corresponding Madhaviya sutra.  This program remedies that deficiency.
The principal of correspondence is to match full roots.  Westergaard gives only
full roots; suppose we have a full root in Westergaard, which occurs in a 
sutra which has been associated with a particular Madhaviya sutra.  Then,
we try to match the Westergaard full root with the 'fullDAtu' field from each
of the entries that occur in the Madhaviya sutra. The list of entry sids that
match is placed as the value of the 'msid'  attribute in the Westergaard root
element.  Some examples may clarify some of the possibilities:
Example 1:
old:
<sutra msid="01.0007"><root wsid="2.5">nADf</root><root wsid="2.6">nATf</root><sense mdp="yAYcopatApESvaryASIHzu">yAcYopatApESvaryASIHzu</sense></sutra>

in mdp.xml we look for sid="01.007", there are two roots
  01.007-01 = nADf, 01.007-02 = nATf.
new:
<sutra msid="01.0007"><root wsid="2.5" msid="01.007-01">nADf</root><root wsid="2.6" msid="01.007-02">nATf</root><sense mdp="yAYcopatApESvaryASIHzu">yAcYopatApESvaryASIHzu</sense></sutra>

Example 2:
old:
<sutra msid="01.0094"><root wsid="5.53" mdp="GaGa">GagGa</root><sense>hasane</sense></sutra>
Recall that the 'GaGa' value of mdp was set in the original comparison between
Westergaard and the sutratext file; in this case, ejf made a judgment that,
even though Madhaviya sutratext had 'GaGa' and Westergaard had the non-identical
'GagGa', nonetheless the difference did not vitiate the identification; and
since there was a difference, this was represented by the mdp attribute.
Here, we look for GaGa as the fullroot in mdp.xml under sutra 01.009:
new:
<sutra msid="01.0094"><root wsid="5.53" mdp="GaGa" msid="01.094-01">GagGa</root><sense>hasane</sense></sutra>

Example 3:
old:
<sutra msid="01.xxxx"><root wsid="5.54">daGi</root><sense>pAlane</sense></sutra>

Here, msid=01.xxxx means there is no corresponding mdp record. So, we do
nothing to the record.

There will inevitably be cases where there is no <fullDAtu> match.
These are generally due to errors in the original coding of Westergaard in
  noting the alternate Madhaviya spelling via the 'mdp' attribute of a root.
  This leads to a round of corrections.
  There is a series of corrections made by adding,
   as different 'mdp1' attribute of the root, the 'fullDAtu' from
   MadhaviyaDhP2_entries.xml.  While doing this, it was informally noticed
   that MDhP in many cases had a 'norm' attribute on the root, and that
   the fullDAtu agreed with this normalized root.  Thus, many of these
   'corrections' are due to different conventions between the sutraText
   file of MDhP and the fullDAtu field of the MadhaviyaDhP file.

   By comparing wdp1.log and mdp.xml, I manually assigned
   the attribute 'mdp1' to many roots in Westergaard, the value being 
   that of the fullDAtu field of the corresponding sutra entry in mdp.xml.
   Some judgment was used in this process, so it is possible some of the
   ensuing matches between Westergaard and mdp will be in error.
   Since  'mdp1' is a new attribute, these assignments can be examined.
   It is also possible that some of the original 'mdp' attribute assignments
   are in error. The presence of either of these two types of errors would 
   lead to an incorrect identification of Madhaviya and Westergaard roots.
   The copy of wdp1.log used for this comparison is in old/wdp1-20091230.log.

A few changes were made to wdp1.php:
  a) check for a match was done even if the nomdp='yes' attribute is present;
     Since mdp.xml has pAwAntara entries, a few nomdp='yes' instances now
     match. Recall that sutratext did not contain pAWantara entries from
     Madhaviya.
  b) Here is the new logic for matching Westergaard.xml with mdp.xml:
    If the 'mdp1' attribute is present in Westergaard.xml for a root, 
    its value is used to match to fullDAtu of mdp; 
    otherwise, if the 'mdp' attribute is present, its value is used;
    otherwise, the text contents of the root element is used.

 c) In the msid of the sutra,  remove the leading 0.
   This corrects a notational inconsistency introduced earlier in
   Westergaard.xml.
   Example:  msid="01.0004" is changed to msid="01.004".
   This is consistent with mdp.xml.

After these corrections,
  There are 29 sutras in WestergaardDhP1.xml with a root that cannot yet
  be matched to an entry in mdp.xml.  These are identifiable by the regular
  expression -"  (i.e., there msid ends in a dash). For example:
  <root wsid="6.7" nomdp="yes" msid="01.102-">Saci</root>
  These are also present in wdp1.log.

  There are 55 sutras where there are multiple matches for one or more roots;
  This are listed in wdp1.log.  At least some of these (perhaps all) are 
  due to a pAWAntara entry with the same fullDAtu as some non-pAWAntara entry
  in the sutra.

Sample line of WestergaardDhP1.xml:
<sutra msid="01.103"><root wsid="6.8" msid="01.103-01">kaca</root><sense>banDane</sense></sutra>

 This shows that in the 103rd sutra of class one (acc. to MadhaviyaDhP),
 the full root 'kaca' is the 8th root in section 6 of Westergaard, and is the
 1st root of the sutra in MadhaviyaDhP (in this instance, there is only 1
 entry in the MadhaviyaDhP sutra).

 In other words, there is now a partial correspondence in WestergaardDhP1.xml
 between the roots of Westergaard and the entries of Madhaviya.

 In addition to the 29 sutras where this correspondence does not account for
 all of Westergaard roots,  there are also 30 sutras unique to Westergaard;
 These are found by searching for all lines with 'xxxx' .
 For instance:
<sutra msid="01.xxxx"><root wsid="17.14">pakza</root><sense>parigrahe</sense></sutra>

 
 There are 17 sutras of mdp that appear to have no correspondent sutra in 
 Westergaard.  This are indicated by the 'mdpsutra' element. For instance,
<sutra msid="01.250"><mdpsutra>(X5. tepf) kampane ca {mdp}</mdpsutra></sutra>

 There are 16 additional sutras with an 'mdproot' element, indicating 
 (non-pAWAntara) elements of mdp which are alleged to have no correspondent 
 in Westergaard.
 Probably, these 17+16=33 sutras account for all the Madhaviya non-pAWAntara
 roots which don't appear in the (non-pAWAntara) roots of Westergaard.

 Some of these lack of correspondences might be resolved by as yet uncoded
 pAWAntara roots from Madhaviya, or by the completely uncoded pAWAntara 
 roots from Westergaard.

* match2 (in match2 directory)
We now turn attention to comparing the roots of mw (mwverb/mwroots.txt) to
the roots of Madhaviya (mdp/mdp.xml).  
With each record in mwroots.txt we want to associate one or more entries of
mdp.xml.  We would like the value of the key1 element of an mwroot record
to agree with the normalized root of the corresponding mdp entries.
For those mwroots which have class and pada information, we would
like the associated entries to agree in this manner also.

For those elements of mwroots that are in match1.txt, the correspondence
between msid and wsid should provide the correspondence we seek.
However, for those elements in mw1.txt, we must use the key/class/pada
information for the match.

* sh wsid-msid.sh
It is convenient to have a simple file, based on WestergaardDhP1.xml,
with the associations between wsid and msid.  This program creates 
wsid-msid.txt as such a file.  Each of its lines contains a space-separated
list of two values, wsid and msid based on the values of the wsid and msid
values of the root elements in WestergaardDhP1.xml.  When there are
multiple msid values for a wsid value, these are represented on separate lines;
these multiple values are also printed to a log file for easy reference.
In cases of a root where there is no msid value for a wsid value, there is
no corresponding line printed; these root elements are also printed to the 
log file for reference.
Note: from the log file wsid-msid.log, all but 4 of the multiple matches are due
  to pAWAntaras.  The exceptions are:
MANY: <root wsid="15.52" msid="01.365-01,02">zWivu</root>
MANY: <root wsid="22.14" msid="01.639-01,02">styE</root>
MANY: <root wsid="22.14a" mdp="zwyE" mdp1="styE" msid="01.639-01,02">styE</root>
MANY: <root wsid="26.4" msid="04.004-01,02">zWivu</root>

* match1-msid
sh match1-msid.sh
This reads each line of match1.txt, and, using wsid-msid, replaces the
list of wsids for the line by corresponding msids.
When there is no msid, the line is written to the log file (match1-msid.log).
When there is a match, the line is written to match1-msid.txt

There were 1237 records written to match1-msid.txt
43 of the 1280 lines of match1.txt had no matches (match1-nomsid.txt) 
16 inputlines had partial (incomplete) matches (see log file)
61 wsids altogether had no msids. (see log file)

For the purpose of matching mwroots to Madhaviya, the 43 match1-nomsid.txt
will have to be dealt with like those of mw1.txt; e.g., the
Westergaard data cannot directly help us associate mw with Madhaviya.


* match2.txt
sh match2.sh
This joins the records of match1-msid with records of mdp.xml;
  In particular, it adds, for each msid, an mdp record containing the
  root from mdp (the normalized root is obtained if available)
Inputs: match1-msid.txt
        mdp/mdp.xml
Output: match2-1.txt
 
NOTE: see kdp/kdp-MDhP/step0/mdpentries.xml: this has 'preds' from MDhP.
