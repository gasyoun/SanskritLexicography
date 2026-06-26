# Performance of a Lexical and POS Tagger for Sanskrit

**Authors:** Oliver Hellwig (SAI, Universität Heidelberg)  
**Venue:** 4th Intl. Sanskrit Computational Linguistics Symposium (LNCS 6465), pp. 162–172  
**Extracted from:** Performance_of_a_Lexical_and_POS_Tagger.pdf (full ISCLS-4 proceedings, 275 pp.) — this file is the cited paper only (PDF pages 178–188), sliced out of the full proceedings bundle so it can be mined directly.

---

Performance of a Lexical and POS Tagger
for Sanskrit
Oliver Hellwig
SAI, Universit¨at Heidelberg, Germany
hellwig7@gmx.de
Abstract. Due to the phonetic, morphological, and lexical complexity
of Sanskrit, the automatic analysis of this language is a real challenge
in the area of natural language processing. The paper describes a se-
ries of tests that were performed to assess the accuracy of the tagging
program SanskritTagger. To our knowlegde, it oﬀers the ﬁrst reliable
benchmark data for evaluating the quality of taggers for Sanskrit us-
ing an unrestricted dictionary and texts from diﬀerent domains. Based
on a detailed analysis of the test results, the paper points out possible
directions for future improvements of statistical tagging procedures for
Sanskrit.
1
Overview and Previous Research
The quality of automatic language analysis methods is one of the central issues
in natural language processing (NLP). Most research in this area concentrates
on English and the voluminous corpora available in this language. For example,
the tagsets and the precision of the POS tagging applied to the Penn treebank
were described in [6]. The authors used a small POS tagset that consisted of 48
categories and included tags such as “existential there” and “comma”. Applying
“a cascade of stochastic and rule-based taggers” to the treebank, they obtained
an error rate of 2-6% using this tagset. A similar approach is found in [5] where
CLAWS4, a tagger for the British National Corpus, is described. The authors
used a multi-level model for analysis and reported error rates of 1-5% for POS
tagging. In more recent publications, however, it has been pointed out that
many of the assumptions on which the popular NLP systems for English are
based do not apply to other languages. For tagging Hungarian, for instance, a
completely diﬀerent tagset was used in [2]. This tagset consisted of 744 tags,
thus even exceeding the size of the tagset applied by SanskritTagger. Using
a morphological analyzer and a maximum entropy model, the authors reported
error rates of 1-3% for POS assignment in a Hungarian corpus.
Obviously, the precautions brought forward in [2] apply to the computational
analysis of Sanskrit to an even higher degree. Like in Hungarian, the linguistic
complexity of Sanskrit is partly caused by its inﬂectional nature. In addition,
the automatic processing of Sanskrit faces a number of problems that occur on
diﬀerent levels of language analysis and are not well studied in NLP literature
dealing with European and especially Germanic languages:
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 162–172, 2010.
c
⃝Springer-Verlag Berlin Heidelberg 2010

