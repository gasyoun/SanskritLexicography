_Created: 27-09-2026 · Last updated: 27-09-2026_

# Scharf_ReviewOfRajpopat-InPaniniWeTrust_2022

**Kind:** full-text extraction (source PDF is openly posted by The Sanskrit Library)
**Citation:** Scharf, Peter M. Review of Rishi Rajpopat, *In Pāṇini we trust: Discovering the algorithm for rule conflict resolution in the Aṣṭādhyāyī* (Ph.D. diss., University of Cambridge, 2021). 23 December 2022. 11 pp.
**Source:** Critical review of the Rajpopat rule-conflict-resolution dissertation. Source PDF freely posted at https://sanskritlibrary.org/pub/scharf-ReviewOfRajpopat-InPaniniWeTrust.pdf.
**Source SHA-256:** `6ed2b0236706e4acebc32fbf032032f9e75bc7ed9117169c1eae8c4b8d7fe7f3`
**Extraction:** PyMuPDF text layer, 27-09-2026 (H5510); tables are linearized — glyph cells may interleave.

**Rights-pending note (MG 30-07-2026 precedent, recorded not blocking):** © The Sanskrit Library / the author; fetched from the publisher's own openly-posted URLs for research use. Redistribution beyond research use is **pending rights confirmation — UNRESOLVED, recorded**. Derived measurements (coverage counts, crossrows) are free.

---

