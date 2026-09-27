_Created: 27-09-2026 · Last updated: 27-09-2026_

# Scharf-Hyman_LinguisticIssuesInEncodingSanskrit_2011

**Kind:** full-text extraction (source PDF is openly posted by The Sanskrit Library)
**Citation:** Scharf, Peter M. and Malcolm D. Hyman. *Linguistic issues in encoding Sanskrit.* Providence: The Sanskrit Library, 2011. 289 pp.
**Source:** The Sanskrit Library's foundational encoding-standards paper (SLP1 among eight accepted transliterations; basis of slStyle.html). Source PDF freely posted at https://sanskritlibrary.org/Sanskrit/pub/lies_sl.pdf.
**Source SHA-256:** `a07748c1cb729b2d37d77ca27296ac3002d87c70b7ba0c6a8c7549088266d769`
**Extraction:** PyMuPDF text layer, 27-09-2026 (H5510); tables are linearized — glyph cells may interleave.

**Rights-pending note (MG 30-07-2026 precedent, recorded not blocking):** © The Sanskrit Library / the author; fetched from the publisher's own openly-posted URLs for research use. Redistribution beyond research use is **pending rights confirmation — UNRESOLVED, recorded**. Derived measurements (coverage counts, crossrows) are free.

---

Linguistic Issues in Encoding Sanskrit
Peter M. Scharf
Brown University
Malcolm D. Hyman
MPIWG
June 21, 2011
iv
Scharf, Peter M. and Malcolm D. Hyman. Linguistic Issues in Encoding
Sanskrit. Providence: The Sanskrit Library, 2011.
Copyright c⃝2011 by The Sanskrit Library. All rights reserved. Repro-
duction in any medium is restricted.
Foreword
by GEORGE CARDONA
Questions surrounding the encoding of speech have been considered since
scholars began to consider the history of different writing systems and of
writing itself. In modern times, attention has been paid to such issues as
standardizing systems for portraying in Roman script the scripts used for
recording other languages, and this has given rise to discussions about
distinctions such as that between transliteration and transcription. In re-
cent times, moreover, the advent and general use of digital technology
has allowed us not only to replicate with relative ease details of various
scripts and to produce machine searchable texts but also to reproduce
images of manuscripts that can be viewed and manipulated, a true boon
to philologists in that they are thus enabled to consult and study mate-
rials with all the details found in original manuscripts, such as different
hands that can be discerned and clues to modiﬁcations made due to fea-
tures of different scripts. At the source of such endeavors lie the facts
of language: phonological and phonetic matters that scripts portray with
various degrees of ﬁdelity.
India can justiﬁably lay claim to being the home of what is doubt-
less the most thorough and sophisticated consideration of speech pro-
duction, phonetics, and phonology in ancient times. The preservation of
Vedic texts and their proper recitation according to the norms of vari-
ous groups of reciters led to the early analysis of continuously recited
texts (sa ˙mhit¯ap¯at.ha) into constituents — called pada — characterized
by phonological alternations that appear at word boundaries, including
boundaries before particular morphemes within syntactic words. A text
v
vi
FOREWORD
that includes such elements is termed padap¯at.ha. At least one such ana-
lyzed text predates the grammarian P¯an.ini, the padap¯at.ha to the R
˚
gveda
by ´S¯akalya. The padap¯at.ha related to any sa ˙mhit¯ap¯at.ha obviously derives
from the latter, its source. On the other hand, the separate padas of the
padap¯at.ha can be viewed theoretically as the source of the continuously
recited text, gotten by removing pauses at boundaries and thereby apply-
ing phonological rules that take effect between contiguous units. This is,
in fact, the theoretical stance taken by authors of texts called pr¯ati´s¯akhya,
which formulate phonological rules modifying padas in contiguity with
other padas. Thus, phonological alternations within Vedic texts were ob-
jects of concern by at least the early sixth century B.C. P¯an.ini himself
— who can hardly be dated later than around 500 B.C. — composed a
generalized grammatical work, his ´sabd¯anu´s¯asana, which includes both a
set of rules, called As.t. ¯adhy¯ay¯ı, serving to account through a derivational
system for the accepted usage of his time and place as well as certain
dialectal differences and features particular to earlier Vedic. One of the
appendices to the As.t. ¯adhy¯ay¯ı is an inventory of sounds — referred to
as the aks.arasam¯amn¯aya by early students of P¯an.ini’s work — that is
divided into fourteen sets, each set off from the others by a ﬁnal conso-
nantal marker (it), which serves to form abbreviatory terms (praty¯ah¯ara)
referring to groups of sounds with respect to phonological rules as for-
mulated in the As.t. ¯adhy¯ay¯ı.
The order of sounds in P¯an.ini’s aks.arasam¯amn¯aya shows properties
best explained as due to its being a reworking of an earlier source. The
ﬁve sets of stops in such earlier inventories, moreover, show an obvi-
ous phonetic ordering, from velar to labial, that is, an order based on
the production of sounds, from the back of the oral cavity to the front.
Moreover, pr¯ati´s¯akhyas not only state rules of phonological replacement
but also describe the production of sounds, a topic which is dealt with in
works on phonetics (´siks. ¯a) such as the ¯Api´sali´siks. ¯a of ¯Api´sali. Accord-
ingly, scholars are justiﬁed in maintaining that early Indian texts reﬂect
a sophisticated investigation of Sanskrit phonology and phonetics.
Scholars have also frequently debated whether or not writing played
a role in the composition and transmission of such early works as the
pr¯ati´s¯akhyas and the As.t. ¯adhy¯ay¯ı. There can be no doubt whatever that
the latter was later transmitted orally. It is also most plausible that P¯an.ini
himself composed and transmitted his work orally. Thus, P¯an.ini formu-
FOREWORD
vii
lates a group of rules identifying certain sounds as markers, given the
class name it, and provides that such sounds are unconditionally deleted
before any other operations apply. Had he transmitted his work in writ-
ing, thus being able to make use of script particularities such as placing
given sounds above or below a line, P¯an.ini would not have needed such
rules. That works such as P¯an.ini’s were transmitted orally does not mean,
however, that the society in which P¯an.ini lived was not literate. To the
contrary, he lived in a part of the subcontinent — ´Sal¯atura in the ex-
treme north-west — that at his time was under Persian control, and the
Achemenid rulers had inscriptions recorded. Nevertheless, a literate so-
ciety does not imply necessarily that compositions must be put in writing
and thus transmitted; later Indian traditions, for example, stress the oral
transmission, though writing was clearly known then. The earliest at-
tested written documents on the subcontinent, nevertheless, come several
centuries after P¯an.ini. These are the inscriptions of the emperor A´soka
in the third century B.C., which for the most part employ two scripts:
Br¯ahm¯ı everywhere except the northwest, where Kharos.t.h¯ı is used; in
the extreme-north-west, one ﬁnds also Aramaic and Greek used.
Peter M. Scharf and the late Malcom D. Hyman have written a valu-
able work, Linguistic Issues in Encoding Sanskrit, in which Sanskrit and
its systems of description and transmission serve as a background to more
general discussions concerning encoding of language. The authors ex-
plain the need for a work such as this and set forth their general aims in
the introduction (p. 2) as follows:
Today people use computers to manipulate linguistic and textual
data in sophisticated ways; yet current encoding systems tend to
reﬂect visual and orthographic design factors to the exclusion of
more relevant information-processing principles. Thus these sys-
tems reproduce deﬁciencies inherent in the traditional orthogra-
phies themselves. In this book we examine some fundamental is-
sues in the coding of natural language texts. We consider above all
the relation the information selected for encoding bears to natural
language structure. We focus on Sanskrit, which is characterized
by an extensive oral tradition, a highly phonetic orthography, and
a copious literature. We survey various Sanskrit encoding schemes
in past and present use and investigate their suitability for particular
applications. We conclude by advancing some concrete proposals.
viii
FOREWORD
Although this book centers on Sanskrit, it covers a great many impor-
tant issues and history relative to the general subject of encoding. The
second and third chapters take up different coding systems.
A brief
sketch of the history of Indian printing serves as a background to pre-
senting coding systems, including Roman transliterations, keyboard ar-
rangements, and Unicode. These are subjected to a critique that cen-
ters on issues of ambiguity and redundancy consequent to their being
based on Devan¯agar¯ı and Roman transliteration. The fourth chapter may
well be the most important one from a theoretical viewpoint. Here the
authors take up what they deem to be the basis for encoding. Their
discussion is organized around three axes, as follows (p. 47): Axis I:
Graphic–phonetic: Is the basic unit of the encoding a written character or
a speech sound? Axis II: Synthetic–analytic: Are units encoded as a sin-
gle Gestalt? Or are they decomposed into distinctively encoded features?
Axis III: Contrastive–non-contrastive: Are codepoints selected only for
units that contrast minimally (graphemes or phonemes)? The sixth and
seventh chapters deal with the basic issue of encoding elements of speech
or writing. The discussion of distinctive elements in chapter six is partic-
ularly wide ranging and includes succinct presentation of issues in areas
such as generative grammar and historical linguistics. Given that the
principal emphasis throughout is on Sanskrit, it is appropriate that these
discussions are preceded, in chapter ﬁve, by considerations of Sanskrit
phonetics and phonology. These include both presentations of what was
said in various pr¯ati´s¯akhyas and ´siks.¯as — including treatments of these
statements by modern scholars — and feature analysis (section 5.2.6).
In the eighth and ﬁnal chapter, the authors emphasize that, since com-
puters now are used to carry out many tasks in addition to displaying
data, this can no longer be considered the primary factor in determin-
ing a scheme for encoding. Instead, “... language should be encoded in
such a way as to facilitate automatic processing, to minimize extrinsic
ambiguity and redundancy, and to ensure longevity (p. 113).” Scharf
and Hyman then go on to discuss what they call dynamic transcoding
as well as possibilities concerning text-to-speech and speech-recognition
and higher-level encoding.
The main text is complemented by a series of appendixes, four of
which directly concern encoding. The ﬁrst of these contains thirteen ta-
bles, in which are treated not only Sanskrit phonetic and phonological
FOREWORD
ix
features but also, interestingly, reconstructions of Proto-Indo-European
phonology according to different scholars. The second, third and fourth
appendixes concern encoding schemes developed within the context of
the Sanskrit Library established as a website by Scharf: the Sanskrit Li-
brary Phonetic basic encoding scheme, the Sanskrit Library segmental
encoding scheme, and the Sanskrit Library phonetic featural encoding
scheme.
Even this brief overview should show that Linguistic Issues in Encod-
ing Sanskrit is a rich and varied work that deserves the serious attention
not merely of Sanskritists but of scholars working in several areas related
to language encoding.
George Cardona
February 19, 2011
x
FOREWORD
Preface
The current generation is witnessing a transition in the dominant medium
of knowledge transmission from print to electronics. The transition be-
gan in America and Western Europe but is quickly spreading around
the world. Naturally due to the region of its origin, conventions in the
new digital medium have been dominated by the conventions of mod-
ern Western European languages. While these conventions are making
some adjustments to suit the diversity of the world’s cultures, the world
is likewise quickly adapting to prevalent standards, and these standards
are quickly becoming entrenched. That which doesn’t ﬁt the standards is
in danger of being left behind. History has shown that in previous media
transitions the knowledge that fails to adapt to the new medium recedes
from public view to the restricted domain of the endeavoring antiquarian
research scholar or becomes irretrievably lost. Yet the digital medium is
ﬂexible and powerful; it has the potential not only to adequately mimic
the printed medium but to exceed it by innovative software design and
interactivity. The current book — and indeed much of the work of the
authors including the Sanskrit Library itself — is motivated by the de-
sire to minimize the loss of access to the knowledge of the vast heritage
of ancient India in the current media transition, to facilitate innovation
in the digital medium to make that knowledge more readily accessible,
and to inspire those who discover it to integrate that knowledge into the
dominant stream of education and culture. We believe that the insights
we have gained working to make Sanskrit more accessible should be of
use in making other major culture-bearing languages of the world more
accessible as well. Some of these insights should be useful in the com-
munication of knowledge in the digital medium in general.
xi
xii
PREFACE
Sanskrit text has been moving into the digital medium. Recent dec-
ades have witnessed the growth of machine-readable Sanskrit texts in
archives such as the Thesaurus Indogermanischer Text-und Sprachmate-
rialien (TITUS), Kyoto University, Indology, and the Göttingen Register
of Electronic Texts in Indian Languages (GRETIL). The last few years
have witnessed a burgeoning of digital images of Sanskrit manuscripts
and books hosted on-line. For example, the University of Pennsylvania
Library, which houses the largest collection of Sanskrit manuscripts in
the Western Hemisphere, has made digital images of two hundred ninety-
seven of them available on the web. The Universal Digital Library, and
Google Books have made digital images of large numbers of Sanskrit
texts accessible as part of their enormous library digitization projects.
Digitized Sanskrit documents include machine-readable text and images
of lexical resources such as those of the Cologne Digital Sanskrit Lexi-
con project (CDSL), and the University of Chicago’s Digital Dictionaries
of South Asia project (DDSA).
As oral, manuscript, and print media that have conveyed the knowl-
edge embodied in the ancient Sanskrit language make their transition into
digital media, a number of scholars have begun collaborating in the San-
skrit Computational Linguistics Consortium which has organized sev-
eral symposia since 2007. Members include linguists ﬁnding new chal-
lenges in formalizing the syntax of a free-word-order language, computer
scientists drawn to model techniques of generative grammar used by
the ancient India grammarian P¯an.ini, philologists using digital methods
to assist in critical editing, and scholars collaborating to build corpora,
databases, and tools for the use of academic researchers and commercial
enterprises. The authors of the present volume have actively participated
in and fostered this growing collaboration.
Since 1999, we have worked together to facilitate the entry, linguis-
tic processing, and display of Sanskrit texts both in print and on the Web.
Our collaboration began with the preparation of the web and print publi-
cation of Scharf’s (2002) R¯amop¯akhy¯ana and the launch of The Sanskrit
Library website1 in 2002, and continued with the International Digital
Sanskrit Library Integration project at Brown University under grants
from the National Science Foundation (NSF) 2006–2009. In July 2009
we began the project Enhancing Access to Primary Cultural Heritage
1<http://sanskritlibrary.org/>.
PREFACE
xiii
Materials of India under a grant from the National Endowment for the
Humanities, and in July 2010 we began the project Sanskrit Lexical
Sources: Digital Synthesis and Revision. Struggling to overcome the
lack of adequate encoding for Sanskrit led us to tackle the issue both
practically and theoretically. With colleagues worldwide, we prepared
a proposal to extend the Unicode Standard to allow adequate encoding
of Vedic Sanskrit. Simultaneously, we engaged in a thorough review of
the fundamental principles of encoding. We reviewed encoding princi-
ples not just for Sanskrit and not just in digital character encoding, but
considered the question broadly in terms of the means that humans com-
municate knowledge through speech, writing, print, and electronic me-
dia. The present volume is a result of these investigations. While the
linguistic material discussed is drawn primarily from Sanskrit, the ques-
tions addressed are relevant to linguistic encoding in general and should
be of interest to scholars of linguistics.
On the ﬁfth of September 2009, I received a call from my colleague
and co-author Malcolm Hyman’s wife informing me that he had passed
away suddenly the night before. It is regrettable that he did not get to see
the publication of this book that has been nearly complete for two years
and that he himself was primarily responsible for typesetting. It is far
more regrettable that the fruitful collaboration that we have undertaken
in the past decade has come to an end, and that the potential contributions
he had to make will not materialize. Malcolm had a comprehensive view
of digital humanities and prescient vision of productive directions for
research. I am grateful for what I have learned from him in the course of
our work together – even in being forced to learn TEX to bring this book
to completion. In tribute to him and in the hope that others may ﬁnd his
work instructive and inspiring, his complete curriculum vitae is included
in Appendix E of this volume.
Part of this work was supported by the NSF under grant no. 0535207.
Any opinions, ﬁndings, and conclusions or recommendations expressed
are those of the authors and do not necessarily reﬂect the views of the
NSF.
xiv
PREFACE
Contents
Foreword by GEORGE CARDONA
v
Preface
xi
Illustrations
xix
Abbreviations
xxi
1
Introduction
1
1.1
Technologies for representing spoken language
. . . . .
2
1.2
The Sanskrit language . . . . . . . . . . . . . . . . . . .
8
1.3
The Devan¯agar¯ı script . . . . . . . . . . . . . . . . . . .
9
1.4
Roman transliteration . . . . . . . . . . . . . . . . . . .
16
1.5
The All-India Alphabet . . . . . . . . . . . . . . . . . .
18
2
Existing encoding systems for Sanskrit
21
2.1
A brief history of Indian printing . . . . . . . . . . . . .
21
2.2
Legacy systems: before standards
. . . . . . . . . . . .
25
2.3
UPACCII
. . . . . . . . . . . . . . . . . . . . . . . . .
28
2.4
ISCII
. . . . . . . . . . . . . . . . . . . . . . . . . . .
29
2.5
Unicode: Indic scripts . . . . . . . . . . . . . . . . . . .
30
2.6
CS (Classical Sanskrit) and CSX (Classical Sanskrit
Extended) . . . . . . . . . . . . . . . . . . . . . . . . .
32
2.7
TITUS Indological 8-bit Encoding . . . . . . . . . . . .
33
2.8
Unicode: Indic transliteration . . . . . . . . . . . . . . .
34
2.9
7-bit meta-transliterations . . . . . . . . . . . . . . . . .
35
xv
xvi
CONTENTS
2.10 Velthuis transliteration and ITRANS . . . . . . . . . . .
36
2.11 wx . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
37
2.12 Kyoto-Harvard
. . . . . . . . . . . . . . . . . . . . . .
37
2.13 Varn.am¯al¯a . . . . . . . . . . . . . . . . . . . . . . . . .
38
3
Critique of encoding systems seen so far
41
3.1
Ambiguity and redundancy . . . . . . . . . . . . . . . .
42
3.2
Ambiguity in the encoding of accentuation . . . . . . . .
45
4
The basis for encoding: a reanalysis
47
4.1
Axis I: Spoken communication is prior to written . . . .
48
4.2
Axis II: General remarks on the units of spoken and
written language . . . . . . . . . . . . . . . . . . . . . .
52
4.2.1
Segments . . . . . . . . . . . . . . . . . . . . .
52
4.2.2
Features . . . . . . . . . . . . . . . . . . . . . .
53
4.3
Axis III: What is relevant for encoding? . . . . . . . . .
56
4.4
Encoding Sanskrit language vs. Devan¯agar¯ı script . . . .
57
5
Sanskrit phonology
61
5.1
Description of Sanskrit sounds . . . . . . . . . . . . . .
62
5.2
Phonetic and phonological differences . . . . . . . . . .
65
5.2.1
Phonetic differences
. . . . . . . . . . . . . . .
65
5.2.2
Sounds of problematic characterization
. . . . .
68
5.2.3
Differences in phonological classiﬁcation of
segments . . . . . . . . . . . . . . . . . . . . .
71
5.2.4
Differences in the system of feature classiﬁcation
73
5.2.5
Indian treatises on phonological features . . . . .
73
5.2.6
Modern feature analysis
. . . . . . . . . . . . .
75
6
Sound-based encoding
79
6.1
Criteria for selecting distinctive elements to encode . . .
79
6.1.1
Phoneme . . . . . . . . . . . . . . . . . . . . .
80
6.1.2
Generative grammar . . . . . . . . . . . . . . .
84
6.1.3
Historical linguistics . . . . . . . . . . . . . . .
85
6.1.4
Paralinguistic semantics
. . . . . . . . . . . . .
87
6.1.5
Contrastive segments . . . . . . . . . . . . . . .
89
6.1.6
Phoneme in the broader sense
. . . . . . . . . .
91
6.1.7
Contrastive phonologies . . . . . . . . . . . . .
92
CONTENTS
xvii
6.2
Higher-order protocols . . . . . . . . . . . . . . . . . .
93
6.2.1
The phonetic encoding schemes . . . . . . . . .
98
7
Script-based encoding
101
7.1
Featural analysis
. . . . . . . . . . . . . . . . . . . . . 103
7.2
Analysis of Devan¯agar¯ı script . . . . . . . . . . . . . . . 108
7.3
Component analyses of Devan¯agar¯ı script . . . . . . . . 109
8
Conclusions
113
8.1
Dynamic transcoding . . . . . . . . . . . . . . . . . . . 117
8.2
Text-to-speech and speech-recognition . . . . . . . . . . 118
8.3
Higher-level encoding . . . . . . . . . . . . . . . . . . . 119
Appendices
121
A Tables
123
A.1
Phonetic features . . . . . . . . . . . . . . . . . . . . . 124
A.2
Sounds categorized by ¯Api´sali . . . . . . . . . . . . . . 126
A.3
Sounds categorized by ´Saunaka . . . . . . . . . . . . . . 128
A.4
Sounds categorized after Halle et al. . . . . . . . . . . . 130
A.5
Sanskrit phonetics . . . . . . . . . . . . . . . . . . . . . 132
A.6
Sanskrit phonetics according to ¯Api´sali
. . . . . . . . . 134
A.7
Sanskrit phonetics according to ´Saunaka . . . . . . . . . 136
A.8
Sanskrit phonemics . . . . . . . . . . . . . . . . . . . . 138
A.9
Sanskrit sounds derived from PIE by Burrow
. . . . . . 140
A.10 PIE phonemics according to Burrow . . . . . . . . . . . 142
A.11 PIE phonemics according to Szemerényi . . . . . . . . . 144
A.12 Feature tree after Halle . . . . . . . . . . . . . . . . . . 146
A.13 Graphic features of Devan¯agar¯ı according to Ivanov and
Toporov . . . . . . . . . . . . . . . . . . . . . . . . . . 148
B
Sanskrit Library Phonetic Basic
151
B.1
Basic Segments . . . . . . . . . . . . . . . . . . . . . . 152
B.2
Punctuation . . . . . . . . . . . . . . . . . . . . . . . . 153
B.3
Modiﬁers
. . . . . . . . . . . . . . . . . . . . . . . . . 153
B.3.1
Stricture . . . . . . . . . . . . . . . . . . . . . . 153
B.3.2
Length
. . . . . . . . . . . . . . . . . . . . . . 153
B.3.3
Accent
. . . . . . . . . . . . . . . . . . . . . . 154
xviii
CONTENTS
B.3.4
Nasalization . . . . . . . . . . . . . . . . . . . . 154
B.4
Modiﬁer combinations and usage notes
. . . . . . . . . 154
B.4.1
Stricture . . . . . . . . . . . . . . . . . . . . . . 154
B.4.2
Length
. . . . . . . . . . . . . . . . . . . . . . 155
B.4.3
Surface accent
. . . . . . . . . . . . . . . . . . 155
B.4.4
Syllabiﬁed visarga and anusv¯ara accent . . . . . 156
B.4.5
Nasals . . . . . . . . . . . . . . . . . . . . . . . 156
C Sanskrit Library Phonetic Segmental
159
D Sanskrit Library Phonetic Featural
205
E
Malcolm D. Hyman
215
E.1
A Memoir by Phoebe Pettingell . . . . . . . . . . . . . . 215
E.2
Curriculum Vitae . . . . . . . . . . . . . . . . . . . . . 221
Bibliography
231
Index
261
Illustrations
1.1
Some of Gutenberg’s ligatures and abbreviations
. . . .
3
1.2
Printed text with paradigm of the Latin verb lego
. . . .
3
1.3
Newspaper composing room . . . . . . . . . . . . . . .
5
1.4
Fragment of A´soka’s 6th pillar edict . . . . . . . . . . .
10
2.1
Engraved plate illustrating the Devan¯agar¯ı script . . . . .
22
2.2
Hitopade´sa Introduction
. . . . . . . . . . . . . . . . .
23
2.3
Hindi typewriter keyboard
. . . . . . . . . . . . . . . .
26
7.1
Devan¯agar¯ı atoms . . . . . . . . . . . . . . . . . . . . . 111
xix
xx
ILLUSTRATIONS
Abbreviations
A.
P¯an.ini’s As.t. ¯adh¯ay¯i
¯A´S.
¯Api´sali´siks. ¯a
APr.
Atharvapr¯ati´s¯akhya
ASCII
American Standard Code for Information Inter-
change
BCDIC
Extended Binary Coded Decimal Interchange
Code
CA.
Catur¯adhy¯ayik¯a
CCITT
Comité Consultatif International Télpéhonique et
Télégraphique
DhP.
The P¯an.inian Dh¯atup¯at.ha
MBhK.
Kielhorn’s edition of Patañjali’s Mah¯abh¯as.ya
PIE
Proto-Indo-European
R
˚
Pr.
R
˚
kpr¯ati´s¯akhya
R
˚
V.
R
˚
gveda
TPr.
Taittir¯ıyapr¯ati´s¯akhya
VPr.
V¯ajasaneyipr¯ati´s¯akhya
Vy¯a. Pa.
Vy¯ad. i Paribh¯as. ¯avr
˚
tti
xxi
xxii
ABBREVIATIONS
Chapter 1
Introduction
Human beings express knowledge in various modes: through images in
visual art; through movement in dance, theatrical performance, and ges-
tures; and through speech in spoken language. Each of these means of
expression includes means to encode knowledge, and each is used to
express knowledge originally encoded in one of the others. Poetry de-
scribes depicted scenes, while epics narrate the events depicted there.
Manuscript images depict scenes from the epics the texts they decorate
narrate, while Kathakali enacts the epics in performance. Certain media
dominate as the primary methods for the transmission of detailed infor-
mation at different times and places. Oral tradition dominated the tradi-
tion of Sanskrit in India in the ﬁrst and second millennia B.C.E. Writing
overtook orality in the ﬁrst millennium C.E. and dominated until replaced
gradually by printing beginning in the 15th century in Europe and in the
19th century in India. Since the invention of digital electronic transmis-
sion in the 19th century, the digital medium has slowly expanded its do-
main and now is replacing printing as the dominant means of knowledge
transmission. In order to rescue the enormous body of literature extant in
print, writing, and living memory from being marginalized and becom-
ing extinct, it is vital to reﬂect on the nature of transitions in knowledge
transmission in order to understand the nature of the present transition
from the printed to digital now taking place. Consciousness of the nature
of the transition taking place will allow deliberate steps to maximize the
1
2
CHAPTER 1. INTRODUCTION
preservation of inherited learning. Such consciousness will additionally
open avenues of research not previously practicable without features of
the digital medium.
Today people use computers to manipulate linguistic and textual data
in sophisticated ways; yet current encoding systems tend to reﬂect vi-
sual and orthographic design factors to the exclusion of more relevant
information-processing principles.
Thus these systems reproduce de-
ﬁciencies inherent in the traditional orthographies themselves. In this
book we examine some fundamental issues in the coding of natural lan-
guage texts. We consider above all the relation the information selected
for encoding bears to natural language structure. We focus on Sanskrit,
which is characterized by an extensive oral tradition, a highly phonetic
orthography, and a copious literature. We survey various Sanskrit en-
coding schemes in past and present use and investigate their suitability
for particular applications. We conclude by advancing some concrete
proposals.
1.1
Technologies for representing spoken lan-
guage
Problems that arise in current encoding schemes stem from a long history
of adaptation in technologies for the visual representation of language.
The history of these technologies reveals a recurrent tendency to imitate
the appearance of earlier technologies and the possibility of information
loss at each transition (cf. Waller 1988, 262; Hockey 2000, 25).1 Recent
developments in text processing lead us to reconsider the fundamental
purpose of text encoding.
Writing emerged gradually as a technology for representing spoken
human language.2 Social and economic factors led at certain times and in
certain places to an increase in the frequency of writing and the number
1“No revolution in communications media succeeds without a transitional period during
which it simply imitates the old system. [. . . ] For example, early printed books imitated
manuscripts, and early cinema used ﬁxed cameras in imitation of the ﬁxed viewpoint of the
theatre-goer” (Waller, 1986, 74).
2The earliest “proto-writing”, attested in the ancient Near East, is associated with
economic and administrative functions; it is related only loosely to spoken language
(Damerow, 1999). For further remarks on proto-writing, see: Boltz 2006; Hyman 2006.
1.1. REPRESENTING SPOKEN LANGUAGE
3
©  «  ¢  °  ´  ¼  À  Ý
FIGURE 1.1: Some of Gutenberg’s ligatures and abbreviations (from left
to right): pp/pop, ppe, prae, pre/pri, pri, prop, qua/qui, quoque
FIGURE 1.2: Printed text with paradigm of the Latin verb lego ‘read’,
ca. 1445
of literate individuals. Historians distinguish three stages: (1) scribal
literacy, in which the technology is restricted to a specialized group of
users; (2) craftsman’s literacy, in which a majority of skilled craftspeople
use writing; and (3) mass literacy, in which the technology of writing is
known to nearly everyone (Harris, 1989).
An invention in ﬁfteenth-century Germany — the printing press —
came to have a profound and worldwide effect on the dissemination and
production of documents (Eisenstein, 1980). It is in the context of this
technology that mass literacy was achieved in Europe and other parts
of the world in the nineteenth and twentieth centuries (Vincent, 2000).
Printing with movable type closely followed the conventions of scribal
writing (Füssel, 2005, 18–19).3 Gutenberg’s 42-line Bible of 1455 em-
ployed a font of almost 300 characters, including a large number of lig-
3“The earlier printers, in their anxiety to compete successfully with manuscript books,
adopted the existing written letter forms and did not question their entire suitability as
shapes for reproduction into metal types. Nor did either printer or founder, for many years
until printing had been recognized for its own sake, make any attempt to seek or create
letter forms better adapted to type reproduction than the written characters” (Ghosh, 1983,
12).
4
CHAPTER 1. INTRODUCTION
atures, alternate letterforms, accented letters, and abbreviations (Stein-
berg 1961, 20, 30; Walden Font 1997; Füssel 2005, 17–18); see FIGURE
1.1. These had arisen in response to the demands of manuscript copy-
ing. Gutenberg’s characters were modeled upon a style of gothic script
current in the Germany of his day (Gill 1936, 32–33; Sampson 1985,
112; Kapr 1993, 20–22; Haralambous 2004, 367–368); see FIGURE
1.2. In its general layout, the printed Bible also resembled a ﬁfteenth-
century northern European handwritten codex.4 Adaptation of printing
with movable type to radically different writing systems was neither fast
nor without difﬁculty.5 When the Venetian Gregorio de Gregorii pub-
lished an Arabic-language Book of Hours (Kit¯ab s.al¯at as-saw¯a, ¯ı) in
1514, his attempt to produce the hundreds of types needed to imitate Ara-
bic calligraphy and reproduce the contextual variants of Arabic charac-
ters resulted in an un-aesthetic and partly unreadable publication (Lunde
1981, 21; Roper 2002). Arabic printing only achieved a mature form
with the types cut by Robert Granjon in the 1580s.6
The Industrial Revolution of the nineteenth century led to increased
mechanization in the production of printed materials and the transforma-
tion of basic techniques. The Mergenthaler Linotype (1886) and Lanston
Monotype (1889) allowed the keyboarding of text to replace the process
of manual composition, in which types were picked one by one from a
wooden typecase, as in FIGURE 1.3 (Steinberg 1961, 286; Schlesinger
1989; Kahan 2000).7 The layout of the keyboards on these machines,
4The British Library has made digital images of its two complete Gutenberg Bibles
available: <http://www.bl.uk/treasures/gutenberg/homepage.html>. See also the Ransom
Center’s Digital Gutenberg Project: <http://www.hrc.utexas.edu/exhibitions/permanent/
gutenberg/>.
5On the earliest printing in Greek and Hebrew, see Füssel (2005, 101–104, 107–109).
Aldus Manutius, who published the ﬁrst volume of an edition of Aristotle in Greek in
1495, closely imitated calligraphic style in his type, and made use of numerous ligatures
and abbreviations. Ingram (1966), who provides an extensive guide to ligatures and ab-
breviations in early Greek typography, remarks that when he ﬁrst encountered Renaissance
Greek printing, “I saw little resemblance between the Greek I had learned in school and
this peculiar, cramped typeface which I could not read and which often contained only an
occasional letter I could recognize” (Ingram, 1966, 371).
6On the early history of Arabic typography in Europe, see Roper (2002).
7Automation began to be introduced into type composition and casting considerably
earlier in the nineteenth century. Notable early systems were devised by William Church
(1822) and by James Young and Adrian Delambre (1840–1841) (Schlesinger 1989; Kahan
2000, 1–2).
1.1. REPRESENTING SPOKEN LANGUAGE
5
FIGURE 1.3: Newspaper composing room with workers setting text
manually from typecases, 1892
6
CHAPTER 1. INTRODUCTION
however, resembled at ﬁrst the older typecases; with time, they became
simpliﬁed and more ergonomic (AbiFarès, 2001). Another late nine-
teenth century technology, the typewriter, was ﬁrst commercially manu-
factured in the United States in the 1870s.8 The typewriter greatly ex-
panded the mechanical production of texts and allowed mechanical tech-
nology to be used for the creation of even ephemeral documents. Type-
writers reproduced many aspects of printing technology, but with several
accommodations: a greatly reduced inventory of characters, monospac-
ing, and the elimination of many possibilities for aesthetic reﬁnement.
Teletype machines, which originated around 1907, allowed for the
remote transmission and printing of text; they led eventually to stan-
dards for information encoding, most notably ASCII (American Standard
Code for Information Interchange) in the 1960s (Bemer, 1963; Smith,
1964; Mackenzie, 1980; Gaylord, 1995).9 Current digital computer key-
boards evolved from teletype keyboards, and the ﬁrst documents created
using computers resembled typewritten documents. Digital typesetting
emerged in the 1970s and made possible the creation of high-quality doc-
uments that incorporated aspects of traditional typography (Syropoulos,
Tsolomitis & Sofroniou, 2003). The desktop publishing revolution of the
1980s and 90s brought these capabilities to an international public that
continues to expand today.
8Manufacture by Remington of the typewriter designed by Christopher Latham Sholes
and Carlos Glidden began in 1873 (Beeching, 1990; Bukatman, 1993; Kahan, 2000).
9We may look even earlier, to the ﬁve-bit code for telegraphy patented in 1874 by Bau-
dot (Gillam, 2002, 43). A later rearrangement of the code was standardized in 1931 as
CCITT #2 by the Comité Consultatif International Télpéhonique et Télégraphique (now
renamed ITU-T) and extensively used by teletype machines (Mackenzie, 1980, 6, 62–64).
As a matter of historical curiosity, we may note that the ultimate antecedent of the Bau-
dot code was Francis Bacon’s so-called “bi-literal” cipher, ﬁrst published in 1623 (Strasser
1988, 88–9; Kahn 1996, 882–3).
ASCII became an American (ASA) standard on June 17, 1963. Although ASCII is gen-
erally thought of as a seven-bit code, it was actually designed as an eight-bit code with the
eighth bit unassigned (Bemer, 1963, 35). When ASA (American Standards Association)
became ANSI (American National Standards Institute), ASCII was ofﬁcially designated
ANSI X3.4-1968 (Mackenzie, 1980, 8). On the relation of ASCII to ISO 646 see Gaylord
(1995).
An interesting predecessor of character encoding is the Linotype, which redistributed
its matrices in accordance with a seven-digit binary code assigned to each type, “although
[Mergenthaler] probably did not realize the mathematical signiﬁcance” (Kahan, 2000, 206).
1.1. REPRESENTING SPOKEN LANGUAGE
7
With each shift in technology, we observe the survival of elements
from earlier technologies. To varying degrees, writing represents spoken
language (Gibson, 1972, 13); printing represents writing; the typewrit-
ten text represents the printed text; and the ﬁrst texts created with digital
computers represent their typewritten forbears. The representation of
speech in writing involves a fundamental change of medium from aural
to visual, while the representation of writing in print, printed text in typed
text, and typed text in digitally produced printed text all occur within vi-
sual media. Yet even the latter involve deliberate information recoding.
Decisions are made in the selection of a limited repertoire of certain ﬁxed
shapes to represent in print the multiplicity of variously formed charac-
ters written with the free hand. Similar decisions are made in the further
reduction of the relatively large number of print types to the relatively
small number of types used in a typewriter, and in the design of patterns
to represent characters in a dot-matrix. The issue of character coding
emerges as a problem with the technological shift from traditional man-
ual instruments such as pen, stylus, and brush to mechanized technolo-
gies: movable type, the typewriter, and the digital computer. Whereas
the earlier manual technologies allowed complete ﬂexibility in the ﬁnal
shape of characters, printing ﬁxed the repertoire of possible shapes into
sets of types (τÍποÂ: that which is struck or impressed; but also a type
as opposed to a token — cf. Plato Republic 396e). With the possibility
of data transmission, it was necessary to ensure that characters on one
machine were mapped accurately to characters on another.
At present, the digital computer offers exciting possibilities and chal-
lenges.
There is great ﬂexibility in how a text may be displayed or
printed — designers can even draw upon calligraphic principles that were
not possible within the conﬁnes of traditional printing technologies. At
the same time, display is only one of numerous functions that comput-
ers can perform. Computers can exchange textual data over space and
time; they can perform linguistic processing, such as spell-checking, ma-
chine translation, content analysis and indexing, and morphological and
syntactic analysis.10 Display for a human reader should no longer be
10Computers led ﬁrst to advances in the culture of calculation. Their application to
text and language processing followed at ﬁrst only slowly, although we ﬁnd already in
1949 the ﬁrst electronic text project in the humanities, namely, Roberto Busa’s computer-
generated concordance Index Thomisticus (Hockey, 2000, 5). Today the Index Thomisticus
lives on as the Index Thomisticus Treebank, a morphologically and syntactically annotated
8
CHAPTER 1. INTRODUCTION
considered as the primary determinant of an encoding scheme. Rather,
language should be encoded in such a way as to facilitate automatic pro-
cessing, to minimize extrinsic ambiguity and redundancy, and to ensure
longevity. Traditional orthographies — which have led time and again to
scribal corruption, readers’ misunderstandings, and entire industries of
textual criticism — are clearly not optimal. The need to encode Sanskrit,
which has for its entire history been associated with an extremely sophis-
ticated tradition of phonetic and linguistic analysis, provides us with an
exceptional opportunity to rethink some fundamental issues of language
encoding. Traditional orthographies for Sanskrit exhibit a number of in-
felicities in their design that should not be carried over into computer
encodings.
1.2
The Sanskrit language
Sanskrit is the primary culture-bearing language of India, with a con-
tinuous production of literature in all ﬁelds of human endeavor over the
course of four millennia. Middle Indo-Aryan languages (Pr¯akrits P¯al¯ı,
Apabhra ˙m´sa, etc.) and New Indo-Aryan languages (regional languages
such as Tamil, Malayalam, Marathi, Hindustani, etc.) served as the me-
dia of literary composition as well since about the third century B.C.E.
Yet the extent and diversity of literature produced in Sanskrit, the long
temporal span of its use, and the breadth of the use of the language
throughout the Indian subcontinent and Southeast Asia are unparalleled.
Indeed, extant literature in Sanskrit constitutes the largest body of liter-
ature in the world prior to the invention of the printing press. The cul-
tural heritage of Sanskrit is extant in some thirty million manuscripts and
serves as an object of study in academic institutions. The language per-
sists in the recitation of hymns in daily worship and ceremonies, as the
medium of instruction in centers of traditional learning, as the medium of
communication in selected academic and literary journals and academic
fora, and as the primary language of a revivalist community near Ban-
galore. Preceded by a strong oral tradition of knowledge transmission,
corpus that will be invaluable in the construction of new NLP tools for post-classical Latin
(see <http://gircse.marginalia.it/~passarotti>). Lamentably, the increasing availability, and
decreasing cost, of computer equipment has led (perhaps paradoxically) to an atavism that
fetishizes display.
1.3. THE DEVAN ¯AGAR¯I SCRIPT
9
records of written Sanskrit remain in the form of inscriptions dating back
only to the ﬁrst century B. C. E. — two centuries after the oldest inscrip-
tion in one of the Middle Indo-Aryan languages descended from Sanskrit
(Bühler 1896; Salomon 1998, 17, 46, 86).11 While the oldest Sanskrit in-
scriptions are in the Br¯ahm¯ı script, texts are mostly written in the many
Br¯ahm¯ı-derived scripts used today in South and Southeast Asia. Most
of the twenty-two ofﬁcially recognized languages of India also use writ-
ing systems derived from Br¯ahm¯ı, and these writing systems have been
used for writing Sanskrit and Pr¯akrits as well as regional languages. The
most common script today for writing and printing Sanskrit is Devan¯a-
gar¯ı. While the following discussion therefore selects Devan¯agar¯ı as ex-
emplar, the issues raised with regard to Devan¯agar¯ı pertain to the other
Br¯ahm¯ı-derived writing systems as well. In the nineteenth century, Eu-
ropean philologists adapted Roman script to represent Sanskrit. Most
computer encoding schemes for Sanskrit are based on either Devan¯agar¯ı
script or Romanization.
1.3
The Devan¯agar¯ı script
Devan¯agar¯ı, like the majority of the scripts of South and Southeast Asia,
is derived from the ancient Br¯ahm¯ı script (of which the ﬁrst attested in-
scriptions date from the third century B. C. E.; see FIGURE 1.4). The
Br¯ahm¯ı script is related to another ancient Indian script, Kharos.t.h¯ı,12
which appears to be adapted from Aramaic (Salomon, 1995; Scharfe,
2002; Voigt, 2005). Br¯ahm¯ı developed into a number of regional vari-
eties, partly in response to differing technologies of writing; the Proto-
N¯agar¯ı style originated in Rajasthan toward the end of the sixth century
C. E. (Dani, 1963; Sharma, 2002). By the eleventh century Devan¯agar¯ı
had become important for the transcription of Sanskrit literature (Singh
1991; Salomon 1998, 41). Today Devan¯agar¯ı is used for writing Hindi,
as well as Marathi, Nepali, and at least twenty-four other languages (Uni-
code Consortium, 2006).
11The preference for oral rather than written transmission of texts in India has often been
remarked upon. In the late seventh century the Chinese Buddhist pilgrim Yijing noted that
“The Vedas have been handed down from mouth to mouth, not transcribed on paper or
leaves” (Takakusu, 1896, 182).
12Kharos.t.h¯ı is now encoded in plane 1 of Unicode (U+10A00–U+10A5F).
10
CHAPTER 1. INTRODUCTION
FIGURE 1.4: Fragment of A´soka’s 6th pillar edict, written in Br¯ahm¯ı
script, 238 B. C. E.
Devan¯agar¯ı, like other scripts derived from Br¯ahm¯ı, has attributes of
both alphabetic and syllabic writing systems (Patel 1995; Salomon 1998,
15; Ishida 2002; Vaid 2002). Consonantal graphs imply an inherent short
/a/ vowel, unless another vowel is explicitly indicated, or the absence
of a vowel is made explicit by the vir¯ama sign (, ). With the exception
of word-initial vowels, for which independent characters exist, vowels
are indicated by means of dependent (diacritic) signs. Dependent vowel
signs are placed above, below, before, or after the character (or char-
acters) that represent the preceding consonant sound (or sounds). Thus
Devan¯agar¯ı differs on the one hand from a pure alphabetic system such
as Greek, which has independent letters to indicate vowel sounds, and on
the other from the Japanese syllabaries (Hiragana and Katakana). Greek
vowel characters α ⟨a⟩, ι ⟨i⟩, υ ⟨u⟩, etc. are as independent as consonant
characters β ⟨b⟩, γ ⟨g⟩, δ ⟨d⟩. Japanese Katakana syllable symbols «
⟨ka⟩, ­ ⟨ki⟩, and ¯ ⟨ku⟩are not related to each other in any systematic
fashion even though they represent syllables that have the consonant /k/
in common.
The basic unit of Devan¯agar¯ı writing is sometimes known as an or-
thographic syllable (or orthosyllable): that is, a sequence of any number
1.3. THE DEVAN ¯AGAR¯I SCRIPT
11
of consonant characters plus a vowel diacritic, optionally accompanied
by a sign for the nasal anusv¯ara ( M ) or release of breath, visarga (H). Al-
though modern languages written in Devan¯agar¯ı make less use of com-
plicated ligatures, sequences of up to ﬁve consonants are permissible and
occur in Sanskrit, and in Sanskrit loanwords in modern Indic languages:
• Sanskit: d:*øñÍÎÉ ÉöÁá*+.eaH da˙nks.n. voh. GEN/LOC DU M/F of d:*øñÍÎÉ ÅÅá*u da˙nks.n. u ‘mor-
dacious’
• Hindi < Sanskrit: ta;a;t~Tya t¯atsthya ‘metonymy’.
A symbol for a velar fricative [x] (jihv¯am¯ul¯ıya) or bilabial fricative [F]
(upadhm¯an¯ıya) (usually written ^) may occur instead of the visarga.
Thus, letting C stand for any consonant graph, V for any vowel graph,
and X for the anusv¯ara or visarga (or jihv¯am¯ul¯ıya, upadhm¯an¯ıya) graph,
we may describe an orthographic syllable by means of the regular ex-
pression C0−5VX?.13 Because all consonant graphs imply an inherent
vowel, a sequence of multiple consonants (consonant cluster, sa ˙myoga)
must be rendered with a single ligature, in which the shape of constituent
graphs can vary considerably. The shape of the ligature is a function
of the shapes of the constituent consonant graphs. Generally, all conso-
nants are rendered in partial form except the last (the prevocalic one).
Consonant graphs that have a vertical bar to the right are usually stacked
horizontally; round-bottomed consonant graphs, by contrast, are stacked
vertically. Sequences involving /r/ are especially complex: when /r/ oc-
curs as the initial element of a consonant cluster, it is written as a diacritic
above the line (kR ⟨rka⟩= .=, + k); elsewhere it takes the form of a diag-
onal bar slanted down to the left, attached near the bottom of the graph
that represents the (phonetically) preceding consonant (kÒ ⟨kra⟩= k, + .=).
13Notation: e0−5 denotes a concatenation of from zero to ﬁve occurrences of e; e? is
equivalent to e0−1.
Psycholinguistic research suggests “that orthographic representations are organized into
syllable-like units independently from phonological inﬂuences” (Ward & Romani, 2000,
654). Cf. Caramazza & Miceli (1990); Badecker (1996, 60 n. 5, 67). For further dis-
cussion with reference to Indic scripts see Sproat (2006); Kompalli (2007). The regular
expression given above formalizes one of the two criteria of orthographic legality: “how
many consonant letters you may have in a row before you must have a vowel” (Ward &
Romani, 2000, 654). Knowledge of orthographic legality also involves knowledge of or-
thotactic constraints on sequences of consonant characters (i. e., is a particular sequence of
characters legal or illegal?).
12
CHAPTER 1. INTRODUCTION
Some ligatures (e. g., [a ⟨ks.a⟩= k, + :Sa) have idiosyncratic forms that are
opaque in terms of their constituent analysis, and may thus be considered
“graphic idioms” (Ivanov & Toporov, 1968, 35).14 Traditional Sanskrit
orthography requires glyphs for representing more than a thousand con-
sonant clusters, and it is not uncommon for there to exist four or more
distinct styles for representing a single cluster (Wikner, 2002). Agen-
broad (n.d.) illustrates difﬁculties in unifying consonantal characters in
single ligatures. Shaw (1980, 28) reports that traditionally Devan¯agar¯ı
fonts required 500–800 types for conjunct consonants.
An examination of the visual characteristics of Devan¯agar¯ı script
helps to explain its graphotactic properties. Hamp (1959, 2) uses the
term ‘graphotactic’ for the combination of graphic units by analogy with
the term ‘phonotactic’. The two most obvious visual features of Devan¯a-
gar¯ı are the headstroke (´sirorekh¯a) that runs horizontally across the top
of a sequence of Devan¯agar¯ı consonant graphs,15 and the vertical bar that
appears at the right of many characters. The portion of the character that
is densest in information (in information-theoretic terms) is below the
14Voigt (2005, 34) argues that ⟨[a⟩originally was not a ligature, but rather was derived
directly from Aramaic ⟨s.⟩and was used to represent [ts] (possibly with the ﬁnal component
glottalized: [ts’]).
15This feature arose from the technology of calligraphy (Ghosh, 1983, 16). The head-
stroke developed from an earlier head mark, which evolved in turn from the triangle of
ink formed by the ﬁrst placement of the pen at the start of drawing a character (Salomon
1998, 31–8l; Shaw 1980, 28). In typographic terms, the headstroke in Devan¯agar¯ı is the
equivalent of the baseline in scripts such as Latin and Greek (cf. Katsoulidis 1996).
Ivanov & Toporov (1968, 35) offer a doubtful functional explanation of the ´sirorekh¯a.
They write:
The continuity of the phonetic stream is reﬂected in the continuity of the
graphic chain: separate syllabic symbols in a word and separate words
themselves are connected by an uninterrupted horizontal line. This feature
of the Indian writing can be explained not only by its phonetic character
but also by the speciﬁc character of the word in Sanskrit where a signiﬁcant
role is played by long compound words which are sometimes functionally
analogous to entire syntagms.
Such an explanation cannot be accepted because there is no correlation between the pho-
netic unity and the graphic unity of strings united by a headbar or separated by a gap in
the headbar. There is no greater phonetic unity in tasm¯atkaroti than in anyo ’gacchat even
though the latter breaks the headbar between words, and the former forms a conjunct conso-
nant running the headbar across two words. Moreover, manuscripts write entire sentences
uninterrupted regardless of word boundaries.
1.3. THE DEVAN ¯AGAR¯I SCRIPT
13
headstroke and to the left of the vertical bar.16 In only a few signs (Ta
⟨tha⟩, ;Da ⟨dha⟩, and Ba ⟨bha⟩) is the headstroke broken. Visually, we can
establish three major classes of (consonant) characters:17
1. Characters with a vertical bar at the far right (Ka ga ;Ga .ca .ja Va :Na ta
Ta ;Da na :pa ba Ba ma ya va Za :Sa .sa)
2. Characters with a vertical bar at the center (k :P)
3. Characters that hang from a small stem attached to the headstroke
(C f F .q Q d h); most of these characters have round bottoms.
The character ⟨jha⟩may belong either to group 1 (if it takes the shape
Ja) or to group 2 (if it takes the shape ½). The character ⟨la⟩may be-
long either to group 1 (if it takes the shape a) or group 3 (if it takes the
shape l). The character .= does not readily ﬁt into this typology. The fol-
lowing basic script behaviors are explicable with reference to the above
categories:
1. Ordinarily, the vertical bar at the right of a consonant character is
deleted when the consonant appears as the non-ﬁnal member of a
cluster. (e g. gma = g,a + ma)
2. But consonant characters with a vertical bar at the right that do not
extend all the way up to the headstroke are often stacked vertically,
sharing a single vertical bar. (e g. ëëÁ+;a = v,a + va)
3. Characters with a vertical bar at the center lose their rightmost
portion when they appear non-ﬁnally in a cluster. (e. g. #pa = k, + :pa)
4. Round-bottom characters are typically stacked above the graph for
the following consonant in a cluster. (e. g. ææ* = f, + f)
(a) A consonant that follows /d/ is drawn using the tail of d ⟨da⟩
as its right vertical bar. (e. g. dõââ = d, + ba)
16Within-character information density may be expected to vary between different writ-
ing systems (Shimron & Navon, 1980).
17Cf. Mohanty (1998); Bansal & Sinha (1999); Govindaraju, Setlur, Khedekar, Kom-
palli, Farooq & Vemulapati (2004).
14
CHAPTER 1. INTRODUCTION
(b) A consonant that follows /H/ is drawn within the open circle
that comprises the lower half of the h, utilizing the roof and
right of this circle as its upper horizontal or right vertical bar.
(e. g. Ì = h, + l)
Vowels are mostly written in Devan¯agar¯ı with diacritics, which may
appear above, below, to the left, or to the right of the onset of the or-
thographic syllable. For example, diacritics for the vowels /e/ and /o/
are written above (:ke
;kE ), below (ku
kU
kx
kX
kw ), to the left (;
a;k), or to
the right (k+:a k
 +:a k+:ea k+:Ea) of the consonant character k ⟨ka⟩. Utterance-
initially, however, independent vowel characters are used. This practice
seems to reﬂect the inﬂuence of Semitic scripts (Scharfe 2002; Voigt
2005, 44). In Semitic writing, words do not begin with a vowel; this
is a consequence of Semitic word structure, in which only consonants
are allowed in word-initial position (Miller, 1994, 56).18 Two consonant
symbols, aleph (representing a glottal stop) and , ayin (representing a
pharyngeal or epiglottal voiced continuant) (McCarthy, 1994), that are
frequent word-initially in Semitic are likely not to have been recognized
as representing consonant sounds by speakers of languages that lacked
the phonemes represented (cf. Driver 1976, 154–155, 178–179; Miller
1994, 46).19 Thus the Br¯ahm¯ı characters that developed into Devan¯a-
gar¯ı A/A;a derive from the Aramaic aleph (for which the Aramaic name
was ¯alaph), and the characters that developed into O;/Oe; derive from the
Aramaic , ayin (for which the Aramaic name was , ¯en). The charac-
ters   A;ea A;Ea are secondary developments from A. Characters for
independent r
˚
and au are not attested until the second half of the ﬁrst
millennium C. E. (Scharfe, 2002, 393). In Kharos.t.h¯ı initial vowels are
formed from attaching the dependent vowel signs to a character derived
from aleph. Although Indian grammarians do not include the glottal stop
in their phonologies, we may conceive of the independent initial vowel
signs (A A;a I IR o     O; Oe; A;ea A;Ea) as representing glottal stop
+ vowel,20 an idea apparently anticipated already by Lepsius (see Whit-
18For the Arabic grammarians’ treatment of this fact, see Hadj-Salah (1971, 74); Al-
Nassir (1993, 22).
19A number of Middle and Modern Aramaic dialects show , ayin having weakened into
the glottal stop [P] (Kaufman 1984, 93 n. 40; Hoberman 1985, 224).
20In Kharos.t.h¯ı initial consonants are formed from attaching the dependent vowel signs
to a character derived from aleph (Scharfe, 2002, 393).
1.3. THE DEVAN ¯AGAR¯I SCRIPT
15
ney 1861, 328).21 The independent vowel signs appear word-internally
in the rare (Salomon, 1998, 15 n. 26) Sanskrit lexical items that contain
a sequence of vowels in hiatus, e .g. :pra;o+.ga praüga ‘front part of the shafts
of a chariot’, and in compounds, e. g. manaA;apa mana¯apa ‘gaining the heart,
attractive, beautiful’.
Nasalization and pitch accents are written in Devan¯agar¯ı with addi-
tional diacritics. Nasalization is written by a half-moon plus dot (candra-
bindu) over the vertical bar of the nasalized sound (e. g. ta;<a;(ãÉa t˜¯a´sca). The
accentual systems of Vedic schools vary. The most widely used, the R
˚
g-
vedic accentual system, generally places a horizontal stroke beneath the
CV portion of an orthographic syllable that includes a low-pitched vowel
(anud¯atta) (e. g. k! ), and a vertical stroke above the CV portion of an or-
thographic syllable that includes a circumﬂexed vowel (svarita) (e. g. k ).
Short and long aggravated svaritas (kampa) use the numerals 1 and 3 in
addition (nya1! ; :Sya;e!a3! ). The high pitch (ud¯atta) is left unmarked. Other
accentual systems employ additional diacritics, including various signs
above, below, to the left, to the right, through the middle of, and around
the CV portion of an orthographic syllable that includes a circumﬂexed
vowel; within a given system, various signs differentiate particular types
of circumﬂex accent. Diacritics added to the visarga symbol indicate
high pitch, low pitch, or circumﬂex.22
21Owing to sandhi, initial independent vowel signs will be written only (1) in hiatus,
i. e. the environment V##V; or (2) in pausa (initially in a major phonological phrase). Al-
though the glottal stop is not a phoneme of English, it commonly occurs in inter-word
hiatus, e. g. heavy oak; steady awning — N. B. that the glottal stop is not ordinarily real-
ized as full glottal closure (Hillenbrand & Houde, 1996); cf. Hadj-Salah (1971, 73 n. 63).
Similar phonetics is likely to obtain in Sanskrit. Note that inter-word hiatus is often consid-
ered exceptional — careful authors of ancient Greek prose, for example, avoided it entirely
(Benseler, 1841). Many languages typically eliminate within-word hiatus (Clements, 1990,
301) or disallow it entirely (Romani & Calabrese, 1998, 102).
22Cardona 1997, li–lxiv; Witzel 1974.
16
CHAPTER 1. INTRODUCTION
1.4
Roman transliteration
As Sanskrit studies became important in the West, European scholars de-
vised methods to transliterate Sanskrit text in Roman script. The early
history of efforts to standardize such methods are described in the pref-
ace to the dictionary of Monier-Williams (1872). The eminent Sanskritist
William D. Whitney made some comments in 1880 in the Proceedings of
the American Oriental Society (Whitney, 1880). Whitney accords West-
ern scholars great license, writing, “the language is written in India, to
no small extent, in whatever alphabet the writers are accustomed to em-
ploy for other purposes; and there is no reason why we may not allow
ourselves to do the same” (Whitney, 1880, li). He considers questions of
how to mark vocalic quantity in Romanized Sanskrit, examines the ques-
tion of how the diphthongs should be presented, prefers r. (or Lepsius’
r
˚
) to r.i (likewise l. or l
˚
to lr.i — characterized as “that monstrous absur-
dity”), and devotes considerable discussion to the matter of anusv¯ara. He
concludes, “To sum up brieﬂy: the items to be most strongly urged, as
involving important principles, are the use of r. and s. for the lingual vowel
and lingual sibilant respectively; of next consequence, for the sake of uni-
formity, is the adoption of the signs c, j, y, ç for the palatal sounds; the
designation of long vowels, of the diphthongs, of the nasals, are minor
matters, which will doubtless settle themselves by degrees in the right
manner” (Whitney, 1880, liii).
Of particular importance as regards standardization of the schemes
used by European scholars was the Geneva Oriental Congress of 1894
(Wujastyk, 1996). Contemporary schemes for Romanizing Sanskrit are
quite similar to those employed in the nineteenth century and are charac-
terized by the following conventions:
1. Sanskrit sounds that correspond to normal values for Roman letters
are represented by those letters (e. g. b = [b]).
2. The letter h, which by itself indicates a phoneme /H/, is used also
to indicate the aspirate series of stops in digraphs such as bh.
3. The retroﬂex consonants are indicated with an underdot (e. g. t.).
4. A macron indicates a long vowel (e. g. ¯a).
5. The palatal nasal is written ñ; the velar, ˙n.
1.4. ROMAN TRANSLITERATION
17
6. The palatal sibilant is written ´s (formerly, ç).
7. Vocalic/syllabic l and r are written with an undercircle or underdot
(l
˚
r
˚
).
8. The anusv¯ara is written m. or ˙m; the visarga, h. ; jihv¯am¯ul¯ıya and
upadhm¯an¯ıya, h¯ and h
ˇ
, respectively.
9. Acute and grave accent marks indicate the ud¯atta and independent
svarita accents, respectively (yé, kvà); the dependent svarita (¯ı in
agním ¯ıl.e) and the anud¯atta (nah. ) accent are usually left unmarked.
Several published standards relate to the Romanization of Sanskrit text
written in Devan¯agar¯ı or other scripts.
These include the Library of
Congress transliteration (Barry, 1997, 186–7) and ISO 15919 “Translit-
eration of Devanagari and related Indic scripts into Latin characters”.23
Unicode, as part of its CLDR (Common Locale Data Repository) project
released Unicode Transliteration Guidelines in 2008.24 In the case of In-
dic scripts, these guidelines closely follow ISO 15919. The intent is that
native script representations and transliterations be round-trippable.
It is important to distinguish between strict transliteration and Ro-
manization. The former refers to a mapping at the graphic level: some
character or characters in one script (e. g. Roman) are substituted for
some character or characters in another (e. g. Devan¯agar¯ı). The trans-
literation reﬂects idiosyncrasies of the source orthography. Thus in Rus-
sian the name William is sometimes transliterated as Уиллям, despite
the fact that the second ⟨л⟩has no phonetic signiﬁcance in Russian. A
Romanization, on the other hand, renders linguistic content using the let-
ters of the Roman alphabet; these letters stand for sounds of the source
language. In designing a Romanization, one does not consider the non-
Roman orthography of the source language.
Romanizations often suffer from the problem that the phonetic inven-
tory of the source language differs considerably from (and is larger than)
the set of sounds conventionally indicated by Roman characters. Three
solutions get around this problem: (1) the use of digraphs, trigraphs, or
“polygraphs”; (2) the use of diacritic marks; and (3) the creation of new
23ISO documents are available from the International Organization for Standardization
(website: <http://www.iso.ch/>).
24<http://www.unicode.org/cldr/transliteration_guidelines.html>.
18
CHAPTER 1. INTRODUCTION
letters (Jones, 1942, 2–3). Each of these solutions has its weaknesses.
Bartholomew Ziegenbalg in his Tamil grammar of 1716 spells the pre-
palatal affricate (a unitary phoneme) of Tamil as ⟨ytsch⟩(Firth, 1936,
34). Even today, it is customary in Germany to render with the hepta-
graph ⟨schtsch⟩the phoneme written in Cyrillic as ⟨щ⟩. Clearly the use
of “polygraphs” can be uneconomical. The use of diacritics can present
extraordinary challenges to the typesetter, as when one wishes to indicate
in a Romanized text that a Sanskrit vowel is long (macron), nasalized
(tilde), and accented; in this case three diacritics must be stacked. The
creation of new characters is always an option; but after one has added
enough new characters, one has a new script — no longer Roman.25
1.5
The All-India Alphabet
The British linguist J. R. Firth served as professor at the University of
Punjab in Lahore from 1920 to 1928 and returned to India in the late
1930s to spend a year studying Gujarati and Telugu (Anderson, 1985,
177). During his time in India, Firth became extremely interested in the
development of a new orthography for Indian languages. This interest led
to the creation of Firth’s All-India Alphabet, intended as writing system
for the languages of the Indian subcontinent. The All-India Alphabet is
an adaptation of the Roman alphabet, with a number of additional modi-
ﬁed letters; a few letters borrowed from other scripts, such as Cyrillic and
Greek; and several symbols borrowed from the International Phonetic
Alphabet (IPA). Upon occasion, Firth, rather grandiloquently, spoke of
his scheme as “World Orthography” (Firth, 1936).
Firth’s Alphabet aimed at addressing the problem of mass illiteracy
in colonial India (Jones, 1942, 1). In addition, British intellectuals in
India considered that a national orthography would contribute to national
unity. In the words of Daniel Jones, “For the promotion of an All India
mind, a sound All India Alphabet developed from the world-wide Roman
alphabet would be a powerful implement” (Jones, 1942, 4). Firth claimed
that the Alphabet was “designed on linguistic principles for the main
languages of India entirely from the Indian point of view” (Harley, 1955,
25Yet even the Romans themselves proposed the addition of new characters to their al-
phabet (Ryan 1993; Desbordes 1990). On more recent created characters for the Latin
alphabet, see Abercrombie (1981).
1.5. THE ALL-INDIA ALPHABET
19
x). The Alphabet was also associated with progress in communication
technologies: “the adoption of a Romanic system [...] would enable
Indians to bring into use for their own languages such modern devices as
the teleprinter and tape machine, with consequent great advantage to the
Indian Press” (Jones, 1942, 17).26
Despite the ambitions of Firth, the Alphabet was scarcely used. Sev-
eral textbooks made use of it, including A. H. Harley’s Colloquial Hin-
dustani (Harley, 1955) and T. Grahame Bailey’s Teach Yourself Urdu
(edited by Firth and Harley, and originally entitled Teach Yourself Hin-
dustani) (Bailey, Firth & Harley, 1956). The Alphabet comprised a core
set of characters, with extensions added for sounds present only in spe-
ciﬁc Indian languages. Firth worked out orthographies based on the Al-
phabet for Hindustani (Hindi and Urdu), Marathi, Gujarati, Tamil, Tel-
ugu, and Sinhalese (the last devised by Jones and Perera) (Jones, 1942,
13), as well as Burmese and Persian (Firth, 1936). Occasionally Firth’s
orthography appeared in the publications of linguists associated with the
School of Oriental and African Studies (SOAS) at the University of Lon-
don, for instance Allen (1951).
Although the All-India Alphabet seems not to have been used for
Sanskrit, Firth included symbols for spelling Sanskrit words as they ap-
pear in Hindi. Moreover, W. Sidney Allen adapted the Alphabet for San-
skrit (Allen, 1953). The Alphabet was designed as a scientiﬁc orthog-
raphy, “an alphabet that embodies all the latest ﬁndings of phonetics,
linguistics and psychology, and which satisﬁes the demands of the ty-
pographer, the typewriter, and the calligraphist” (Jones, 1942, 10). The
Alphabet tends to represent phonological rather than phonetic distinc-
tions (Firth, 1936, 539). Surface morphophonological alterations and
phonetic differences are not supposed to be represented in the orthogra-
phy (Jones, 1942, 5–6). On the whole Firth aims at representing single
sounds with single characters, but he departs for various reasons, em-
ploying at times digraphs and even trigraphs (e. g. phw27 for a bilabial
aspirated stop with velar co-articulation in Burmese) (Firth, 1936, 543).
The design of the Alphabet is motivated by ease of reading (legibility
26Such arguments were once made also for China and Japan (Ramsey 1989, 143–154;
Trigger 1998, 41). They are clearly vitiated by the high levels of literacy current in these
countries as well, of course, as the tremendous economic growth.
27Text in the All-India Alphabet is conventionally printed in boldface.
20
CHAPTER 1. INTRODUCTION
and distinctness) as well as ease of writing (Jones, 1942, 10–11). Dia-
critic marks are eschewed, as they hinder reading and cause additional
problems for printers. The inventory of characters is kept small, to make
typesetting and typewriting more convenient.
Most stop consonants are represented in the All-India Alphabet as
they are in conventional Romanizations. Aspirated stops are represented
by digraphs kh, ch, etc. Retroﬂex sounds are indicated with a “tail”, as
ú, ã, ù. The palatal sibilant is indicated by S (capital form Σ). The basic
vowels of Hindi are represented by @ [@], a [a], y [I], i [i], w [U], u [u], e
[E], @y [e], o [O], @w [o] (IPA equivalents are given here in brackets for
reference). Nasalization of vowels (anun¯asika, @nwnasyk) is indicated
by N following the basic vowel graph (@N etc.). The All-India alphabet is
duo-case, with distinct upper- and lower-case letterforms.
In Allen’s use of the Alphabet for Sanskrit (Allen, 1953), the oral
stops are represented as described above for Hindi. The nasals are indi-
cated by N, ñ, ï, n, m. Here Allen follows Firth’s design for Marathi,
where N is preempted for the velar nasal, and M becomes the marker of
nasalization (Jones, 1942, 13). Allen uses h for both the voiced phoneme
/H/ and the (voiceless) visarga. The symbols a, i, r., l., u are used for
the Sanskrit vowels. Allen follows Firth’s orthography for Tamil in rep-
resenting the long vowels through doubling: aa etc. (Jones, 1942, 15).
The long vocalic ¯r
˚
is indicated by r.r. The diphthongs are represented
conventionally by e, ai, o, au.
Chapter 2
Existing encoding systems
for Sanskrit
2.1
A brief history of Indian printing
The Jesuits introduced printing to India, when a printing press (appar-
ently en route to Abyssinia) came to stay at Goa in 1556.1 In 1578,
Tamil types were created, and St. Xavier’s Doutrina Christã was printed
in Tamil, in sixteen pages. By the end of 1577 João Gonçalves had
prepared a repertoire of about 50 pieces of Devan¯agar¯ı type, but these
languished after his death in the subsequent year. During this period,
books were predominantly published in European languages such as Por-
tuguese. The press at Goa functioned until 1674. “Printing in the Deva-
n¯agar¯ı characters in Goa started only in the second half of the nineteenth
century” (Priolkar, 1958, 27).
The earliest printing of Devan¯agar¯ı took place in Europe.
In the
seventeenth century, works such as Athanasius Kircher’s China Illus-
trata (Amsterdam, 1667) reproduced Devan¯agar¯ı by the technique of
engraving (see FIGURE 2.1). The Orientalisch- und Occidentalischer
Sprachmeister of Johann Friedrich Fritz and Benjamin Schulze (Leipzig,
1This paragraph is based on Priolkar (1958, 3–27). On the international spread of print-
ing at this time see Füssel (2005, 70).
21
22
CHAPTER 2. EXISTING ENCODING SYSTEMS
FIGURE 2.1: Engraved plate illustrating the Devan¯agar¯ı script from
Athanasius Kircher, China Illustrata, 1667.
2.1. A BRIEF HISTORY OF INDIAN PRINTING
23
FIGURE 2.2:
Hitopade´sa Introduction 2ab excerpted from Charles
Wilkins, A Grammar of the Sanskr˘ıta Language, 1808 (set with
Devan¯agar¯ı type of the author’s design).
1748) included two hundred translations of the Lord’s Prayer in various
languages and writing systems, Indian ones among them (Firth, 1936,
519). The ﬁrst movable types for Devan¯agar¯ı were successfully cast in
the 1740s in Rome for the press of the Congregatio de Propaganda Fide
(Glaister 1979, 134; Shaw 1980, 29).2
The ﬁrst important book printed in an Indic script is commonly held
to be the Bengali grammar of Nathaniel Brassey Halhed (1751–1830),
published in 1783, with type cast by Charles Wilkins (b. 1749–1750;
d. 1836) (Smith 1885, 211, 242; Priolkar 1958, 51–53; Diehl 1968;
cf. Firth 1946, 119–120), who later designed the ﬁrst truly serviceable
Devan¯agar¯ı type (see FIGURE 2.2) (Diehl, 1968, 335–336).
Printed
Devan¯agar¯ı in India appears as early as 1789, with The New Asiatick
Miscellany published by the Chronicle Press of Calcutta (Shaw, 1980,
29).
In 1804 the English shoemaker and Baptist missionary William Car-
ey published a Sanskrit reader at Serampore, thus making, in the words
of H. T. Colebrook, the “ﬁrst attempt to employ the press in multiply-
ing copies of Sanscr˘ıt books with the Dévanagarí character” (Windisch,
1917, 28). A Devan¯agar¯ı font subsequently produced (in 1806) under
the supervision of Carey contained nearly a thousand character combina-
tions (Smith 1885, 243; Priolkar 1958, 59, 63, 65). Carey’s Devan¯agar¯ı
2On the early history of Devan¯agar¯ı typography in Europe, see Windisch (1917, 70,
78–79); Glaister (1979, 134–136); Shaw (1980).
24
CHAPTER 2. EXISTING ENCODING SYSTEMS
was used not only for setting Sanskrit, but also for vernacular languages
such as Marathi, Hindi, Nepali, and Gujarati (Shaw, 1980, 30).
Hot-metal typesetting came to India in the 1920s when the Mergen-
thaler Linotype Company started shipping Indic fonts for its linecasters
(Ross, 2002). The Monotype Corporation cut a 12 point Devan¯agar¯ı font
for hot-metal typesetting as early as 1923 (Shaw, 1980, 28). Hot-metal
technology, however, necessitated “severely restricted character sets, the
lack of kerning, and the inability to position the subscribed or super-
scribed vowel signs” (Ross, 2002).3 The Indologist W. Norman Brown
(1892–1975), founder of the ﬁrst South Asia area studies program in
the United States (at the University of Pennsylvania), served as consul-
tant to the Merganthaler Linotype Company in the 1930s and subsequent
decades. Brown considered script reform measures that would ease the
transition to modern technologies such as hot-metal typesetting.4 The
Devan¯agar¯ı script reform committee of Uttar Pradesh made several rec-
ommendations (1940), including:
1. to abandon the practice of vertical stacking of characters in con-
juncts; instead characters with a vertical bar should form conjuncts
using their combining form (without the vertical bar), and con-
juncts involving other consonants should be indicated by means of
the vir¯ama;
2. to eliminate the exceptional directionality of certain characters: ⟨i⟩
is to be written with a new symbol that follows the consonant, ⟨r⟩
in clusters is to be replaced by a new symbol that does not disrupt
the linear order;
3. to indicate anusv¯ara by a small circle at the right (Brown, 1953, 4).
The aim of these reforms was to reduce the number of pieces of type
needed to set Devan¯agar¯ı. (Traditionally, Devan¯agar¯ı type required four
3“The Linotype mechanism put constraints on type face design because the machine
could not emulate all the features of manuscript; in particular, where adjacent elements
overlap vertically” (Kahan, 2000, 190). See also Ghosh (1983, 10).
4Politicians of course had their say in the matter. Jawharlal Nehru for some time con-
sidered the beneﬁts that might follow from adopting the Roman alphabet. Gandhi sought
to replace the independent vowel signs of Devan¯agar¯ı with the sign A, together with the
dependent vowel signs.
2.2. LEGACY SYSTEMS: BEFORE STANDARDS
25
typecases, compared to the two needed for Roman.) The proposal of the
committee required only 110 types (Brown, 1953, 5):
full consonant forms and independent vowel forms
42
half forms of consonants
26
special conjunct forms
1
dependent vowel forms
14
punctuation
8
numerals
10
miscellaneous signs
9
Several Hindi newspapers adopted certain of the committee’s sugges-
tions, although none adopted all (Brown, 1953, 5).5
2.2
Legacy systems: before standards
Modern text-processing technology arose in the English-speaking world
and assumed as a norm the use of the Roman alphabet with few or no
diacritics. CCITT #2, BCDIC version 2, and the original version of
ASCII, as well as the original ISO 7-bit code, for instance, reserved three
code positions for national use, in order to accommodate Western Euro-
pean orthographies such as Danish, German, Finnish, Norwegian, and
Swedish, which require (assuming only a single case, rather than sepa-
rate lower- and upper-case sets) only three characters with diacritics (e.g.
Ä-Ö-Ü or Æ-Ø-Å) (Mackenzie, 1980, 64, 90, 238, 411–418, 450–451).6
While the typewriter was an efﬁcient instrument for composing English
text, its adaptation to some non-Western scripts required considerable
effort and compromise (Krishna, 1991). A number of keyboard layouts
were designed for Hindi use. Such typewriters provided an early model
for computer text processing, and their design is still reﬂected in some
computer keyboard layouts.
Examining a typical Hindi typewriter keyboard (FIGURE 2.3)7 re-
veals that many keys when struck without the shift modiﬁer generate the
5For discussion of similar orthographic reforms in the Middle East, see Mahmoud
(1979).
6See for instance the German code DIN 66003-1967, Informationsverarbeitung 7-Bit
Code.
7For some other Hindi typewriter layouts, see Beeching (1990, 58). See also Bhatia
(1974).
26
CHAPTER 2. EXISTING ENCODING SYSTEMS
FIGURE 2.3: Hindi typewriter keyboard
full forms of consonants, while the same keys struck with shift depressed
generate the half-forms used in the construction of ligatures. Certain in-
dividual graphs can only be typed with a combination of keystrokes. For
instance the aspirate :P ⟨pha⟩must be typed as: (1) :pa ⟨pa⟩and (2) the
loop that appears to the right of the vertical bar. Thus the Devan¯aga-
r¯ı typewriter decomposes characters into their visual constituents.8 Of
course, many of the conjunct forms and diacritics traditionally used in
high-quality Sanskrit typography simply cannot be reproduced with such
a typewriter.
Text processing software on the digital computer brought the possi-
bility of an expanded character repertoire and the possibility of shifting
the burden of tedious composition processes from human to machine. Yet
in the absence of standardized encodings and text layout software ade-
quate to meeting the challenges of complex scripts, the ﬁrst generation
of Devan¯agar¯ı fonts made use of completely proprietary, non-standard
encodings, were not able to unify non-distinctive glyph variants under a
single grapheme,9 and required that text be stored (and, often, typed) in
8Similarly, the typewriter keyboard designed by the Arabic script reformer Ahmed
Lakhdar-Ghazal uses three symbols as the appendices of word-ﬁnal Arabic letters; tra-
ditionally, the combination of letterform and appendix has been considered a variant form
of a single grapheme (Mahmoud, 1979, 111).
9The term grapheme denotes a minimal distinctive unit of visual language; cf. Pulgram
1951; Hamp 1959. The term has been used in various ways by (psycho-)linguists. This
2.2. LEGACY SYSTEMS: BEFORE STANDARDS
27
display order rather than phonetic order.10 In the absence of specialized
software, the end-user was often required to deal manually with such te-
dious issues as choosing which alternate shape for a dependent vowel
aligned most harmoniously with a particular consonant graph.
The Devan¯agar¯ı typewriter and the ﬁrst generation of Devan¯agar¯ı
fonts provided solutions that were more or less adequate for the dis-
play and printing of texts. But these systems did not adequately ad-
dress such problems as: the robust electronic interchange of data, fa-
cilitation of searching and collation, linguistic applications (e. g., spell-
checking, morphological analysis, machine translation), and automatic
transliteration and transcoding. By the end of 2009, India had about
eighty-one million Internet users, which represents approximately 7% of
the population.11 Even so, many Indian-language web pages still require
fonts with non-standardized, idiosyncratic encodings that severely im-
pede many of the beneﬁts commonly associated with the World Wide
Web (Mujoo, Malviya, Moona & Prabhakar 2000; Singh 2006). Authors
working for a UNESCO study on linguistic diversity on the Web note the
need for the adoption of standards:
Although there exist national standards, hardware vendors, font de-
velopers and even end-users have been creating their own character
code tables which inevitably lead [sic] to a chaotic situation. The
creations of so called exotic encoding scheme [sic] or local internal
encoding have been accelerated particularly through the introduc-
tion of user-friendly font development tools. Although the appli-
usage has been studied by Henderson (1985), who identiﬁes a Sense 1: the grapheme is
“the minimal contrastive unit in a writing system” (135); and a Sense 2: the “grapheme is
comprised of a letter or letters that refer to or correspond to a single phoneme in speech”
(135). Throughout we follow Henderson’s Sense 1; thus grapheme is parallel to phoneme,
allograph to allophone, and graph to phone. It is worth remarking here that even the term
“letter” has traditionally led to some confusion; see Abercrombie (1949).
10While the directionality of Devan¯agar¯ı is generally left-to-right, the short /i/ vowel
is written to the left of the onset consonant(s) in its orthographic syllable; thus -nti is
written ; //
a;nta. Moreover, in a sequence of /r/ + consonant(s), the /r/ is written above the ﬁnal
constituent of the orthographic syllable: ;Da;}yRa dharmya ‘suitable, legitimate, virtuous’, k+.a;Ra
kartr¯ı ‘female agent’.
Primary users of Devan¯agar¯ı, however, sometimes ﬁnd the visual order of graphs “nat-
ural” (in as much as it is the order that they follow when writing by hand) and become
confused if they are required to input the /i/ (for example) in its phonetic position (Joshi,
Ganu, Chand, Parmar & Mathur, 2004).
11<http://www.internetworldstats.com/asia/in.htm>.
28
CHAPTER 2. EXISTING ENCODING SYSTEMS
cation systems working in these areas are not stand-alone systems
and are published widely via the Web, the necessity for standard-
ization has not been given serious attentions [sic] by users, ven-
dors and font developers (Mikami, abu Bakar, Sonlert-lamvanich,
Vikas, Pavol, abdul Rozan, János & Takahashi, 2005, 99).
2.3
UPACCII
In the early part of 1983 Pijush K. Ghosh was a guest of the digital typog-
raphy project at Stanford University. Ghosh worked to create fonts that
would allow Indic languages to be set using Donald Knuth’s TEX sys-
tem. Ghosh (1983, 23) recognized the need for “[t]he design of efﬁcient
internal codes for the characters of a script for information processing,
storage and transmission.” The solution was a Universal Phonetic Atom
Code Chart for Information Interchange (UPACCII), based on ASCII
(Ghosh, 1983, 26). Ghosh includes the control characters at their normal
ASCII positions (000–037).12 He largely maintains the ASCII characters
at 040–077 in their normal positions, substituting only the candrabindu
at 044 for ⟨$⟩, the anusv¯ara at 046 for ⟨&⟩, and the danda at 056 for ⟨.⟩.
From 0100–0107 he places the visarga, accent marks, punctuation, the
avagraha, and the short vowel ⟨A⟩. The consonants ⟨k⟩through ⟨;Da⟩are
positioned at 0110–0132. The ASCII sequence is preserved from 0133–
0140. The consonants ⟨na⟩through ⟨h⟩are at 0141–0156. The vowels
(save ⟨A⟩) follow at 0157–0170: ⟨A;a⟩, ⟨I⟩, ⟨IR⟩, ⟨o⟩, ⟨⟩, ⟨⟩, ⟨O;⟩, ⟨Oe;⟩,
⟨A;ea⟩, ⟨A;Ea⟩. At 0171 Ghosh places the vir¯ama, at 0172 a BREAK charac-
ter to prevent ligation (parallel to ZWNJ U+200C in Unicode). Normal
ASCII values continue from 0173–0177.
Ghosh rightly makes his code independent from input (keyboarding)
and output (printing). For the former, he proposes an ergonomic key-
board layout inspired by the Dvorak layout; for the latter he proposes a
print code chart (Ghosh, 1983, 28, 31). UPACCII is basically phonetic
in nature, so that there are not (as in ISCII and Unicode) separate char-
acters for independent vowels and for dependent vowel m¯atras. Ghosh’s
encoding is intelligent and possesses some strengths in comparison with
contemporary encodings that are widespread, but it was never adopted as
12Character codes are indicated here in octal notation, like that used for constants in the
C programming language.
2.4. ISCII
29
a standard or used in other projects. The code is inadequate for Sanskrit,
since it provides no way to represent ¯r
˚
, l
˚
, etc.
2.4
ISCII
The Indian Script Code for Information Interchange (ISCII) is an Indian
national standard; the ﬁrst version was published by the Indian Depart-
ment of Electronics (DOE) in 1983 (Bhatt, n.d.). More recent versions
have been published in 1986, 1988, 1991, and 1998. ISCII is designed
to support Devan¯agar¯ı as well as nine other Br¯ahm¯ı-derived scripts: Gu-
jarati, Panjabi, Assamese, Bengali, Oriya, Telugu, Tamil, Malayalam and
Kannada. These scripts are the primary means of writing for the twenty-
two nationally recognized languages of India, with the exception of those
that are primarily written in Perso-Arabic script, viz. Urdu, Kashmiri,
Sindhi (Singh, 1997).
ISCII employs a single set of codepoints for ten distinct scripts. Thus
the syllable ⟨ka⟩is encoded identically whether it is written in Devan¯a-
gar¯ı, Gujarati, or Malayalam. The general structural principles of ISCII
are based on those of the Br¯ahm¯ı-derived scripts. In general:
• Consonants imply /a/, unless overridden by either an explicit vowel
or the HALANT character (= vir¯ama, i.e. the ∅vowel).
• Separate codepoints exist for independent and dependent vowel
signs.
• Characters are encoded in logical (phonetic) rather than visual or-
der.
ISCII is an abstract encoding that does not specify the particular glyphs
used to represent the underlying character stream. Proper rendering of
ISCII-encoded text requires knowledge of the script behaviors for a par-
ticular writing system. ISCII-1991 (IS 13194:91) deﬁnes three important
control characters (Bureau of Indian Standards, 1992):
1. INV: an abstract “invisible” consonant allows for the rendering of
diacritic signs which would normally have to be positioned with
respect to a particular consonant graph.
30
CHAPTER 2. EXISTING ENCODING SYSTEMS
2. EXT: introduces extensions, including the Vedic extensions (31
symbols) speciﬁed in Annex G: special signs for jihv¯am¯ul¯ıya, upa-
dhm¯an¯ıya, and visarga; special signs for anusv¯ara; diacritics for
accents (varieties of ud¯atta, anud¯atta, svarita, and kampa); and an
abbreviation sign and ﬁller mark. These symbols do not exhaust
the repertoire employed by the various Vedic schools.
3. ALT: preﬁxes a character or script attribute code that allows for
character styles such as boldface or italic and for Indic script se-
lection such as Bengali or Gujarati.
2.5
Unicode: Indic scripts
The Unicode Standard is an evolving character encoding designed to pro-
vide support for a great many of the modern and ancient languages of
the world (Unicode Consortium, 2006). Many code blocks in Unicode
are based on existing national or international standards; the Devan¯agar¯ı
block of Unicode is based on ISCII-1988. Unicode differs from ISCII in
that it provides separate blocks, isomorphic with one another to the great-
est degree possible for each script, for eight other Indic scripts covered by
ISCII. By design, Unicode encodes plain text and leaves non-distinctive
character styles such as boldface or italic to a higher-level protocol. By
employing separate blocks for distinct Indic scripts and by encoding only
plain text, Unicode needs no equivalent for the ISCII ALT character. Ver-
sion 5.0 of Unicode did not support characters needed for the adequate
representation of Vedic texts. It did not include the Vedic character ex-
tensions in ISCII Annex G. The authors of the present volume drafted
a joint proposal in collaboration with Michael Everson, the Irish repre-
sentative to ISO 10646 (Universal Character Set), R. K. Joshi and Alka
Irani of the Centre for Development of Advanced Computing (C-DAC)
in Mumbai, Swaran Lata of the Department of Information Technol-
ogy in the Ministry of Communications & Information Technology of
the Government of India, New Delhi, and other scholars. The Unicode
Technical Committee and International Standards Organization accepted
sixty-eight new characters for Vedic and historical Indic which became
part of Unicode Standard 5.2, and amendment 6 of ISO/IEC 10646:2003
in the Fall of 2009. The new characters are included in two code pages:
2.5. UNICODE: INDIC SCRIPTS
31
Devanagari Extended, and Vedic Extensions. Details of the proposal and
its history are available on the Vedic Unicode page of the Sanskrit Li-
brary website (<http://sanskritlibrary.org/VedicUnicode/>). The Tech-
nical document specifying Vedic character context and usage there links
to the Vedic Unicode Character Phonetic Value Table which correlates
most of the new characters with the Sanskrit Library Phonetic encoding
(SLP1) and demonstrates which are used in which of the various Vedic
traditions.
A fundamental principle of Unicode is the character-glyph model
(Gillam, 2002, 44–7).13 Unicode generally distinguishes between dis-
tinctive units of textual content (called “characters”) and displayed to-
kens (called “glyphs”), although the distinction may at times be con-
tentious, and certain compromises have been made (Jenkins, 1999).14 To
put it differently, a glyph is a typographic symbol considered primar-
ily as a visual object; a character is a linguistically- or logically-based
archetype (Haralambous, 2002).15 Characters frequently stand in a one-
to-many relation to their glyph realizations. Consider the following ex-
amples:
• The sequence of Roman characters f + i may be displayed as two
glyphs (fi) or as a single-glyph ligature (ﬁ).
• The Arabic letter n¯un, a single character, may be realized as one
of four different glyphs, depending on its context:
	à
isolated
	K
word-initial
I.	K nabata ‘to sprout’
	J
word-medial
I	K. bint ‘girl’
	á
word-ﬁnal
	á.K tibn ‘straw’.
• The Devan¯agar¯ı sequence of k ⟨ka⟩+ HALANT + k ⟨ka⟩may be re-
alized as (1) a single glyph with two components stacked vertically
13A thorough discussion is to be found in ISO/IEC TR 15285:1998(E) “Information
technology — An operational model for characters and glyphs”.
14Frequently, inconsistencies are inherited from earlier encoding standards.
15The distinction resembles that sometimes drawn in the theoretical literature on writing
between inscriptions and characters, where the latter are categorical in nature and presup-
pose an equivalence class (Tolchinsky, 2003, 17).
32
CHAPTER 2. EXISTING ENCODING SYSTEMS
(ëÐÅëÐÁ*:), (2) a single glyph with two components stacked horizontally
(#k), or (3) ⟨ka⟩+ vir¯ama + ⟨ka⟩(k, +.k).
A number of criticisms of Unicode, with reference to Indic scripts,
can be found (Hellingman, 1998; White, 2002). We focus here on those
features that may be perceived as anomalous from the point of view of
the Sanskritist:
1. As Yannis Haralambous writes, Unicode is (for historical reasons)
“quite awkward: it is partly logical and partly graphical” (Har-
alambous & Plaice, 2002). Separate versions of vowels (e. g. /¯a/)
exist for the independent (A;a) and dependent (:a) forms. But the
distribution of these vowel forms is entirely complementary.
2. In order to code the isolated consonant /k/, it is necessary to use the
sequence U+0915 (k) U+094D (, ) (DEVANAGARI LETTER KA
+ DEVANAGARI SIGN VIRAMA). Here a character is needed to
encode the zero-vowel, whereas in U+0915 (k) (DEVANAGARI
LETTER KA) no distinct character encodes the vowel /a/.
(a) Shaping engines are supposed to provide a suitable ligature
for k ⟨ka⟩+ vir¯ama + k ⟨ka⟩(= ëÐÅëÐÁ*:); in order to prevent liga-
ture formation, a special character ZWNJ (U+200C: ZERO-
WIDTH NON-JOINER) is needed: U+0915 (k) + U+094D
(, ) + U+200C (ZWNJ) + U+0915 (k) →k, +.k.
Similarly,
to form the horizontally stacked conjunct, the special char-
acter ZWJ (U+200D: ZERO-WIDTH JOINER) is needed:
U+0915 (k) + U+094D (, ) + U+200D (ZWJ) + U+0915 (k)
→#k. These two format characters correspond to nothing
either visual or linguistic.
2.6
CS (Classical Sanskrit) and CSX (Classi-
cal Sanskrit Extended)
In 1990 a group of scholars at the 8th World Sanskrit Conference in Vi-
enna agreed on an 8-bit encoding for transliterated Sanskrit called CS
(Wujastyk, 1990). A superset of this standard, CSX (Classical Sanskrit
Extended), was also devised, which allowed for characters used in the
2.7. TITUS INDOLOGICAL 8-BIT ENCODING
33
transliteration of Vedic and Tamil. The CS and CSX standards are based
on IBM CP 437 (an 8-bit codepage with the lower half corresponding to
ASCII, and an upper half containing accented characters for European
languages and additional symbols). The CS standard replaced 32 code-
points in CP 437 with upper- and lower-case characters used in Sanskrit
transliteration (but not used for modern Western European languages).
CSX replaced an additional 22 codepoints. A fundamental design prin-
ciple of CS and CSX was to depart as little as possible from CP 437. A
superset of CSX, CSX+, also exists, which adds an additional 28 charac-
ters used in Indic transliteration and speciﬁed in ISO 15919; four other
characters for general-purpose typography are also added. One character
(á) has been moved, since its codepoint is reserved in Windows character
sets for a non-breaking space.
Although a number of fonts supporting the CS family of standards
exist (including fonts released under free licenses such as the GPL16),
CS/CSX/CSX+ are not registered with any international standards au-
thority and lack any general OS- or application-level support. Packages
providing support for CS in TEX are available, however (Pandey, 1998).
2.7
TITUS Indological 8-bit Encoding
TITUS (Thesaurus Indogermanischer Text- und Sprachmaterialen), di-
rected by Prof. Dr. Jost Gippert at the Johann Wilhelm von Goethe Uni-
versität, Frankfurt am Main, holds a signiﬁcant collection of digitally-
accessible texts for the investigation of proto-Indo-European (PIE) lin-
guistics. Among this collection is found a large number of Indic texts
(Old Indic, Middle Indic, and Modern Indic). The collection of Old
Indic (Sanskrit) texts is one of the largest in the world. Historically,
TITUS made these texts available in the TITUS Indological 8-bit Encod-
ing, which is based on the legacy IBM CP 437 codepage used by the
PC-DOS variant of MS-DOS. Nowadays, the publically-accesible ver-
sion of the texts is available in Unicode via a Web interface. Still, the
TITUS Indological 8-bit Encoding is primarily used in private work with
the documents, in which the WordCruncher software plays a signiﬁcant
16See the website of John Smith: <http://bombay.indology.info/>.
34
CHAPTER 2. EXISTING ENCODING SYSTEMS
role. CD-ROMs distributed by TITUS still contain the texts in the TITUS
Indological 8-bit Encoding.
The TITUS Indological encoding departs signiﬁcantly from CP 437;
with the exception of the basic alphanumeric characters and basic punc-
tuation, all symbols have been redeﬁned. (Even CP 437 is not a superset
of ASCII, as it redeﬁnes the ASCII control characters (0x00-0x19) as
dingbats, and other symbols.) The TITUS encoding in addition overrides
other characters in the ASCII range: 0x23 = # →h (indicates aspiration
of the preceding segment); 0x24 = $ →¯r
˚
(syllabic long r); 0x25 =
% →,
(Semitic , ayin); 0x26 = & →-
(Semitic hamza); 0x7f =
BEL →˙m (anusv¯ara). The upper half of the TITUS encoding contains
modiﬁed Roman characters used in the transcription of Sanskrit, as well
as other Indic and Dravidian languages, and such related languages as
Avestan. Some characters frequently used in the orthography of Western
European languages are retained as well.17
2.8
Unicode: Indic transliteration
Unicode contains the characters and diacritics needed for encoding trans-
literated Sanskrit. Characters for basic Sanskrit transliteration, as well as
relevant diacritics, are found in the following blocks:
• Basic Latin (U+0020–U+007E)
• Latin-1 Supplement (U+0080–U+00FF)
• Latin Extended-A (U+0100–U+017F)
• Latin Extended Additional (U+1E00–U+1EFF)
• Combining Diacritical Marks (U+0300–U+036D)
• Devanagari (U+0900–U+097F).
Unicode lacks codepoints for characters with under-rings and for charac-
ters with the combination of an accent and another diacritic; these may
17Details of the encoding were kindly supplied by Jost Gippert (personal communica-
tion). A TrueType font for displaying texts in the TITUS Indological encoding is available
from TITUS (<http://titus.uni-frankfurt.de/>).
2.9. 7-BIT META-TRANSLITERATIONS
35
be formed with a two-character sequence, using the combining diacrit-
ics. For example: r
˚
= U+0071 (LATIN SMALL LETTER R) + U+0325
(COMBINING RING BELOW); ´¯a = U+0101 (LATIN SMALL LETTER A
WITH MACRON) + U+0301 (COMBINING ACUTE ACCENT). For San-
skrit, three stacked diacritics will sometimes be needed. Diacritic stack-
ing for rendering takes place at the OS/font level or the application lev-
el.18 Up to three diacritics may need to be stacked above a Roman char-
acter (length + nasalization + accent), in addition to one below (e g. ring
below indicating syllabicity of a liquid).
2.9
7-bit meta-transliterations
7-bit meta-transliterations are designed to be pure ASCII transliterations
that may be mapped unambiguously onto an encoding that assigns a
unique codepoint to each character in an underlying Romanization (La-
gally, 1999).19 Reversibility is guaranteed by ensuring that the meta-
transliteration satisﬁes the Fano condition: no code word is a preﬁx of
any other code word (Fano, 1966, 67). If the meta-transliteration is based
on a conventional Romanization, it should be human-readable to some
degree.
To represent diacritics, meta-characters are chosen; thus ⟨.⟩(ASCII
PERIOD) may represent an underdot. Such a meta-transliteration for Ro-
manized Sanskrit would use .n to encode n. , the retroﬂex nasal spelled in
Devan¯agar¯ı with the character :N,a. If it is desired to encode the period, this
may be indicated uniquely as PERIOD + SPACE. A meta-transliteration
inherits defects in the corresponding Romanization. Thus, if we Ro-
manize the voiceless aspirate dental (in Devan¯agar¯ı, T,a) as th, the meta-
transliteration th satisﬁes the Fano condition for the Romanization, but
not for Devan¯agar¯ı — as will be exempliﬁed in the next section.
18At the 12th World Sanskrit Conference in Helsinki, 13–18 July, 2003, a proposal was
circulated, under the name “The V¯amana Project”, to add to Unicode all characters needed
for implementing ISO 15919 in precomposed format. It is, however, the policy of the Uni-
code consortium to add no new precomposed characters, where characters can be composed
from presently-encoded characters.
19Such input schemes are used, for instance, in Lagally’s excellent ArabTEX package
(Lagally, 2004).
36
CHAPTER 2. EXISTING ENCODING SYSTEMS
The meta-transliterations have the advantages of being round-trip-
pable (e. g. to CSX) and easily manipulable in virtually any software
environment, since they are pure ASCII and can be read by humans with
only a minimum of effort. A tabular overview of a modiﬁed form of the
Velthuis scheme, the Kyoto-Harvard scheme, the “wx” (or Hyderabad-
Tirupati) scheme, as well as SLP1, is given by Huet (2009, 196).
2.10
Velthuis transliteration and ITRANS
The Velthuis transliteration is named for the Dutch scholar Frans Velthuis
(Wujastyk, 1996).20 It does not satisfy the Fano condition for represent-
ing Sanskrit phonemic strings, since (for example) the voiceless aspirate
dental may be coded th, which is potentially ambiguous with respect
to a sequence representing a voiceless dental /t/ followed by a voiced
glottal fricative /H/. Since Sanskrit phonotactics forbids such a sequence,
Velthuis applications can assume that the sequence th uniquely repre-
sents the voiceless aspirate dental. Problems will still arise elsewhere,
as in the case where digraphs for diphthongs are spelled identically with
sequences of distinct vowels. For instance, additional means will be re-
quired to disambiguate between the diphthong au and sequence of simple
vowels a + u.
Velthuis also offers alternative ways of transliterating certain speech
sounds, e. g. O for the diphthong au, T for the voiceless aspirate dental
th, and .T for the voiceless aspirate retroﬂex dental t.h. If only these
alternatives are used, the meta-transliteration satisﬁes the Fano condition.
Charles Wikner’s package “Sanskrit for LATEX2ε” (Wikner, 2002)
employs a modiﬁed version of the Velthuis scheme. The ITRANS (In-
dian languages TRANSliteration) scheme, used by a popular software
package (developed by Avinash Chopde) for transliteration and recod-
ing, also signiﬁcantly resembles the Velthuis scheme (Pandey, 1998).21
An ITRANS package is available for TEX, which allows for typesetting
Devan¯agar¯ı, Tamil, Bengali, Telugu, Gujarati, Kannada, Panjabi, and Ro-
manized Sanskrit using the ITRANS software and transliteration conven-
tions (Syropoulos et al., 2003, 351–355).
20Cf. Bakker, Barkhuis & Velthuis (1990).
21<http://www.aczoom.com/itrans/>
2.11. WX
37
2.11
wx
The authors of the textbook Natural Language Processing: A Paninian
Perspective present a scheme for “[i]nternal representation in the com-
puter” that shares many design principles with our SLP1 (Bharati, Chai-
tanya & Sangal, 1996, 193). In the wx scheme (so dubbed after the
characters used to encode the dental stops t and d), a single charac-
ter represents a single speech sound.
Equivalences are more or less
straight-forward. Lower-case ASCII letters represent short vowels or
close diphthongs, while upper-case letters represent long vowels and
open diphthongs.
The symbol q represents r
˚
, and L, l
˚
(Huet, 2009,
196); while no provision is made at all for ¯r
˚
or ¯l
˚
. The graphic oppo-
sition lowercase–uppercase consistently represents the phonological op-
position unaspirated–aspirated. Some characters have a peculiar repre-
sentation: e. g. the velar nasal ˙n (f) and the palatal nasal ñ (F). The den-
tal oral stops t, th, d, dh are represented as w, W, x, X, whereas the
retroﬂex t., t.h, d. , d. h are represented as t, T, d, D. This convention
is no doubt motivated by the fact that speakers of Modern Indic and Dra-
vidian languages regularly perceive English alveolar stops as retroﬂex.22
The retroﬂex sibilant s. is represented as R. This scheme, despite its con-
siderable virtues, seems not to be widely used, although Indian students
in NLP study it, and it plays a role in the Anusaaraka suite of NLP soft-
ware,23 including the Sanskrit morphological analyzer of Amba Kulkarni
and V. Sheeba. The scheme is, however, fundamentally limited, since it
does not allow for the full set of vocalic liquids described by the Sanskrit
grammarians, the unaspirated and aspirated retroﬂex lateral ﬂaps l. and
l.h, any system of accents, or other sounds peculiar to Vedic traditions.
2.12
Kyoto-Harvard
The Kyoto-Harvard transliteration is not a meta-transliteration as deﬁned
above. It instead chooses one or two symbols for each Sanskrit speech
sound, with the addition of some special-use symbols (Wujastyk, 1996).
22Thus in Hindi, for example, both instances of alveolar [t] in tractor become [ú]: :f"E ;#f:=.
The retroﬂex series of stops in Hindi contrasts (as in Sanskrit) with pure dentals: [t”], [t”h],
[d”], [d”h] (not alveolars). Cf. Harley (1955, xix).
23<http://ltrc.iiit.net/~anusaaraka/>
38
CHAPTER 2. EXISTING ENCODING SYSTEMS
Where the conventional Romanization for a Devan¯agar¯ı character can
be represented in ASCII, Kyoto-Harvard uses that representation. Oth-
erwise: r
˚
→R, l
˚
→L; long vowels are represented by their upper-case
equivalents, except ¯r
˚
→q, ¯l
˚
→E; ˙n →G; ñ →J; retroﬂex consonants are
uppercased (and followed by h if they are aspirated); ´s →z; ˙m →M; h.
→H. Special symbols exist also for anun¯asika (&), jihv¯am¯ul¯ıya and upa-
dhm¯an¯ıya (x and f), the ud¯atta and svarita accents (; and :), external
sandhi (ˆ), and compound junction (.). A variant form of the Kyoto-
Harvard scheme is sometimes used, in which long vowels are indicated
by doubling the symbol for the short vowel.
A signiﬁcant number of Sanskrit texts have been entered in this for-
mat. Unfortunately, it is not ideal, since it allows ambiguity such as that
between the diphthong au and the sequence of simple vowels a + u.
2.13
Varn. am¯al¯a
Joshi, Dharmadhikari & Bedekar (2007) have proposed a scheme for
Sanskrit text encoding which they term varn. am¯al¯a ‘garland of speech
sounds’. Whereas ISCII and Unicode take as their starting point for
the encoding of Indian-language texts the orthographic syllable (aks.ara),
Joshi et al. propose a phonemic approach in which the fundamental unit
is the individual speech sound (varn. a). The proposed varn. am¯al¯a in-
cludes the fourteen vowels of Sanskrit; six additional vowels (short e,
candra e, long candra e, short o, candra o, long candra o); anusv¯ara,
nasalization (candrabindu), and visarga; and thirty-four consonants (in-
cluding the retroﬂex lateral ﬂap l.).
The varn. am¯al¯a scheme has been implemented in the context of the
IndiX project developed by C-DAC Mumbai. IndiX is a set of libraries
and applications based on the GNU/Linux operating system that provide
support for Indic scripts.24
The varn. am¯al¯a scheme is indeed based on phonetic principles, many
of which are in accord with principles that we develop below. The status
of this encoding, however, remains unclear. Joshi et al. (2007) do not
assign codepoints or provide an ordering of the sounds in the repetoire.
Earlier work by Joshi (2006) presents the varn. am¯al¯a as a “Vedic San-
24<http://www.cdacmumbai.in/projects/indix/>.
2.13. VARN. AM ¯AL ¯A
39
skrit Coding Scheme”. Codes are envisioned as being assigned in the
(currently unused) Unicode block beginning U+0800. In Joshi’s draft,
the basic Sanskrit sounds, together with numerals, some special sym-
bols (such as the danda), and a few control characters are allocated to
U+0800–U+087F. In U+0880–U+08FF are signs used in various Ve-
dic manuscript traditions, including diacritics that indicate accents. Here
the consonants and vowels of Sanskrit are treated phonetically (although
not all the sounds Joshi includes have phonemic status in Sanskrit), but
the remainder of the coded items are not phonetic but rather visual (or
script-based)! Marks for accents could be interpreted phonetically, al-
though they are presented merely as uninterpreted symbols; but the sva-
stika (U+08E6) represents nothing phonetic, and numerals (U+0800–
U+0809) are properly non-glottographic (Hyman, 2006). This scheme
is unsuitable for encoding in Unicode, since it is phonetically organized
and duplicates material already encoded. At the same time, it cannot
properly be called a sound-based encoding, since it includes a substan-
tial number of characters that do not represent sounds.
Joshi et al. (2007) present a number of arguments in support of the
varn. am¯al¯a that are specious. They assert, “Through the Varnamala ap-
proach the IPA equivalence for Sanskrit text (as well as other Indian lan-
guage text) can be established as one to one correspondence”. Yet many
sounds will have to be represented with digraphs in IPA. They assert,
“Through the Varnamala-Phonemic approach lexical order and sorting
operations in the areas of dictionary etc. can be done in the logical and
more efﬁcient way”. But collation is fundamentally independent of en-
coding (Wissink, 2001). Collating order varies for different languages
written in the same script.
And sometimes multiple collating orders
are used even within a single language. Thus in the case of Sanskrit,
anusv¯ara and visarga collate between the vowels and the consonants in
dictionaries such as Monier Williams’, while in Bloomﬁeld’s Vedic Con-
cordance, anusv¯ara collates after visarga, jihv¯am¯ul¯ıya, and upadhm¯an¯ı-
ya. In addition the authors assert, “Under the phonemic scheme the key-
board in put [sic] procedure will be simpliﬁed by reducing keys for vowel
matras”. Yet input methods are independent of underlying encodings; an
input method in which independent vowels and vowel m¯atras are entered
in the same way could equally be used with the existing Unicode Deva-
n¯agar¯ı encoding. As we shall see, there are more reliable justiﬁcations
40
CHAPTER 2. EXISTING ENCODING SYSTEMS
for a sound-based encoding than these.
Chapter 3
Critique of encoding
systems seen so far
Most of the encoding systems surveyed above are based primarily either
upon Devan¯agar¯ı script or upon the standard Romanization of Sanskrit.
The difﬁculties with these systems are due in part to problems in the
modes of graphic representation of Sanskrit sounds adopted in Devan¯a-
gar¯ı and the standard Romanization themselves. Current encoding per-
sists in being script-based; it allows display conventions to govern uses of
encoding that transcend appearance. While free-hand drawing and type-
face, upon which contemporary encoding systems are based, historically
served only display purposes, contemporary character encoding serves
linguistic and archiving purposes that transcend mere display. Hence,
while it is understandable that initially character encoding was motivated
by display issues in imitation of typeface or manuscript hand, recent ex-
igencies require an explicit system for encoding complete linguistic in-
formation. It is therefore timely to consider the principles governing the
design of character-encoding systems.
The difﬁculties with the Devan¯agar¯ı standards and the Roman stan-
dards surveyed above become evident by observing the discrepancies be-
tween the encoding of Sanskrit embodied in the Devan¯agar¯ı script and in
standard Romanization. Consider especially the following three points:
41
42
CHAPTER 3. CRITIQUE OF ENCODING SYSTEMS
1. In the Devan¯agar¯ı standards, there are separate characters for vow-
els when they appear post-consonantally versus when they appear
phrase-initially or post-vocalically. In the Roman standards, a sin-
gle character is used in all contexts.
2. In the Devan¯agar¯ı standards, post-consonantal /a/ is implicitly indi-
cated by the graph of the preceding consonant, while its absence is
explicitly represented by a sign indicating the cessation of speech
(vir¯ama). In the Roman standards, the distribution of ⟨a⟩corre-
sponds exactly to the distribution of the vowel /a/.
3. In the Roman standards, certain single sounds are represented by
digraphs: the aspirate stops (kh, gh, ch, jh, t.h, d. h, th, dh, ph, bh)
and the open diphthongs (ai, au). In the Devan¯agar¯ı standards,
single characters represent each of these segments.
The common feature of these discrepancies is a departure from the prin-
ciple of representing a single Sanskrit sound by a single character. Both
the Devan¯agar¯ı and the Roman standards concur in departing from this
principle in one additional case:
4. In both the Devan¯agar¯ı and Roman standards the aspirate retroﬂex
lateral ﬂap / h/ is represented by a digraph: \h, l.h.
5. An additional discrepancy exists between the encoding of accent
in Devan¯agar¯ı script and the encoding in standard Romanization.
The Romanization encodes lexical or post-prosodic high pitch and
independent circumﬂex, or deep accent. Devan¯agar¯ı encodes man-
ifest pitch or surface accent. The failure of scholars to recognize
the difference has led to confused explanations of Devan¯agar¯ı ac-
centual systems and the obfuscation of genuinely different recita-
tional traditions and dialects.
3.1
Ambiguity and redundancy
The deﬁciencies that current encoding systems inherit from the Devan¯a-
gar¯ı and Roman orthographies raise questions regarding general princi-
ples. In particular, we will consider the principles of avoiding ambiguity
and redundancy. To avoid ambiguity and redundancy requires that an
3.1. AMBIGUITY AND REDUNDANCY
43
encoding system be characterized by a one-to-one correspondence be-
tween characters and items to be encoded,1 and that all encoded items be
of the same kind (e. g., phonemes or written characters). In items (1), (3),
and (4), above, a single sound is represented by more than one character,
and in (2), a sound is inversely represented: that is, the presence of the
sound is represented by the absence of a character, and the absence of the
sound by the presence of a character. The departure from the principle of
a one-to-one correspondence between what is to be represented and the
representation signals confusion concerning the principles of encoding.
Although the adoption of digraphs to transcribe aspirate stops and
the aspirate retroﬂex lateral ﬂap / h/ in the Roman transcription of San-
skrit departs from a one-to-one correspondence between what is to be
represented and the representation, the character ⟨h⟩was chosen because
it represents aspiration, which is the common feature of all the aspirate
stops and also of the voiced fricative /H/. Similarly, although ai and au
are digraphs representing single diphthongs, the individual components
of the digraphs were chosen as representations of the subsegments of
those diphthongs. Insofar as the individual characters in these digraphs
represent individual features and subsegments in the sounds they repre-
sent, the Roman transcription of Sanskrit does observe a one-to-one cor-
respondence. Yet it still garners the fault of inconsistency in the princi-
ples of representation: some characters represent sound segments, while
others represent features; and others, subsegments.
It is not absolutely necessary that an encoding scheme adhere to the
principle of one-to-one correspondence and a consistent basis for its en-
coding. Yet, if it does not, it runs the risk of ambiguity, which is a fault
in itself. Freedom from ambiguity is the minimal requirement for the
adequacy of an encoding scheme.
The standard Roman encoding is encumbered with the fault of ambi-
guity in either case, whether it adheres to a consistent basis of encoding
sound segments while it departs from the principle of one-to-one repre-
sentation, or else conforms to the principle of one-to-one representation
while it adopts an inconsistent basis of encoding. If it consistently rep-
resents sound segments, it uses the characters ⟨h⟩, ⟨a⟩, ⟨i⟩, and ⟨u⟩in
ambiguous ways. Each serves the dual functions of (1) representing a
1Compare Whitney (1861, 301): “each single sign was originally meant to have a single
sound, and each single sound a separate and invariable sign”.
44
CHAPTER 3. CRITIQUE OF ENCODING SYSTEMS
segment by itself as well as (2) constituting a member of one or more
digraphs that represent another segment. Sometimes the character ⟨h⟩
represents the voiced fricative /H/; but when preceded by ⟨k⟩, ⟨g⟩, etc.
it represents an aspirate stop /kh/, /gh/ etc.; and in conjunction with ⟨l.⟩
it represents the aspirate retroﬂex lateral ﬂap / h/. Moreover, the char-
acters ⟨k⟩, ⟨g⟩, etc. also serve dual functions: each by itself represents
an unaspirated stop (/k/, /g/); in addition, these characters serve as the
ﬁrst member of digraphs ⟨kh⟩, ⟨gh⟩that represent aspirated stops (/kh/,
/gh/). Similarly, sometimes the character ⟨a⟩represents the short vowel
/a/; sometimes, in conjunction with the characters ⟨i⟩or ⟨u⟩, it represents
the ﬁrst portion of an open diphthong /ai/ or /au/. Conversely, some-
times the characters ⟨i⟩and ⟨u⟩represent short vowels; sometimes they
represent the second portion of open diphthongs.
Although it is possible to disambiguate ⟨k⟩, ⟨g⟩, etc. and ⟨h⟩by pho-
netic context, it is not always possible to do so for the characters ⟨a⟩, ⟨i⟩,
and ⟨u⟩. Although the former characters are ambiguous individually, it
is possible to disambiguate them contextually, because the voiced frica-
tive /H/ can never occur post-consonantally. Therefore, ambiguity can be
avoided by interpreting the characters ⟨k⟩, ⟨g⟩, etc. always as part of the
digraphic representation of a voiced aspirate stop or retroﬂex lateral ﬂap
/ h/ whenever they occur before ⟨h⟩(and we can similarly disambiguate
⟨h⟩). It is not, however, possible to avoid ambiguity in the case of ⟨a⟩,
⟨i⟩, and ⟨u⟩. The sequence of characters ⟨au⟩represents the sequence
of two simple vowels in prauga but represents a diphthong in praud. ha.
Similarly, the sequence of characters ⟨ai⟩represents two simple vowels
in manaicch¯a but represents a diphthong in taih. .
It would be an improvement to trade ambiguity for redundancy. One
can at least free the Roman system from contextual ambiguity if one
introduces the diaeresis over the second character in a sequence to show
that both characters are simple vowels: thus praüga, manaïcch¯a. But in
so doing one introduces redundancy, itself a fault. In some cases /i/ will
be represented as ⟨i⟩, whereas in others it will have to be represented as
⟨ï⟩. Such inelegant means to avoid ambiguity reveal deeper structural
problems.
The Devan¯agar¯ı standards depart from the principle of one-to-one
correspondence in (1), (2), and (4), and from the principle of a consis-
tent basis for encoding in (2). Yet they do not introduce the degree of
3.2. AMBIGUITY IN THE ENCODING OF ACCENTUATION
45
ambiguity seen in the Roman standards. The Devan¯agar¯ı standards suf-
fer from the same context-free ambiguity regarding the dual use of the
characters L and h as the Roman standards do in their use of ⟨l.⟩and ⟨h⟩.
These characters represent the voiced unaspirated retroﬂex lateral ﬂap / /
and the voiced fricative /H/, respectively, when they are parsed as sepa-
rate tokens; taken together, they indicate the aspirate retroﬂex lateral ﬂap
/ h/. Although these characters are ambiguous in isolation, it is possible
to disambiguate them contextually, since the sequence of retroﬂex lateral
ﬂap / / + /H/ is not possible in Sanskrit.
In (1), the Devan¯agar¯ı standards suffer from redundancy in represent-
ing Sanskrit and in (2) from an inconsistent basis for encoding. While
in general the Devan¯agar¯ı standards encode sound segments, the vir¯ama
does not. Even if it is accepted that the vir¯ama encodes a zero segment
(like the Arabic suk¯un), the segment /a/ remains unencoded when it oc-
curs after a consonant.
If the Roman standards conform to the principle of one-to-one rep-
resentation while they adopt an inconsistent basis of encoding, they are
still marred by the fault of ambiguity. If the character ⟨h⟩represents the
feature of aspiration common to the aspirate stops, the aspirated retroﬂex
lateral ﬂap / h/, and the voiced fricative /H/, then in the last case, the
other features of the fricative (voicing, etc.) remain unencoded. It would
remain ambiguous, when the character ⟨h⟩is used in isolation, whether
these other features were to be assumed or not. Context can resolve this
ambiguity. Yet even if the other features of the voiced aspirate fricative
are assumed by default when the character ⟨h⟩occurs in contexts not pre-
ceded by one of the characters ⟨k⟩, ⟨g⟩, etc., the encoding scheme would
be inconsistent as to the segment to which the feature of aspiration be-
longs: although it usually indicates aspiration of the preceding segment,
in the case of the voiced aspirate fricative it indicates its own aspiration.
3.2
Ambiguity in the encoding of accentuation
Typically, explanations of the most common R
˚
gvedic accentual system
state that a high-pitched syllable is unmarked, the last low-pitched sylla-
ble before a high-pitched syllable is marked with a horizontal line below,
and a circumﬂexed syllable is marked with a vertical line above. All low-
pitched syllables preceding the ﬁrst high-pitched or circumﬂexed syllable
46
CHAPTER 3. CRITIQUE OF ENCODING SYSTEMS
in a sentence are marked with a horizontal line below. Low-pitched sylla-
bles following a circumﬂexed syllable, yet preceding the last low-pitched
syllable before a high-pitched syllable, are unmarked. An independent
circumﬂexed syllable followed by a high-pitched syllable or another in-
dependently circumﬂexed syllable is marked by putting the digit 1 or 3
to the right of the vowel, depending upon whether it is short or long re-
spectively, and placing both a vertical line above and a horizontal line
below the digit. If the vowel is long, it too is marked with a horizontal
line below (Whitney, 1889, 28–31).2
Such a system, if indeed it marked what it has been claimed to mark,
would be unnecessarily complex, because it would depart from a one-to-
one correspondence between accents to be represented and graphs used
to represent them. First, it would suffer from redundancy in the marking
of low pitch. It would mark low-pitched syllables in some contexts with
a horizontal line below and in others with the absence of any mark. Sec-
ond, it would suffer from ambiguity in its use of the absence of marking,
which in some contexts would represent high pitch and in others, low
pitch. Third, it would violate the Fano condition, since the vertical bar
above, which usually marks any circumﬂexed syllable, would, used over
a digit with a horizontal line below, mark an independently circumﬂexed
syllable followed by a high-pitched or circumﬂexed syllable. Finally, the
vertical line above would cause further ambiguity since it would mark
only the dependent circumﬂexed syllable in the V¯ajasaneyisa ˙mhit¯a and
all circumﬂexed syllables in the Taittir¯ıyasa ˙mhit¯a, but it would mark
high-pitched syllables in the the Kashmiri recension of the R
˚
gveda, the
K¯at.hakasa ˙mhit¯a and Maitr¯ayan. ¯ısa ˙mhit¯a of the Yajurveda, and in the
Paippal¯adasa ˙mhit¯a of the Atharvaveda. Indeed, Böhtlingk and Roth, in
their Sanskrit-wörterbuch, and Whitney, in his Sanskrit Grammar, aban-
don the system and instead adapt to Devan¯agar¯ı the system used to mark
accent in Roman script. They indicate only what they consider to be the
“really accented syllables”: high pitch by means of an o above and an
independent circumﬂex by a vertical line above (Whitney, 1889, 31).
2Cf. Macdonell 1910, 77-78; Renou 1952, 68–69 (both cited critically by Cardona 1997,
lvi–lxi).
Chapter 4
The basis for encoding: a
reanalysis
In the preceding chapter we described how encoding standards for San-
skrit that are based on Devan¯agar¯ı or Romanization inherit the deﬁcien-
cies inherent in the underlying scripts. They suffer from ambiguity and
redundancy by departing from a one-to-one correspondence and by in-
consistency in the basis for encoding. In the current chapter we examine
the principles that underlie encoding. First we examine the motivations
behind our principles. Why is it a minimum requirement for an encod-
ing scheme to avoid ambiguity? Why should it avoid redundancy? Why
should it conform to the principle of one-to-one correspondence? Why
should it adopt a consistent basis? To begin to answer these questions,
we must outline the dimensions of a possibility space for encoding.
The possibility space for text encodings is deﬁned by three dimen-
sions:
1. Axis I: Graphic–phonetic: Is the basic unit of the encoding a
written character or a speech sound?
2. Axis II: Synthetic–analytic: Are units encoded as a single Ge-
stalt? Or are they decomposed into distinctively encoded features?
3. Axis III: Contrastive–non-contrastive: Are codepoints selected
only for units that contrast minimally (graphemes or phonemes)?
47
48
CHAPTER 4. THE BASIS FOR ENCODING
Or are non-contrastive units that exit in complementary distribu-
tion also encoded?
4.1
Axis I: Spoken communication is prior to
written
Knowledge may be communicated by three types of expressive media:
(1) speech, (2) static visual art, (3) movement. While drawing and dance
exemplify the latter two, natural language takes the form of speech. Any
knowledge expressed in one of these media may be secondarily repre-
sented in any of the others. Thus the visual and performing arts may
be described in speech (as in art historical texts and in performance re-
views), and speech may be represented in visual form (in scripts), or
reenacted in movement (as in the game of charades). Written language
is ordinarily a secondary representation of spoken language, although
there is often also use of ideographs (such as the Indo-Arabic numerals)
(Edgerton, 1941) and icons (arrows and so forth).
The possibility of information degradation arises at each stage of
presentation. Some knowledge may be lost because the medium is not
purely transparent. For example, at the ﬁrst stage of expression, a skill-
ful dancer and a klutz will enjoy varying degrees of success in com-
munication through the movement of their bodies. At the second stage,
even the best performance review will not adequately capture the expe-
rience of the reviewer who attended the performance. Similarly: at the
ﬁrst stage of expression, spoken language does not succeed in commu-
nicating ideational and affective content perfectly; at the second stage,
a manuscript that transcribes speech loses even more content. In face-
to-face interaction, humans possess diverse channels for communicating,
ranging from spoken language through paralinguistic hand gestures (Mc-
Neill 1992; Goldin-Meadow 2003), physical deixis (Kita, 2003), head
and body movements, and facial expression (Bruce & Young, 1998, 187–
216). In an audio recording of speech, the informational content of these
non-vocal channels is simply lost (Laver, 1994, 16). Yet the audio record-
ing still succeeds in capturing something of the speaker’s affective state
through such variables as rate of speech, amplitude, tone, and global
pitch and emphasis (cf. Wennerstrom 2001, 206–208). A phonemic or
4.1. I: SPOKEN COMMUNICATION IS PRIOR TO WRITTEN
49
phonetic transcription loses all or much of this information.
Trigger
(1998, 43) observes that no orthography “records all the linguistic struc-
ture of speech. Few have developed means for systematically noting the
tone, stress, pitch, speed, or loudness of speciﬁc utterances”. Moreover, a
transcription necessarily reduces the speech continuum to a succession of
discrete units (cf. Aronoff 1992). The transition from manuscript to print
may impose further information loss: for instance, Indian manuscripts of
Vedic recitation often include strokes in colored ink that indicate pitch
accents and word boundaries. Similarly, at one point in Arabic orthogra-
phy, black ink was used for letters and the diacritic dots used to differ-
entiate otherwise identical letters, red for the diacritics indicating short
vowels (naqt.), yellow for a dot used to mark the hamza (glottal stop),
and green for the elided hamza (Mahmoud, 1979, 9).1 Printed editions,
restricted in their typographic range and limited for ﬁnancial reasons to
a single ink color, usually sacriﬁce some or all of this information.2
The primacy of phonology over graphic representation of a language
is relevant to phonographic writing systems — i. e. those that represent
spoken language by means of symbols for sounds (Sampson, 1985, 32–
4). Most of the examples we discuss in this book, and in general the
representation of the Sanskrit language in Devan¯agar¯ı and Romaniza-
tion, are clear cases of phonography. Phonographic writing systems are
distinguished from so-called logographic or ideographic systems. The
latter encode concepts in written form directly, unmediated by phonol-
ogy. Goodglass (1993, 168) aptly writes that
human speakers are equipped to acquire a variety of techniques for
encoding the sound units of speech and the meaning of concepts
in the form of written characters, and correspondingly equipped to
decode these characters into strings of sounds and meaningful con-
cepts. Within the scope of this cognitive-linguistic endowment,
various cultures have developed markedly different writing sys-
tems that call on different cognitive processes.
Human cognitive processes do interact directly with graphic representa-
tion in reading and drawing. Children’s drawings have been analyzed
1For illustrations, see the color plates reproducing pages from Maghreb Korans in Er-
duman (2004, 104–109).
2Cf. Waller (1988, 45–46, 239) on the loss of color in the transition from manuscript to
print in Europe.
50
CHAPTER 4. THE BASIS FOR ENCODING
into a small number of graphemes organized around a system of distinc-
tive features (Olivier 1974; Krampen 1986), and psychological research
conﬁrms that in reading the grapheme has a salient status independent of
phonetics. This status can be conﬁrmed by disorders such as pure global
alexia, in which patients cannot read written text, although they may be
capable of writing with considerable ﬂuency; at the same time, the patient
may have no difﬁculty copying or naming non-grapheme shapes (Cohen
& Dehaene 2004, 471–473; Caramazza 2000, 204).3 Moreover, research
suggests that the consonant/vowel distinction in orthography “reﬂects a
psychological reality” that is not entirely parasitic on the same distinc-
tion at the phonological level (Cubelli, 1991, 260). Another conﬁrm-
ing phenomenon is grapheme-color synesthesia, in which an involuntary
color percept accompanies the visual presentation of a grapheme; this is
the most commonly presented form of synesthesia (Esterman, Verstynen,
Ivry & Robertson 2006; Simner, Ward, Lanz, Hansari, Noonan, Glover &
Oakley 2005; Ward, Simner & Auyeung 2005; Smilek, Dixon & Merikle
2005; Rich & Mattingley 2005; Wollen & Ruggiero 1983). That the con-
comitant color is genuinely perceived is demonstrated by a number of
experiments (Ramachandran, Hubbard & Butcher, 2004, 869–870).4
To the extent that current encoding systems are based primarily on the
underlying script, their capacity to represent knowledge can be no bet-
3A complementary variety of agraphia occurs, in which a subject is incapable of fol-
lowing the phonetic–graphic route in writing (and thus is entirely incapable of writing
nonsense words) but has well-preserved ability to write known words via the whole-word
route (Shallice, 1981).
4There are two kinds of grapheme-color synesthetes: for projectors, the color percept
is bound to the visually-presented grapheme, whereas for associators the color percept
is “seen” before the “mind’s eye” (Smilek et al., 2005). The most compelling current
explanation of grapheme-color synesthesia is based on proximity of the V4 or V8 areas
implicated in color vision to the so-called “visual number grapheme” area. These areas are
all located within the fusiform gyrus. Additional connections between these areas could
explain the synesthetic percepts (Ramachandran & Hubbard 2001; Ramachandran et al.
2004). Subsequent research has identiﬁed the “visual number grapheme” area as belong-
ing to the visual word form area (VWFA), with the approximate location (−43, −54, −12)
in Talairach space (Cohen & Dehaene, 2004). Although it is unlikely that the VWFA is
entirely devoted to reading, it is hypothesized that the VWFA contains detectors tuned to
recognize graphemes, as opposed to pseudo-graphemes. It is further hypothesized that
“neurons in the fusiform region are tuned to progressively larger and more invariant units
of words, from visual features in extrastriate cortex to broader units such as graphemes,
syllables, morphemes, or even entire words as one moves anteriorily [sic: anteriorly] in the
fusiform gyrus” (Cohen & Dehaene, 2004, 471).
4.1. I: SPOKEN COMMUNICATION IS PRIOR TO WRITTEN
51
ter than the orthography associated with that script. The complexity of
the mapping between the orthographic and the phonetic levels is known
as orthographic depth and can be precisely quantiﬁed (Frost 1992; van
den Bosch, Content, Daelemans & de Gelder 1994; Treiman 2006, 595).
To take two contrasting cases, Finnish orthography is very shallow (or
transparent), while English is quite deep (Lyytinen, Aro, Holopainen,
Leiwo, Lyttinen & Tolvanen, 2006, 40). Since orthographies are never
entirely shallow or transparent (Weir, 1967), character encoding by its
very nature represents knowledge that has already passed through sev-
eral stages at which information loss is possible. The goal of encoding
should be to minimize the loss of information. Since degradation can
occur at each stage of expression and transition, one ought to capture the
informational content at the earliest stage possible. Given that script is
inherently a secondary phenomenon vis-à-vis spoken language, encoding
should be based directly on spoken language.
As noted above (§1.3), Devan¯agar¯ı script itself was not speciﬁcally
designed to represent Sanskrit phonology but rather was adapted to this
use subsequently. Devan¯agar¯ı derives from Br¯ahm¯ı script, which was in
turn inﬂuenced by Kharos.t.h¯ı, which was itself adapted from Aramaic.
Br¯ahm¯ı was placed in service in India originally to represent the phonol-
ogy of Pr¯akrit, rather than Sanskrit; the former lacks a number of the
latter’s phonemes, including vocalic r
˚
, ¯r
˚
, and l,
˚
and the open diphthongs
ai and au (Oberlies, 2003, 168). Moreover, some phonological features
of Sanskrit for which Devan¯agar¯ı incorporates an encoding mechanism,
such as the glottal stop, are not explicitly recognized in the phonologies
of Indian linguists. Since Devan¯agar¯ı was never systematically designed
to represent the phonological systems of Indian linguists in the ﬁrst place,
it would be surprising indeed if it should serve as a more appropriate ba-
sis for encoding Sanskrit than Sanskrit phonology. In fact, very few of the
world’s writing systems were designed for the languages that they repre-
sent in extant texts and manuscripts. Borrowing is the norm in the history
of writing, and adaptations almost always fail to capture the structure of
the spoken language adequately.
Therefore, where one has access to the phonology of the language,
where the orthography is fairly shallow, and where the orthography de-
parts from an ideal coding of spoken language structure, the basis for text
encoding should be phonetic rather than graphic. Sanskrit meets these
52
CHAPTER 4. THE BASIS FOR ENCODING
conditions, and so it is better to encode Sanskrit speech sounds directly
than to encode the secondary representations of those sounds in Devan¯a-
gar¯ı script, Roman script, or any other script. Directly coding Sanskrit
speech sounds will solve the problems of ambiguity and redundancy that
we have noted in our survey of current encoding systems.
4.2
Axis II: General remarks on the units of
spoken and written language
4.2.1
Segments
The continuum of knowledge is made discrete in expression (Pulgram,
1976). Since speech occurs over the temporal dimension, the expression
of knowledge in language occurs in units serially over time. The size of
these units is limited by natural human and environmental factors that
result in cessation or signiﬁcant alteration in the continuum of speech.
In the European Middle Ages, law professors taught the Corpus Juris
divided into sections called puncta, which could be read aloud within
the time periods set by the academic calendar. The length of a day is
a factor in the length of chapters of certain texts. Chapters of Patañ-
jali’s grammatical treatise, Mah¯abh¯as.ya (2nd c. B. C. E.), for example,
are called ¯ahnika, literally ‘to be studied in a day’.5 The attention span
of speaker and listener and the conventions of dialogue establish limits
on the lengths of utterances. Breath limits the length of a foot (p¯ada)
or line of verse.6 Working memory is a factor that may limit sentence
length (Baddeley & Wilson 1988; Shapiro, McNamara, Zurif, Lanzoni,
& Cermak 1992; Goodglass 1993, 122). Finally, mechanisms involved
in articulation and auditory perception constrain the duration of speech
sounds. The minimal independent unit in the chain of speech is the pho-
netic segment or phone.
Scripts that represent spoken language have a linear dimension that
corresponds to the temporal dimension of spoken language. The length
and form of literary productions are constrained by limitations of tech-
nology and human vision. In the ancient Mediterranean world, the length
5For further examples of this type, see Waller (1988, 228).
6Cf. Hixon (1987, 28–43); Watson & Hixon (1987).
4.2. II: THE UNITS OF SPOKEN AND WRITTEN LANGUAGE
53
of a papyrus roll ﬁxed a limit on the extent of a book (or single section
of a complete work).7 In India, binding techniques and materials con-
strained the number of pages in a manuscript, and the size of palm leaves
constrained the size of a page. Writing implements, the resolution of
human vision, and manual motor limitations governed the size of char-
acters. The minimal independent unit in script is the graphic segment or
graph.
4.2.2
Features
Speech is not one-dimensional. Phonetic units may be decomposed into
a number of acoustic or articulatory features that are realized simultane-
ously. Early work on phonetic features conceived features as constituents
of phonetic segments; or, from a different perspective, segments were
bundles of features (Jakobson, Fant & Halle, 1963, 3).8 Yet more re-
cently, linguists have come to see that features overlap segments; for
instance, the feature of voice [+ voice] is realized across all six segments
of the Sanskrit word form babh¯uva ‘he was’.9 Ancient Indian phonetic
treatises recognized that pitch either spread from a vowel to neighboring
consonants in its syllable (TPr. 1.43), or properly belonged to the sylla-
ble itself (cf. R
˚
Pr. 3.9; VPr. 3.130 (Rastogi); APr. 3.67) (Whitney, 1868,
314). In Sanskrit, the prosody of retroﬂexion extends rightward from r
˚
, ¯r
˚
,
r, or s., causing non-ﬁnal n to be realized as n. despite intervening vowels,
semivowels, gutturals, labials, or anusv¯ara (A. 8.4.1–2; cf. Allen 1951,
940; Zwicky 1965, 61–63; Hock 1979, 52–53; Anderson 1985, 191–
192; Dixon & Aikhenvald 2002, 17; Hamann 2003, 122). Thus a feature
may be associated with a string of one or more segments; and a segment
is associated with a set of features. It was J. R. Firth’s insight that “some
phonological properties are not uniquely ‘placed’ with respect to partic-
ular segments within a larger unit” (Anderson, 1985, 185); Firth refers to
such properties as prosodies.10
7For details, see Kenyon (1951).
8We bypass here the question of whether the mental lexicon contains featural speciﬁ-
cations (Feature-Segment Hypothesis) or just segments (Indivisible-Segment Hypothesis)
(Stemberger, 1982).
9Cf. Zellig Harris’ notion of long components (Anderson, 1985, 191).
10It is the norm that features overlap segments. Contemporary research on articulatory
phonetics emphasizes the importance of coarticulation, which “can be detected in almost
54
CHAPTER 4. THE BASIS FOR ENCODING
Speech may be analyzed into acoustic parameters (frequency, phase,
and amplitude of waveforms)11 as well as articulatory parameters (ma-
nipulation of the vocal tract, including larynx, tongue, lips, etc.). Feature
analysis seeks to characterize perceptible features by associating them
with regular patterns of concurrent acoustic and articulatory parameters
(Laver, 1994, 101–110).
Nor is writing one-dimensional. Just as speech is analyzable into
phonetic features, so writing may be analyzed into graphic features. Ana-
logous to articulatory and acoustic features in phonetics are stroke analy-
sis and block adjacency graph (BAG) analysis in optical character recog-
nition (OCR) (Sonka, Hlavac & Boyle, 1999; Kompalli, 2007). Just as
articulatory features are correlated with the production of speech sounds,
stroke sequence is correlated with the production of written characters,
and just as acoustic features are correlated with auditory parameters of
speech sounds, BAG analysis is correlated with the shape of the complete
character.12 Marked alterations in phonetic and graphic features occur at
the boundaries between phonetic and graphic segments.
The analysis of graphic features is more obviously applicable to some
writing systems than to others; it is of particular interest where graphic
features are correlated with phonetic features. Perhaps the most obvi-
ous application is to Korean han’g˘ul, “in which graphic shapes are de-
every phoneme sequence in normal speech” (Goodglass, 1993, 62). Cf. Oudeyer 2006, 24.
Some researchers have moved in the direction of developing a nonsegmental phonology
(Griffen, 1976).
11Sine waves (or sinusoids) may be uniquely characterized in terms of these parameters.
Mathematically speaking, they correspond to equations of the form y = a sin b(x+c), where
a determines the amplitude, b determines the frequency, and c determines the phase. In a
linear oscillating system the output (a periodic time waveform) corresponds to the sum
of a set of sinusoids. Fourier analysis allows us to ﬁnd the complex coefﬁcients Cn that
represent the phases and amplitudes of the harmonic sinusoid components of the periodic
time waveform v(t) using the following equation:
Cn = 1
T
Z T/2
−T/2
v(t)ej2πnt/T dt,
where T is the period of the waveform (Pierce, 1999). In speech, vowels are approximately
harmonic, whereas consonants correspond generally to noise.
12Analysis of characters as mathematical graphs is not merely a recent development.
Already Bondy (1972) presents a graph theoretical analysis of the Greek alphabet, together
with some interesting remarks on palaeographic developments, some hints of prospective
algorithms, and a good measure of humor.
4.2. II: THE UNITS OF SPOKEN AND WRITTEN LANGUAGE
55
signed in such a way that subsegmental phonetic features are systemati-
cally correlated” (Kim, 1997, 145).13 Several modern artiﬁcial alphabets
also include extensive featural components. Pitman’s Shorthand (Pit-
man, 1837) uses segment thickness to represent the voiced/non-voiced
contrast for non-nasal consonants (Sampson 1985, 41–42; Kelly 1981).
Alexander Melville Bell’s visible speech is a universal phonetic alpha-
bet based entirely on the visual representation of phonetically distinctive
features (Bell, 1870).14 The phonetic variant of Henry Sweet’s “Cur-
rent” system of shorthand (Sweet, 1892) iconically represents place fea-
tures by “projection” and manner features by shape (MacMahon, 1981,
269).15 Graphic/phonetic features also play a signiﬁcant role in the Sha-
vian alphabet posthumously funded by George Bernard Shaw (1856–
1950) (Shaw 1962; MacCarthy 1969).16
While the systems discussed above are remarkable in their correla-
tion of phonetic and graphic features, it seems to us that research on
the application of a purely graphic featural analysis to a multiplicity of
writing systems is likely to produce interesting results (cf. Smith, Lott &
Cronnell 1969; Gibson 1972, 5; Klima 1972, 63). Graphic units may be
analyzed along at least three dimensions, from the perspective of produc-
tion: horizontal and vertical stroke direction, and stroke thickness.17 In
13Cf. Sampson (1985, 120–144). We may recall Sir William Jones’ enjoinment: “a
natural character for all articulate sounds might easily be agreed on, if nations would
agree on anything generally beneﬁcial, by delineating the several organs of speech in the
act of articulation, selecting from each a distinct and elegant outline” (qtd. by Firth 1946,
122).
14Bell’s system is indeed remarkable, and it is to be lamented that such a system was
never developed further. On the other hand, from our perspective as twenty-ﬁrst century
linguists, there are many insufﬁciencies in visible speech: how, for example, to represent
the retroﬂex series of Sanskrit, or the emphatic (pharyngealized) series of Arabic, or the in-
gressive sounds of certain African languages? Bell’s system allows for 120 unique sounds,
which is approximately equal to the maximum phonemic inventory of any known language;
yet it is by no means adapted for transcribing a language such as !X˜u/!Kung, which has,
on one count, 141 phonemes (Maddieson 1984, 421–422; cf. Ladefoged 2005, 9). (48 of
these are “click” consonants. The phonemics of this language are somewhat controversial.
The classic study is Snyman (1970).) On languages with a large phonemic inventory cf.
Szemerényi (1967, 86), who characterizes the 84 phonemes of Ubykh as “a world record”.
15“Yet Sweet differs from Bell by relating place to the passive, not the active, articulator”
(MacMahon, 1981, 269).
16Shavian is now encoded in the SMP of Unicode (U+10450–U+1047F).
17For an early computational approach to online stroke-based analysis of handwriting,
see Mermelstein & Eden (1964).
56
CHAPTER 4. THE BASIS FOR ENCODING
the same way that phonetic features may spread over multiple phonetic
segments, graphic features may spread over multiple graphic segments.
An example is the horizontal headstroke that runs across a sequence of
Devan¯agar¯ı characters.
4.3
Axis III: What is relevant for encoding?
It may be demonstrated empirically that certain design principles lead to
undesired effects. In the realm of communication, design mistakes lead
to information loss. Information is lost when meaning-bearing distinc-
tions fail to be copied, transmitted, or perceived. The design of a system
for the purpose of transmitting or storing information requires ﬁrst a con-
sideration of what information is needed or desired. It is neither possible
nor practical to transmit or store all information. Thus in videorecording
and videoconferencing no provision is made for touch, taste, or smell.
All modes of information storage and transmission presuppose a selec-
tion of relevant information. Decisions concerning text encoding depend
on the set of distinctions present in the texts to be encoded and the uses
to which an encoder anticipates the encoded texts will be put. A designer
must reﬂect with care on the character of both the corpus of texts and the
potential user base.
In coding phonetic and graphic segments and features, it is necessary
that each be coded uniquely. Here we encounter the well-known problem
of how a human recognizes sameness amidst difference and determines
that individual instances which vary in their details belong to the same
class. Phoneticians recognize that speech sounds vary in numerous ways
from one speaker to the next and even from one utterance (of the same
speaker) to the next. Speech sounds are like snowﬂakes: no two are ever
identical. Yet humans (and even machines) learn to class certain sounds
together. Certain speech sounds share distinctive acoustic patterns that
allow them to be considered phonetically equivalent — that is, to be con-
sidered as instances of a particular phone (Laver, 1994, 29). Other infor-
mation in the speech signal may be useful (inter alia) for gauging speaker
affect or emotional state (Williams & Stevens 1981; Alpert 1981; Wen-
nerstrom 2001, 221) or for performing the task of speaker recognition
(Nolan, 1997). Such information is hardly ever transcribed, because it is
not linguistically relevant; that is, it does not help to convey a linguistic
4.3. ENCODING LANGUAGE VS. SCRIPT
57
message. Similarly, the stains, smudges, spills, and creases on the page
of a manuscript, as well as the wiggles, trailers, absolute (as opposed to
relative) stroke dimensions are irrelevant to the scholar who is decipher-
ing the linguistic content of a manuscript (cf. Kropaˇc 1991, 118). Yet to a
palaeographer or codicologist, these same idiosyncratic marks may pro-
vide valuable information about the manuscript’s date, its copyist, and
the conditions under which it has been stored.
Speakers of a particular language normally do not distinguish phones
that occur only in complementary distribution in their language. Thus
Arabic does not distinguish between [b] and [p], which constitute distinct
phonemes in English. English does not distinguish between [p] and [ph],
which are distinct phonemes in Sanskrit. For an English speaker [p] and
[ph] are the same phoneme, just as for the Arabic speaker [b] and [p] are
the same (cf. Jakobson et al. 1963, 9).
The structure of an encoding should closely follow the structure of
the linguistic units themselves. A character-encoding scheme ideally en-
codes only the minimally distinctive graphs of the language. A sound en-
coding scheme ideally encodes only the minimally distinctive phones of
the language. In either case, codepoints are assigned only to contrastive
units. The ancient Indian linguists understood a similar principle regard-
ing the relationship between speech and meaning in the ﬁrst stage of
the expression of knowledge. They desired a one-to-one correspondence
between the speech form and the object to be conveyed. The principle
of the avoidance of redundancy is embodied in Patañjali’s oft-repeated
phrase, “one does not employ a speech form for what has already been
stated” (ukt¯arth¯an¯am aprayogah. ).18 Similarly, in M¯im¯a ˙ms¯as¯utra 1.3.26
any¯aya´s c¯aneka´sabdatvam, Jaimini states that it is improper for a single
meaning to be donoted by multiple speech forms.
4.4
Encoding Sanskrit language vs. Devan¯a-
gar¯ı script
It may at ﬁrst seem natural to encode language in terms of written char-
acters. We argue, however, that in certain cases it makes more sense to
18Kielhorn I 105.3, I 227.3, I 238.11, etc.
58
CHAPTER 4. THE BASIS FOR ENCODING
encode directly the sounds of the spoken language, rather than the char-
acters that symbolize them. In making such decisions, one must consider
whether the cultural heritage is received primarily in written or in oral
form and, if written, how closely the written form represents the phonol-
ogy of the language.
For English, the Roman script, rather than the oral language, is the
predominant vehicle of the received cultural heritage. Scholarship is
primarily written. Although regional pronunciation varies, spelling is
highly standardized and needs to be taught even to native speakers up
through secondary school. The Roman script, designed to model the
Latin sound system, was never systematically remodeled to accord with
English phonology.19 Moreover, the phonology of English has changed
signiﬁcantly since the adoption of the Roman alphabet, widening further
the gap between script and sound. Character encoding evolved ﬁrst to
capture the system of contemporary written English (Birnbaum, 1989),
and ASCII (as well as supersets such as ISO 8859-120 and Unicode) pro-
vides a reasonable basis for archiving and processing English language
text. A phonetic encoding of English would not be desirable for many ap-
plications, since it would necessarily impose arbitrary dialectal features
on written texts. Furthermore, writers and readers of English are used to
an orthography that often privileges morphological representation over
phonological representation (consider for instance the different vowels
in potent ["powtn" t] and impotent ["Imp@tn" t]) (Weir 1967; Klima 1972;
French 1976, 124; Sampson 1985, 204–205; Tolchinsky 2003, 92, 193–
194; Snowling 2005; Lyytinen et al. 2006, 49). English spelling also
possesses a lexical-semantic aspect, as shown by such homophonous but
heterographic and heterosemantic sets as {knew, new, gnu} (Weir 1967,
19The earliest inscriptions in Old English are in the Runic futhorc alphabet, which de-
rives from the Germanic futhark and is ﬁrst attested (in the Caistor-by-Norwich runes) for
the fourth or early ﬁfth century (Page, 1999, 21). The adoption of the Roman alphabet
was a response to the spread of Christianity. Originally, several added letters represented
phonemes speciﬁc to English: ⟨æ, ð, þ, ß⟩(the latter two directly borrowed from futhorc: þ
= þorn ‘thorn’; ß = ßynn ‘joy’) (Page, 1999, 186, 212–213). With the rise of printing in the
15th century, the added characters fell into disuse, since they did not exist in the fonts of
continental printers (McArthur, 1992, 31–32). Once again we see the limitations imposed
by a shift in technology.
20See Gaylord 1995.
4.4. ENCODING LANGUAGE VS. SCRIPT
59
173–177; Miller 1994, xii).21 Of course, in certain domains such as di-
alectology and child language research, phonetic encoding may be nec-
essary.22
The case of Sanskrit is different. Here the standard Devan¯agar¯ı or-
thography is extremely faithful to the phonology. Even interword pros-
ody is represented systematically in writing. The reasons are historical:
after a millennium of oral transmission of texts, Sanskrit scholars had
developed by the ﬁfth century B. C. E. precise sciences of phonetics and
grammar. Their systematization of Sanskrit phonology lay at the founda-
tion of education in India and served as the basis for all written literature.
Given the oral bias of Indian culture and the highly phonetic aspect of the
traditional orthography, we may well consider whether Sanskrit phonol-
ogy is a more appropriate basis for encoding Sanskrit language texts than
a secondary encoding derived from the Devan¯agar¯ı script.
21Similarly, French orthography involves a number of elements that are not phono-
graphic; thus, for instance, homophones are sometimes distinguished heterographically
(sain ‘sane’ vs. saint ‘saint’), and a “silent” -s morphographically indicates [+plural] (Jaf-
fré & Fayol, 2006).
22Unicode provides IPA (U+0250–U+02AF) and other phonetic symbols. Several ear-
lier systems allowed for phonetic transcription using only ASCII symbols. CHILDES
(Child Language Data Exchange System) (<http://childes.psy.cmu.edu/>) uses the
PHONASCII transliteration format (based on IPA) in its CHAT database (Allen 1988;
MacWhinney 1991, 71–82). ARPAbet (Shoup, 1980) is a widely-used pure ASCII sys-
tem for the phonetic transcription of American English.
60
CHAPTER 4. THE BASIS FOR ENCODING
Chapter 5
Sanskrit phonology
Sanskrit phonology has been a topic of investigation since phoneticians
analyzed interword sound alterations in Vedic hymns at the beginning
of the ﬁrst millennium B. C. E.1 During the 6th through 4th centuries
B. C. E., around the time that P¯an.ini composed his grammar of Sanskrit,
phoneticians systematically analyzed the phonetic features of sounds and
categorized sounds according to these features in treatises termed Pr¯ati-
´s¯akhya that were proper to particular Vedic schools (Staal, 1972, xxiv).2
Subsequent treatises called ´Siks. ¯a continued the tradition of phonological
analysis. The phonetic and phonological analyses in these texts differ
from each other and from that assumed for the operation of P¯an.inian
grammatical rules.
Modern historical and comparative linguists ana-
lyze the sound structure of various Sanskrit dialects at various histori-
cal periods; in so doing they rely on the data of Indian predecessors and
adopt or adapt many of their analytic principles. Relevant also are the
independently-motivated featural analyses proposed by modern phonol-
ogists. While it is neither practical nor desirable for us to present all the
1By phonology we mean the study of the sound system of a language, including the
relationship of sounds to one another and the patterned alternation of sounds. Phonetics
denotes a broader science that may also describe paralinguistic, extralinguistic, and non-
systematic aspects of a spoken language.
2Dating is a matter of some controversy. Scharfe (1977, 129–30) dates the V¯ajasaneyi-
pr¯ati´s¯akhya to 250 B. C. E.
61
62
CHAPTER 5. SANSKRIT PHONOLOGY
details of such analyses, we aim to survey here those aspects of phonemic
and featural analyses of Sanskrit that are relevant to its encoding.
We summarize the system of phonological features of Sanskrit in TA-
BLE 1 and show the classiﬁcation of phonetic segments of Sanskrit in ac-
cordance with these features in TABLE 5. The system presented in these
tables is based upon our own analyses of the Indian phonetic treatises
and on recent contributions to Sanskrit phonetics. Signiﬁcant differences
and variations both in the system of features and in the classiﬁcation of
segments will be discussed in due course.
5.1
Description of Sanskrit sounds
Phonetic segments are categorized in TABLE 5 in rows by their place of
articulation within the mouth and in columns by their manner features:
stricture, voicing, aspiration, nasalization, and duration.3 Indian phoneti-
cians categorize the duration of segments by recourse to the measure of
the short vowel. A short vowel measures one mora;4 long vowels, two
morae; prolonged vowels (not shown), three morae; consonants, half a
mora.5 In terms of pitch, Indian phoneticians categorize vowels as high-
pitched, low-pitched, circumﬂexed, or monotone. A circumﬂexed vowel
is described as dropping from high to low, and a series of syllables is
monotone if devoid of relative distinction in pitch.
The vowels represented in Devan¯agar¯ı by O; and A;ea, although typ-
ically categorized as diphthongs, are phonetically monophthongal mid
vowels and hence Romanized e and o. The true diphthongs (written Oe;
and A;Ea) have two places of articulation — one each from the subseg-
ments of which they are composed: ai, composed of subsegments a and
i, is glottal-palatal; whereas au, composed of subsegments a and u, is
glottal-labial. In the table they are placed in the row that corresponds to
their second property. The vowels and semivowels other than r (i. e. y,
l, and v) include nasalized variants (not shown) as well as the clear (un-
3Allen (1953, 20) differs in leaving out ¯l
˚
as well as the more open and most open
manners of articulation, and in not categorizing anusv¯ara and h as semivowels.
4The mora is a unit of relative duration that holds constant over differing rates of speech.
5For comparison, in English spoken in a connected style and at an ordinary rate, the
median absolute duration of a stressed vowel is 130 msec; that of a consonant or unstressed
vowel is about 70 msec (Klatt, 1976).
5.1. DESCRIPTION OF SANSKRIT SOUNDS
63
nasalized) varieties. v,a, conventionally Romanized as v, was originally a
labiovelar approximant [w]; in some dialects it is described by ancient
phoneticians as a labiodental [V] (P¯an. in¯ıya´siks. ¯a 18).
Indian phoneticians describe a number of other phonetic segments
not shown in TABLE 5. Nasals called yama occur as a transition be-
tween an oral stop and a subsequent nasal stop. Four yamas character-
ized by the voicing and aspiration of the preceding stop are Romanized
˜k k˜h ˜g g˜h and are designated variously in Indian phonetic treatises as
k<u K<ua g<ua ;G<ua 6 or kM KMa gMa ;GMa.7 Another nasal segment called n¯asikya (˜h) oc-
curs as a transition between h /H/ and a subsequent nasal stop n. , n, or
m.8 Unreleased stops occur before stops, and reduced semivowels cor-
responding to y, l, and v occur word-ﬁnally; both are termed abhinidh¯a-
na (Varma 1929, 137–147; Allen 1953, 71–73). Firmer approximants y
and v occur word-initially, and lighter approximants y and v occur word-
ﬁnally in several dialects (Varma 1929, 126–132; Allen 1953, 68–69;
A. 8.3.18). Short simple vowels ˘e and ˘o occur in Vedic recitation and
in phonetic treatises.9 The Ke´sav¯ı´siks. ¯a and Pratijñ¯as¯utra notice slightly
lengthened short vowels in the V¯ajasaneyisa ˙mhit¯a. The former states
that short vowels are slightly long (ki ˙mcit d¯ırgham) except when fol-
lowed by a syllable containing a long ¯a preceded by a consonant, or a
vowel preceded by a consonant and followed by a visarga. The latter
states that slight length (¯ıs.add¯ırghat¯a) occurs in a word-initial syllable
containing the vowel a preceded by a consonant (Varma, 1929, 179).10
Vowel segments (a i u r
˚
l
˚
e) called svarabhakti break up certain consonant
clusters (Schmidt, 1875, 1–8). In particular, a svarabhakti appears in
clusters consisting of r plus a fricative, and in broken clusters consist-
6VPr. 8.31 (Rastogi, 1967, 89).
7The Catur¯adhy¯ayik¯abh¯as.ya on CA. 1.1.26 (Deshpande, 1997b, 139).
8See Allen (1953, 75–78), Mishra (1972, 87–88), van Nooten (1973, 412), Cardona
(1977), Cardona (1980, 253 n. 14).
9chandog¯an¯a ˙m s¯atyamugrir¯an. ¯ayan¯ıy¯a ardham ek¯aram ardham ok¯ara ˙m c¯adh¯ıyate, etc.
MBhK., I 22.21–24. See Cardona 1987, 28–30; Cardona 1983.
10The statement of the P¯ari´siks. ¯at.¯ık¯a Y¯ajus.abh¯us.an. a that one should pronounce a short
vowel like a long one in an aggravated svarita seems to lengthen a short vowel to a long one
rather than account for a length between that of a short vowel and a long one. Likewise, it is
not clear that shortened long vowels termed ks.ipra ‘quick’ are any different in length from
short vowels. The only evidence Varma (1929, 178) cites for them describes their length as
that of a short vowel, and he himself notes that their length “may be confused with that of
a short vowel”.
64
CHAPTER 5. SANSKRIT PHONOLOGY
ing of a voiced abhinidh¯ana plus a stop or fricative (Schmidt 1875, 1–
8; Varma 1929, 133–136; Allen 1953, 73–75; R
˚
kpr¯ati´s¯akhya 6.46-53,
14.58). Catur¯adhy¯ayik¯a 1.4.10–11 distinguishes two lengths of svara-
bhakti.
Vedic phonetic treatises also describe (1) longer and shorter
lengths of anusv¯ara, which regularly occur after short and long vowels
respectively (V¯ajasaneyipr¯ati´s¯akhya 4.148–149; R
˚
kpr¯ati´s¯akhya 13.32–
33); (2) realizations of anusv¯ara as velar nasalized stops before r and
fricatives (g˜u and, before unvoiced fricatives, ˙nk) (Cardona, 2003, 110);
and (3) extra high or extra low pitches and special varieties of circum-
ﬂex accent determined by sandhi and phonotactics (R
˚
kpr¯ati´s¯akhya 3.4;
V¯ajasaneyipr¯ati´s¯akhya 4.136, 138; A. 1.2.40). Patañjali asserts that there
are prolonged vowels measuring four morae (MBhK. III 421.13–14).
Certain ´Siks. ¯a texts distinguish in addition to short and long anusv¯ara (1) a
two-mora (dvim¯atra) anusv¯ara before consonant + r
˚
(Y¯ajñavalkya´siks. ¯a
139; P¯ar¯a´sar¯ı´siks. ¯a 31) or (2) a heavy (guru) anusv¯ara before a consonant
cluster (Laghum¯adhyandin¯ıya´siks. ¯a 14–15; Ke´sav¯ı´siks. ¯a 5). Some ´Siks. ¯as
describe nasalized vowels prolonged by up to six morae (ra˙nga) (Malla-
´sarmakr
˚
ta´siks. ¯a 43–46). Vocalic and consonantal subsegments comprise
the vowels r
˚
and l
˚
(Allen, 1953, 61–62). Subsegments of diphthongs
are of similar quality to independent vowels. Unaspirated and aspirated
retroﬂex lateral ﬂaps / / and / h/, written L, l. and \h, l.h, occur intervocali-
cally in R
˚
gvedic (as well as in the Nirukta) in place of d. and d. h (Allen,
1953, 73).11
11After consultation with the colleagues mentioned in parentheses below, it remains un-
clear whether the Vedic L, l. and \h, l.h were ﬂaps, taps, or approximants. In Modern Indic
(Gujarati, Marathi, Oriya, and the four Dravidian languages), L, l. is a retroﬂex lateral ap-
proximant, not a ﬂap (Aklujkar, Cardona, Deshpande, Bhaskararao), and it is reasonable to
assume that retroﬂex lateral approximants developed from the intervocalic voiced retroﬂex
stops .q, d. and Q, d. h (Cardona). In Tamil the retroﬂex lateral approximant ñ l. is not exclu-
sively intervocalic but occurs in clusters, including geminates (Steever) and contrasts with
a central retroﬂex approximant with lateral contact between the sides of the mid-tongue
and the palate xñ l¯ , as well as with a non-lateral post-alveolar ñ r¯ (which may be in the
process of merging with alveolar `ñ r) (Keane, 2004, 113) (with thanks also to Chevillard).
Likewise, the Vedic retroﬂex laterals are distinguished from the modern Hindi retroﬂex
ﬂaps .qÍ , and QÍ ,. The development of weaker allophones in intervocalic position in Vedic is
paralleled in Middle Indo-Aryan: nn > n. , and ll > l. (Hock).
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
65
5.2
Phonetic and phonological differences
Ancient and modern authorities disagree over the classiﬁcation of par-
ticular phonetic segments as well as over the system of classiﬁcation.
When Indian phonetic treatises differ in their classiﬁcation of phonetic
segments, it is not immediately obvious whether the differences are pho-
netic or phonological. Different treatises may reﬂect actual differences
in pronunciation due to historical or dialectal variation or may impose
different classiﬁcation of the same sounds to achieve elegance or utility
in the system of classiﬁcation itself or in the system’s use in formulating
linguistic rules.
5.2.1
Phonetic differences
Ancient Indian treatises themselves report genuine phonetic differences.
For example, R
˚
kpr¯ati´s¯akhya 1.45 states that s, r, and l are produced at
the base of the teeth, but 1.47 reports that some teachers hold r to be
produced at the alveolar ridge (barsvya) (Shastri, 1937, 7). Differing
from both, the P¯an. in¯ıya´siks. ¯a classiﬁes r as coronal (Varma, 1929, 6–
7). Alveolar, coronal, and velar places of articulation are reported for
vocalic r
˚
(Varma, 1929, 8–9, 53).12 Ancient treatises report differences
concerning the relative duration of subsegments that compose diphthongs
(see commentaries on A. 8.2.106, MBhK. III 421.3–14 and Varma 1929,
180–181) and about types and durations of anusv¯ara (Varma, 1929, 151).
Varma (1929, 53–54) demonstrates that such differences reﬂect dialec-
tal variation by showing that the reﬂexes of Sanskrit words in regional
languages originate in differences found in Indian phonetic treatises. He
(8–9) shows, for instance, that dental and coronal pronunciations of vo-
calic r
˚
correlate to reﬂexes in regional Ashokan inscriptions and mod-
ern languages that developed subsequent dental versus retroﬂex geminate
consonants respectively.
In a few cases, ancient phoneticians disagree with each other even
about the existence of certain sounds. For example, is there a long ¯l
˚
corresponding to ¯r
˚
? Taittir¯ıyapr¯ati´s¯akhya 1.2 omits ¯l
˚
, and ¯Api´sali´siks. ¯a
6.4 and the K¯a´sik¯a on A. 6.1.101 deny its existence, while R
˚
kpr¯ati´s¯akhya
12Whitney (1868, 431) lists the differences of opinion mentioned in the Taittir¯ıyapr¯ati-
´s¯akhya.
66
CHAPTER 5. SANSKRIT PHONOLOGY
Intro. 9, and K¯aty¯ayana and Patañjali on A. 6.1.101 (MBhK. III 77.18–
19) accept its existence. Are there prolonged (i. e. trimoraic) versions of
r
˚
and l
˚
(Mishra, 1972, 62–4)? Taittir¯ıyapr¯ati´s¯akhya 1.2 omits not only
¯l
˚
, but also r
˚
3, l
˚
3 (Whitney 1868, 10; Varma 1929, 25). Do jihv¯am¯ul¯ı-
ya, upadhm¯an¯ıya, and intervocalic l. and l.h occur? Some sources do not
include them (Whitney 1868, 282; Varma 1929, 54).
In several cases, ambiguity concerning the phonetic character of seg-
ments has continued into the modern literature. Allen, citing evidence of
Westermann and Ward, refutes Müller’s and Whitney’s denial that h ⟨h⟩
and the series of voiced aspirate stops could be produced with both voic-
ing and aspiration simultaneously (Allen, 1953, 34–6). In fact, contra
Whitney (1868, 52), standard modern treatments of phonetics do rec-
ognize a voiced glottal fricative or approximant [H] (Pullum & Ladu-
saw, 1986, 67). The situation with the voiced aspirated stops is rather
more complex. Ladefoged (1971, 13) argues that voicing and aspira-
tion are incompatible states of the glottis: “Phonemically it may be very
convenient to symbolize these sounds as /b bh p ph/, and so on; but
when one uses a term such as voiced aspirated, one is using neither
the term voiced nor the term aspirated in the same way as in the de-
scriptions of the other stops”. What we call “voiced aspirated stops”,
Ladefoged calls “murmured stops” and Ohala (1983, 2) calls “breathy-
voiced stops”. Chomsky & Halle (1968) allow the term “voiced aspirated
stops”, for which they require the feature heightened subglottal pressure.
Ladefoged (1971, 96) is skeptical of this analysis. Experimental data are
presented by Ohala (1983, 155-160) that the “voiced aspirated stops” of
Hindi speakers are not necessarily accompanied by increased subglot-
tal pressure. Allen also reviews the evidence for and against the ancient
view that semivowels were produced with greater closure than their cor-
responding vowels, defending this view at least for initial semivowels in
later times (Allen 1953, 27–9; Varma 1929, 126–32).
Ancient Indian treatises differ in their description of the pitches that
result from phonotactics. The R
˚
kpr¯ati´s¯akhya, with which the Taittir¯ıya-
pr¯ati´s¯akhya primarily agrees,13 describes a set of three pitches — extra-
high, high, and low — in contrast to the set of three pitches — high, low,
13TPr. 1.41–42, 14.29–31, 21.10–11. Yet it also reports several disparate views includ-
ing those that correspond to the views of P¯an.ini and the V¯ajasaneyipr¯ati´s¯akhya, which are
not always clearly indicated as the views of others.
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
67
and extra-low — described by P¯an.ini and the V¯ajasaneyipr¯ati´s¯akhya.
According to the R
˚
kpr¯ati´s¯akhya, the ﬁrst part of a circumﬂex is higher-
pitched than a high-pitched syllable (R
˚
Pr. 3.4); the latter part is high-
pitched (3.5) unless the following syllable is high-pitched or circum-
ﬂexed, in which case the remainder is low-pitched (3.5–6). It particularly
prohibits making a circumﬂexed syllable too low (3.32). Low-pitched
syllables that follow a high-pitched syllable become circumﬂexed (3.17),
whereas those that follow a circumﬂexed syllable become high-pitched
(3.19); but followed by a high-pitched or circumﬂexed syllable, a low-
pitched syllable remains low-pitched (3.21). According to P¯an.ini, on the
other hand, the ﬁrst part of a circumﬂexed vowel is high-pitched and the
latter part is low-pitched (A. 1.2.32). A low-pitched vowel followed by a
high-pitched or circumﬂexed vowel is replaced by a lower-pitched vowel
(1.2.40). Similarly, according to the V¯ajasaneyipr¯ati´s¯akhya, a low-pitch-
ed vowel and the last part of an independently circumﬂexed vowel fol-
lowed by a high-pitched or circumﬂexed vowel both become lower-pitch-
ed (VPr. 4.136, 138 according to Rastogi). Otherwise, low-pitched vow-
els that follow a circumﬂexed vowel remain low-pitched (4.141–142 ac-
cording to Sharma, Trip¯at.h¯ı; = 4.139–140 Rastogi).14
In sum, in the system of pitches that result from phonotactics de-
scribed in the R
˚
kpr¯ati´s¯akhya, the initial portion of the circumﬂex as-
sumes a higher pitch than the underlying high pitch, while in the sys-
tem of P¯an.ini and the V¯ajasaneyipr¯ati´s¯akhya, it doesn’t. According to
the latter, instead, low pitches followed by high pitches and circumﬂexes
become lower than the low pitch. These descriptions clearly reﬂect pho-
netic differences in the accentuation of the sa ˙mhit¯a texts recited in dif-
ferent Vedic schools and may in addition reﬂect dialectal differences.
Cardona (1993) demonstrates even greater phonetic differences in the
accentuation of the ´Satapathabr¯ahman. a and argues that they represent
dialectal variation.
14According to the text in Sharma’s edition 4.141 reads svarit¯at param anud¯attam anu-
d¯attamayam, but commentators and Rastogi’s edition 4.139 read ud¯attamayam instead of
anud¯attamayam. If Sharma’s edition is simply mistaken, the accentual system prescribed
is more complex than here described, but it is possible that commentators and Rastogi have
revised the text to conform to the R
˚
kpr¯ati´s¯akhya description without recognizing that the
V¯ajasaneyipr¯ati´s¯akhya described a different accentual system.
68
CHAPTER 5. SANSKRIT PHONOLOGY
TABLE 5.1: The systems of accentuation of the R
˚
kpr¯ati´s¯akhya versus
V¯ajasaneyipr¯ati´s¯akhya
tone
R
˚
kpr¯ati´s¯akhya
V¯ajasaneyipr¯ati´s¯akhya
extra high
beginning of svarita
high
ud¯atta, pracaya, end of
svarita
ud¯atta, beginning of sva-
rita
low
anud¯atta, end of svarita
before ud¯atta or svarita
anud¯atta, pracaya, end of
svarita
extra low
anud¯atta and end of sva-
rita before ud¯atta or sva-
rita
5.2.2
Sounds of problematic characterization
The differences in the description of certain sounds by Indian phoneti-
cians is due to genuine challenges in characterizing sounds whose princi-
pal articulators are extra-buccal. Ancient descriptions of anusv¯ara ( ˙m) re-
ﬂect phonetic differences in its production (Allen 1953, 40–6; Bhaskara-
rao & Mathur 1991; Cardona 2003, 110). Yet most of these differing de-
scriptions concur in attributing to it no speciﬁc oral place of articulation.
Some regard its place as the nose alone, others as the nose and throat, and
others still as dependent upon the place of articulation of a neighboring
sound.15 Such descriptions, understood as phonological classiﬁcations
that partially capture the phonetic realizations of the sound, are consistent
with other ancient and modern evidence. Ancient phonetic treatises and
grammars generally distinguish anusv¯ara not only from the nasal stops
(˙n, ñ n. , n, m), but also from nasal semivowels (˜y, ˜l, ˜v) (A. 8.4.59), and
nasalized vowels (ã, ˜ı, etc.) (A. 8.3.4; Cardona 1983a).16 ¯Api´sali´siks. ¯a 4.5
describes it as aspirated; and R
˚
kpr¯ati´s¯akhya 1.10, as a fricative. Modern
15Other differences include that ¯Api´sali´siks. ¯a 4.4 describes it as voiced; R
˚
kpr¯ati´s¯akhya
1.11, as unvoiced.
16Whitney 1868, 66–9, 318–9. Varma (1929, 148–55) wrongly denigrates the distinction
between anusv¯ara and anun¯asika across the board.
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
69
phoneticists describe anusv¯ara as a nasal glide whose designated articu-
lator is the soft palate. The velum is lowered. Debuccalization of a nasal
consonant eliminates its buccal place feature and designated articulator,
and its secondary articulator takes over (Halle 1995, 13, 16; Trigo 1988).
The distinction between anusv¯ara ( ˙m) and the velar nasal stop (˙n) is ac-
counted for by the fact that there is no dorsal movement (of the tongue
body) for the former, while there is for the latter.17 Elimination of the
buccal place feature and designated articulator explains why the Indian
phonetic treatises usually avoid ascribing a particular intrabuccal place
of articulation to the anusv¯ara, even if they do differ in other aspects of
its character. Consistent with these descriptions is a nasal (rhinal) glide
minimally characterized by lowering of the velum and nasality, while it
adopts other features from its environment. Yet there is no evidence for
the realization of anusv¯ara without additional buccal features. In the dia-
lect represented by the R
˚
kpr¯ati´s¯akhya, it is realized as a nasalized frica-
tive by adopting the aspiration and voicing of the following r or fricative.
In the dialect represented by the P¯an. in¯ıya´siks. ¯a for instance, it is realized
as the nasalized vowel offglide of a clear vowel by adopting the articu-
lator, place of articulation, stricture, and voicing of the preceding vowel
(Cardona, n.d., 42).18 In some dialects, it does have a deﬁnite buccal
place of articulation: it is realized as a velar stop accompanied by nasal-
ity (g˜u; ˙nk /
[−voiced]) in White Yajurvedic traditions (Cardona,
17Bhaskararao & Mathur (1991) conclude that anusv¯ara is phonetically identical to a ve-
lar nasal by arguing that if anusv¯ara is phonetically a pure nasal, as some ancient treatises
describe it, its production would require dorsovelar closure. This identity cannot be ac-
cepted, however, because Indian phonetic treatises consistently distinguish anusv¯ara from
the nasal stops, including the velar nasal. A uvular place of articulation would account for
the distinction of the anusv¯ara from the velar nasal stop (Laver, 1994, 209–14). It might also
account for the diverse descriptions of its place of articulation: the uniqueness of the uvula
as a place of articulation would account for its escaping the notice of the ancients, or if it
were recognized, the systematic inelegance of creating a sixth buccal place of articulation
solely for this sound would have discouraged ancient phoneticians from so categorizing it.
Yet a voiced uvular nasal stop is rare in the phonetic inventories of the world’s languages
and is not recognized by any Indian phonetic treatises.
18Busetto (2003, 193 n. 3, 205 n. 18) combines the voicing of the P¯an. in¯ıya´siks. ¯a and
related traditions with the aspiration of the R
˚
kpr¯ati´s¯akhya tradition.
He characterizes
anusv¯ara as originally being a voiced fricative homorganic with the subsequent segment.
While ancient phonetic treatises generally characterize anusv¯ara as voiced, the R
˚
kpr¯ati-
´s¯akhya, which characterizes it as unvoiced, represents the earliest phonetic description in
the Indian tradition.
70
CHAPTER 5. SANSKRIT PHONOLOGY
n.d., 36–7), and other evidence supports its articulation as a palatal or
dental in connection with the epenthesis of homorganic palatal or dental
stops. Reﬂexes in Panjabi and Sindhi show palatal stops (Varma, 1929,
153); the metrical version of the P¯an. in¯ıya´siks. ¯a and its Pañjik¯a commen-
tary report its production at the base of the teeth; and there is inscriptional
evidence for dental as well as velar retroﬂexes (Cardona, n.d., 48–9).
The situation with h and visarga (h. ) is similar to that of anusv¯ara.
The voiced approximant h /H/ contrasts with voiced aspirated stops (gh,
jh, d. h, dh, bh). Ancient treatises generally distinguish the voiceless vis-
arga from voiceless fricatives produced at buccal places of articulation
(h¯ [x], ´s [ç], s. [ù], s [s], h
ˇ
[F]). Moreover, they concur in attributing to
h and h. no speciﬁc oral place of articulation. Debuccalization of stops
and fricatives eliminates their buccal place features and designated ar-
ticulators, and secondary articulators take over. Some ancient treatises
regard the place of articulation of h as that of the following vowel and of
h. as that of the preceding vowel. Others regard their place of articulation
as the glottis or chest.19 These distinctions could reﬂect either phonetic
differences or a difference in phonological classiﬁcation. If phonetic, in
some dialects, the h and h. adopt the buccal place of articulation of the
following and preceding vowels (respectively), just as in the dialect rep-
resented by the P¯an. in¯ıya´siks. ¯a anusv¯ara adopts the place of articulation
of the clear vowel that precedes it. In other dialects, it could be the case
that feature spreading is resisted and an extrabuccal secondary articulator
takes over as the designated articulator. Debuccalized stops and frica-
tives would result in fricatives whose only articulator is the glottis, just
as the debuccalized nasal results in the anusv¯ara whose only designated
articulator is the velum. Yet just as there is no evidence for the realiza-
tion of anusv¯ara without additional buccal features, there is no evidence
for the realization of visarga and h with no additional features. Visarga,
for instance, regularly adopts features of the preceding vowel. Modern
pronunciations echo the preceding vowel after visarga in pausa, and Ya-
jurvedic traditions mark the visarga differently depending upon the pitch
of the preceding vowel, thus demonstrating that the pitch feature spreads
19R
˚
kpr¯ati´s¯akhya 1.39-40; Taittir¯ıyapr¯ati´s¯akhya 2.46-48; Allen 1953, 48–9; Mishra 1972,
90.
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
71
to the syllabiﬁed visarga.20 Differences in the designation of the place of
articulation of h and visarga are therefore probably due to phonological
considerations.
5.2.3
Differences in phonological classiﬁcation of seg-
ments
It is not necessarily the case that different classiﬁcations reﬂect differ-
ences in phonetics. Phonologists make different decisions concerning
how to classify complex phonetic data as they balance ﬁdelity to pho-
netic detail against elegance in the phonological system.21 Hence it is
probably due to the consideration of secondary articulations that some
treatises place the vowels r
˚
and l
˚
at the base of the tongue.22 A similar
consideration accounts for the disagreement over whether the place of
articulation of h and h. is that of a neighboring vowel, the glottis, or the
chest. Those who consider the place of articulation as that of the neigh-
boring vowel regard spread buccal place features as more primary than
extrabuccal place features; those who consider the place of articulation
as the glottis regard glottal stricture as primary; and those who consider
the place of articulation as the chest regard the regulation of pulmonic
airﬂow as primary. Similarly, although nasalization might be regarded as
a resonance feature, a number of treatises make the nose a second place
of articulation for nasal vowels, semivowels, and stops (Allen 1953, 39;
Bare 1976, 75).
In several other cases there is reason to believe that ostensibly pho-
netic descriptions are colored by phonological considerations. Some In-
dian treatises classify e and o as monophthongs with single places of
articulation (as we do) (R
˚
kpr¯ati´s¯akhya 13.40; Shastri 1937, 98); others
classify them as diphthongs with dual places of articulation (Deshpande,
1997a, 76). They are phonetically realized as monophthongs; but histori-
cally and underlyingly, in terms of phonology, they are diphthongs (Allen
1953, 62–4; Cardona 1983, 13–32). Similar is the case of v, which some
20Likewise the pitch feature spreads to syllabiﬁed anusv¯ara in the White Yajurvedic g˜u
pronunciation, as demonstrated by a horizontal line beneath the sign for g˜u after extra-low-
pitched vowels.
21Cardona (1983) considers the interplay of phonetics and phonology in Indian treatises.
22R
˚
kpr¯ati´s¯akhya 1.41; Allen 1953, 55; Mishra 1972, 80; Varma 1929, 7.
72
CHAPTER 5. SANSKRIT PHONOLOGY
classify as labiodental; others as purely labial (as we have) (Deshpande
1997a, 76; Allen 1953, 57). P¯an.inian prosodic rules operate as though
v were a labial semivowel, even though commentators recognize that it
is realized as a labiodental fricative. For like reasons, while P¯an.inians
recognize the phonetic occurrence of diphthongs measuring three or four
morae, they classify them all as prolonged (i. e. trimoraic) in order to
preserve a strict tripartite division of vocalic length.23
While R
˚
Pr. 6.29 describes yamas as non-nasal stops that have devel-
oped a nasal offset before a nasal,24 the TPr. 21.12, APr. 1.99, and CA.
1.4.8 describe them as epenthetic nasals inserted between a non-nasal
stop and a following nasal. Uvat.a, in his comment on R
˚
Pr. 6.29 (Shas-
tri, 1931, 206), VPr. 8.31 (Rastogi, 1967, 89), the Tribh¯as.yaratna, in
its initial enumeration of sounds (Whitney, 1862, 10) and its comment
on TPr. 21.12 (Whitney, 1862, 389), and the Catur¯adhy¯ayik¯abh¯as.ya
on APr. 1.1.14–15 (Deshpande, 1997b, 117–119) and 26 (Deshpande,
1997b, 139) all count four yamas. Yet Whitney (1862, 393–395) and
Deshpande (1997b, 251–254) are of the opinion that the CA. held there
to be twenty yamas. Whitney and Deshpande’s insistence that there were
twenty must be accepted as a phonetic evaluation on the grounds that
the yama inherits properties of the preceding sounds, of which there are
twenty, in addition to the nasality of the following sound. Conversely,
the ancient texts enumerated four yamas on the grounds of phonologi-
cal abstraction based upon the features of voicing and aspiration of the
preceding sound. The R
˚
Pr. and VPr. 1.103 syllabify yamas with the
preceding vowel while the TPr. 21.8 syllabiﬁes them with the following.
Varma (1929, 79–80) attributes different reﬂexes in different dialects to
dialectal differences in the syllabiﬁcation of yamas described by the two
Pr¯ati´s¯akhyas.25
23Nage´sa writes that the term trim¯atra is indicatory (upalaks.an. a) of anything longer
than two morae (¯uk¯ala eveti. tatra trim¯atragrahan. am ekadvim¯atrabhinnopalaks.an. am iti
bh¯avah. .
MBh. Uddyota on Patañjali’s comment is.yate eva caturm¯atrah. plutah. under
A. 8.2.106. MBhK. III 421.14, Rohatak ed. V.427, Guru Prasad Shastri, vol. VIII, p. 149.
24Whitney (1862, 393–394) interprets the passage as doubling and therefore as epenthe-
sis in the manner of the other Pr¯ati´s¯akhyas.
25See the additional note of Shastri (1937, 192) on R
˚
Pr. 6.29.
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
73
5.2.4
Differences in the system of feature classiﬁcation
Apart from differences concerning the classiﬁcation of speciﬁc segments,
ancient authorities differ over the system of feature classiﬁcation.26 Pho-
netic treatises vary in the number of places of articulation enumerated,
generally distinguishing the place of articulation of velar stops and jihv¯a-
m¯ul¯ıya from that of a, h, and h. . They place the jihv¯am¯ul¯ıya at the base of
the tongue (jihv¯am¯ula) and the velar stops either there or at the base of
the jaw (hanum¯ula); a, h, and h. they place in the throat (kan. t.ha) (Allen
1953, 51–2; Deshpande 1997a, 76; Bare 1976, 74; Mishra 1972, 77, 80).
In contrast, P¯an.inian grammarians operate with ﬁve places of articulation
rather than six; they combine the glottal and velar places under the term
guttural (kan. t.hya) (Allen 1953, 52; Mishra 1972, 77,119).27 They avoid
having to posit different places of articulation for distinguishing between
a and h (on the one hand) and the velar stops (on the other) by employ-
ing efﬁcient techniques of reference to the segments instead. P¯an.inian
grammarians consider the nose (nasality) as a means, rather than a place,
of articulation. Thereby they avoid complications that would result from
considering all nasals (their distinct oral places of articulation notwith-
standing) as homorganic.28
5.2.5
Indian treatises on phonological features
Signiﬁcantly, certain Indian phoneticians give particular prominence to
features. A few explicitly state that features are entities distinct from
both articulatory processes and phonetic segments and serve as the ele-
ments of which the latter are composed. Such analyses directly inspired
feature analysis in modern linguistics. Beyond classifying sounds ac-
cording to their common features, the ¯Api´sali´siks. ¯a operates with the fea-
tures associated with those sound classes (Cardona, 1965, 248). After
classifying sounds according to their place of articulation in section 1,
the second section explicitly associates these sound classes, designated
26These differences have been studied by Bare (1976) and summarized by Deshpande
(1997a).
27Bhat.t.ojid¯ıks.ita preserves for etymological reasons the base of the tongue as a separate
place of pronunciation only for the jihv¯am¯ul¯ıya: Siddh¯antakaumud¯ı 10 (Cardona, 1965,
227).
28Deshpande (1997a, 84). K¯a´sik¯a on A. 1.1.8.
74
CHAPTER 5. SANSKRIT PHONOLOGY
by terms that refer to their common place of articulation, with articula-
tors (van Nooten, 1973, 425). Thus 2.4 states that velars are produced
with the base of the tongue; 2.5, that palatals are produced with the mid-
tongue; 2.6, that coronals are produced with the tongue blade; 2.7, that
the coronals are alternatively produced with the back of the tongue blade
(retroﬂex); and 2.8, that the dentals are produced with the tongue-tip.
While the sounds associated with these places of articulation all have
some part of the tongue as their independent articulator, 2.9 states that
the rest of the sounds have their respective places of articulation as their
articulator. The third section describes the degree of contact of the ar-
ticulator at the buccal place of articulation for stops, semivowels, frica-
tives, and vowels. This method of description gives an operative role
to features beyond noting shared characteristics of segments. It also de-
scribes articulation in terms that directly associate features with articula-
tory components and only make indirect reference to speech segments.
(See TABLE 2.)
In the eighth section it becomes clear that the ¯Api´sali´siks. ¯a estab-
lishes articulatory features intermediate between the articulatory pro-
cesses themselves, and sets of sounds with shared properties. The fourth
section already categorized sounds according to their common extrabuc-
cal articulatory processes and resultant characteristics: certain sounds are
open-glottis, breath-reverberant (´sv¯as¯anuprad¯ana), unvoiced; others by
contrast are closed-glottis, sound-reverberant (n¯ad¯anuprad¯ana), voiced.
Certain sounds are unaspirated in contrast to others that are aspirated.
Section 8 establishes that articulatory processes produce features that in
turn produce other features. For example, 8.7 states that closure arises
from the glottis being closed, while openness arises from the glottis be-
ing open. 8.8 concludes that these are closure and openness. Clearly the
author intends to establish the existence of features as entities in their
own right. To interpret the statements otherwise would be to accuse him
of serious redundancy (Cardona, 1980, especially p. 248).
Other Indian phonetic treatises establish different systems of features.
Some features are identiﬁed with articulatory constituents; some are re-
stricted to a domain in which they are contrastive. The R
˚
k- and Taittir¯ı-
yapr¯ati´s¯akhyas concur with the ¯Api´sali´siks. ¯a in restricting the features of
voicing (ghos.a) and non-voicing (aghos.a) to consonants, while the for-
mer allow the features breath (´sv¯asa) and sound (n¯ada) for all sounds.
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
75
According to R
˚
kpr¯ati´s¯akhya 13.3–6, breath and sound are the materials
from which all speech segments are produced: breath is the material of
voiceless segments; both breath and sound are the material of voiced as-
pirates and h; and sound is the material of the rest.
R
˚
kpr¯ati´s¯akhya 13.1–21 forms a treatise on the features of segments.
In 13.14, the author, presumed to be ´Saunaka, distances himself from the
view that segments are fundamental, immutable entities. Yet he also dis-
tances himself from the view — in the case of a number of sounds but
not all of them — that certain segments are the constituents of others.
13.15 reports the view of others that the segments a and anusv¯ara consti-
tute the voicing in non-nasalized voiced stops and nasal stops. 13.6–17
attributes to others a view expressed in the ¯Api´sali´siks. ¯a.
¯Api´sali´siks. ¯a
4.9–10 states that the unvoiced aspirates contain the fricative produced at
the same place of articulation (i. e. kh, ch, t.h, th, ph contain h¯, ´s, s., s, h
ˇ
,
respectively) and that the voiced aspirates contain h.
The commentary on Atharvavedapr¯ati´s¯akhya 1.10 reports that some
consider there to be only ﬁve stops (the ﬁrst in each series).
These
become differentiated by the addition of certain features. United with
the unvoiced fricatives, they become the unvoiced aspirates; united with
voicing, they become the voiced unaspirates; united with their corre-
sponding fricative in addition, they become the voiced aspirates; and
united with voicing and nasalization, they become nasal stops.29 These
statements name both features and segments as the constituents of other
segments. Still, they demonstrate a penetrating phonological analysis in
terms of constituents that are more fundamental than segments.
5.2.6
Modern feature analysis
Modern feature analysis is concerned with discovering the internal orga-
nization of phonological features in human language.30 The fact that
features have internal organization was, of course, already known to
the ancient Indian phoneticians. Indian phoneticians typically organized
their feature systems in such a way that the binary voicing and aspira-
tion features were constrained by buccal stricture. Voicing and aspira-
tion apply only to consonants in Sanskrit; vowels are inherently voiced
29Whitney 1862, 346, 591; cf. Shastri 1937, 221–2, n. on 13.15–20.
30A seminal work in this area is Bell (1870), on which see p. 55.
76
CHAPTER 5. SANSKRIT PHONOLOGY
and aspiration-neutral. Indian phoneticians also typically organized their
feature systems in such a way that the length feature was constrained
by stricture. They reserved lengths greater than half a mora to vowels.
¯Api´sali already understood that the binary nasalization feature was con-
strained to buccal places of articulation. He does not assign the extrabuc-
cal nasalization feature to sounds to which he gives exclusively a nasal
place of articulation. Still, the modern discovery that features have inter-
nal organization has inspired exciting progress in modeling the relations
between features.
Modern linguists make essentially three advances in feature analy-
sis. First, they apply analysis of changes in a language’s feature system
to the understanding of historical language change. Second, they extend
feature analysis to virtually all of the world’s languages and investigate
feature universals. Third, they understand that features can endure and
spread in time independently of each other and of ﬁxed temporal units.
Halle (1988) draws attention to Jakobson’s insightful recognition of the
importance the system of features and its evolution holds for historical
linguistics (Jakobson, [1929] 1971).31
According to Halle, Jakobson
realized that phonemes were not the ultimate constituents of language;
rather, they are composed of distinctive features, and the change of dis-
tinctive features is the principal vehicle of sound change. Hence, sound
change ordinarily affects entire classes of sounds and not just individual
phonemes. Language change involves reorganization of the system of
distinctive features known to the speakers, rather than an arbitrary clas-
siﬁcation of features. And the phonotactic rules that constrain the form
of words are part of the realization of the phonological system.
Zwicky (1965) employed a set of twelve binary features, based on
the system of Jakobson, Fant, and Halle, for Sanskrit.32 An analysis
by Ivanov & Toporov (1968, 35–41) makes use of ten binary features.33
31For the history of Jakobson’s thinking on these matters, see Joseph (2000, 170–183).
32To wit: (1) consonantality, (2) vocalicity, (3) obstruence, (4) continuance, (5) gravity,
(6) compactness, (7) diffuseness, (8) nasality, (9) voicing, (10) tenseness, (11) ﬂatness,
(12) stridency. Zwicky does not make reference to the analysis of Ivanov and Toporov,
originally published in Russian in 1960.
33(1) aspirate–non-aspirate, (2) voiced–voiceless, (3) nasal–oral, (4) cerebral–non-
cerebral, (5) palatal–non-palatal, (6) grave–acute, (7) compact–diffuse, (8) continuant–
discontinuous, (9) consonantal–non-consonantal, (10) vocalic–non-vocalic. Features (2),
(3), (6), (7), (8), (9), and (10) correspond to features used by Zwicky. Ivanov and Toporov
observe that opposition (1) might be interpreted in terms of checked–unchecked or in terms
5.2. PHONETIC AND PHONOLOGICAL DIFFERENCES
77
Early work in generative phonology primarily treated features as vec-
tors without internal organization.34 Chomsky & Halle (1968), in their
inﬂuential sketch of a system of universal phonetic features, presented
a hierarchical system, which they characterized, however, as primarily
expository in purpose (300). At the same time, they noted the desirabil-
ity of research into the organization of features. More recently, excit-
ing progress has been made in modeling the relations between features.
Halle (1983) demonstrated that articulatory mechanisms, acoustic data,
and phonological rules all provide constraints on the organization of fea-
tures. Clements (1985) suggested that features follow a hierarchical or-
ganization governed by limits regarding both their sequential ordering
and their simultaneous grouping. On this view, features are regarded not
as properties of sound segments but as independent units in their own
right. Associated with each point in the speech signal is a feature geom-
etry that is orthogonal to the temporal dimension of the signal. Perhaps
the most signiﬁcant aspect of Clements’ account is a “constrained the-
ory of assimilation processes, according to which all assimilation rules
involve the spreading of a single node: the root node, a class node, or a
feature node” (Clements, 1985, 247). In feature spreading, multiple seg-
ments, which were previously linked to separate features, are relinked
to a single feature.35 Since feature groupings recur across the world’s
languages, the aim of phonologists is to discover an adequate universal
feature organization (Clements & Hume, 1995).
Halle (1995) and Halle, Vaux & Wolfe (2000) arrange features un-
der their articulators instead of grouping them according to constriction,
which was the organizing principle of feature geometry in Clements’
model. Halle also considers that acoustic aspects of features play a sec-
ondary role. He believes “that there is a direct connection only between
features in memory and the articulatory actions to which they give rise”
(2002, 7). He therefore groups features under the only moveable parts
of the vocal tract, namely: lips, tongue blade, tongue body, tongue root,
soft palate, and larynx, and provides each with a unary designated artic-
of tenseness; (4) might be interpreted in terms of ﬂatness; and (5) might be interpreted in
terms of stridency.
34Ivanov & Toporov (1968, 40), however, present a feature tree, with (10) as the root
node and with higher nodes branching on the basis of features with decreasing indices in
their (inversely) ranked list (see n. 33 above).
35See e. g. Halle (1995); Calabrese (1998, 9).
78
CHAPTER 5. SANSKRIT PHONOLOGY
ulator feature (Halle et al. 2000, 388–389; cf. TABLE 12). The fact that
articulators are controlled by paired sets of agonistic and antagonistic
muscles is directly reﬂected in the binary character of their subordinate
features. Further, he requires that features constitute only terminal nodes
and that only these spread; he thereby abandons Clements’ (1985) provi-
sion that higher nodes spread. If this proposal proves correct, then a net-
work model might better represent feature organization than a tree model
does. Halle’s recent research validates the articulatory feature analysis
employed by the ancient Indian phoneticians, especially that of ¯Api´sali,
who gives prominence to articulators (see above §5.2.5).
Since the feature organization of Halle et al. represents the most
advanced feature analysis in the ﬁeld of phonology and since it shares
the articulatory approach to feature analysis of ancient Indian treatises,
it may be a fruitful basis for analyzing the feature systems and sound
catalogs of the Indian treatises. Certain features and articulators Halle
employs are not distinctive in Sanskrit, such as the articulator tongue
root and its subordinate features, and the articulator-free feature suction.
Halle reduces the number of articulators considered separate by ¯Api´sali
(TABLE 2, II); he accounts for the required distinctions instead by in-
troducing disposition features subordinate to the remaining articulators
(back, low, high, anterior, distributed) and the articulator-free feature lat-
eral. His laryngeal features capture well the observations of ¯Api´sali and
´Saunaka concerning the effect of the larynx on pitch (TABLE 2; TABLE
3 IV, VI[E]) and revise the effect ´Saunaka describes of glottal aperture
on voicing (TABLE 3 III, V). Halle converts the feature nasal from a
place-of-articulation (TABLE 2, [II]D; TABLE 3, [I]G) or an extra-buccal
feature (TABLE 2 [III]B5; TABLE 3 [VI]C) to an articulator. He cap-
tures stricture features, used conservatively by ´Saunaka (TABLE 3, II)
and liberally by ¯Api´sali (TABLE 2, III) by the articulator-free features
continuant, consonantal, and sonorant. The direction of Halle’s research
would seem to lead to an articulatory account of the latter two. TABLE 4
summarizes the articulatory features of Sanskrit sounds per Halle et al.
(2000).
Chapter 6
Sound-based encoding
6.1
Criteria for selecting distinctive elements
to encode
In a comprehensive linguistic encoding scheme, whether based on speech
segments or on phonological features, it is not necessary to encode all
the elements that may be observed; one need only encode distinctive el-
ements. For an encoding scheme based on segments, we select a set
of Sanskrit sounds that are minimally distinctive in the sense described
above (§4.3). For a scheme based on features, we select a set of mini-
mally distinctive features to describe the set of distinctive segments. The
set of minimally distinctive features we select is shown in TABLE 1. It
is not possible to eliminate (as did P¯an.ini) the distinction between the
guttural and velar places of articulation, if we wish the feature system
uniquely to distinguish the visarga from the velar fricative jihv¯am¯ul¯ıya.
P¯an.ini did not need this feature distinction, since he was able to refer
to segments directly (not just through the feature system). Further re-
ductions to the feature systems of the Indian phoneticians are not pos-
sible. We preserve the stricture distinctions of ¯Api´sali between open,
more open, and most open in order to distinguish vowels that P¯an.ini dis-
tinguishes by explicitly classifying certain vowels as gun.a and vr
˚
ddhi.
We abandon, however, the purely phonetically motivated stricture fea-
ture close (sa ˙mvr
˚
tta) of a number of phonetic and grammatical treatises
79
80
CHAPTER 6. SOUND-BASED ENCODING
including ¯Api´sali’s; the category is associated only with the vowel a,
which is already uniquely characterized by place and length features.
We select our set of minimally distinctive Sanskrit sounds to encode
from those discussed in section 5.1. In order to clarify our criteria for
determining which sounds are distinctive, we discuss next the concept of
a phoneme, its limiting parameters, its relation to P¯an.ini’s concept of a
sound class, and the relevance of some of the limiting parameters to gen-
erative grammar and to historical and comparative linguistics. At each
stage in this discussion we specify the set of sounds that our developing
concept of a distinctive segment would include. Finally, having arrived
at a satisfactory concept of a distinctive segment, we specify the set of
sounds we wish to encode and justify the inclusion of various segments
with reference to the limiting parameters already discussed.
6.1.1
Phoneme
Kemp (1994) summarizes the major elements and history of the con-
cept of a phoneme. Early deﬁnitions of the phoneme limited features
that could distinguish phonemes to those qualifying timbre, but since
the 1950s the concept has been extended to include duration, stress, and
pitch.
Phonemes are the minimally contrastive segments of sound in a lan-
guage, on the basis of the contrast between which lexical and gram-
matical distinctions can be made. Sounds that are lexically or gram-
matically contrastive in parallel distribution are independent phonemes.
Conversely, where phonetically similar sounds differ only post-lexically,
they are not independent phonemes; rather they are either allophones or
free phonetic variants. Phonetically similar sounds that occur in com-
plementary distribution are allophones; phonetically similar sounds that
are non-contrastive in parallel distribution are free phonetic variants. A
middle category concerns sounds that are barely contrastive (Goldsmith,
1995a, 10–12). Two sounds, both of which are common, may be con-
trastive in just a small set of environments; one of two contrastive sounds
may occur only in limited contexts; or there may be some other asym-
metry between contrastive sounds. The contrast here possesses a low
functional yield.
6.1. DISTINCTIVE ELEMENTS
81
The concept of a phoneme is yoked with two parameters that limit its
utility as the sole basis for encoding. The ﬁrst is that the sounds belong
to the same language in the strictest sense, namely, “the speech of one
individual pronouncing in a deﬁnite and consistent style” (Jones, 1962,
9). Differences in style, rate, or dialect are not included in the same
phonemic system. The second limiting parameter of the concept of a
phoneme is that for sounds to be considered contrastive they are required
to differentiate semantic content in a narrow sense.
A number of the phonetic segments described in section 5.1 are not
phonemes. These include inseparable phonetic segments described as
subsegments. The status of subsegments within the vowels r
˚
and l
˚
and
within e, o, ai, and au cannot be considered independently of those vow-
els. Although Old Indo-Aryan e, o, ai, and au are historically derived
from Proto-Indo-Iranian sequences of separate vowels *aï, *aü, *¯aï, and
*¯aü, they cannot be eliminated as independent phonemes in a synchronic
description of Sanskrit. The rest of the subsegments described in section
5.1 are overlapping phases, that is, they are simultaneously the offset
phase of the ﬁrst of two segments and the onset phase of the second.
As such, they form parts of allophones. These include the nasals yama
and n¯asikya in the phonological description of the R
˚
kpr¯ati´s¯akhya, where
they are the overlapping phases of a stop or h and the following nasal
stop. While Indian phoneticians make a great contribution to the science
of phonetics by providing descriptions of these sounds, the subsegments
are not phonemic. They occur in very limited environments as parts of
sounds that occur in complementary distribution with other allophones
of their respective phonemes.
Several other marginal phonetic segments are not phonemes in the
strict and narrow sense. They occur only in complementary distribution
with other sounds in parallel contexts and hence are allophones. The
short vowels ˘e and ˘o occur word-initially in hiatus after e and o in com-
plementary distribution with a in certain Vedic dialects. They also occur
in S¯amaveda as free phonetic variants in a speciﬁc recitational repetition
called nyu˙nkha. Slightly lengthened short vowels in V¯ajasaneyisa ˙mhit¯a
occur in complementary distribution with short vowels.1 The retroﬂex
L, l. and \h, l.h occur intervocalically in complementary distribution with d.
1Long vowels shortened in speciﬁc contexts and termed ks.ipra likewise would not be
phonemes, even if they did differ in length from short vowels.
82
CHAPTER 6. SOUND-BASED ENCODING
and d. h in R
˚
gvedic dialect. In several dialects, in complementary distri-
bution with normal y and v, ﬁrmer palatal and labial approximants occur
word-initially, and lighter palatal and labial approximants occur word-
ﬁnally. The epenthetic vocalic segments svarabhakti are automatically
inserted in predictable environments and thus are not phonemic. For the
same reason, the nasals yama and n¯asikya, which in the phonological de-
scription of most ancient Indian phonetic treatises are epenthetic nasals
automatically inserted in predictable environments, are not phonemic.
Certain members of two subgroups of phonetic segments, sibilants
and nasals, occur only non-contrastively either in complementary distri-
bution in speciﬁc dialects or as free phonetic variants. In the sibilant
subgroup, jihv¯am¯ul¯ıya and upadhm¯an¯ıya are allophones of s and r word-
ﬁnally before unvoiced velar and labial stops. Visarga generally occurs
in pausa (dahati agnih. ) in complementary distribution with r and voice-
less fricatives h¯, ´s, s., s and h
ˇ
(agnir dahati, agnih¯ karoti, agni´s carati,
agnis tis.t.hati, agnih
ˇ
p¯ujyate), and as a dialectal or free phonetic vari-
ant of jihv¯am¯ul¯ıya (h¯) and upadhm¯an¯ıya (h
ˇ
) before unvoiced velar and
labial stops (agnih. karoti, agnih. p¯ujyate),2 and of sibilants before sibi-
lants (agni´s ´sr
˚
n. oti : agnih. ´sr
˚
n. oti). It also occurs as a phonetic variant
before palatal and labial stops in certain dialects (yajuh. karoti : yajus.
karoti). A parallel situation is found with certain sounds in the nasal
subgroup. Nasalized semivowels are allophones of word-ﬁnal3 m be-
fore their corresponding clear semivowels (cakame pur¯uravasam : sa˜y-
yama). Anusv¯ara generally occurs in complementary distribution with
m before a fricative (sa ˙m-´saya) and as a dialectal or free phonetic vari-
ant of nasal stops before oral stops (´sa˙n-kara : ´sa ˙m-kara), and of nasal-
ized semivowels before semivowels (sa˜y-yama : sa ˙m-yama). Different
lengths of anusv¯ara are allophones additionally determined by the length
of the preceding vowel and by following consonant clusters or consonant
+ r
˚
. Among the nasal stops the palatal nasal is not a phoneme. It is an
allophone of m before a palatal stop (sañ-caya) and is a phonetic variant
2Labial and velar sounds, such as [F] and [x], are acoustically similar and share the
feature gravity. Historically, the voiceless velar fricative symbolized by ⟨gh⟩in English
words like cough is in Present Day English a voiceless labio-dental fricative [f] (Ladefoged,
1971, 44).
3We use word-ﬁnal as a translation of pad¯anta, that is, occurring at the end of a pada
(independent word, preverb, or compound element).
6.1. DISTINCTIVE ELEMENTS
83
of anusv¯ara in the same context (sa ˙m-caya). It is likewise an allophone
of n before a voiced palatal stop (jala ˙m piban, pibañ jalam).
Visarga and anusv¯ara are marginally contrastive with sibilants and
nasals respectively. Visarga occurs in contrastive distribution with s and
s. in limited environments: before k and p. For example, paspa´sa : antah. -
pura; paras-para : sarah. -padma; antah. -karan. a : uras-ka; v¯acas-pati :
v¯acah. pati. Anusv¯ara occurs in contrastive distribution with m in lim-
ited environments: sam-r¯at. : sa ˙m-r¯addha; samyak : sa ˙m-yata; amla,
a-ml¯ana : sa ˙m-l¯apa; and ¯a-mred. ita : sa ˙m-rih¯an. a. By virtue of this con-
trastive occurrence, they retain phonemic status. Yet the narrow range of
this contrastive occurrence raises questions. Fry (1941) denies that vis-
arga is phonemic, while Emeneau (1946) concludes that anusv¯ara is. Ar-
guments to show that phonetic segments in such cases are not phonemes
depend on showing that the particular examples of contrastive distribu-
tion do not properly belong to the same language. Hence Fry argues that
sibilants before velar and labial stops are holdovers from an earlier his-
torical dialect to which they properly belong. Vacek (1976) argues on
similar grounds that the retroﬂex sibilant s. is not phonemic but is an al-
lophone of the palatal and dental ´s and s. Similar reasoning would deny
that retroﬂex stops have phonemic status in Sanskrit.4
Prolonged vowels similarly have marginal phonemic status; they are
barely contrastive. Such vowels occur in contrastive distribution with
shorter durations of their corresponding vowels in fairly narrowly cir-
cumscribed contexts and conditions. The contrastive semantic content
is always of a paralinguistic nature (cf. Wennerstrom 2001, 60–4). In
A. 8.2.82–107, P¯an.ini prescribes prolonged vowels in such pragmatic
contexts as return salutation of an upper casteman, calling from afar,
speciﬁc ritual situations, and answering a question (the last optionally in
the word hi ‘certainly’). For example, the sentence-ﬁnal vowel is pro-
longed, as indicated by the numeral 3, in O;;
a;h :de;va;d!:a3 ehi devadattá3
“Come, Devadatta!” used in calling from afar but not in ehi devadatta
used otherwise. Because such paralinguistic content is not regarded as
semantically contrastive, prolonged vowels are not considered to be sep-
arate phonemes.
4Hock 1975, Hock 1979, and Hock 1993 examine the issue of retroﬂexion in Sanskrit
in detail.
84
CHAPTER 6. SOUND-BASED ENCODING
Pitch in Sanskrit is contrastive. Patañjali, the author of the great
commentary on P¯an.inian grammar (Mah¯abh¯as.ya, Kielhorn’s ed., I 2.10–
11, second century B. C. E.), provides the famous example of the word
índra-´satru, which, accented with initial high pitch as shown (preserv-
ing the original accent of the ﬁrst compound element índra ‘Indra’), is
a bahuvr¯ıhi compound (A. 6.2.1) meaning ‘having Indra as his slayer’.
When accented with high pitch on the ﬁnal syllable, however, indra-
´satrú is a tatpurus.a compound (A. 6.1.223) meaning ‘slayer of Indra’.
´Satapathabr¯ahman. a 1.6.3.8–10 tells of Tvas.t.r
˚
, who utters the word with
the improper accent in a rite to secure the birth of Vr
˚
tra to slay Indra and
fulﬁlls the import of his erroneous utterance, thus getting Vr
˚
tra slain by
Indra. Although lexical pitch is contrastive in Sanskrit, the differences in
the surface pitch that result from different phonotactic rules in the Pr¯ati-
´s¯akhyas proper to various Vedic schools (see §5.2.1) are not contrastive.
They are variants proper to different speech communities — the reciters
of various Vedic schools — and arguably to different dialects. Hence dis-
tinctions in surface pitch are not phonemic distinctions, because phone-
mic distinctions belong to the same language stricto sensu. Differences
in style and dialect are not included in the same phonemic system.
Eliminating just allophones and phonetic variants but still affording
phonemic status to the marginal phonemes, the set of phonemes of San-
skrit would consist of the sounds shown in TABLE 5 plus prolonged vow-
els, minus jihv¯am¯ul¯ıya, upadhm¯an¯ıya, and the palatal nasal. If marginal
phonemes also are eliminated, the set also subtracts the prolonged vow-
els, anusv¯ara, visarga, and retroﬂex s. (see TABLE 8). By comparison,
the P¯an.inian sound catalog differs from TABLE 5 in that it lists only
one length for each simple vowel, the short one, and does not include
anusv¯ara, visarga, jihv¯am¯ul¯ıya, or upadhm¯an¯ıya.
6.1.2
Generative grammar
Certain formal synchronic descriptions of language capture phonologi-
cal information that is not captured in an unordered set of phonemes of
the language. The P¯an.inian derivational system, for example, not only
captures the alternation of anusv¯ara, visarga, jihv¯am¯ul¯ıya, upadhm¯an¯ı-
ya and the palatal nasal with their respective allophones but in addition
obviates the need to posit the velar nasal as an original speech sound.
6.1. DISTINCTIVE ELEMENTS
85
Historical and comparative linguists recognize the velar nasal ˙n as an
independent phoneme in the set of phonemes of Sanskrit because it oc-
curs word ﬁnally in forms such as pr¯a˙n, pratya˙n, uda˙n, yu˙n, and kru˙n
in contrastive distribution with n and m, for example in balav¯an, r¯ajan,
and vipram. In P¯an.ini’s derivational system, however, the velar nasal
is consistently generated by rules from n. The forms in question are
masculine and feminine nominative singulars of nominal derivates of the
roots
√
anc ‘bend’ (DhP. 1.118, 1.595),
√
yuj ‘yoke’ (DhP. 7.7), and
√
krunc ‘shrink’ (DhP. 1.116) accounted for by A. 3.2.59. After its orig-
inal penultimate n is deleted by A. 6.4.24, the root
√
anc, followed by
nominal terminations termed sarvan¯amasth¯ana, is again supplied with
penultimate n by A. 7.1.70.5 Uncompounded, the root
√
yuj is similarly
supplied with penultimate n by A. 7.1.71. The palatal stop in all three
roots is replaced by a velar stop in speciﬁed contexts, including word-
ﬁnal context (A. 8.2.30). The n is replaced by anusv¯ara (A. 8.3.24) which
is in turn replaced by the featurally closest sound homorganic with the
following non-nasal stop (A. 8.4.58). Deletion of the ﬁnal stop (A. 8.2.23)
then leaves the velar nasal in the contrastive position (e.g. anc > ank >
a ˙mk > a˙nk > a˙n). By systematically accounting for the palatal/velar stop
alternation and replacing the preceding nasal by the featurally closest
sound homorganic with the following stop, P¯an.ini accounts for the al-
ternation of both palatal and velar nasals with n and m. The P¯an.inian
account of ﬁnal ˙n, like Jakobson’s (1929) account of Russian soft con-
sonants, recognizes that Sanskrit sounds form a system related to each
other by a system of features.
6.1.3
Historical linguistics
Analogous to the fact that generative descriptions of language capture
phonological information not available on the surface level, the historical
and comparative method captures phonological information not available
through synchronic analysis by using diachronic analysis. The phone-
mic inventory of a language changes through time. In a few rules strik-
ingly reminiscent of the rules of P¯an.ini discussed in the previous section,
5Original penultimate n in
√
krunc is excepted from deletion according to the K¯a´sik¯a
on A. 3.2.59
86
CHAPTER 6. SOUND-BASED ENCODING
Jakobson’s (1929) historical explanation of the loss of ﬁnal vowels after
soft consonants allowed him to explain the alternation of hard and soft
consonants in Russian systematically by a rule of palatalization before
front vowels prior to the loss of the ﬁnal vowel.
Although diachronic analysis may provide insight into the phonolog-
ical system of a language, a phonological system is a system which be-
longs to a particular language, in the narrow sense, that is, to a particular
speech community at a particular time. Such a system varies diachron-
ically and geographically. Hence one must distinguish the synchronic
phonemic analysis of Sanskrit from the diachronic analysis which at-
tempts to reconstruct the phonemics of Proto-Indic, Proto-Indo-Iranian,
or Proto-Indo-European (PIE). The phonemic inventory of these ear-
lier languages differs from that of Sanskrit in a number of respects. In
Szemerényi’s (1967) reconstruction of PIE (see Table 11), for instance,
retroﬂex sounds are absent, semivowels and vowels occur in complemen-
tary distribution, diphthongs are reducible to clusters of simple vowels,
which include vowels e and o, and the consonant inventory includes a
laryngeal stop.
In the case of the two marginal phonemes anusv¯ara and visarga, di-
achronic analysis interferes with the synchronic analysis of the phono-
logical system of Sanskrit. We noted in §6.1.1 that, in order to show that
these phonetic segments are not phonemes, linguists argue that the few
examples demonstrating contrastive distribution do not properly belong
to Sanskrit stricto sensu. Hence, concerning the examples in which s. oc-
curs in contrast to ´s and s, Vacek (1976, 409) argues, “All these words
must be considered as phonological foreignisms which exist in the pe-
riphery of the Sanskrit system. In all probability these words were bor-
rowed either from the Pr¯akrits or (via Pr¯akrits or a different OIA dialect)
from a non-IA source”. He concludes that s. is not a “genuine Sanskrit
phoneme”; “Therefore, the present state of Sanskrit sibilants has to be
deﬁned by referring s. to a foreign subsystem in the language” (1976,
412). Similarly, in order to demonstrate that visarga is not a Sanskrit pho-
neme, linguists argue that paspa´sa, paras-para, uras-ka, and v¯acas-pati
are borrowings from earlier stages of the language, and to demonstrate
that anusv¯ara is not a Sanskrit phoneme, linguists argue that sam-r¯at.,
samyak (unsuccessfully in these cases), and amla are borrowings from
different speech communities.
6.1. DISTINCTIVE ELEMENTS
87
In describing his method of analysis, Vacek (1976, 407) notes, “every
language is likely to be composed of two or more [coexistent phonemic]
subsystems — some of the subsystems may be foreign, some may be
traditionalisms and some may also be dialectal features from a different
local or social dialect”. He explains that it is typical for written or stan-
dard languages to be “composed of more than one phonological layer”
resulting from “the leveling of several . . . layers”.
Now, the methodology of segregating foreign loanwords and detect-
ing the inﬂuence of foreign phonological subsystems in a language is
sound for attempting to reconstruct the historical predecessors of the lan-
guage; yet one is completely misled if one understands the results syn-
chronically, in which case it can only be compared to ethnic cleansing.
Words with unusual phonological structure are vestiges of other speech
communities, just as idioms are vestiges of syntactic structures of an
historically prior dialect. Nevertheless, they are present in the language
and must be accounted for in the synchronic description of the language.
In isolation, segments in loanwords may present one system of contrasts
reminiscent of the language from which they were borrowed. Yet to eval-
uate synchronically the phonological structure of the language which has
adopted them, the sounds of the loanword must be compared with that of
words in the adopting language. Contrastive and complementary distri-
bution is always with respect to a speciﬁc context. The provision in the
deﬁnition of the phoneme that the sounds belong to the same language
in the strictest sense and that differences in style and dialect are not in-
cluded in the same phonemic system implies the necessity of specifying
the boundaries of the language clearly. If the loanwords are included in
the language, they must be explained in the same phonological system. If
they are considered part of some other language, they must be bracketed.
The same clarity of scope is required in framing a phonetic encoding
scheme.
6.1.4
Paralinguistic semantics
Another methodolical consideration concerning the scope of phonolog-
ical contrasts arises in the case of the other marginal phonemes. Pro-
longed vowels were not considered to be separate phonemes because
paralinguistic content was not regarded as semantically contrastive. One
88
CHAPTER 6. SOUND-BASED ENCODING
of the provisions in the deﬁnition of a phoneme was that for sounds in
parallel distribution to be contrastive they serve to differentiate seman-
tic content in a narrow sense. Such a segregation of semantic content
is somewhat arbitrary. Decisions to exclude paralinguistic information
were based on the conventions of the Roman alphabet to represent North-
west European languages. Similar decisions had earlier excluded dura-
tion, stress, and pitch from the concept of the phoneme, but these were
incorporated when phonologists realized the necessity of extending the
idea of contrastive distribution to these linguistic attributes in order to ac-
curately represent the minimally contrastive segments of languages such
as tonal languages. A comprehensive phonological system of the lan-
guage should be able to convey whatever information speech conveys.
It is precisely the purpose of semiotic theory to recognize that com-
munication transcends the arbitrary boundaries of such categorizations.
If paralinguistic information had to be separately categorized, a separate
phonological system would have to be adopted in order to explain how
such information was communicated. It would more likely be simpler to
segregate sytems of communicative analysis according to the means of
communication, namely, speech, static visual art, or movement — and
to include the paralinguistic information conveyed through speech in the
criteria for determining the phonological system — than it would be to
segregate systems of communicative analysis according to terrains of in-
formational content.
In view of the methodological points discussed in this and the pre-
vious section, it is necessary to broaden the conception of a phoneme to
tolerate linguistic variation, borrowing, and paralinguistic semantics. A
phoneme in such a comprehensive phonological system remains the min-
imally contrastive phonetic segment in a language on the basis of which
one word could be distinguished from another. However, it differs from
the strict deﬁnition by relaxing its limiting parameters. By a language is
meant a speciﬁed range of dialects including borrowings, and for sounds
in parallel distribution to be contrastive they serve to differentiate a speci-
ﬁed range of semantic content. Conventionally in Sanskrit linguistics and
critical theory, this semantic content includes paralinguistic content.6
6For a survey of semantic content included in P¯an.ini’s As.t. ¯adhy¯ay¯ı, including paralin-
guistic content, see Scharf (2009).
6.1. DISTINCTIVE ELEMENTS
89
6.1.5
Contrastive segments
Employing the broader concept of a phoneme just described, we reex-
amine the phonemic status of Sanskrit phonetic segments. A number of
sounds which were not phonemic in the narrow sense, are phonemic in
the broader sense. Since the semantic content of Sanskrit includes par-
alinguistic content, trimoraic duration, which conveys some distinction
in paralinguistic content, is contrastive and so phonemic. Since con-
trasts can extend to lexical borrowings, the sounds anusv¯ara and vis-
arga, which are in contrastive distribution over pairs with borrowings
like samr¯at. and v¯acaspati, are contrastive and so phonemic. So are the
retroﬂex sounds. Since the language in question ranges over various di-
alects of Vedic and classical Sanskrit, these dialects merge within that
range. Hence the retroﬂex L, l. and \h, l.h, short simple vowels ˘e and ˘o,
slightly lengthened short vowels in the V¯ajasaneyisa ˙mhit¯a, the ﬁrmer
and lighter y and v, and unreleased stops and semivowels (abhinidh¯ana),
which are in complementary distribution only insofar as such dialects are
distinguished, are now in contrastive distribution as indices of the par-
alinguistic semantic information that the utterances in which they occur
belong to those different dialects. Likewise, surface accentuation, which
is non-contrastive within a particular recitational tradition, is contrastive
when set side by side with differently accented text from another recita-
tional tradition within a single language that encompasses both traditions.
Similarly, different lengths and syllabiﬁcations of anusv¯ara and nasalized
vowels prolonged more than three morae (ra˙nga), which are allophonic
within a particular recitational tradition, are contrastive across the sin-
gle language that encompasses the various traditions. Since the language
in question ranges over various genres, including linguistics where di-
alectal and free phonetic variants are compared side by side, allophones,
which are contrastive in that genre (just as allophones in narrow tran-
scription are) become phonemic. Hence jihv¯am¯ul¯ıya, upadhm¯an¯ıya, and
nasal semivowels are phonemic in the comprehensive phonological sys-
tem. And since the palatal nasal ñ in technical terms in linguistic treatises
(e. g. añ, ñit) occurs in contrastive distribution with n and m, it is phone-
mic in the broader sense. Finally, epenthetic nasals (yama) and vowels
(svarabhakti), which are entirely predictable in particular Vedic dialects
by rules stated in treatises concerned with those particular dialects, are
unpredictable in the broader range of the Sanskrit language, in which the
90
CHAPTER 6. SOUND-BASED ENCODING
various dialects merge.
On the other hand, a few phonetic segments discussed in the pre-
ceding chapter that were not phonemic in the narrow sense of the term
are neither phonemic in the broader sense of the term, because they are
not contrastive. It is not necessary to distinguish two or three lengths of
contrasting svarabhakti vowels, even though the Catur¯adhy¯ayik¯a notices
a distinction in length and reports an authority that notices a distinction
between two different lengths. Catur¯adhy¯ayik¯a 1.4.10 describes svara-
bhakti after an r before a spirant followed by a vowel equivalent to half
an a, or a quarter according to some authorities. Catur¯adhy¯ayik¯a 1.4.11
describes a shorter svarabhakti after r before another consonant besides
a spirant equal to a quarter a or an eighth according to the authorities by
which the longer svarabhakti is a quarter. Deshpande (1997b, 258) argues
that the term sphot.ana refers to the shorter svarabhakti. The svarabhakti
termed sphot.ana carries the accent of the previous vowel and does not
dismember the consonant cluster according to Catur¯adhy¯ayik¯a 1.4.13.
There are two issues to address. First, must one distinguish a svarabhakti
of length 1
8 to accomodate the short svarabhakti noticed by the reported
authority in addition to two lengths of svarabhakti 1
4, and 1
2 noticed by
the authors of the Catur¯adhy¯ayik¯a itself? Second, are the two lengths
distinguished by each authority contrastive? Both questions must be an-
swered in the negative. First, it is not clear that the two authorities offer
anything more than two scientiﬁc estimates regarding the length of the
same epenthetic segments in the same text in the same tradition. There is
no independent evidence of two different traditions of recitation that con-
trast with each other, each of which recites two lengths of svarabhakti.
Should such evidence be found, it would serve as grounds to contrast the
two traditions, and the svarabhaktis in each tradition would contrast with
the svarabhaktis in the other tradition as indices of the broader semantic
content that the texts in which they occur belong to distinct traditions.
Second, the two distinct lengths of svarabhakti reported by each author-
ity are allophonic, not phonemic. The contexts in which the long svara-
bhakti occurs (before spirants) are different from the contexts in which
the short svarabhakti occurs (i. e. before other consonants), so long svara-
bhakti does not contrast with short svarabhakti in either tradition. More-
over, it is not clear that the distinction as to whether svarabhakti inherits
the accent of the preceding vowel is associated with the length of the
6.1. DISTINCTIVE ELEMENTS
91
svarabhakti as argued by Deshpande. There is no independent evidence
that long svarabhakti vowels do not inherit the high or low pitch of the
preceding vowel, nor that short svarabhakti vowels are not recited with
accumulated (pracaya) pitch after a svarita vowel. There is therefore no
independent evidence that the term sphot.ana applies only to the short
svarabhakti as Deshpande argues. It is doubtful that it does and doubtful
that the text itself asserts a different behavior regarding accent inheri-
tance. Therefore there is insufﬁcient evidence to establish any contrast
between short and long svarabhakti. Should evidence be found to estab-
lish such a contrast, of course, it would serve as grounds to recognize
short and long svarabhakti as distinct phonemes.
6.1.6
Phoneme in the broader sense
It is clear that the limiting parameters placed on the concept of a pho-
neme, in the strict and narrow sense, diminish its utility as the sole basis
for a single character-encoding scheme for Sanskrit texts. If an encoding
scheme is to convey the same information that the language conveys, it
should provide the means to distinguish all minimally contrastive seg-
ments, insofar as any contrastive information is conveyed by the differ-
ence between those segments. And it must include differences in style,
dialect, and genre, insofar as these are signiﬁcant contrasts within the
scope of the collection encoded. The corpus of Sanskrit texts includes
various dialects of Vedic and classical as well as more varied speech
communities such as Buddhist Hybrid Sanskrit (Edgerton, 1970). It in-
cludes borrowings from early dialects, Pr¯akrits, substrate languages (cf.
Witzel 1999, Hock 1975), and foreign languages. In many cases, the only
evidence for such loan words is in the Sanskrit itself. And extant doc-
uments indicate paralinguistic semantic content through such devices as
prolonged vowels, at least in the Vedic texts. The extended parameters in
the concept of a phoneme discussed in sections 6.1.3–6.1.5 are adequate
to convey the desired contrasts. Hence the phoneme in the broad sense is
suitable to serve as the basis for a single character-encoding scheme for
all Sanskrit dialects, borrowings, and linguistic uses.
92
CHAPTER 6. SOUND-BASED ENCODING
6.1.7
Contrastive phonologies
Incompatible phonological schemes have been proposed for the descrip-
tion of Sanskrit (see above §5.2). The form in which Sanskrit and Ve-
dic texts have been received in oral recitation as well as in manuscripts
and the various scripts and encodings used to transmit Sanskrit texts all
adopt — at least implicitly — some phonological scheme. The vari-
ous encodings used to transmit Sanskrit texts are not entirely compatible
with one another. Information contained in one phonological scheme
cannot necessarily be captured in another. Although we have attempted
to devise an encoding that captures all the distinctions made by all the
phonological schemes used to describe and transmit Sanskrit, most ex-
isting texts do not represent all these distinctions. Most Sanskrit texts
do not represent epenthetic nasals (yamas and n¯asikya), unreleased stops
and semivowels (abhinidh¯ana), epenthetic vowels (svarabhakti), accent,
distinctions in the weight of semivowels, and distinctions in types of
anusv¯ara. Where accent is represented, it is often not represented in such
a way that one can determine how it is to be mapped onto the range
of tones needed to describe the various traditions of Vedic accentuation
completely. When information is not provided about epenthetic nasals
(yamas and n¯asikya), unreleased stops and semivowels (abhinidh¯ana),
epenthetic vowels (svarabhakti), accent, semivowel weight, and length
of anusv¯ara, these features should simply be ignored. Since sufﬁcient
information is not always available to encode a text with the full reper-
toire of phonological distinctions required for a completely contrastive
description, an encoding scheme must provide defaults to allow the in-
formation that is provided to be represented, even if that information is
less than complete.
In the case of epenthetic sounds (yamas, n¯asikya, and svarabhakti),
the default is simple: leave them out. In the case of the unusual weight of
semivowels, unreleased varieties of stops and semivowels, and accented
vowels, in the absence of special information, the normal, clear, unmod-
iﬁed sound will be the default. If a semivowel is not speciﬁed as heavy,
light, or unreleased, the default semivowel, without speciﬁcation of spe-
cial weight will be used. If accent is not speciﬁed, the monotone vowel
will be used. In such cases the default does not necessarily indicate the
lack of the special feature; it merely indicates the absence of information
concerning the feature. Only when the text does specify a particular con-
6.2. HIGHER-ORDER PROTOCOLS
93
trastive feature can the default be construed as indicating the lack of that
feature.
In the case of anusv¯ara, it is necessary to encode a unit to repre-
sent a default anusv¯ara unspeciﬁed as regards length — in addition to
a short, long, heavy, and two-mora anusv¯ara. Although the V¯ajasaneyi-
pr¯ati´s¯akhya (4.149) assigns a length of 1
2 mora to the short anusv¯ara it de-
scribes as contrasting with a long anusv¯ara, and the R
˚
kpr¯ati´s¯akhya (1.34)
assigns the same weight of 1
2 mora to the only anusv¯ara it approves, it
would not be suitable to use the short anusv¯ara as a default anusv¯ara,
since the R
˚
kpr¯ati´s¯akhya (13.32–33) reports that other authorities specify
the short and long anusv¯ara as measuring 1
4 mora and 3
4 mora respec-
tively. The R
˚
kpr¯ati´s¯akhya anusv¯ara is thereby distinguished from both
short and long anusv¯ara. Similarly, it is necessary to encode a system
of three accents in addition to the system of four tones and monotone,
because many texts indicate three accents without providing any infor-
mation about which of the four tones are represented. Ancient Indian
linguists provide rules of accent sandhi that transform isolated accent
into contextual tone. To allow encoding of accent both before and after
the application of these rules, it is necessary to adopt both a system of
three underlying accents (to capture the pitch distribution before accent
sandhi) as well as four surface tones (to capture the pitch distribution
after accent sandhi). While the surface tone scheme is required to cap-
ture the contrasts of different traditions of pitch distribution after accent
sandhi, European scholars have established a tradition of representing
Vedic accent utilizing the system of three contrasting pitches belonging
to the derivational level at which accent sandhi has not yet applied.
6.2
Higher-order protocols
There are alternatives to creating a single character-encoding scheme
for all Sanskrit dialects, borrowings, and linguistic uses.
One could
use higher-order text-encoding devices to bracket off stretches of text
for which the character-encoding scheme was inadequate to distinguish
the informational content. Thus one could bracket off different dialects,
loanwords, and paralinguistic uses of language by Extensible Markup
Language (XML) tags and employ a separate character-encoding scheme
for such sequences that was adequate to distinguish the contrasts within
94
CHAPTER 6. SOUND-BASED ENCODING
it. For example, the unaspirated and aspirated retroﬂex lateral ﬂaps / /
and / h/ do not occur in Classical Sanskrit; the phonemes /ã/ and /ãh/
do. In certain R
˚
gvedic dialects, unaspirated and aspirated retroﬂex lat-
eral ﬂaps occur in complementary distribution with [ã], [ãh] and hence
are allophones of [ã], [ãh]. In separate encoding schemes for Classical
Sanskrit and for the R
˚
gvedic dialects, encodings are necessary only for
the two phonemes /ã/, /ãh/.
In a database that includes passages both in the R
˚
gvedic dialect and in
the Classical Sanskrit dialect, one could tag the passages in one or both of
the dialects and apply phonetic rules to produce the contextually appro-
priate allophones proper to each dialect. For instance, Y¯aska’s Nirukta,
which is predominantly in the Classical Sanskrit dialect, cites passages
in the R
˚
gvedic dialect. Nirukta 3.11 cites R
˚
V. 2.23.9, which contains
the word tal.ito with an intervocalic retroﬂex lateral ﬂap, Romanized l..
Nirukta 3.11 then cites the linguist ´S¯akap¯un.i explaining that tal.it refers
to lightning in the passage vidyut tal.id bhavat¯ıti ´s¯akap¯un. ih. . Rather than
including both the retroﬂex lateral ﬂap [ ] and [ã] in the character encod-
ing, one might tag the text in R
˚
gvedic dialect and allow special rules to
realize /ã/ as the retroﬂex lateral ﬂap [ ] in text so tagged. Such a tagging
in the latter passage could be achieved as follows:
<embed dialect="rv">vidyut taqid bhavati</embed>
iti SAkapURiH
Within the tagged dialect portion, intervocalic /ã/ will always be real-
ized as the retroﬂex lateral ﬂap [ ]; outside such tags, it will always be
realized as [ã].
It is not likely that such a system would be practical at the present
stage, however, since this encoding would have to be fairly ﬁne-grained,
and since we possess insufﬁcient information about dialectal differences
and loanwords. We are uncertain, for instance, whether ´S¯akap¯un.i writes
consistently in R
˚
gvedic dialect or just cites the single word tal.it in R
˚
g-
vedic dialect. If the latter, the above demonstration includes too much of
the passage within the <embed> tag. Moreover the Nirukta itself uses
the retroﬂex l., l.h even when not directly citing. Immediately after refer-
ring to ´S¯akap¯un.i, the Nirukta continues, s¯a hy avat¯al.ayati, using l. outside
R
˚
gvedic dialect. The text as received makes no mention/use distinction.
With the lack of reliable information about the author’s dialect, one is
6.2. HIGHER-ORDER PROTOCOLS
95
forced to accept that [ã], [ãh] and unaspirated/aspirated retroﬂex lateral
ﬂaps [ ], [ h] occur in contrastive distribution. Sequences Vl.V occur
in the Nirukta external to R
˚
gvedic citations and alongside Vd. V, setting
[ã] and the retroﬂex lateral ﬂap [ ] in contrast; for example, avat¯al.ayati
‘strikes down’ (3.11) : lambac¯ud. aka ‘one having long locks (of hair)’
(1.14). Therefore, the unaspirated and aspirated retroﬂex lateral ﬂaps
[ ], [ h] occur in contrastive distribution with [ã], [ãh] not only within
the collection comprising all the dialects of Sanskrit, but even in the clas-
sical Sanskrit dialect that excludes the R
˚
gvedic dialect. Hence all four
must be encoded separately at the character level.
Similarly, an encoding of surface accent at the character level must
embrace the range of pitches utilized across Vedic schools and dialects
because it is not always practical to use higher-order text-encoding de-
vices to bracket off excerpts from the texts of various Vedic schools and
dialects. Many texts, especially ritual texts, cite passages from more than
one Vedic sa ˙mhit¯a. One could bracket passages of the ´S¯akalasa ˙mhit¯a
of the R
˚
gveda and passages of the V¯ajasaneyisa ˙mhit¯a of the Yajurveda
separately in XML tags and employ separate encoding schemes ade-
quate to capture the surface pitch contrasts within each.7 Yet many ritual
texts include passages, which, though accented in accordance with ei-
ther the system described in the R
˚
kpr¯ati´s¯akhya or that described in the
V¯ajasaneyipr¯ati´s¯akhya, are untraced to known collections. To be sure
higher level text bracketing may be preferrable in instances in which the
signiﬁcance of accentual marks is only known by identifying the text and
knowing the accentual system described by a particular phonetic treatise.
There are, however, instances in which the accentual system is known,
yet the text is unidentiﬁed. Such texts lack clear criteria for higher-order
tagging. While a character-level surface pitch encoding does require
choice of pitch level, it does not commit one to textual identiﬁcations
for which there is no evidence.
Separately each system described in section 5.2.1 requires the dis-
tinction of only three pitches. The system of the R
˚
kpr¯ati´s¯akhya distin-
7Neither the M¯adhyandina nor the K¯an. va recension of the V¯ajasaneyisa ˙mhit¯a employs
the system described in the V¯ajasaneyipr¯ati´s¯akhya according to which one would expect
the vertical line above the high-pitched syllable rather than above the circumﬂexed syllable,
if graphic marks correspond with pitch contours as suggested by Witzel 1974. But several
sa ˙mhit¯as (cf. §3.2) do employ a vertical line above the high-pitched syllable (M¯ım¯a ˙msaka,
1964, 12, 21, 25, 42).
96
CHAPTER 6. SOUND-BASED ENCODING
guishes between extra-high, high, and low, while the system of P¯an.ini
and the V¯ajasaneyipr¯ati´s¯akhya distinguishes between high, low, and ex-
tra-low. Although each of the systems of surface accentuation distin-
guishes only three pitches, a system of surface accentuation that will ac-
commodate contrasts across these systems must distinguish four pitches.
A system that captures distinction in pitch across Vedic dialects must
therefore distinguish between extra-high, high, low, and extra-low. Con-
sequently, it is necessary to devise a character-encoding scheme adequate
to capture phonemic distinctions in the broad sense across all Sanskrit di-
alects.
Higher-level bracketing does not seem suitable to capture distinctions
in various Sanskrit dialects and loan words since there may be insufﬁ-
cient evidence to identify the various dialects and source languages for
loan words. There exist, however, phonetic distinctions that are more
suitably captured by using higher-level bracketing than by incorporating
them in a character encoding based on the phoneme in the broad sense.
Higher-level bracketing is appropriate where the phonetic distinction is
made only with explicit reference to units at a higher level than the pho-
neme. For instance, higher-level bracketing is appropriate where the pho-
netic distinction is made only with reference to lexical items. For exam-
ple, Malla´sarmakr
˚
ta´siks. ¯a 45–46 describes nasalized vowels prolonged
to ﬁve and six morae. While there is no reason to doubt the phonetic
accuracy of the description, there is no need to include the distinction of
ﬁve- and six-mora lengths in the featural scheme of Sanskrit nor to in-
clude nasalized vowels having a length of ﬁve or six morae in the broadly
phonemic character inventory. Such lengths need not be included be-
cause their only occurrence is in the ﬁnal vowels of particular lexical
items. The length of ﬁve morae occurs only in the word mah¯a, and the
length of six morae occurs only in the word ati (Malla´sarmakr
˚
ta´siks. ¯a
46). Because the occurrence is lexically speciﬁc, the phenomenon is best
described lexically, as it was described by the ´Siks.¯a itself. The ´Siks.¯a
calls the occurrence of these extra-long nasalized vowels mah¯ara˙nga and
atira˙nga, i.e. the ra˙nga of mah¯a and the ra˙nga of ati. The deﬁning char-
acter of the distinguishing feature seems to be the lexical item rather than
the length of the sound. Therefore, we consider it a lexical feature rather
than a phonetic one.
It is difﬁcult to capture suprasegmental features such as accent in
6.2. HIGHER-ORDER PROTOCOLS
97
a segmental encoding; hence, one might choose to utilize higher-order
units — in particular syllabic units — to encode accent. One could thus
tag syllables and assign accentual features to them. Indian phonetic trea-
tises themselves recognized the syllabic nature of accent. As mentioned
in §4.2.2, ancient Indian linguistic treatises recognized that vocalic ac-
cent spread to adjacent consonants. Other Indian treatises limited accent
to vowels and ignored consonants in accentual rules (Vy¯a. Pa. 33). Yet
difﬁculties would arise in attempting to encode the accent of syllabiﬁed
visarga and anusv¯ara. In these cases the techniques of marking accent in
Vedic texts are more easily correlated with individual characters. Certain
Vedic traditions mark accent of the non-vocalic elements anusv¯ara and
visarga. Such marking, and the oral recitation of the texts, demonstrate
that anusv¯ara and visarga are syllabiﬁed. Visarga is syllabiﬁed by echo-
ing the preceding vowel or ﬁnal subsegment of an open diphthong, and
anusv¯ara is syllabiﬁed in White Yajurvedic recitation as g˜u. Yet no vowel
belongs in the underlying text and no vowel is written. Since the syllab-
iﬁcation is clearly indicated by the marking of accent on the anusv¯ara
and visarga characters and the syllabiﬁcation can be most reliably in-
ferred from the accent marking, it seems preferable, given the lack of
other explicit information about the syllabiﬁcation of these elements, to
include accent in a character encoding.8 In the purely segmental encod-
ing SLP2, we include characters for high-pitched visarga, low-pitched
visarga, and svarita visarga, and for low-pitched anusv¯ara. We do not,
however, include characters for high-pitched and svarita anusv¯ara. Al-
though the vertical stroke above, used in Devan¯agar¯ı script to indicate a
svarita in the V¯ajasaneyisa ˙mhit¯a, is found above the sign for an anusv¯ara,
it is found there instead of above the sign for the preceding syllable onset
and core, unlike the signs for visarga accent, which appear in addition to
the vertical stroke above the preceding syllable onset and core, and un-
like the horizontal stroke that indicates low pitch, which appears below
the sign for anusv¯ara in addition to below the sign for the syllable onset
and core. The vertical stroke above the sign for anusv¯ara is therefore a
graphic transposition that still indicates the accent of the entire syllable,
8Phonetic
treatises
disagree
as
to
whether
anusv¯ara
is
syllabiﬁed.
Varn. aratnaprad¯ipik¯a´siks. ¯a 50-51 states that anusv¯ara is among the group of sounds
called yogav¯aha that are devoid of their own accent. Several ´Siks.¯as (e.g. Ke´sav¯i´siks. ¯a 5,
Tatkr
˚
t¯a pady¯atmik¯a ´Siks. ¯a 15, Svarabhaktilaks.an. apari´sis.t.a´siks. ¯a 19), in contrast, state that
anusv¯ara is replaced by nasalized a when a spirant or r follows.
98
CHAPTER 6. SOUND-BASED ENCODING
not a distinct accent of the anusv¯ara. Since the svarita accent of the syl-
lable is encoded by the vowel accent, it would be redundant to encode it
again for the anusv¯ara.
6.2.1
The phonetic encoding schemes
In view of the discussion of criteria in section 6.1 “Criteria for select-
ing distinctive elements to encode”, we have decided not to limit our
phonetic encoding scheme to a strictly phonemic one. Rather, by using
the concept of a phoneme in the broad sense, we have designed a single
scheme capable of showing all the contrastive information in the corpus
of Sanskrit texts. The phonetic encoding scheme encodes the segments
shown in TABLE 5, described in the notes appended thereunto, and dis-
cussed in section 6.1.5 “Contrastive segments”. The scheme has three
forms called Sanskrit Library Phonetic Basic (SLP1) (see Appendix B),
Sanskrit Library Phonetic Segmental (SLP2) (see Appendix C), and San-
skrit Library Phonetic Featural (SLP3) (see Appendix D). In the ﬁrst, we
associate each sound in TABLE 5 with an upper- or lower-case alphabetic
Roman character, with the additional use of several other characters from
the ASCII set for the aspirated retroﬂex lateral ﬂap and for modiﬁers.
Modiﬁers signify alterations of stricture, length, accent, and nasaliza-
tion. In SLP2 we associate a single codepoint with each sound, includ-
ing all varieties of stricture, length, accent, and nasalization. In SLP3 we
propose a featural encoding of Sanskrit based on Halle’s (2000) set of
articulatory features described in Table 4.
In view of the discussion of higher-level bracketing in section 6.2
“Higher-order protocols”, we include within the scope of the single lan-
guage encoded all the various dialects of Sanskrit and Vedic as well as
loanwords regardless of their source. On the other hand, we limit our en-
coding to items that contrast by distinctions identiﬁed in phonetic terms
and exclude items that contrast only in terms of higher-order units such
as lexemes. Yet we do maintain the encoding of accent at the charac-
ter level in spite of its suprasegmental status. By utilizing modiﬁers to
capture the accentual features of Sanskrit sounds, SLP1 encodes the four
pitch distinctions necessary for cross-dialect encoding of surface pitch
by a numeral ranging from 6 to 9. Pitch contours that combine more than
one pitch within a single character are coded by combinations of numer-
6.2. HIGHER-ORDER PROTOCOLS
99
als. For example, the vowel a with a dependent circumﬂex which falls
from extra-high to high according to the description in the R
˚
kpr¯ati´s¯akhya
is coded a^98; with the independent circumﬂex before a high-pitched
or circumﬂexed syllable, a^97. As described in the V¯ajasaneyipr¯ati-
´s¯akhya, these are coded a^87 and a^86 respectively. Contours that
include three pitches within a single vowel can be similarly accommo-
dated.
100
CHAPTER 6. SOUND-BASED ENCODING
Chapter 7
Script-based encoding
Although discussion so far has focused on sound-based encoding, we
note that there are many applications for script-based encoding. Much
of the human cultural heritage has been transmitted primarily in written
form. Some forms of writing are independent of spoken language (Hy-
man, 2006), and written and spoken language manifest parallel struc-
tures that are partly independent (Weir 1967; Vachek 1973). The typo-
graphic form — meaning the visual aspects of written and printed lan-
guage (Waller, 1988, 5) — conveys information that may need to be en-
coded in machine-readable documents. Researchers concerned with his-
torical manuscripts, for instance, attend to characteristics such as scribal
hands, ink color, abbreviations, letterforms, ductus,1 margins, and spac-
ing (Kropaˇc, 1991).
A focus on the primacy of spoken language in particular contexts
need not, and should not, lead to a denigration of writing. In the 1920s
the Soviet psychologist L. S. Vygotsky recognized that writing is both the
product of human cognition and an environmental factor that contributes
to cognitive development. More adventurously, he argued that the in-
vention of writing led historically to new complexity in human cognition
(Vygotskii 2005, 417; Cole, Levitin & Luria 2006, 44–45).2 The fact
1Cf. Skelton 2008, 161.
2On the sociogenesis of such complex cultural products as writing see also (Tomasello,
1999, 41–48) and (Damerow, 1996, 316–321).
101
102
CHAPTER 7. SCRIPT-BASED ENCODING
that human psychology shapes writing, and writing in turn shapes hu-
man psychology, he argued, produces a feedback loop that allowed for
rapid evolution. Writing is associated with the rise of complex forms of
social and cultural organization, the accrual of speciﬁc historical knowl-
edge, and the abstract thought that led to the sciences and technologies.
The written document allows for increasing distance from the primary
act of communication; it “speaks” to an imagined reader, or a generally
literate audience. Writing abstracts distinctive features from the chaine
de la parôle, levels the differences between spoken language dialects
(and a fortiori idiolects) (Weir, 1967, 172), and removes many of the
context-dependent features of face-to-face interaction.
There is no question that writing contributes to certain elements of
cognitive development, and that it has historically been associated with
the development of complex social organization and the accrual of spe-
ciﬁc knowledge.
The accrual of speciﬁc knowledge itself allows for
progress in science and technology. However, the contention that writing
is directly responsible for the development of abstract thought in human
evolution is speculative at best. Indeed, the opposite may be the case.
The reliance on writing may contribute to the deterioration of cognitive
ability. In the Phaedrus, Socrates denigrates writing by relating the words
of king Thamus of the Egyptian Thebes to the god Theuth when Theuth
revealed the art of writing to him. When Theuth promised that it would
make the people wiser and improve their memories, king Thamus retorts
that it would have the very opposite effect. He says, “it will implant
forgetfulness in their souls; they will cease to exercise memory because
they rely on that which is written”. (Phaedrus 275a.) Speciﬁc knowl-
edge inherited through the oral tradition could produce the development
of abstract thought just as well as speciﬁc knowledge inherited through
written means. The development of linguistic sciences in India are evi-
dence against the claim that writing is responsible for the development
of the abstract thought that led to the sciences. These sciences developed
in oral medium. P¯an.ini composed the As.t. ¯adhy¯ay¯ı using phonetic, not
visual, markers. The oral transmission of Vedic texts spawned the devel-
opment of mnemonic techniques that led to prodigous feats of memory.
To this day students trained in traditional methods know thousands of
verses or s¯utras by heart. The composition of poetry in early cultures
attests to the ability to speak to an imagined reader in the abstract, in the
7.1. FEATURAL ANALYSIS
103
absence of writing.
Although writing cannot claim sole responsibility for producing ab-
stract thought in the history of human cognitive development, neverthe-
less writing has been the dominant medium for knowledge transmission
in the past couple of millenia. Attention to the structure of written lan-
guage is important to historians, psychologists (Ellis, 1979), and educa-
tors. Moreover the study of written language has technological appli-
cation in optical character recognition (OCR), handwriting recognition,
and the design of new media (Rosenberger, 1998). The investigation of
written-language structure begins with segmentation. Writing systems
give different cues to segmentation at different levels, for instance by
punctuation and regularity of spacing, which may be present or absent to
varying degrees. Words are delimited in most present-day Western writ-
ing, whereas in East Asian writing they are not (nor are they in many pre-
modern Western manuscripts) (Saenger, 1991); printed Sanskrit texts in
Devan¯agar¯ı lie somewhere in-between, with word separation only where
sandhi and the graphotactic structure of the script permit it. Analysis of
written language into abstract units called characters that are repeated
with variable visual features is the basis for most computer processing of
language as it is known today. Characters may be discretely realized, as
in contemporary English texts, or unsegmented, as in a printed or hand-
written Arabic text (Abu-Rabia & Taha, 2006). Handwriting (as well as
printing, insofar as its glyphs are imitative of handwritten ones) can be
analyzed into units smaller than the character, in particular, “a set of up-
strokes and downstrokes ordered in time” (Mermelstein & Eden, 1964,
257). Such a level of analysis takes into account the physical mechanism
involved in writing and is capable of identifying units that are invariant,
while characters may be realized with inﬁnite variation.
7.1
Featural analysis
Type designers have long recognized that characters can be decomposed
into primitive graphic elements (Mohanty, 1998). Albrecht Dürer (1471–
1528) designed an alphabet using only ruler and compass construction
(Hoenig, 1990). The designers of the Romain du Roi, commissioned by
Louis XIV and completed in 1745, “drew up the design of each letter
on a strictly analytical and mathematical basis, using as their norm a
104
CHAPTER 7. SCRIPT-BASED ENCODING
rectangle subdivided into 2,304 (i.e. 64 times 36) squares” (Steinberg,
1961, 169).3 These approaches anticipate a rigorous featural analysis of
graphemes.
Notwithstanding the pessimism of Vachek (1973, 48)4 with respect to
such efforts, psychologists of visual perception and pattern recognition
in the 1960s and 1970s developed schemes for classifying characters of
the Latin alphabet by means of distinctive features, akin to those that
had become popular in phonology (Gibson 1969, 86–91; Geyer 1970;
Laughery 1971; Geyer & DeWald 1973; Massaro 1973; Naus & Shill-
man 1976; Estes 1978, 171–177; Reed 1978).5 In addition, the quest for
visual features was inspired by the description of processing in the pri-
mary visual cortex by Hubel & Wiesel (1968).6 Gibson (1969, 86–88)
gives criteria for establishing a set of distinctive features for an alphabet:
1) the features had to be critical ones, present in some members of
the set but not in others, so as to present a contrast; 2) they should
be relational so as to be invariant under brightness, size, and per-
spective transformations; 3) they should yield a unique pattern for
each grapheme; and 4) the list should be reasonably economical.
Gibson (1969, 88) proposes a set of distinctive features, divided into ﬁve
classes, for capital letters of the Roman alphabet:
1. straight: [± horizontal], [± vertical], [± diagonal /], [± diagonal \]
2. curve: [± closed], [± open V], [± open H]
3. intersection: [± intersection]
4. redundancy: [± cyclic change], [± symmetry]
5. discontinuity: [± vertical], [± horizontal]
3Cf. Morison (1972, 316–317).
4Cf. Badecker 1996, 72.
5An extension of featural theories is visual grammar theories (Reed, 1978, 145–146,
150–151). A set of attributes used in a visual grammar of the upper-case Roman letters in-
cludes {shaft, leg, arm, bay, closure, weld, inlet, notch, hook, crossing, symmetry, marker}
(Reed, 1978, 146). Cf. Narasimhan & Reddy (1967).
Featural analysis has also been applied to graphic systems other than written language,
e. g. children’s drawings (Krampen, 1986, 87–88).
6See Gibson (1969, 88–89).
7.1. FEATURAL ANALYSIS
105
Similar sets of features were proposed by Geyer (1970) and Laughery
(1971), both of whom made use of computer simulation models; the lat-
ter author proposed features to distinguish not only capital letters but
also Arabic numerals. The validity of such feature sets can be tested
by empirical data for letter confusion errors derived from psychological
experiments (Geyer & DeWald, 1973).
These schemes take the form of feature lists, that is, essentially un-
ordered sets of features. It is possible also to organize features into trees,
which have an inherent geometry, reﬂecting systemic relations between
features (cf. p. 77, above). Tversky (1977, 346) presents a feature tree
for the lower-case letters (save ⟨w⟩), using the binary features {curved,
arched, vertical, angular, circular, tailed, long, dotted, twisted, forked}.
In developing her Prosodic Font system, Rosenberger (1998, 41–42)
identiﬁed ﬁve similarity groups for Latin characters: “[t]hose that are
constructed as combinations of vertical strokes and circles, those formed
of circles left open for some interval (e. g. like a horseshoe) and a vertical
line, those constructed of slanted lines, the class of letters that combines
elements from the other three, and the letter ‘s”’.7 Her original system
used only four stroke primitives: line, circle, open circle, and s. Because
of implementation difﬁculties, a second system added three stroke prim-
itives (dot, curved tail, cross-bar) and recognized two basic principles of
stroke positioning: consecutiveness vs. simultaneity and dependence vs.
independence (Rosenberger, 1998, 43–47).
Analysis of characters in terms of graphic features is important in
work on OCR and handwriting recognition (Bansal & Sinha, 2000). In
the case of cursive handwriting, general features (both single-valued and
multi-valued) may be tested for each column within the word rectan-
gle, e. g.: projection proﬁle, partial projection proﬁle, upper/lower word
proﬁle, background to ink transitions, grayscale invariance, Gaussian
smoothing, and Gaussian derivatives (Rath & Manmatha, 2003). “Word
spotting” is an information retrieval technique that uses one or more
images of a written or printed word as a prototype (or prototypes) to
ﬁnd other tokens of the same word in a set of document images. This
approach treats the word as a holistic entity, rather than as a string of
graphemes. Gradient, Structural, and Concavity (GSC) features are ex-
tracted from the entire word at multiple scales/resolutions. The gradient
7Cf. Estes (1978, 175).
106
CHAPTER 7. SCRIPT-BASED ENCODING
features indicate changes in stroke orientation; the structural features in-
dicate the presence of corners as well as diagonal, horizontal, and vertical
lines; and the concavity features indicate “bowls” and open cavities (Sri-
hari, Srinivasan, Huang & Shetty, 2006).8
In an OCR system for Devan¯agar¯ı, characters (together with frequent
ligatures) are pre-classiﬁed into major categories depending on the posi-
tion (or absence) of a vertical bar (termed danda by the authors) (Govin-
daraju et al., 2004). Gradients (i. e. the magnitude and direction of in-
tensity changes around the pixels of a digitized image of a character) are
thresholded and quantized for a 3 × 3 grid. The resulting feature vector
of length 72 forms the input to a neural network with an input layer of
72 perceptrons. The network classiﬁes characters from a blind test set at
around 95% accuracy (Govindaraju et al., 2004).9
Chinese characters (hanzi/kanji) are traditionally classiﬁed (in dictio-
naries and reference works) on the basis of a number (most commonly
189 or 214) basic elements termed “radicals”. In the Rosenberg Graph-
ical System the characters are more conveniently classiﬁed according to
22 basic graphical elements, which can be subsumed under ﬁve cate-
gories of stroke direction: (1) horizontal, (2) vertical, (3) sloping down-
ward to the left, (4) sloping downward to the right, (5) reverse curved
down (Barlow, 1995). In OCR of Chinese characters, characters are mod-
eled as a set of linear primitives (Suen, Mori, Kim & Leung, 2003). It
is possible analytically to decompose Devan¯agar¯ı characters into primi-
tives, but these primitives are non-linear, and no computational technique
has been implemented to decompose characters in such a fashion (Kom-
palli, 2007). Chinese calligraphy recognizes seven or eight basic strokes.
A computational implementation demands further distinctions. Thus the
Hàn Zì software implemented by Douglas Hofstadter and David Leake
in the 1980s required about 40 distinct basic strokes (Hofstadter, 1985,
294).
Donald Knuth’s METAFONT system, begun in 1978 in collabora-
tion with Charles Bigelow and Kris Holmes, implements a high-level
8Such a computational approach may not be wholly foreign to ways in which humans
recognize words. Psychological evidence suggests that parallel to other word-identiﬁcation
processes is a holistic process that is sensitive to salient peripheral features of a word’s
shape (Beech & Mayall, 2007).
9For an elaboration of this model, including reports of word accuracy, see Kompalli
(2007).
7.1. FEATURAL ANALYSIS
107
programming language that can be used to construct font glyphs math-
ematically. METAFONT allows for the creation of a family of fonts, by
specifying a fairly large number (about 60) of parameters that determine
the particular realization of glyphs. The best known fonts created with
METAFONT are Knuth’s own Computer Modern fonts, frequently used
with TEX. In Indic typography METAFONT was ﬁrst used to create a
Devan¯agar¯ı font (NCSD) by Ghosh (1983). Subsequently, Frans Velthuis
used METAFONT to create a font Devanag (Pandey, 1998) and Charles
Wikner employed the software in creating his Sanskrit Devan¯agar¯ı font
(Wikner, 2002).
Douglas Hofstadter in his ingenious 1982 reply to Knuth argues that
semantic categories (such as the character ⟨A⟩) are productive sets (Hofs-
tadter, 1985, 263). That is, no ﬁnite parameterization is capable of spec-
ifying all the ways in which a particular character may be graphically
realized. Hofstadter understands characters as belonging to a structural
system (such as the system of Latin letters) that employs a set of contrasts
(thus ⟨p⟩and ⟨b⟩differ in the relative position of their “post” and “bowl”)
(Hofstadter, 1985, 280). Although Hofstadter rejects analysis of letter-
forms into geometric parts, he allows instead for conceptual roles (such
as “crossbar”, “bowl”, “post”, “tail”) that may be variously realized by
particular glyphs. Glyphs are accepted as characters to the degree that
they are successful in fulﬁlling a set of roles. Hofstadter’s approach re-
sembles in certain respects prototype theories (Reed, 1978, 153–158).
One potential use of featural analysis is to investigate the history of
writing systems. Coding a set of palaeographic characters by means of
feature vectors might serve as a preliminary to studies employing the
methods of phylogenetic systematics (cladistics) (Skelton, 2008). From
the feature vectors, characters for producing a data matrix of the sort
that is used in phylogenetic analysis might be extracted. Phylogenetic
analysis uses algorithms or optimality criteria to compute an evolutionary
tree that describes the relations between taxa. Such categories as scribal
hands, documents, or ﬁnd sites might be chosen as appropriate taxa.
Featural analysis also can model character confusion, as in palaeo-
graphic situations when a scribe mistakes one character for a visually
similar one. Feature systems can be used to predict the likelihood of
particular confusions. By combining a set of graphic features with an
edit function such as stepped distance function (SDF), it is possible to
108
CHAPTER 7. SCRIPT-BASED ENCODING
compute the orthographic similarity between two strings (Singh, 2006).
Because the orthographic syllable is such a salient unit in Indic scripts,
analysis of this type has many potential applications in manuscript stud-
ies and textual criticism.
7.2
Analysis of Devan¯agar¯ı script
We have surveyed a number of attempts to analyze writing at the sub-
graphemic level. As we move from typographers to psychologists, new
media designers, lexicographers, OCR implementors, and cognitive sci-
entists, we see, with shifting goals, shifting levels of analysis. There is no
real consensus on what meaningful distinctions to draw below the level
of the grapheme. This situation is in contrast to that obtaining in phonol-
ogy, where — although there is disagreement about particular features
and about issues such as whether articulatory or acoustic features are
more relevant; or whether n-ary, and not just binary, features should be
adopted — there is a consensus that speech sounds can be understood in
terms of sets of distinctive features (Jakobson et al., 1963; Chomsky &
Halle, 1968; Ladefoged, 1971; Halle, 1983; Clements, 1985; Clements
& Hume, 1995).
Although in most writing systems there is normally no correlation
between graphic and phonetic features, we do occasionally ﬁnd such a
correlation. ⟨p⟩and ⟨b⟩differ in only one visual feature, while /p/ and /b/
differ only in the feature [± voice]. Similarly, ⟨b⟩and ⟨d⟩differ only in
one visual feature, while /b/ and /d/ differ only in place of articulation.
Such distinctions appear to emerge synchronically in a process of “re-
signiﬁcation”. The parallelisms do not hold for letterforms such as {⟨B⟩,
⟨D⟩, ⟨P⟩} (from which the lower-case forms developed) or a fortiori {⟨B⟩,
⟨D⟩, ⟨P⟩} or {⟨B⟩, ⟨∆⟩, ⟨Π⟩}.
Historically, we know or suspect that certain characters were derived
from others. Thus in Br¯ahm¯ı, characters for aspirated stops are derived
from characters for unaspirated stops (Dani, 1963). Sometimes the char-
acter for the aspirated stop is formed by completing part of the shape of
the character for the homorganic unaspirated stop, as in
⟨cha⟩<
⟨ca⟩
and
⟨t.ha⟩<
⟨t.a⟩. In other cases an extra “curlicue” is added, as in
⟨d.ha⟩<
⟨d.a⟩and
⟨pha⟩<
⟨pa⟩. The derivational relationship may
still be evident in Devan¯agar¯ı, where ⟨:pa⟩and ⟨:P⟩represent /p/ and /ph/
7.3. COMPONENT ANALYSES OF DEVAN ¯AGAR¯I SCRIPT
109
respectively, which differ only in [± aspirated]; ⟨ba⟩and ⟨va⟩represent /b/
and /w/, which are both non-syllabic voiced segments with labial articu-
lation;10 and ⟨Ba⟩and ⟨ma⟩represent /bh/ and /m/, which differ only in the
values of [± aspirated, ± nasal]. Moreover, the four retroﬂex non-nasal
stop characters ⟨f⟩, ⟨F⟩, ⟨.q⟩, and ⟨Q⟩all share the graphic feature of a
round bottom. Graphic similarity, however, is by no means always corre-
lated with phonetic similarity, and Devan¯agar¯ı has several close graphical
pairs corresponding to sounds that are not especially similar, such as ya
⟨ya⟩and Ta ⟨tha⟩, :pa ⟨pa⟩and :Sa ⟨´sa⟩, Ba ⟨bha⟩and ½ ⟨jha⟩.
7.3
Component analyses of Devan¯agar¯ı script
In A Grammar of the Sanskr˘ıta Language (1808) Charles Wilkins in-
cluded an engraved plate entitled “The Elements of the Devanagari Char-
acter”. The plate presents the strokes and combinations of strokes used
to build up characters ordered according to the traditional varn. am¯al¯a se-
quence. Strokes or combinations that have been previously introduced
are not repeated. In this scheme the Devan¯agar¯ı characters are reduced
to 55 “elements”, ranging in complexity from a vertical bar to the entire
character  (save the ´sirorekh¯a). The analysis is clearly based on cal-
ligraphic technique, and the aim is pedagogical. There is no attempt to
reduce shared stroke combinations rigorously to a minimal set of com-
ponent strokes.11
A more rigorous approach is adopted in the linguistic survey of Iva-
nov & Toporov (1968). A set of 21 binary distinctive features, each
corresponding to a graphic component, is posited for the graphemes of
Devan¯agar¯ı (see TABLE 13). The authors note that the scheme is provi-
sional, and no empirical evaluation of the feature set is attempted. They
observe moreover that certain features are always expressed, whereas
10In some ancient dialects /w/ was realized as labiodental /V/ (P¯an. in¯ıya´siks. ¯a 18), and
in modern pronunciations it is sometimes realized as a bilabial fricative [B] (a sound that
differs from [b] only in the feature [± continuant]).
11Hock (n.d.) presents an analysis along similar lines, also intended for pedagogical
application. Character components fall into four groups: (a) straight lines (5), (b) circles
and curlicues (7), (c) dots (2), (d) other shapes (24). Several components are given in
variant forms. We thank Hans Hock for sharing these materials with us.
110
CHAPTER 7. SCRIPT-BASED ENCODING
others are neutralized in the allograph demanded by a particular graphic
context.
At the Indian National Centre for Software Technology (NCST) in
the mid 1980s, R. K. Joshi identiﬁed a basic set of 55 graphic primitives
that could be combined to create the skeletons of basic Devan¯agar¯ı char-
acters. His analysis was used in the context of Vinyas, a digital type
design system collaboratively created at NCST (Parida, 1993). Primi-
tives include horizontal lines (2), vertical lines (2), diagonal lines (4),
circles of different sizes (4), quarter circumferences (9), half circumfer-
ences (11), various additional curves (22), and a dot (FIGURE 7.1).12
Joshi noted that the basic set of primitives could be considerably reduced
by applying command tags to primitives when selecting them for char-
acter construction. Such command tags include extend, extract, mirror
x/y axis, repeat, condense, ﬂip, and rotate. Joshi also noted that his com-
ponent analysis has a predecessor in the standard orthographic pedagogy
introduced in primary education under British rule in the late nineteenth
century. An attempt was made to provide a series of primitive elements
of Devan¯agar¯ı script for students to copy and then combine following
similar pedagogical techniques used for Roman script.
Also in the 1980s Pijush K. Ghosh, in designing his NCSD font (cf.
p. 107, above), undertook a “Stroke Analysis and Synthesis” of Devan¯a-
gar¯ı, in which primitives were identiﬁed and rules for composing com-
plete characters from the primitives were speciﬁed. Ghosh suggested
that such a method might lead in the future to “Syntactic Letter Form
Generation”, in which glyph shapes could be speciﬁed using a context-
free grammar (Ghosh, 1983, 47).13 Ghosh identiﬁed a Pattern Primitive
Set (PPS) with 48 elements. His aims were to identify primitives that
were simple enough to be concatenated algorithmically and to minimize
the size of the PPS. Despite the systematic aspect of such an approach,
Ghosh acknowledged that the selection of any such set must involve sub-
jective factors.
12The late R. K. Joshi kindly granted us permission to reproduce this drawing.
13Cf. Narasimhan & Reddy (1967).
7.3. COMPONENT ANALYSES OF DEVAN ¯AGAR¯I SCRIPT
111
FIGURE 7.1: Devan¯agar¯ı atoms, as drawn by R. K. Joshi, 1984.
112
CHAPTER 7. SCRIPT-BASED ENCODING
Chapter 8
Conclusions
Although computers manipulate linguistic and textual data in sophisti-
cated ways, current encoding systems reﬂect orthographic design fac-
tors to the exclusion of more relevant information-processing principles.
Even the most recent standardized encoding systems reproduce deﬁcien-
cies inherent in the traditional orthographies themselves. These tradi-
tional orthographies have undergone a long history of adaptation in tech-
nologies for the visual representation of language. Beginning with styli,
brushes, etc., and continuing with the invention of movable type, ma-
chine typesetting, the typewriter, remote transmission by means of tele-
type machines, the invention of standardized computer encodings from
ASCII to Unicode, right up to the desktop publishing revolution, each
stage in technological development represents language visually. Yet
display is only one of numerous functions that computers now perform.
Computers exchange textual data over space and time and perform lin-
guistic processing, such as spell-checking, machine translation, content
analysis and indexing, and morphological and syntactic analysis. There-
fore display for a human reader should no longer be considered the pri-
mary determinant of an encoding scheme. Rather, language should be
encoded in such a way as to facilitate automatic processing, to minimize
extrinsic ambiguity and redundancy, and to ensure longevity. To avoid
ambiguity and redundancy requires that an encoding system be charac-
terized by a one-to-one correspondence between characters and items to
113
114
CHAPTER 8. CONCLUSIONS
be encoded, and that all encoded items be of the same kind.
Text-processing technology arose in the English-speaking world and
assumed as a norm the use of the Roman alphabet with few or no di-
acritics. Adaptation to some non-European scripts required consider-
able effort and compromise. The adaptation of Roman script itself re-
quired the use of a number of diacritics to represent the phonology of
non-European languages accurately. The greatest challenge remains the
application of encoding principles to the representation of non-European
languages. Sanskrit, the primary culture-bearing language of India, with
its enormous body of literature, strong oral tradition, and highly devel-
oped linguistics presents a particularly appropriate case for study.
The encoding schemes used for Sanskrit are based primarily either
upon Devan¯agar¯ı script or upon the standard Romanization of Sanskrit.
The difﬁculties with these schemes are due in part to problems in the
modes of graphic representation of Sanskrit sounds adopted in the scripts
themselves. Both depart from one-to-one correspondence between char-
acters and items to be encoded and from consistency in the type of en-
coded item. Devan¯agar¯ı employs redundancy in the representation of
phrase-initial and post-vocalic vowels, and an inversion in the graphic
representation of phonetic elements in its representation of /a/. Roman-
ization employs digraphs for the representation of aspirate stops and open
diphthongs. Both employ digraphs for the representation of the aspirated
retroﬂex lateral ﬂap / h/. The duplicate use of a sign used to represent an
aspirate segment additionally to represent the feature of aspiration, and
the use in Romanization of a, i, and u to represent phonetic segments
as well as subsegments of diphthongs, garners inconsistency in the type
of item represented and therefore introduces ambiguity. Or, if it avoids
ambiguity by using the diaeresis over the second of two vowels, Roman-
ization still suffers from redundancy in the representation of the vowels i
and u. Encoding standards for Sanskrit that are based on Devan¯agar¯ı or
Romanization inherit the deﬁciencies inherent in the underlying scripts.
They suffer from ambiguity and redundancy by departing from a one-to-
one correspondence and by inconsistency in the basis for encoding.
Clear principles of encoding require determining the location of the
encoding in the space deﬁned by three axes: graphic–phonetic, syn-
thetic–analytic, and contrastive–non-contrastive. One must determine
whether to encode written characters or speech sounds, segments or fea-
CONCLUSIONS
115
tures, and what criteria to use to contrast items. Since information degra-
dation arises at each stage in representation of knowledge, it is felicitous
to encode the primary medium of knowledge transmission. Given that
script is inherently a secondary phenomenon vis-à-vis spoken language,
encoding should be based directly on spoken language. Devan¯agar¯ı script
itself was not speciﬁcally designed to represent Sanskrit phonology, but
rather was adapted to this use subsequently; hence it is not surprising
that it proves to be a less appropriate basis for encoding Sanskrit than
Sanskrit phonology itself.
Few of the world’s writing systems were designed for the languages
that they represent in extant texts. Most were adapted, and adaptations
almost always fail to capture the structure of the spoken language ade-
quately. Therefore, in general, where one has access to the phonology of
the language, where the orthography is fairly shallow, and where the stan-
dard orthography departs from an ideal coding of spoken language struc-
ture, the basis for text encoding should be phonetic rather than graphic.
Sanskrit meets these conditions, and so it is better to encode Sanskrit
speech sounds directly than to encode the secondary representations of
those sounds in Devan¯agar¯ı, Roman, or any other script. Directly coding
Sanskrit speech sounds will solve the problems of ambiguity and redun-
dancy that we have noted in our survey of current encoding schemes.
Spoken language has a temporal dimension, and scripts that repre-
sent spoken language have a linear dimension that corresponds to the
temporal dimension of spoken language. The minimal independent unit
in the chain of speech is the phonetic segment or phone. The minimal
independent unit in script is the graphic segment or graph. A segmental
linguistic encoding is based upon minimal phonetic or graphic segments.
Yet both phonetic and graphic units may be decomposed into systems
of features orthogonal to this dimension of segmentation and not nec-
essarily coterminous with the minimal units of segmentation. Phonetic
units may be decomposed into a set of acoustic or articulatory features
that are realized simultaneously. Similarly, writing may be analyzed into
graphic features. Although the boundaries between phonetic and graphic
segments are sites of marked alterations in phonetic and graphic fea-
tures, each feature may independently be associated with a string of one
or more phonetic or graphic segments. Encodings may be entirely seg-
mental, at one pole of the synthetic–analytic axis, or entirely featural at
116
CHAPTER 8. CONCLUSIONS
the other. For Sanskrit, we have devised an entirely segmental phonetic
encoding (SLP2) (see Appendix C), an encoding based entirely on artic-
ulatory features (SLP3) (see Appendix D), and a phonetic encoding that
utilizes both segmental and featural units, while remaining clear about
which is which (SLP1) (See Appendix B. The features in SLP1 are indi-
cated by modiﬁers described in section B.3).
All modes of information storage and transmission presuppose a se-
lection of relevant information. The selection of the set of distinctions
to be encoded depends upon the nature of the textual corpus and the in-
formation of interest to its users. Encoding requires classifying items,
identifying items within each class by ignoring irrelevant distinguishing
information, and designating each class by unique identiﬁers. A linguis-
tic transcription of speech ignores non-linguistic information such as ab-
solute tempo and pitch; a linguistic copy of a manuscript ignores absolute
line thickness and character height. An encoding assigns codepoints to
units that have signiﬁcant contrasts. Yet a segmental phonetic encoding
of a corpus of Sanskrit texts for a general scholarly community cannot
limit itself to the narrow concept of a phoneme as the distinctive segment
to be encoded, even with its recent extension to include distinctions in
duration, stress, and pitch. Typically, phonemes are the minimally con-
trastive segments of sound in a language, on the basis of the contrast
between which lexical and grammatical distinctions can be made. But
a comprehensive phonological system of the language should be able
to convey whatever information speech conveys. Contrastive and com-
plementary distribution is always with respect to a speciﬁc context. If
one stretches two parameters in the typical deﬁnition of a phoneme, the
modiﬁed concept may serve as a suitable basis for a phonetic encoding:
(1) The language must collapse within its bounds diachronic differentia-
tion, regional dialects, and stylistic strata. (2) The range of the semantic
content that contrastive sounds are required to differentiate must include
paralinguistic semantics.
It is necessary to broaden the concept of a phoneme to comprise lin-
guistic variation, borrowing, and paralinguistic semantics. A phoneme in
such a comprehensive phonological system remains the minimally con-
trastive phonetic segment in a language on the basis of which one word
could be distinguished from another. It differs, however, from the strict
deﬁnition by relaxing its limiting parameters. A language then refers to a
8.1. DYNAMIC TRANSCODING
117
speciﬁed range of dialects, including borrowings. And for sounds in par-
allel distribution to be contrastive, they serve to differentiate a speciﬁed
range of semantic content, including paralinguistic content. We have em-
ployed the broader conception of a phoneme to classify Sanskrit sounds
as distinctive in our phonetic encodings. We utilize the SLP1 encoding
for the storage of a corpus of Sanskrit texts in our digital Sanskrit library
and for linguistic processing. We transcode to a variety of Indic scripts
and Romanization in Unicode for display purposes and employ various
meta-transliterations, Indic Unicode, as well as clickable input keyboards
for data input.
8.1
Dynamic transcoding
By storing text in a single underlying format that maximizes ﬁdelity to
the phonetic representation of the spoken language, we allow for extreme
ﬂexibility in display and input options. Text stored in a single underly-
ing representation may easily be displayed in Devan¯agar¯ı, Roman trans-
literation, phonetic transcription (e. g., that of the IPA), or one of the
regional scripts of India. Likewise, text entered and viewed in Roman
transliteration or one of the Indic scripts may be transcoded and pro-
cessed in the underlying phonetic format. Rules for translating the under-
lying format to one of the surface representations (typically encoded as
Unicode) can be implemented with ﬁnite state transducers (Huet, 2005).
We have developed a number of model transcoders using lex (Kernighan
& Pike, 1984) and similar scanner generators (which generate determin-
istic ﬁnite automata). Philosophically, such an approach is satisfying,
since it conceives of written Sanskrit as a rule-based transformation from
an underlying level that corresponds in some sense to speech. Practically,
it is very useful to be able to display the same stretch of Sanskrit text in
multiple ways; this possibility allows one to reach multiple audiences,
including beginning students (who cannot yet read an Indic script), and
Indian scholars, whether pandits or amateurs, who are used to using an
Indic script other than Devan¯agar¯ı.
The Sanskrit Library has deployed a full set of transcoding routines
written in Java that allow Sanskrit text encoded in SLP1 to be displayed
in most major Indic scripts (Bengali, Devanagari, Gujarati, Gurmukhi,
Kannada, Malayalam, Oriya, or Telugu), standard Romanization, or any
118
CHAPTER 8. CONCLUSIONS
of several popular encodings (Kyoto-Harvard, wx, ITRANS, etc.), de-
pending upon user preference. Data-entry, and the display of entered
text, is likewise available in numerous formats based upon user prefer-
ence. Clickable input keyboards provide data-entry for those unfamiliar
with any of the available encodings. A transcoding page also allows
users to enter short passages or upload ﬁles for transcoding. Although
pre-existing encodings generally capture less information than ours, the
Sanskrit Library has developed automatic and machine-assisted facilities
for conversion of prior and legacy data into the Sanskrit Library Phonetic
encodings.
It would also be easy to develop additional input modes that can
be used with the encoding schemes. These input modes could be cus-
tomized for the needs of different users: e.g., Western scholars used to
dealing with Sanskrit in Romanization, Indians accustomed to differing
regional keyboard layouts, and scholars accustomed to legacy schemes.1
Suitable input methods can also be developed for devices with alterna-
tive input hardware, such as pen computers, PDAs, and mobile phones
(Shanbhag, Rao & Joshi 2002; Gupta 2006).2 In cases where input meth-
ods are being developed for users who are not already accustomed to
existing methods, attention should be paid to ergonomic factors such as
ﬁnger travel, error rate, typing speed, cognitive load, and learning curve.
8.2
Text-to-speech and speech-recognition
The discussion of transcoding between data-input, linguistic processing,
and display formats in the context of phonetics raises questions concern-
ing text-to-speech software and phonetic input methods. Text-to-speech
software and phonetic input methods are designed on the basis of the
sound structure of language, rather than on the traditional visual presen-
tation of language. The phonetic encodings described here, particularly
the featural encoding (SLP3), may serve as a starting point for develope-
1QWERTY keyboards are not well-adapted to Indic script typing, especially for Indian
users who are not familiar with English and English keyboard layouts. New hardware
addresses these challenges (Joshi et al., 2004).
2As of March 2010, India had about 545 million mobile phone users. Source: <https:
//www.cia.gov/library/publications/the-world-factbook/geos/in.html>.
8.3. HIGHER-LEVEL ENCODING
119
ment of a correlation between acoustic parameters and encoded units and
thereby set the foundation for this promising area of research.
8.3
Higher-level encoding
The present book has focused on issues of character-encoding with par-
ticular reference to Sanskrit. Yet accurate and comprehensive character-
encoding merely lays the foundation for digital linguistic and philolog-
ical research. Once the machine-readable text is available in a consis-
tent form, it is possible to encode linguistic and literary information of
the language and the text. Linguistic encoding captures morphological,
syntactic, and semantic information in the language. Literary encoding
captures textual metadata and facets of artistic appreciation such a poetic
ﬁgures and sentiments.
Formal and computational linguistics was dominated by English at its
inception and developed in subsequent decades primarily in the environ-
ment of European languages. More recently there has been a concerted
effort to undertake formal linguistic analysis of a wide variety of lan-
guages, with particular interest in those with dramatically different fea-
tures, and to enrich linguistic theory to account for linguistic variety. In
spite of this effort, analytic structures and procedures utilized in formal
linguistics remain dominated by those invented for, and most suitable
for, English and other European languages. Linguistic theory remains
unduly weighted in favor of European languages even as their exten-
sion to the variety of the world’s languages involves undue complication
thereby revealing their inadequacy in representing language universally.
It would prove particularly useful in developing universally adequate lin-
guistic theory to investigate sophisticated linguistic theories, structures,
and procedures developed to describe languages of a very different char-
acter from English.
India developed an extraordinarily rich linguistic tradition over more
than three millennia that remains under-appreciated and under-investigat-
ed. A cursory glance at the long tradition of discussion and argumen-
tation within and between Indian sciences of phonetics (´siks. ¯a), gram-
mar (vy¯akaran. a), logic (ny¯aya), ritual exegesis (karmam¯ım¯a ˙ms¯a), and
literary theory (ala˙nk¯ara´s¯astra) reveals that Indian linguistic traditions
have much to offer contemporary linguistic theory in the areas of pho-
120
CHAPTER 8. CONCLUSIONS
netics, morphology, syntax, and semantics. The current book drew heav-
ily from the ﬁrst. The tradition of grammar (vy¯akaran. a) offers interest-
ing modes of morphological and syntactic analysis that may prove to be
more suitable to highly-inﬂected free-word-order languages than meth-
ods employed in contemporary computational frameworks. The tradi-
tions of grammar, logic (ny¯aya), ritual exegesis (karmam¯ım¯a ˙ms¯a), and
literary theory (ala˙nk¯ara´s¯astra) offer various competing intricate theo-
ries of verbal comprehension. These Indian linguistic traditions might
contribute useful insights to contemporary formal linguistics.
Indian linguistic theories can be formalized and implemented compu-
tationally. Research to work out the details of Indian semantic and syn-
tactic theory could contribute to contemporary research at the semantics-
syntax interface where computational linguistic work is ﬂourishing. The
authors’ current work draws upon major semantic and syntactic trea-
tises in the Indian grammatical tradition and contemporary techniques
of formalization and computational implementation to bring ancient In-
dian theories face to face with contemporary computational linguistic
work. On the one hand, we articulate Indian theories in contemporary
terms and offer a critique and insights useful to contemporary linguists.
On the other hand, we suggest ways of modeling ancient Indian theo-
ries computationally. The latter will allow computational modeling to
clarify those ancient theories and assist in answering difﬁcult questions
regarding their principles and historicity. Implementing Indian theories
of morphology, syntax, and semantics computationally requires working
out methods to encode the categories and distinctions articulated in these
theories. Research that compares the Indian theories with contemporary
theories requires correlating the encodings of Indian linguistic categories
with traditional European categories. We hope to develop these higher-
level linguistic encoding schemes and to utilize them in the creation of
tagged corpora for linguistic research.
XML has emerged as the standard method of implementing higher-
level encoding in digital texts. The Text-Encoding Initiative (TEI) has de-
veloped standards for encoding metadata of digital texts in XML, and for
encoding various literary aspects of texts. Investigation of the categories
and distinctions of sentiments (rasa) and literary ﬁgures (ala˙nk¯ara) in the
Indian traditions of literary criticism and artistic appreciation (ala˙nk¯ara-
´s¯astra, n¯at.ya´s¯astra) remains a fruitful ﬁeld for future research.
Appendices
121
122
APPENDICES
Appendix A
Tables
123
124
APPENDICES
A.1
Phonetic features
TABLE 1 shows the structure of phonetic features that serve to character-
ize and contrast the phonetic segments of Sanskrit. The authors selected
the phonetic features shown after examining the sets of features described
in ancient Indian phonetic treatises including those of ¯Api´sali, ´Saunaka,
and others. These features include both place of articulation and stricture
features as well as length and pitch, which have often been excluded from
the discussion of features. Place of articulation features do not include
nasal, although both ¯Api´sali and ´Saunaka include this feature. On the
other hand, stricture features include some of the ﬁner distinctions de-
scribed by ¯Api´sali. Recent universal linguistic featural systems devised
by Halle and Clements, utilize articulatory and stricture features as their
primary elements respectively.
APPENDIX A: TABLES
125
TABLE 1: Phonetic features
I. place of articulation
A. guttural
B. velar
C. palatal
D. retroﬂex
E. dental
F. labial
II. manner of articulation (stricture)
A. contacted
B. slightly contacted
C. slightly open
D. open
1. simply open
(sa ˙mpras¯aran. a)
2. more open (gun. a)
3. most open (vr
˚
ddhi)
III. voicing [±]
IV. aspiration [±]
V. nasalization [±]
VI. length
A. half
B. short
C. slightly long
D. long
E. protracted 3
F. protracted 4+
VII. underlying pitch
A. none
B. high
C. low
D. circumﬂex
VIII. surface tone
A. extra low
B. low
C. high
D. extra high
126
APPENDICES
A.2
Sounds categorized by ¯Api´sali
TABLE 2 shows the structure of phonetic features described by the an-
cient Indian phonetician ¯Api´sali. Most conspicuously, ¯Api´sali explicitly
describes the active articulators of sounds (II), anticipating the approach
adopted by the contemporary phonologist Morris Halle.
¯Api´sali char-
acterizes nasals by including a nasal place of articulation ([I]G) and in-
cludes a full set of stricture distinctions including ﬁve degrees of open-
ness ([III]A4). The extrabuccal features that are associated with the glot-
tis ([III]B1) imply particular features of the larynx ([III]B2), which in
turn imply voice features ([III]B3). Implications are represented by right
arrows (→). To the right of each feature in parentheses are shown the
phonetic segments to which the feature belongs. ¯Api´sali attributes the
feature dorsolingual only to the jihv¯am¯ul¯ıya ([I]B), while ´Saunaka asso-
ciates it with several sounds (TABLE 3 [I]B).
Notes:
1. ˙nñn. nm have a secondary place of articulation in the nose.
2. eai gutturo-palatal.
3. oau gutturo-labial.
4. v dento-labial.
5. ˘e ˘o in S¯atyamugri and R¯an. ¯ayan¯ıya S¯amaveda ( ¯A´S. 6.9).
6. ¯l
˚
in imitation of proper names ( ¯A´S. 6.6).
APPENDIX A: TABLES
127
TABLE 2: Sounds categorized according to phonetic features by ¯Api´sali
I. place of articulation
A. guttural (akkhggh ˙n1 hh. eai2
oau3 )
B. dorsolingual (h¯)
C. palatal (icchjjhñ1 y´seai2)
D. coronal (r
˚
t. t.hd. d. hn.
1 rs.)
E. dental (l
˚
tthddhn1 lsv4)
F. labial (upphbbhm1 h
ˇ
v4 oau3)
G. nasal ( ˙m ˜k ˜kh ˜g ˜gh ˙nñn. nm)
II. articulator
A. tongue
1. root (dorsolingual)
2. middle (palatal)
3. undertip (coronal)
4. tip (dental)
B. throat (guttural)
C. lips (labial)
D. nose (nasal)
III. manner of articulation
A. buccal: stricture
1. contacted (stops, yamas)
2. slightly contacted (yrlv)
3. slightly open (´ss. sh. h¯ h
ˇ
h ˙m)
4. open (vowels)
a. simply open (iur
˚
l
˚
)
b. more open (eo)
c. even more open (aiau)
d. most open (¯a)
e. close (a)
B. extrabuccal (1 →2 →3)
1. glottis
a. spread (→2a, 8b) (low
pitched vowels, kct. tp
khcht.hthph´ss. sh. h¯ h
ˇ
˜k
˜kh)
b. constricted (→2b, 8a)
(high-pitched vowels,
gjd. dbghjhd. hdhbhyr
lvh ˙m ˜g ˜gh)
2. larynx
a. breath (→3−) (= 1a)
b. sound (→3+) (= 1b)
3. voice [+/−] (= 1b) /
(= 1a)
4. aspiration [+/−] (khcht.h
thph´ss. sh. h¯ h
ˇ
˜khghjhd. hdh
bhh ˙m ˜gh) / (kct. tp ˜kgjd. d
byrlv ˜g ˙nñn. nm)
5. nasalization [+/−] (˙nñn. n
mã˜ı ˜u˜r
˚
˜l
˚
˜ea˜ıõa˜u ˜y˜l ˜v /
(others)
6. breath impact
a. iron (stops, yamas)
b. wood (semivowels)
c. wool (spirants, vowels)
7. length
a. short (aiur
˚
l
˚
˘e ˘o5)
b. long (¯a¯ı ¯u¯r
˚
¯l
˚
6 eaioau)
c. protracted
8. relative pitch (vowels)
a. high
b. low
c. circumﬂex (→8a, 8b)
128
APPENDICES
A.3
Sounds categorized by ´Saunaka
TABLE 3 Shows the structure of phonetic features described by ´Saunaka.
Most conspicuous is ´Saunaka’s inclusion of an intermediate feature of
glottal aperture ([III]C), only recently recognized as accurate by modern
phoneticians, and his discussion of the material of sounds (V), which the
three dispositions of glottal aperture imply (as indicated by the arrow).
Also signiﬁcant is ´Saunaka’s recognition of the implication of vocal fold
disposition (IV) on pitch ([VI]E). Like ¯Api´sali (see TABLE 2), ´Saunaka
utilizes a full set of places of articulation including a nasal place of articu-
lation ([I]G). In contrast to ¯Api´sali’s full set of stricture features ([III]A),
he includes only three manners of articulation (II).
APPENDIX A: TABLES
129
TABLE 3: Sounds categorized according to phonetic features by ´Saunaka
I. place of articulation
A. guttural (ahh. )
B. dorso-lingual (r
˚
l
˚
kkhggh ˙nh¯)
C. palatal (ieaicchjjhñy´s)
D. coronal (t. t.hd. d. hn. s.)
E. dental (tthddhnrls)
F. labial (uoaupphbbhmvh
ˇ
)
G. nasal ( ˙m ˜k ˜kh ˜g ˜gh ˜h)
II. manner of articulation
A. non-continuously contacted
(stops, yamas)
B. slightly contacted (yrlv)
C. continuously open (vowels, h
´ss. sh. h¯ h
ˇ ˙m)
III. glottal aperture
A. open (→V[A])
B. closed (→V[B])
C. between (→V[C])
IV. disposition of vocal folds
A. stretching (→VI[E1])
B. slack (→VI[E2])
C. tossing (¯ak˙sepa) (→VI[E3])
V. material
A. breath (unvoiced segments: k
ct. tpkhcht.hthph ˜k ˜kh´ss. sh. h¯ h
ˇ
˙m)
B. sound (voiced unaspirated
segments: gjd. db ˜g ˙nñn. nmyr
lv; vowels)
C. both (voiced aspirates and
spirant: ghjhd. hdhbh ˜ghh)
VI. other features
A. voice [+/−] (gjd. db ˜g ˙nñn. nm
yrlvghjhd. hdhbh ˜ghh) / kct. t
pkhcht.hthph ˜k ˜kh´ss. sh. h¯ h
ˇ ˙m
B. aspiration [+/−] (khcht.hthph
˜kh´ss. sh. h¯ h
ˇ ˙mghjhd. hdhbh ˜gh
h) / (kct. tp ˜kgjd. dbyrlv ˜g ˙nñn.
nm)
C. nasalization [+/−] (˙nñn. nmã˜ı
˜u˜r
˚
˜l
˚
˜ea˜ıõa˜u ˜y ˜v˜l) / (others)
D. length in moras
1.
1
4 (short svarabhakti)
2.
1
2 (consonants, ˙m, long
svarabhakti)
3. 1 (aiur
˚
l
˚
’)
4. 2 (¯a¯ı ¯u¯r
˚
¯l
˚
eaioau)
5. 3 (protracted vowels)
E. relative pitch (vowels)
1. high
2. low
3. circumﬂex
130
APPENDICES
A.4
Sounds categorized after Halle et al.
TABLE 4 shows the Sanskrit sounds categorized according to the artic-
ulatory feature geometry described recently by Halle et al. (2000). Ar-
ticulators and features are reorganized in the order generally presented
by Indian phonetic treatises: articulators from back to front followed by
articulator-free features. The higher nodes Place and Guttural, and the
root node are ignored.
APPENDIX A: TABLES
131
TABLE 4: Sounds categorized using phonetic features of Halle et al.
I. articulators
A. Larynx (Glottis)
1. [glottal] (hh. )
2. [constricted glottis] (not
used)
3. [spread glottis] (aspirates:
khghchjht.hd. hthdhphbh;
spirants: ´ss. s h h. h¯ h
ˇ ˙m)
4. [stiff vocal folds]
(high-pitched and
circumﬂexed vowels;
unvoiced consonants: kkh
ccht. t.htthpph´ss. sh. h¯ h
ˇ
)
5. [slack vocal folds]
(low-pitched and
circumﬂexed vowels;
voiced consonants: gghj
jhd. d. hddhbbh ˙nñn. nmh ˙m
l. l.hl˜l ry ˜yv ˜v)
B. Tongue Root (not used)
1. [radical]
2. [retracted tongue root]
3. [advanced tongue root]
C. Soft Palate
1. [rhinal] (anusv¯ara, yamas,
n¯asikya: ˙m ˜k ˜kh ˜g ˜gh ˜h)
2. [nasal] (anusv¯ara, yamas,
n¯asikya: ˙m ˜k ˜kh ˜g ˜gh ˜h;
nasal stop, vowels,
semivowels: ˙nñn. nmã˜ı ˜u˜r
˚
˜l
˚
˜ea˜ıõa˜u ˜y ˜v˜l)
D. Tongue Body
1. [dorsal] (kkhggh ˙nh¯;
vowels: aiueoaiau)
2. [back] (auo)
3. [high] (iu)
4. [low] (a)
E. Tongue Blade
1. [coronal] (cchjjhñt. t.hd. l.
d. hl.hn. tthddhnrl˜ly ˜y´ss. s)
2. [+ anterior] (tthddhnl˜ls)
3. [−anterior]
a. [+ distributed] (cchjjh
ñy ˜y´s)
b. [−distributed] (t. t.hd. l.
d. hl.hn. rs.)
F. Lips
1. [labial] (uoaupphbbhmv
˜vh
ˇ
)
2. [rounded] (uoauv ˜v)
II. articulator-free features
A. [+ consonantal] (cavity)
1. [+ sonorant] (no pressure)
a. [+ lateral] (lateral
resonants: l. l.hl˜l)
b. [−lateral] (nasal stops:
˙nñn. nm; approximant:
r)
2. [−sonorant] (pressure)
a. [+ continuant]
(spirants: h¯ ´ss. sh
ˇ
)
b. [−continuant]
(non-nasal stops)
3. [suction] (not used)
4. [strident] (not used)
B. [−consonantal] (no cavity)
(glides: y ˜yv ˜v; vowels; hh. ˙m)
132
APPENDICES
A.5
Sanskrit phonetics
TABLE 5 shows Sanskrit phonetic segments categorized according to the
features in TABLE 1. Place of articulation features appear in the leftmost
column. Stricture appears in the third row of headings with subcate-
gories of vowel stricture in the fourth row. The subcategories of vowel
stricture serve to distinguish vowel grades termed sampras¯aran. a, gun. a,
and vr
˚
ddhi in P¯an.inian grammar. The ﬁfth row of headings shows voic-
ing; while the sixth row shows aspiration and nasalization of consonants,
as well as length of vowels. Pitch is not shown. Less common segments
are discussed in the notes.2−3,6−8 Unusual is the placement of h with
semivowels,4 and the placement of anusv¯ara with the velars.5
Notes:
1. The diphthongs ai and au have, and the monophthongs e and o are
considered to have, two places of pronunciation: (i) the glottis, (ii)
the palate or lips.
2. Vowels include prolonged lengths called pluta; three pitches ud¯atta,
anud¯atta, svarita; and nasalized variants.
3. Semivowels y, l, v include nasal variants ˜y, ˜l, ˜v.
4. Short vowels ˘e and ˘o occur in Vedic recitation and in phonetic trea-
tises.
5. Slightly lengthened short vowels occur in certain traditions of the
recitation of the V¯ajasaneyisa ˙mhit¯a.
6. With partial stricture and voicing, h shares features with buccal semi-
vowels.
7. Anusv¯ara is a nasal glide with the velum as its primary articulator.
8. Unaspirated and aspirated retroﬂex lateral ﬂaps written L, l. and \h, l.h
occur intervocalically in R
˚
gvedic dialect (and in the Nirukta), instead
of d. and d. h.
APPENDIX A: TABLES
133
TABLE 5: Sanskrit phonetics
CONSONANTS
VOWELS1,2
stops
semivowels3
spirants
contacted
slightly cont. slightly open open
simply open
more open
most open
UNVOICED
VOICED
VOICED
UNVOICED
VOICED
VOICED
VOICED
unasp. asp.
unasp. asp.
nasal
short4,5 long short long
long
GUTTURAL
h, h6
H h.
A a
A;a ¯a
VELAR
k, k
K,a kh
g,a g
;G,a gh
.z, ˙n
M ˙m7
^ h¯
PALATAL
.c,a c
C, ch
.j,a j
J,a jh
V,a ñ
y,a y
Z,a ´s
I i
IR ¯ı
O; e
Oe; ai
RETROFLEX8
f, t.
F, t.h
.q, d.
Q, d. h
:N,a n.
.=, r
:S,a s.
 r
˚
 ¯r
˚
DENTAL
t,a t
T,a th
d, d
;D,a dh
n,a n
l, l
.s,a s
 l
˚
 ¯l
˚
LABIAL
:p,a p
:P, ph
b,a b
B,a bh m,a m
v,a v
^ h
ˇ
o u
 ¯u
A;ea o
A;Ea au
134
APPENDICES
A.6
Sanskrit phonetics according to ¯Api´sali
TABLE 6 shows Sanskrit phonetic segments categorized according to the
phonetic features described by the ancient Indian linguist ¯Api´sali and
shown in TABLE 2. Place of articulation features appear in the leftmost
column. Stricture appears in the third row of headings. The fourth row
of headings shows voicing, and the ﬁfth row shows aspiration and nasal-
ization of consonants. Articulators — as well as the extrabuccal features
glottis, larynx, breath impact, length, and pitch — are not shown. Less
common segments are discussed in the notes.1−3 Noteworthy is the place-
ment of anusv¯ara ( ˙m) with spirants.
Notes:
1. Vowels include prolonged lengths called pluta; three pitches ud¯atta,
anud¯atta, svarita; and nasalized variants.
2. Semivowels y, l, v include nasal variants ˜y, ˜l, ˜v.
3. The long vowels IR ¯ı  ¯r
˚
 ¯l
˚
 ¯u are classiﬁed here, with the same
place of articulation as the corresponding short vowels.
4. Four additional nasals ˜k, ˜kh, ˜g, and ˜gh, called yama, occur instead of
non-nasal stops before nasals.
5. The more open diphthongs O; e A;ea o also have a guttural place of
articulation.
6. The even more open diphthongs Oe; ai A;Ea au also have a guttural place
of articulation.
7. The nasal stops .z, ˙n V,a ñ :N,a n. n,a n m,a m have a secondary nasal place of
articulation.
APPENDIX A: TABLES
135
TABLE 6: Sanskrit phonetics according to ¯Api´sali
CONSONANTS
VOWELS1
stops
semivowels2
spirants
simple diphthongs
simple
incontinuously contacted
slightly cont. slightly open open3
>
>>
most open close
UNVOICED
VOICED
VOICED
UNVD.
VD.
VOICED
unasp. asp.
unasp. asp.
nasal4
GUTTURAL
k, k
K,a kh
g,a g
;G,a gh
.z, ˙n
H h.
h, h
⇓5
⇓6
A;a ¯a
A a
DORSOLINGUAL
^ h¯
PALATAL
.c,a c
C, ch
.j,a j
J,a jh
V,a ñ
y,a y
Z,a ´s
I i
O; e
Oe; ai
RETROFLEX
f, t.
F, t.h
.q, d.
Q, d. h
:N,a n.
.=, r
:S,a s.
 r
˚
DENTAL
t,a t
T,a th
d, d
;D,a dh
n,a n
l, l
.s,a s
 l
˚
LABIAL
:p,a p
:P, ph
b,a b
B,a bh
m,a m
v,a v
^ h
ˇ
o u
A;ea o A;Ea au
NASAL
⇑7
M ˙m
136
APPENDICES
A.7
Sanskrit phonetics according to ´Saunaka
TABLE 7 shows Sanskrit phonetic segments categorized according to the
phonetic features described by the ancient Indian linguist ´Saunaka and
shown in TABLE 3. Place of articulation features appear in the leftmost
column. Stricture appears in the third row of headings. The fourth row of
headings shows voicing, and the ﬁfth row shows aspiration and nasaliza-
tion of consonants, as well as length of vowels. Not noted in TABLE 3,
´Saunaka distinguishes fused complex vowels from diphthongs, as shown
in the sixth row of headings. Glottal aperture, vocal fold disposition,
material, and pitch described in TABLE 3 are not shown. Less common
segments are discussed in the notes.1−5 Noteworthy is the placement of
anusv¯ara ( ˙m) with spirants.
Notes:
1. Vowels include prolonged lengths called pluta; three pitches ud¯atta,
anud¯atta, svarita; and nasalized variants.
2. Semivowels y, l, v include nasal variants ˜y, ˜l, ˜v.
3. Four additional nasals ˜k, ˜kh, ˜g, and ˜gh, called yama, occur instead
of non-nasal stops before nasals. A nasal fricative ˜h occurs after h
before n. , n, m.
4. Unaspirated and aspirated retroﬂex lateral ﬂaps written L, l. and \h, l.h
occur intervocalically instead of d. and d. h, according to Vedamitra
(1.51).
5. Anusv¯ara is lengthened by 1
4 mora to 3
4 mora after short vowels and
is shortened 1
4 mora to 1
4 mora after long vowels.
APPENDIX A: TABLES
137
TABLE 7: Sanskrit phonetics according to ´Saunaka
CONSONANTS
VOWELS1
stops
semivowels2
spirants
simple
complex
incontinuously contacted
slightly cont. continuously open continuously open continuously open
UNVOICED
VOICED
VOICED
UNVD.
VD.
VOICED
VOICED
unasp. asp.
unasp. asp.
nasal3
short long
long
fused diphthong
GUTTURAL
H h.
h, h
A a
A;a ¯a
VELAR
k, k
K,a kh
g,a g
;G,a gh
.z, ˙n
^ h¯
PALATAL
.c,a c
C, ch
.j,a j
J,a jh
V,a ñ
y,a y
Z,a ´s
I i
IR ¯ı
O; e
Oe; ai
RETROFLEX4
f, t.
F, t.h
.q, d.
Q, d. h
:N,a n.
.=, r
:S,a s.
 r
˚
 ¯r
˚
DENTAL
t,a t
T,a th
d, d
;D,a dh
n,a n
l, l
.s,a s
 l
˚
 ¯l
˚
LABIAL
:p,a p
:P, ph
b,a b
B,a bh
m,a m
v,a v
^ h
ˇ
o u
 ¯u
A;ea o
A;Ea au
NASAL
M ˙m5
138
APPENDICES
A.8
Sanskrit phonemics
TABLE 8 shows Sanskrit phonemes according to traditional strict deﬁni-
tions of the concept of a phoneme. The table redisplays Sanskrit phonetic
segments shown in TABLE 5, setting phonemes in black and sounds that
occur only as allophones in gray. The latter and the marginal phonemes
anusv¯ara and visarga are discussed in the notes.1−4
Notes:
1. Visarga, allophone of s in pausa becomes a phonetic variant of jihv¯a-
m¯ul¯ıya and upadhm¯an¯ıya before unvoiced velar and labial stops and
of sibilants before the same sibilant.
It contrasts with s < k, p;
e. g. paspa´sa : antah. pura, paraspara : sarah. padma, antah. karan. a :
uraska.
2. Anusv¯ara, generally an allophone of morpheme-ﬁnal m before a semivowel
or spirant, and word-ﬁnal before a non-labial stop, is a phonetic vari-
ant of m before a labial stop. It contrasts with m in samr¯at., samyak,
aml¯ana, ¯amred. ita.
3. Jihv¯am¯ul¯ıya and upadhm¯an¯ıya are allophones of s word-ﬁnally be-
fore unvoiced velar and labial stops, respectively.
4. The palatal nasal is an allophone of n before a palatal stop and is an
allophone of m and phonetic variant of anusv¯ara in the same context.
APPENDIX A: TABLES
139
TABLE 8: Sanskrit phonemics
CONSONANTS
VOWELS
stops
semivowels
spirants
contacted
slightly cont. slightly open open
simply open more open
most open
UNVOICED
VOICED
VOICED
UNVOICED
VOICED
VOICED
VOICED
unasp. asp.
unasp. asp.
nasal
short long
short long
long
GUTTURAL
h, h
H h.
1
A a
A;a ¯a
VELAR
k, k
K,a kh
g,a g
;G,a gh
.z, ˙n
M ˙m2
^ h¯
3
PALATAL
.c,a c
C, ch
.j,a j
J,a jh V,a ñ4
y,a y
Z,a ´s
I i
IR ¯ı
O; e
Oe; ai
RETROFLEX
f, t.
F, t.h
.q, d.
Q, d. h
:N,a n.
.=, r
:S,a s.
 r
˚
 ¯r
˚
DENTAL
t,a t
T,a th
d, d
;D,a dh
n,a n
l, l
.s,a s
 l
˚
 ¯l
˚
LABIAL
:p,a p
:P, ph
b,a b
B,a bh m,a m
v,a v
^ h
ˇ
3
o u
 ¯u
A;ea o
A;Ea au
140
APPENDICES
A.9
Sanskrit sounds derived from PIE by Bur-
row
TABLE 9 redisplays the headings and arrangement of sounds given in
TABLE 5 and shows the Proto-Indo-European reconstruction of each
Sanskrit sound in the place the Sanskrit sound occupies in TABLE 5.
The derivations follow those given in Burrow (1955); for Burrow’s re-
construction of PIE phonology see TABLE 10.
Notes:
1. Some voiced aspirates may perhaps be derived from a voiced unaspi-
rated stop + H (ibid, 72).
2. The symbol Xh stands for the voiced aspirated stops gwh, ´gh, dh, bh.
3. Labiovelars become palatal before H1e, eH1, i, iH; otherwise they
become velar (Burrow, 1955, 74–76).
4. Dental stops become retroﬂex after s. or together with preceding l
(ibid., 96–99).
5. s →s. after i u r/r
˚
k except before r/r
˚
(ibid., 80).
6. /b/ is rare or non-existent in PIE. Sanskrit b may arise from voicing
of p; a special instance is voicing caused by a laryngeal, thus Skt.
pibati ‘drinks’ < *pi-pH3-eti (ibid., 72–73).
APPENDIX A: TABLES
141
TABLE 9: Derivation of Sanskrit sounds from Proto-Indo-European phonemes according to Burrow
CONSONANTS
VOWELS
stops
semivowels
spirants
contacted
slightly cont. slightly open open
simply open more open
most open
UNVOICED
VOICED
VOICED
UNVOICED
VOICED
VOICED
VOICED
unasp. asp.
unasp.
asp.1
nasal
short long
short long long
GUTTURAL
Xh 2
s
He
eH
VELAR3
kw
kwH
gw
gwh
n
n,m
s
PALATAL3
kw,´k kwH,´kH
gw,´g
gwh,´gh
n
y
´k
y
yH
Hey
eHy
RETROFLEX4
t
tH
d
dh
n
r,l
´k,s5
r
rH
DENTAL
t
tH
d
dh
n
r,l
´k,s
l
lH
LABIAL
p
pH
b,p,pH6
bh
m
w
s
w
wH
Hew
eHw
142
APPENDICES
A.10
PIE phonemics according to Burrow
TABLE 10 shows the Proto-Indo-European phonological system as re-
constructed by Burrow (1955). Burrow’s exposition is less than pellucid,
and his introductory lists of PIE sounds with reﬂexes in various daughter
languages is misleading, since he later vigorously argues against the ra-
tionale for a considerable number of these sounds. In part, he is reacting
to Edgerton (1946). Burk (1976, 15–18) takes Burrow’s tables at face
value, and attributes to Burrow a Brugmannesque reconstruction of the
consonant system together with 26 (!) vowels and diphthongs.
Notes:
1. Burrow also reconstructs a so-called “laryngeal” H, of unspeciﬁed
phonetic value (Burrow, 1955, 85–89). He further describes a three-
laryngeal theory with H1, H2, and H3 but notes that “the laryngeal
theory has not yet acquired a completely satisfactory form” (ibid.,
108). He denies that “H in any of its varieties could function as a
vowel” (ibid., 107).
2. Burrow dismisses as “without serious foundation” (ibid., 82) the re-
construction of fricatives þ and ð. On p. 67 he notes a velar nasal and
z but does not discuss these further.
3. Voiceless aspirated stops are not shown, since Burrow reconstructs
these uniformly from voiceless stop + H (ibid., 71–73).
4. Burrow observes that, since the development of the laryngeal theory,
the only “purely ...vocalic element” is /e/ (ibid., 108). /a/ and /o/
are to be explained either through qualitative alteration or by the ac-
tion of H. /i/ and /u/ as well as the syllabic nasals and liquids are
allophones of the respective consonant phonemes. Long vowels re-
sult uniformly from vowel + H. For a notably lapidary criticism of
similar reconstructions, see Velten (1956).
5. The nasal stops and sonorants have syllabic (vocalic) allophones /n"
m" r" l" i u/ (ibid., 108).
6. Velar stops are shown in gray, since Burrow regards it as “exceed-
ingly doubtful whether three distinct series [i. e. palatal, velar, labiove-
lar] existed in Indo-European” (ibid., 76).
APPENDIX A: TABLES
143
TABLE 10: Proto-Indo-European phonemics according to Burrow
CONSONANTS1,2,3
VOWELS4
stops
liquids5
glides5
spirants
UNVD.
VOICED
VOICED
UNVD.
VOICED
unasp.
unasp.
asp.
nasal5
LABIOVELAR
kw
gw
gwh
VELAR6
k
g
gh
w
PALATAL
´k
´g
´gh
r
y
e
DENTAL
t
d
dh
n
l
s
LABIAL
p
b
bh
m
144
APPENDICES
A.11
PIE phonemics according to Szemerényi
TABLE 11 shows the Proto-Indo-European phonological system as re-
constructed by Szemerényi (1967). This is Szemerényi’s proposed “new
look” for Indo-European, that is “the linguistic stage which can be recon-
structed from the data of the IE languages as their immediate antecedent”
(Szemerényi, 1967, 96 n. 90). The primary differences between this re-
construction and Burrow’s are as follows: (1) a system of four, rather
than three, types of stops is posited in each series of stops; (2) a sepa-
rate series of “palatal” stops is introduced; (3) only a single laryngeal is
given, and it is identiﬁed as /h/, a glottal spirant; (4) there are ﬁve basic
vowel phonemes, which occur both short (/a e o i u/) and long (/¯a ¯e ¯o ¯ı
¯u), and also a schwa.
It is worth noting that this analysis resembles, along broad lines, that
of Brugmann (1906–1916).
APPENDIX A: TABLES
145
TABLE 11: Proto-Indo-European phonemics according to Szemerényi
CONSONANTS
VOWELS1
stops
liquids
glides
spirants
low
mid
high
UNVOICED
VOICED
VOICED
UNVD.
VOICED
unasp.
asp.
unasp.
asp.
nasal
GLOTTAL
h
LABIOVELAR
kw
kwh
gw
gwh
VELAR
k
kh
g
gw
a
PALATAL
´k
´kh
´g
´gh
r
y
@
e
i
DENTAL
t
th
d
dh
n
l
s
LABIAL
p
ph
b
bh
m
w
o
u
146
APPENDICES
A.12
Feature tree after Halle
TABLE 12 shows the feature geometry proposed by Halle (1995). In fa-
vor of the interpretation of phonological features as organized in a tree,
rather than constituting an unordered list, are the facts that (1) only a
substantially restricted combination of features is ever used in phono-
logical rules, and (2) sets of features used in phonological rules share a
designated articulator.
APPENDIX A: TABLES
147
TABLE 12: Feature tree after Halle (1995)
[suction]
[continuant]
[strident]
[lateral]
[nasal]
Soft Palate
[consonantal]
[sonorant]
[retracted tongue root]
Tongue Root
[advanced tongue root]
Guttural
[stiff vocal folds]
[slack vocal folds]
Larynx
[constricted glottis]
[spread glottis]
[anterior]
Coronal
[distributed]
[round]
Labial
Place
[back]
[high]
Dorsal
[low]
148
APPENDICES
A.13
Graphic features of Devan¯agar¯ı accord-
ing to Ivanov and Toporov
TABLE 13 reproduces the set of distinctive features for graphemes of the
Devan¯agar¯ı script suggested by Ivanov & Toporov (1968, 27–32):
1. upper horizontal line
2. main vertical line
3. upper non-right-hand “curved” line
4. upper non-right-hand diagonal curve
5. lower quirk
6. straight line perpendicular to the main vertical line
7. curved connecting line
8. closed curve
9. second vertical line parallel to the main line
10. curved line to the right or to the left of the vertical line
11. diagonal line inside the close ﬁgure
12. semiloop
13. rounded lower continuation of line 3 turned to the right
14. minor circle
15. rounded lower continuation of line 3 turned to the left
16. the combination of one-directional minor and major loops
17. left diagonal line
18. curved downward line
19. curve with the incomplete loop
20. upper diacritic
21. dot
APPENDIX A: TABLES
149
TABLE 13: Graphic features of Devan¯agar¯ı according to Ivanov and Toporov
A A;a I IR o      O; Oe; A;ea A;Ea k Ka ga ;Ga .z .ca C .ja Ja Va f F .q Q :Na ta Ta d ;Da na :pa :P ba Ba ma ya .= l va Za :Sa .sa h M H
1
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
+
−
+
+
+
+
−
+
+
+
+
+
+
+
+
+ −−
2
+
+
−
−
−
−
+
+
+
+
−
−
+
+
+
+
+
+
−
+
−
+
+
+
−
−
−
−
+
+
+
−
+
+
+
+
+
+
+
+
−
+
+
+
+
+
−−−
3
−
−
+
+
+
+
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
+
−
+
+
+
+
−
−
+
+
−
−
−
−
−
−
−
+
−
−
−
−
−
−
+ −−
4
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
+
+
−
+
−
−
−
−
+
−−−
5
−
−
+
+
−
−
−
−
−
−
+
+
−
−
−
+
−
−
−
−
−
−
+
−
−
−
−
−
+
−
−
+
−
−
−
−
−
−
−
−
+
−
−
+
−
+
−−−
6
−
−
−
−
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
+
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
+
−
−
−
−
−
−
+
−−−
7
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
+
+
−
−
−
+
−
−
−
−
+
−
−−−
8
−
−
−
−
−
−
−
−
−
−
+
−
−
−
+
+
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
+
−
−
−
−−−
9
−
+
−
−
−
−
+
+
−
−
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
10
−
−
−
−
−
+
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−−−
11
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
+
−
−
+
−
−
−
−
−
−
−
+
−
−−−
12
−
−
−
+
−
−
+
+
+
+
−
−
−
−
−
−
−
−
−
+
−
+
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
13
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
+
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+ −−
14
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−−−
15
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
+
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
16
−
−
−
−
−
−
−
−
+
+
−
−
−
−
−
−
−
+
−
−
+
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
17
+
+
+
−
−
−
+
+
−
−
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
18
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
19
−
−
−
−
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−−−
20
−
−
−
−
−
−
−
−
−
−
+
+
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−−−
21
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
+
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−
−+ +
150
APPENDICES
Appendix B
Sanskrit Library Phonetic
Basic
The Sanskrit Library Phonetic Basic encoding scheme (SLP1) attempts
to meet high standards of unambiguous encoding while restricting encod-
ing to 76 codepoints in the ASCII character set. SLP1 utilizes 58 code-
points to encode segments: 53 to represent phonetic segments and ﬁve
to represent punctuation ⟨’ .
?
-
⟩. In addition SLP1 utilizes 18
codepoints to encode phonetic features: three to indicate stricture, six to
indicate length, eight to indicate tone, and one to indicate nasalization.
Although certain features are indicated by a sequence of codepoints, no
codepoints double as both segments and features. While useful, SLP1
is not an ideal encoding. To its credit it is consistent in that it consis-
tently encodes phonetic rather than graphic elements (with the exception
of the punctuation signs). Yet it does not maintain a consistent basis of
encoding because it mixes the encoding of phonetic segments and pho-
netic features. Nor does it satisfy the Fano condition because it utilizes a
few codepoints as preﬁxes in code sequences. For example, the forward
slash ⟨/⟩, back slash ⟨\⟩, and caret ⟨^⟩indicate ud¯atta, anud¯atta, and
independent svarita accents by themselves but also serve as the preﬁxes
in several sequences that indicate particular tones and tonal sequences
realized in various Vedic traditions; and the digit ⟨1⟩, which by itself
indicates short length, is used as a preﬁx in a sequence that serves to in-
151
152
APPENDICES
dicate length of 1 1
2 morae. Nevertheless, single codepoints capture most
phonetic segments commonly used in classical Sanskrit. The only com-
monly occurring phonetic segment that requires a sequence is nasalized
l, i. e. ⟨l~⟩. Moreover, SLP1 does clearly deﬁne single codepoints or
code sequences to capture a comprehensive set of phonetic distinctions
in classical and Vedic Sanskrit.
B.1
Basic Segments
A a
a
A;a ¯a
A
I i
i
IR ¯ı
I
o u
u
 ¯u
U
 r
˚
f
 ¯r
˚
F
 l
˚
x
 ¯l
˚
X
O; e
e
Oe; ai
E
A;ea o
o
A;Ea au
O
k, k
k
K,a kh
K
g,a g
g
;G,a gh
G
.z, ˙n
N
.c,a c
c
C, ch
C
.j,a j
j
J,a jh
J
V,a ñ
Y
f, t.
w
F, t.h
W
.q, d.
q
Q, d.h
Q
:N,a n.
R
L, l.
L
\h, l.h
|
t,a t
t
T,a th
T
d, d
d
;D,a dh
D
n,a n
n
:p,a p
p
:P, ph
P
b,a b
b
B,a bh
B
m,a m
m
y,a y
y
.=, r
r
l, l
l
v,a v
v
Z,a ´s
S
:S,a s.
z
.s,a s
s
h, h
h
H h.
H
^ h¯
Z
^ hˇ
V
M ˙m
M
APPENDIX B: SANSKRIT LIBRARY PHONETIC BASIC
153
B.2
Punctuation
Although punctuation does not properly belong to a phonetic encoding,
a limited number of punctuation tokens are supported in this encoding,
since they can be used to provide basic segmentation information. The
question mark is used to indicate inaudible or illegible characters in tran-
scription.
Y ’
’
Á .
.
;;; ?
?
- -
-
2
avagraha
danda
question
hyphen
space
B.3
Modiﬁers
Modiﬁers are added after a character to indicate variations in segment
stricture, length, accent, and nasalization, in the order stated. Prolonged
length, accent, and nasalization occur in classical Sanskrit as well as Ve-
dic. Modiﬁers are used in combination to indicate special features of
stricture, length, accent, and nasalization in Vedic.
B.3.1
Stricture
_
heaviness [used for semivowels y or v]
=
lightness [used for semivowels y or v]
!
lack of release (abhinidh¯ana) [used for stops or
semivowels y, v, or l]
B.3.2
Length
*
subsegmental epenthetic vowel (svarabhakti)
#
length of half a mora
1
length of one mora [used in Vedic after short agi-
tated kampa; short e, o; and heavy anusv¯ara]
1#
slightly lengthened
2
length of two morae [used for dvim¯atra anusv¯ara
in Vedic]
154
APPENDICES
3
prolonged length of three morae [used for pluta
vowels]
4
prolonged length of four or more morae [used in
ra˙nga]
B.3.3
Accent
/
high pitch
\
low pitch
^
circumﬂex
6
extra low tone
7
low tone
8
high tone
9
extra high tone
+
sharpness
B.3.4
Nasalization
~
nasalization
B.4
Modiﬁer combinations and usage notes
B.4.1
Stricture
y_
heavy y
v_
heavy v
y=
light y
v=
light v
k!
unreleased (abhinidh¯ana) k
g!
unreleased (abhinidh¯ana) g
... similarly for other unreleased stops
y!
unreleased (abhinidh¯ana) y
v!
unreleased (abhinidh¯ana) v
l!
unreleased (abhinidh¯ana) l
APPENDIX B: SANSKRIT LIBRARY PHONETIC BASIC
155
B.4.2
Length
a*
epenthetic a
i*
epenthetic i
u*
epenthetic u
f*
epenthetic r
˚
x*
epenthetic l
˚
e*
epenthetic e
e1
short e
o1
short o
a1#
slightly lengthened short a
... similarly for other slightly lengthened short vowels
B.4.3
Surface accent
Tonal contours in Vedic have numerous distinct varieties described in
Pr¯ati´s¯akhyas. The indication of these requires the use of the accent signs
for high pitch, low pitch, and circumﬂex (/, \, and ^) in conjunction with
tonal modiﬁers 6, 7, 8, 9 that indicate the features extra low, low, high,
and extra high pitch respectively. The additional modiﬁer + is used to
indicate a distinction in sharpness or effort of uncertain phonetic signiﬁ-
cance described in the V¯ajasaneyi (1.125) and Taittir¯ıya (20.9-12) Pr¯ati-
´s¯akhyas, in spite of the same length of vowel and same beginning and
end pitches. The term ‘aggravation’ below translates kampa: ‘aggra-
vated’ means with kampa; ‘unaggravated’ means without kampa. The
following modiﬁer sequences are used to indicate the tonal features de-
scribed to their right:
/8
high tone (ud¯atta)
\7
low tone (anud¯atta)
\6
extra low tone (sannatara)
^98
declining tone from extra high to high (dependent
and unaggravated independent svarita according
to the R
˚
kpr¯ati´s¯akhya)
^97
declining tone from extra high to low (aggra-
vated independent svarita according to the R
˚
k-
pr¯ati´s¯akhya)
156
APPENDICES
^87
declining tone from high to low (dependent sva-
rita according to the V¯ajasaneyi (1.125) and Tait-
tir¯ıya (20.9–12) Pr¯ati´s¯akhyas)
^87+
sharp declining tone from high to low (indepen-
dent svarita according to the V¯ajasaneyi (1.125)
and Taittir¯ıya (20.9–12) Pr¯ati´s¯akhyas)
^86
declining tone from high to extra low (aggravated
independent svarita according to the V¯ajasaneyi-
pr¯ati´s¯akhya)
Vowel accent examples
a/8
high toned vowel a
a^97
the vowel a with short agitated circumﬂex as de-
scribed in the R
˚
kpr¯ati´s¯akhya
a3^97
the vowel a with prolonged agitated circumﬂex as
described in the R
˚
kpr¯ati´s¯akhya
B.4.4
Syllabiﬁed visarga and anusv¯ara accent
H/
high-pitched visarga
H\
low-pitched visarga
H^
svarita visarga
M\
low-pitched anusv¯ara
B.4.5
Nasals
Nasalization
Both SLP1 and SLP2 include means to encode 20 yamas (k~, kh~, ...,
b~, bh~) considered, on phonetic grounds, to be epenthetic nasalized
segments that adopt features of both of the preceding stop and of the fol-
lowing nasal. Yet the preferred method of encoding yamas, in accordance
with the phonological analysis of most ancient Indian phonetic treatises,
is to employ characters for just four epenthetic nasals (k~, kh~, g~,
gh~), or, on the minority view of the R
˚
kpr¯ati´s¯akhya, to employ yamas
APPENDIX B: SANSKRIT LIBRARY PHONETIC BASIC
157
(k~, kh~, ..., b~, bh~) in place of the non-nasal stop that precedes the
nasal. (See p. 63 and p. 72 for discussion.)
l~
nasalized l
y~
nasalized y
v~
nasalized v
k~
nasalized offset (yama), after unvoiced unaspi-
rated non-nasal stop when followed by a nasal
stop
K~
nasalized offset (yama), after unvoiced aspirated
non-nasal stop when followed by a nasal stop
g~
nasalized offset (yama), after voiced unaspirated
non-nasal stop when followed by a nasal stop
G~
nasalized offset (yama), after voiced aspirated
non-nasal stop when followed by a nasal stop
h~
nasalized offset (n¯asikya), after h when followed
by a nasal stop
Anusv¯ara
M#
short anusv¯ara (which follows a long vowel ac-
cording to the R
˚
k and V¯ajasaneyi Pr¯ati´s¯akhyas:
R
˚
Pr. 13.22, 13.29, 13.32–33; VPr.
4.148–149;
the short anusv¯ara measures half a mora while the
preceding vowel measures 1.5 morae)
M1#
long anusv¯ara (which follows a short vowel ac-
cording to the R
˚
k and V¯ajasaneyi Pr¯ati´s¯akhyas;
the long anusv¯ara measures 1.5 morae while the
preceding vowel measures 0.5 morae)
M1
heavy anusv¯ara (which is usually called guru and
also by some hrasva and which occurs before a
conjunct consonant according to ´Siks.¯as)
M2
two-mora anusv¯ara (which is called dvim¯atra and
occurs before a consonant followed by r
˚
according
to ´Siks.¯as)
158
APPENDICES
Ra˙nga
2~
two-mora ra˙nga (vowel two m¯atras in length
nasalized for the last half m¯atra with kampa in the
middle according to P¯an. in¯ıya´siks. ¯a 26–30)
4~
ra˙nga (nasalized vowel four m¯atras in length fol-
lowed by a break according to Malla´sarmakr
˚
ta-
´siks. ¯a; texts show a double danda to mark the break
Appendix C
Sanskrit Library Phonetic
Segmental
The Sanskrit Library Phonetic Segmental encoding scheme (SLP2) ad-
heres to the most rigorous standards of unambiguous encoding described
in Chapter 4. It utilizes a consistent basis for encoding, namely broadly
deﬁned phonemes, and it creates a one-to-one correspondence between
codepoints and items encoded. In terms of the three axes of encoding,
SLP2 encodes phonetics rather than graphics, segments rather than fea-
tures, and contrastive rather than complementary units. It encodes San-
skrit phonetic segments by assigning one codepoint to each phoneme
broadly deﬁned, that is, to each segment that is minimally contrastive in
the sense concluded in sections 6.1.5 and 6.1.6.
In column 1 the unique codepoints of SLP2 are shown in hexadecimal
notation. In column 2 the equivalent encoding in SLP1 is given. In
columns 3 and 4 Devan¯agar¯ı and Roman representations are given. In
column 5 an IPA transcription of the encoded sound is given.
Devan¯agar¯ı
Often several options are given for the marking of Vedic accentuation in
Devan¯agar¯ı, including those used in the following traditions:
159
160
APPENDICES
1. ´S¯akalasa ˙mhit¯a of the R
˚
gveda
2. V¯ajasaneyisa ˙mhit¯a of the ´Suklayajurveda
3. Taittir¯ıyasa ˙mhit¯a of the Kr
˚
s.n. ayajurveda
4. ´Saunak¯ıyasa ˙mhit¯a of the Atharvaveda
5. Maitr¯ayan. ¯ısa ˙mhit¯a of the Kr
˚
s.n. ayajurveda, R
˚
gveda khil¯ani, and
Kashmiri mss. of #2
6. K¯at.hakasa ˙mhit¯a of the Kr
˚
s.n. ayajurveda
7. Paippal¯adasa ˙mhit¯a of the Atharvaveda
8. S¯amavedasa ˙mhit¯a in the Kauthuma ´sakh¯a
9. ´Satapathabr¯ahman. a
Superscript numerals given in the table refer to these nine traditions. The
options are illustrative rather than comprehensive for two reasons: First,
correlating the precise phonetics of various traditions of Vedic recitation
with graphic signs used in manuscripts requires further research and may
never be determined completely. The association of svarita marks with
particular surface tonal sequences in 012-017, for instance, is merely
suggestive based on the division into dependent (012-013), independent
(014-015), and aggravated independent svaritas (016-017) for traditions
in which the ud¯atta is the highest tone (5-7). Second, at the time of writ-
ing, even sophisticated typesetting software does not permit representa-
tion of all the graphic signs used in various Vedic traditions. Among
svaritas not shown is Maitr¯ayan.¯ı dependent svarita, marked with a hori-
zontal stroke at mid-height through a character. Besides the marks that
represent the independent svarita shown at 006, 010 and 058, 014, and
016, there is, for example, º used in the ´Saunak¯ıyasa ˙mhit¯a of the Athar-
vaveda. The Vedic Unicode Character Phonetic Value Table linked to the
Sanskrit Library Vedic Unicode page correlates most of the new charac-
ters included in the Devanagari Extended and Vedic Extensions blocks
with the Sanskrit Library Phonetic encoding (SLP1) and demonstrates
which are used in which Vedic traditions.
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 161
IPA transcription
The IPA transcription given in column 5 is for reference; it does not
necessarily represent the only historically correct reconstruction for the
sound in question. Surface tones are indicated using the tone-letter sys-
tem of Chao (1930). Underlying tones are indicated using the grave ac-
cent, acute accent, and circumﬂex accent with their standard IPA (1949–
1996) meanings.
The short a [5] in Sanskrit, although described as close in comparison
with ¯a [A:], is yet more open than schwa [@].
The diphthongs ai and au in the modern pronunciation of Sanskrit
use the close a [5] at the onset but preserve the same sounds as the corre-
sponding vowels i [i] and u [u] at the offset. The vowels represented by
i and u are the most front and most back vowels shown in the IPA chart;
they never represent [I] as in ‘pin’ or [U] as in ‘book’.
We use the true palatal symbols for the palatal series of stops c ch j
jh [c ch é éh] and a palatal spirant ´s [ç] rather than alveolar fricatives [Ù Ùh
Ã Ãh].
162
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
000
a
A
a
5
001
a~
A<
˜a
˜5
002
a/
A 1−4 / A 5−7 / A 8
´a
´5
003
a/~
A< 1−4 / A< 5−7 / A< 8
´˜a
´˜5
004
a\
A! 1−5 / AÉ
6,7 / A 8
a/a¯
`5
005
a\~
A<! 1−5 / A<É
6,7 / A< 8
˜a/˜a¯
`˜5
006
a^
A 1,3 / AÉï
2 / A 8
`a
ˆ5
007
a^~
A< 1,3 / A<Éï
2 / A< 8
`˜a
ˆ˜5
008
a/8
A 1−4 / A 5−7
5Ă£
009
a/8~
A< 1−4 / A< 5−7
˜5Ă£
00A
a\7
A! 1−4 / A 5−6 / AÍ
7
5Ă£
00B
a\7~
A<! 1−4 / A< 5−6 / A<Í
7
˜5Ă£
00C
a\6
A! 5 / AÉ
6,7
5Ă£
00D
a\6~
A<! 5 / A<É
6,7
˜5Ă£
00E
a^98
A 1−4
5Ą£
00F
a^98~
A< 1−4
˜5Ą£
010
a^97
A1! 1,4
5Ć£
011
a^97~
A<1! 1,4
˜5Ć£
012
a^87
A 5 / AÍ
6,7
5Ą£
013
a^87~
A< 5 / A<Í
6,7
˜5Ą£
014
a^87+
A 5,6 / AÉï
7
5Ą£
015
a^87+~
A< 5,6 / A<Éï
7
˜5Ą£
016
a^86
3A! 5 / A 6
5Ć£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 163
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
017
a^86~
3A<! 5 / A< 6
˜5Ć£
018
a1#
A
a
5;
019
a1#~
A<
˜a
˜5;
01A
a1#/
A 1−4 / A 5−7 / A 8
´a
´5;
01B
a1#/~
A< 1−4 / A< 5−7 / A< 8
´˜a
´˜5;
01C
a1#\
A! 1−5 / AÉ
6,7 / A 8
a/a¯
`5;
01D
a1#\~
A<! 1−5 / A<É
6,7 / A< 8
˜a/˜a¯
`˜5;
01E
a1#^
A 1,3 / AÉï
2 / A 8
`a
ˆ5;
01F
a1#^~
A< 1,3 / A<Éï
2 / A< 8
`˜a
ˆ˜5;
020
a1#/8
A 1−4 / A 5−7
5;Ă£
021
a1#/8~
A< 1−4 / A< 5−7
˜5;Ă£
022
a1#\7
A! 1−4 / A 5−6 / AÍ
7
5;Ă£
023
a1#\7~
A<! 1−4 / A< 5−6 / A<Í
7
˜5;Ă£
024
a1#\6
A! 5 / AÉ
6,7
5;Ă£
025
a1#\6~
A<! 5 / A<É
6,7
˜5;Ă£
026
a1#^98
A 1−4
5;Ą£
027
a1#^98~
A< 1−4
˜5;Ą£
028
a1#^97
A1! 1,4
5;Ć£
029
a1#^97~
A<1! 1,4
˜5;Ć£
02A
a1#^87
A 5 / AÍ
6,7
5;Ą£
02B
a1#^87~
A< 5 / A<Í
6,7
˜5;Ą£
02C
a1#^87+
A 5,6 / AÉï
7
5;Ą£
02D
a1#^87+~
A< 5,6 / A<Éï
7
˜5;Ą£
164
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
02E
a1#^86
3A! 5 / A 6
5;Ć£
02F
a1#^86~
3A<! 5 / A< 6
˜5;Ć£
030
A
A;a
¯a
A:
031
A~
A;a<
˜¯a
˜A:
032
A/
A;a 1−4 / A;a 5−7 / A;a 8
´¯a
´A:
033
A/~
A;a< 1−4 / A;a< 5−7 / A;a< 8
´˜¯a
´˜A:
034
A\
A;a! 1−5 / A;aÉ
6,7 / A;a 8
¯a/¯a¯
`A:
035
A\~
A;a<! 1−5 / A;a<É
6,7 / A;a< 8
˜¯a/˜¯a¯
`˜A:
036
A^
A;a 1,3 / A;aÉï
2 / A;a 8
`¯a
ˆA:
037
A^~
A;a< 1,3 / A;a<Éï
2 / A;a< 8
`˜¯a
ˆ˜A:
038
A/8
A;a 1−4 / A;a 5−7
A:Ă£
039
A/8~
A;a< 1−4 / A;a< 5−7
˜A:Ă£
03A
A\7
A;a! 1−4 / A;a 5−6 / A;aÍ
7
A:Ă£
03B
A\7~
A;a<! 1−4 / A;a< 5−6 / A;a<Í
7
˜A:Ă£
03C
A\6
A;a! 5 / A;aÉ
6,7
A:Ă£
03D
A\6~
A;a<! 5 / A;a<É
6,7
˜A:Ă£
03E
A^98
A;a 1−4
A:Ą£
03F
A^98~
A;a< 1−4
˜A:Ą£
040
A^97
A;a!3! 1,4
A:Ć£
041
A^97~
A;a<!3! 1,4
˜A:Ć£
042
A^87
A;a 5 / A;aÍ
6,7
A:Ą£
043
A^87~
A;a< 5 / A;a<Í
6,7
˜A:Ą£
044
A^87+
A;a 5,6 / A;aÉï
7
A:Ą£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 165
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
045
A^87+~
A;a< 5,6 / A;a<Éï
7
˜A:Ą£
046
A^86
3A;a! 5 / A;a 6
A:Ć£
047
A^86~
3A;a<! 5 / A;a< 6
˜A:Ć£
048
a3
A3
a3
A::
049
a3~
A<3
˜a3
˜A::
04A
a3/
A3 1−4 / A3 5−7 / A3 8
´a3
´A::
04B
a3/~
A<3 1−4 / A<3 5−7 / A<3 8
´˜a3
´˜A::
04C
a3\
A!3 1−7 / A3 8
a3/a¯3
`A::
04D
a3\~
A<!3 1−7 / A<3 8
˜a3/˜a¯3
`˜A::
04E
a3^
A3 1,3 / AÉï3 2 / A3 8
`a3
ˆA::
04F
a3^~
A<3 1,3 / A<Éï3 2 / A<3 8
`˜a3
ˆ˜A::
050
a3/8
A3 1−4 / A3 5−7
A::Ă£
051
a3/8~
A<3 1−4 / A<3 5−7
˜A::Ă£
052
a3\7
A!3 1−4 / A3 5−7
A::Ă£
053
a3\7~
A<!3 1−4 / A<3 5−7
˜A::Ă£
054
a3\6
A!3 5 / AÉ3 6,7
A::Ă£
055
a3\6~
A<!3 5 / A<É3 6,7
˜A::Ă£
056
a3^98
A3 1−4
A::Ą£
057
a3^98~
A<3 1−4
˜A::Ą£
058
a3^97
A!3! 1,4
A::Ć£
059
a3^97~
A<!3! 1,4
˜A::Ć£
05A
a3^87
A 3 5 / AÍ 3 6,7
A::Ą£
05B
a3^87~
A< 3 5 / A<Í 3 6,7
˜A::Ą£
166
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
05C
a3^87+
A3 5,6 / AÉï3 7
A::Ą£
05D
a3^87+~
A<3 5,6 / A<Éï3 7
˜A::Ą£
05E
a3^86
3A!3 5 / A3 6
A::Ć£
05F
a3^86~
3A<!3 5 / A<3 6
˜A::Ć£
060
a4~
A<4
˜a4
˜A:::
061
a4/~
A<4 1−4 / A<4 5−7 / A<4 8
´˜a4
´˜A:::
062
a4\~
A<!4 1−7 / A<4 8
˜a4/˜a¯4
`˜A:::
063
a4^~
A<4 1,3 / A<Éï4 2 / A<4 8
`˜a4
ˆ˜A:::
064
a4/8~
A<4 1−4 / A<4 5−7
˜A:::Ă£
065
a4\7~
A<!4 1−4 / A<4 5−7
˜A:::Ă£
066
a4\6~
A<!4 5 / A<É4 6,7
˜A:::Ă£
067
a4^98~
A<4 1−4
˜A:::Ą£
068
a4^97~
˜A:::Ć£
069
a4^87~
A< 4 5 / A<Í 4 6,7
˜A:::Ą£
06A
a4^87+~
A<4 5,6 / A<Éï4 7
˜A:::Ą£
06B
a4^86~
3A<!4 5 / A<4 6
˜A:::Ć£
06C
a*
a
˘5
080
i
I
i
i
081
i~
I<
˜ı
˜ı
082
i/
I 1−4 / I 5−7 / I 8
´ı
´ı
083
i/~
I< 1−4 / I< 5−7 / I< 8
´˜ı
´˜ı
084
i\
I! 1−5 / IÉ
6,7 / I 8
i/i¯
`ı
085
i\~
I<! 1−5 / I<É
6,7 / I< 8
˜ı/˜ı¯
`˜ı
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 167
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
086
i^
I 1,3 / IÉï
2 / I 8
`ı
ˆı
087
i^~
I< 1,3 / I<Éï
2 / I< 8
`˜ı
ˆ˜ı
088
i/8
I 1−4 / I 5−7
iĂ£
089
i/8~
I< 1−4 / I< 5−7
˜ıĂ£
08A
i\7
I! 1−4 / I 5−6 / IÍ
7
iĂ£
08B
i\7~
I<! 1−4 / I< 5−6 / I<Í
7
˜ıĂ£
08C
i\6
I! 5 / IÉ
6,7
iĂ£
08D
i\6~
I<! 5 / I<É
6,7
˜ıĂ£
08E
i^98
I 1−4
iĄ£
08F
i^98~
I< 1−4
˜ıĄ£
090
i^97
I1! 1,4
iĆ£
091
i^97~
I<1! 1,4
˜ıĆ£
092
i^87
I 5 / IÍ
6,7
iĄ£
093
i^87~
I< 5 / I<Í
6,7
˜ıĄ£
094
i^87+
I 5,6 / IÉï
7
iĄ£
095
i^87+~
I< 5,6 / I<Éï
7
˜ıĄ£
096
i^86
3+I! 5 / I 6
iĆ£
097
i^86~
3+I<! 5 / I< 6
˜ıĆ£
098
i1#
I
i
i;
099
i1#~
I<
˜ı
˜ı;
09A
i1#/
I 1−4 / I 5−7 / I 8
´ı
´ı;
09B
i1#/~
I< 1−4 / I< 5−7 / I< 8
´˜ı
´˜ı;
09C
i1#\
I! 1−5 / IÉ
6,7 / I 8
i/i¯
`ı;
168
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
09D
i1#\~
I<! 1−5 / I<É
6,7 / I< 8
˜ı/˜ı¯
`˜ı;
09E
i1#^
I 1,3 / IÉï
2 / I 8
`ı
ˆı;
09F
i1#^~
I< 1,3 / I<Éï
2 / I< 8
`˜ı
ˆ˜ı;
0A0
i1#/8
I 1−4 / I 5−7
i;Ă£
0A1
i1#/8~
I< 1−4 / I< 5−7
˜ı;Ă£
0A2
i1#\7
I! 1−4 / I 5−6 / IÍ
7
i;Ă£
0A3
i1#\7~
I<! 1−4 / I< 5−6 / I<Í
7
˜ı;Ă£
0A4
i1#\6
I! 5 / IÉ
6,7
i;Ă£
0A5
i1#\6~
I<! 5 / I<É
6,7
˜ı;Ă£
0A6
i1#^98
I 1−4
i;Ą£
0A7
i1#^98~
I< 1−4
˜ı;Ą£
0A8
i1#^97
I1! 1,4
i;Ć£
0A9
i1#^97~
I<1! 1,4
˜ı;Ć£
0AA
i1#^87
I 5 / IÍ
6,7
i;Ą£
0AB
i1#^87~
I< 5 / I<Í
6,7
˜ı;Ą£
0AC
i1#^87+
I 5,6 / IÉï
7
i;Ą£
0AD
i1#^87+~
I< 5,6 / I<Éï
7
˜ı;Ą£
0AE
i1#^86
3+I! 5 / I 6
i;Ć£
0AF
i1#^86~
3+I<! 5 / I< 6
˜ı;Ć£
0B0
I
IR
¯ı
i:
0B1
I~
I_
˜¯ı
˜ı:
0B2
I/
IR 1−4 / IR 5−7 / IR 8
´¯ı
´ı:
0B3
I/~
I_ 1−4 / I_ 5−7 / I_ 8
´˜¯ı
´˜ı:
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 169
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
0B4
I\
IR! 1−5 / IRÉ
6,7 / IR 8
¯ı/¯ı¯
`ı:
0B5
I\~
I_! 1−5 / I_É
6,7 / I_ 8
˜¯ı/˜¯ı¯
`˜ı:
0B6
I^
IR 1,3 / IRÉï
2 / IR 8
`¯ı
ˆı:
0B7
I^~
I_ 1,3 / I_Éï
2 / I_ 8
`˜¯ı
ˆ˜ı:
0B8
I/8
IR 1−4 / IR 5−7
i:Ă£
0B9
I/8~
I_ 1−4 / I_ 5−7
˜ı:Ă£
0BA
I\7
IR! 1−4 / IR 5−6 / IRÍ
7
i:Ă£
0BB
I\7~
I_! 1−4 / I_ 5−6 / I_Í
7
˜ı:Ă£
0BC
I\6
IR! 5 / IRÉ
6,7
i:Ă£
0BD
I\6~
I_! 5 / I_É
6,7
˜ı:Ă£
0BE
I^98
IR 1−4
i:Ą£
0BF
I^98~
I_ 1−4
˜ı:Ą£
0C0
I^97
IR! 3! 1,4
i:Ć£
0C1
I^97~
I_!3! 1,4
˜ı:Ć£
0C2
I^87
IR 5 / IRÍ
6,7
i:Ą£
0C3
I^87~
I_ 5 / I_Í
6,7
˜ı:Ą£
0C4
I^87+
IR 5,6 / IRÉï
7
i:Ą£
0C5
I^87+~
I_ 5,6 / I_Éï
7
˜ı:Ą£
0C6
I^86
3+IR! 5 / IR 6
i:Ć£
0C7
I^86~
3+I_! 5 / I_ 6
˜ı:Ć£
0C8
i3
I3
i3
i::
0C9
i3~
I<3
˜ı3
˜ı::
0CA
i3/
I3 1−4 / I3 5−7 / I3 8
´ı3
´ı::
170
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
0CB
i3/~
I<3 1−4 / I<3 5−7 / I<3 8
´˜ı3
´˜ı::
0CC
i3\
I!3 1−7 / I3 8
i3/i¯3
`ı::
0CD
i3\~
I<!3 1−7 / I<3 8
˜ı3/˜ı¯3
`˜ı::
0CE
i3^
I3 1,3 / IÉï3 2 / I3 8
`ı3
ˆı::
0CF
i3^~
I<3 1,3 / I<Éï3 2 / I<3 8
`˜ı3
ˆ˜ı::
0D0
i3/8
I3 1−4 / I3 5−7
i::Ă£
0D1
i3/8~
I<3 1−4 / I<3 5−7
˜ı::Ă£
0D2
i3\7
I!3 1−4 / I3 5−7
i::Ă£
0D3
i3\7~
I<!3 1−4 / I<3 5−7
˜ı::Ă£
0D4
i3\6
I!3 5 / IÉ 3 6,7
i::Ă£
0D5
i3\6~
I<!3 5 / I<É 3 6,7
˜ı::Ă£
0D6
i3^98
I3 1−4
i::Ą£
0D7
i3^98~
I<3 1−4
˜ı::Ą£
0D8
i3^97
I! 3! 1,4
i::Ć£
0D9
i3^97~
I<!3! 1,4
˜ı::Ć£
0DA
i3^87
I 3 5 / IÍ 3 6,7
i::Ą£
0DB
i3^87~
I< 3 5 / I<Í 3 6,7
˜ı::Ą£
0DC
i3^87+
I3 5,6 / IÉï3 7
i::Ą£
0DD
i3^87+~
I<3 5,6 / I<Éï3 7
˜ı::Ą£
0DE
i3^86
3+I!3 5 / I3 6
i::Ć£
0DF
i3^86~
3+I<!3 5 / I<3 6
˜ı::Ć£
0E0
i4~
I<4
˜ı4
˜ı:::
0E1
i4/~
I<4 1−4 / I<4 5−7 / I<4 8
´˜ı4
´˜ı:::
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 171
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
0E2
i4\~
I<!4 1−7 / I<4 8
˜ı4/˜ı¯4
`˜ı:::
0E3
i4^~
I<4 1,3 / I<Éï4 2 / I<4 8
`˜ı4
ˆ˜ı:::
0E4
i4/8~
I<4 1−4 / I<4 5−7
˜ı:::Ă£
0E5
i4\7~
I<!4 1−4 / I<4 5−7
˜ı:::Ă£
0E6
i4\6~
I<!4 5 / I<É 4 6,7
˜ı:::Ă£
0E7
i4^98~
I<4 1−4
˜ı:::Ą£
0E8
i4^97~
˜ı:::Ć£
0E9
i4^87~
I< 4 5 / I<Í 4 6,7
˜ı:::Ą£
0EA
i4^87+~
I<4 5,6 / I<Éï4 7
˜ı:::Ą£
0EB
i4^86~
3+I<!4 5 / I<4 6
˜ı:::Ć£
0EC
i*
i
˘ı
100
u
o
u
u
101
u~
o<
˜u
˜u
102
u/
o 1−4 / o 5−7 / o 8
´u
´u
103
u/~
o< 1−4 / o< 5−7 / o< 8
´˜u
´˜u
104
u\
o! 1−5 / oÉ
6,7 / o 8
u/u¯
`u
105
u\~
o<! 1−5 / o<É
6,7 / o< 8
˜u/˜u¯
`˜u
106
u^
o 1,3 / oÉï
2 / o 8
`u
ˆu
107
u^~
o< 1,3 / o<Éï
2 / o< 8
`˜u
ˆ˜u
108
u/8
o 1−4 / o 5−7
uĂ£
109
u/8~
o< 1−4 / o< 5−7
˜uĂ£
10A
u\7
o! 1−4 / o 5−6 / oÍ
7
uĂ£
10B
u\7~
o<! 1−4 / o< 5−6 / o<Í
7
˜uĂ£
172
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
10C
u\6
o! 5 / oÉ
6,7
uĂ£
10D
u\6~
o<! 5 / o<É
6,7
˜uĂ£
10E
u^98
o 1−4
uĄ£
10F
u^98~
o< 1−4
˜uĄ£
110
u^97
o1! 1,4
uĆ£
111
u^97~
o<1! 1,4
˜uĆ£
112
u^87
o 5 / oÍ
6,7
uĄ£
113
u^87~
o< 5 / o<Í
6,7
˜uĄ£
114
u^87+
o 5,6 / oÉï
7
uĄ£
115
u^87+~
o< 5,6 / o<Éï
7
˜uĄ£
116
u^86
3+o! 5 / o 6
uĆ£
117
u^86~
3+o<! 5 / o< 6
˜uĆ£
118
u1#
o
u
u;
119
u1#~
o<
˜u
˜u;
11A
u1#/
o 1−4 / o 5−7 / o 8
´u
´u;
11B
u1#/~
o< 1−4 / o< 5−7 / o< 8
´˜u
´˜u;
11C
u1#\
o! 1−5 / oÉ
6,7 / o 8
u/u¯
`u;
11D
u1#\~
o<! 1−5 / o<É
6,7 / o< 8
˜u/˜u¯
`˜u;
11E
u1#^
o 1,3 / oÉï
2 / o 8
`u
ˆu;
11F
u1#^~
o< 1,3 / o<Éï
2 / o< 8
`˜u
ˆ˜u;
120
u1#/8
o 1−4 / o 5−7
u;Ă£
121
u1#/8~
o< 1−4 / o< 5−7
˜u;Ă£
122
u1#\7
o! 1−4 / o 5−6 / oÍ
7
u;Ă£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 173
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
123
u1#\7~
o<! 1−4 / o< 5−6 / o<Í
7
˜u;Ă£
124
u1#\6
o! 5 / oÉ
6,7
u;Ă£
125
u1#\6~
o<! 5 / o<É
6,7
˜u;Ă£
126
u1#^98
o 1−4
u;Ą£
127
u1#^98~
o< 1−4
˜u;Ą£
128
u1#^97
o1! 1,4
u;Ć£
129
u1#^97~
o<1! 1,4
˜u;Ć£
12A
u1#^87
o 5 / oÍ
6,7
u;Ą£
12B
u1#^87~
o< 5 / o<Í
6,7
˜u;Ą£
12C
u1#^87+
o 5,6 / oÉï
7
u;Ą£
12D
u1#^87+~
o< 5,6 / o<Éï
7
˜u;Ą£
12E
u1#^86
3+o! 5 / o 6
u;Ć£
12F
u1#^86~
3+o<! 5 / o< 6
˜u;Ć£
130
U

¯u
u:
131
U~
<
˜¯u
˜u:
132
U/
 1−4 /  5−7 /  8
´¯u
´u:
133
U/~
< 1−4 / < 5−7 / < 8
´˜¯u
´˜u:
134
U\
! 1−5 / É
6,7 /  8
¯u/¯u¯
`u:
135
U\~
<! 1−5 / <É
6,7 / < 8
˜¯u/˜¯u¯
`˜u:
136
U^
 1,3 / Éï
2 /  8
`¯u
ˆu:
137
U^~
< 1,3 / <Éï
2 / < 8
`˜¯u
ˆ˜u:
138
U/8
 1−4 /  5−7
u:Ă£
139
U/8~
< 1−4 / < 5−7
˜u:Ă£
174
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
13A
U\7
! 1−4 /  5−6 / Í
7
u:Ă£
13B
U\7~
<! 1−4 / < 5−6 / <Í
7
˜u:Ă£
13C
U\6
! 5 / É
6,7
u:Ă£
13D
U\6~
<! 5 / <É
6,7
˜u:Ă£
13E
U^98
 1−4
u:Ą£
13F
U^98~
< 1−4
˜u:Ą£
140
U^97
! 3! 1,4
u:Ć£
141
U^97~
<! 3! 1,4
˜u:Ć£
142
U^87

5 / Í
6,7
u:Ą£
143
U^87~
<
5 / <Í
6,7
˜u:Ą£
144
U^87+
 5,6 / Éï
7
u:Ą£
145
U^87+~
< 5,6 / <Éï
7
˜u:Ą£
146
U^86
3+! 5 /  6
u:Ć£
147
U^86~
3+<! 5 / < 6
˜u:Ć£
148
u3
o3
u3
u::
149
u3~
o<3
˜u3
˜u::
14A
u3/
o3 1−4 / o3 5−7 / o3 8
´u3
´u::
14B
u3/~
o<3 1−4 / o<3 5−7 / o<3 8
´˜u3
´˜u::
14C
u3\
o!3 1−7 / o3 8
u3/u¯3
`u::
14D
u3\~
o<!3 1−7 / o<3 8
˜u3/˜u¯3
`˜u::
14E
u3^
o3 1,3 / oÉï3 2 / o3 8
`u3
ˆu::
14F
u3^~
o<3 1,3 / o<Éï3 2 / o<3 8
`˜u3
ˆ˜u::
150
u3/8
o3 1−4 / o3 5−7
u::Ă£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 175
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
151
u3/8~
o<3 1−4 / o<3 5−7
˜u::Ă£
152
u3\7
o!3 1−4 / o3 5−7
u::Ă£
153
u3\7~
o<!3 1−4 / o<3 5−7
˜u::Ă£
154
u3\6
o!3 5 / oÉ 3 6,7
u::Ă£
155
u3\6~
o<!3 5 / o<É 3 6,7
˜u::Ă£
156
u3^98
o3 1−4
u::Ą£
157
u3^98~
o<3 1−4
˜u::Ą£
158
u3^97
o!3! 1,4
u::Ć£
159
u3^97~
o<!3! 1,4
˜u::Ć£
15A
u3^87
o 3 5 / oÍ 3 6,7
u::Ą£
15B
u3^87~
o< 3 5 / o<Í 3 6,7
˜u::Ą£
15C
u3^87+
o3 5,6 / oÉï3 7
u::Ą£
15D
u3^87+~
o<3 5,6 / o<Éï3 7
˜u::Ą£
15E
u3^86
3+o!3 5 / o3 6
u::Ć£
15F
u3^86~
3+o<!3 5 / o<3 6
˜u::Ć£
160
u4~
o<4
˜u4
˜u:::
161
u4/~
o<4 1−4 / o<4 5−7 / o<4 8
´˜u4
´˜u:::
162
u4\~
o<!4 1−7 / o<4 8
˜u4/˜u¯4
`˜u:::
163
u4^~
o<4 1,3 / o<Éï4 2 / o<4 8
`˜u4
ˆ˜u:::
164
u4/8~
o<4 1−4 / o<4 5−7
˜u:::Ă£
165
u4\7~
o<!4 1−4 / o<4 5−7
˜u:::Ă£
166
u4\6~
o<!4 5 / o<É 4 6,7
˜u:::Ă£
167
u4^98~
o<4 1−4
˜u:::Ą£
176
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
168
u4^97~
˜u:::Ć£
169
u4^87~
o< 4 5 / o<Í 4 6,7
˜u:::Ą£
16A
u4^87+~
o<4 5,6 / o<Éï4 7
˜u:::Ą£
16B
u4^86~
3+o<!4 5 / o<4 6
˜u:::Ć£
16C
u*
u
˘u
180
f

r
˚
õ
"
181
f~
<
˜r
˚
˜õ
"
182
f/
 1−4 /  5−7 /  8
´r
˚
´õ
"
183
f/~
< 1−4 / < 5−7 / < 8
´˜r
˚
´˜õ
"
184
f\
! 1−5 / É
6,7 /  8
r
˚
/r
˚¯
`õ
"
185
f\~
<! 1−5 / <É
6,7 / < 8
˜r
˚
/˜r
˚¯
`˜õ
"
186
f^
 1,3 / Éï
2 /  8
`r
˚
ˆõ
"
187
f^~
< 1,3 / <Éï
2 / < 8
`˜r
˚
ˆ˜õ
"
188
f/8
 1−4 /  5−7
õ
"
Ă£
189
f/8~
< 1−4 / < 5−7
˜õ
"
Ă£
18A
f\7
! 1−4 /  5−6 / Í
7
õ
"
Ă£
18B
f\7~
<! 1−4 / < 5−6 / <Í
7
˜õ
"
Ă£
18C
f\6
! 5 / É
6,7
õ
"
Ă£
18D
f\6~
<! 5 / <É
6,7
˜õ
"
Ă£
18E
f^98
 1−4
õ
"
Ą£
18F
f^98~
< 1−4
˜õ
"
Ą£
190
f^97
1! 1,4
õ
"
Ć£
191
f^97~
< 1! 1,4
˜õ
"
Ć£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 177
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
192
f^87

5 / Í
6,7
õ
"
Ą£
193
f^87~
<
5 / <Í
6,7
˜õ
"
Ą£
194
f^87+
 5,6 / Éï
7
õ
"
Ą£
195
f^87+~
< 5,6 / <Éï
7
˜õ
"
Ą£
196
f^86
3+! 5 /  6
õ
"
Ć£
197
f^86~
3+<! 5 / < 6
˜õ
"
Ć£
198
f1#

r
˚
õ
"
;
199
f1#~
<
˜r
˚
˜õ
"
;
19A
f1#/
 1−4 /  5−7 /  8
´r
˚
´õ
"
;
19B
f1#/~
< 1−4 / < 5−7 / < 8
´˜r
˚
´˜õ
"
;
19C
f1#\
! 1−5 / É
6,7 /  8
r
˚
/r
˚¯
`õ
"
;
19D
f1#\~
<! 1−5 / <É
6,7 / < 8
˜r
˚
/˜r
˚¯
`˜õ
"
;
19E
f1#^
 1,3 / Éï
2 /  8
`r
˚
ˆõ
"
;
19F
f1#^~
< 1,3 / <Éï
2 / < 8
`˜r
˚
ˆ˜õ
"
;
1A0
f1#/8
 1−4 /  5−7
õ
"
;Ă£
1A1
f1#/8~
< 1−4 / < 5−7
˜õ
"
;Ă£
1A2
f1#\7
! 1−4 /  5−6 / Í
7
õ
"
;Ă£
1A3
f1#\7~
<! 1−4 / < 5−6 / <Í
7
˜õ
"
;Ă£
1A4
f1#\6
! 5 / É
6,7
õ
"
;Ă£
1A5
f1#\6~
<! 5 / <É
6,7
˜õ
"
;Ă£
1A6
f1#^98
 1−4
õ
"
;Ą£
1A7
f1#^98~
< 1−4
˜õ
"
;Ą£
1A8
f1#^97
1! 1,4
õ
"
;Ć£
178
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
1A9
f1#^97~
< 1! 1,4
˜õ
"
;Ć£
1AA
f1#^87

5 / Í
6,7
õ
"
;Ą£
1AB
f1#^87~
<
5 / <Í
6,7
˜õ
"
;Ą£
1AC
f1#^87+
 5,6 / Éï
7
õ
"
;Ą£
1AD
f1#^87+~
< 5,6 / <Éï
7
˜õ
"
;Ą£
1AE
f1#^86
3+! 5 /  6
õ
"
;Ć£
1AF
f1#^86~
3+<! 5 / < 6
˜õ
"
;Ć£
1B0
F

¯r
˚
õ
"
:
1B1
F~
<
˜¯r
˚
˜õ
"
:
1B2
F/
 1−4 / 
5−7 / 
8
´¯r
˚
´õ
"
:
1B3
F/~
<
1−4 / <
5−7 / <
8
´˜¯r
˚
´˜õ
"
:
1B4
F\
! 1−5 / É
6,7 / 
8
¯r
˚
/¯r
˚¯
`õ
"
:
1B5
F\~
<! 1−5 / <É
6,7 / <
8
˜¯r
˚
/˜¯r
˚¯
`˜õ
"
:
1B6
F^

1,3 / Éï
2 / 
8
`¯r
˚
ˆõ
"
:
1B7
F^~
<
1,3 / <Éï
2 / <
8
`˜¯r
˚
ˆ˜õ
"
:
1B8
F/8
 1−4 / 
5−7
õ
"
:Ă£
1B9
F/8~
<
1−4 / <
5−7
˜õ
"
:Ă£
1BA
F\7
! 1−4 /  5−6 / Í
7
õ
"
:Ă£
1BB
F\7~
<! 1−4 / <
5−6 / <Í
7
˜õ
"
:Ă£
1BC
F\6
! 5 / É
6,7
õ
"
:Ă£
1BD
F\6~
<! 5 / <É
6,7
˜õ
"
:Ă£
1BE
F^98

1−4
õ
"
:Ą£
1BF
F^98~
<
1−4
˜õ
"
:Ą£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 179
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
1C0
F^97
! 3! 1,4
õ
"
:Ć£
1C1
F^97~
<! 3! 1,4
˜õ
"
:Ć£
1C2
F^87

5 / Í
6,7
õ
"
:Ą£
1C3
F^87~
<
5 / <Í
6,7
˜õ
"
:Ą£
1C4
F^87+
 5,6 / Éï
7
õ
"
:Ą£
1C5
F^87+~
< 5,6 / <Éï
7
˜õ
"
:Ą£
1C6
F^86
3+! 5 /  6
õ
"
:Ć£
1C7
F^86~
3+<! 5 / < 6
˜õ
"
:Ć£
1C8
f3
3
r
˚
3
õ
"
::
1C9
f3~
< 3
˜r
˚
3
˜õ
"
::
1CA
f3/
3 1−4 /  3 5−7 /  3 8
´r
˚
3
´õ
"
::
1CB
f3/~
< 3 1−4 / < 3 5−7 / < 3 8
´˜r
˚
3
´˜õ
"
::
1CC
f3\
! 3 1−7 /  3 8
r
˚
3/r
˚¯
3
`õ
"
::
1CD
f3\~
<! 3 1−7 / < 3 8
˜r
˚
3/˜r
˚¯
3
`˜õ
"
::
1CE
f3^
 3 1,3 / Éï 3 2 /  3 8
`r
˚
3
ˆõ
"
::
1CF
f3^~
< 3 1,3 / <Éï 3 2 / < 3 8
`˜r
˚
3
ˆ˜õ
"
::
1D0
f3/8
3 1−4 /  3 5−7
õ
"
::Ă£
1D1
f3/8~
< 3 1−4 / < 3 5−7
˜õ
"
::Ă£
1D2
f3\7
! 3 1−4 / 3 5−7
õ
"
::Ă£
1D3
f3\7~
<! 3 1−4 / < 3 5−7
˜õ
"
::Ă£
1D4
f3\6
! 3 5 / É 3 6,7
õ
"
::Ă£
1D5
f3\6~
<! 3 5 / <É 3 6,7
˜õ
"
::Ă£
1D6
f3^98
 3 1−4
õ
"
::Ą£
180
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
1D7
f3^98~
< 3 1−4
˜õ
"
::Ą£
1D8
f3^97
! 3! 1,4
õ
"
::Ć£
1D9
f3^97~
<! 3! 1,4
˜õ
"
::Ć£
1DA
f3^87
 3 5 / Í 3 6,7
õ
"
::Ą£
1DB
f3^87~
< 3 5 / <Í 3 6,7
˜õ
"
::Ą£
1DC
f3^87+
 3 5,6 / Éï 3 7
õ
"
::Ą£
1DD
f3^87+~
< 3 5,6 / <Éï 3 7
˜õ
"
::Ą£
1DE
f3^86
3+! 3 5 /  3 6
õ
"
::Ć£
1DF
f3^86~
3+<! 3 5 / < 3 6
˜õ
"
::Ć£
1E0
f4~
< 4
˜r
˚
4
˜õ
"
:::
1E1
f4/~
< 4 1−4 / < 4 5−7 / < 4 8
´˜r
˚
4
´˜õ
"
:::
1E2
f4\~
<! 4 1−7 / < 4 8
˜r
˚
4/˜r
˚¯
4
`˜õ
"
:::
1E3
f4^~
< 4 1,3 / <Éï 4 2 / < 4 8
`˜r
˚
4
ˆ˜õ
"
:::
1E4
f4/8~
< 4 1−4 / < 4 5−7
˜õ
"
:::Ă£
1E5
f4\7~
<! 4 1−4 / < 4 5−7
˜õ
"
:::Ă£
1E6
f4\6~
<! 4 5 / <É 4 6,7
˜õ
"
:::Ă£
1E7
f4^98~
< 4 1−4
˜õ
"
:::Ą£
1E8
f4^97~
˜õ
"
:::Ć£
1E9
f4^87~
< 4 5 / <Í 4 6,7
˜õ
"
:::Ą£
1EA
f4^87+~
< 4 5,6 / <Éï 4 7
˜õ
"
:::Ą£
1EB
f4^86~
3+<! 4 5 / < 4 6
˜õ
"
:::Ć£
1EC
f*
r
˚
˘õ
"
200
x

l
˚
l"
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 181
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
201
x~
<
˜l
˚
˜l"
202
x/
 1−4 /  5−7 /  8
´l
˚
´l"
203
x/~
< 1−4 / < 5−7 / < 8
´˜l
˚
´˜l"
204
x\
! 1−5 / É
6,7 /  8
l
˚
/l
˚¯
`l"
205
x\~
<! 1−5 / <É
6,7 / < 8
˜l
˚
/˜l
˚¯
`˜l"
206
x^
 1,3 / Éï
2 /  8
`l
˚
ˆl"
207
x^~
< 1,3 / <Éï
2 / < 8
`˜l
˚
ˆ˜l"
208
x/8
 1−4 /  5−7
l"
Ă£
209
x/8~
< 1−4 / < 5−7
˜l"
Ă£
20A
x\7
! 1−4 /  5−6 / Í
7
l"
Ă£
20B
x\7~
<! 1−4 / < 5−6 / <Í
7
˜l"
Ă£
20C
x\6
! 5 / É
6,7
l"
Ă£
20D
x\6~
<! 5 / <É
6,7
˜l"
Ă£
20E
x^98
 1−4
l"
Ą£
20F
x^98~
< 1−4
˜l"
Ą£
210
x^97
1! 1,4
l"
Ć£
211
x^97~
< 1! 1,4
˜l"
Ć£
212
x^87
 5 / Í
6,7
l"
Ą£
213
x^87~
< 5 / <Í
6,7
˜l"
Ą£
214
x^87+
 5,6 / Éï
7
l"
Ą£
215
x^87+~
< 5,6 / <Éï
7
˜l"
Ą£
216
x^86
3+! 5 /  6
l"
Ć£
217
x^86~
3+<! 5 / < 6
˜l"
Ć£
182
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
218
x1#

l
˚
l";
219
x1#~
<
˜l
˚
˜l";
21A
x1#/
 1−4 /  5−7 /  8
´l
˚
´l";
21B
x1#/~
< 1−4 / < 5−7 / < 8
´˜l
˚
´˜l";
21C
x1#\
! 1−5 / É
6,7 /  8
l
˚
/l
˚¯
`l";
21D
x1#\~
<! 1−5 / <É
6,7 / < 8
˜l
˚
/˜l
˚¯
`˜l";
21E
x1#^
 1,3 / Éï
2 /  8
`l
˚
ˆl";
21F
x1#^~
< 1,3 / <Éï
2 / < 8
`˜l
˚
ˆ˜l";
220
x1#/8
 1−4 /  5−7
l";Ă£
221
x1#/8~
< 1−4 / < 5−7
˜l";Ă£
222
x1#\7
! 1−4 /  5−6 / Í
7
l";Ă£
223
x1#\7~
<! 1−4 / < 5−6 / <Í
7
˜l";Ă£
224
x1#\6
! 5 / É
6,7
l";Ă£
225
x1#\6~
<! 5 / <É
6,7
˜l";Ă£
226
x1#^98
 1−4
l";Ą£
227
x1#^98~
< 1−4
˜l";Ą£
228
x1#^97
1! 1,4
l";Ć£
229
x1#^97~
< 1! 1,4
˜l";Ć£
22A
x1#^87
 5 / Í
6,7
l";Ą£
22B
x1#^87~
< 5 / <Í
6,7
˜l";Ą£
22C
x1#^87+
 5,6 / Éï
7
l";Ą£
22D
x1#^87+~
< 5,6 / <Éï
7
˜l";Ą£
22E
x1#^86
3+! 5 /  6
l";Ć£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 183
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
22F
x1#^86~
3+<! 5 / < 6
˜l";Ć£
230
X

¯l
˚
l":
231
X~
<
˜¯l
˚
˜l":
232
X/
 1−4 /  5−7 /  8
´¯l
˚
´l":
233
X/~
< 1−4 / < 5−7 / < 8
´˜¯l
˚
´˜l":
234
X\
! 1−5 / É
6,7 /  8
¯l
˚
/¯l
˚¯
`l":
235
X\~
<! 1−5 / <É
6,7 / < 8
˜¯l
˚
/˜¯l
˚¯
`˜l":
236
X^
 1,3 / Éï
2 /  8
`¯l
˚
ˆl":
237
X^~
< 1,3 / <Éï
2 / < 8
`˜¯l
˚
ˆ˜l":
238
X/8
 1−4 /  5−7
l":Ă£
239
X/8~
< 1−4 / < 5−7
˜l":Ă£
23A
X\7
! 1−4 /  5−6 / Í
7
l":Ă£
23B
X\7~
<! 1−4 / < 5−6 / <Í
7
˜l":Ă£
23C
X\6
! 5 / É
6,7
l":Ă£
23D
X\6~
<! 5 / <É
6,7
˜l":Ă£
23E
X^98
 1−4
l":Ą£
23F
X^98~
< 1−4
˜l":Ą£
240
X^97
!3! 1,4
l":Ć£
241
X^97~
<!3! 1,4
˜l":Ć£
242
X^87
 5 / Í
6,7
l":Ą£
243
X^87~
< 5 / <Í
6,7
˜l":Ą£
244
X^87+
 5,6 / Éï
7
l":Ą£
245
X^87+~
< 5,6 / <Éï
7
˜l":Ą£
184
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
246
X^86
3+! 5 /  6
l":Ć£
247
X^86~
3+<! 5 / < 6
˜l":Ć£
248
x3
3
l
˚
3
l"::
249
x3~
< 3
˜l
˚
3
˜l"::
24A
x3/
3 1−4 /  3 5−7 /  3 8
´l
˚
3
´l"::
24B
x3/~
< 3 1−4 / < 3 5−7 / < 3 8
´˜l
˚
3
´˜l"::
24C
x3\
!3 1−7 /  3 8
l
˚
3/l
˚¯
3
`l"::
24D
x3\~
<!3 1−7 / < 3 8
˜l
˚
3/˜l
˚¯
3
`˜l"::
24E
x3^
 3 1,3 / Éï3 2 /  3 8
`l
˚
3
ˆl"::
24F
x3^~
< 3 1,3 / <Éï3 2 / < 3 8
`˜l
˚
3
ˆ˜l"::
250
x3/8
3 1−4 /  3 5−7
l"::Ă£
251
x3/8~
< 3 1−4 / < 3 5−7
˜l"::Ă£
252
x3\7
!3 1−4 / 3 5−7
l"::Ă£
253
x3\7~
<!3 1−4 / < 3 5−7
˜l"::Ă£
254
x3\6
!3 5 / É 3 6,7
l"::Ă£
255
x3\6~
<!3 5 / <É 3 6,7
˜l"::Ă£
256
x3^98
 3 1−4
l"::Ą£
257
x3^98~
< 3 1−4
˜l"::Ą£
258
x3^97
!3! 1,4
l"::Ć£
259
x3^97~
<!3! 1,4
˜l"::Ć£
25A
x3^87
 3 5 / Í 3 6,7
l"::Ą£
25B
x3^87~
< 3 5 / <Í 3 6,7
˜l"::Ą£
25C
x3^87+
3 5,6 / Éï3 7
l"::Ą£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 185
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
25D
x3^87+~
<3 5,6 / <Éï3 7
˜l"::Ą£
25E
x3^86
3+!3 5 / 3 6
l"::Ć£
25F
x3^86~
3+<!3 5 / <3 6
˜l"::Ć£
260
x4~
< 4
˜l
˚
4
˜l":::
261
x4/~
< 4 1−4 / < 4 5−7 / < 4 8
´˜l
˚
4
´˜l":::
262
x4\~
<!4 1−7 / < 4 8
˜l
˚
4/˜l
˚¯
4
`˜l":::
263
x4^~
< 4 1,3 / <Éï4 2 / < 4 8
`˜l
˚
4
ˆ˜l":::
264
x4/8~
< 4 1−4 / < 4 5−7
˜l":::Ă£
265
x4\7~
<!4 1−4 / < 4 5−7
˜l":::Ă£
266
x4\6~
<!4 5 / <É 4 6,7
˜l":::Ă£
267
x4^98~
< 4 1−4
˜l":::Ą£
268
x4^97~
˜l":::Ć£
269
x4^87~
< 4 5 / <Í 4 6,7
˜l":::Ą£
26A
x4^87+~
<4 5,6 / <Éï4 7
˜l":::Ą£
26B
x4^86~
3+<!4 5 / <4 6
˜l":::Ć£
26C
x*
l
˚
˘l"
280
e1
O;1
˘e
e
281
e1~
O;<1
˜˘e
˜e
282
e1/
O;1 1−4 / O;1 5−7 / O;1 8
´˘e
´e
283
e1/~
O;<1 1−4 / O;<1 5−7 / O;<1 8
´˜˘e
´˜e
284
e1\
O;!1 1−7 / O;1 8
˘e/˘e¯
`e
285
e1\~
O;<!1 1−7 / O;<1 8
˜˘e/˜˘e¯
`˜e
286
e1^
O;1 1,3 / O;Éï1 2 / O;1 8
`˘e
ˆe
186
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
287
e1^~
O;<1 1,3 / O;<Éï1 2 / O;<1 8
`˜˘e
ˆ˜e
288
e1/8
O;1 1−4 / O;1 5−7
eĂ£
289
e1/8~
O;<1 1−4 / O;<1 5−7
˜eĂ£
28A
e1\7
O;!1 1−4 / O;1 5−7
eĂ£
28B
e1\7~
O;<!1 1−4 / O;<1 5−7
˜eĂ£
28C
e1\6
O;!1 5 / O;É1 6,7
eĂ£
28D
e1\6~
O;<!1 5 / O;<É1 6,7
˜eĂ£
28E
e1^98
O;1 1−4
eĄ£
28F
e1^98~
O;<1 1−4
˜eĄ£
290
e1^97
O;1! 1,4
eĆ£
291
e1^97~
O;<1! 1,4
˜eĆ£
292
e1^87
O; 1 5 / O;Í 1 6,7
eĄ£
293
e1^87~
O;< 1 5 / O;<Í 1 6,7
˜eĄ£
294
e1^87+
O;1 5,6 / O;Éï1 7
eĄ£
295
e1^87+~
O;<1 5,6 / O;<Éï1 7
˜eĄ£
296
e1^86
3:O;!1 5 / O;1 6
eĆ£
297
e1^86~
3:O;<!1 5 / O;<1 6
˜eĆ£
298
e
O;
e
e:
299
e~
O;<
˜e
˜e:
29A
e/
O; 1−4 / O; 5−7 / O; 8
´e
´e:
29B
e/~
O;< 1−4 / O;< 5−7 / O;< 8
´˜e
´˜e:
29C
e\
O;! 1−5 / O;É
6,7 / O; 8
e/e¯
`e:
29D
e\~
O;<! 1−5 / O;<É
6,7 / O;< 8
˜e/˜e¯
`˜e:
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 187
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
29E
e^
O; 1,3 / O;Éï
2 / O; 8
`e
ˆe:
29F
e^~
O;< 1,3 / O;<Éï
2 / O;< 8
`˜e
ˆ˜e:
2A0
e/8
O; 1−4 / O; 5−7
e:Ă£
2A1
e/8~
O;< 1−4 / O;< 5−7
˜e:Ă£
2A2
e\7
O;! 1−4 / O; 5−6 / O;Í
7
e:Ă£
2A3
e\7~
O;<! 1−4 / O;< 5−6 / O;<Í
7
˜e:Ă£
2A4
e\6
O;! 5 / O;É
6,7
e:Ă£
2A5
e\6~
O;<! 5 / O;<É
6,7
˜e:Ă£
2A6
e^98
O; 1−4
e:Ą£
2A7
e^98~
O;< 1−4
˜e:Ą£
2A8
e^97
O;!3! 1,4
e:Ć£
2A9
e^97~
O;<!3! 1,4
˜e:Ć£
2AA
e^87
O; 5 / O;Í
6,7
e:Ą£
2AB
e^87~
O;< 5 / O;<Í
6,7
˜e:Ą£
2AC
e^87+
O; 5,6 / O;Éï
7
e:Ą£
2AD
e^87+~
O;< 5,6 / O;<Éï
7
˜e:Ą£
2AE
e^86
3:O;! 5 / O; 6
e:Ć£
2AF
e^86~
3:O;<! 5 / O;< 6
˜e:Ć£
2B0
e3
O;3
e3
e::
2B1
e3~
O;<3
˜e3
˜e::
2B2
e3/
O;3 1−4 / O;3 5−7 / O;3 8
´e3
´e::
2B3
e3/~
O;<3 1−4 / O;<3 5−7 / O;<3 8
´˜e3
´˜e::
2B4
e3\
O;!3 1−7 / O;3 8
e3/e¯3
`e::
188
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
2B5
e3\~
O;<!3 1−7 / O;<3 8
˜e3/˜e¯3
`˜e::
2B6
e3^
O;3 1,3 / O;Éï3 2 / O;3 8
`e3
ˆe::
2B7
e3^~
O;<3 1,3 / O;<Éï3 2 / O;<3 8
`˜e3
ˆ˜e::
2B8
e3/8
O;3 1−4 / O;3 5−7
e::Ă£
2B9
e3/8~
O;<3 1−4 / O;<3 5−7
˜e::Ă£
2BA
e3\7
O;!3 1−4 / O;3 5−7
e::Ă£
2BB
e3\7~
O;<!3 1−4 / O;<3 5−7
˜e::Ă£
2BC
e3\6
O;!3 5 / O;É3 6,7
e::Ă£
2BD
e3\6~
O;<!3 5 / O;<É3 6,7
˜e::Ă£
2BE
e3^98
O;3 1−4
e::Ą£
2BF
e3^98~
O;<3 1−4
˜e::Ą£
2C0
e3^97
O;!3! 1,4
e::Ć£
2C1
e3^97~
O;<!3! 1,4
˜e::Ć£
2C2
e3^87
O; 3 5 / O;Í 3 6,7
e::Ą£
2C3
e3^87~
O;< 3 5 / O;<Í 3 6,7
˜e::Ą£
2C4
e3^87+
O;3 5,6 / O;Éï3 7
e::Ą£
2C5
e3^87+~
O;<3 5,6 / O;<Éï3 7
˜e::Ą£
2C6
e3^86
3:O;!3 5 / O;3 6
e::Ć£
2C7
e3^86~
3:O;<!3 5 / O;<3 6
˜e::Ć£
2C8
e4~
O;<4
˜e4
˜e:::
2C9
e4/~
O;<4 1−4 / O;<4 5−7 / O;<4 8
´˜e4
´˜e:::
2CA
e4\~
O;<!4 1−7 / O;<4 8
˜e4/˜e¯4
`˜e:::
2CB
e4^~
O;<4 1,3 / O;<Éï4 2 / O;<4 8
`˜e4
ˆ˜e:::
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 189
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
2CC
e4/8~
O;<4 1−4 / O;<4 5−7
˜e:::Ă£
2CD
e4\7~
O;<!4 1−4 / O;<4 5−7
˜e:::Ă£
2CE
e4\6~
O;<!4 5 / O;<É4 6,7
˜e:::Ă£
2CF
e4^98~
O;<4 1−4
˜e:::Ą£
2D0
e4^97~
˜e:::Ć£
2D1
e4^87~
O;< 4 5 / O;<Í 4 6,7
˜e:::Ą£
2D2
e4^87+~
O;<4 5,6 / O;<Éï4 7
˜e:::Ą£
2D3
e4^86~
3:O;<!4 5 / O;<4 6
˜e:::Ć£
2D4
e*
e
˘e
300
E
Oe;
ai
5I<:
301
E~
Oe;<
a˜ı
5˜I<:
302
E/
Oe; 1−4 / Oe; 5−7 / Oe; 8
a´ı
5´I<:
303
E/~
Oe;< 1−4 / Oe;< 5−7 / Oe;< 8
a´˜ı
5´˜I<:
304
E\
Oe;! 1−5 / Oe;É
6,7 / Oe; 8
ai/ai¯
5`I<:
305
E\~
Oe;<! 1−5 / Oe;<É
6,7 / Oe;< 8
a˜ı/a˜ı¯
5`˜I<:
306
E^
Oe; 1,3 / Oe;Éï
2 / Oe; 8
a`ı
5ˆI<:
307
E^~
Oe;< 1,3 / Oe;<Éï
2 / Oe;< 8
a`˜ı
5ˆ˜I<:
308
E/8
Oe; 1−4 / Oe; 5−7
5I<:Ă£
309
E/8~
Oe;< 1−4 / Oe;< 5−7
5˜I<:Ă£
30A
E\7
Oe;! 1−4 / Oe; 5−6 / Oe;Í
7
5I<:Ă£
30B
E\7~
Oe;<! 1−4 / Oe;< 5−6 / Oe;<Í
7
5˜I<:Ă£
30C
E\6
Oe;! 5 / Oe;É
6,7
5I<:Ă£
30D
E\6~
Oe;<! 5 / Oe;<É
6,7
5˜I<:Ă£
190
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
30E
E^98
Oe; 1−4
5I<:Ą£
30F
E^98~
Oe;< 1−4
5˜I<:Ą£
310
E^97
Oe;!3! 1,4
5I<:Ć£
311
E^97~
Oe;<!3! 1,4
5˜I<:Ć£
312
E^87
Oe; 5 / Oe;Í
6,7
5I<:Ą£
313
E^87~
Oe;< 5 / Oe;<Í
6,7
5˜I<:Ą£
314
E^87+
Oe; 5,6 / Oe;Éï
7
5I<:Ą£
315
E^87+~
Oe;< 5,6 / Oe;<Éï
7
5˜I<:Ą£
316
E^86
3:Oe;! 5 / Oe; 6
5I<:Ć£
317
E^86~
3:Oe;<! 5 / Oe;< 6
5˜I<:Ć£
318
E3
Oe;3
ai3
Ai<::
319
E3~
Oe;<3
a˜ı3
A˜ı<::
31A
E3/
Oe;3 1−4 / Oe;3 5−7 / Oe;3 8
a´ı3
A´ı<::
31B
E3/~
Oe;<3 1−4 / Oe;<3 5−7 / Oe;<3 8
a´˜ı3
A´˜ı<::
31C
E3\
Oe;!3 1−7 / Oe;3 8
ai3/ai¯3
A`ı<::
31D
E3\~
Oe;<!3 1−7 / Oe;<3 8
a˜ı3/a˜ı¯3
A`˜ı<::
31E
E3^
Oe;3 1,3 / Oe;Éï3 2 / Oe;3 8
a`ı3
Aˆı<::
31F
E3^~
Oe;<3 1,3 / Oe;<Éï3 2 / Oe;<3 8
a`˜ı3
Aˆ˜ı<::
320
E3/8
Oe;3 1−4 / Oe;3 5−7
Ai<::Ă£
321
E3/8~
Oe;<3 1−4 / Oe;<3 5−7
A˜ı<::Ă£
322
E3\7
Oe;!3 1−4 / Oe;3 5−7
Ai<::Ă£
323
E3\7~
Oe;<!3 1−4 / Oe;<3 5−7
A˜ı<::Ă£
324
E3\6
Oe;!3 5 / Oe;É3 6,7
Ai<::Ă£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 191
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
325
E3\6~
Oe;<!3 5 / Oe;<É3 6,7
A˜ı<::Ă£
326
E3^98
Oe;3 1−4
Ai<::Ą£
327
E3^98~
Oe;<3 1−4
A˜ı<::Ą£
328
E3^97
Oe;!3! 1,4
Ai<::Ć£
329
E3^97~
Oe;<!3! 1,4
A˜ı<::Ć£
32A
E3^87
Oe; 3 5 / Oe;Í 3 6,7
Ai<::Ą£
32B
E3^87~
Oe;< 3 5 / Oe;<Í 3 6,7
A˜ı<::Ą£
32C
E3^87+
Oe;3 5,6 / Oe;Éï3 7
Ai<::Ą£
32D
E3^87+~
Oe;<3 5,6 / Oe;<Éï3 7
A˜ı<::Ą£
32E
E3^86
3:Oe;!3 5 / Oe;3 6
Ai<::Ć£
32F
E3^86~
3:Oe;<!3 5 / Oe;<3 6
A˜ı<::Ć£
330
E4~
Oe;<4
a˜ı4
A˜ı<:::
331
E4/~
Oe;<4 1−4 / Oe;<4 5−7 / Oe;<4 8
a´˜ı4
A´˜ı<:::
332
E4\~
Oe;<!4 1−7 / Oe;<4 8
a˜ı4/a˜ı¯4
A`˜ı<:::
333
E4^~
Oe;<4 1,3 / Oe;<Éï4 2 / Oe;<4 8
a`˜ı4
Aˆ˜ı<:::
334
E4/8~
Oe;<4 1−4 / Oe;<4 5−7
A˜ı<:::Ă£
335
E4\7~
Oe;<!4 1−4 / Oe;<4 5−7
A˜ı<:::Ă£
336
E4\6~
Oe;<!4 5 / Oe;<É4 6,7
A˜ı<:::Ă£
337
E4^98~
Oe;<4 1−4
A˜ı<:::Ą£
338
E4^97~
A˜ı<:::Ć£
339
E4^87~
Oe;< 4 5 / Oe;<Í 4 6,7
A˜ı<:::Ą£
33A
E4^87+~
Oe;<4 5,6 / Oe;<Éï4 7
A˜ı<:::Ą£
33B
E4^86~
3:Oe;<!4 5 / Oe;<4 6
A˜ı<:::Ć£
192
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
380
o1
A;ea1
˘o
o
381
o1~
A;ea<1
˜˘o
˜o
382
o1/
A;ea1 1−4 / A;ea1 5−7 / A;ea1 8
´˘o
´o
383
o1/~
A;ea<1 1−4 / A;ea<1 5−7 / A;ea<1 8
´˜˘o
´˜o
384
o1\
A;ea!1 1−7 / A;ea1 8
˘o/˘o¯
`o
385
o1\~
A;ea<!1 1−7 / A;ea<1 8
˜˘o/˜˘o¯
`˜o
386
o1^
A;ea1 1,3 / A;eaÉï1 2 / A;ea1 8
`˘o
ˆo
387
o1^~
A;ea<1 1,3 / A;ea<Éï1 2 / A;ea<1 8
`˜˘o
ˆ˜o
388
o1/8
A;ea1 1−4 / A;ea1 5−7
oĂ£
389
o1/8~
A;ea<1 1−4 / A;ea<1 5−7
˜oĂ£
38A
o1\7
A;ea!1 1−4 / A;ea1 5−7
oĂ£
38B
o1\7~
A;ea<!1 1−4 / A;ea<1 5−7
˜oĂ£
38C
o1\6
A;ea!1 5 / A;eaÉ1 6,7
oĂ£
38D
o1\6~
A;ea<!1 5 / A;ea<É1 6,7
˜oĂ£
38E
o1^98
A;ea1 1−4
oĄ£
38F
o1^98~
A;ea<1 1−4
˜oĄ£
390
o1^97
A;ea1! 1,4
oĆ£
391
o1^97~
A;ea<1! 1,4
˜oĆ£
392
o1^87
A;ea 1 5 / A;eaÍ 1 6,7
oĄ£
393
o1^87~
A;ea< 1 5 / A;ea<Í 1 6,7
˜oĄ£
394
o1^87+
A;ea1 5,6 / A;eaÉï1 7
oĄ£
395
o1^87+~
A;ea<1 5,6 / A;ea<Éï1 7
˜oĄ£
396
o1^86
3A;ea!1 5 / A;ea1 6
oĆ£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 193
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
397
o1^86~
3A;ea<!1 5 / A;ea<1 6
˜oĆ£
398
o
A;ea
o
o:
399
o~
A;ea<
˜o
˜o:
39A
o/
A;ea 1−4 / A;ea 5−7 / A;ea 8
´o
´o:
39B
o/~
A;ea< 1−4 / A;ea< 5−7 / A;ea< 8
´˜o
´˜o:
39C
o\
A;ea! 1−5 / A;eaÉ
6,7 / A;ea 8
o/o¯
`o:
39D
o\~
A;ea<! 1−5 / A;ea<É
6,7 / A;ea< 8
˜o/˜o¯
`˜o:
39E
o^
A;ea 1,3 / A;eaÉï
2 / A;ea 8
`o
ˆo:
39F
o^~
A;ea< 1,3 / A;ea<Éï
2 / A;ea< 8
`˜o
ˆ˜o:
3A0
o/8
A;ea 1−4 / A;ea 5−7
o:Ă£
3A1
o/8~
A;ea< 1−4 / A;ea< 5−7
˜o:Ă£
3A2
o\7
A;ea! 1−4 / A;ea 5−6 / A;eaÍ
7
o:Ă£
3A3
o\7~
A;ea<! 1−4 / A;ea< 5−6 / A;ea<Í
7
˜o:Ă£
3A4
o\6
A;ea! 5 / A;eaÉ
6,7
o:Ă£
3A5
o\6~
A;ea<! 5 / A;ea<É
6,7
˜o:Ă£
3A6
o^98
A;ea 1−4
o:Ą£
3A7
o^98~
A;ea< 1−4
˜o:Ą£
3A8
o^97
A;ea!3! 1,4
o:Ć£
3A9
o^97~
A;ea<!3! 1,4
˜o:Ć£
3AA
o^87
A;ea 5 / A;eaÍ
6,7
o:Ą£
3AB
o^87~
A;ea< 5 / A;ea<Í
6,7
˜o:Ą£
3AC
o^87+
A;ea 5,6 / A;eaÉï
7
o:Ą£
3AD
o^87+~
A;ea< 5,6 / A;ea<Éï
7
˜o:Ą£
194
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
3AE
o^86
3A;ea! 5 / A;ea 6
o:Ć£
3AF
o^86~
3A;ea<! 5 / A;ea< 6
˜o:Ć£
3B0
o3
A;ea3
o3
o::
3B1
o3~
A;ea<3
˜o3
˜o::
3B2
o3/
A;ea3 1−4 / A;ea3 5−7 / A;ea3 8
´o3
´o::
3B3
o3/~
A;ea<3 1−4 / A;ea<3 5−7 / A;ea<3 8
´˜o3
´˜o::
3B4
o3\
A;ea!3 1−7 / A;ea3 8
o3/o¯3
`o::
3B5
o3\~
A;ea<!3 1−7 / A;ea<3 8
˜o3/˜o¯3
`˜o::
3B6
o3^
A;ea3 1,3 / A;eaÉï3 2 / A;ea3 8
`o3
ˆo::
3B7
o3^~
A;ea<3 1,3 / A;ea<Éï3 2 / A;ea<3 8
`˜o3
ˆ˜o::
3B8
o3/8
A;ea3 1−4 / A;ea3 5−7
o::Ă£
3B9
o3/8~
A;ea<3 1−4 / A;ea<3 5−7
˜o::Ă£
3BA
o3\7
A;ea!3 1−4 / A;ea3 5−7
o::Ă£
3BB
o3\7~
A;ea<!3 1−4 / A;ea<3 5−7
˜o::Ă£
3BC
o3\6
A;ea!3 5 / A;eaÉ3 6,7
o::Ă£
3BD
o3\6~
A;ea<!3 5 / A;ea<É3 6,7
˜o::Ă£
3BE
o3^98
A;ea3 1−4
o::Ą£
3BF
o3^98~
A;ea<3 1−4
˜o::Ą£
3C0
o3^97
A;ea!3! 1,4
o::Ć£
3C1
o3^97~
A;ea<!3! 1,4
˜o::Ć£
3C2
o3^87
A;ea 3 5 / A;eaÍ 3 6,7
o::Ą£
3C3
o3^87~
A;ea< 3 5 / A;ea<Í 3 6,7
˜o::Ą£
3C4
o3^87+
A;ea3 5,6 / A;eaÉï3 7
o::Ą£
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 195
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
3C5
o3^87+~
A;ea<3 5,6 / A;ea<Éï3 7
˜o::Ą£
3C6
o3^86
3A;ea!3 5 / A;ea3 6
o::Ć£
3C7
o3^86~
3A;ea<!3 5 / A;ea<3 6
˜o::Ć£
3C8
o4~
A;ea<4
˜o4
˜o:::
3C9
o4/~
A;ea<4 1−4 / A;ea<4 5−7 / A;ea<4 8
´˜o4
´˜o:::
3CA
o4\~
A;ea<!4 1−7 / A;ea<4 8
˜o4/˜o¯4
`˜o:::
3CB
o4^~
A;ea<4 1,3 / A;ea<Éï4 2 / A;ea<4 8
`˜o4
ˆ˜o:::
3CC
o4/8~
A;ea<4 1−4 / A;ea<4 5−7
˜o:::Ă£
3CD
o4\7~
A;ea<!4 1−4 / A;ea<4 5−7
˜o:::Ă£
3CE
o4\6~
A;ea<!4 5 / A;ea<É4 6,7
˜o:::Ă£
3CF
o4^98~
A;ea<4 1−4
˜o:::Ą£
3D0
o4^97~
˜o:::Ć£
3D1
o4^87~
A;ea< 4 5 / A;ea<Í 4 6,7
˜o:::Ą£
3D2
o4^87+~
A;ea<4 5,6 / A;ea<Éï4 7
˜o:::Ą£
3D3
o4^86~
3A;ea<!4 5 / A;ea<4 6
˜o:::Ć£
400
O
A;Ea
au
5U
<:
401
O~
A;Ea<
a˜u
5˜U
<:
402
O/
A;Ea 1−4 / A;Ea 5−7 / A;Ea 8
a´u
5´U
<:
403
O/~
A;Ea< 1−4 / A;Ea< 5−7 / A;Ea< 8
a´˜u
5´˜U
<:
404
O\
A;Ea! 1−5 / A;EaÉ
6,7 / A;Ea 8
au/au¯
5`U
<:
405
O\~
A;Ea<! 1−5 / A;Ea<É
6,7 / A;Ea< 8
a˜u/a˜u¯
5`˜U
<:
406
O^
A;Ea 1,3 / A;EaÉï
2 / A;Ea 8
a`u
5ˆU
<:
407
O^~
A;Ea< 1,3 / A;Ea<Éï
2 / A;Ea< 8
a`˜u
5ˆ˜U
<:
196
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
408
O/8
A;Ea 1−4 / A;Ea 5−7
5U
<:Ă£
409
O/8~
A;Ea< 1−4 / A;Ea< 5−7
5˜U
<:Ă£
40A
O\7
A;Ea! 1−4 / A;Ea 5−6 / A;EaÍ
7
5U
<:Ă£
40B
O\7~
A;Ea<! 1−4 / A;Ea< 5−6 / A;Ea<Í
7
5˜U
<:Ă£
40C
O\6
A;Ea! 5 / A;EaÉ
6,7
5U
<:Ă£
40D
O\6~
A;Ea<! 5 / A;Ea<É
6,7
5˜U
<:Ă£
40E
O^98
A;Ea 1−4
5U
<:Ą£
40F
O^98~
A;Ea< 1−4
5˜U
<:Ą£
410
O^97
A;Ea!3! 1,4
5U
<:Ć£
411
O^97~
A;Ea<!3! 1,4
5˜U
<:Ć£
412
O^87
A;Ea 5 / A;EaÍ
6,7
5U
<:Ą£
413
O^87~
A;Ea< 5 / A;Ea<Í
6,7
5˜U
<:Ą£
414
O^87+
A;Ea 5,6 / A;EaÉï
7
5U
<:Ą£
415
O^87+~
A;Ea< 5,6 / A;Ea<Éï
7
5˜U
<:Ą£
416
O^86
3A;Ea! 5 / A;Ea 6
5U
<:Ć£
417
O^86~
3A;Ea<! 5 / A;Ea< 6
5˜U
<:Ć£
418
O3
A;Ea3
au3
Au
<::
419
O3~
A;Ea<3
a˜u3
A˜u
<::
41A
O3/
A;Ea3 1−4 / A;Ea3 5−7 / A;Ea3 8
a´u3
A´u
<::
41B
O3/~
A;Ea<3 1−4 / A;Ea<3 5−7 / A;Ea<3 8
a´˜u3
A´˜u
<::
41C
O3\
A;Ea!3 1−7 / A;Ea3 8
au3/au¯3
A`u
<::
41D
O3\~
A;Ea<!3 1−7 / A;Ea<3 8
a˜u3/a˜u¯3
A`˜u
<::
41E
O3^
A;Ea3 1,3 / A;EaÉï3 2 / A;Ea3 8
a`u3
Aˆu
<::
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 197
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
41F
O3^~
A;Ea<3 1,3 / A;Ea<Éï3 2 / A;Ea<3 8
a`˜u3
Aˆ˜u
< ::
420
O3/8
A;Ea3 1−4 / A;Ea3 5−7
Au
< ::Ă£
421
O3/8~
A;Ea<3 1−4 / A;Ea<3 5−7
A˜u
< ::Ă£
422
O3\7
A;Ea!3 1−4 / A;Ea3 5−7
Au
< ::Ă£
423
O3\7~
A;Ea<!3 1−4 / A;Ea<3 5−7
A˜u
< ::Ă£
424
O3\6
A;Ea!3 5 / A;EaÉ3 6,7
Au
<::Ă£
425
O3\6~
A;Ea<!3 5 / A;Ea<É3 6,7
A˜u
<::Ă£
426
O3^98
A;Ea3 1−4
Au
<::Ą£
427
O3^98~
A;Ea<3 1−4
A˜u
<::Ą£
428
O3^97
A;Ea!3! 1,4
Au
<::Ć£
429
O3^97~
A;Ea<!3! 1,4
A˜u
<::Ć£
42A
O3^87
A;Ea 3 5 / A;EaÍ 3 6,7
Au
<::Ą£
42B
O3^87~
A;Ea< 3 5 / A;Ea<Í 3 6,7
A˜u
<::Ą£
42C
O3^87+
A;Ea3 5,6 / A;EaÉï3 7
Au
<::Ą£
42D
O3^87+~
A;Ea<3 5,6 / A;Ea<Éï3 7
A˜u
<::Ą£
42E
O3^86
3A;Ea!3 5 / A;Ea3 6
Au
<::Ć£
42F
O3^86~
3A;Ea<!3 5 / A;Ea<3 6
A˜u
<::Ć£
430
O4~
A;Ea<4
a˜u4
A˜u
<:::
431
O4/~
A;Ea<4 1−4 / A;Ea<4 5−7 / A;Ea<4 8
a´˜u4
A´˜u
<:::
432
O4\~
A;Ea<!4 1−7 / A;Ea<4 8
a˜u4/a˜u¯4
A`˜u
<:::
433
O4^~
A;Ea<4 1,3 / A;Ea<Éï4 2 / A;Ea<4 8
a`˜u4
Aˆ˜u
<:::
434
O4/8~
A;Ea<4 1−4 / A;Ea<4 5−7
A˜u
< :::Ă£
435
O4\7~
A;Ea<!4 1−4 / A;Ea<4 5−7
A˜u
< :::Ă£
198
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
436
O4\6~
A;Ea<!4 5 / A;Ea<É4 6,7
A˜u
<:::Ă£
437
O4^98~
A;Ea<4 1−4
A˜u
<:::Ą£
438
O4^97~
A˜u
<:::Ć£
439
O4^87~
A;Ea< 4 5 / A;Ea<Í 4 6,7
A˜u
<:::Ą£
43A
O4^87+~
A;Ea<4 5,6 / A;Ea<Éï4 7
A˜u
<:::Ą£
43B
O4^86~
3A;Ea<!4 5 / A;Ea<4 6
A˜u
<:::Ć£
480
k
k,
k
k
481
k!
k,
k
k^
482
k~
k, <
˜k
kn
483
K
K,a
kh
kh
484
K!
K,a
kh
kh^
485
K~
K,a<
k˜h
khn
486
g
g,a
g
g
487
g!
g,a
g
g^
488
g~
g,a<
˜g
gn
489
G
;G,a
gh
gh
48A
G!
;G,a
gh
gh^
48B
G~
;G,a<
g˜h
ghn
48C
N
.z,
˙n
N
48D
N!
.z,
˙n
N^
48E
c
.c,a
c
c
48F
c!
.c,a
c
c^
490
c~
.c,a<
˜c
cn
491
C
C,
ch
ch
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 199
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
492
C!
C,
ch
ch^
493
C~
C, <
c˜h
chn
494
j
.j,a
j
é
495
j!
.j,a
j
é^
496
j~
.j,a<
˜j
én
497
J
J,a
jh
éh
498
J!
J,a
jh
éh^
499
J~
J,a<
j˜h
éhn
49A
Y
V,a
ñ
ñ
49B
Y!
V,a
ñ
ñ^
49C
w
f,
t.
ú
49D
w!
f,
t.
ú^
49E
w~
f, <
˜t.
ún
49F
W
F,
t.h
úh
4A0
W!
F,
t.h
úh^
4A1
W~
F, <
t.˜h
úhn
4A2
q
.q,
d.
ã
4A3
q!
.q,
d.
ã^
4A4
q~
.q, <
˜d.
ãn
4A5
L
L,
l.
ó
4A6
Q
Q,
d.h
ãh
4A7
Q!
Q,
d.h
ãh^
4A8
Q~
Q, <
d. ˜h
ãhn
4A9
|
\h,
l.h
óh
200
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
4AA
R
:N,a
n.
ï
4AB
R!
:N,a
n.
ï^
4AC
t
t,a
t
t”
4AD
t!
t,a
t
t”^
4AE
t~
t,a<
˜t
t”n
4AF
T
T,a
th
t”h
4B0
T!
T,a
th
t”h^
4B1
T~
T,a<
t˜h
t”hn
4B2
d
d,
d
d”
4B3
d!
d,
d
d”^
4B4
d~
d, <
˜d
d”n
4B5
D
;D,a
dh
d”h
4B6
D!
;D,a
dh
d”h^
4B7
D~
;D,a<
d˜h
d”hn
4B8
n
n,a
n
n”
4B9
n!
n,a
n
n”^
4BA
p
:p,a
p
p
4BB
p!
:p,a
p
p^
4BC
p~
:p,a<
˜p
pn
4BD
P
:P,
ph
ph
4BE
P!
:P,
ph
ph^
4BF
P~
:P, <
p˜h
phn
4C0
b
b,a
b
b
4C1
b!
b,a
b
b^
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 201
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
4C2
b~
b,a<
˜b
bn
4C3
B
B,a
bh
bh
4C4
B!
B,a
bh
bh^
4C5
B~
B,a<
b˜h
bhn
4C6
m
m,a
m
m
4C7
m!
m,a
m
m^
4C8
y
y,a
y
j
4C9
y_
y, ,a
y
éJ<
4CA
y=
y,a
y
4CB
y!
y,a
y
j^
4CC
y~
y<,a
˜y
j˜
4CD
r
.=,
r
õ
4CE
l
,a
l
l”
4CF
l!
,a
l
l”^
4D0
l~
< ,a
˜l
˜l”
4D1
v
v,a
v
w
4D2
v_
ëëÁ+;a,
v
B
4D3
v=
v,a
v
4D4
v!
v,a
v
w^
4D5
v~
v<.,a
˜v
˜w
4D6
S
Z,a
´s
ç
4D7
z
:S,a
s.
ù
4D8
s
.s,a
s
s”
4D9
h
h,
h
H
202
APPENDICES
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
4DA
h~
h, <
˜h
Hn
4DB
H
H
h.
h
4DC
H/8
HÙ 2,5
4DD
H\7
ôH 2
4DE
H\6
ôH 5
4DF
H^98
H- 2
4E0
H^87
H- 5
4E1
Z
^
h¯
x
4E2
V
^
hˇ
F
4E3
M
M/` 9
˙m
4E4
M#
कM 2
4E5
M#/8
कM 2
4E6
M#\7
कM! 2
4E7
M#\6
4E8
M1
><
3
4E9
M1/8
><
3
4EA
M1\7
><! 3
4EB
M1\6
4EC
M1#
घ2
4ED
M1#/8
घ2
4EE
M1#\7
घ! 2
4EF
M1#\6
4F0
M2
> 3
4F1
M2/8
> 3
APPENDIX C: SANSKRIT LIBRARY PHONETIC SEGMENTAL 203
SLP2
SLP1
DEVAN ¯AGAR¯I
ROMAN
IPA
4F2
M2\7
>! 3
4F3
M2\6
204
APPENDICES
Appendix D
Sanskrit Library Phonetic
Featural
The Sanskrit Library Phonetic Featural encoding scheme (SLP3) creates
a correspondence between codepoints numbered 1-242, selected SLP1
segments, and their features. Each SLP1 segment is associated with nine-
teen features each of which is assigned a value of plus, minus, or neutral.
The latter applies if the feature is inapplicable to the segment in ques-
tion. In addition true diphthongs are assigned pairs of featural values,
one for each of the two constituent sounds. The SLP3 encoding is based
upon phonetic features as described by Halle and shown in Table 4. In
terms of the three axes of encoding described in Chapter 4, SLP3 encodes
phonetics rather than graphics, and contrastive rather than complemen-
tary units. Although it encodes segments, these are explicitly associated
with sets of features, each of which could be assigned a codepoint. Each
segment could then be associated with sets of featural codepoints in a
consistent and unambiguous featural encoding scheme. We have chosen
instead to represent SLP3 in terms of phonetic segments associated with
sets of phonetic features.
In column 1 the unique codepoints of SLP3 are shown in decimal no-
tation. In column 2 the equivalent encoding in SLP1 is given. In columns
3 through 21 the value for each of nineteen features in Halle’s system are
given. Row four of the table header indicates terminal features. Rows
205
206
APPENDICES
one through three of the header show higher nodes in Halle’s feature tree
as shown in Table 12. ‘GUTTRL’ stands for GUTTERAL, ‘SPal’ and
‘spal’ for soft palate, and ‘tblade’ for tongue blade. The abbreviations
shown in columns 3-21 in row four of the table header are given in the
following table:
G
glottal
Sp
spread glottis
St
stiff vocal folds
Sl
slack vocal folds
R
rhinal
N
nasal
Dr
dorsal
B
back
H
high
L
low
Cr
coronal
A
anterior
Dt
distributed
Lb
labial
Rd
round
Cn
consonantal
Sn
sonorant
Ct
continuant
Lt
lateral
APPENDIX D: SANSKRIT LIBRARY PHONETIC FEATURAL
207
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
1 000 a
−−−
−+ +
−
+
−
2 001 a~
−−−
+ + +
−
+
−
3 002 a/
−+ −
−+ +
−
+
−
4 003 a/~
−+ −
+ + +
−
+
−
5 004 a\
−−+
−+ +
−
+
−
6 005 a\~
−−+
+ + +
−
+
−
7 006 a^
−+ +
−+ +
−
+
−
8 007 a^~
−+ +
+ + +
−
+
−
9 030 A
−−−
−+ +
−
+
−
10 031 A~
−−−
+ + +
−
+
−
11 032 A/
−+ −
−+ +
−
+
−
12 033 A/~
−+ −
+ + +
−
+
−
13 034 A\
−−+
−+ +
−
+
−
14 035 A\~
−−+
+ + +
−
+
−
15 036 A^
−+ +
−+ +
−
+
−
16 037 A^~
−+ +
+ + +
−
+
−
17 048 a3
−−−
−+ +
−
+
−
18 049 a3~
−−−
+ + +
−
+
−
19 04A a3/
−+ −
−+ +
−
+
−
20 04B a3/~
−+ −
+ + +
−
+
−
21 04C a3\
−−+
−+ +
−
+
−
22 04D a3\~
−−+
+ + +
−
+
−
23 04E a3^
−+ +
−+ +
−
+
−
24 04F a3^~
−+ +
+ + +
−
+
−
25 080 i
−−−
−+ −
+
−
−
26 081 i~
−−−
+ + −
+
−
−
27 082 i/
−+ −
−+ −
+
−
−
28 083 i/~
−+ −
+ + −
+
−
−
29 084 i\
−−+
−+ −
+
−
−
30 085 i\~
−−+
+ + −
+
−
−
31 086 i^
−+ +
−+ −
+
−
−
32 087 i^~
−+ +
+ + −
+
−
−
33 0B0 I
−−−
−+ −
+
−
−
208
APPENDICES
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
34 0B1 I~
−−−
+ + −
+
−
−
35 0B2 I/
−+ −
−+ −
+
−
−
36 0B3 I/~
−+ −
+ + −
+
−
−
37 0B4 I\
−−+
−+ −
+
−
−
38 0B5 I\~
−−+
+ + −
+
−
−
39 0B6 I^
−+ +
−+ −
+
−
−
40 0B7 I^~
−+ +
+ + −
+
−
−
41 0C8 i3
−−−
−+ −
+
−
−
42 0C0 i3~
−−−
+ + −
+
−
−
43 0CA i3/
−+ −
−+ −
+
−
−
44 0CB i3/~
−+ −
+ + −
+
−
−
45 0CC i3\
−−+
−+ −
+
−
−
46 0CD i3\~
−−+
+ + −
+
−
−
47 0CE i3^
−+ +
−+ −
+
−
−
48 0CF i3^~
−+ +
+ + −
+
−
−
49 100 u
−−−
−+ +
+
−
+ +
−
50 101 u~
−−−
+ + +
+
−
+ +
−
51 102 u/
−+ −
−+ +
+
−
+ +
−
52 103 u/~
−+ −
+ + +
+
−
+ +
−
53 104 u\
−−+
−+ +
+
−
+ +
−
54 105 u\~
−−+
+ + +
+
−
+ +
−
55 106 u^
−+ +
−+ +
+
−
+ +
−
56 107 u^~
−+ +
+ + +
+
−
+ +
−
57 130 U
−−−
−+ +
+
−
+ +
−
58 131 U~
−−−
+ + +
+
−
+ +
−
59 132 U/
−+ −
−+ +
+
−
+ +
−
60 133 U/~
−+ −
+ + +
+
−
+ +
−
61 134 U\
−−+
−+ +
+
−
+ +
−
62 135 U\~
−−+
+ + +
+
−
+ +
−
63 136 U^
−+ +
−+ +
+
−
+ +
−
64 137 U^~
−+ +
+ + +
+
−
+ +
−
65 148 u3
−−−
−+ +
+
−
+ +
−
66 149 u3~
−−−
+ + +
+
−
+ +
−
APPENDIX D: SANSKRIT LIBRARY PHONETIC FEATURAL
209
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
67 14A u3/
−+ −
−+ +
+
−
+ +
−
68 14B u3/~
−+ −
+ + +
+
−
+ +
−
69 14C u3\
−−+
−+ +
+
−
+ +
−
70 14D u3\~
−−+
+ + +
+
−
+ +
−
71 14E u3^
−+ +
−+ +
+
−
+ +
−
72 14F u3^~
−+ +
+ + +
+
−
+ +
−
73 180 f
−−−
−
−
74 181 f~
−−−
+
−
75 182 f/
−+ −
−
−
76 183 f/~
−+ −
+
−
77 184 f\
−−+
−
−
78 185 f\~
−−+
+
−
79 186 f^
−+ +
−
−
80 187 f^~
−+ +
+
−
81 1B0 F
−−−
−
−
82 1B1 F~
−−−
+
−
83 1B2 F/
−+ −
−
−
84 1B3 F/~
−+ −
+
−
85 1B4 F\
−−+
−
−
86 1B5 F\~
−−+
+
−
87 1B6 F^
−+ +
−
−
88 1B7 F^~
−+ +
+
−
89 1C8 f3
−−−
−
−
90 1C9 f3~
−−−
+
−
91 1CA f3/
−+ −
−
−
92 1CB f3/~
−+ −
+
−
93 1CC f3\
−−+
−
−
94 1CD f3\~
−−+
+
−
95 1CE f3^
−+ +
−
−
96 1CF f3^~
−+ +
+
−
97 200 x
−−−
−
−
98 201 x~
−−−
+
−
99 202 x/
−+ −
−
−
210
APPENDICES
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
100 203 x/~
−+ −
+
−
101 204 x\
−−+
−
−
102 205 x\~
−−+
+
−
103 206 x^
−+ +
−
−
104 207 x^~
−+ +
+
−
105 230 X
−−−
−
−
106 231 X~
−−−
+
−
107 232 X/
−+ −
−
−
108 233 X/~
−+ −
+
−
109 234 X\
−−+
−
−
110 235 X\~
−−+
+
−
111 236 X^
−+ +
−
−
112 237 X^~
−+ +
+
−
113 248 x3
−−−
−
−
114 249 x3~
−−−
+
−
115 24A x3/
−+ −
−
−
116 24B x3/~
−+ −
+
−
117 24C x3\
−−+
−
−
118 24D x3\~
−−+
+
−
119 24E x3^
−+ +
−
−
120 24F x3^~
−+ +
+
−
121 280 e1
−−−
−+ −
−
−
−
122 281 e1~
−−−
+ + −
−
−
−
123 282 e1/
−+ −
−+ −
−
−
−
124 283 e1/~
−+ −
+ + −
−
−
−
125 284 e1\
−−+
−+ −
−
−
−
126 285 e1\~
−−+
+ + −
−
−
−
127 286 e1^
−+ +
−+ −
−
−
−
128 287 e1^~
−+ +
+ + −
−
−
−
129 298 e
−−−
−+ −
−
−
−
130 299 e~
−−−
+ + −
−
−
−
131 29A e/
−+ −
−+ −
−
−
−
132 29B e/~
−+ −
+ + −
−
−
−
APPENDIX D: SANSKRIT LIBRARY PHONETIC FEATURAL
211
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
133 29C e\
−−+
−+ −
−
−
−
134 29D e\~
−−+
+ + −
−
−
−
135 29E e^
−+ +
−+ −
−
−
−
136 29F e^~
−+ +
+ + −
−
−
−
137 2B0 e3
−−−
−+ −
−
−
−
138 2B1 e3~
−−−
+ + −
−
−
−
139 2B2 e3/
−+ −
−+ −
−
−
−
140 2B3 e3/~
−+ −
+ + −
−
−
−
141 2B4 e3\
−−+
−+ −
−
−
−
142 2B5 e3\~
−−+
+ + −
−
−
−
143 2B6 e3^
−+ +
−+ −
−
−
−
144 2B7 e3^~
−+ +
+ + −
−
−
−
145 300 E
−−−
−+ +/−−/+ +/−
−
146 301 E~
−−−
+ + +/−−/+ +/−
−
147 302 E/
−+ −
−+ +/−−/+ +/−
−
148 303 E/~
−+ −
+ + +/−−/+ +/−
−
149 304 E\
−−+
−+ +/−−/+ +/−
−
150 305 E\~
−−+
+ + +/−−/+ +/−
−
151 306 E^
−+ +
−+ +/−−/+ +/−
−
152 307 E^~
−+ +
+ + +/−−/+ +/−
−
153 318 E3
−−−
−+ +/−−/+ +/−
−
154 319 E3~
−−−
+ + +/−−/+ +/−
−
155 31A E3/
−+ −
−+ +/−−/+ +/−
−
156 31B E3/~
−+ −
+ + +/−−/+ +/−
−
157 31C E3\
−−+
−+ +/−−/+ +/−
−
158 31D E3\~
−−+
+ + +/−−/+ +/−
−
159 31E E3^
−+ +
−+ +/−−/+ +/−
−
160 31F E3^~
−+ +
+ + +/−−/+ +/−
−
161 380 o1
−−−
−+ +
−
−
+ +
−
162 381 o1~
−−−
+ + +
−
−
+ +
−
163 382 o1/
−+ −
−+ +
−
−
+ +
−
164 383 o1/~
−+ −
+ + +
−
−
+ +
−
165 384 o1\
−−+
−+ +
−
−
+ +
−
212
APPENDICES
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
166 385 o1\~
−−+
+ + +
−
−
+ +
−
167 386 o1^
−+ +
−+ +
−
−
+ +
−
168 387 o1^~
−+ +
+ + +
−
−
+ +
−
169 398 o
−−−
−+ +
−
−
+ +
−
170 399 o~
−−−
+ + +
−
−
+ +
−
171 39A o/
−+ −
−+ +
−
−
+ +
−
172 39B o/~
−+ −
+ + +
−
−
+ +
−
173 39C o\
−−+
−+ +
−
−
+ +
−
174 39D o\~
−−+
+ + +
−
−
+ +
−
175 39E o^
−+ +
−+ +
−
−
+ +
−
176 39F o^~
−+ +
+ + +
−
−
+ +
−
177 3B0 o3
−−−
−+ +
−
−
+ +
−
178 3B1 o3~
−−−
+ + +
−
−
+ +
−
179 3B2 o3/
−+ −
−+ +
−
−
+ +
−
180 3B3 o3/~
−+ −
+ + +
−
−
+ +
−
181 3B4 o3\
−−+
−+ +
−
−
+ +
−
182 3B5 o3\~
−−+
+ + +
−
−
+ +
−
183 3B6 o3^
−+ +
−+ +
−
−
+ +
−
184 3B7 o3^~
−+ +
+ + +
−
−
+ +
−
185 400 O
−−−
−+ +/+ −/+ +/−
+ +
−
186 401 O~
−−−
+ + +/+ −/+ +/−
+ +
−
187 402 O/
−+ −
−+ +/+ −/+ +/−
+ +
−
188 403 O/~
−+ −
+ + +/+ −/+ +/−
+ +
−
189 404 O\
−−+
−+ +/+ −/+ +/−
+ +
−
190 405 O\~
−−+
+ + +/+ −/+ +/−
+ +
−
191 406 O^
−+ +
−+ +/+ −/+ +/−
+ +
−
192 407 O^~
−+ +
+ + +/+ −/+ +/−
+ +
−
193 418 O3
−−−
−+ +/+ −/+ +/−
+ +
−
194 419 O3~
−−−
+ + +/+ −/+ +/−
+ +
−
195 41A O3/
−+ −
−+ +/+ −/+ +/−
+ +
−
196 41B O3/~
−+ −
+ + +/+ −/+ +/−
+ +
−
197 41C O3\
−−+
−+ +/+ −/+ +/−
+ +
−
198 41D O3\~
−−+
+ + +/+ −/+ +/−
+ +
−
APPENDIX D: SANSKRIT LIBRARY PHONETIC FEATURAL
213
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
199 41E O3^
−+ +
−+ +/+ −/+ +/−
+ +
−
200 41F O3^~
−+ +
+ + +/+ −/+ +/−
+ +
−
201 480 k
−+ −
−+
+
−−
202 483 K
+ + −
−+
+
−−
203 486 g
−−+
−+
+
−−
204 489 G
+ −+
−+
+
−−
205 48C N
−−+
+ +
+
+
−
206 48E c
−+ −
−
+ −+
+
−−
207 491 C
+ + −
−
+ −+
+
−−
208 494 j
−−+
−
+ −+
+
−−
209 497 J
+ −+
−
+ −+
+
−−
210 49A Y
−−+
+
+ −+
+
+
−
211 49C w
−+ −
−
+ −−
+
−−
212 49F W
+ + −
−
+ −−
+
−−
213 4A2 q
−−+
−
+ −−
+
−−
214 4A5 L
−−+
−
+ −−
+
+
+
215 4A6 Q
+ −+
−
+ −−
+
−−
216 4A9 |
+ −+
−
+ −−
+
+
+
217 4AA R
−−+
+
+ −−
+
+
−
218 4AC t
−+ −
−
+ +
+
−−
219 4AF T
+ + −
−
+ +
+
−−
220 4B2 d
−−+
−
+ +
+
−−
221 4B5 D
+ −+
−
+ +
+
−−
222 4B8 n
−−+
+
+ +
+
+
−
223 4BA p
−+ −
−
+ −
+
−−
224 4BD P
+ + −
−
+ −
+
−−
225 4C0 b
−−+
−
+ −
+
−−
226 4C3 B
+ −+
−
+ −
+
−−
227 4C6 m
−−+
+
+ −
+
+
−
228 4C8 y
−−+
−
−+
−
229 4CC y~
−−+
+
−+
−
230 4CD r
−−+
−
+ −−
+
+
−
231 4CE l
−−+
−
+ +
+
+
+
214
APPENDICES
GUTTRL
PLACE
Larynx
SPal
Dorsal
Coronal Labial
glottis
spal
tongue body
tblade
lips
SLP3 SLP2 SLP1 G Sp St Sl R N Dl B
H
L
Cr A Dt Lb Rd Cn Sn Ct Lt
232 4D0 l~
−−+
+
+ +
+
+
+
233 4D1 v
−−+
−
+ +
−
234 4D5 v~
−−+
+
+ +
−
235 4D6 S
+ + −
−
+ −+
+
−+
236 4D7 z
+ + −
−
+ −−
+
−+
237 4D8 s
+ + −
−
+ +
+
−+
238 4D9 h
+ + −+
−
−
239 4DB H
+ + + −
−
−
240 4E1 Z
+ + −
−+
+
−+
241 4E2 V
+ + −
−
+ −
+
−+
242 4E3 M
+ −+ + +
−
Appendix E
Malcolm D. Hyman
12 November 1970 – 2 September 2009
E.1
A Memoir by Phoebe Pettingell
Malcolm could truthfully say, in the words of the John Cougar Mellen-
camp song, “I was born in a small town.” It seems ironic that some-
one who became so much at home in the global intellectual community
should have grown up in an isolated village in Northern Wisconsin – in
the midst of the largest expanse of virgin timber in the United States. But
perhaps the irony diminishes when one realizes that this part of Wiscon-
sin is home to a diverse group of cultures, including three major Native
Americans nations, immigrants from Middle and Eastern Europe, Scan-
dinavia and the Balkans, Laos, Vietnam and Cambodia. Malcolm’s own
heritage was diverse. His father, the late literary critic, Stanley Edgar
Hyman was descended from a Lithuanian rabbinic dynasty. My own
family was predominantly Scottish, with one German great grandmother.
The closeness of a small town that nonetheless possesses such diversity
shaped Malcolm profoundly. Wherever he lived, he thought of Three
Lakes as home.
His growing up there had not been anticipated. Stanley taught at
Bennington College in Vermont. As writers, we both spent time in New
York City, and lately had been living in Europe and England. However,
Stanley’s unexpected death three months before Malcolm’s birth moti-
vated me to join my mother at our former summer home in Three Lakes
215
216
APPENDICES
where she had been living permanently for several years. The atmosphere
seemed congenial for the raising of a fatherless child, and we cooperated
in his upbringing as long as he lived at home. Malcolm was rather shy
as a child, though in college he became much more extroverted. From
the beginning, he was deeply compassionate, with a respect for all living
things. One could not so much as swat a mosquito in his presence. He
was also a natural leader, one whose inﬂuence sprang from his generos-
ity toward others and his having thought through what he had to say. All
his life, Malcolm was his ideas, which, in turn, were imbued with his
passionate convictions about the moral worth of creation.
Malcolm began talking late – he spoke a private language until kinder-
garten (this tendency ran in the male line in my family) which, in his case,
may have inﬂuenced his fascination with grammar, syntax and language
in general. Within a few months of entering ﬁrst grade, he was read-
ing on an adult level. One day, he mentioned the schwa to me. When
I expressed ignorance, he asked with genuine surprise, “Don’t you pay
attention to the diacritical marks in the dictionary? In second grade, he
brought home a book from the music library and, in a weekend, taught
himself to read both treble and bass clef, not to mention alto and tenor.
Shortly thereafter, he asked to take piano lessons, which he continued
throughout high school. His musical gifts were signiﬁcant enough to
contemplate a career as a pianist or composer. By this time, he was
spending every weekend in a city eighty miles from our home, working
with a piano coach and studying harmony and composition.
He also brought home grammar text books throughout school, pour-
ing over them and sometimes pointing out mistakes in the author’s rea-
soning. At eleven, having never laid hands on a computer, he bought two
books on programming. The following Monday, he walked into the high
school computer lab and asked the teacher if he might try something. He
then wrote a program that surpassed the teacher’s skills. That summer,
he enrolled in a graduate level computer course at The University of Wis-
consin at LaCrosse. A year later, he began to attend the summer sessions
in computing at Michigan Tech, where professors often asked him to as-
sist in teaching the other students. At twelve, he was running his own
software company, creating programs for local businesses.
Wisconsin devotes many of its resources to education from the pri-
mary grades through its excellent state university system, and the Three
APPENDIX E: MALCOLM D. HYMAN
217
Lakes school offered a particularly ﬁne education, especially in the sci-
ences. The teacher in charge of physics and advanced math courses had
worked at the Fermi Lab. Everyone assumed Malcolm would choose to
major in some branch of the sciences once he went to college, or else
follow a musical career. However, he was fascinated by a wide range of
ﬁelds. From age seven, he had won national children’s poetry contests
again and again. He proved to be quick at picking up languages – a gift
from his rabbinic ancestors, but also from his grandmother who contin-
ued to teach herself new ones well into her 80s. By the time he applied
to universities, Malcolm’s interests had expanded to philosophy and the-
ology. He had also fallen under the spell of James Joyce’s A Portrait
of the Artist as a Young Man, and imagined attending Trinity College
in Dublin, Ireland, at some point. Knowing that this would require a
background in Ancient Greek and Latin, at the last moment, he started
entering his prospective major as Classics, and took a crash course in
Latin with a local Episcopal priest. He ended up at Lawrence Univer-
sity in Appleton Wisconsin. They offered him a Merit Scholarship, and
later awarded him the Wriston Fellowship on Academic merit. There,
he met Professor Daniel J. Taylor, a scholar of the Roman grammarian
and polymath, Marcus Terentius Varro (116-27 BCE). Dan became his
mentor and friend, inﬂuencing the direction of his future academic ca-
reer. Malcolm made the most of his college years, attending almost ev-
ery lecture on campus, in addition to his course work, and making lasting
friendships. The ﬁrst semester of his senior year was spent at the Center
for Classical Studies in Rome. In 1993, Malcolm graduated summa cum
laude, the top student in his class.
Back at Lawrence, Malcolm had fallen under the spell of Martha
Nussbaum when he read her The Fragility of Goodness. This inﬂuenced
his decision to enter the Ph.D. program in Classics at Brown University in
Providence, Rhode Island. An added incentive was that Dr. William Wy-
att, Dan Taylor’s own mentor, also taught in the department. With Nuss-
baum, Malcolm was able to pursue his interests in philosophy and ethics,
while with Wyatt he continued to indulge his fascination with linguistic
structures. With his colleague, Philip Thibodeau, he published several
short papers. Over one summer, he took an intensive course in Sanskrit
at Harvard, and while at Brown studied Akkadian. Though he never took
a computer course after high school, his skills were such that he designed
218
APPENDICES
and maintained the highly sophisticated web site for the Brown Classics
Department, and picked up design tips from the Rhode Island School of
Design, next door. Some intellects keep their various interests in sep-
arate compartments. Malcolm, however, saw the relationships between
different disciplines, and his vast knowledge in one area illuminated his
understanding of others. His thirst for knowledge continued to expand as
long as he lived. He read voraciously in literature, philosophy, psychol-
ogy, history and the sciences. Popular culture was a longtime fascination
for him, and music remained close to his heart.
Malcolm’s dissertation concerned the way Latin grammarians treated
barbarisms and solecisms. His ﬁrst signiﬁcant published paper, “Bad
Grammar in Context,” deﬁned his philosophy in this regard: Let me con-
clude by sketching the “big picture,” as I see it. Language is constitu-
itive of institutions – such as religion and law – that serve to produce
social cohesion. Given that spoken and written language are the media
par excellence for communication, the importance of linguistic norms
in maintaining group identity should be evident. Conservatism in lan-
guage preserves the social status quo. But society is not a static entity;
it must adjust continually to changing situations and modes of living.
Revolutionary movements (such as Stoicism and early Christianity) aim
toward an upheaval of traditional institutions; and so it is not surprising
to see their depreciation of the prescriptive stance of the grammarians.
These two linguistic attitudes – the prescriptive and the anti-prescriptive
– exist in a dynamic that shapes, at any historical moment, the form of
cultural life. Malcolm’s own sympathies were generally against the pre-
scriptivists, especially when their purpose was to deﬁne class barriers.
Having grown up among people who worked with their hands, he fought
the kind of genteel grammatical notions that look down on what they
perceive as uneducated speech.
At the same time, he was intrigued with the ways in which culture
is transmitted in writing, even when the writing does not communicate
in conventional ways. His paper, “Of Glyphs and Glottography,” written
during his productive years at the Max Planck Institute for the History of
Science in Berlin, examines proto-writing and the connection between
written and spoken language. It begins with a typically whimsical epi-
graph, from Popeye the Sailor Man: “This writin’ is wroten rotten, if
you happen to ask me,” and observes, It is ... evident that writing that
APPENDIX E: MALCOLM D. HYMAN
219
is (or purports to be) glottographic may serve – as we learn from Greek
nonsense inscriptions on vases or Japanese T-shirts with messages in du-
bious English (or non-English) – other functions: e.g. to communicate
prestige directly or to connote cultural capital. Even writing that straight-
forwardly notates spoken language is overdetermined, in the sense that
it can perform other functions besides. The paper goes on to point out
that linguists and philologists tend to pay most attention to literary arti-
facts, whereas “calendars, tables of sines and cosines, architectural plans,
recipes for foods and drugs, mathematical formulae, coins and bank-
notes, charts for navigation, computer programs – reﬂect highly sophisti-
cated intellectual activity and serve as indispensable bearers of culture.”
Malcolm’s post-graduate career included positions at Harvard and
Brown as a research fellow, and at the Max Planck Institute in their His-
tory of Science department. In the words of Dr. Jürgen Renn, the head of
that department, Malcolm “was always there to give advice, to help out,
to stimulate new ideas, or to clear the atmosphere with a subtle joke.” His
work led him more and more into computer programming as it pertained
to making the worldwide Web more useful for scholars. As he pointed
out, “Browsing the Web is scarcely more interactive than surﬁng televi-
sion channels.” He envisioned “not a browser but an interagent.” His
“Arboreal” program, developed in conjunction with the Max Planck Isti-
tute, and used for the 2005 exhibition, “Albert Einstein: Chief Engineer
of the Universe,” as well as in his groundbreaking Sanskrit web projects
with his Brown colleague and close friend, Dr. Peter Scharf, were two
examples of his multiverse efforts to make the web ever more useful for
intellectual pursuits. He and Dr. Renn envisioned a new epistemic Web:
“Is it enough to create a digital library of Alexandria, with (perhaps) im-
proved ﬁnding aids? We propose that the crucial question is how to struc-
ture knowledge on the Web to facilitate the construction of new knowl-
edge, knowledge that will be critical in addressing the challenges of the
emerging global society.” Malcolm’s work in Sanskrit on the web with
Peter Scharf of Brown and with scholarly web programs with Dr. Mark
Schifsky of Harvard continued to push these boundaries. But his primary
interest in computing related to his fascination with linguistics itself and
with human communication. Increasingly, he attempted to devise new
models of thought for the various ﬁelds in which he worked: History
of Science, Linguistics, Classics and Ancient Sumerian languages, and
220
APPENDICES
Information Science.
It would seem that already Malcolm had set the course of a produc-
tive and happy life. He rejoiced in his many friends and colleagues who
helped sustain his own productivity and with whom he was invariably
and selﬂessly generous. In 2006, he married Dr. Ludmila Selemeneva,
a Russian specialist in rhetoric, and on December 2, 2008, their son,
Stanley William Hyman was born in Berlin. Malcolm was looking for-
ward to dividing his time between there and Providence where his work
at Brown had expanded. Yet he had always lived with such intensity
and drive that periodically he succumbed to the temptation to push him-
self too far. Unfortunately, for some years he had also suffered from
a complex of physical diseases which may well have had one underly-
ing though undiagnosed root. Because he was such a selﬂess and warm
person, convivial and happy to immerse himself in the fellowship of oth-
ers, only those closest to him were aware that he suffered from several
escalating and life-threatening conditions. His sudden death on Septem-
ber 4, 2009, left all who knew him bereft. It also deprived scholarship
of the signiﬁcant contributions he would surely have made had he lived
longer. Fortunately, that aspect of him lives on in the continuing work of
all whom he inﬂuenced, and not least in this book.
E.2
Curriculum Vitae
MALCOLM DONALD HYMAN
12 NOVEMBER 1970 – 2 SEPTEMBER 2009
EDUCATION
Ph. D. in Classics, May 2002
Brown University, Providence, RI
Thesis: “Barbarism and Solecism in Ancient Grammatical Thought”
Advisor: William F. Wyatt
B. A. in Classics, summa cum laude, June 1993
Lawrence University, Appleton, WI
RESEARCH INTERESTS
cognitive aspects of writing; ancient literacy
linguistic and scholarly computing
technical terminology and scientiﬁc concepts
Graeco-Roman language science
POSITIONS
Visiting Scholar, Department of Classics, Brown University, Providence,
RI (2006–2009)
Wissenschaftlicher Mitarbeiter, Max-Planck-Institut für Wissenschafts-
geschichte, Berlin, Germany (2004–2009)
Research Fellow, Department of Classics, Harvard University (2001–
2004)
GRANTS
Co-Principal Investigator, “Enhancing Access to Primary Cultural Her-
itage Materials of India,” National Endowment for the Humanities
($301,540, 12 months, starting July 2009) (with PI: P. Scharf)
222
APPENDICES
Co-Principal Investigator, “Collaborative Research: International Digital
Sanskrit Library Integration,” National Science Foundation ($225,
428, 36 months, starting January 2006) (with PIs: P. Scharf, V. Gov-
indaraju)
HONORS AND AWARDS
NHC Young Scholar’s Summer Institute, “The Concept of Language in
the Academic Disciplines” (2003–2004)
Wilbour Fellowship in Latin, Brown University (1998, 1999)
Mellon Fellowship in the Humanities (1993–1994)
Governer J. T. Lewis Prize (senior with highest academic rank), Lawrence
University (1993)
Phi Beta Kappa
Maurice P. Cunningham Prize in Greek (1993)
Wisconsin Association of Foreign Language Teachers Award (1993)
Peerenboom Prize Scholarship in the Field of Semantics, Lawrence Uni-
versity (1992)
PUBLICATIONS
“On the Tip of the Ancient Tongue: Failures of Lexical Access in Greek
and Latin” (co-author: P. Thibodeau), in progress (2009)
“Studies in Cacemphaton” (co-author: P. Thibodeau), in progress (2009)
“Chomsky between Revolutions,” in Chomsky’s Revolutions, ed. D. Kib-
bee (forthcoming, 2009)
Linguistic Issues in Encoding Sanskrit (co-author: P. Scharf), Motilal
Banarsidass (forthcoming, 2009)
“Toward an Epistemic Web” (co-author: J. Renn), in Globalization of
Knowledge and its Consequences, ed. J. Renn (forthcoming, 2009)
“Euclid and Beyond: Towards a Long-term History of Deductivity” (co-
author: M. Schiefsky), Künstliche Intelligenz 4/09 (2009)
APPENDIX E: MALCOLM D. HYMAN
223
“Enhancing Access to Primary Cultural Heritage Materials of India” (co-
author: P. Scharf), in Guide to OCR for Indic Scripts: Document
Recognition and Retrieval, edd. V. Govindaraju and S. Setlur, Ad-
vances in Pattern Recognition (2009)
“From P¯an.inian Sandhi to Finite State Calculus,” in Sanskrit Computa-
tional Linguistics: First and Second International Symposia, edd.
G. Huet, A. Kulkarni, P. Scharf, Lecture Notes in Artiﬁcial Intelli-
gence (2007)
Review of Eleanor Dickey, Ancient Greek Scholarship, Historiographia
Linguistica 35.3 (2008)
“Encoding S¯amaveda with Ruby,” Sanskrit Library Technical Note 1
(2007)
“Semantic Networks: A Tool for Investigating Conceptual Change and
Knowledge Transfer in the History of Science,” in Übersetzung
und Transformation,edd.H. Böhme,C. Rapp,andW.Rösler(2007)
“Of Glyphs and Glottography,”Language&Communication26.3/4(2006)
“Terms for ‘Word’ in Roman Grammar,” in Antike Fachtexte, ed. T. Fö-
gen (2005)
Review of David Sedley, Plato’s Cratylus, Historiographia Linguistica
32.1 (2005)
“One-Word Solecisms and the Limits of Syntax,” in Syntax in Antiquity,
edd. P. Swiggers and A. Wouters, Orbis Supplementa 23 (2003)
Review of Rachel Barney, Names and Nature in Plato’s Cratylus, Bryn
Mawr Classical Review 2003.03.35 (2003)
“Bad Grammar in Context,” New England Classical Journal 29.2 (2002)
“The Hope of the Year: Virgil Georgics 1.224 and Hesiod Opera et Dies
617” (co-author: P. Thibodeau), Classical Philology 94.2 (1999)
Seven articles in Bearers of Meaning: The Ottilia Buerger Collection of
Ancient and Byzantine Coins at Lawrence University, Lawrence
University Press (1995)
224
APPENDICES
PRESENTATIONS AND PAPERS
“Reﬂecting on Oral Traditions: P¯an.ini’s Grammar,” Writing and the
Transmission of Knowledge, Bibliothek Werner Oechslin, Ein-
siedeln, Switzerland, April 30–May 2, 2009
“Linguae Francae, Monetary Systems, and Economy,” Multilingualism,
Linguae Francae, and the Global History of Religious and Scien-
tiﬁc Concepts, The Norwegian Institute at Athens, Greece, April
3–5, 2009
Commentary on P. Marthelot, “Bühler’s Theory of Language as a Solu-
tion to the Crisis in Psychology,” Crisis Debates in Psychology:
International Workshop, Berlin, October 10–12, 2008
“The Globalisation of Knowledge and its Consequences” (with J. Renn),
4th HERA Annual Conference “European Diversities — European
Identities,” Strasbourg, October 8–9, 2008
“Term Discovery in an Early Modern Latin Scientiﬁc Corpus,” ALLC/
ACH, Oulu, Finland, June 24–28, 2008
Workshop on “Multilingualism,” co-organizer (with J. Braarvig), Max
Planck Institute for the History of Science, May 7, 2008
“Humanities Computing: Theoretical Challenges,” invited lecture, Hu-
manities Center, Harvard University, April 17, 2008
“The Epistemic Web,” Epistemic Networks and GRID + Web 2.0 for Arts
and Humanities, Imperial College, London, January 30–31, 2008
“MultilingualismandtheGlobalizationofKnowledge,”UniversitetiOslo,
December 11, 2007
“On Glottography: Parallels between Ontogeny and History,” Workshop
on the Origin of Writing Systems, Max-Planck-Institut für Wis-
senschaftsgeschichte, Berlin, August 27–31, 2007
“Introduction: Modeling the Diffusion of Knowledge,” Dahlem Kon-
ferenzen 97, Globalization of Knowledge and its Consequences,
Program Advisory Committee Meeting, Berlin, May 22–25, 2007
“A Digital Library for Sanskrit and the Challenges of Non-Western Cul-
tural Heritage” (with P. Scharf), Million Books Workshop, Tufts
University, Medford, Massachusetts, May 22–24, 2007
APPENDIX E: MALCOLM D. HYMAN
225
“From Research Challenges of the Humanities to the Epistemic Web
(Web 3.0)” (with J. Renn), NSF/JISC Digital Libraries Infrastruc-
tures, Phoenix, April 17–19, 2007
“What is the Next Step? A Humanities Perspective” (with J. Renn),
Cyber-research Infrastructures and Data Management for Science
and Communities — an ESF/BOREAS Workshop, Paris, February
19–20, 2007
“A Computational Approach to Sanskrit Morphology and Phonology,”
World Sanskrit Conference, Edinburgh, July 10–14, 2006
“Software para realizar exposiciones virtuales” (with J. Damerow), Work-
shop: Ciencia y Cultura entre dos mundos, La Orotava, Tenerife,
May 31, 2006
“Towards a New Platform for Linguistic Analysis and Scholarly Anno-
tation,” Digital Philology: Problems and Perspectives, Universität
Hamburg, January 20, 2006
Co-chair of roundtable discussion “Comparative Literacies of the An-
cient World,” American Historical Society (participants: S. Hous-
ton, M. Hyman, D. Lurie, R. Salomon), January 5, 2006
“Semantic Networks in Ancient and Early Modern Mechanics Texts:
Development and Transformation,” SFB 644 Jahrestagung: Über-
setzung und Transformation, Humboldt-Universität, December 3,
2005
“Aristotle’s Theory of the Syllable,” ICHoLS, Champaign-Urbana, Sep-
tember 2, 2005
“Encoding Sanskrit Phonetics vs.
Encoding Devan¯agar¯ı Script,” De-
van¯agar¯ı OCR Workshop, Brown University, Providence, Rhode
Island, January 22–23, 2005
“The Challenges of the Humanities to the World Wide Web: Perspectives
from the Archimedes Project” (with M. Schiefsky), ALLC/ACH,
Göteborg, Sweden, June 11–16, 2004
“Interfaces for Parser and Dictionary Access,” invited speaker, LDC In-
stitute, University of Pennsylvania, January 26, 2004
Co-chair of panel “Linguistic Issues in the Text Encoding of Sanskrit,”
ALLC/ACH, Athens, Georgia, May 30, 2003
226
APPENDICES
“Greek and Roman Grammarians on Motion Verbs and Place Adver-
bials,” NAAHoLS, Atlanta, Georgia, January 4, 2003
“The Archimedes Project: Current Research” (with M. Schiefsky), NSDL
Workshop, Dibner Institute, MIT, March 9, 2002
CONFERENCE ORGANIZATION
“Multilingualism, Linguae Francae, and the Global History of Religious
and Scientiﬁc Concepts” (with J. Braarvig), The Norwegian Insti-
tute at Athens, Greece, April 3–5, 2009
“Viva
Voce:
Echoes
of
Performance
in
the
Ancient
Text”
(with
V. Panoussi, J. Rowley, P. Thibodeau, M. Sundahl), Brown
University, February 7–8, 1997
TEACHING
Teaching Fellow, Department of Classics, Brown University (1995–1997)
• Essentials of the Latin Language (two semesters)
• Introduction to Latin (intensive)
Teaching Assistant, Department of Classics, Brown University (1994)
• Reason and the Human Good in Ancient Ethical Thought (Instruc-
tor: Martha C. Nussbaum)
PROFESSIONAL AFFILITATIONS
North American Association for the History of the Language Sciences
Linguistic Society of America
Henry Sweet Society for the History of Linguistic Ideas
Association for Literary and Linguistic Computing
Association for Computing in the Humanities
PROFESSIONAL ACTIVITIES
Leader, Cross-Sectional Group III: The Spread of Knowledge through
Cultures, TOPOI: The Formation and and Transformation of Space in
APPENDIX E: MALCOLM D. HYMAN
227
Ancient Civilizations (German Excellence Cluster 264) (2009)
Project Manager, XML Workﬂow and Presentation, project funded by
the Max Planck Digital Library (2008–2009)
• Managed a team of three individuals to develop a standardized
workﬂow for transcription of historical books into structured XML,
a Relax NG schema for these texts, and software for online presen-
tation and content-based access to historical sources
Program Committee member, Second International Sanskrit Computa-
tional Linguistics Symposium (Brown University, May 15–17, 2008);
Third International Sanskrit Computational Linguistics Symposium (Hy-
derabad, January 12–14, 2009)
Expert consultant to ISO/IEC JTC1/SC2/WG2 “Universal Multiple-Octet
Coded Character Set” (2007–2008)
• Proposed standards for encoding Vedic Characters in ISO 10646/
Unicode
• Co-author of working group documents N3235, N3235R, N3290
Exhibitor at the Wissenschaftssommer in Essen, Germany (theme: “Die
Geisteswissenschaften: ABC der Menschheit”) (2007)
• Developed exhibit on current research in linguistic computing and
the decipherment of ancient Near Eastern writing
Member of Sonderforschungsbereich 644 “Transformationen der An-
tike,” Berlin, Germany (2005–2008)
• Investigator in Teilprojekt A6, “Gewicht, Bewegung und Kraft:
Begrifﬂiche Strukturveränderungen antiken Wissens als Folge sei-
ner Tradierung”
228
APPENDICES
Chief technical architect for the interactive component of the German
government-sponsored exhibition “Albert Einstein: Ingenieur des Uni-
versums: 100 Jahre Relativität, Atome und Quanten” (2004–2005)
• The interactive component — “an exhibition without walls” — is
an original concept, with major ﬁnancial support from the Heinz
Nixdorf Foundation, Siemens, and BASF
• Development: distributed software system (Python/Zope) allows
for content creation by scientists and template design by design
professionals. About ﬁfty interactive stations in the Kronprinzen-
palais run the enviroment for the duration of the exhibition. The
exibition has, in addition, a permanent home on the Web, which
includes all digital content produced during the course of the exhi-
bition
• The exhibition won a bronze medal in the “Exhibition Campaign”
categoryoftheInternationalMuseumCommunicationAward(2007)
Member, Board of Directors, The Sanskrit Library, Providence, Rhode
Island (2004–2009)
Technical Consultant, CDLI (Cuneiform Digital Library Initiative), Ber-
lin/Los Angeles (2002–2009)
Research Fellow, Archimedes Project, Harvard University (2001–2004)
• Collaborator with an international team of scholars to implement
a digital research library of texts in the history of mechanics
• Chief developer of Arboreal, an XML-based scholarly working en-
vironment for texts in Greek, Latin, Arabic, Chinese, Akkadian,
Sumerian, and modern European languages (Java, 45,000+ lines)
Technical and linguistic consultant for Sanskrit Library Project, Brown
University (2000–2009)
• Implemented system for morphological analysis of Sanskrit
• Developed system for typesetting a book MS. in Sanskrit, using
TEX (automatic hyphenation for Devan¯agar¯ı text; automatic index
generation and formatting)
APPENDIX E: MALCOLM D. HYMAN
229
• Authored electronic index browser, with capabilities for lexical
and grammatical analysis of word-forms (Java, 7000+ lines)
Prepared SGML-encoded text of Dyer-Seymour commentary on Plato’s
Apology and Crito for Perseus Project (1998)
Referee for John Benjamins, Transactions of the American Philological
Association, New England Classical Journal, Historiographia Linguis-
tica, Harvard Studies in Classical Philology, Association for Literary
and Linguistic Computing, Association for Computing in the Humani-
ties, Boston Studies in the Philosophy of Science, (1994–2009)
COMPUTER SKILLS
Programming Languages: Java, Perl, Python
Other: XML, XSL, RDF, Relax NG, TEI, HTML, CGI, JavaScript, LATEX,
PostgreSQL, Zope, R, xfst
Linux system administration
LANGUAGES READ
Latin, Ancient Greek, Sanskrit, Italian, French, Spanish, German
some university study also of Akkadian
OTHER SKILLS
Copy-editing and indexing experience
230
APPENDICES
Bibliography
Abercrombie, D. (1949), ‘What is a “letter”?’, Lingua 2(1), 54–63.
—–. (1981), Extending the Roman alphabet: Some orthographic exper-
iments of the past four centuries, in Asher & Henderson (1981),
pp. 207–224.
Abhyankar, K. V., ed. (1967), Paribh¯as. ¯a˙ngraha (A Collection of Original
Works on Vy¯akaran. a Paribh¯as. ¯as), Bhandarkar Oriental Research
Institute, Pune.
AbiFarès, H. S. (2001), Arabic Typography: A Comprehensive Source-
book, Saqi, London.
Abu-Rabia, S. & Taha, H. (2006), Reading in Arabic orthography: Char-
acteristics, research ﬁndings, and assessment, in Joshi & Aaron
(2006), pp. 321–338.
Agenbroad, J. E. (n.d.), ‘Difﬁcult characters: A collection of Devana-
gari conjunct consonants’, International Association of Orientalist
Librarians, Bulletin 38, pages 17–53.
Al-Nassir, A. A. (1993), Sibawayh the Phonologist: A Critical Study of
the Phonetic and Phonological Theory of Sibawayh as Presented
in his Treatise Al-Kitab, Vol. 10 of Library of Arabic Linguistics,
Kegan Paul, London.
Allen, G. D. (1988), ‘The PHONASCII system’, Journal of the Interna-
tional Phonetic Association 18(1), 9–25.
231
232
BIBLIOGRAPHY
Allen, W. S. (1951), ‘Some prosodic aspects of retroﬂexion and aspi-
ration in Sanskrit’, Bulletin of the School of Oriental and African
Studies, University of London 13(4), 939–946.
—–. (1953), Phonetics in Ancient India, Oxford University Press, Lon-
don.
Alpert, M. (1981), Speech and disturbances of affect, in Darby (1981),
pp. 221–240.
Anderson, S. R. (1985), Phonology in the Twentieth Century: Theories
of Rules and Theories of Representations, University of Chicago
Press, Chicago.
Aronoff, M. (1992), Segmentalism in linguistics: The alphabetic basis
of phonological theory, in P. Downing, S. D. Lima & M. Noonan,
eds, ‘The Linguistics of Literacy’, Vol. 21 of Typological Studies in
Language, John Benjamins, Amsterdam, pp. 71–82.
Asher, R. E. & Henderson, E. J. A., eds (1981), Towards a History of
Phonetics, Edinburgh Univeristy Press, Edinburgh.
Baddeley, A. & Wilson, B. (1988), ‘Comprehension and working mem-
ory: A single case neuropsychological study’, Journal of Memory
and Language 27(5), 479–498.
Badecker, W. (1996), ‘Representational properties common to phonolog-
ical and orthographic output systems’, Lingua 99, 55–83.
Bailey, T. G., Firth, J. R. & Harley, A. H. (1956), Teach Yourself Urdu,
English Universities Press, London.
Bakker, H. T., Barkhuis, R. & Velthuis, F. J. (1990), ‘Printing N¯agar¯ı
script with TEX’, Newsletter of the International Association of
Sanskrit Studies 3, 27–34.
Bansal, V. & Sinha, R. M. K. (1999), On how to describe shapes of De-
vanagari characters and use them for recognition, in ‘Proceedings
of the Fifth International Conference on Document Analysis and
Recognition (ICDAR ’99)’, pp. 410–413.
BIBLIOGRAPHY
233
—–. (2000),
‘Integrating knowledge sources in Devanagari text
recognition system’, IEEE Transactions on Systems, Man, and
Cybernetics—Part A: Systems and Humans 30(4), 500–505.
Bare, J. S. (1976), Phonetics and Phonology in P¯an. ini: The System of
Features Implicit in the As.t. ¯adhy¯ay¯ı, Vol. 21 of Natural Language
Studies, Phonetics Laboratory, University of Michigan. PhD thesis,
1975.
Barlow, J. S. (1995), A Chinese-Russian-English Dictionary, University
of Hawai‘i Press, Honolulu.
Barry, R. K., ed. (1997), ALA-LC Romanization Tables: Transliteration
Schemes for Non-Roman Scripts, Cataloging Distribution Service,
Library of Congress, Washington.
Beech, J. R. & Mayall, K. A. (2007), The word shape hypothesis re-
examined: Evidence for an external feature advantage in visual
recognition, in P. L. Cornelissen & C. Singleton, eds, ‘Visual Fac-
tors in Reading’, Blackwell, Malden MA, pp. 87–103.
Beeching, W. A. (1990), Century of the Typewriter, 2d edn, British Type-
writer Museum Publishing, New York.
Bell, A. M. (1870), Explanatory Lecture on Visible Speech, The Science
of Universal Alphabetics, Delivered before the College of Precep-
tors, Feb. 9, 1870, Simpkin, Marshall, & Co., London.
Bemer, R. W. (1963), ‘The American Standard Code for Information
Interchange’, Datamation 8–9, 32–36, 39–44.
Benseler, G. E. (1841), De Hiatu in Oratoribus Atticis et Historicis Grae-
cis Libri Duo, J. G. Engelhardt, Freiburg.
Bharati, A., Chaitanya, V. & Sangal, R. (1996), Natural Language
Processing: A Paninian Perspective, Prentice-Hall of India, New
Delhi.
Bhaskararao, P. & Mathur, R. (1991), ‘Phonetic nature of anusvaara’,
Bulletin of the Deccan College Post-graduate & Research Institute
51–2, 229–231.
234
BIBLIOGRAPHY
Bhatia, T. K. (1974), ‘The problems of programming Devanagari script
on PLATO IV and a proposal for a revised Hindi typewriter’, Lan-
guage, Literature and Society: Occasional Papers, No. 1. Center for
Southeast Asian Studies, Northern Illinois University, pages 52–64.
Bhatt, S. (n.d.), ‘Character encoding standard for Indian scripts—a re-
port’, <http://www.cicc.or.jp/english/hyoujyunka/mlit4/7-3India/
India.htm>.
Birnbaum, D. J. (1989), Issues in developing international standards for
encoding non-Latin alphabets, in E. Johnson, ed., ‘Proceedings of
the Fourth International Conference on Symbolic and Logical Com-
puting’, Dakota State University, Madison SD, pp. 41–54.
Boltz, W. G. (2006), ‘Pictographic myths’, Bochumer Jahrbuch zur Ost-
asienforschung 30, 39–54.
Bondy, J. A. (1972), The “graph theory” of the Greek alphabet, in
Y. Alavi, D. R. Lick & A. T. White, eds, ‘Graph Theory and Appli-
cations: Proceedings of the Conference at Western Michigan Uni-
versity, May 10–13, 1972’, Vol. 303 of Lecture Notes in Mathemat-
ics, Springer, Berlin, pp. 43–54.
Brown, W. N. (1953), ‘Script reform in modern India, Pakistan, and Cey-
lon’, Journal of the American Oriental Society 73(1), 1–6.
Bruce, V. & Young, A. (1998), In the Eye of the Beholder, Oxford Uni-
versity Press, Oxford.
Brugmann, K. (1906–1916), Grundriss der vergleichende Grammatik
der indo-germanischen Sprachen, 2d edn, Trübner, Strassburg. 2
vols.
Bühler, G. (1896), Indische Palaeographie: von circa 350 A. Chr.–circa
1300 P. Chr., Vol. 1. Bd., 11. Heft of Grundriss der indo-arischen
Philologie und Altertumskunde, K. J. Trübner, Strassburg.
Bukatman, S. (1993), ‘Gibson’s typewriter’, South Atlantic Quarterly
92(4), 627–645.
BIBLIOGRAPHY
235
Bureau of Indian Standards (1992), Indian Script Code for Information
Interchange—ISCII standard, New Delhi.
Burk, M. G. (1976), An exposition and a relative chronology of
the phonological transformations from Indo-European to Sanskrit,
Master’s thesis, The University of Texas at Austin. Jointly pub-
lished with Sv¯atmaprak¯a´sik¯a ‘Light on one’s real self’.
Burrow, T. (1955), The Sanskrit Language, Faber & Faber, London.
Reprinted, Motilal Banarsidass, 2001.
Busetto, L. (2003), ‘Fonetica nell’India antica’, Studi Linguistici e Filo-
logici Online 1, 191–226. <http://www.humnet.unipi.it/slifo/>.
Calabrese, A. (1998), On coronalization and affrication in palatalization
processes: An inquiry into the nature of a sound change, in D. Chen,
T.-H. Hsin & E. Shortt, eds, ‘Papers in Phonology’, Vol. 9 of Uni-
versity of Connecticut Working Papers in Linguistics, University of
Connecticut Department of Linguistics, Storrs CN.
Caramazza, A. (2000), Aspects of lexical access: Evidence from aphasia,
in Y. Grodzinsky, L. P. Shapiro & D. Swinney, eds, ‘Language and
the Brain: Representation and Processing’, Academic Press, San
Diego, chapter 11, pp. 203–228.
Caramazza, A. & Miceli, G. (1990), ‘The structure of graphemic repre-
sentations’, Cognition 37, 243–297.
Cardona, G. (1965), ‘On P¯an.ini’s morphophonemic principles’, Lan-
guage 41(2), 225–237.
—–. (1977), ‘A note on morphophonemic and phonetic rules in Sanskrit’,
The Mysore Orientalist 10, 1–6.
—–. (1980), On the ¯Api´sali´siks.¯a, in A. L. Basham et al., eds, ‘A Cor-
pus of Indian Studies: Essays in Honor of Prof. Gaurin¯ath Sastr¯ı’,
Sanskrit Pustak Bhandar, Calcutta, pp. 245–256.
—–. (1983), Phonetics and phonological rules in grammars, in ‘Linguis-
tic Analysis and Some Indian Traditions’, Bhandarkar Oriental Re-
search Institute, Pune, pp. 1–36.
236
BIBLIOGRAPHY
—–. (1987), ‘Some neglected evidence concerning the development of
abhinihita sandhi’, Studien zur Indologie und Iranistik 13/14, 59–
68.
—–. (1993), ‘The Bh¯as.ika accentuation system’, Studien zur Indologie
und Iranistik 18, 1–40.
—–. (1997), P¯an. ini: His Work and its Traditions, Vol. I, Background and
Introduction, 2d edn, Motilal Banarsidass.
—–. (2003), Sanskrit, in Cardona & Jain (2003), pp. 104–160.
—–. (n.d.), Developments of nasals in early Indo-Aryan: anun¯asika and
anusv¯ara. Unpublished MS.
—–. & Jain, D., eds (2003), The Indo-Aryan Languages, number 2 in
‘Routledge Language Family Series’, Routledge, London.
Carterette, E. C. & Friedman, M. P., eds (1978), Handbook of Perception
Volume IX: Perceptual Processing, Academic Press, New York.
Chao, Y.-R. (1930), ‘A system of tone-letters’, Le Maître Phonétique
30, 24–27.
Chomsky, N. & Halle, M. (1968), The Sound Pattern of English, MIT
Press, Cambridge MA.
Clements, G. N. (1985), The geometry of phonological features, in
‘Phonology Yearbook’, Vol. 2, Cambridge University Press, Cam-
bridge, pp. 225–252.
—–. (1990), The role of the sonority cycle in core syllabiﬁcation, in
J. Kingston & M. E. Beckman, eds, ‘Papers in Laboratory Phonol-
ogy I: Between the Grammar and Physics of Speech’, Cambridge
University Press, Cambridge, pp. 283–333.
Clements, G. N. & Hume, E. V. (1995), The internal organization of
speech sounds, in Goldsmith (1995b), pp. 245–306.
Cohen, L. & Dehaene, S. (2004), ‘Specialization within the ventral
stream:
the case for the visual word form area’, NeuroImage
22, 466–476.
BIBLIOGRAPHY
237
Cole, M., Levitin, K. & Luria, A. (2006), The Autobiography of Alexan-
der Luria: A Dialogue with The Making of Mind, Lawrence Erl-
baum, Mahwah NJ.
Cubelli, R. (1991), ‘A selective deﬁcit for writing vowels in acquired
dysgraphia’, Nature 353, 258–260.
Damerow, P. (1996), Abstraction and Representation: Essays on the Cul-
tural Evolution of Thinking, Vol. 175 of Boston Studies in the Phi-
losophy of Science, Kluwer, Dordrecht.
—–. (1999), ‘The origins of writing as a problem of historical epistemol-
ogy’, Max-Planck-Institut für Wissenschaftsgeschichte Preprint
114.
Dani, A. H. (1963), Indian Palaeography, Clarendon Press, Oxford.
Darby, J. K., ed. (1981), Speech Evaluation in Psychiatry, Grune & Strat-
ton, New York.
Desbordes, F. (1990), Idées romaines sur l’écriture, Presses Universi-
taires de Lille.
Deshpande, M. M. (1997a), P¯an.ini and the distinctive features, in
I. Hegedus, P. A. Michalove & A. M. Ramer, eds, ‘Indo-European,
Nostratic, and Beyond: Festschrift for Vitalij V. Shevoroshkin’,
Vol. 22 of Journal of Indo-European Studies Monographs, Institute
for the Study of Man, Washington DC, pp. 72–87.
—–, ed. (1997b), ´Saunak¯ıy¯a Catur¯adhy¯ayik¯a: a Pr¯ati´s¯akhya of the
´Saunak¯ıya Atharvaveda, with commentaries Catur¯adhy¯ay¯ıbh¯as.ya,
Bh¯argava-Bh¯askara-Vr
˚
tti and Pañcasandhi, Dept. of Sanskrit and
Indian Studies, Harvard University, Cambridge MA.
Diehl, K. S. (1968), ‘Bengali types and their founders’, Journal of Asian
Studies 27(2), 335–338.
Dixon, R. M. W. & Aikhenvald, A. Y. (2002), Word: A typological
framework, in R. M. W. Dixon & A. Y. Aikhenvald, eds, ‘Word:
A Cross-Linguistic Typology’, Cambridge University Press, Cam-
bridge, pp. 1–41.
238
BIBLIOGRAPHY
Driver, G. R. (1976), Semitic Writing: From Pictograph to Alphabet, 3d
edn, Oxford University Press, London. Edited by S. A. Hopkins.
Edgerton, F. (1946), Sanskrit Historical Phonology: A Simpliﬁed Outline
for Beginners in Sanskrit, Vol. 5 of Supplement to the Journal of the
American Oriental Society, American Oriental Society, Baltimore
MD.
—–. (1970), Buddhist Hybrid Sanskrit Grammar and Dictionary, 2 vols.,
Motilal Banarsidass, Delhi. Facsimile of 1953 New Haven edition.
Edgerton, W. F. (1941), ‘Ideograms in English writing’, Language
17(2), 148–150.
Eisenstein, E. L. (1980), The Printing Press as an Agent of Change:
Communications and Cultural Transformations in Early-Modern
Europe, Cambridge University Press, Cambridge.
Ellis, A. W. (1979), ‘Slips of the pen’, Visible Language 13(3), 265–282.
Emeneau, M. B. (1946), ‘The nasal phonemes of Sanskrit’, Language
22(2), 86–93.
Erduman, D., ed. (2004), Geschriebene Welten: Arabische Kalligraphie
und Literatur im Wandel der Zeit, Dumont, Köln.
Esterman, M., Verstynen, T., Ivry, R. B. & Robertson, L. C. (2006),
‘Coming unbound:
Disrupting automatic integration of synes-
thetic color and graphemes by transcranial magnetic stimulation
of the right parietal lobe’, Journal of Cognitive Neuroscience
18(9), 1570–1576.
Estes, W. K. (1978), Perceptual processing in letter recognition and read-
ing, in Carterette & Friedman (1978), pp. 163–220.
Fano, R. M. (1966), Transmission of Information: A Statistical Theory
of Communications, 2d edn, MIT Press, Cambridge MA.
Firth, J. R. (1936), ‘Alphabets and phonology in India and Burma’, Bul-
letin of the School of Oriental Studies 8(2/3), 517–546.
BIBLIOGRAPHY
239
—–. (1946), ‘The English school of phonetics’, Transactions of the
Philological Society pp. 92–132.
French, M. A. (1976), Observations on the Chinese script and the classi-
ﬁcation of writing-systems, in Haas (1976), pp. 101–129.
Frost, R. (1992), Orthography and phonology: The psychological reality
of orthographic depth, in P. Downing, S. D. Lima & M. Noonan,
eds, ‘The Linguistics of Literacy’, Vol. 21 of Typological Studies in
Language, John Benjamins, Amsterdam, pp. 255–274.
Fry, A. H. (1941), ‘A phonemic interpretation of visarga’, Language
17(3), 194–200.
Füssel, S. (2005), Gutenberg and the Impact of Printing, Ashgate,
Burlington, VT. First published in 1999 as Gutenberg und seine
Wirkung, Insel, Frankfurt am Main.
Gaylord, H. E. (1995), ‘Character representation’, Computers and the
Humanities 29, 51–73.
Geyer, L. H. (1970), A Two-Channel Theory of Short Term Visual Stor-
age, PhD thesis, SUNY at Buffalo.
Geyer, L. H. & DeWald, C. G. (1973), ‘Feature lists and confusion ma-
trices’, Perception & Psychophysics 14(3), 471–482.
Ghosh, P. K. (1983), An approach to type design and text composition
in Indian scripts, Technical Report STAN-CS-83-965, Department
of Computer Science, Stanford University. <http://infolab.stanford.
edu/TR/CS-TR-83-965.html>.
Gibson, E. J. (1969), Principles of Perceptual Learning and Develop-
ment, Appleton-Century-Crofts, New York.
—–. (1972), Reading for some purpose, in Kavanagh & Mattingly
(1972), pp. 3–19.
Gill, E. (1936), An Essay on Typography, 2d edn, Sheed and Ward. Fac-
simile edition with new introduction by Christopher Skelton, David
R. Godine, Boston, 2007.
240
BIBLIOGRAPHY
Gillam, R. (2002), Unicode Demystiﬁed: A Practical Programmer’s
Guide to the Encoding Standard, Addison-Wesley, Boston.
Glaister, G. A. (1979), Glaister’s Glossary of the Book: Terms Used in
Papermaking, Printing, Bookbinding, and Publishing with Notes on
Illuminated Manuscripts and Private Presses, 2d edn, University of
California Press, Berkeley.
Goldin-Meadow, S. (2003), Hearing Gesture: How Our Hands Help Us
Think, Belknap Press, Cambridge MA.
Goldsmith, J. A. (1995a), Phonological theory, in The Handbook of
Phonological Theory (Goldsmith, 1995b), pp. 1–23.
—–, ed. (1995b), The Handbook of Phonological Theory, Blackwell,
Cambridge MA.
Goodglass, H. (1993), Understanding Aphasia, Academic Press, San
Diego.
Govindaraju, V., Setlur, S., Khedekar, S., Kompalli, S., Farooq, F. &
Vemulapati, R. (2004), Enabling digital access to multi-lingual In-
dian documents, in ‘Proceedings of the First International Work-
shop on Document Image Analysis for Libraries’.
Griffen, T. D. (1976), ‘Toward a nonsegmental phonology’, Lingua
40, 1–20.
Gupta, R. (2006), ‘Technology for Indic scripts: A user perspective’,
Language in India 6, 1–17.
<http://www.languageinindia.com/
july2006/indictechnology.pdf>.
Haas, W., ed. (1976), Writing without Letters, Vol. 4 of Mont Follick
Series, Manchester University Press, Manchester.
Hadj-Salah, A. (1971), ‘La notion de syllabe et la theorie cinetico-
impulsionnelle des phoneticiens arabes’, Al-Lis¯aniyy¯at 1, 63–83.
Halle, M. (1983), ‘On distinctive features and their articulatory imple-
mentation’, Natural Language Theory 1, 91–105.
BIBLIOGRAPHY
241
—–. (1988), ‘Remarques sur la révolution scientiﬁque en phonologie,
1926/1930’, Actes de la recherche en sciences sociales 74, 89–96.
—–. (1995), ‘Feature geometry and feature spreading’, Linguistic In-
quiry 26(1), 1–46.
—–. (2002), From Memory to Speech and Back: Papers on Phonetics
and Phonology 1954–2002, Vol. 3 of Phonology and Phonetics, De
Gruyter, Berlin.
Halle, M., Vaux, B. & Wolfe, A. (2000), ‘On feature spreading and
the representation of place of articulation’, Linguistic Inquiry
31(3), 387–444.
Hamann, S. R. (2003), The Phonetics and Phonology of Retroﬂexes, PhD
thesis, Universiteit Utrecht.
Hamp, E. P. (1959), ‘Graphemics and paragraphemics’, Studies in Lin-
guistics 14(1–2), 1–5.
Haralambous, Y. (2002), ‘Unicode et typographie: un amour impossi-
ble’, Document Numérique 6(3/4), 107–139.
—–. (2004), Fontes & codages, O’Reilly, Paris.
Haralambous, Y. & Plaice, J. (2002), ‘Low-level Devan¯agar¯ı support
for Omega—Adapting devnag’, TUGboat 23(1), 50–56. <http:
//www.tug.org/TUGboat/Articles/tb23-1/haralambous.pdf>.
Harley, A. H. (1955), Colloquial Hindustani, Routledge & Kegan Paul,
London. With an introduction by J. R. Firth.
Harris, W. V. (1989), Ancient Literacy, Harvard University Press, Cam-
bridge MA.
Hellingman, J. (1998), ‘Indian scripts and Unicode’, <http://ldc.upenn.
edu/myl/IndianScriptsUnicode.html>.
Henderson, L. (1985), ‘On the use of the term “grapheme” ’, Language
and Cognitive Processes 1(2), 135–148.
242
BIBLIOGRAPHY
Hillenbrand, J. M. & Houde, R. A. (1996), ‘The role of F0 and amplitude
in the perception of intervocalic glottal stops’, Journal of Speech &
Hearing Research 39(6), 1182–1191.
Hixon, T. J. (1987), Respiratory function in speech, in Respiratory Func-
tion in Speech and Song (Hixon & Collaborators, 1987), chapter 1,
pp. 1–54.
Hixon, T. J. & collaborators (1987), Respiratory Function in Speech and
Song, College-Hill Press, Boston.
Hoberman, R. D. (1985), ‘The phonology of pharyngeals and pharyn-
gealization in Pre-Modern Aramaic’, Journal of the American Ori-
ental Society 105(2), 221–231.
Hock, H. H. (1975), ‘Substratum inﬂuence on (Rig-Vedic) Sanskrit?’,
Studies in the Linguistic Sciences 5(2), 76–125.
—–. (1979), ‘Retroﬂexion rules in Sanskrit’, South Asian Languages
Analysis 1, 47–62.
—–. (1993), ‘Subversion or convergence?
the issue of pre-Vedic
retroﬂexion reexamined’,
Studies in the Linguistic Sciences
23(2), 73–115.
—–. (n.d.), ‘Devanagari made easy’, Unpublished instructional materi-
als.
Hockey, S. (2000), Electronic Texts in the Humanities: Principles and
Practice, Oxford University Press, New York.
Hoenig,
A. (1990),
‘A constructed Duerer alphabet’,
TUGboat
11(3), 435–438.
<http://www.tug.org/TUGboat/Articles/tb11-
3/tb29hoenig.pdf>.
Hofstadter, D. R. (1985), Metamagical Themas:
Questing for the
Essence of Mind and Pattern, Basic Books, New York.
Hubel, D. H. & Wiesel, T. N. (1968), ‘Receptive ﬁelds and func-
tional architecture of monkey striate cortex’, Journal of Physiology
195, 215–243.
BIBLIOGRAPHY
243
Huet, G. (2005), ‘A functional toolkit for morphological and phonolog-
ical processing, application to a Sanskrit tagger’, Journal of Func-
tional Programming 15(4), 573–614.
—–. (2009), Formal structure of Sanskrit text: Requirements for a me-
chanical Sanskrit processor, in Huet, Kulkarni & Scharf (2009),
pp. 162–199.
Huet, G., Kulkarni, A. & Scharf, P. M., eds (2009), Sanskrit Com-
putational Linguistics: First and Second International Symposia:
Rocquencourt, France, October 2007; Providence, RI, USA, May
2008, Vol. 5402 of Lecture Notes in Artiﬁcial Intelligence, Springer,
Berlin.
Hyman, M. D. (2006), ‘Of glyphs and glottography’, Language & Com-
munication 26, 231–249.
Ingram, W. H. (1966), ‘The ligatures of early printed Greek’, Greek,
Roman and Byzantine Studies 7(4), 371–389.
Ishida, R. (2002), ‘An introduction to Indic scripts’, Paper delivered at
22nd Int. Unicode Conference, San José, CA, Sept. 2002. <http:
//www.w3.org/2002/Talks/09-ri-indic/indic-paper.pdf>.
Ivanov, V. V. & Toporov, V. N. (1968), Sanskrit, Nauka, Moscow. Origi-
nally published in Russian, 1960.
Jaffré, J.-P. & Fayol, M. (2006), Orthography and literacy in French, in
Joshi & Aaron (2006), pp. 81–103.
Jakobson, R. ([1929] 1971), Remarques sur l’évolution phonologique du
russe comparée à celle des autres langues slaves, in ‘Selected Writ-
ings, Vol. 1: Phonological Studies’, 2d edn, Mouton, The Hague,
pp. 7–116.
Jakobson, R., Fant, C. G. M. & Halle, M. (1963), Preliminaries to Speech
Analysis: The Distinctive Features and their Correlates, MIT Press,
Cambridge MA. With additions and corrigenda to the 1952 edition.
Jenkins, J. H. (1999), ‘The Unicode character-glyph model:
Case
studies’, Paper delivered at 15th Int. Unicode Conference, San
244
BIBLIOGRAPHY
José, CA, Aug./Sept. 1999.
<http://developer.apple.com/fonts/
WhitePapers/IUC15CG.pdf>.
Jones, D. (1942), The Problem of a National Script for India, Pioneer
Press, Lucknow, U. P.
—–. (1962), The Phoneme: Its Nature and Use, 2d edn, W. Heffer &
Sons, Cambridge.
Joseph, J. E. (2000), Limiting the Arbitrary: Linguistic Naturalism and
its Opposites in Plato’s Cratylus and Modern Theories of Lan-
guage, Vol. 96 of Studies in the History of the Language Sciences,
John Benjamins, Amsterdam.
Joshi, A., Ganu, A., Chand, A., Parmar, V. & Mathur, G. (2004),
‘Keylekh: A keyboard for text entry in Indic scripts’, CHI 2004,
April 24–29, Vienna.
Joshi, R. K. (2006), ‘The phonemic model from India for bi-modal appli-
cations’, Paper delivered at the Second Workshop on International-
izing SSML, Heraklion, Crete, May 2006. <http://www.w3.org/
2006/02/SSML/agenda.html>.
Joshi, R. K., Dharmadhikari, T. N. & Bedekar, V. V. (2007), ‘The
phonemic approach for Sanskrit text’, <http://sanskrit.inria.fr/
Symposium/Phonemics_CDAC.pdf>.
Joshi, R. M. & Aaron, P. G., eds (2006), Handbook of Orthography and
Literacy, Erlbaum, Mahwaw NJ.
Kahan, B. (2000), Ottmar Mergenthaler: The Man and his Machine; A
Biographical Appreciation of the Inventor on his Centennial, Oak
Knoll Press, New Castle DE.
Kahn, D. (1996), The Codebreakers: The Story of Secret Writing, 2d edn,
Scribner, New York.
Kapr, A. (1993), Fraktur:
Form und Geschichte der gebrochenen
Schriften, Hermann Schmidt, Mainz.
BIBLIOGRAPHY
245
Katsoulidis, T. (1996), The physiognomy of the Greek typographical let-
ter, in M. S. Macrakis, ed., ‘Greek Letters: From Tablets to Pixels’,
Oak Knoll Press, New Castle DE, pp. 153–161.
Kaufman, S. A. (1984), ‘On vowel reduction in Aramaic’, Journal of the
American Oriental Society 104(1), 87–95.
Kavanagh, J. F. & Mattingly, I. G., eds (1972), Language by Ear and by
Eye: The Relationships between Speech and Reading, MIT Press,
Cambridge MA.
Keane, E. (2004), ‘Tamil’, Journal of the International Phonetic Associ-
ation 34(1), 111–116.
Kelly, J. (1981), The 1847 alphabet: an episode of phonotypy, in Asher
& Henderson (1981), pp. 248–264.
Kemp, J. A. (1994), Phoneme, in R. E. Asher, ed., ‘The Encyclopedia of
Language and Linguistics’, Vol. 6, Pergamon, New York, pp. 3029–
3036.
Kenyon, F. G. (1951), Books and Readers in Ancient Greece and Rome,
2d edn, Clarendon, Oxford.
Kernighan, B. W. & Pike, R. (1984), The UNIX Programming Environ-
ment, Prentice-Hall, Englewood Cliffs NJ.
Kielhorn, L. F., ed. (1962, 1965, 1972), The Vy¯akaran. a-mah¯abh¯as.ya of
Patañjali, third edition revised and furnished with additional read-
ings, references and select critical notes by k. v. abhyankar edn,
Bhandarkar Oriental Research Institute, Pune. 3 vols.
Kim, C. W. (1997), The structure of phonological units in han’g˘ul, in Y.-
K. Kim-Renaud, ed., ‘The Korean Alphabet: Its History and Struc-
ture’, University of Hawai‘i Press, Honolulu, pp. 145–160.
Kita, S., ed. (2003), Pointing: Where Language, Culture, and Cognition
Meet, Erlbaum, Mahwaw NJ.
Klatt, D. H. (1976), ‘Linguistic uses of segmental duration in English:
Acoustic and perceptual evidence’, Journal of the Acoustical Soci-
ety of America 59(5), 1208–1221.
246
BIBLIOGRAPHY
Klima, E. S. (1972), How alphabets might reﬂect language, in Kavanagh
& Mattingly (1972), pp. 57–80.
Kompalli, S. (2007), Design of a Stochastic Framework for Font-
independent Devanagari OCR, PhD thesis, University of Buffalo.
Krampen, M. (1986), On the origins of visual literacy: Children’s draw-
ings as compositions of graphemes, in M. E. Wrolstad & D. F.
Fisher, eds, ‘Toward a New Understanding of Literacy’, Praeger,
New York, pp. 80–111.
Krishna, S. (1991), India’s Living Languages: The Critical Issues, Allied
Publishers, New Delhi.
Kropaˇc, I. H. (1991), Medieval documents, in D. I. Greenstein, ed.,
‘Modelling Historical Data: Towards a Standard for Encoding
and Exchanging Machine-Readable Texts’, Vol. 11 of Halbgraue
Reihe zur Historischen Fachinformatik, Max-Planck-Institut für
Geschichte, St. Katharinen, pp. 117–127.
Ladefoged, P. (1971), Preliminaries to Linguistic Phonetics, University
of Chicago Press, Chicago.
—–. (2005), ‘Features and parameters for different purposes’, Depart-
ment of Linguistics, UCLA. Working Papers in Phonetics. Paper
No104_1. Pages 1–13, <http://repositories.cdlib.org/uclaling/wpp/
No104_1>.
Lagally, K. (1999), ‘7-bit meta-transliterations for 8-bit Romanizations’,
<http://elib.uni-stuttgart.de/opus/volltexte/1999/421/pdf/421_1.
pdf>.
—–. (2004), ‘ArabTEX: Typesetting Arabic and Hebrew, user manual
version 4.00’, <http://129.69.218.213/arabtex/doc/arabdoc.pdf>.
Laughery, K. R. (1971), Computer simulation of short-term memory: A
component decay model, in G. T. Bower & J. T. Spence, eds, ‘The
Psychology of Learning and Motivation: Advances in Research and
Theory’, Vol. 6, Academic Press, New York.
BIBLIOGRAPHY
247
Laver, J. (1994), Principles of Phonetics, Cambridge University Press,
Cambridge.
Lunde, P. (1981), ‘Arabic and the art of printing’, Aramco World
32(2), 20–25.
Lyytinen, H., Aro, M., Holopainen, L., Leiwo, M., Lyttinen, P. & Tolva-
nen, A. (2006), Children’s language development and reading in a
highly transparent orthography, in Joshi & Aaron (2006), pp. 47–
62.
MacCarthy, P. A. D. (1969), The Bernard Shaw alphabet, in W. Haas,
ed., ‘Alphabets for English’, number 1 in ‘Mont Follick Series’,
Manchester University Press, Manchester, pp. 105–117.
Macdonell, A. A. (1910), Vedic Grammar, K. J. Trübner, Strassburg.
Mackenzie, C. E. (1980), Coded Character Sets, History and Develop-
ment, The Systems Programming Series, Addison-Wesley, Reading
MA.
MacMahon, M. K. C. (1981), Henry Sweet’s system of shorthand, in
Asher & Henderson (1981), pp. 265–281.
MacWhinney, B. (1991), The CHILDES Project: Tools for Analyzing
Talk, Erlbaum, Hillsdale NJ.
Maddieson, I. (1984), Patterns of Sounds, Cambridge University Press,
Cambridge. With a chapter contributed by Sandra Ferrari Disner.
Mahmoud, Y. (1979), The Arabic Writing System and the Sociolinguis-
tics of Orthographic Reform, PhD thesis, Georgetown University.
Massaro, D. W. (1973), ‘Perception of letters, words, and nonwords’,
Journal of Experimental Psychology 100(2), 349–353.
McArthur, T., ed. (1992), The Oxford Companion to the English Lan-
guage, Oxford University Press, Oxford.
McCarthy, J. (1994), The phonetics and phonology of Semitic pharyn-
geals, in P. Keating, ed., ‘Papers in Laboratory Phonology III:
Phonological Structure and Phonetic Form’, Cambridge University
Press, Cambridge, pp. 191–233.
248
BIBLIOGRAPHY
McNeill, D. (1992), Hand and Mind: What Gestures Reveal about
Thought, University of Chicago Press, Chicago.
Mermelstein, P. & Eden, M. (1964), ‘Experiments on computer recog-
nition of connected handwritten words’, Information and Control
7, 255–270.
Mikami, Y., abu Bakar, A. Z., Sonlert-lamvanich, V., Vikas, O., Pavol,
Z., abdul Rozan, M. Z., János, G. N. & Takahashi, T. (2005), Lan-
guage diversity on the internet: An Asian view, in UNESCO In-
stitute for Statistics, ed., ‘Measuring Linguistic Diversity on the
Internet’, UNESCO, Paris, pp. 91–103.
Miller, D. G. (1994), Ancient Scripts and Phonological Knowledge, Vol.
116 of Amsterdam Studies in the Theory and History of Linguistic
Science, John Benjamins, Amsterdam.
M¯ım¯a ˙msaka, Y. (1964), Vaidika-v¯a˙nmaya me ˙m vividha svar¯a˙nkana-
prak¯ara, Bharatiya Pracyavidya Pratisthan, Ajmer.
Mishra, V. (1972), A Critical Study of Sanskrit Phonetics, Chowkhamba
Sanskrit Series Ofﬁce, V¯ar¯anas¯ı.
Mohanty, S. K. (1998), The formulation of parameters for type design
of Indian scripts based on calligraphic studies, in R. D. Hersch,
J. André & H. Brown, eds, ‘Electronic Publishing, Artistic Imag-
ing, and Digital Typography: 7th International Conference on Elec-
tronic Publishing, EP ’98, St. Malo, France, March 30–April 3,
1998: Proceedings’, pp. 157–166.
Monier-Williams, M. (1872), A Sanskrit-English Dictionary Etymologi-
cally and Philologically Arranged with Special Reference to Greek,
Latin, Gothic, German, Anglo-Saxon, and Other Cognate Indo-
European Languages, Clarendon, Oxford.
Morison, S. (1972), Politics and Script: Aspects of Authority and Free-
dom in the Development of Graeco-Latin Script from the Sixth-
Century BC, Clarendon Press, Oxford.
Mujoo, A., Malviya, M. K., Moona, R. & Prabhakar, T. V. (2000),
A search engine for Indian languages, in K. Bauknecht, S. K.
BIBLIOGRAPHY
249
Madria & G. Pernul, eds, ‘Electronic Commerce and Web Tech-
nologies: First International Conference, EC-Web 2000, London,
UK, September 4–6, 2000, Proceedings’, Vol. 1875 of Lecture
Notes in Computer Science, Springer, Berlin, pp. 349–358.
Narasimhan, R. & Reddy, V. S. N. (1967), ‘A generative model for hand-
printed English letters and its computer implementation’, ICC Bul-
letin 6, 275–287.
Naus, M. J. & Shillman, R. J. (1976), ‘Why a Y is not a V: A new look
at the distinctive features of letters’, Journal of Experimental Psy-
chology: Human Perception and Performance 2(3), 394–400.
Nolan, F. (1997), Speaker recognition and forensic phonetics, in W. J.
Hardcastle & J. Laver, eds, ‘The Handbook of Phonetic Sciences’,
Blackwell, Oxford, pp. 744–767.
Oberlies, T. (2003), A´sokan Prakrit and P¯ali, in Cardona & Jain (2003),
pp. 161–203.
Ohala, M. (1983), Aspects of Hindi Phonology, Vol. 2 of MLBD Series
in Linguistics, Motilal Banarsidass, Delhi.
Olivier, F. (1974), ‘Le dessin enfantin est-il une écriture?’, Enfance
22, 183–216.
Oudeyer, P.-Y. (2006), Self-Organization in the Evolution of Speech,
Vol. 6 of Studies in the Evolution of Language, Oxford University
Press, Oxford.
P¯at.haka, P. Y., ed. (1883), K¯aty¯ayana’s Pr¯ati´s¯akhya of the White Ya-
jur Veda [V¯ajasaneyi Pr¯ati´s¯akhya] with the Commentary of Uvat.a,
Benares Sanskrit Series 8, V¯ar¯anas¯ı.
Page, R. I. (1999), An Introduction to English Runes, 2d edn, Boydell,
Woodbridge, UK.
Pandey, A. (1998), ‘An overview of Indic fonts for TEX’, TUGboat
19(2), 115–120.
250
BIBLIOGRAPHY
Parida, L. (1993), Vinyas: an interactive calligraphic type design sys-
tem, in ‘Proceedings of the International Conference on Computer
Graphics (ICCG 93)’, Bombay, pp. 355–368.
Patel, P. (1995), Brahmi scripts, orthographic units, and reading acqui-
sition, in I. Taylor & D. Olson, eds, ‘Scripts and Literacy: Read-
ing and Learning to Read Alphabets, Syllabaries, and Characters’,
Kluwer, Dordrecht, pp. 265–276.
Pierce, J. (1999), Sound waves and sine waves, in P. R. Cook, ed., ‘Mu-
sic, Cognition, and Computerized Sound: An Introduction to Psy-
choacoustics’, MIT Press, Cambridge MA, pp. 37–56.
Pitman, I. (1837), Stenographic Sound-Hand, Samuel Bagster, London.
Priolkar, A. K. (1958), The Printing Press in India: Its Beginnings
and Early Development: Being a Quatercentenary Commemora-
tion Study of the Advent of Printing in India (in 1556), Marathi
Samshodhana Mandala, Mumbai.
Pulgram, E. (1951), ‘Phoneme and grapheme: A parallel’, Word 7, 15–
20.
Pulgram, E. (1976), The typologies of writing-systems, in Haas (1976),
pp. 1–28.
Pullum, G. K. & Ladusaw, W. A. (1986), Phonetic Symbol Guide, Uni-
versity of Chicago Press, Chicago.
Ramachandran, V. S. & Hubbard, E. M. (2001), ‘Psychophysical inves-
tigations into the neural basis of synaesthesia’, Proceedings of the
Royal Society of London, B 268, 979–983.
Ramachandran, V. S., Hubbard, E. M. & Butcher, P. A. (2004), Synes-
thesia, cross-activation, and the foundations of neuroepistemology,
in G. A. Calvert, C. Spence & B. E. Stein, eds, ‘The Handbook of
Multisensory Processes’, MIT Press, Cambridge MA, pp. 867–883.
Ramsey, S. R. (1989), The Languages of China, 2d edn, Princeton Uni-
versity Press, Princeton NJ.
BIBLIOGRAPHY
251
Rastogi, S. I., ed. (1967), The ´Suklayajuh. -pr¯ati´s¯akhya of K¯aty¯ayana, Vol.
179 of Kashi Sanskrit Series, Chowkhamba Sanskrit Series Ofﬁce,
V¯ar¯anas¯ı. Forward by Mangal Deva Shastri (author’s father).
Rath, T. M. & Manmatha, R. (2003), Features for word spotting in his-
torical manuscripts, in ‘Proceedings: Seventh International Confer-
ence on Document Analysis and Recognition: August 3 to 6, 2003,
Edinburgh, Scotland, vol. 1’, pp. 218–222.
Reed, S. K. (1978), Schemes and theories of pattern recognition, in
Carterette & Friedman (1978), pp. 137–162.
Renou, L. (1952), Grammaire de la langue védique, IAC, Lyon.
Rich, A. N. & Mattingley, J. B. (2005), Can attention modulate color-
graphemic synesthesia?, in Robertson & Sagiv (2005), chapter 7,
pp. 108–123.
Robertson, L. C. & Sagiv, N., eds (2005), Synesthesia: Perspectives from
Cognitive Neuroscience, Oxford University Press, New York.
Romani, C. & Calabrese, A. (1998), ‘Syllabic constraints in the phono-
logical errors of an aphasic patient’, Brain and Language 64, 83–
121.
Roper, G. (2002), Early Arabic printing in Europe, in E. Hanebutt-Benz,
D. Glass & G. Roper, eds, ‘Sprachen des Nahen Ostens und die
Druckrevolution: Eine interkulturelle Begegnung’, WVA-Verlag
Skulima, Westhofen, pp. 129–150.
Rosenberger, T. M. G. (1998), Prosodic font: The space between the
spoken and the written, Master’s thesis, MIT.
Ross, F. (2002), ‘Non-Latin type design at Linotype’, Paper de-
livered at the First annual Friends of St Bride conference,
Twentieth Century Graphic Communication: Technology, Soci-
ety, and Culture, London, 24–25 Sept. 2002.
<http://stbride.
org/friends/conference/twentiethcentury-graphiccommunication/
NonLatin.html>.
252
BIBLIOGRAPHY
Ryan, F. X. (1993), ‘Some observations on the censorship of Claudius
and Vitellus,
A.D. 47–48’,
American Journal of Philology
114(4), 611–618.
Saenger, P. (1991), The separation of words and the physiology of read-
ing, in D. Olson & N. Torrance, eds, ‘Literacy and Orality’, Cam-
bridge University Press, Cambridge, pp. 198–214.
Salomon, R. (1995), ‘On the origin of the early Indian scripts’, Journal
of the American Oriental Society 115(2), 271–279.
—–. (1998), Indian Epigraphy: A Guide to the Study of Inscriptions in
Sanskrit, Prakrit, and The Other Indo-Aryan Languages, Oxford
University Press, New York.
Sampson, G. (1985), Writing Systems: A Linguistic Introduction, Stan-
ford University Press, Stanford.
Sastri, B. (1987), ´Sr¯ımadbhagavatpatañjalimuniviracitam P¯atañjalam
Mah¯abh¯as.yam.
Kaiyat.op¯adhy¯ayapran. ¯ıtena Prad¯ıpena, N¯age´sa-
bhat.t.aviracitena Mah¯abh¯as.yaprad¯ıpoddyotena, 2d edn, V¯an.¯ıvil¯asa
Prak¯a´sana, Varanasi. [Sanskrit]. = The Mah¯abh¯as.ya of Patañjali
with Kaiyat.a’s Prad¯ıpa and N¯age´sa’s Uddyota. 8 vols. in 7. Origi-
nal edition: ´Sr¯ıgurupras¯ada´s¯astr¯ı-grantham¯al¯a, no. 1.
Scharf, P. M. (2003), R¯amop¯akhy¯ana:
The Story of R¯ama in the
Mah¯abh¯arata: An Independent-Study Reader in Sanskrit, Rout-
ledgeCurzon, London.
—–. (2009), Modeling P¯an.inian grammar, in Huet et al. (2009), pp. 95–
126.
Scharfe, H. (1977), Grammatical Literature, Vol. 5 fasc. 2 of A History
of Indian Literature, Harrassowitz, Wiesbaden. Jan Gonda, ed., pp.
72–216.
—–. (2002), ‘Kharos.t.h¯ı and Br¯ahm¯ı’, Journal of the American Oriental
Society 122(2), 391–393.
Schlesinger, C., ed. (1989), The Biography of Ottmar Mergenthaler, In-
ventor of the Linotype: A New Edition, with Added Historical Notes
Based on Recent Findings, Oak Knoll Press, New Castle DE.
BIBLIOGRAPHY
253
Schmidt, J. (1875), Zur Geschichte des Indogermanischen Vocalismus,
Vol. 2, Hermann Böhlau, Weimar.
Shallice, T. (1981), ‘Phonological agraphia and the lexical route in writ-
ing’, Brain 104, 413–429.
Shanbhag, S., Rao, D. & Joshi, R. K. (2002), An intelligent multi-layered
input scheme for phonetic scripts, in ‘Proceedings of the 2nd Inter-
national Symposium on Smart Graphics’, ACM Press, New York,
pp. 35–38.
Shapiro, L. P., McNamara, P., Zurif, E., Lanzoni, S., & Cermak, L.
(1992), ‘Processing complexity and sentence memory: Evidence
from amnesia’, Brain and Language 42(4), 431–453.
Sharma, R. (2002), Br¯ahm¯ı Script: Development in North-Western India
and Central Asia, B. R. Publishing, Delhi. 2 vols.
Sharma, V. V., ed. (1934), V¯ajasaneyi Pr¯ati´s¯akhya of K¯aty¯ayana:
With the Commentaries of Uvat.a and Anantabhat.t.a, Vol. 5
of Madras University Sanskrit Series, University of Madras.
va;a:ja;sa;nea;a;ya;pra;a;a;ta;Za;a;K.yMa k+:a;tya;a;ya;na;pra;¾a;a;tMa Ba;a;Sya;dõ;ya;ea;pea;ta;m,a.
Shastri, M. D., ed. (1931), The R
˚
gveda-pr¯ati´s¯akhya with the Commen-
tary of Uvat.a: Edited from Original Manuscripts, with Introduc-
tion, Critical and Additional Notes, English Translation of the Text,
and Several Appendices, Vol. 2: Text in S¯utra-Form and Commen-
tary with Critical Apparatus, The Indian Press, Allahabad.
—–, ed. (1937), The R
˚
gveda-pr¯ati´s¯akhya with the Commentary of Uvat.a:
Edited from Original Manuscripts, with Introduction, Critical and
Additional Notes, English Translation of the Text, and Several Ap-
pendices, Vol. 3: English Translation of the Text, Additional Notes,
Several Appendices and Indices, Motlilal Banarsidass, Lahore.
—–, ed. (1959), The R
˚
gveda-pr¯ati´s¯akhya with the Commentary of Uvat.a:
Edited from Original Manuscripts, with Introduction, Critical and
Additional Notes, English Translation of the Text, and Several
Appendices, Vol. 1: Introduction, Original Text of the R
˚
gveda-
pr¯ati´s¯akhya in Stanza-Form, Supplementary Notes, and Several Ap-
pendices, Vaidika Sv¯adhy¯aya Mandira, V¯ar¯anas¯ı.
254
BIBLIOGRAPHY
Shaw, G. B. (1962), Androcles and the Lion: an Old Fable Renovated
by Bernard Shaw; with a Parallel Text in Shaw’s Alphabet, to be
Read in Conjunction Showing its Economies in Writing and Read-
ing, Penguin, Harmondsworth.
Shaw, G. W. (1980), ‘Printing in Devanagari: The evolution of types
in Devanagari script’, The Monotype Recorder 2 (n. s.), 28–32.
:de;va;na;a;ga:=+a ;a;l+.
a;pa :ke f;a;I+.pa;eMa k+:a ;
a;va;k+:a;sa.
Shimron, J. & Navon, D. (1980), ‘The distribution of visual information
in the vertical dimension of Roman and Hebrew letters’, Visible
Language 14(1), 5–12.
Shoup, J. E. (1980), Phonological aspects of speech recognition, in
W. Lea, ed., ‘Trends in Speech Recognition’, Prentice-Hall, En-
glewood Cliffs NJ, pp. 125–138.
Simner, J., Ward, J., Lanz, M., Hansari, A., Noonan, K., Glover, L. &
Oakley, D. A. (2005), ‘Non-random associates of graphemes to
colours in synaesthetic and non-synaesthetic populations’, Cogni-
tive Neuropsychology 22(8), 1069–1085.
Singh, A. K. (1991), Development of Nagari Script, Parimal Publica-
tions, Delhi.
—–. (2006), ‘A computational phonetic model for Indian language
scripts’, Constraints on Spelling Changes:
Fifth International
Workshop on Writing Systems. Nijmegen, The Netherlands, Oc-
tober, 2006.
Singh, K. S. (1997), Languages and Scripts, number 9 in ‘People of India
National Series’, Oxford University Press, Delhi.
Skelton, C. (2008), ‘Methods of using phylogenetic systematics to recon-
struct the history of the Linear B script’, Archaeometry 50(1), 158–
176.
Smilek, D., Dixon, M. J. & Merikle, P. M. (2005), Binding of graphemes
and synesthetic colors in color-graphemic synesthesia, in Robertson
& Sagiv (2005), chapter 5, pp. 74–89.
BIBLIOGRAPHY
255
Smith, F., Lott, D. & Cronnell, B. (1969), ‘The effect of type size and
case alternation on word identiﬁcation’, American Journal of Psy-
chology 82(2), 248–253.
Smith, F. W. (1964), ‘New American Standard Code for Information In-
terchange’, Western Union Technical Review 18(2), 50–61.
Smith, G. (1885), The Life of William Carey, D. D.: Shoemaker and Mis-
sionary, Professor of Sanskrit, Bengali, and Marathi in the College
of Fort William, Calcutta, J. Murray, London.
Snowling, M. J. (2005), Dyslexia, in B. Hopkins, ed., ‘The Cambridge
Encyclopedia of Child Development’, Cambridge University Press,
Cambridge, pp. 433–436.
Snyman, J. W. (1970), An Introduction to the !X˜u (!Kung) Language,
A. A. Balkema, Cape Town.
Sonka, M., Hlavac, V. & Boyle, R. (1999), Image Processing, Analysis
and Machine Vision, 2d edn, PWS, Paciﬁc Grove CA.
Sproat, R. (2006), ‘Brahmi-derived scripts, script layout, and segmental
analysis’, Written Language & Literacy 9(1), 45–65.
Srihari, S. N., Srinivasan, H., Huang, C. & Shetty, S. (2006), ‘Spotting
words in Latin, Devanagari and Arabic scripts’, Vivek: Indian Jour-
nal of Artiﬁcial Intelligence 16(3), 2–9.
Staal, J. F. (1972), A Reader on the Sanskrit Grammarians, Motilal Ba-
narsidass, Delhi.
Steinberg, S. H. (1961), Five Hundred Years of Printing, 2d edn, Penguin,
Harmondsworth.
Stemberger, J. P. (1982), ‘The nature of segments in the lexicon: Evi-
dence from speech errors’, Lingua 56, 235–259.
Strasser, G. F. (1988), Lingua Universalis: Kryptologie und Theorie der
Universalsprachen im 16. und 17. Jahrhundert, Vol. 38 of Wolfen-
bütteler Forschungen, Harrasowitz, Wiesbaden.
256
BIBLIOGRAPHY
Suen, C. Y., Mori, S., Kim, S. H. & Leung, C. H. (2003), Analysis and
recognition of Asian scripts—the state of the art, in ‘Proceedings of
the 7th International Conference on Document Analysis and Recog-
nition’, pp. 866–878.
Sweet, H. (1892), A Manual of Current Shorthand, Orthographic and
Phonetic, Clarendon, Oxford.
Syropoulos, A., Tsolomitis, A. & Sofroniou, N. (2003), Digital Typog-
raphy Using LATEX, Springer, New York.
Szemerényi, O. (1967), ‘The new look of Indo-European: Reconstruc-
tion and typology’, Phonetica 17(2), 65–99.
Takakusu, J. (1896), Record of the Buddhist Religion as Practised in
India and the Malay Archipelago, Clarendon, Oxford.
Tolchinsky, L. (2003), The Cradle of Culture and What Children Know
About Writing and Numbers Before Being Taught, Erlbaum, Mah-
waw NJ.
Tomasello, M. (1999), The Cultural Origins of Human Cognition, Har-
vard University Press, Cambridge MA.
Treiman, R. (2006), Knowledge about letters as a foundation for reading
and spelling, in Joshi & Aaron (2006), pp. 581–599.
Trigger, B. G. (1998), ‘Writing systems: A case study in cultural evolu-
tion’, Norwegian Archaeological Review 31(1), 39–62.
Trigo Ferre, R. L. (1988), The Phonological Derivation and Behavior of
Nasal Glides, PhD thesis, MIT, Cambridge MA. MIT Dissertations
in Linguistics TRIG01.
Tversky, A. (1977), ‘Features of similarity’, Psychological Review
84(4), 327–352.
Unicode Consortium (2006), The Unicode Standard, Version 5.0,
Addison-Wesley, Boston.
Vacek, J. (1976), ‘The Sanskrit sibilants’, Wissenschaftliche Zeitschrift
der Humboldt-Universität zu Berlin, Gesellschafts und sprachwis-
senschaftliche Reihe 25(3), 407–412.
BIBLIOGRAPHY
257
Vachek, J. (1973), Written Language: General Problems and Problems
of English, number 14 in ‘Janua Linguarum Series Critica’, Mou-
ton, The Hague.
Vaid, J. (2002), ‘Exploring word recognition in a semi-alphabetic script:
The case of Devanagari’, Brain and Language 81, 679–690.
van den Bosch, A., Content, A., Daelemans, W. & de Gelder, B. (1994),
‘Measuring the complexity of writing systems’, Journal of Quanti-
tative Linguistics 1(3), 178–188.
van Nooten, B. A. (1973), The structure of a Sanskrit phonetic treatise,
in I. Konks, P. Numerkund & L. Mall, eds, ‘Oriental Studies’, Toid
Orientalistika Alalt; Trudy po Vostokovedeniju II 2, Tartu Univer-
sity, Tartu, pp. 408–436.
Varma, S. (1929), Critical Studies in the Phonetic Observations of In-
dian Grammarians, Royal Asiatic Society, London. Reprint: Delhi:
Munshiram Manoharlal, 1961.
Vedavrata, ed. (1962–1963), Patañjali’s Vy¯akaran. amah¯abh¯as.ya with
Kaiyat.a’s Prad¯ıpa and N¯agoj¯ıbhat.t.a’s Uddyota, Hary¯an. ¯a S¯ahitya
Sa ˙msth¯ana, Gurukula Jhajjar (Rohatak).
Velten, H. V. (1956), Hedgehogs Versus foxes in comparative linguistics,
in M. Halle, H. G. Lunt, H. McLean & C. H. van Schooneveld,
eds, ‘For Roman Jakobson: Essays on the Occasion of His Sixtieth
Birthday, 11 October 1956’, Mouton, The Hague, pp. 585–587.
Vincent, D. (2000), The Rise of Mass Literacy: Reading and Writing in
Modern Europe, Polity, Cambridge.
Voigt, R. (2005), ‘Die Entwicklung der aramäischen zur Kharos.t.h¯ı-
und Br¯ahm¯ı-Schrift’, Zeitschrift der Deutschen Morgenländischen
Gesellschaft 155, 25–50.
Vygotskii, L. S. (2005), Pedagogicheskaia psikhologiia, AST-Astrel-
Liuks, Moscow.
Walden Font (1997), ‘The Gutenberg press: Five centuries of German
Fraktur’, <http://www.waldenfont.com/downloads/gbpmanual.
pdf>.
258
BIBLIOGRAPHY
Waller, R. (1986), ‘What electronic books will have to be better than’,
Information Design Journal 5(1), 72–75.
—–. (1988), The Typographic Contribution to Language: Towards a
Model of Typographic Genres and Their Underlying Structures,
PhD thesis, University of Reading.
Ward, J. & Romani, C. (2000), ‘Consonant-vowel encoding and ortho-
syllables in a case of acquired dysgraphia’, Cognitive Neuropsy-
chology 17(7), 641–663.
Ward, J., Simner, J. & Auyeung, V. (2005), ‘A comparison of lexical-
gustatory and grapheme-colour synaesthesia’, Cognitive Neuropsy-
chology 22(1), 28–41.
Watson, P. J. & Hixon, T. J. (1987), Respiratory kinematics in classical
(opera) singers, in Respiratory Function in Speech and Song (Hixon
& Collaborators, 1987), chapter 10, pp. 337–374.
Weir, R. H. (1967), Some thoughts on spelling, in W. M. Austin, ed., ‘Pa-
pers in Linguistics in Honor of Léon Dostert’, Mouton, The Hague,
pp. 169–177.
Wennerstrom, A. (2001), The Music of Everyday Speech: Prosody and
Discourse Analysis, Oxford University Press, New York.
White, A. (2002), ‘The Unicode Standard for Scripts of India (TUSSI):
A request to make the TUSSI speciﬁcation compatible with the
ISCII standard, and beyond’, <http://www.exnet.btinternet.co.uk/
uniprop/encoding.htm>.
Whitney, W. D. (1861), ‘On Lepsius’s standard alphabet’, Journal of the
American Oriental Society 7, 299–332.
—–. (1862), ‘The Atharva-veda-prâtiçâkhya, or Çâunakîyâ catur-
âdhyâyikâ: Text, translation, and notes’, Journal of the American
Oriental Society 7, 333–615.
—–. (1868), ‘The Tâittirîya-Prâtiçâkhya, with its commentary, the Tri-
bhâshyaratna: Text, translation, and notes’, Journal of the Ameri-
can Oriental Society 9, 1–469.
BIBLIOGRAPHY
259
—–. (1880), ‘On the transliteration of Sanskrit’, Journal of the American
Oriental Society 11(Proceedings of the American Oriental Society
at New York, October, 1880), li–liv.
—–. (1889), Sanskrit Grammar: Including Both the Classical Language,
and the Older Dialects, of Veda and Brahmana, 2d edn, Harvard
University Press, Cambridge MA.
Wikner, C. (2002), ‘Sanskrit for LATEX2ε, Version 2.2’, <http://www.
ctan.org/tex-archive/language/sanskrit/sktdoc.ps>.
Williams, C. E. & Stevens, K. N. (1981), Vocal correlates of emotional
states, in Darby (1981), pp. 221–240.
Windisch, E. (1917), Geschichte der Sanskrit-Philologie und indischen
Altertumskunde, Karl J. Trübner, Strassburg. Reprint: Berlin: De
Gruyter, 1992.
Wissink, C. (2001), ‘Issues in Indic language collation’, Paper delivered
at the 19th Int. Unicode Conference, San José, CA, Sept. 2001.
<http://www.unicode.org/notes/tn1/Wissink-IndicCollation.pdf>.
[= Unicode Technical Note #1].
Witzel, M. (1974), ‘On some unknown systems of marking the Vedic
accents’, Vishveshvaranand Indological Journal 12, 472–502. [=
Vishvabandu Commemoration Volume].
—–. (1999), ‘Substrate languages in old Indo-Aryan (R
˚
gvedic, Mid-
dle and Late Vedic)’,
Electronic Journal of Vedic Studies
5(1), 1–67.
<http://www.ejvs.laurasianacademy.com/ejvs0501/
ejvs0501article.pdf>.
Wollen, K. A. & Ruggiero, F. T. (1983), ‘Colored-letter synesthesia’,
Journal of Mental Imagery 7(2), 83–86.
Wujastyk, D. (1990), ‘Standardization of Sanskrit for electronic data and
screen representation’, <http://www.tug.org/tex-archive/fonts/csx/
docs/charset.ps>.
—–. (1996), ‘Transliteration of Devan¯agar¯ı’, <http://www.ucl.ac.uk/
~ucgadkw/members/transliteration/translit.pdf>.
260
BIBLIOGRAPHY
Zwicky, A. M. (1965), Topics in Sanskrit Phonology, PhD thesis, MIT.
MIT Working Papers in Linguistics.
Index
!Kung, see !X˜u
!X˜u, 55
A Grammar of the Sanskr˘ıta
Language, 109
A. H. Harley, 19
Aklujkar, Ashok, 64
ala˙nk¯ara´s¯astra, 119, 120
All-India Alphabet, 18
Allen, W. Sidney, 19, 20, 66
alphabet, see writing system,
alphabetic
American Oriental Society, 16
ANSI, 6
Apabhra ˙m´sa, 8
¯Api´sali, 76, 78, 79, 124, 126, 128,
134
Arabic, 49, 55, 57, 103
calligraphy, 4
grammarians, 14
numerals, see numerals,
Indo-Arabic
script, see script,
Perso-Arabic
ArabTEX, 35
Aramaic, 14
script, see script, Aramaic
Aristotle, 4
ARPAbet, 59
ASA, 6, 74
ASCII, see encoding systems,
ASCII
A´soka, 10
Assamese, 29
As.t. ¯adhy¯ay¯ı, 88, 102
Avestan, 34
Bacon, Francis, 6
Bailey, Thomas Grahame, 19
Baudot, Emile, 6
Bell, Alexander Melville, 55, 75
Bengali, 23, 29, 30, 36, 117
Bhaskararao, Peri, 64
Bhat.t.ojid¯ıks.ita, 73
Bible, 3
Bigelow, Charles, 106
Bloomﬁeld, Maurice, 39
Böhtlingk, Otto, 46
Book of Hours, 4
British Library, 4
Brown, W. Norman, 24
Brugmann, K., 142
Buddhist Hybrid Sanskrit, 91
Burmese, 19
Burrow, T., 140, 142, 144
Busa, Roberto, 7
C-DAC, 30, 38
261
262
INDEX
calligraphy, 12, 19
Cardona, George, 64
Carey, William, 23
CDSL, xii
character, 3, 6, 7, 10–12, 17, 19,
23–26, 28–32, 34, 35,
37, 39, 42–45, 47, 49,
53, 54, 57, 58, 97, 98,
103, 105–110, 113, 114
alphanumeric, 34
confusion, 107
control, 28–30, 34, 39
Devan¯agar¯ı, 38, 56, 106, 110
meta-character, 35
natural, 55
style, 30
character encoding, 6, 7, 30, 41,
51, 58, 94–96
digital, xiii
character-glyph model, 31
CHILDES, 59
Chinese, 19, 106
Chopde, Avinash, 36
Christianity, 58
Church, William, 4
cinema, 2
cipher
“biliteral”, 6
cladistics, 107
Clements, G. N., 77, 78, 124
clicks, 55
code position, see codepoint
codepoint, 25, 29, 33–35, 38, 47,
57, 98, 116, 151, 152,
159, 205
codex, 4
Colebrook, H. T., 23
Colloquial Hindustani, 19
color, 49, 50, 101
Congregatio de Propaganda Fide,
23
dance, 48, 88
data transmission, 1, 7, 28, 56,
113, 116
DDSA, xii
deixis, 48
Delambre, Adrian, 4
Deshpande, Madhav M., 64, 72,
91
desktop publishing, 6, 113
diacritic, 10, 11, 14, 15, 17, 18,
20, 25, 26, 29, 30, 34,
35, 39, 49, 114
stacking, 35
digital images, xii, 4
Doutrina Christã, 21
Dravidian languages, 34, 37, 64,
see also Kannada;
Malayalam; Tamil;
Telugu
Dürer, Albrecht, 103
encoding systems, 2, 21–47, 50,
52, 57, 79, 91–93, 96,
98, 113
ASCII, xxi, 6, 25, 28, 33–38,
58, 59, 98, 113, 151
BCDIC, 25
CCITT, xxi, 6, 25
CP 437, 33, 34
CS, see encoding systems,
CSX
CSX, 32–33
INDEX
263
CSX+, see encoding systems,
CSX
IPA, see IPA
ISCII, 28–30, 38
ISO
ISO 646, 6
ISO/IEC TR 15285, 31
ISO 10646, 30, see also
encoding systems,
Unicode
ISO 15919, 17, 33, 35
ISO 8859-1, 58
ITRANS, 36, 118
Kyoto-Harvard, 36, 37, 118
PHONASCII, see
PHONASCII
proprietary, 26, 27
TITUS Indological, 33–34
Unicode, xiii, 9, 17, 28,
30–35, 38, 39, 55, 58,
59, 113, 117, 160
Velthuis, 36
wx, 36, 37, 118
engraving, 21, 109
ergonomics, 6, 28, 118
Everson, Michael, 30
exstrastriate cortex, 50
Fano condition, 35, 36, 46, 151
Fano, Robert M., see Fano
condition
Fant, Carl Gunnar Michael, 76
Farsi, see Persian
Finnish, 51
Firth, J. R., 18–20, 53
font, 3, 27, 33, 35, 58
Computer
Modern, 107
Devanag, 107
Devan¯agar¯ı, 12, 21, 23, 24,
26, 27
Indic, 24, 28
METAFONT, 107
NCSD, 107, 110
Prosodic Font, 105
TrueType, 34
Fourier analysis, 54
free-word-order language, xii, 120
French, 59
Fritz, Johann Friedrich, 21
Fry, A.H., 83
fusiform gyrus, 50
Gandhi, Mahatma, 24
German, 18
Ghosh, Pijush K., 110
Gippert, Jost, 33
Glidden, Carlos, 6, see also
typewriter
glyph, 12, 26, 29, 31, 103, 107,
110
Goa, 21
Gonçalves, João, 21
Google Books, xii
grammar
context-free, 110
generative, xii, 80, 84–85
visual, 104
Granjon, Robert, 4
graphotactic, 12, 103
Greek, 4, 15
script, see script, Greek
de Gregorii, Gregorio, 4
GRETIL, xii
Gujarati, 18, 19, 24, 29, 30, 36,
64, 117
264
INDEX
Gurmukhi, 117
Gutenberg, Johannes, 3
Halhed, Nathaniel Brassey, 23
Halle, Morris, 76–78, 98, 124,
126, 205
Hàn Zì software, 106
handwriting, see writing
handwriting recognition, 55, 103,
105
Haralambous, Yannis, 32
Hebrew, 4
hiatus, 15, 81
Hindi, 9, 11, 19, 20, 24, 37
newspapers, 25
script, see script, Devan¯agar¯ı
voiced aspirate stops, 66
Hindustani, 8
Hock, Hans Henrich, 64, 109
Hofstadter, Douglas, 106, 107
Holmes, Kris, 106
Hyman, Malcom, 215
illiteracy, 18, see also literacy
Index Thomisticus, 7
Indic
Middle, 33
Modern, 33, 37, 64
Old, 33
IndiX, 38
Indo-Aryan
Middle, 8, 9, 64
New, 8
Old, 81, 86
Industrial Revolution, 4
information processing, 2, 7, 28,
103, 113
International Digital Sanskrit
Library Integration
Project, xii
Internet, 27
IPA, 18, 20, 39, 59, 117, 159, 161
Irani, Alka, 30
ISCII, see encoding systems,
ISCII
Ivanov, V. V., 76
Jakobson, Roman, 76, 85
Japanese, 10, 19
Jesuits, 21
Johann Wilhelm von Goethe
Universität, 33
Jones, Daniel, 18, 19
Jones, Sir William, 55
Joshi, R. K., 30, 38–40, 110, 111
Kannada, 29, 36, 117
karmam¯ım¯a ˙ms¯a, 119
Kashmiri, 29
Kathakali, 1
kerning, 24
keyboard, 4, 6, 28
computer, 6
input, 39
layout, 25, 26, 28, 118
Dvorak, 28
QWERTY, 118
Kircher, Athanasius, 21, 22
Knuth, Donald, 28, 106, 107
Koran, 49
Kulkarni, Amba, 37
Ladefoged, P., 66
Lagally, Klaus, 35
Lakhdar-Ghazal, Ahmed, 26
INDEX
265
Lata, Swaran, 30
LATEX, 36
Latin, 3, 8, 58
script, see script, Roman
Leake, David, 106
Lepsius, 14, 16
letter, see character
letter case, 20, 25, 33, 37, 38, 98,
104, 105, 108
letterform, 3, 4, 20, 26, 101, 107,
108, 110
lex, 117
Library of Congress, 17
license
GPL, 33
ligature, 4, 11, 12, 26, 28, 31, 32,
106
linguistic encoding, xiii, 79, 115,
119, 120
Linotype, 4, 6, 24
literacy, 3, 19, 102
mass, 3
scribal, 3
literature
English language, 58
Sanskrit, 2, 8, 9, 59, 114
loanword, 11, 87, 93, 94, 98
Lord’s Prayer, 23
Louis XIV, 103
machine translation, 7, 27, 113
machine-readable, xii, 101, 119
Malayalam, 8, 29, 117
manuscripts, 2, 3, 48, 49, 51, 57,
101, 103, 108, 116, 160
length of, 53
Sanskrit, 8
Vedic, 49
Manutius, Aldus, 4
Marathi, 8, 9, 19, 20, 24, 64
margins, 101
media, 7, 48
communications, 2
digital, 1
electronic, xiii
new, 103
Mergenthaler, Ottmar, 6
METAFONT, 106
Middle East, 25
monospacing, 6
Monotype, 4, 24
morphological analysis, 7, 27, 37,
113, 120
movable type, 3, 7, 113
Müller, Friedrich Max, 66
Nage´sa, 72
Natural Language Processing: A
Paninian Perspective, 37
n¯at.ya´s¯astra, 120
NCST, 110
Nehru, Jawharlal, 24
Nepali, 9, 24
neural network, 106
The New Asiatick Miscellany, 23
Nirukta, 64, 94
NLP, 8, 37
NSF, xii, xiii
numerals, 15, 39, 83, 98
Devan¯agar¯ı, 25
Indo-Arabic, 48, 105
ny¯aya, 119
OCR, 54, 103, 105, 106, 108
operating system
GNU/Linux, 38
266
INDEX
Microsoft Windows, 33
MS-DOS, 33
oral tradition, 1, 2, 8, 58, 59, 102,
114
Oriya, 29, 64, 117
orthographic depth, 51
orthographic legality, 11
orthographic syllable, 10, 11, 14,
15, 27, 38, 108
orthography, 2, 11, 12, 17–20, 25,
49–51, 59, 113, 115
Devan¯agar¯ı, 42, 59
English, 51, 58
European, 25, 34
national, 18
pedagogy of, 58, 110
phonetic, 2
reform of, 24–26, 49
scientiﬁc, 19
World Orthography, 18
orthosyllable, see orthographic
syllable
orthotactic constraints, 11
palaeography, 107
P¯al¯ı, 8
P¯an.ini, xii, 61, 66, 67, 72–73,
79–80, 88, 83–85, 96,
102, 132
Panjabi, 29, 36, 70
Pañjik¯a, 70
P¯ari´siks. ¯at.¯ık¯a Y¯ajus.abh¯us.an. a, 63
Patañjali, 52, 57, 64, 72, 84
Pattern Primitive Set, 110
perceptron, 106
Phaedrus, 102
PHONASCII, 59
phonetic input method, 118
phonology
English, 58, 62
foreign, 87
non-European, 114
Proto-Indo-European, 142,
144
Sanskrit, 51, 59, 61–78, 86,
92–93, 115, 124, 126,
128, 130, 132, 134, 136,
138, 140, 159
phonotactics, 36, 64, 66, 67
phonotypy, see Pitman, Isaac
phylogenetic analysis, 107
Pitman, Isaac, 55
Plato, 7
poetry, 1, 102, 119
polygraph, 17
Pr¯akrit, 8, 9, 51, 86, 91
Pr¯ati´s¯akhyas, 61, 72, 84, 155, 157
Atharvavedapr¯ati´s¯akhya, 75
Catur¯adhy¯ayik¯a, 90
Catur¯adhy¯ayik¯abh¯as.ya,
63, 72
R
˚
kpr¯ati´s¯akhya, 65–69, 75,
81, 93, 95, 99, 156
Taittir¯ıyapr¯ati´s¯akhya, 65, 66,
74, 155
Tribh¯as.yaratna, 72
V¯ajasaneyipr¯ati´s¯akhya,
66–67, 93, 95, 96, 99,
155
preﬁx code, see Fano condition
printing, xiii, 2, 4, 6, 7, 58, 101,
103
Devan¯agar¯ı, 21
press, 3–4, 8, 21
Sanskrit, 9, 21–25
INDEX
267
Proto-Indic, 86
Proto-Indo-European, 86, 140
Proto-Indo-Iranian, 81, 86
Proto-N¯agar¯ı, 9
Rajasthan, 9
R¯amop¯akhy¯ana, xii
rasa, 120
Rastogi, S. I., 67
regular expression, 11
Remington, 6
R
˚
gvedic, 15, 45, 64, 82, 94–95
Romain du Roi, 103
Rome, 23
Rosenberg Graphical System, 106
Roth, Rudolf, 46
Russian, 17, 85, 86
script, see script, Cyrillic
´S¯akap¯un.i, 94
sandhi, 15, 38, 64, 93, 103
Sanskrit Computational
Linguistics Consortium,
xii
Sanskrit Library, xii, 31, 117, 151,
159, 160, 205
´Satapathabr¯ahman. a, 84
´Saunaka, 75, 78, 124, 128, 136
Scharf, Peter, xii
Schulze, Benjamin, 21
script, 28, 39, 47, 48, 50, 52, 103,
115
Aramaic, 9, 12, 51
behaviors, 29
Br¯ahm¯ı, 9, 10, 14, 29, 51, 108
complex, 26
Cyrillic, 18
Devan¯agar¯ı, 9–15, 17, 21,
22–24, 27, 29–31,
34–36, 39, 41, 42,
44–47, 49, 51, 52, 59,
62, 97, 103, 107–110,
114, 115, 117, 148, 159,
160
futhorc, 58
gothic, 4
Greek, 10, 12, 18, 54
han’g˘ul, 54
Hiragana, 10
Indic, 11, 17, 23, 29–32, 38,
108, 117, 118
Katakana, 10
Kharos.t.h¯ı, 9, 14, 51
non-Western, 25, 114
Perso-Arabic, 4, 26, 29, 31,
45, 49
Roman, 9, 16–18, 24, 25, 31,
34, 46, 47, 52, 58, 88,
98, 104, 105, 107, 110,
114, 115, 117, 159
Semitic, 14
Shavian, 55
Sharma, V.V., 67
Shaw, George Bernard, 55
Sheeba, V., 37
Sholes, Christopher Latham, 6, see
also typewriter
shorthand, 55
´Siks. ¯as, 61, 64, 97, 119, 157
¯Api´sali´siks. ¯a, 65, 68, 73–75
Malla´sarmakr
˚
ta´siks. ¯a, 96,
158
P¯an. in¯ıya´siks. ¯a, 69, 70, 158
Varn. aratnaprad¯ipik¯a´siks. ¯a, 97
268
INDEX
Sindhi, 29, 70
SLP1, 36, 37, 98, 116, 117,
151–158
SLP2, 97, 98, 116, 159–203
SLP3, 98, 116, 118, 205–214
Socrates, 102
spell checking, 7, 27, 113
St. Xavier, 21
Stanford University, 28
Steever, Sanford, 64
stepped distance function, 107
subglottal pressure, 66
Sweet, Henry, 55
syllabary, see writing system,
syllabic
synesthesia, 50
syntactic analysis, 7, 113, 120
Szemerényi, O., 86, 144
Talairach space, 50
Tamil, 8, 18–20, 29, 33, 36, 64
printing, 21
Teach Yourself Urdu, 19
teletype, 6, 113
Telugu, 18, 19, 29, 36, 117
TEX, 28, 33, 36, 107, see also
LATEX
text processing, 2, 25, 26, 114
Text-Encoding Initiative, 120
text-to-speech, 118
theater, 1, 2
tone-letter system, 161
Toporov, V. N., 76
typecase, 4, 6, 25
typeface, see font
typesetting, 18, 20, 36, 160
digital, 6
hot metal, 24, 113, see also
Linotype, Monotype
typewriter, 6, 7, 19, 20, 25, 113
Hindi, 25–27
typography
Indic, 107
Sanskrit, 26
Ubykh, 55
UNESCO, 27
Unicode, see encoding systems,
Unicode
Universal Digital Library, xii
University of London, 19
University of Pennsylvania, xii, 24
University of Punjab, 18
UPACCII, 28
Urdu, 19, 29
Uttar Pradesh, 24
varn. am¯al¯a, 38–40
Vedas, 9
Atharvaveda, 46, 160
R
˚
gveda, 46, 95, 160
S¯amaveda, 81
V¯ajasaneyisa ˙mhit¯a, 46, 63,
81, 89, 95, 97
Yajurveda, 46, 69, 70, 95, 97,
160
Vedic, xiii, 30, 33, 37, 64, 91, 152,
153, 155
accent, 15
dialects, 81, 89, 91, 95, 96
hymns, 61
in ISCII, 30
in Unicode, 31
phonetic treatises, 63–65, see
also Pr¯ati´s¯akhyas, 156
INDEX
269
recitation, 49, 63
sa ˙mhit¯a, 95
schools, 30, 61, 67, 84, 95, 97
Vedic Sanskrit Coding Scheme,
see varn. am¯al¯a
Velthuis, Frans, 36, 107
visible speech, see Bell, Alexander
Melville
visual art, 1, 48, 88
visual word form area, 50
vy¯akaran. a, 119
Vygotsky, L. S., 101
Ward, Ida Caroline, 66
Westermann, Diedrich, 66
Whitney, William Dwight, 16, 46,
66, 72
Wikner, Charles, 36, 107
Wilkins, Charles, 23, 109
Williams, Monier, 39
word spotting, 105
World Wide Web, xii, 27, 33
writing, xiii, 2–4, 7, 9, 12, 27, 29,
31, 41, 50, 51, 54, 55,
59, 101–103, 108, 115
cursive, 105
ease of, 20
implements, 53
proto-writing, 2
writing system, 4, 9, 13, 18, 23,
27, 29, 49, 51, 54, 55,
107, 108, 115
alphabetic, 10, 16
artiﬁcial, 55
borrowing of, 51
East Asian, 103
ideographic, 49
logographic, 49
non-glottographic, 39
phonographic, 49
Roman, 19
syllabic, 10
XML, 93, 95, 120
Y¯aska, 94
Yijing, 9
Young, James, 4
Ziegenbalg, Bartholomew, 18
Zwicky, Arnold M., 76