Performance of a Lexical and POS Tagger for Sanskrit
163
1. Segmenting a Sanskrit phrase into its inﬂected components is the ﬁrst and
perhaps most demanding task in the analysis of Sanskrit texts. This situation
is mainly caused by the phonetic rules called Sandhi, and it is aggravated by
the almost complete absence of typographic conventions such as punctuation
or the lower/upper case opposition, which is so useful in analyzing German
texts. Similar problems are, for example, known from the automatic pro-
cessing of Chinese, where word segmentation is a well-studied, though not
satisfactorily solved problem (cmp. [8] for an overview of this area).
2. On a higher level of linguistic analysis, the large number of homonyms and
the comparatively free word order complicate the automatic processing of
Sanskrit. Studies performed for languages whose word order is less regi-
mented than in English suggest that tagging strategies that are based on
positional information are less successful in processing such languages (see,
for example, [7, 280]). The situation is further complicated by the structure
of digital dictionaries of Sanskrit. Many of these dictionaries are not designed
for the needs of NLP, but are created from scanned versions of printed dictio-
naries. Due to the exigencies of philological work, many printed dictionaries
contain collocations or inﬁnite verbal forms that may be interesting from a
philological perspective, but deteriorate the quality of automatic processing.
This means that the stages of processing Sanskrit diﬀer strongly from what
is known for European languages and especially English. To analyze Sanskrit
phrases, a multi-level strategy had to be designed whose single components are
much more entangled than in the processing of European languages (cmp. [4]).
Due to these diﬀerences in the analysis process and thus in the test design, POS
error rates found for European languages are hardly comparable with those for
Sanskrit.
The following section ﬁrst sketches the basic ideas of the tagging process
applied in SanskritTagger and then describes the testing procedure and its
results.
2
Testing the SanskritTagger
2.1
The Test Design
In the statistical model used by SanskritTagger, the result of the analysis is
inﬂuenced by two factors: The language data from which statistical key values
are estimated and the procedures that make use of these statistical values to
analyze a given piece of text. Since the procedures were outlined in [4], we will
concentrate on the question of how the lexical data and the amount of data used
for training inﬂuences the quality of the analysis.
To begin with, let us shortly reconsider some details of the analysis process
to make clear on which kind of data the analysis is based. In the following, W
denotes an uninterrupted string, this means a string of letters that does not
contain break markers such as spaces or dan. d. as. If W is formed correctly, it can
be split into at least one substring wi, which is a grammatically correct Sanskrit
form. SanskritTagger divides the analysis of W roughly into three stages:

164
O. Hellwig
1. Initially, a list of candidate solutions is generated for each substring wi that
may be contained in W. The number of candidate solutions depends on
the well-known features that complicate the computational (and human!)
analysis of Sanskrit: the number of possible Sandhi breakpoints and the
morphological and lexical complexity of wi.
2. In the second step, the program searches for a path through the elements
of the candidate lists that is optimal from the perspective of phraseology or
lexicography. The path is calculated using a ﬁrst-order Markov chain whose
parameters (i.e., relative frequencies of single lexemes and transition proba-
bilities between bigrams of lexemes) are the statistical key values mentioned
above (cmp. [4, 273/74]). These values are estimated from the texts stored in
the database of SanskritTagger. As a ﬁrst hypothesis, we may assume that
the size of this text database strongly inﬂuences the quality of the estimated
parameters and, therefore, also the accuracy of the analysis. At this point,
it should be taken into consideration that previous research has shown that
the correlation between the amount of training data and the analysis quality
is not linear (see, e.g., [9, 363ﬀ.] for an early treatment of this problem).
Therefore, we will variate the number of texts used to calculate these pa-
rameters for reaching a realistic picture of how the accuracy of the tagging
is inﬂuenced by the size of the text database (cmp. page 168).
3. After the candidate lists have been ﬁltered by lexical criteria, the third stage
of the analysis process uses similar methods to ﬁnd an optimal POS path
through the remaining candidates. The role of the text database and the
parameter estimation corresponds with the scenario described in the second
step.
For performing the tests, we used the standard leave-one-out strategy with con-
sistent train-test splits. First, the set T of all texts t that contain more than
10.000 words was retrieved from the corpus.1 Next, for each t ∈T, the statis-
tical data was rebuilt without including t, and t was analyzed using this data
and the built-in routines of SanskritTagger. To evaluate the test result, the
new analysis anew of each separable string was compared with the analysis of
the string aDB that is stored in the program database. This step seems trivial
at ﬁrst view. However, consider the following case:
String: kr.s.n. ap¯adasevanatatparah.
aDB:
kr.s.n. a-p¯ada-sevana-tatparah.
anew:
kr.s.n. a-p¯adasevana-tatparah.
If the new analysis anew were marked as completely wrong, the error rate would
be overestimated because 2 of 4 lexemes (kr.s.n. a and tatpara) were identiﬁed
correctly. Therefore, we had to devise an evaluation procedure that was able to
cope with such imperfect matches.
A simple solution of this problem is oﬀered by alignment techniques (see [3]
for a survey of techniques for pairwise alignment and [1, 368ﬀ] for an Indological
1 The only large text that was skipped is the Mah¯abh¯arata, whose processing time
would have amounted to several hours.

Performance of a Lexical and POS Tagger for Sanskrit
165
application of such algorithms). The basic idea of these techniques can be sketched
as follows. Given two vectors of symbols v1 and v2, a matrix is created that has the
dimensions (|v1|+1)·(|v2|+1). The ﬁrst row and the ﬁrst column of the matrix are
ﬁlled with ascending numbers, i.e., c[i,1] = i −1 for the ﬁrst row and c[1,i] = i −1
for the ﬁrst column. Now, the comparison algorithm ﬁlls the remaining |v1| · |v2|
cells of the matrix. The value c[x,y] of each cell [x, y] is calculated by inspecting
the three preceeding cell values c[x,y−1], c[x−1,y] and c[x−1,y−1]:
c[x,y] = min
⎧
⎨
⎩
c[x,y−1] + γ
c[x−1,y] + γ
c[x−1,y−1] + compare(v1x, v2y)
γ is the gap penalty with which the non-alignment of two symbols is penalized.
compare(v1x, v2y) is a function that compares the symbols v1x and v2y, which
are represented by the analysis of a substring stored in the database (v1x) and
its new analysis (v2y) in our case. The value of compare ranges from 1 (= v1x
and v2y are derived from diﬀerent lexemes) to 0 (= v1x and v2y are identical).
It is calculated by inspecting to which degree the analyses of v1x and v2y are
diﬀerent. A diﬀerence in the lexical analysis is the most severe kind of error
because it invalidates the following morphological and POS analysis. compare
returns 1 in this case. This kind of error is caused by two scenarios. In the
ﬁrst scenario, the string is segmented diﬀerently in the database and by the
new analysis. The string kr.s.n. ap¯adasevanena may, for instance, be analyzed as
kr.s.n. a[comp.]-p¯ada[comp.]-sevanena[instr.] in the database, but as kr.s.n. a[comp.]-
p¯adasevanena[instr.] by the new analysis. In many cases, these errors are caused
by redundancies found in the Sanskrit dictionaries (cmp. page 163). In the second
scenario, both procedures have split the string in the same way, but have assigned
diﬀerent lexemes to at least one substring. In our example, this may result in
analyses such as “the worship of the feet of Kr.s.n.a” in the database and “the
worship of black feet” by the new analysis due to the homonymy of the noun
and the adjective kr.s.n. a. A more detailed analysis of this class of errors is given
in section 2.2. If the lexical analysis has succeeded, errors may occur in the
morphological and POS analysis of the words (third step of the analysis). The
most frequent types of errors are caused by bahuvr¯ıhi composites whose diﬀering
gender is not recognized correctly, and by morphologically ambiguous forms
such as vanam, which may be a nominative, an accusative, or a vocative. In
these cases, compare returns a positive value larger than zero that represents
the number of correct decisions the algorithm has made. Errors in the analysis
of a noun, for example, can occur during the four stages of lexical analysis, this
means in case, number, and gender. If the lexical analysis, case, and number
were recognized correctly, compare returns 3
4 = 0.75.
After the algorithm has traversed the whole matrix, the cell c[|v1|+1,|v2|+1]
contains the accumulated costs of the optimal alignment of v1 and v2. This
value may be used to calculate a measure of quality e for the analysis process:
e(v1, v2) = 1 −
c[|v1|+1,|v2|+1]
γ · max(|v1|, |v2|).