Review of
In P¯an. ini we trust
Discovering the algorithm for rule conflict
resolution in the As.t. ¯adhy¯ay¯ı
by
RISHI RAJPOPAT
Ph.D. dissertation, University of Cambridge,
2021
PETER M. SCHARF
23 December 2022
i
REVIEW OF RAJPOPAT
1
Few scholars choose to study Sanskrit. Fewer still choose to spend a signif-
icant portion of their lives studying the linguistic traditions of India. Of those
who do study P¯an.inian linguistics, few delve into the intricacies of derivational
procedure (prakriy¯a). We therefore are pleased that Rishi Rajpopat has chosen to
do so and has drawn considerable attention to P¯an.inian grammar on the subject
in interviews, social media posts, youtube videos, and even interviews and an-
nouncements on Indian national television and the BBC. On the other hand, his
self-proclaimed “ingenious algorithm” having solved a 2,500 year old problem in
P¯an.inian grammar, as John Lowe has pointed out, requires examination.
Before we delve into the details of how his proposed interpretation of 1.4.2
vipratis.edhe para ˙m k¯aryam falls short of his claim, let us point out a positive in-
sight he has expressed in his dissertation, even if this insight is not his own unique
initial discovery. On p. 202 he writes, “P¯an.ini always followed the same order:
first, he substituted the affix if required, and then he modified the base (or both
base and affix together, in case of ek¯ade´sa) if required.” Later on the same page
he reiterates this observation writing, “P¯an.ini’s goal was to replace the affix first,
where required, and only then to modify the base (or modify both base and affix
together, in case of ek¯ade´sa) where required.” This is generally a correct observa-
tion and one consistent with the phonetic facts such as that regressive assimilation
is far more common than progressive assimilation. I myself came to such a con-
clusion in my own first computational implementations of nominal declension and
verbal conjugation. There I segregated operations into “changes to terminations,
changes to stems, and sandhi” (2008: 27) in that order generally with rare excep-
tions. Rajpopat explicitly recognizes P¯an.ini’s preference for this order, and this
recognition appears to be the inspiration for his interpretation of A. 1.4.2 in a man-
ner that regularizes prioritization of operations on subsequent units over operation
on preceding ones. His observation and clear articulation of it deserve approval.
Another praiseworthy observation in his dissertation concerns the derivation
of tray¯an. ¯am. One of the benefits of rigorously applying a consistent pattern of
analysis over a large number of cases is that inconsistencies reveal themselves.
This is one of the principal contributions of digital humanities to the humanities:
the correlation of large amounts of information reveals patterns and discontinuities
that facilitate new insights. While examining the application of his technique to
solve different operation interaction (DOI), Rajpopat noticed that the technique
accounted for the derivation of the Vedic form tr¯ın. ¯am rather than the classical
Sanskrit form tray¯an. ¯am which led him to observe that A. 7.1.53 tres trayah. is the
only replacement rule in a sequence of augmentation rules. Although cognizant of
P¯an.ini use of tray¯an. ¯am in A. 7.4.75, nevertheless he suspects 7.1.53 to be a later
REVIEW OF RAJPOPAT
2
addition added to account for the historically later form. While P¯an.ini’s use of
tray¯an. ¯am would still require explanation, nevertheless, his analysis and process
of discovery of the problem is commendable.
Let us now turn to some difficulties that arise with the proposition that A. 1.4.2
vipratis.edhe para ˙m k¯arya ˙m universally selects the operation on the subsequent
operand where two different operations are applicable at the same stage of deriva-
tion (DOI). The procedure does not select the correct operation in some instances.
First of all, consider the derivation of the form bhavya, gerundive of the verb ‘to
be’. While the form is derivable from the root bh¯u, P¯an.ini also derives it from
the root as. In the derivation from the latter, two rules are simultaneously appli-
cable: (1) A. 2.4.52 aster bh¯uh. (¯ardhadh¯atuke 35), and (2) A. 3.1.124 r
˚
halor n. yat
(dh¯atoh. 91). The former provides the replacement of the root as with the root bh¯u
when an ¯ardhadh¯atuka affix is to be provided. The term ¯ardhadh¯atuke is a vis.aya-
saptam¯ı making the rule a forward-looking condition so that the replacement can
take place before the particular affix is actually provided (Scharf 2011a: 67, 2016:
317–18). The latter provides the affix n. yat after a root that ends in a short or long
vowel r
˚
or in a consonant. Rajpopat’s procedure would provide the affix since it
is the right-hand operation resulting in the incorrect form *¯asya. The correct form
requires that the left-hand operation apply replacing the root as with bh¯u. Since
bh¯u ends in a vowel, A. 3.1.97 aco yat, which provides the affix yat after a vowel-
final root, applies in exception to A. 3.1.124 thereby resulting in the correct form
bhavya.
Secondly, consider the derivation of the form bhavanti, third-person plural
present active indicative of the root bh¯u. At the stage bh¯u a anti two rules apply (1)
A. 7.3.84 s¯arvadh¯atuk¯ardhadh¯atukayoh. (gun. ah. 82) which provides replacement
of the final vowel ¯u of the stem bh¯u before the stem-forming affix ´sap, and (2)
A. 6.1.97 ato gun. e (parar¯upam 94). Rajpopat’s procedure would select the right-
hand operation A. 6.1.97 resulting in bh¯u anti. Now the affix anti, unlike ´sap is
not marked with p so that it becomes marked with ˙n by A. 1.2.4 s¯arvadh¯atukama-
pit (˙nit 1). Because it is marked with ˙n the metarule A. 1.2.5 kh˙niti ca prevents
gun.a which would occur by the application of A. 7.3.84. After the application
of A. 6.4.77 aci ´snudh¯atubhruv¯a ˙m yvor iya˙nuva˙nau, the incorrect form *bhuva-
nti would then result. The M¯adhav¯ıyadh¯atuvr
˚
tti (Shastri 1983: 13) proposes the
possibility that even so gun.a could occur by the sth¯anivadbh¯ava of ´sap by A.
1.1.57 acah. parasminp¯urvavidhau with a questionable application of sth¯aniva-
dbh¯ava in the case of ek¯ade´sa. The simpler derivation is to acknowledge that rules
that apply to an a˙nga take precedence over simple phonetic rules in accordance
with the metarule varn. ¯ad¯a˙nga ˙m bal¯ıyah. (PBIS. 56). However, Rajpopat does not
REVIEW OF RAJPOPAT
3
accept such paribh¯as.¯as.
Thirdly, consider the derivation of the form aj¯abhih. , feminine instrumental
plural ‘she-goat’. At the stage after the introduction of the instrumental plural
termination bhis we have the string aja bhis. Here two rules are applicable (1)
A. 4.1.3 aj¯adyatas. t. ¯ap which introduces the feminine affix ¯a after the nominal base
aja, and (2) A. 7.1.9 ato bhisa ais which replaces the nominal termination bhis
after a stem ending in a by ais. By his DOI principle, A. 7.1.9 will apply yielding
the string aja ais. A. 4.1.3 would then apply to yield aja ¯a ais and ultimately ajaih.
which is incorrect.
These three examples, which are representative of large classes of derivations
underivable by his method, bring up a third problem with Rajpopat’s thesis: he
complains that both the tradition and modern scholars limit the scope of A. 1.4.2
to accommodate the incapacity of their interpretation of it while he ends up do-
ing just the same to accommodate the incapacity of his interpretation. He writes
(pp. 31–32) “I do not agree with both the traditional and the modern perspectives
towards this topic, because instead of trying to decipher the actual meaning of
1.4.2, these approaches try to brush 1.4.2 under the carpet, to make it less effec-
tive or to weaken its impact. One does it by excluding certain rule pairs from the
scope of vipratis.edha, and the other by reducing the jurisdiction of 1.4.2.” The
tradition, he argues, limits its scope by restricting it to cases of competing rules
of equal strength (tulyabalavirodha) outside the scope of metarules concerning
apav¯ada, nitya, and antara˙nga rules. Modern scholars limit its scope by limiting
it to rules that introduce technical terms between 1.4.1 and 2.2.38. Yet Rajpopat
also limits the scope of applicability of his interpretation of A. 1.4.2 by excluding
same operand interaction (SOI), by arbitrarily redefining the term a˙nga to exclude
cases that involve the introduction of a medial affix, i.e. explicitly a stem-forming
affix (vikaran. a), but the same logic would also exclude the introduction of femi-
nine affixes. Yet there are no criteria to distinguish whether his interpretation of
A. 1.4.2 should or should not apply to the introduction of such medial affixes. He
does not consider the issue of feminine affixes at all. With regard to verbal stem-
forming affixes, on the one hand, he applies his DOI principle to the introduction
of such medial affixes, for example, the stem-forming affix ´sap in the derivation of
edhante (pp. 113–114). Yet he argues (p. 111) that only the fused form of the root
and stem-forming affix can be termed a˙nga, neither the root by itself nor the root
with the stem forming affix prior to the changes these would undergo. Concerning
the derivation of the present active third-person singular of the verbal root cit, he
writes that the term a˙nga could only apply to ceta “after applying all possible rules
to cit and ´Sap, except those that are triggered by tip.” By excluding such cases
REVIEW OF RAJPOPAT
4
of the interaction of rules that apply to the root conditioned by the stem-forming
affix with rules that apply to the termination, he arbitrarily limits the scope of ap-
plication of his interpretation of A. 1.4.2 committing the very fault he accuses the
tradition and modern scholars of in their interpretation of the rule.
Yet Rajpopat’s redefinition of the term a˙nga commits an additional fault. By
requiring that the medial verbal stem-forming affix be fused with the preceding
root (or, if he considered the case at all, a feminine affix with the nominal base
after which it is provided) basically he is applying the principle that the more inter-
nally conditioned operation apply first. This is just the principle of antara˙ngatva.
He similarly wants antara˙ngatva when dealing with the asiddhatva of retroflexion
across word boundaries when he writes (p. 175), “I think P¯an.ini does not consider
word-level rules to be asiddha with respect to sentence-level rules.” Yet he dis-
cards the antara˙nga paribh¯as.¯a and all such metarules. He writes (p. 93) “Besides,
if P¯an.ini wanted us to use these metarules, he would have taught them explicitly in
the As.t.¯adhy¯ay¯ı.” Thus while condemning the tradition under its interpretation of
A. 1.4.2 for the use of metarules, he introduces the very same metarules to allow
his interpretation to function successfully. And he claims that his interpretation al-
lows rules to be applied in a consistent manner while he repeatedly condemns the
tradition for applying rules in a random manner. He writes, for example, (p. 115)
“the tradition chooses to apply rules in a random order”, (p. 118) “the tradition
would have applied rules in any haphazard order”, (p. 120) “the tradition applies
rules in a random order” ... “the tradition applies rules in a haphazard order.”
In sum, we can conclude regarding Rajpopat’s DOI principle exactly what he
concluded in brushing aside the traditional and modern interpretations of A. 1.4.2,
namely, “This approach which seeks to undervalue P¯an.ini’s rule interaction mech-
anism and replaces it with self-invented methods of ‘rule conflict resolution’ can
lead to some success for a limited set or specific type of examples, but does not
allow us to understand and appreciate the larger picture.”
Enough has been said to demonstrate that his DOI principle suffers from se-
rious faults. A few words are now in order about his principle of same operand
interaction (SOI). This principle involves a faulty procedure of determining the
specificity of one rule with respect to another. When different rules are simultane-
ously applicable to the same operand, he adopts the policy of determining which
rule is more specific. In general such a policy implements just what the tradi-
tion does in determining that one rule is an exception to (apav¯ada of) another.
However, where the tradition resorts to other principles, such as nityatva or its in-
terpretation of A. 1.4.2, to solve certain conflicts, Rajpopat devises a procedure to
determine the specificity of one with regard to the other by dividing the rule into
REVIEW OF RAJPOPAT
5
parts. He expands the abbreviations that refer to sets of sounds (praty¯ah¯aras),
selects the common sounds, then looks for an additional limiting adjunct. This
procedure, however, is biased and therefore faulty. For example, in the compar-
ison of the application of A. 6.1.87 ¯ad gun. ah. (aci) and A. 6.1.101 akah. savarn. e
d¯ırgah. to tava ¯anandam, he eliminates the vowels other than those of the class a
(short and long a) and then concludes that the latter rule is more specific because
it mentions savarn. a. Conversely, one might equally well have started by selecting
pairs of savarn. a vowels and then determining that the former rule is more spe-
cific because it is restricted to vowels of the class a. Rajpopat uses a similarly
biased analysis of the rules A. 7.3.84 s¯arvadh¯atuk¯ardhadh¯atukayoh. (gun. ah. ) and
A. 7.1.100 ¯r
˚
ta iddh¯atoh. . The former applies to a short or long simple vowel i, u, r
˚
,
or l
˚
before a s¯arvadh¯atuka or ¯ardhadh¯atuka affix not marked with k or ˙n; the latter
to the vowel ¯r
˚
before any affix. Clearly a s¯arvadh¯atuka or ¯ardhadh¯atuka affix so
marked constitutes a domain wholly included within the domain of any affix; yet
conversely the vowel ¯r
˚
constitutes a domain wholly included within the domain
of a short or long simple vowel i, u, r
˚
, or l
˚
. Each rule includes a parameter which
is more specific than the corresponding parameter of the other rule. After describ-
ing Cardona’s (1970: 57-58) method of limited blocking and Kiparsky’s (1991:
350-351) criticism of Cardona’s method, Rajpopat writes, “I think that Cardona’s
limited blocking principle is similar to my method of dealing with SOI. However,
Kiparsky correctly points out that the explanation offered by Cardona is ambigu-
ous. On the other hand, my solution overcomes such ambiguity by following the
clearly defined procedure which I have developed and used to tackle all examples
of SOI in this thesis.” Rajpopat does not see that his procedure suffers exactly
the fault that Kiparsky describes and fails to articulate a procedure that success-
fully solves such cases. He would have done well to take a close look at my own
analysis of specificity conditions (Scharf 2011b: 18–25). There I argue that P¯an.ini
operates with a hierarchy in which more abstract types of reference are considered
more specific than more concrete types of reference in the following ranking from
concrete to abstract: phonetics, phonology, morphology, semantics. Krishna and
Goyal (2015: 179) successfully utilized this hierarchy to select the correct rule
where exception alone did not.
There are many other instances where Rajpopat summarily dismisses tra-
ditional solutions, often due to failing to understand the argumentation in pri-
mary sources or being unaware of secondary discussions. For example, he fails
to understand the hypothetical argumentation in Patañjali’s discussion of the
conflict between A. 7.1.9 ato bhisa ais and A. 7.1.103 bahuvacane jhaly et at
MBh. III.244.13–21, writing (p. 50) “His explanation for calling 7.1.9 nitya is
REVIEW OF RAJPOPAT
6
illogical at best, and we will not delve into it.” He similarly dismisses Patañja-
li’s discussion of A. 7.1.23 svamor napu ˙msak¯at (MBh. III.248.19–249.2) writing
(p. 58), “The tradition seems to be confused about this,” and (p. 59) “We will
not dwell on his argument, because it is beyond our scope.” Likewise, given his
discussion of A. 8.2.66 and A. 6.1.113 (p. 175), he seems to be unaware of Car-
dona’s discussion in his article “p¯urvatr¯asiddham and ¯a´sray¯at siddham” of rules
in the trip¯ad¯ı that nevertheless have to be considered siddha with respect to rules
preceding the trip¯ad¯ı.
The discussion above reveals that Rajpopat did not sufficiently examine or un-
derstand discussions in the commentaries regarding the traditional interpretation
of A. 1.4.2 nor in the modern scholarship concerning rule interaction. Instead he
brazenly asserted his own interpretations and proposed solutions hastily brushing
aside traditional procedures and neglecting recent work on the topic. Unfortu-
nately, his proposed solutions are largely ineffective and his interpretations lead
him to unwittingly adopt the very metarules he seeks to dismiss. His dissertation
would have made a more helpful contribution had he spent a greater proportion of
the work analyzing passages in commentaries and recent articles concerning the
interpretation of A. 1.4.2 and other rule selection metarules. In the bibliography
accompanying this review, I include a number of recent articles dealing with the
topic, mostly my own, of which only four are listed in Rajpopat’s bibliography
and none of which are referred to in his text.
REVIEW OF RAJPOPAT
7
Bibliography
Ajotikar, Anuja P., Malhar Kulkarni, and Peter M. Scharf. 2016. “On the resolu-
tion of conflict between accentual rules and other rules of derivation in P¯an.i-
nian grammar.” Vy¯akaran. aparipr
˚
cch¯a: proceedings of the Vy¯akaran. a section
of the 16th World Sanskrit Conference, 28 June–2 July 2015, Sanskrit Stud-
ies Center, Silpakorn University, Bangkok, ed. by George Cardona and Hideyo
Ogawa, pp. 1–21.
Ajotikar, Tanuja, Anuja Ajotikar, and Peter M. Scharf. 2015. “Some issues in
the computational implementation of the As.t.¯adhy¯ay¯ı.” Sanskrit and Compu-
tational Linguistics: select papers presented at the 16th World Sanskrit Con-
ference in the ‘Sanskrit and the IT world’ section 28 June – 2 July 2015, San-
skrit Studies Center, Silpakorn University, Bangkok, ed. by Amba Kulkarni,
pp. 103–24.
Biagetti, Erica, Chiara Zanchi, and Silvia Luraghi, eds. 2021. Building new re-
sources for historical linguistics. Pavia: Pavia University Press.
Cardona, George, ed. 2013. Proceedings of 15th World Sanskrit Conference; vol.
2, Vy¯akaran. a across the ages: Section 5: Vy¯akaran. a. New Delhi, January, 5–
10, 2012. New Delhi: Rashtriya Sanskrit Sansthan and D. K. Printworld.
Cardona, George, Ashok N. Aklujkar, and Hideyo Ogawa, eds. 2011. Studies in
Sanskrit grammars: proceedings of the Vy¯akaran. a section of the 14th World
Sanskrit Conference, 1–5 September 2009, Kyoto University, Kyoto. New
Delhi: D. K. Printworld.
Cardona, George and Hideyo Ogawa, eds. 2016. Vy¯akaran. aparipr
˚
cch¯a: proceed-
ings of the Vy¯akaran. a section of the 16th World Sanskrit Conference, 28 June–
2 July 2015, Sanskrit Studies Center, Silpakorn University, Bangkok. New
Delhi: D. K. Publishers.
Huet, Gérard, Amba Kulkarni, and Peter M. Scharf, eds. 2009. Sanskrit compu-
tational linguistics: first and second international symposia, Rocquencourt,
France, October 2007; Providence, RI, USA, May 2008; Revised selected and
invited papers. Lecture Notes in Artificial Intelligence 5402. Berlin; Heidel-
berg: Springer-Verlag.
Jha, Girish Nath, ed. 2010. Sanskrit computational linguistics: 4th International
Symposium, New Delhi, India, December 2010, Proceedings. Lecture Notes
in Artificial Intelligence 6465. Berlin; Heidelberg: Springer-Verlag.
REVIEW OF RAJPOPAT
8
Krishna, Amrith and Pawan Goyal. 2015. “Towards automating the generation
of derivative nouns in Sanskrit by simulating P¯an.ini,” ed. by Amba Kulkarni,
pp. 157–94.
Kulkarni, Amba, ed. 2015. Sanskrit and Computational Linguistics: select papers
presented at the 16th World Sanskrit Conference in the ‘Sanskrit and the IT
world’ section 28 June – 2 July 2015, Sanskrit Studies Center, Silpakorn Uni-
versity, Bangkok. New Delhi: D. K. Publishers.
Kulkarni, Amba and Gérard Huet, eds. 2009. Sanskrit computational linguistics:
third international symposium, Hyderabad, India, January 2009, proceedings.
Lecture Notes in Artificial Intelligence 5406. Berlin; Heidelberg: Springer-
Verlag.
Kulkarni, Malhar and Chaitali Dangarikar, eds. 2013. Proceedings of the Fifth
International Sanskrit Computational Linguistics Symposium. New Delhi: D.
K. Printworld.
Scharf, Peter M. 1995. “Early Indian grammarians on a speaker’s intention.” Jour-
nal of the American Oriental Society 115.1: 66–76.
—. 2002. “P¯an.ini, vivaks. ¯a, and k¯araka-rule-ordering.” Indian linguistic studies:
festschrift in honour of George Cardona, ed. by Madhav M. Deshpande and
Peter E. Hook, pp. 121–49. Delhi: Motilal Banarsidass.
—. 2008a. “P¯an.inian accounts of the class eight presents.” Journal of the Ameri-
can Oriental Society 128.3: 489–504.
—. 2008b. “P¯an.inian accounts of the Vedic subjunctive: let. kr
˚
n. va´ıte.” Indo-
Iranian Journal 51.1: 1–21. Corrected version of Indo-Iranian Journal 48.1
(2005): 71–96.
—. 2009a. “Levels in P¯an.ini’s As.t. ¯adhy¯ay¯ı.” Sanskrit computational linguistics:
third international symposium, Hyderabad, India, January 2009, proceedings,
ed. by Amba Kulkarni and Gérard Huet. Lecture Notes in Artificial Intelli-
gence 5406.
—. 2009b. “Modeling P¯an.inian grammar.” Sanskrit computational linguistics:
first and second international symposia, Rocquencourt, France, October
2007; Providence, RI, USA, May 2008; Revised selected and invited papers,
ed. by Gérard Huet, Amba Kulkarni, and Peter M. Scharf. Lecture Notes in
Artificial Intelligence 5402.
—. 2010. “Rule-blocking and forward-looking conditions in the computational
modeling of P¯an.inian derivation.” Sanskrit computational linguistics: 4th In-
ternational Symposium, New Delhi, India, December 2010, Proceedings, ed.
by Girish Nath Jha, pp. 48–56. Lecture Notes in Artificial Intelligence 6465.
REVIEW OF RAJPOPAT
9
—. 2011a. “On the semantic foundation of P¯an.inian derivational procedure: the
derivation of kumbhak¯ara.” Journal of the American Oriental Society 131.1:
39–72.
—. 2011b. “Rule selection in the As.t. ¯adhy¯ay¯ı or Is P¯an.ini’s grammar mechanis-
tic?” Studies in Sanskrit grammars: proceedings of the Vy¯akaran. a section
of the 14th World Sanskrit Conference, 1–5 September 2009, Kyoto Univer-
sity, Kyoto, ed. by George Cardona, Ashok N. Aklujkar, and Hideyo Ogawa,
pp. 319–50.
—. 2013a. “An analytic database of the As.t. ¯adhy¯ay¯ı.” Proceedings of the Fifth
International Sanskrit Computational Linguistics Symposium, ed. by Malhar
Kulkarni and Chaitali Dangarikar, pp. 40–61.
—. 2013b. “Teleology and the simplification of accentuation in P¯an.inian deriva-
tion.” Vy¯akaran. a across the ages: Section 5: Vy¯akaran. a; vol. 2, ed. by George
Cardona, pp. 31–53. New Delhi, January, 5–10, 2012. New Delhi: Rashtriya
Sanskrit Sansthan and D. K. Printworld.
—. 2015a. “An XML formalization of the As.t. ¯adhy¯ay¯ı.” Sanskrit and Computa-
tional Linguistics: select papers presented at the 16th World Sanskrit Confer-
ence in the ‘Sanskrit and the IT world’ section 28 June – 2 July 2015, Sanskrit
Studies Center, Silpakorn University, Bangkok, ed. by Amba Kulkarni, pp. 77–
102.
—. ed. 2015b. Sanskrit syntax: selected papers presented at the seminar on San-
skrit syntax and discourse structures, 13–15 June 2013, Université Paris
Diderot, with a bibliography of recent research by Hans Henrich Hock. Prov-
idence: The Sanskrit Library.
—. 2016. “On the status of nominal terminations in upapada compounds.” Vy¯a-
karan. aparipr
˚
cch¯a: proceedings of the Vy¯akaran. a section of the 16th World
Sanskrit Conference, 28 June–2 July 2015, Sanskrit Studies Center, Silpakorn
University, Bangkok, ed. by George Cardona and Hideyo Ogawa, pp. 287–316.
—. 2017. “A computational implementation of P¯an.ini’s derivational morphol-
ogy of Sanskrit.” Proceedings of the Workshop on Resources and Tools for
Derivational Morphology (DeriMo), Milano, Italy, 5–6 October 2017, ed. by
Eleonora Litta and Marco Passarotti, pp. 93–104. Milan: EDUCatt.
—. 2021a. “Are taddhita affixes provided after pr¯atipadikas or padas?” Vy¯akaran. a
and ´s¯abdabodha: Indian linguistic studies in honor of George Cardona; vol. 1,
ed. by Peter M. Scharf, pp. 123–67. Paper presented at the Troisième Atelier
du Projet ANR PP16–17 (P¯an.ini et les P¯an.inéens des XVIe–XVIIe siècles)
accueilli par EFEO, IFP, EPHE, Pondichéry, 14–16 octobre 2014. Providence:
The Sanskrit Library.
REVIEW OF RAJPOPAT
10
—. 2021b. “Non-linear syntax: insights from Indian linguistic traditions for devel-
oping language-neutral syntactic representation.” Building new resources for
historical linguistics, ed. by Erica Biagetti, Chiara Zanchi, and Silvia Luraghi,
pp. 67–102.
—. 2021c. “Rule-prioritization principles in the derivation of compound absolu-
tives in lyap.” Vy¯akaran. a and ´s¯abdabodha: Indian linguistic studies in honor
of George Cardona; vol. 1, ed. by Peter M. Scharf, pp. 53–122. Providence:
The Sanskrit Library.
—. ed. 2021d. ´sabd¯anugamah. : Indian linguistic studies in honor of George Car-
dona; vol. 1, Vy¯akaran. a and ´s¯abdabodha. 2 vols. Providence: The Sanskrit
Library.
—. 2023. “Insights from P¯an.inian grammar and theory of verbal cognition for rep-
resenting non-linear syntax: developing language-neutral syntactic representa-
tion.” Studies in Humanities and Social Sciences. Presented to the fellows of
the Indian Institute of Indian Studies, Shimla, 15 April 2020. Forthcoming.
Scharf, Peter M., Pawan Goyal, Anuja Ajotikar, and Tanuja Ajotikar. 2015.
“Voice, preverb, and transitivity restrictions in Sanskrit verb use.” Sanskrit
syntax: selected papers presented at the seminar on Sanskrit syntax and dis-
course structures, 13–15 June 2013, Université Paris Diderot, with a bibli-
ography of recent research by Hans Henrich Hock, ed. by Peter M. Scharf,
pp. 157–201.
Shastri, Dwarikadas, ed. 1983. The m¯adhav¯ıy¯a dh¯atuvr
˚
tti [A treatise on Sanskrit
roots based on the dh¯atup¯at.ha of P¯an. ini] by s¯ayan. ¯ac¯arya. 2nd ed. Kamachha,
Varanasi: Tara Book Agency.