166
O. Hellwig
Using γ · max(|v1|, |v2|) in the divisor is motivated by the fact that the accu-
mulated costs amout to max(|v1|, |v2|) · γ if two sequences contain no pairwise
identical symbols. Therefore, e(v1, v2) is in the range [0, 1] with e(v1, v2) = 1 for
a perfect match. To extract the details about the errors made by the program,
the matrix is traversed in backward direction by using pointers set during the
forward pass. The error information gained in this step is examined in detail in
the next section.
2.2
Results and Evaluation
All texts in the SanskritTagger database that contain more than 10.000 words
were analyzed using the testing scenario described in the preceeding section.
The test data will be evaluated in two steps. First, we will give an overview of
general trends in the performance of the tagger, which includes questions such
as the inﬂuence of the text genre and the style on the analysis accuracy (page
166). Second, we will have a closer look at the lexical errors, which constitute
the most frequent class of errors (page 168).
The general performance. The raw test results are listed in table 1, which
contains some types of information that need further explanation:
1. Lexical richness is the ratio of the number of diﬀerent lexemes divided by
the number of all words contained in a text (nT ). It ranges from
1
nT (each
word of the text is derived from the same lexeme, something like ´siva ´siva
´siva) to nT
nT = 1 (each word is derived from another lexeme).
2. Six kinds of errors are distinguished in the tests. Apart from a lexical error
eLEX (cmp. page 165 and page 168 for a detailed analysis of this kind of
error), a wrong POS tag can be assigned to a correctly identiﬁed lexeme
(ePOS1−5). ePOS1 occurs only when an inﬁnite verbal form is confused with
a ﬁnite one.
3. The hit rate H records the overall hit rate of SanskritTagger. If C is the
number of words that were analyzed correctly and ω = 5
i=1 ePOSi, it is
deﬁned as
H =
C
C + eLEX + ω .
The lexical hit rate HLEX ignores POS errors because the lexeme has been
recognized correctly in such cases:
HLEX =
C + ω
C + eLEX + ω .
To compare the accuracy of SanskritTagger with that of other POS taggers,
the POS error rate can be calculated as follows (values not displayed in
table 1):
EPOS =
ω
C + ω .

Performance of a Lexical and POS Tagger for Sanskrit
167
Table 1. Results of the leave-one-out tests; refer to page 166 for the exact meanings
of the columns
Text
Lexical richness
Avg. phrase length
Analyzed correctly (C)
Error: lexical analysis (eLEX)
Error: diﬀ. word classes (eP OS1)
Error: case, number (eP OS2)
Error: gender (eP OS3)
Error: tense, mode (eP OS4)
More than one non-lexical error (eP OS5)
Hit rate
Lex. hit rate
Rasaratnasamuccaya-
0.18 9.8
9986
800
8
357 299 1 234 0.855 0.932
t.¯ık¯a
Rasama˜njar¯ı
0.22 7.2 10550
694
5
576 244 0 281 0.854 0.944
Bh¯avaprak¯a´sa
0.25 7.0 11096
878
2
314 280 0 161 0.872 0.931
La˙nk¯avat¯aras¯utra
0.16 11.6 9305
1730 17 347 254 3 388 0.773 0.856
Rasendracint¯aman.i
0.25 7.7 10845
922
4
555 337 0 244 0.840 0.929
Bodhicary¯avat¯ara
0.21 7.4 11257 1219 10 520 288 5 198 0.834 0.910
Y¯aj˜navalkyasmr.ti
0.27 7.0 11764 1059 19 557 234 1 150 0.853 0.923
Gokarn.apur¯an.as¯arah.
0.19 6.6 12497 1100 18 431 220 4 144 0.867 0.924
´S¯ar˙ngadharasam. hit¯a-
0.17 8.1 12449
833
2
532 372 1 305 0.859 0.943
d¯ıpik¯a
Da´sakum¯aracarita
0.28 16.9 12081 1283 19 439 357 5 252 0.837 0.911
Rasaprak¯a´sasudh¯akara 0.19 7.4 13263
988
2
608 288 2 219 0.863 0.936
Skandapur¯an.a
0.20 6.8 13827 1242 15 559 317 6 157 0.858 0.923
Rasendrac¯ud. ¯aman.i
0.21 7.2 15417
888
9
553 345 0 335 0.879 0.949
Vis.n.usmr.ti
0.24 5.7 15071 1378 29 809 371 4 257 0.841 0.923
Buddhacarita
0.20 9.1 15748 1485 22 723 536 5 237 0.840 0.921
Mr.gendrat.¯ık¯a
0.16 12.4 17443 1902 23 705 569 5 478 0.826 0.910
S¯atvatatantra
0.30 7.1
6240
1259
4
309 143 0 1923 0.632 0.873
Artha´s¯astra
0.29 9.3
8877
962
5
450 318 0 248 0.817 0.911
Hitopade´sa
0.23 7.1
9822
900
12 414 167 3
77 0.862 0.921
Rasaratnasamuccaya
0.18 7.2 23311 1656
5 1175 672 1 546 0.852 0.939
Mugdh¯avabodhin¯ı
0.13 12.7 24613 2087 20 1268 797 0 443 0.842 0.929
Ras¯arn.ava
0.13 6.8 26198 1895 10 1427 1031 1 711 0.838 0.939
Manusmr.ti
0.17 7.0 31177 2728 57 1650 890 9 342 0.846 0.926
¯Ayurvedad¯ıpik¯a
0.12 12.8 31355 2834 51 1259 902 10 545 0.848 0.923
K¯urmapur¯an.a
0.14 6.6 33308 2856 26 1244 715 17 391 0.864 0.926
Bh¯agavatapur¯an.a
0.17 7.1 33840 4076 76 1958 1062 22 625 0.812 0.902
Br.hatkath¯a´sloka-
0.12 6.8 49372 5482 114 1997 1401 28 864 0.833 0.907
sam. graha
¯Anandakanda
0.11 6.9 68767 5896 17 3720 1731 17 1791 0.839 0.928
Carakasam. hit¯a
0.11 10.5 73239 6830 157 3582 2189 79 1763 0.834 0.922
Skandapur¯an.a (2)
0.08 6.8 97348 7645 112 3951 1627 44 1250 0.869 0.932
Matsyapur¯an.a
0.10 6.8 101860 9805 141 3996 2518 25 1517 0.850 0.918
Li˙ngapur¯an.a
0.08 6.9 105185 10477 63 4137 3447 23 1557 0.842 0.916
Su´srutasam. hit¯a
0.09 8.9 113237 11904 209 5769 3809 30 2274 0.825 0.913
R¯am¯ayan.a
0.05 6.8 220398 18643 387 8292 4437 64 2619 0.865 0.927

168
O. Hellwig
Figure 1 displays the boxplots of H, HLEX and EPOS. Since the analysis of
Sanskrit diﬀers strongly from that of other languages, H and HLEX are hardly
comparable with rates recorded in previous research. Obviously, however, both
H and HLEX need signiﬁcant improvements in future versions of the program. If
we take into account the complex considerations that the linguistic phenomena
of composite creation and bahuvr¯ıhi make necessary for POS tagging of Sanskrit,
the POS accuracy of SanskritTagger compares acceptably with POS error rates
reported for less complex languages (μe POS = 0.090, σe POS = 0.035).
To go deeper into the details of table 1, we should try to determine the
inﬂuence of literary features on the analysis quality. If lexical richness and the
average phrase length are used to get an estimation of the complexity of a literary
style, we get the four plots displayed in ﬁgure 2. Astonishingly, the correlations
between these two features and the (lexical) hit rates are almost unnoticeable.
This result is supported by inspecting linear regressions performed with these
data none of whose parameters (intercept, slope) are signiﬁcant at the 10% level.
0.75
0.85
0.95
0.75
0.85
0.95
0.10
0.15
0.20
0.25
Fig. 1. Boxplots of the hit rates recorded in table 1; left: hit rate H, middle: lexical
hit rate HLEX, right: POS error rate
In the introduction, we mentioned the theory that the amount of training
data inﬂuences the analysis accuracy. To assess this theory, the analysis of the
Rasama˜njar¯ı was repeated using statistical key values that were calculated
from randomly selected subsets of the text corpus. Figure 3 displays graphically
the inﬂuence between the amount of training data and the analysis quality.
Although the analysis accuracy obviously increases with the amount of training
data, we achieve comparatively high rates of accuracy even when only 20% of
the corpus are used for training. Therefore, it seems that substantial increases
in the accuracy of the tagger cannot be achieved by increasing the size of the
corpus, but only by improving the analysis procedures.
Lexical errors. Errors in the lexical analysis constitute the major part of the
errors made by SanskritTagger. Since a reduction of this class of errors would
strongly increase the accuracy of the tagger, we should detail the subclasses of
this kind of error:

Performance of a Lexical and POS Tagger for Sanskrit
169
6
8
10
12
14
16
0.5
0.6
0.7
0.8
0.9
1.0
Avg. phrase length
6
8
10
12
14
16
0.5
0.6
0.7
0.8
0.9
1.0
0.05
0.10
0.15
0.20
0.25
0.30
0.5
0.6
0.7
0.8
0.9
1.0
Hit rate
0.05
0.10
0.15
0.20
0.25
0.30
0.5
0.6
0.7
0.8
0.9
1.0
Lexical richness
Lexical hit rate
Fig. 2. Correlation between the average phrase length (upper row)/lexical richness
(lower row) and the hit rate (left column)/lexical hit rate (right column)
Confusion of (partly) homonymous words. In most cases, homonyms be-
longing to diﬀerent declensional classes (e.g., adjectives and nouns) such as
pr.thu = “broad” and pr.thu = “name of a man” are confused in this sub-
class. One of the most productive pairs of words that belongs to this error
class is tad = “this” and the suﬃx t¯a, which denotes abstract nouns. Since
the nominative and accusative plural of t¯a are identical with the nomina-
tive/accusative plural fem. of the pronoun, the program selects the much
more frequent pronoun for the conﬁguration any word - t¯ah. as long as
no overwhelming testimony for the pair any word - t¯a is recorded in the
database. Less frequent are confusions of two or more homonymous nouns
that are entered as diﬀerent lexemes in the dictionary. Among these cases, we

170
O. Hellwig
0.75
0.85
0.95
20%
40%
80%
100%
60%
Fig. 3. Accuracy of SanskritTagger (y-axis) correlated with the size of the training
corpus (x-axis); the solid line indicates the lexical hit rate and the dashed line the hit
rate (cmp. page 2)
ﬁnd, for example, the triple ´siva (m.) = “the god ´Siva”, ´siva (n.) = “bliss”,
and ´siva (adj.) = “auspicious”, some of whose inﬂected forms are identical.
Another subtype comprised in this class pertains to comparatively few lex-
emes, but contributes much to the lexical error rate: When inﬂected forms of
nouns or adjectives are recorded as independent lexical items in the dictio-
nary, the lexical analysis often has problems to distinguish between these –
ﬁnally identical – instances. Examples are pr¯aya (m.)/pr¯ayen. a (adv.), pra-
tyaha (adj.)/pratyaham or ¯a´su (adj.)/¯a´su (adv.).
Inﬁnite verbal forms. This category partly coincides with the preceeding one.
Frequently, gerundives or participles are included as independent lexical
items in the dictionary. Examples are h¯asya (adj.) = “ridiculous” and h¯asya
as the gerundive of the root has or kart¯a = nom. sg. of kartr. (adj.) = “doing”
or as the periphrastic future of the verb kr.. The Monier-Williams, from which
the lexical database of SanskritTagger is built, contains a large number of
such lemmatized participles. If the meaning of such lemmata can be derived
directly from the meaning of the root (e.g., sam. jih¯ana), these lemmata are
removed from the digital dictionary. Although this – still ongoing – manual
cleanup is time consuming, it reduces the number of alternatives and thus
the possibilities of lexical errors. Some few lemmatized participles have de-
veloped independent meanings and are therefore kept in the dictionary (e.g.,
vidagdha= “clever” or samuddhata = “arrogant”). In spite of these improve-
ments, there remains a group of high frequency lemmatized participles such
as sat = “good” or kr.ta that are responsible for the majority of errors in
this class.
Segmentation errors. In this class, two types of errors can be distinguished.
The ﬁrst one is caused by redundancies found in the Monier-Williams. If the
dictionary contains both a composite noun and the components constituting

Performance of a Lexical and POS Tagger for Sanskrit
171
it, a substring wi corresponding to the composite noun can be analyzed
in two ways. An example is the term suhr.dv¯akya for which the Monier-
Williams gives the meaning “the advice of a friend” and whose components
suhr.d and v¯akya are also recorded in the dictionary. Obviously, the lemma
suhr.dv¯akya is redundant because its meaning can be derived directly from
the meaning of its components when standard rules of compound analysis
are applied. Similar to most of the lemmatized participles mentioned above,
such lemmata should therefore be removed from the digital dictionary. The
second class of errors are real missegmentations, which are comparatively
rare.
3
Conclusions and Future Developments
To our knowledge, the tests described in this paper have yielded the ﬁrst reliable
estimations of error rates that occur during the automatic processing of Sanskrit
using an unrestricted dictionary and texts from diverse knowledge domains. The
largest group of errors consists of lexical misinterpretations, which are mostly
caused by high frequency homonyms and redundancies in the digital dictionary.
While the redundancies will be reduced by an ongoing revision of the dictio-
nary, the homonyms pose a serious challenge to the computational analysis of
Sanskrit. Considering the weak correlation between the amount of training data
and the accuracy of the tagger, we cannot expect these and similar errors will
disappear with an increasing size of the text corpus. Manually designed decision
rules or a more detailed context analysis may oﬀer a way out of this problem.
When compared with results reported for other languages, the POS error rate
of SanskritTagger is still too high. A combination of morphological and syn-
tactic analysis steps may help to decrease the frequency of this error; however,
the basic steps necessary for such an analysis have ﬁrst to be implemented in
SanskritTagger. In conclusion, the results reported in this paper indicate that
the three steps of analysis should be merged into one step in future versions of
SanskritTagger.
References
1. Csernel, M., Patte, F.: Critical edition of Sanskrit texts. In: Huet, G., Kulkarni,
A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI),
vol. 5402, pp. 358–379. Springer, Heidelberg (2009)
2. Hal´acsy, P., Kornai, A., Oravecz, C., Tr´on, V., Varga, D.: Using a morphological
analyzer in high precision POS tagging of Hungarian. In: Proceedings of 5th Con-
ference on Language Resources and Evaluation (LREC), Citeseer, pp. 2245–2248
(2006)
3. Haque, W., Aravind, A., Reddy, B.: Pairwise sequence alignment algorithms: a sur-
vey. In: Proceedings of the 2009 conference on Information Science, Technology and
Applications, pp. 96–103 (2009)
4. Hellwig, O.: SanskritTagger, a stochastic lexical and POS tagger for Sanskrit.
In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics
2007/2008. LNCS (LNAI), vol. 5402, pp. 266–277. Springer, Heidelberg (2009)

172
O. Hellwig
5. Leech, G., Garside, R., Bryant, M.: CLAWS4: The tagging of the British National
Corpus. In: Proceedings of the 15th International Conference on Computational
Linguistics, Kyoto pp. 622–628 (1994)
6. Marcus, M.P., Marcinkiewicz, M.A., Santorini, B.: Building a large annotated corpus
of English: The Penn Treebank. Computational Linguistics 19(2), 313–330 (1993)
7. Megyesi, B.: Improving Brill’s POS tagger for an agglutinative language, pp. 275–
284.
8. Sproat, R., Shih, C.: Corpus-based methods in Chinese morphology and phonology.
In: Proceedings of the 19th International Conference on Computational Linguistics
(2002)
9. Weischedel, R., Schwartz, R., Palmucci, J., Meteer, M., Ramshaw, L.: Coping with
ambiguity and unknown words through probabilistic models. Computational Lin-
guistics 19(2), 360–382 (1993)
