# Performance_of_a_Lexical_and_POS_Tagger

**Source:** `Performance_of_a_Lexical_and_POS_Tagger.pdf`  
**Format:** PDF  
**Size:** 4.8 MB

---

<!-- page 1 -->

Lecture Notes in Artiﬁcial Intelligence
Edited by R. Goebel, J. Siekmann, and W. Wahlster

6465

Subseries of Lecture Notes in Computer Science

---

<!-- page 2 -->

Girish Nath Jha (Ed.)
Sanskrit Computational Linguistics
4th International Symposium New Delhi, India, December 10-12, 2010 Proceedings
13

---

<!-- page 3 -->

Series Editors
Randy Goebel, University of Alberta, Edmonton, Canada Jörg Siekmann, University of Saarland, Saarbrücken, Germany Wolfgang Wahlster, DFKI and University of Saarland, Saarbrücken, Germany
Volume Editor
Girish Nath Jha Special Center for Sanskrit Studies Jawaharlal Nehru University New Delhi 110067 India E-mail: girishjha@gmail.com

Library of Congress Control Number: 2010939861

CR Subject Classiﬁcation (1998): I.2.7, F.4.2, I.2, F.4.1, J.5, I.2.7

LNCS Sublibrary: SL 7 – Artiﬁcial Intelligence

ISSN

0302-9743

ISBN-10 3-642-17527-9 Springer Berlin Heidelberg New York ISBN-13 978-3-642-17527-5 Springer Berlin Heidelberg New York

This work is subject to copyright. All rights are reserved, whether the whole or part of the material is concerned, speciﬁcally the rights of translation, reprinting, re-use of illustrations, recitation, broadcasting, reproduction on microﬁlms or in any other way, and storage in data banks. Duplication of this publication or parts thereof is permitted only under the provisions of the German Copyright Law of September 9, 1965, in its current version, and permission for use must always be obtained from Springer. Violations are liable to prosecution under the German Copyright Law.
springer.com
© Springer-Verlag Berlin Heidelberg 2010 Printed in Germany
Typesetting: Camera-ready by author, data conversion by Scientiﬁc Publishing Services, Chennai, India Printed on acid-free paper 06/3180

---

<!-- page 4 -->

Preface
It is with great pleasure that I present the selected papers from the 4th International Sanskrit Computational Linguistics Symposium (4i-SCLS) to you. The event is being hosted by the Jawaharlal Nehru University, the premier research University of India during (December 10–12, 2010) at the Special Center for Sanskrit Studies. The ﬁrst symposium was organized at INRIA, France, by G´erard Huet in 2007, the second at Brown University, USA, by Peter Scharf in 2008, and the third was organized at the University of Hyderabad by Amba Kulkarni in January 2009. The Sanskrit computational linguistics community is relatively young, and the foundation for this kind of formal meeting to exchange ideas between Sanskritists, linguists and computer scientists was given by Prof. Huet and Prof. Amba Kulkarni. My hearty thanks to both of them for bringing about this uniﬁcation of scholars under one umbrella.
The 4i-SCLS saw excellent response from the scholars. We received more than 31 papers, which were examined by our Program Committee members to shortlist 18 papers for publication presented in this volume. The papers can be categorized under the following broad areas:
1. Phonology and speech technology 2. Morphology and shallow parsing 3. Syntax, semantics and parsing 4. Lexical resources, annotation and search 5. Machine translation and ambiguity resolution 6. Computer simulation of As.t.a¯dhya¯y¯ı
Some of the notable misses were the speech corpora annotation, image processing techniques like OCR, and also the papers written in Sanskrit. Eﬀorts will be made to ensure wider participation by scholars in future events.
Under category 1, the following papers were selected: Wiebke Peterson and Silke Hamann (Unversity of Duesseldorf) in their pa-
per “On the generalizability of Pa¯n. ini’s Pratya¯ha¯ra Technique to Other Languages” have experimented the Pa¯n. ini’s pratya¯h¯ara technique to German with good results. That there are universal principles in Pa¯n. ini’s grammar has been a well-known fact among linguists, but actually applying them to languages other than Sanskrit has not been done a great deal. The present paper is therefore very important in this context. One of the more signiﬁcant conclusions arrived at by the authors is that they have found this technique to be better than the feature-based techniques used by modern phonology. The paper “Building a Prototype Text to Speech for Sanskrit” by Baiju Mahananda, Raju C.M.S., Ramalinga Reddy Patil, Narayana Jha, Shrinivasa Varakhedi, and Kishore Prahallad presents a prototype TTS system for Sanskrit. The paper is signiﬁcant

---

<!-- page 5 -->

VI

Preface

because the group is the ﬁrst to develop a prototype using a simpliﬁed phone set and the well-known Festvox engine.
The following three papers were presented under category 2: “Rule Interaction, Blocking and Derivation in Pa¯n. ini” by Rama Nath Sharma
(University of Hawaii) is based on an earlier paper by the author, and is the title of the keynote talk to be delivered in the inaugural session. It is a detailed account of rule applications, interpretations and interplay, blocking in the complex process of obtaining a syntactic form from stems. Prof. Sharma’s mastery of the structure and processes in the As.t.a¯dhya¯y¯ı can be seen in the description of the blocking parameters and the derivation procedures. Peter Scharf (Brown University) in his paper titled “Rule-Blocking and Forward-Looking Conditions in the Computational Modeling of Pa¯n. inian Derivation” demonstrates the mechanism of rule blocking and looking ahead in Pa¯n. ini through XML schema and regular expressions compiled into Perl code. The paper, besides discussing this in the context of derivations and other preprocessing implementations, gives an option to those Pa¯n. inian enthusiasts who can learn a simple tag like schema (not a programming language yet) and hope to convert Pa¯n. ini’s rules into XML. Then a routine done by Hyman can convert all that into a Perl program. The paper titled “Sanskrit Compound Processor” by Anil Kimar, Vipul Mittal and Amba Kulkarni (University of Hyderabad) presents a compound processor for Sanskrit which does segmentations and type identiﬁcation based on manually annotated data. Sanskrit derivational morphology has not been worked on a great deal due to various reasons. The paper is signiﬁcant in this context and also because it will help in identifying complex words not found in the dictionary.

Under category 3, the following papers were selected: “Designing a constraint-based parser for Sanskrit” by Amba Kulkarni,
Sheetal Pokar and Devendra Shukl (University of Hyderabad) is an attempt toward parsing simple one-verb sentences of Sanskrit prose with proper annotation and morphological information. The ´sa¯bdabodha and m¯ıma¯m. sa¯ parameters are brought in to reduce ambiguities and far-fetched possibilities. As Sanskrit is a highly inﬂected language with relatively free word-order, morphological analyses are generally assigned a greater role. However, the importance of parsers cannot be underestimated when one considers processing constituents higher than words—sentence and discourse. In the paper “Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)”, Rajesh Tavva and Navjyoti Singh (IIIT Hyderabad) describe a formal model of Vai´se.sika ontology for computing ´sa¯bdabodha of sentences (among other things). The approach described is foundational and bottom–up and the proposed grammar based on graphs can correctly distinguish well-formed graphs from others. The proposed framework is generative and can help model ontologies eﬀectively without the known disadvantages of the top–down approach. The paper “Headedness and Modiﬁcation in Nya¯ya Morphosyntactic Analysis: Towards a Bracket-Parsing Model” by Malhar Kulkarni, Anuja Ajotikar, Tanuja Ajotikar, Dipesh Katira, Chinmay

---

<!-- page 6 -->

Preface VII
Dharurkar and Chaitali Dangarikar (IIT Bombay) present an alternative model for sentence analysis using the prak¯arata¯ and vi´se.syata¯ concepts of the NavyaNya¯ya school of philosophy. The paper is a comprehensive account of the alternative parsing model which the authors have tried on simple and complex sentences as well as discourses with anaphors and ellipsis.
Under category 4, the following six papers were presented: In the paper “Citation Matching in Sanskrit Corpora Using Local Align-
ment”, the authors Abhinandan S. Prasad and Shrisha Rao from IIIT Bangalore experiment with a citation matching technique used in bioinformatics for Sanskrit corpora. Of particular interest is their method of approximate matching of Maha¯bha¯rata citations in Maha¯bh¯arata-t¯atparyanirn. aya using the SmithWaterman-Gotoh algorithm which is generally used in scientiﬁc documents. Diwakar Mani in “RDBMS-Based Lexical Resource for Indian Heritage: The Case of Maha¯bha¯rata (MB)” presents his research work done at Jawaharlal Nehru University. The indexing system developed as part of this research is done in Java/JSP and MS SQL server with a Unicode input/output mechanism. The system is live at http://sanskrit.jnu.ac.in/mb. The author has used BORI’s authoritative version of the MB text and has created a database system which allows three kinds of searches – direct search, alphabetical search and the search by structure of MB. The search results are listed as index of words, details of which can be obtained by following the link. As an extension, not typical of indices, the system also links the results with other lexical resources available on the internet through simple http connections. The signiﬁcance of the work rests in the fact that in future, interlinked database resources of heritage texts can be developed which will make classical indological research more attractive. In another paper in this category—“Evaluating Tagsets for Sanskrit” Madhav Gopal, Diwakar Mishra and Priyanka Singh from Jawaharlal Nehru University compare existing tagsets for Sanskrit: JNU Sanskrit tagset (JPOS), Sanskrit consortium tagset (CPOS), MSRI-Sanskrit tagset (IL-POST), IIIT Hyderabad tagset (ILMT POS) and CIIL Mysore tagset for their LDCIL project (LDCPOS). The main goal behind this enterprise is to check the suitability of existing tagsets for Sanskrit. Indian language computing groups have created numerous tagsets and therefore it is very important that these are evaluated based on standard procedures. In this context, the paper by Oliver Hellwig titled “Performance of a Lexical and POS Tagger for Sanskrit” is very relevant. The paper reports testing the performance of SanskritTagger on more than 34 Sanskrit texts and does estimations of the error rates in automatic processing of Sanskrit. They also note the problems like segmentation, homonymy, complexities of Sanskrit morphology and syntax which aﬀect the accuracy of automatic processing. “Knowledge Structure in Amarako´sa” by Sivaja S. Nair and Amba Kulkarni presents a structural description of Amarako´sa bringing out complex relationships that lexical items may have across k¯an. d. as and vargas. The paper seems to suggest how a wordnet based on Amarako´sa structure can be evolved for Indian languages. In “Gloss in Sanskrit Wordnet”, Malhar Kulkarni,

---

<!-- page 7 -->

VIII Preface
Iravati Kukarni, Chaitali Dangarikar and Pushpak Bhattacharya (IIT Mumbai) highlight the role of glosses in the wordnet and MRDs. Their paper also describes the experience in building Sanskrit wordnet which is based on the Hindi wordnet. The authors also report on the various wordnet activities on Indian languages based on the Hindi wordnet done at IIT Mumbai.
Under category 5, the following papers were presented: “Vibhakti Divergence Between Sanskrit and Hindi” by Preeti Shukla, De-
vanand Shukl and Amba Kulkarni (University of Hyderabad) focuses on a speciﬁc kind of variance between a pair of languages under MT. Mapping Sanskrit (which is a synthetic language) vibhaktis to Hindi (which is post-positional in nature) is not easy due to many-to-one as well as one-to-many cases, and also because of many new features emerging in Hindi in the course of evolution. The authors examine this problem at the level of divergence and discuss each case in detail. In “Anaphora Resolution Algorithm for Sanskrit”, Pravin Pralayankar and Sobha Lalitha Devi (AU-KBC Research Centre, Anna University) have continued some of the recent work in this area with a more deﬁnite mechanism for resolving anaphora in Sanskrit. They have also implemented a system and have given performance evaluation based on 200 anaphoric sentences. The work on Sanskrit syntax and discourse has been minimal, and therefore the paper becomes very important for future research and development in this direction. The paper by Brendan S. Gillon (McGill University)—“Linguistic Investigations into Ellipsis in Classical Sanskrit – provides a detailed account of the distribution of Ellipsis in Sanskrit, its classiﬁcation and linguistic analysis. Since not many scholars have ventured in this area of Sanskrit linguistics, this work is certainly going to be a fundamental document for researchers working this area.
Under category 6, the following papers were presented: “Asiddhatva Principle in Computational Model of As.t.¯adhya¯y¯ı” by Sridhar
Subbanna (Rashtriya Sanskrit Vidyapeetha, Tirupati) and Srinivasa Varakhedi (Sanskrit Academy, Osmania University, Hyderabad) has evolved from a previous work by the same authors on the conﬂict resolution techniques in As.t.a¯dhya¯y¯ı. In this paper they have tried to map the asiddhatva principle to the concept of ‘ﬁlter’ so that all the cases of asiddha operations can be accounted for. In “Modeling As.t.¯adhya¯y¯ı—An Approach Based on the Methodology of Ancillary Disciplines (Veda¯n˙ ga)”, the author (Anand Mishra, University of Heidelberg) extends his previous works (as presented in the previous symposia at Paris and Hyderabad) and has adopted a new perspective. Since Pa¯n. ini’s grammar is situated in the tradition of Veda¯n˙ ga (four of which deal with language), the organization of the text may have certain inheritances from the tradition. The author has exploited this fact in terms of the content, structure and operations of methodological enquiry of Veda¯n˙ ga and As.t.a¯dhya¯y¯ı and has put together a generalized model with broader coverage.
This volume would not have been possible without the active support of my Ph.D. students Diwakar Mishra (from the Special Center for Sanskrit Studies)

---

<!-- page 8 -->

Preface

IX

and Ritesh Kumar (from the Center for Linguistics). Their LaTex skills and unending enthusiasm were critical in ﬁnalizing this volume.
I also thank all the members of the Program Committee who took pains to review the papers in time despite their hectic schedules. My special thanks to the members of the Steering Committee, Local Advisory Committee and Organizing Committee for facilitating this event. I also thank the sponsors (Dept. of I.T., C.I.I.L. Mysore, Microsoft Research India and others who may conﬁrm support later) whose generous support was key to organizing this symposium. Finally, a special mention of Springer for accepting to publish this volume.
I hope the readers will like the volume and it will lead to the popularization of computational linguistics amongst Sanskrit scholars and students.

November 2010

Girish Nath Jha

---

<!-- page 9 -->

Conference Organization

Conference Chair
Girish Nath Jha

Jawaharlal Nehru University, New Delhi, India

Steering Committee
Brendan S. Gillon Gerard Huet Girish Nath Jha Amba P. Kulkarni Malhar A. Kulkarni Peter M. Scharf

McGill University, Montreal, Quebec, Canada INRIA, Rocquencourt, Paris, France Jawaharlal Nehru University, New Delhi, India University of Hyderabad, India I.I.T. Mumbai, India Brown University, USA

Program Committee
Pushpak Bhattacharya Brendan S. Gillon Oliver Hellwig Gerard Huet Girish Nath Jha Amba P. Kulkarni Malhar A. Kulkarni Shoba L. K.V. Ramkrishnamacharyulu Peter M. Scharf Lalit Tripathi Srinivasa Varakhedi

I.I.T. Mumbai McGill University, Montreal, Quebec, Canada University of Berlin, Germany INRIA, Rocquencourt, Paris, France Jawaharlal Nehru University, New Delhi, India University of Hyderabad, India I.I.T. Mumbai, India Anna University (AU-KBC), Chennai, India Rashtriya Sanskrit Vidyapeeth, Tirupati, India Brown Universiry, USA Rashtriya Sanskrit Sansthan, Allahabad, India Sanskrit Academy, Osmania University,
Hyderabad, India

Local Organizing Committee

Santosh Kumar Shukla Ramnath Jha Hariram Mishra Rajnish Mishra

Jawaharlal Nehru University, India Jawaharlal Nehru University, India Jawaharlal Nehru University, India Jawaharlal Nehru University, India

---

<!-- page 10 -->

XII Organization

Local Advisory Committee

Sankar Basu Devendra Chaube Shashiprabha Kumar D. K. Lobiyal Varyam Singh

Jawaharlal Nehru University, India Jawaharlal Nehru University, India Jawaharlal Nehru University, India Jawaharlal Nehru University, India Jawaharlal Nehru University, India

---

<!-- page 11 -->

Table of Contents
Rule Interaction, Blocking and Derivation in Pa¯n. ini . . . . . . . . . . . . . . . . . . 1 Rama Nath Sharma
On the Generalizability of Pa¯n. ini’s Pratya¯ha¯ra-Technique to Other Languages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
Wiebke Petersen and Silke Hamann
Building a Prototype Text to Speech for Sanskrit . . . . . . . . . . . . . . . . . . . . 39 Baiju Mahananda, C.M.S. Raju, Ramalinga Reddy Patil, Narayana Jha, Shrinivasa Varakhedi, and Prahallad Kishore
Rule-Blocking and Forward-Looking Conditions in the Computational Modelling of Pa¯n. inian Derivation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48
Peter M. Scharf
Sanskrit Compound Processor . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57 Anil Kumar, Vipul Mittal, and Amba Kulkarni
Designing a Constraint Based Parser for Sanskrit . . . . . . . . . . . . . . . . . . . . 70 Amba Kulkarni, Sheetal Pokar, and Devanand Shukl
Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 91
Rajesh Tavva and Navjyoti Singh
Headedness and Modiﬁcation in Nya¯ya Morpho-Syntactic Analysis: Towards a Bracket-Parsing Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 106
Malhar Kulkarni, Anuja Ajotikar, Tanuja Ajotikar, Dipesh Katira, Chinmay Dharurkar, and Chaitali Dangarikar
Citation Matching in Sanskrit Corpora Using Local Alignment . . . . . . . . . 124 Abhinandan S. Prasad and Shrisha Rao
RDBMS Based Lexical Resource for Indian Heritage: The Case of Maha¯bha¯rata . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 137
Diwakar Mani
Evaluating Tagsets for Sanskrit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 150 Madhav Gopal, Diwakar Mishra, and Devi Priyanka Singh
Performance of a Lexical and POS Tagger for Sanskrit . . . . . . . . . . . . . . . . 162 Oliver Hellwig
The Knowledge Structure in Amarako´sa . . . . . . . . . . . . . . . . . . . . . . . . . . . . 173 Sivaja S. Nair and Amba Kulkarni

---

<!-- page 12 -->

XIV Table of Contents
Gloss in Sanskrit Wordnet . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 190 Malhar Kulkarni, Irawati Kulkarni, Chaitali Dangarikar, and Pushpak Bhattacharyya
Vibhakti Divergence between Sanskrit and Hindi . . . . . . . . . . . . . . . . . . . . . 198 Preeti Shukla, Devanand Shukl, and Amba Kulkarni
Anaphora Resolution Algorithm for Sanskrit . . . . . . . . . . . . . . . . . . . . . . . . 209 Pravin Pralayankar and Sobha Lalitha Devi
Linguistic Investigations into Ellipsis in Classical Sanskrit . . . . . . . . . . . . . 218 Brendan S. Gillon
Asiddhatva Principle in Computational Model of As.t.a¯dhya¯y¯ı . . . . . . . . . . 231 Sridhar Subbanna and Shrinivasa Varakhedi
Modelling As.t.¯adhya¯y¯ı: An Approach Based on the Methodology of Ancillary Disciplines (Ved¯an˙ ga) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 239
Anand Mishra
Author Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 259

---

<!-- page 13 -->

Rule Interaction, Blocking and Derivation in P¯an. ini⋆
Rama Nath Sharma
University of Hawaii at Manoa Honolulu, HI, U.S.A. rama@hawaii.edu
1 Sa¯ma¯nya, Vi´ses. a and S´es. a
P¯an. ini’s grammar is a class of rules formulated based on generalization abstracted from usage, so that the vast oceans of words could be properly understood. This class of rules will consist of general (utsarga) and their related particulars (vi´ses. a). A general rule, since it is to be formulated with certain generalizations made about its scope of application, must yield to its related particulars which would necessarily require delineation of their own particular scope of application. A particular rule is thus formulated with particular properties relative to generalized properties. A general rule is supposed to pervade its scope of application in its entirety. It is in this sense that it is called vy¯apaka (pervader). Since a particular rule is formulated with particular properties relative to the general, the scope of application of a particular must then be extracted from within the scope of its general counterpart. A related particular is called pervaded (vy¯apya), since its scope of application is to be carved out from within the general scope of its corresponding utsarga, the pervader (vy¯apaka). Rules whose application cannot be captured within the related class of general and particular have been classed as residual (´ses. a). A residual would thus fall outside of the applicational scope of its general and particular counterparts. For, it refers to a proposal which is yet to be made, close to its context (upayukt¯ad anyah. ´se.sah. ).
Rules of P¯an. ini’s grammar have been formulated with brevity though certainly not at the expense of clarity. Consideration of brevity demands that rule be formulated with terms and symbols. Condition of explicitness requires proper interpretation of rules, so that they could reach their desired context of application. Two rules may share a single context of application (s¯avak¯a´sa), thereby presenting the diﬃculty of selecting concurrent (yugapad ) application, application in turn (parya¯ya), application of one by blocking the application of the other (ba¯dhaka), or application of one over the other based on it being left with no context of application (niravak¯a´sa). For a rule should apply only once
⋆ Based on Laguage, Grammar and Linguistics my paper published in the History of Indian Science, Philosophy and Culture in Indian Civilization (2010, Vol. VI.4: pp. 134-250).
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 1–20, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 14 -->

2

R.N. Sharma

in realizing its desired goal of application (lak.sye lak.san. am. sak.rd eva pravartate). A rule which is formulated against a provision already made available to a rule, blocks the application of the other, obligatorily (nitya; yena na¯pra¯pte yo vidhir a¯rabhyate sa tasya b¯adhako bhavati). A prior (pu¯rva) rule may block the application of a rule which is subsequent (para) in the order of enumeration. A rule whose condition of application is internal (antaran˙ ga) to the other conditioned externally (bahiran˙ ga), blocks the application of the other. Relative power of application of these rules is determined in this order: pu¯rva ‘prior’, para ‘subsequent’, nitya ‘obligatory’, antaran˙ ga ‘externally conditioned’ and apav¯ada ‘exception, particular’.
Rules of grammar are likened to rain clouds which rain over land and water indiscriminately (parjanyaval lak.san. a¯ni bhavanti). This indiscriminate raining of clouds over land and water with no consideration whatsoever of its beneﬁcent, or malevolent, results, is not acceptable in the world of grammar. A parjanya enjoys a great deal of freedom when it comes to accomplishing its desired goal of raining (var.san. a). A rule of grammar, on the other hand, does not enjoy as much freedom when it comes to its desired application. It has to be carefully restrained or its scope of application must be delineated with care, so that it can accomplish its desired (i.s.ta) goal.
Proper delineation of context of rule application depends on interpretation of rules. Since rules are interpreted as a sentence, and also since rules also share single sentence relationship with rules placed at diﬀerent places in grammar, interpretation of rules become very diﬃcult. This implies that interpretation of rules is two-fold, (i) where rules which share single sentence relationship are placed together in one place, and (ii) where rules which share single sentence relationship are placed at diﬀerent places.
It is generally agreed that proper understanding of a rule is possible only when one considers the exposition of the learned (PS´1: vya¯khya¯nato vi´se.sapratipattir na hi sandeh¯ad alaks. an. am. ). It is in this sense that Pa¯n. in¯ıyas accept the notion of ekava¯kyat¯a ‘single sentence-ness’ for interpretation of a rule. A rule in its physical context can be interpreted as a single sentence rather easily. To interpret a rule as a single sentence in its functional context is not so easy. For, that rule could not be properly understood unless the single sentence interpretation of its physical context is brought close to its functional context of application. Now consider two interpretive conventions (PS´2-3) which both are complementary to each other, and which scholars consider operative in the As.t.a¯dhya¯y¯ı:
1. yathodde´sam. sam. jn˜¯a-paribha¯s. ham 2. k¯aryaka¯lam. sam. jn˜¯a-paribha¯s. ham
These two views about interpretation of technical names (sam. jn˜¯a), and interpretive conventions (paribha¯s. a¯), are called yathodde´sa ‘not going beyond the place where taught’ and k¯aryaka¯la ‘taught at the place where operative.’ A student may like to understand a rule, for example 1.1.2 aden˙ gun. ah. , right at the place where it is taught in the grammar. Some other student may like to understand this rule where, for example, rule 6.1.87 a¯d gun. ah. is taught with the use of the

---

<!-- page 15 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

3

term gun. a. He understands 1.1.2 aden˙ gun. ah. as a rule which assigns the name gun. a to aT and eN˙ . He also learns that eN˙ , per 1.1.71 a¯dir antyena sahet¯a with reference to inventory of sounds listed by the S´iva-su¯tra, is an abbreviated symbol used with the denotation of e and o. An understanding of 1.1.70 taparas tatk¯alasya further explains that a speciﬁcation made with -t (which shows here with the uppercase T ) denotes duration (k¯ala) of ‘that which is used with T.’ He thus understands that gun. a is a name (sam. jn˜¯a) assigned to vowels a, e, and o. Rules 1.1.3 iko gun. avr. ddh¯ı , 1.1.49 s. as..th¯ı stha¯neyog¯a and 1.1.67 tasma¯d ity uttarasya, similarly teach him that ‘a speciﬁcation made with the genitive (.sas..th¯ı) means ‘in place of’ (that which is speciﬁed with the genitive),’ and ‘a speciﬁcation made with the ablative (pan˜cam¯ı) means ‘after’ (that which is speciﬁed with the ablative).’ In addition, a replacement ordered with express mention of the terms gun. a and v.riddhi must come in place of a vowel denoted by the abbreviated symbol iK (1.1.3 iko gun. avr. ddh¯ı ). It is at the time of understanding the function (k¯arya), and thereby application of rule 6.1.87 a¯d gun. ah. , that his sam. ska¯ra ‘memory impressions’ of understanding 1.1.2 aden˙ gun. ah. , 1.1.3 iko gun. avr. ddh¯ı , 1.1.70 taparas tatk¯alasya, 1.1.71 a¯dir antyena sahet¯a and 1.1.67 tasma¯d ity uttarasya must be brought close to the context of 6.1.87 ¯ad gun. ah. , for its proper interpretation and application. The ablative of a¯T and the term gun. a, must serve as a mark (lin˙ ga) for reconstruction of the full context of this rule by memory so that its application could be accomplished. Note that this rule is put in the domain (adhika¯ra) of 6.1.72 sam. hita¯ya¯m, where sam. hita¯ya¯m 7/1, aci 7/1 (6.1.77 iko yan. aci) and ekah. 1/1 pu¯rvaparayoh. 6/1 (6.1.84 ekah. pu¯rvaparayoh. ) must be carried over to its context. The locative (saptam¯ı) of aci 7/1 and the genitive dual (.sas..th¯ı dvivacana) of pu¯rvaparayoh. 6/2 must also serve as marks for reconstructing memory impressions of rules 1.1.3 iko gun. avr. ddh¯ı , 1.1.49 s. as..th¯ı stha¯neyog¯a and 1.1.67 tasma¯d ity uttarasya. This, in turn, facilitates his full understanding of rule 6.1.87. I now quote single sentence interpretation of this rule from the Ka¯´sika¯vr.tti:
avarn. a¯t paro yo’c aci ca pu¯rvo yo avarn. ah. tayoh. pu¯rvaparayoh. avarn. ¯acoh. sth¯ane eko gun. a¯de´so bhavati ‘a single replacement termed gun. a comes in place of both, the (gun. a) vowel which follows a, and the (gun. a vowel) a which precedes it, within the scope of sam. hita¯ ‘close proximity between sounds’
Notice that this preceding is a single sentence interpretation of rule 6.1. 87 a¯d gun. ah. , presented in the physical context of sam. hita¯ (6.1.72 sam. hita¯ya¯m). But this interpretation cannot be considered yathodde´sa ‘place where gun. a is taught’ interpretation. For, it involves bringing memory impressions of rules placed outside the domain of rule 6.1.87 a¯d gun. ah. . It must then be viewed as the ka¯ryaka¯la at time when the rule is functional interpretation whereby rules necessary for proper interpretation of a rule are brought close to its context from the outside of its domain. It is to be noted that no derivation is possible without taking help from the k¯aryaka¯la view. What triggers this interpretation in the derivational process? It is triggered by the mark of deﬁnitional terms, and interpretive conventions (paribha¯s. a¯). We see that gun. a is the mark of the deﬁnitional term gun. a

---

<!-- page 16 -->

4

R.N. Sharma

in rule 6.1.87 ¯ad gun. ah. . We also ﬁnd pan˜cam¯ı ‘ablative’, .sas..th¯ı ‘genitive’ and saptam¯ı ‘locative’ in words which are brought close to the context of rule 6.1.87 ¯ad gun. ah. , and trigger the reconstruction of pan˜cam¯ı, .sas..th¯ı, and saptam¯ı from domains of rules placed outside this domain. This reconstruction is triggered by deﬁnitional and interpretational terms, and is accomplished by scanning rules where they have been used. This reconstruction entails bringing memory impressions of rules such as 1.1.2 aden˙ gun. ah. , 1.1.3 iko gun. avr. ddh¯ı , 1..49 s. as..th¯ı sth¯aneyog¯a, 1.1.67 tasma¯d ity uttarasya and tasminn iti nirdi.s.te pu¯rvasya, to facilitate proper interpretation of rule 6.1.87 ¯ad gun. ah. . I have shown in the derivational section how derivations cannot be carried out without reference to antecedents of deﬁnitional and interpretational terms. I have used the word Referential Index (RI) for reconstruction of rule contexts triggered by marks of terms on hand.

2 General Blocking Considerations
Rule-interaction has been studied in the literature from the point of view of possibility of rule application (pra¯pti-sambhava). Once this possibility of application is ascertained in a context, we look at the context and give some serious consideration towards establishing the blocked-blocker relationship (b¯adha-cint¯a). Rules whose possibility of application is ascertained in a given context are called sa¯vak¯a´sa (with valid scope of application). If two rules A and B become applicable in a given context Z, a concurrent application of both rules is impossible. There are two possibilities:
1. Apply rules A and B in turn (parya¯ya), or 2. Apply only one rule by blocking the application of the other 3. A rule (kak.san. a) applies only once (sak.rd ) to reach its desired goal (i.s.ta)
Here are some generally established blocking considerations:
1. B blocks the application of A if B is a particular (vi´se.sa) related to its general (utsarga) counterpart A;
2. The a¯kad. ¯ar¯ıya proposal of viprati.sedha ‘conﬂict among rules of equal strength’ whereby B blocks the application of A if B is subsequent (para) in the order of enumeration (1.4.1 a¯ kad. a¯ra¯d ek¯a sam. jn˜¯a and 1.4.2 viprati.sedhe param. ka¯ryam ).
3. The ¯abh¯ıya proposal of rule suspension (asiddhatva) of 6.4.22 asiddhavad atr¯abh¯at.
4. The tripa¯d¯ı proposal of rule (8.2.1 pu¯rvatra¯siddham ) suspension (asiddhatva).
5. B blocks the application of A if B may be rendered without any scope of application (niravaka¯´sa).
6. B blocks the application of A if B is obligatory (nitya). 7. B blocks A if B is internally conditioned (antaran˙ ga), as against A which is
externally conditioned (bahiran˙ ga).

---

<!-- page 17 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

5

8. B blocks A if B is placed higher in relative hierarchy of rules in interaction. Consider the following interpretive convention of relative blocking from the Paribh¯as. endu´sekhara of Na¯ge´sa: pu¯rvaparanitya¯ntaran˙ g¯apav¯ad¯an¯amuttarottaram. bal¯ıyah. ‘prior (pu¯rva), subsequent (para), obligatory (nitya), internally conditioned (antaran˙ ga) and exception (apav¯ada), are considered more powerful in this order.’
These blocking considerations express closely relate to the utsarg¯apav¯ada dichotomy of (1) general (sa¯ma¯nya), particular (vi´se.sa) and residual (´se.sa). It is in this sense that P¯an. ini’s grammar, the As.t.¯adhya¯y¯ı, is considered a set of ordered rules capable of deriving the inﬁnity of utterances of the Sanskrit language.

3 Derivational System of the As..t¯adhy¯ay¯ı
The goal of grammar is to derive correct words (´sabda-ni.spatti) of the language. The tradition uses ´sabda ‘word’ in the general sense of an utterance which, given its basic purpose of serving as means of communication, can be referred to as a sentence. A word in its technical sense is accepted as fully derived, a pada which ends in two sets of aﬃxes, namely sUP and tiN˙ (1.4.14 suptin˙ antam. padam). This yields two pada types, subanta ‘that which ends in a sUP, and tin˙ anta ‘that which ends in a tiN˙ .’ Recall that this grammar imagines constituency of words in bases (prakr. ti) and aﬃxes (pratyaya), and as a result of operations (k¯arya) carried out with application of rules on input strings, yields a fully derived word. There are two types of bases, namely pra¯tipadika ‘nominal stem’ and dh¯atu ‘verb root’:
1.2.45 - arthavad adh¯atur apratyayah. pra¯tipadikam ‘a non-root and nonaﬃx word-form (´sabda-ru¯pa) which carries a meaning (arthavad ) is termed pra¯tipadika nominal stem.’ 1.2.46 - kr. ttaddhitasam¯as¯a´s ca ‘a word form which ends in aﬃxes termed kr. t (3.1.93 kr. d atin˙ ) and taddhita (4.1.76 taddhit¯ah. ), or which is termed sama¯sa (2.1.3 pr¯ak-kad. ¯ara¯t sam¯asah. ), is also termed pra¯tipadika nominal stem.’ 1.3.1 - bhu¯va¯dayo dh¯atavah. ‘word-forms which are listed in groups headed by bhu¯ ‘to be, become,’ and its likes, are termed dh¯atu. 3.1.33 - san¯adyant¯a dh¯atavah. ‘word-forms which end aﬃxes saN, etc., are also termed dh¯atu.’
Note that nominal stems (pra¯tipadika), and verb roots (dh¯atu) will be here considered as base-input (prakr. ti). Aﬃxes which are introduced after base- inputs are classiﬁed into three groups of (i) n˙ ya¯P ‘those which are formed with a common N˙¯ı (N˙¯ıP /N˙¯ıS. /N˙¯ıN ) and a¯P (Ca¯P /T. ¯aP /D. ¯aP ), (ii) Vibhakti : ‘nominal inﬂectional endings (sUP )’ and ‘verbal inﬂectional endings (tiN˙ ),’ (iii) kr. t (3.1.93 k.rd atin˙ ) and taddhita (4.1.76 taddhit¯ah. ). Now consider the following rules:

---

<!-- page 18 -->

6

R.N. Sharma

3.1.7 - dh¯atoh. karman. ah. sam¯anakartr. ka¯d icch¯aya¯m. va¯ (san) ‘aﬃx saN is, optionally, introduced after a verb root used with the denotation of object of i.s ‘to desire, wish,’ provided its agent (kartr. ) is the same as the agent of i.s.’

For example, kartum icchati −→ cik¯ır.sati, where cik¯ır.sa ‘to wish to do’ is a root derived with aﬃx saN, introduced after the verbal root D. Ukr. N˜ ‘to do.’ This derived base input can then gain access to the domain of 3.1.91 dh¯atoh. whereby cik¯ır.sa, with introduction of LAT. −→ tiP, and S´aP would yield cik¯ır.sati, a verbal pada.

3.1.8 supa ¯atmanah. kyac ‘aﬃx KyaC is, optionally, introduced after a pada which ends in a sUP, and is used with the denotation of an object wished for one’s own (¯atmanah. ).’

For example, a¯tmanah. putram. icchati −→ putr¯ıyati, where putr¯ıya ‘to wish a son of one’s own’ is a root derived with aﬃx saN introduced after putra + am, a pada ending in sUP.

3.1.91 - dh¯atoh. ‘after a verb root’ 3.2.123 - vartam¯ane la.t ‘aﬃx LAT. is introduced after a verb root when action is denoted at the current time’

3.4.77 - lasya ‘in place of that which is formed with a LA’

3.4.78

-

tiptasjhi-sipthastha-mivbasmas-t¯at¯an˜jhatha¯s¯atha¯m. -

dhvamid. vahimahin˙ ‘the aﬃxes tiP, tas, jhi, etc.’ For example, pac + LAT. −→ tiP −→ pac + S´aP + tiP = pacati, a verbal pada which ends in a tiN˙ .

4.1.1 - n˙ ya¯p-pra¯tipadika¯t ‘an aﬃx is introduced after that which ends in an aﬃx, formed with N˙¯ı and a¯P (T. ¯aP/C¯aP/D. a¯P; N˙¯ıP/N˙¯ıS. /N˙¯ıN ), or after that which is termed a pra¯tipadika (nominal stem)’ 4.1.2 - svaujasmau.tchas..t¯abha¯y¯am. bhisn˙ ebhya¯m. bhyasn˙ asibhya¯m. bhyasn˙ asos¯am. n˙ yossup ‘an aﬃx denoted by sUP is introduced after that which ends in an aﬃx formed with N˙¯ı and ¯aP, or after that which is termed a pr¯atipadika’

Table 1. The tiN˙ aﬃxes

prathama madhyama uttama
prathama madhyama uttama

ekavacana ‘singular’
tiP siP miP
ta th¯as iT.

dvivacana

bahuvacana

‘dual’

‘plural’

parasmaipada ‘active’

tas

jhi

thas

tha

vas

mas

a¯tmanepada ‘middle’

a¯t¯am

jha

a¯tha¯m vahi

dhvam mahiN˙

3rd person 2nd person 1st person
3rd person 2nd person 1st person

---

<!-- page 19 -->

pratham¯a
dvit¯ıy¯a tr. t¯ıy¯a caturth¯ı pan˜cam¯ı
.sas..th¯ı saptam¯ı

Rule Interaction, Blocking and Derivation in P¯an. ini

7

Table 2. The sUP aﬃxes

ekavacana ‘singular’
sU
am
T. ¯a N˙ e N˙ asI N˙ as N˙ i

dvivacana ‘dual’ au
auT. bhy¯am bhya¯m bhya¯m os os

bahuvacana ‘plural’ Jas S´as bhis bhyas bhyas a¯m suP

‘nominative’ ‘accusative’ ‘instrumental’ ‘dative’ ‘ablative’ ‘genitive’ ‘locative’

4.1.3 striya¯m ‘an aﬃx is introduced after a nominal stem when feminine is denoted’ 4.1.4 aja¯dyatah. .t¯ap ‘aﬃx T. a¯P is introduced after a nominal stem... 4.1.5 r. nnebhyo n˙¯ıp ‘aﬃx N˙¯ıP is introduced after a nominal stem extracted from the group headed by aja ‘goat,’ or one which ends in -a’ 4.1.76 taddhit¯ah. ‘aﬃxes termed taddhita...’
A form which ends in the feminine suﬃxes T. a¯P, N˙¯ıP etc., is not assigned the name pra¯tipadika. It, however, gains access to the domain of 4.1.1 n˙ y¯appr¯atipadika¯t as a base-input again since its suﬃx is marked with n˙ ya¯p. This time it must opt for application of 4.1.2 svaujasmau.t..., whereby, with introduction of sUP, it subsequently yields a pada.
4.1.82 samartha¯n¯am. pratham¯ad va¯ ‘a taddhita aﬃx, namely aN. (read with 4.1.83 pra¯g d¯ıvyato’an. ) is introduced after the ﬁrst among syntactically related nominal pada.’
Consider upagu + N˙ as, a nominal pada which, with introduction of the taddhita aﬃx aN. , yields aupagava, a nominal stem. This nominal stem must now get access to the domain of 4.1.1 n˙ ya¯p-pra¯tipadika¯t, whereby, with introduction of sUP (4.1.2 svaujasmau.t...) it yields aupagavah. ‘male descendant of upagu’ , a nominal pada. Note however, that a base-input ending in a taddhita aﬃx may gain access to the domain of 4.1.3 striya¯m for yielding a nominal base ending in a feminine aﬃx. The output of this application will then go for access to the domain of 4.1.1 n˙ ya¯p-pra¯tipadika¯t for application of 4.1.2 svaujasmau.t... This clearly establishes the cyclic nature of these domain accesses.
It is clear from the deﬁnitions of nominal stems and roots that they each have two sets of forms, simple and derived. A nominal pada which ends in a sUP can also serve as a base input for introduction of taddhita aﬃxes under the provision of rule 4.1.82 samartha¯n¯am. pratham¯ad v¯a. This will still yield a nominal stem, and with the introduction of a sUP would yield a nominal pada. A kr. t aﬃx can be introduced after a verbal base under the co-occurrence condition of a nominal pada, whereby a form which ends in a k.rt aﬃx is termed a nominal stem. For

---

<!-- page 20 -->

8

R.N. Sharma

example, kumbhaka¯ra ‘pot-maker’ which is a derived nominal stem. This can access the domain of 4.1.1 n˙ ya¯p-pra¯tipadika¯t , where with the introduction of sU of 4.1.2 svaujasmau.t... it yields kumbhaka¯rah. , a nominal pada. A pada which ends in a sUP can also be combined with another, also ending in a sUP, to yield a compound (2.1.3 saha supa¯; sama¯sa), again termed a nominal stem. Aﬃxes saN, etc., can be introduced after a base-input termed dh¯atu, whereby a form which ends in them is again termed dh¯atu, a derived verb root. An aﬃx of this class, for example KyaC, can also be introduced after a nominal pada, for example putra + am, under some co-occurrence condition to yield putr¯ıya, a verb root. This verb root can then yield a verbal pada, for example putr¯ıyati ‘he wishes a son of his own.’ Finally, aﬃxes formed with the two shared elements N˙¯ı and a¯P are introduced after a nominal stem to yield yet another complex base-input. Note that this set of six base-inputs which denote feminine are not classed as a nominal stem, or verb root. They are, characterized as ending in aﬃxes formed with N˙¯ı and a¯P instead.
This controlled description of a fully derived word by way of bases (prakr. ti), aﬃxes (pratyaya) and operations (ka¯rya) may give the impression to many that the As.t.¯adhya¯y¯ı is a morphological grammar, even more so because a pada is its ﬁnal output. It is true that Pa¯n. ini accepts pada as the ﬁnal output of his grammar. But his pada ends in a sUP, or in a tiN˙ (1.4.14 suptin˙ antam. padam). These sUP and tiN˙ aﬃxes which come as terminal elements in a pada are introduced after bases which carry meaning. The sUP and tiN˙ aﬃxes themselves express meanings both grammatical and notional. The meaning of a base is always notional. Grammatical and notional meanings are expressed by aﬃxes, including sUP and tiN˙ . For example, consider nara + sU + odana + am −→ narah. odanam, and pac + LAT. −→ pac + S´aP+tiP = pac + a + ti = pacati = narah. odanam. pacati ‘the man cooks rice,’ where aﬃx LAT. is introduced after pac, a verbal base-input. Rule lah. karman. i ca bh¯ave c¯akarmakebhyah. states that a LAaﬃx is introduced after a transitive (sakarmaka) verb root when kart.r ‘agent’ and karman ‘object’ are denoted. This same LAT. can also be introduced after an intransitive (akarmaka) verb root when kart.r and bh¯ava ‘root-sense’ are denoted. The -ti of pacati is selected as a replacement of LAT. with the choice of expressing kart.r ‘agent.’
This choice of expressing kart.r with -ti has consequence for selecting the nominal inﬂectional ending sUP after nara and odana which happen to be the named kart.r and karman of the sentence. Now consider rule 2.3.1 anabhihite which makes a restrictive provision for selection of sUP. This rule would allow the selection of a sUP only when the denotatum of sUP is not already expressed. The dvit¯ıya¯ ekavacana ‘accusative’ ending -am of sUP which is selected for introduction after odana expresses the named object (karman) of pac. This is made possible because the -ti of pacati has expressed kart.r, and the karman is not already expressed (2.3.1 anabhihite; 2.3.2 karman. i dvit¯ıya¯ ). The choice to express kart.r by 2.3.18 kart.r-karan. ayos tr. t¯ıya¯ was not allowed in case of nara, the named agent of the sentence, because the -ti of pacati has already expressed it. It is for this reason that the prathama¯-ekavacana ‘nominative singular’ ending

---

<!-- page 21 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

9

of 2.3.46 pra¯tipadika¯rtha... had to be introduced after nara to express nothing but the sense of the nominal stem (pra¯tipadika¯rtha). If a choice is made to express the karman with the verbal pada at the time of selection of tiN˙ , a replacement of LAT. , rule 2.3.1 anabhihite would not allow introduction of -am after odana to express the karman. The nominative singular ending sU would be then introduced after odana to express its nominal stem notion. The kart.r of the sentence would then be expressed by 2.3.18 kart.r-karan. ayos tr. t¯ıya¯ . The sentence would then be naren. a odanam. pacyate, a passive counterpart of the active narah. odanam. pacati. This clearly shows that a pada in Pa¯n. ini expresses grammatical and notional relations in a sentence. Furthermore, its derivation must adhere to certain selectional restrictions which bear upon the derivation of a sentence as a whole. I shall subsequently show how derivation of complex bases is related closely to expression of kart.r, karman and bh¯ava, thereby yielding complex sentential strings. This expression of kart.r, karman, and bh¯ava directly relates to derivation of simple and complex sentences, and the derivational paths the strings follow.
Pa¯n. ini derives words (pada; 1.4.14 suptin˙ antam. padam) by ﬁrst extracting them from sentences, and then by analyzing their constituency in terms of bases and aﬃxes. A formal string of base(s) and aﬃx(es) is then processed through a network of rule applications to yield a fully derived pada. Since a pada necessarily carries an impression of grammatical and notional relations, and such relations are part of sentential meaning, a pada shares dependency relationship with a sentence. A pada cannot be fully derived without reference to its syntactic context. It thus becomes necessary for grammar to ﬁrst present an abstract syntactic representation of a sentence. Since action (kriya¯) forms the central denotatum of a Sanskrit sentence, its abstract syntactic representation is presented as an action-complex with participants, namely the k¯arakas. Pa¯n. ini sets up six k¯araka categories, namely ap¯ad¯ana, samprad¯ana, karan. a, adhikaran. a and kart.r, in this order.
Note that agent (kart.r) is a k¯araka which is independent of all other k¯arakas in the sense that the action (kriya¯) must necessarily have it as a participant. All other k¯arakas are named by the action depending on its own nature. It is not necessary for all six k¯arakas to participate in accomplishment of all actions. It is also not necessary that a speaker may not look at the role of a given k¯araka as that of some other. Consider the following sentences where ap¯ad¯ana could not be brought as a participant ka¯raka:

1. bhr. tyah. vane ka¯s..thaih. sth¯alya¯m. odanam. pacati kumbhaka¯ra¯ya ‘the servant cooks rice in a pot with wood in the forest for the pot-maker’
2. bhr. tyena vane k¯as..thaih. sth¯alya¯m. odanam. pacyate kumbhak¯ara¯ya ‘rice is cooked in a pot with wood in the forest for the pot-maker by the servant’

These two sentences are related in the sense that (1) is an action, and the other is its passive counterpart. Since Pa¯n. ini derives them with a common string, I shall present the abstract conceptual structure (CS) of the active, namely the ﬁrst sentence. A CS would constitute an action-complex where < action> will

---

<!-- page 22 -->

10

R.N. Sharma

be central. Each CS will obligatorily have at least one participant, namely agent < kart.r >, who will bring other participating k¯arakas into action, if the speaker so desires.

Let us now return to the CS of sentences (1):

CS1: bhr. tyah. vane k¯as..thaih. sth¯alya¯m odanam pacati ‘x engages in accomplishing the action named y (softening) intended for z at a place named r in m, a receptacle’

This sentence has ﬁve participants in its action complex, where since the agent

is expressed with the verbal pada pacati. In fact pacati, by itself, can be accepted

as a single pada sentence with its third person singular agent already expressed.

I shall next show the derivation of pacati ‘he / she / it cooks,’ along with the

derivation of other padas of the sentence (1).

Participant(s) Action <viklitti ‘softening’

< kart.r > > (3) pacati ‘he cooks’

step #1

pac ‘to cook’

<dh¯atu / sakarmaka>

1.3.1 bhu¯va¯dayo dh¯atavah. step #2

pac −→ pac + LAT. 3.1.91 dh¯atoh. {3.1.1 pratyayah. 3.1.2 para´s ca,

3.1.3 a¯dyuda¯tta´s ca,

3.1.4 anud¯attau suppitau}

<anud¯atta>

#1.1.67 tasma¯d ity uttarasya

<pan˜cam¯ı >

3.2.123 vartama¯ne la.t

<LAT. >

‘aﬃx LAT. is introduced after a verb root when action is denoted at the current

time’

3.4.69 lah. karman. i ca bha¯ve ca¯karmakebhyah.

<kart.r >

‘a LA-aﬃx is introduced after a transitive (sakarmaka) verb root when kart.r ‘agent’ and karman ‘object’ are denoted; it is introduced after an intransitive (akarmaka) verb root when kart.r ‘agent’ and ‘bh¯ava’ are denoted’

−→ pac + LAT.

<dh¯atu / sakarmaka / pratyaya / anud¯atta /vartam¯ana / kartr. / LAT. >

step #3

pac + (LAT. −→ tiP ) = pac + tiP

3.4.77 lasya ‘in place of that which is formed with LA (LAT. )’

#1.1.49 s. as..th¯ı stha¯neyog¯a

<.sas..th¯ı >

3.4.78 tip-tas-jhi-sip-thas-tha-mip-vas-mas-ta-a¯ta¯m-jha-tha¯s-a¯th¯am- dhvam-

id. -vahi-mahin˙ ’ −→ pac + tiP

<tiN˙ >

---

<!-- page 23 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

11

# tiN˙ -selection

1.4.99 lah. parasmaipadam ‘a LA-replacement is termed parasmaipada’ <tiN˙ / parasmaipada>
1.4.100 tan˙ ¯an¯av ¯atmanepadam ‘replacements of LA denoted by taN˙ , and also

¯ana, are termed a¯tmanepada’

<tiN˙ -a¯tmanepada>

1.4.102 t¯any ekavacana-dvivacana-bahuvacan¯any eka´sah. ‘elements of triads of tiN˙ are termed ekavacana, dvivacana and bahuvacana,

one after the other’

<ekavacana>

1.4.104 vibhakti´s ca

<vibhakti >

‘triads of sUP, and tiN˙ , are termed vibhakti’

1.4.107 tin˙ as tr¯ın. i tr¯ın. i prathamamadhyamottama¯h. ‘each triad of tiN˙ is termed

prathama, madhyama and uttama’

<prathama...>

1.4.108 ´se.se prathamah. ‘a prathama ‘the ﬁrst triplet of verbal ending’ is used when the remainder, i.e., tad ‘third personal pronominal,’ whether explicitly

stated or implicitly assumed, shares co-referential relation with it.’

step #4

<prathama> pac + tiP −→ pac + S´aP + tiP <S´aP> 3.4.113 tin˙´sit sa¯rvadh¯atukam ‘that which is a tiN˙ , or is marked with S´ as an

it, is termed sa¯rvadh¯atuaka’

<sa¯rvadh¯atuka>

3.1.67 sa¯rvadh¯atuke yak ‘yaK is introduced after a verb root when an aﬃx termed

sa¯rvadh¯atuka follows’

#1.1.66 tasminn iti nirdi.s.te pu¯rvasya <sa¯rvadh¯atuka>
3.1.68 kartari ´sap ‘aﬃx S´aP is introduced after a verb root when a

sa¯rvadh¯atuka with the denotation of kart.r follows’ <sa¯rvadh¯atuka> −→ tiN˙ -selection −→ pac + (S´ −→ φ) a (P −→ φ) + ti (P −→ φ)

step #5

1.4.14 suptin˙ antam. padam pac +a + ti −→ pacati ‘he /she / it cooks’ <pada> Referential Index <dh¯atu / sakarmaka / pratyaya / anud¯atta /vartam¯ana / kartr. / LAT. / tiN˙ / prathama / ekavacana / pada>

Let us now return to the derivation of (3) pacati, our base-input pac activates the grammatical device and is assigned the term dhtu by the rule 1.3.1 bhu¯va¯dayo dh¯atavah. of the Controlling Domain (CD; adhy¯aya one). It is then sent for scanning domain headings in the Obligatory Domain (OD; adhy¯aya three through ﬁve) of the grammar for possible rule application. It locates the domain of 3.1.91 dh¯atoh. for possible rule application because dh¯atoh. is the heading (adhika¯ra) of the domain and it also contains the term dh¯atu with which the base

---

<!-- page 24 -->

12

R.N. Sharma

input is identiﬁed. Term assignment (Naming a term) thus guides a base-input in locating domain of possible rule application. Further scanning of this domain, especially in view of its CS marker of <vartama¯na> ‘current time,’ facilitates application of rule 3.2.123 vartama¯ne la.t. This rule must be interpreted with the obligatory anuvr. tti of 3.1.1 pratyayah. , 3.1.2 para´s ca, 3.1.3 ¯adyuda¯tta´s ca and 3.1.4 anud¯attau suppitau. For these form the rule-context of the larger domain of which 3.1.91 dh¯atoh. is an interior domain. This is how 3.1.123 vartama¯ne la.t yields the meaning, ‘aﬃx (pratyaya) la.t is introduced after the transitive (sakarmaka) verb root pac when action is accomplished at the current time (vartama¯na); it is also marked with uda¯tta at the beginning (3.1.3 a¯dyuda¯tta´s ca). Since rule 3.1.91 dh¯atoh. is marked with pan˜cam¯ı ‘ablative,’ rule 1.1.67 tasma¯d ity uttarasya becomes operative. This assures that aﬃx la.t is introduced not just after (3.1.2 para´s ca) pac , but ‘immediately after’ pac. Our string pac + LAT. must now scan the domain looking for application of a rule guided by introduction of the term LAT. . We ﬁnd rule 3.4.69 lah. karman. i ca bh¯ave c¯akarmakebhyah. whereby we learn that a LA-aﬃx is introduced after an intransitive verb root when kart.r and karman are to be denoted. Our string pac + LAT. , where pac is marked with <sakarmaka> and LAT. is marked with <pratyaya, initial uda¯tta (3.1.1-3.13), + kart.r, + karman (3.4.69) >, now moves to the application of rules 3.4.77 lasya and 3.4.78 tip-tas-jhi-sip-thas-tha-mip-vas- mas... where it is faced with the problem of selecting one tiN˙ -element out of eighteen. Recourse must now be taken to reconstruction of referential index triggered by the terms LAT. and tiN˙ whereby rules 1.4.99, 1.4.100, 1.4.102, 1.4.104, 1.4.107 and 1.4.108 are brought close to application of rule 43.4..77 and 3.4.78. This is how we select tiP, an active (parasmaipada) third personal (prathama) singular (ekavacana) ending (vibhakti) with the denotation of kart.r ‘agent.’ Two things must be noted here: (i) selection of -ti is made on the basis of choice expression of kart.r ‘agent’ with reference to 3.4.69 lah. karman. i ca bh¯ave ca¯karmakebhyah. ; (ii) the anud¯atta accent assigned to LAT. in view of 3.1.2 a¯dyuda¯tta´s ca must be replaced with the anud¯atta of 3.1.4 anud¯attau suppitau, based on P as an it of tiP. The following is the summary representation of tiN˙ -selection:

1.4.99 lah. parasmaipadam 1.4.100 tan˙ ¯an¯av a¯tmanepadam

<parasmaipada> <¯atmanepada>

1.4.101 tin˙ astr¯ın. itr¯ın. iprathamamadhya...

<prathama>

1.4.102 t¯any ekavacana-dvivacana... <ekavacana>

1.4.104 vibhakti´s ca

<vibhakti>

1.4.108 ´se.se prathamah. 1.4.22 dvyekayor dvivacanaikavacane

<prathama> <ekavacana>

The -ti of our string pac + LAT. −→ ti (P −→ φ) = pac + ti is now assigned the term sa¯rvadh¯atuka by rule 3.4.113 tin˙´sit sa¯rvadh¯atukam. This triggers the reconstruction of the term <sa¯rvadh¯atuka> which, via reverse scanning, leads to application of rule 3.1.68 kartari S´aP read with 3.1.67 sa¯rvadh¯atuke yak. This rule introduces aﬃx S´aP after the verb root pac under the right condition of a sa¯rvadh¯atuka aﬃx, namely -ti, used with the denotation of kart.r ‘agent.’ Notice

---

<!-- page 25 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

13

that rules 3.4.78 tiptasjhisipthastha.. which introduces -ti is in the fourth quarter of adhy¯aya three. Rule 3.1.68 kartari ´sap which introduces S´aP is placed in the ﬁrst quarter of adhy¯aya three, even before 3.1.91 dh¯atoh. within whose domain 3.2.123 vartama¯ne la.t introduced aﬃx LAT. . The selection of -ti, via reconstruction of LAT. and tiN˙ , not only helps the selection of -ti but also facilitates application of 3.1.68 kartari ´sap, by way of -ti as right condition of application. This application is made possible by reconstruction of the term <sa¯rvadh¯atuka>. Our string pac + (S´ −→ φ)a(P −→ φ) + ti = pa + a + ti can exit this domain, and with assignment of new term in the Controlling Domain (CD), must gain access to domains of further rule application. A summary representation of terms which facilitated this derivation can be made in the form of a string with rule numbers as follows:

<dh¯atu / sakarmaka (1.3.1) / pratyaya (3.1.1) / anuda¯tta (3.1.4) / vartam¯ana (3.2.123) /kart.r (3.4.68) / LAT. (3.2.123) / tiN˙ (3.4.78) / parasmaipada (1.4.99) / prathama (1.4.101) / vibhakti (1.4.104) / ekavacana (1.4.12) / pada (1.4.14)>

(4) bhr. tyah. ‘servant’ Participant: Action pac ‘to cook’ bhr. tyah. ‘servant’ step #1

<kart.r > <viklitti/dha¯tu/sakarmaka /+ kart.r >

bhr. tya

<pra¯tipadika>

1.2.45 arthavad adh¯atur apratyayah. pra¯tipadikam ‘that which is meaningful

(arthavat ), non-root (adh¯atuh. ) and non-aﬃx (apratyayah. ) is termed pra¯tipadika’

1.4.53 svatantrah. kartt¯a; ‘kart.r is independent (svatantra)’

−→ bhr. tya ‘servant’

<pra¯tipadika; kart.r >

step #2

bhr. tya −→ bhr. tya + sU 4.1.1 n˙ ya¯p-pra¯tipadika¯t ‘an aﬃx occurs after that which is marked with

n˙ ya¯p, or else is a nominal stem’

4.1.2 su-au-jas-am-au.t-´sas-.ta¯-bhya¯m-bhis-n˙ e-bhya¯m-bhyas-n˙ asi-bhya¯m- bhyasn˙ as-os-a¯m-n˙ i-os-sup ‘the nominal endings sUP ’

−→ bhr. tya + sU #sUP -selection

2.3.1 anabhihite ‘when not already expressed’

2.3.64 pra¯tipadika¯rthalin˙ gaparima¯n. avacanam¯atre pratham¯a ‘prathama¯ ‘nominative’ is used when sense of the nominal stem (pra¯tipadika¯rtha), gender (lin˙ ga)

and number (vacana), alone, is to be expressed’

−→bhr. tya +sU

<pra¯tipadika/kartr. /sUP/ sU/ ekavacana>

1.4.22 dvyekayor dvivacanaikavacane ‘dvivacana ‘dual’ and ekavacana ‘singu-

lar’ occur when ‘two-ness, duality’ and ‘one-ness, singularity’ is to be denoted’

1.4.100 ...tr¯ın. i tr¯ın. i... ‘each triad...’

<ekavacana>

1.4.102 t¯any ekavacana-dvivacana-bahuvacan¯any eka´sah. ‘elements of triads of tiN˙ are termed ekavacana, dvivacana and bahuvacana, one after the other’

<ekavacana>

1.4.103 supah. ‘elements of triads of sUP are termed ekavacana,

---

<!-- page 26 -->

14

R.N. Sharma

dvivacana and bahuvacana, one after the other’ <sUP > 1.4.104 vibhakti´s ca ‘triads of sUP, and tiN˙ , are termed vibhakti’

step #3

<vibhakti >

bhr. tya + s(U −→ φ) = bh.rtya + s 1.4.13 yasma¯t pratyayavidhis tada¯di...

<an˙ ga>

6.4.1 an˙ gasya (no rule application in the an˙ ga domain)

1.4.14 suptin˙ antam. padam 1.4.110 vira¯mo’ vasa¯nam

<pada> <avas¯ana>

1.2.41 apr. kta ek¯al pratyayah. ‘an aﬃx formed with a single sound segment is

termed apr. kta’

<apr. kta>

step #4

8.1.16 padasya ‘of that which is a pada’ <pada>

8.2.66 sasaju.so ruh. −→ bhr. tya + (s−→r (U˜ −→ φ) −→ bhr. tya + r

8.3.15 kharavas¯anayor visarjan¯ıyah.

<avas¯ana>

−→ bhr. tya + (r−→ h. ) = bh.rtyah. ‘servant’ <pada>

Referential Index

<pra¯tipadika / kart.r/ vibhakti / pratham¯a/ sU / ekavacana / pada / avas¯ana / apr. kta>

The derivation of pada (4) bhr. tyah. ‘servant’ begins with the base-input bhr. tya which is assigned the term pra¯tipadika by rule 1.2.46 arthavad adh¯atur apratyayah. ... of the Controlling Domain (CD). Our string bhr. tya <pra¯tipadika> is now sent to the Obligatory Domain (OD) for locating an interior domain where possibility of rule application is indicated by the term pra¯tipadika. The interior domain of 4.1.1 n˙ ya¯p-pra¯tipadika is selected because the rule is formed with the term pra¯tipadika in it. The application of rule 4.1.2 svaujasmau.tchas..t¯abhya¯m... poses the problem of selecting one sUP aﬃx out of twenty-one. Similar to tiN˙ selection of (1) pacati, recourse must be taken to reconstruct the referential index of sUP. The selection of the nominative (prathama¯) singular (ekavacana) ending (vibhakti) will be made by bringing the following rules close to its context via reconstruction of referential index of sUP :
1.4.102 t¯any ekavacana-dvivacana-bahuvacana¯ny eka´sah. ‘elements of triads of tiN˙ are termed ekavacana, dvivacana and bahuvacana, one after the other’ <ekavacana>
1.4.103 supah. ‘elements of triads of sUP are termed ekavacana, dvivacana and bahuvacana, one after the other’
1.4.104 vibhakti´s ca ‘triads of sUP, and tiN˙ , are termed vibhakti’ 1.4.22 dvyekayor dvivacanaikavacane ‘ekavacana ‘singular’ and dvivacana ‘dual’ are used when singularity and duality is denoted’ 2.3.1 anabhihite ‘when not expressed otherwise’ 2.3.46 pra¯tipadika¯rthalin˙ gaparima¯n. avacanam¯atre pratham¯a ‘prathama¯ is introduced when nothing but the sense of the nominal stem (pra¯tipadika¯rtha), gender (lin˙ ga), measure (parima¯n. a) and number (vacana) is denoted’

---

<!-- page 27 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

15

Note here that this selection of -sU is made under the restrictive provision of 2.3.1 anabhihite. This rule can allow the selection of a sUP if its denotaum is not already expressed otherwise. Since pacati has already expressed the named kartr. of the sentence, bhr. tya must now be introduced with the nominative singular -sU to express nothing but its own sense (pr¯atipadika¯rtha), per rule 2.3.46 ‘pr¯atipadika¯rthalin˙ gaparima¯n. avacanam¯atre prathama¯.’ Our string bhr. tya +s (U−→ φ) is now sent to the Controlling domain where it is assigned the term pada (1.4.14 suptin˙ antam. padam). This term then facilitates scanning of domain headings beyond adhy¯aya ﬁve (Obligatory Domain), and thereby access to the domain of rules headed by 8.1.16 padasya. Rule 8.2.66 sasaju.so ruh. then replaces the -s with r (U˜ −→ φ), thereby yielding bhr. tya + r. This -r is then replaced with visarjan¯ıya of rule 8.3.15 kharavasa¯nayor visarjan¯ıyah. . Note however that rule 8.3.15 turns the -s turned -r to visarga under the condition of -s termed apr. kta (1.2.41 apr. kta ek¯al pratyayah. ). We now have bhr. tya +(r−→h. ) = bh.rtyah. , a pada.
The derivational history of bhr. tyah. can be captured with the following string of terms of its referential index which guided the derivation:

<pr¯atipadika (1.2.45) / kartr. (1.4.53) / sUP (4.1.2) / vibhakti (1.4.104) / pratham¯a (2.3.46) / sU (4.1.2) /ekavacana (1.4.22) / pada (1.4.53) / avasa¯na (1.4.110 ) / apr. kta (1.2.41)>

(5) vana ‘forest’

<pra¯tipadika; adhikaran. a>

1.2.45 arthavad adh¯atur apratyayah. pra¯tipadikam

4.1.1 n˙ ya¯p-pr¯atipadika¯t

1.4.45 ¯adha¯ro’ dhikaran. am #similar to step #2 of (4) bhr. tyah. 4.1.2 svaujasmau.t... # sUP-selection 2.3.1 anabhihite

2.3.36 saptamyadhikaran. e ca −→vana + N˙ i −→

6.1.87 a¯d gun. ah. (6.1.72 sam. hit¯ay¯am)

(6) ka¯s..tha ‘wood’

<pra¯tipadika; karan. a>

1.2.45 arthavad adh¯atur apratyayah. pra¯ipadikam

4.1.1 n˙ ya¯p-pr¯atipadika¯t

1.4.42 s¯adhakatamam karan. am #similar to step #2 of (4) bhr. tyah. 4.1.2 svaujasmau.t... 2.3.1 anabhihite

2.3.18 kartr. -karan. ayos t.rt¯ıya¯ −→ ka¯s..tha + bhis 1.4.13 yasm¯at pratyayavidhis tad¯adi pratyaye’ n˙ gam

6.4.1 an˙ gasya ka¯s..tha + bhis 7.1.9 ato bhis ais

−→ ka¯s..tha (bhis −→ ais) k¯a.s.tha + ai(s−→h. )

---

<!-- page 28 -->

16

R.N. Sharma

k¯a.s.thaih. ‘woods,’ a pada (7) odana ‘rice’

<pra¯tipadika; karman>

1.2.45 arthavad adh¯atur apratyayah. pra¯ipadikam 4.1.1 n˙ ya¯p-pr¯atipadika¯t

1.4.49 kartur ¯ıpsitatamam. karma #similar to step #2 of (4) bhr. tyah. 4.1.2 svaujasmau.t... −→odana + am

6.1.72 sam. hit¯aya¯m 6.1.106 ami pu¯rvah. −→odan(a+a −→ a)m = odanam

= odanam ‘rice,’ a pada

(8) sth¯al¯ı 1.4.45 a¯dha¯ro’ dhikaran. am... (9) kumbhaka¯ra¯ya

<pr¯atipadika; adhikaran. a

1.2.45 arthavad adha¯tur apratyayah. pr¯aipadikam 4.1.1n˙ y¯ap-pr¯atipadika¯t

1.4.49 karman. a¯ yam abhipraiti sa samprada¯nam #similar to step #2 of (4) bhr. tyah 4.1.2 svaujasmau.t... 2.3.1 anabhihite

2.3.13 caturth¯ı samprada¯ne −→ kumbhaka¯ra + N˙ e

1.4.13 yasm¯at pratyayavidhis tad¯adi pratyaye’ n˙ gam

6.4.1 an˙ gasya

7.1.13 n˙ er yah. −→ kumbhak¯ara + (N˙ e−→ya)

= kubhaka¯ra + ya

7.3.102 supi ca

−→ kumbhaka¯r (a −→ a¯ ) + ya

= kumbhaka¯ra¯ya

(10) kumbhaka¯rah. (a) D. Ukr. N˜ −→ 1.3.1 bhu¯va¯dayo dh¯atavah. <dha¯tu> −→ 1.3.3 halantyam

−→ 1.3.5 a¯dirn˜i.tud. avah. −→ 1.3.9 tasya lopah. (it-deletion) (D. U −→ φ)k.r(N˜ −→ φ) = k.r (b) k.r −→ 3.1.91 dh¯atoh. 1.1.62 tasma¯d ity uttarasya

3.1.1 pratyayah. 3.1.2 para´s ca

3.1.3 ¯adyuda¯tta´s ca <¯adyuda¯tta>

3.2.1 karman. y an. <karman>

---

<!-- page 29 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

17

3.1.92 tatropadama saptam¯ıstham

<upapada> ‘that which is spec-

iﬁed in this domain of dh¯atoh. with the saptam¯ı ‘locative’ is termed upapada ‘conjoined pada’

3.4.67 kartari k.rt

<kart.r >

k.r + a(N. −→ φ) = k.r + a (it -deletion)

1.4.49 kartur ¯ıpsitatamam. karma <karman>

2.3.1 anabhihite

2.3.65 kart.r-karman. oh. kr. ti −→kumbha + am

<karman / kartr. >

−→kumbha + ¯am k.r + a 2.2.19 upapadam atin˙ e

<upapada>

2.1.3 pra¯kkad. ¯ara¯t sama¯sah. −→kumbha am ka¯ra

<sama¯sa>

1.2.46 k.rt-taddhitasam¯as¯a´s ca 2.4.71 supo dha¯tupra¯tipadikayoh. −→kumbha + (am −→ φ) + ka¯ra

<pra¯tipadika>

= kumbhaka¯ra ‘pot-maker’

Our base input for deriving kumbhaka¯ra is verb root k.r ‘to do, make’ which ,in turn, is assigned the term <dh¯atu>. This serves as a mark for guiding the string for

access to the domain of 3.1.91 dh¯atoh. . Rule 3.2.1 karman. y an. then applies to introduce aﬃx aN. . The locative singular (saptam¯ı-ekavacana) of karman. i of this rule serves as a mark for bringing rule 3.1.92 tatropapadam. saptam¯ıstham ‘that which is speciﬁed with a locative (saptam¯ıstham) in this domain of dh¯atoh. is termed an upapada ‘a conjoined pada.’ If a choice is made to introduce aﬃx aN. after kr. , a pada denoting karman must be brought close to this context of k.r.
Selection of a nominal ending with the denotation of karman must be made in

accordance with the condition of 2.3.1 anabhihite ‘not already stated, otherwise.’

We realize that the aﬃx which is to be introduced, namely aN. , is a kr. t (3.4.67 kartari k.rt ) aﬃx, and hence it would denote kart.r. We may now select the genitive (.sas..th¯ı) plural ending -a¯m of rule 2.3.36 kart.rkarman. oh. k.rti. Note that 2.3.36 allows genitive to denote kart.r or karman, when they are not already expressed otherwise, and when a k.rt (non-tiN˙ ; 3.1.93 kr. d atin˙ ) aﬃx follows in construction. This is what enables us to meet the condition of 2.3.1 anabhihite,

and select genitive plural to express karman. The kart.r is already expressed with k¯ara. The derivational string at this stage is: kumbha + ¯am k.r + aN. . It has the referential index of <dh¯atu, upapada, pratyaya, k.rt, ady uda¯tta>. Rule 1.4.13 yasma¯t pratyayavidhis tad¯adi pratyaye’ n˙ gam assigns the term an˙ ga.

The string is sent to the domain of 6.4.1 an˙ gasya where rule 7.2.115 aco’ n˜n. iti applies to replace r. of the an˙ ga with its v.rddhi counterpart ¯ar. This application yields kumbha + ¯am k(.r −→ ¯ar) a(N. −→ φ) = kumbha + am ka¯ra. The term upapada must now guide the derivation. Rule 2.2.19 upapadam atin˙ allows the

formation of a compound (2.1.3 sama¯sah. ) which yields kumbha + am + ka¯ra. This string is then assigned the new term pra¯tipadika ‘nominal stem.’ This leads

to application of rule 2.4.71 supo dh¯atupra¯tipadikayoh. whereby a sUP, here am of kumbha + am + k¯ara, is subject to deletion by LUK. We now have

---

<!-- page 30 -->

18

R.N. Sharma

kumbha (am −→ φ)ka¯ra = kumbhaka¯ra, a derived nominal base (pra¯tipadika). This completes the derivational history of fully derived words (padas) which form simple sentences.
The following is a ﬂow-chart showing selectional restriction and agreement based of reconstruction of rule contexts by Referential Indices:

4 Derivational Mechanism
The derivational mechanism of the As.t.¯adhya¯y¯ı makes use of a network of bases and aﬃxes to derive padas, with application of select operations. These operations are carried out, primarily at two levels of naming and expressing, following certain conventions.
5 Levels of Derivation
The derivational mechanism of the As.t.a¯dhya¯y¯ı primarily operates on two levels of naming and expressing, with reference to the Action Complex (AC) of the Conceptual Structure (CS) of sentences:

---

<!-- page 31 -->

Rule Interaction, Blocking and Derivation in P¯an. ini

19

(1) CS1:

‘x accomplishes the action of making y at the current time’

bhr. tyah. gha.tam. karoti ‘servant makes a pot’

AC1: <kart.r >

Action: <dh¯atu>

Level 1: Naming: <term assignment>

bhr. tya <kart.r > <pra¯tipadika / kartr. > 1.2.45 arthavad... 1.3.1

Action: pac <dh¯atu> <dh¯atu / sakarmaka> bhu¯va¯dayo...

Level 2: <domain access / aﬃx placement>

<adhika¯ra / pratyaya>

bhr. tya <kart.r/ pr¯atipadika>

pac <dh¯atu/ sakarmaka>

1.2.45 arthavad...

3.1.7 dha¯toh. karman. ah. ...

4.1.1 n˙ ya¯p-pra¯t...

3.1.91 dh¯atoh.

4.1.2 svaujas...<sUP /pr¯atipadika> 3.1.123 vartama¯ne la.t <LAT. >

4.1.3 striy¯am

<dh¯atu / la.t / vartam¯ana>

4.1.76 taddhit¯ah. 4.1.82 samarth¯an¯ah.

3.4.77 tasya 3.4.78 tiptasjhi... <tiN˙ >

<rule Context>

3.1.1 pratyayah.

3.1.2 para´s ca

3.1.3 a¯dyuda¯tta´s ca

3.1.4 anud¯attau suppitau

<sUP -selection> <tiN˙ -selection> <agreement>

1.4.99 lah. parasmaipadam

1.4.100 tan˙ ¯an¯av ¯atmanepadam

1.4.102 t¯any ekavacana...

1.4.103 supah.

1.4.104 vibhakti´s ca

1.4.105 yu.smady upapade...

1.4.106 praha¯se ca manyopa...

1.4.107 asmady uttamah.

1.4.108 ´se.se prathamah.

1.4.21 bahu.su bahuvacanam

1.4.22 dvyekayor dvivacanaikavacane

6, Term Assignment (Naming; for exiting the Obligatory Domain)

1.4.109 parah. sannikars. ah. sam. hita¯ <6.1.72 sam. hita¯ya¯m >

1.4.13 yasma¯t pratyayavidhis...

<6.4.1 an˙ gasya>

1.4.14 suptin˙ antam. padam 1.4.18 yaci bham

<8.1.16 padasya> <6.4.129 bhasya>

Other terms, depending on the base-input, and inputs yielded by individual

applications, may be assigned to direct operations.

C. Convention

1. A base-input, i.e. dh¯atu and pra¯tipadika, when made input to the controlling domain (CD; the ﬁrst adhy¯aya of the grammar) activates this grammatical device with assignment of term (sam. jn˜¯a-ka¯rya) to the base-input(s). For example, the assignment of the term <dh¯atu> to pac by 1.3.1 bhu¯va¯dayo dh¯atavah. , and of the term <pra¯tipadika> to bhr. tya by 1.2.45 arthavad adh¯atur... This process can be called <Term Assignment>.
2. A base-input must gain access to the Obligatory Domain (OD; adhy¯aya three through ﬁve) of the grammar for scanning of domain headings (adhika¯ra) for possible rule application. A heading formed with the term assigned to the

---

<!-- page 32 -->

20

R.N. Sharma

base- input locates the domain for possible rule application. For example, pac, the base-input which is assigned the term <dh¯atu>, can opt for possible rule application in the domain of 3.1.5 guptijkidbhyah. san, 3.1.7 dh¯atoh. ..., and 3.1.91 dh¯atoh. , if it meets required condition. Access to the domain of possible rule application is made fairly automatic by assignment of the term, this case, <dh¯atu>. 3. Access to, and application of a rule within a domain, must be made in consonance with syntactico-semantic speciﬁcation of the CS, and terms currently assigned. This is the reason why pac was sent to the domain of 3.1.91 dh¯atoh. . 4. Each time a deﬁnitional term and abbreviated symbol is introduced to the derivational string, recourse should be taken to scanning of the domain for possible explanation and application via reconstruction of referential index. 5. A referential index of deﬁnitional terms and symbol must be reconstructed by scanning rules beginning with the Controlling Domain (CD) to the domain which triggers scanning. Terms and symbols of the referential index alone guide a string for further location of domains and thereby rule application. 6. Operations directed by terms of the referential index must be performed in the order the terms and symbols appear on the index. Operations relative to term1 must be completed before an operation required by term2 is performed. 7. The string, after each application, is sent back to the (CD) for possible assignment of new term, and thereby termination of operation in that domain. 8. Result of each application must be sent to the Controlling Domain (CD) for assignment of term for scanning of domains of possible rule-application.

---

<!-- page 33 -->

On the Generalizability of Pa¯n. ini’s Praty¯ah¯ara-Technique to Other Languages
Wiebke Petersen and Silke Hamann
Heinrich-Heine-Universit¨at Du¨sseldorf wiebke.petersen@phil.uni-duesseldorf.de
hamann@phil.uni-duesseldorf.de
Abstract. P¯an. ini deﬁnes the sound classes involved in grammatical rules by praty¯aha¯ras, i.e., a two-letter code based on the order of the sounds in the S´ivasu¯tras. In the present paper we demonstrate that P¯an. ini’s praty¯aha¯ra method is generalizable to the description of the phonological systems of other languages by applying it to the sound classes and phonological alternations of German. Furthermore, we compare P¯an. ini’s praty¯aha¯ra technique with the technique of describing phonological classes by phonological features, which is more common in Western phonology. It turns out that pratya¯ha¯ras perform better than features for the description of our sample of German phonological processes if one considers the quality criterion for class-description devices proposed by [10] which is based on the ratio of describable to actual classes.
Keywords: Panini, Sivasutras, phonological features, sound classes, formal concept analysis.
1 Introduction
The As..ta¯dhy¯ay¯ı – Pa¯n. ini’s circa 2 500 years old grammar of Sanskrit – starts with the S´ivasu¯tras, a list of the sounds of Sanskrit. Throughout his grammar, Pa¯n. ini uses the so-called praty¯aha¯ras – a two-letter code based on the order of the sounds in the S´ivasu¯tras – to deﬁne the sound classes involved in grammatical rules. Since Pa¯n. ini’s time, the S´ivasu¯tras have been studied intensively with focus on the following questions: Is the order of the sounds in the S´ivasu¯tras determined by the rules in the As..t¯adhy¯ay¯ı? Why does one sound (the glottal [h]) occur twice in the list? Are the S´ivasu¯tras minimal? And how did Pa¯n. ini develop the S´ivasu¯tras?
In the present article we make a ﬁrst attempt to describe the phonological processes of another language with the help of a S´ivasu¯tra-like list and pratya¯ha¯ras. For this purpose we chose German, another Indo-European language with a phonological system that diﬀers considerably from Sanskrit. We propose a list of all German sounds in the style of the S´ivasu¯tras that allows us to refer to the sound classes relevant for the description of German phonological processes in the form of pratya¯ha¯ras. This S´ivasu¯tra-like list of sounds will be called pratya¯h¯ara su¯tras in the following. Our aim is to test what the formalization of
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 21–38, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 34 -->

22

W. Petersen and S. Hamann

praty¯ah¯ara su¯tras for another language entails, and how far such a description diﬀers from the phonologically more common description of sound classes with phonological features.
The remainder of the paper is structured as follows. In section 2, we introduce two ways of referring to sound classes and phonological processes: the language-independent description of processes with phonological features and P¯an. ini’s approach with S´ivasu¯tras and pratya¯h¯aras that was especially designed for Sanskrit. Section 3 gives a short overview of the German sound system and the phonological processes that are the basis for our analysis of German. In the central section 4 we propose praty¯ah¯ara su¯tras for German. Finally, in section 5 we conclude with a brief discussion of our results.

2 Describing Sound Classes and Phonological Processes
Phonology is concerned with the sound system of a language and the alternations that these sounds undergo. In phonological theory, alternations between sounds are called phonological processes. In German, for instance, plural forms of nouns often involve a number of alternations compared to the singular forms, see the example in (1).
(1) Hand ÒØ℄ ‘hand’ - H¨ande Ò ℄ ‘hands’
In (1), the vowel [a] in the singular alternates with the vowel ℄ in the plural, and the consonant [t] in the singular alternates with the consonant [d] in the plural. Generative phonologists describe such processes by assuming that only one of the alternants is the form that native speakers or listeners have stored in their mind, while the other alternating form is derived from it. The sound representations stored in the mind are usually called underlying representations and are denoted in slashes, and the sounds that the speakers actually produce or the listeners hear are termed surface representations and are denoted in square brackets. For the singular-plural alternation in (1), it is usually assumed that the /d/ is the underlying representation, and the [t] is derived from it by a process that is called ﬁnal devoicing (see section 3.2.1 below).
Phonological processes can be described in terms of phonological rules. These rules are typically of the form “the underlying sound /A/ is realized as the surface sound [B] if it is preceded by sound C and/or followed by sound D”. This can be formalized as
(2) /A/ → [B] / C D .
The variables A, B, C and D in (2) can stand for single sounds, but also for classes of sounds. Whole classes of sounds can thus undergo a phonological process, be the result of a phonological process or pose the context of such a process. Sound classes can be described in several ways. In the following two subsections, we shortly present the commonly employed phonological description with features (2.1) and the description by pratya¯ha¯ras introduced by Panini for Sanskrit (2.2).

---

<!-- page 35 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

23

2.1 Featural Descriptions
Instead of listing whole classes of sounds in phonological processes, phonological descriptions usually employ phonological features. The key assumption of this description technique is that every sound in a language can be described suﬃciently by a set of binary features, making it distinct from all other sounds in the same language [7]. Phonological features have acoustic, articulatory or auditory deﬁnitions. For instance, the feature [+high] is deﬁned as an articulation with a high tongue body. Accordingly, the feature [−high] also refers to the dimension of tongue position; it is deﬁned as an articulation with a non-high tongue body. Sounds that share a feature and therefore a phonetic trait are called a natural class. The Spanish vowels [i u], for instance, are the only vowels in Spanish with the feature [+high] and therefore form a natural class in Spanish.
Unnatural classes of sounds are those that do not share a phonetic trait, and they usually do not occur as undergoer, result or context of a phonological process. A well-known example of an unnatural class is the context of the socalled ruki-rule in Sanskrit [[20], 61f.]. According to this process, the segments Ö℄, Ù℄, ℄ and ℄ cause retroﬂexion of the dental ×℄. The four segments forming the context of this rule form no natural class but rather an arbitrary set of sounds, because they involve two types of vowels (the back vowel Ù℄ and the front vowel ℄), and two types of consonants (a retroﬂex Ö℄ and a velar ℄), which cannot be referred to by one or a few phonological features. To describe this class, all feature speciﬁcations of all four segments have to be given. A situation like this, where the context of a rule cannot be referred to by a single or a few features, is called a disjunction in the phonological literature [e.g.[8], 216]. The disjunct context of the ruki-rule probably diachronically emerged from the merger of several processes [see the discussion in [6]chapter 4.3.4].
‘Binary phonological features’ are a relatively modern concept; the ﬁrst complete set of features has been proposed by [7]. However, the traditional S´iks.a¯s- and Pra¯ti´sa¯khyas-literature, which even predates Pa¯n. ini, already classiﬁes sounds by phonetic criteria that can be interpreted as phonological features [cf. the elaborated varga system of the spar´sas as described in [3,18]]. In his grammar, Pa¯n. ini uses the varga system in addition to his praty¯aha¯ra technique.

2.2 P¯an. ini’s S´ivasu¯tras

P¯an. ini’s grammar in Figure 1, which

oafrSe acnasllkerditS´, itvhaesu¯At.sr.ta¯asd.hEya¯acyh¯ı,siisnpgrleecseu¯dterda

by the 14 su¯tras given consists of a sequence

of sounds which ends in a consonant. This last consonant of each su¯tra is used

meta-linguistically as a marker to indicate the end of a su¯tra. In order to em-

phasize the technical nature of the end consonants, they are replaced by neutral marker elements Mi in Figure 1(III). Together the 14 S´ivasu¯tras deﬁne a lin-

ear order on the sounds of Sanskrit. The order is such that more or less each

class of sounds on which a phonological rule of Pa¯n. ini’s grammar operates forms

---

<!-- page 36 -->

24

W. Petersen and S. Hamann

Á·Óº ·ºÆ¸ ·º ·º ¸ Ç Þ¸ Ç º¸ Ý Ú · ¸ Ð·ºÆ¸ Î Ñ Þ·ºÆ Ò Ñ¸ Â Î¸

(I)

É· Ë¸ º Õ·º ¸ Ã È·º ·º ·ºÌ º Ø Ú¸ ·Ô Ý¸ Ë × ¸ Ð¸

a.i.un. .r.l.k e.on˙ ai.auc hayavarat. lan. n˜aman˙ an. anam jhabhan˜

(II)

ghad. hadhas. jabagad. ada´s khaphachat.hathacat.atav kapay ´sas.asar hal

a i u M1 .r .l M2 e o M3 ai au M4 h y v r M5 l M6 n˜ m n˙ n. n M7 jh bh M8 (III) gh d. h dh M9 j b g d. d M10 kh ph ch t.h th c t. t M11 k p M12 ´s s. s M13 h M14

Fig. 1. Pa¯n. ini’s S´ivasu¯tras for Sanskrit (I: Devan¯agar¯ı script; II: Latin transcription; III: Analysis – the syllable-building vowels are left out and the meta-linguistically used
consonants are replaced by neutral markers Mi)

an interval which ends immediately before a marker element.1 As a result, P¯an. ini could use a two letter code consisting of a sound and a marker called pratya¯h¯ara in order to designate the sound classes in his grammar. A praty¯ah¯ara denotes the continuous sequence of sounds in the interval between the sound and the marker (including the ﬁrst sound, but non of the markers). E.g., the pair iM2 in Figure 1 denotes the class [i, u, r., .l].
Concerning the question of how Pa¯n. ini developed the S´ivasu¯tras, it is generally agreed upon that the order of the sounds in the S´ivasu¯tras is primarily determined by the structural behavior of the sounds in the grammar rules and that the arrangement of the sounds is chosen such that brevity is maximized [cf.[17,12,1,9]]. [13] proves that Pa¯n. ini’s S´ivasu¯tras are an optimal solution for the following task: Given the set of all phonological classes which are encoded as pratya¯h¯aras in the As..ta¯dhya¯y¯ı, construct a list which is interrupted by markers such that each class can be denoted as a pratya¯h¯ara. Choose the list where the fewest sounds are repeated and minimize its length. It follows from the proof that the duplication of the sound [ ] in the S´ivasu¯tras is not superﬂuous and that the number of markers and thereby the number of S´ivasu¯tras cannot be reduced. In [14,15] it could be shown that there are nearly 12 000 000 alternative sound lists interrupted by markers which allow the formation of the required pratya¯h¯aras and which are of the same length as the S´ivasu¯tras.
3 The Phonemes and Phonological Processes of German
In order to describe the phonological processes of German with the technique of P¯an. ini’s pratya¯h¯aras, we ﬁrst have to establish the sound system of German and its phonological alternations. This is not a trivial task. While for Sanskrit it is
1 As mentioned before, Pa¯n. ini uses diﬀerent description techniques in parallel. Hence, he states not every phonological rule in terms of praty¯aha¯ras.

---

<!-- page 37 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

25

generally accepted that Pa¯n. ini’s grammar describes the phonological system of the language, no such undisputable description exists for German. Establishing the sound system of German involves decisions on whether certain sounds are considered to be mentally stored (underlyingly represented), or whether they are considered surface alternants that can be derived from another underlying form via a process. Underlying forms are usually meaning-distinguishing units with relatively unrestricted occurrences, and called phonemes, while those forms that are derived and have only a restricted context are called allophones. If a sound in a language is classiﬁed as an allophone, the phonological description of the language has to include a process to describe its derivation from an underlying phoneme. The velar nasal Æ℄, for instance, is considered by some phonologists [e.g.[19,21]] to be an allophone of the alveolar nasal phoneme»Ò» in German because it only occurs after a vowel and before a syllable break, in the so-called coda position. Such decisions on the phoneme status of a sound are often made purely on theoretical grounds: [2], e.g., postulated that the number of phonemes should be as small as possible while the number of processes is unrestricted. The following description of German is based on [21] and [5] and the theoretical assumptions therein.

3.1 The Sounds of German
The consonants and vowels of German forming the basis of our analysis are given in Figure 2 and 3, respectively [based on [5], pp. 31, 62, 68].
In Figure 2, two consonants are given in brackets, namely the glottal plosive È℄ and the velar fricative Ü℄. These sounds are bracketed in Figure 2 because their occurrence is predictable from the context and can therefore be derived with a process: The glottal stop occurs before syllable-initial stressed vowels, and the velar fricative after low and back vowels, as described with the phonological processes in 3.2.3 and 3.2.5 below. All other sounds in Figure 2 can be considered phonemes of German.
The vowels of German are given in Figure 3. Again, the sounds given in brackets are considered to be allophones of underlying phonemes. These are the low vowel ℄, which is the realization of the German »Ã» in coda position and

bilabial labio- alveolar post- palatal velar uvular glottal

dental

alveolar

plosive

pb

td

kg

(È)

nasal

m

n

Æ

fricative

fv sz

Ë

(x) Ã

h

aﬀricate

pf ts ØË

approximant

j

lateral

l

Fig. 2. Consonants of German

---

<!-- page 38 -->

26

W. Petersen and S. Hamann

´ µ Ý ´Ýµ Á

´µ

´µ

Ù ´Ùµ Í Ó ´Óµ Ç  ´µ

Fig. 3. Vowel triangle with vowels of German

therefore predictable, and the short tense vowels ¸ Ý¸ Ù¸ ¸ ¸ Ó℄. These short tense vowels are allophones of the long tense » ¸ Ý ¸ Ù ¸ ¸ ¸ Ó ». The latter only occur in stressed position, while the former only occur in unstressed position, see the phonological process of vowel shortening in 3.2.4.
In addition to the vowels in Figure 3, German also has three diphthongs; these are vowels that change their quality during the articulation. The diphthongs of German are ÇÁ¸ Á¸ Í℄.

3.2 Phonological Processes of German

The present description is restricted to processes that involve classes of sounds. These classes can be the undergoer, the result or the context of a phonological process. Processes where only single segments are involved are excluded because they are of no relevance for a description with S´ivasu¯tras or phonological features. Such a process is for instance the vocalisation of the German »Ã» to ℄ in coda position [see e.g. [21] pp. 252ﬀ. for a detailed description]. The following six processes meet this criterion and therefore seem to be relevant for our descriptions.

3.2.1 Final Devoicing German, like many other languages, has a process of ﬁnal devoicing that turns a class of voiced consonants into voiceless ones if they occur in word-ﬁnal position [see e.g., [21], pp. 199ﬀ.]. In the example in (1), the plural H¨ande Ò ℄ ‘hands’ is realized as ÒØ℄ with a ﬁnal [t] in the singular.
The whole list of sounds that undergo German ﬁnal devoicing are given in the formalization in (3).

(3)

→ / » ¸ ¸ ¸ Ú¸ Þ¸ »

Ô¸ Ø¸ ¸ ¸ ×¸ Ë ℄

word boundary

The group of sounds undergoing this process are traditionally described as obstruents, a term that refers to all plosives, fricatives, and aﬀricates in a language. As we can see in Figure 3, German has more obstruent phonemes than the ones listed in rule (3). The input to the rule lacks all aﬀricates and the fricatives ¸ Ã¸ ℄. While the voiceless phonemes Ô ¸ Ø×¸ ¸ ℄ cannot undergo ﬁnal devoicing

---

<!-- page 39 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

27

because they have no voiced counterpart, the voiced ℄ and Ã℄ are phonemes that do not occur in coda position, and therefore do not meet the requirements of the process, either.
In featural accounts of phonological processes, the voiced obstruents of German are referred to with the phonological features [+voiced, −sonorant], and the voiceless obstruents with [−voiced, −sonorant]. A rule with features would thus look as follows:
(3)f [+voiced, −sonorant] → [−voiced, −sonorant]/ word boundary
This rule is hyper-inclusive in the sense that it theoretically aﬀects all obstruents. Empirically, however, it is harmless as only the plosives and part of the fricatives occur in the relevant context and thus undergo the rule.

3.2.2 Regressive Nasal Assimilation The nasal alveolar /n/ is often assimilated to its following context in German. The word » Ò ÍÒ Ø» ‘arrival’, for instance, can be realized as Æ ÍÒ Ø℄, and » ÁÒ Ø» ‘gateway’ as ÁÑ Ø℄. This so-called regressive assimilation of nasals has to be formalized as two processes, velar and labial assimilation, distinguishing the two types of outcome:

(4) »Ò» → Æ℄ /

¸℄

(5)

»Ò» → Ñ℄ /

Ô¸ ¸ Ô ¸ ¸ Ú℄

velar nasal assimilation labial nasal assimilation

The two contexts of nasal assimilation can be referred to with the features [+velar, −sonorant, −continuant] for ¸ ℄, and the features [+labial, −sonorant] for Ô¸ . ¸ Ô ¸ ¸ Ú℄

3.2.3 Glottal Stop Epenthesis Vowel-initial words in German are always realized with a preceding glottal stop È℄, e.g. » Á» ‘egg’ is realized as È Á℄. The distribution of the glottal stop is formalized in the following epenthesis rule, a rule that inserts segments:
(6) ∅ → È℄ / word boundary vowel
The regular and predictable occurrence of the glottal stop is the reason why it is not considered a phoneme of German by many phonologists. The class of vowels forming the context of glottal stop epenthesis can be referred to with the phonological feature [−consonantal].

3.2.4 Vowel Shortening The German vowels ¸ Ý ¸ ¸ ¸ Ù ¸ Ó ℄, which are referred to as long and tense vowels, only occur in stressed position. Their short counterparts ¸ Ý¸ ¸ ¸ Ù¸ Ó℄, on the other hand, only appear in unstressed position, and are restricted to loanwords, e.g. the ﬁrst vowel in ÑÓÒ ℄ ‘monarchy’. This complementary distribution led most phonologists to tread the short tense vowels as allophones of the long ones and to describe their distribution with a process as it is formalized in (7).

---

<!-- page 40 -->

28

W. Petersen and S. Hamann

(7)

→ / » ¸ Ý ¸ ¸ ¸ Ù ¸ Ó »

¸ Ý¸ ¸ ¸ Ù¸ Ó℄

unstressed

The long, tense vowels are usually referred to with the features [+long, +tense, −consonantal], and their short counterparts with [−long, +tense, −consonantal].

3.2.5 Palatal Fricative Assimilation The palatal fricative » » is articulated with a more backed tongue position, i.e. as the velar fricative Ü℄, after the vowels ¸ ¸ Ù ¸ Í¸ Ó ¸ Ç¸ Í℄. This process is described in (8).

(8)

→ / » »

Ü℄

¸ ¸ Ù ¸ Í¸ Ó ¸ Ç¸ Í℄

The context vowels for palatal fricative assimilation can be described with the phonological features [−consonantal, +low] for ¸ ℄, and [−consonantal, +back] for Ù ¸ Í¸ Ó ¸ Ç¸ Í℄. This class is an example for a disjunct phonological context, where the sounds forming the context cannot be united under one feature description.

3.2.6 Umlaut In German, we can observe a process of vowel change that has lost its phonological context. This process, called umlaut, changes the vowels »Ù ¸ Í¸ Ó ¸ Ç¸ ¸
¸ Í» into Ý ¸ ¸ ¸ ¸ ¸ ¸ ÇÁ℄, respectively, when a noun is set in the plural. The example ÒØ℄ – Ò ℄ ‘hand (sg. – pl.)’ in (1) illustrated this. Umlaut also occurs for diminutive forms of nouns and the comparative forms of many adjectives, see e.g. [21] (1996: 182f.). A formalization is given in (9), though the context is not speciﬁed because the process is morphologically conditioned.

(9)

→ »Ù ¸ Í¸ Ó ¸ Ç¸ ¸ ¸ Í»

Ý ¸ ¸ ¸ ¸ ¸ ¸ ÇÁ℄

Such a process is familiar to Sanskrit scholars from the Sanskrit ablaut grades termed ÙÒ and ÚÖ .
For a deª scriptionª with phonological features, this process has to be divided into three subprocesses. The sounds Ù ¸ Í¸ Ó ¸ Ç℄ are [−consonant, −low, +back] and change to Ý ¸ ¸ ¸ ℄ with the feature speciﬁcation [−consonant, −low, +front]. The sound class ¸ ℄ with the speciﬁcation [−consonant, +low] changes to ¸ ℄ with the speciﬁcation [−consonant, −low, −high, +front, −tense]. And lastly, the single segment Í℄ changes to ÇÁ℄.
The six processes described in this section involve ten classes of sounds, namely the input and output of ﬁnal devoicing, the context of labial and velar nasal assimilation, the context of glottal stop epenthesis, the input and output of vowel shortening, the context of palatal fricative assimilation, and the input and output of the umlaut process. For a featural description of these processes, a total of 16 features has to be used.2 In the following section we will see how an account with pratya¯h¯aras for the same processes looks.

2 In order to make our analysis independent of the theoretical assumption that features are binary, we treat features like [+high] and [−high] as two distinct privative features.

---

<!-- page 41 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

29

4 Pratya¯ha¯ra su¯tras of German

In section 3, we deﬁned the collection of phonological processes and thereby implicitly the set of 10 phonological classes which we intend to represent as praty¯ah¯aras. Hence, our task is to develop a list of the German sound segments interrupted by markers in the style of the S´ivasu¯tras which allows the formation of a praty¯ah¯ara for each phonological class of the collection. A simple but undesirable solution to the problem would be to line up the phonological classes in one single list and to put a marker behind each class. In such a list, the number of occurrences of a phonological segment would be equal to the number of phonological classes to which the phonological segment belongs. Since P¯an. ini duplicates in his S´ivasu¯tras only one segment, namely ℄, it is obvious that the S´ivasu¯tras are constructed more economically: Pa¯n. ini aims at the minimization of the number of duplicated segments and the reduction of markers [9].
In [14,15] the general problem of generating economical praty¯aha¯ra su¯tras for given sets of sets has been tackled by applying methods from Formal Concept Analysis (FCA) [4]. In what follows we will apply those former results in order to construct adequate, economical praty¯aha¯ra su¯tras for German. A small example helps to clarify the required terminology of FCA:

abcd class1 × × class2 × × class3 × × class4 × × ×

Fig. 4. Example formal context (left) with corresponding concept lattice (right)
In Figure 4 (left) an example set of four classes, namely {a, b}, {b, c}, {c, d}, and {a, b, c}, is given in form of a formal context. A cross in the table indicates that an element (top row) belongs to a class (ﬁrst column). All four classes can be denoted as praty¯aha¯ras of the list of pratya¯h¯ara su¯tras
d c M1 b M2 a M3 (pratya¯h¯aras: bM3, cM2, dM1, cM3)
Note that no element in the pratya¯h¯ara su¯tras occurs twice. The concept lattice of the formal context is the set of all intersections (ordered by the inverted subset

---

<!-- page 42 -->

30

W. Petersen and S. Hamann

ÔØ × Ë

ÚÞ

 Á ÇÍ

ÓÙÝ

ÓÙÝ

Á ÇÁ Í Ô

devoicing input

××××××

devoicing output ××××××

vowel shortening in.

××× × × × ×

vowel shortening out.

×××××××

umlaut input

×××

× ××

×

umlaut output

×

××

×× × ×

palatal assimilation

××× ×× × × ×

×

nasal assim. velar

×

×

nasal assim. labial × × × ×

×

glottal epenthesis

×××××××××××××××××× × × × × × × × ×

Fig. 5. Formal context for the phonological classes of German (due to space limits, the segments ¸ ØË¸ Ø×¸ Ã¸ Ð¸ Æ¸ Ò¸ Ñ¸ ¸ È¸ ¸ ¸ Ü℄ which belong to no class are left out)

relation) which can be generated from the classes (plus the set of all elements). For our example, the set of all intersections is
{{ }, {c}, {b}, {a, b}, {b, c}, {c, d}, {a, b, c}, {a, b, c, d}}.
Figure 4 (right) shows a Hasse diagram of the concept lattice, i.e., a Hasse diagram of the set of the eight intersection sets ordered by the inverted subset relation. In the diagram the nodes (circles) correspond to the intersection sets and an edge between two nodes indicates that the set associated with the upper node is a subset of the one associated with the lower node and that no other intersection set is a superset of the set associated with the upper and a subset of the set associated with the lower node. The diagram is labeled as follows: each segment is written above the node corresponding to the smallest set to which it belongs, e.g., c labels the node for the set {c}, b the node for the set {b}, and a the one for {a, b}. The labeled Hasse diagram can be read as an inheritance hierarchy: each node corresponds to the set of segments by which the node or one of its supernodes is labeled. E.g., the node for ‘class 4’ corresponds to the set {a, b, c}, the bottom node corresponds to {a, b, c, d}, and the top node to the empty set.
The formal context for our collection of phonological classes for German is given in Figure 5. [13] proves that it is impossible to order the phonological segments in praty¯ah¯ara su¯tras without a single duplication if the corresponding concept lattice is not planar, i.e., if it is impossible to draw a Hasse diagram without intersecting edges. A Hasse diagram of the concept lattice of the formal context for our phonological classes of German is given in Figure 6. In order to improve readability, most of the labels are left out. One part of the diagram, namely the one corresponding to the subsets of the phonological class ‘glottal epenthesis’ (i.e. the vowels), stands out, as it is plane. The question is whether it is possible to give a plane drawing, i.e. a drawing without intersecting edges, of the remaining part of the diagram. By Figure 7 we will argue that such a drawing is impossible.

---

<!-- page 43 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

31

Fig. 6. Concept lattice for the phonological classes of German (the big circle indicates the planar part constituted by the vowel segments)
Figure 7 shows a Hasse diagram with intersecting edges of the concept lattice of the formal context constituted by the four classes ‘devoicing output’, ‘devoicing input’, ‘nasal assimilation labial’, and ‘nasal assimilation velar’. According to [11] and [16], a lattice has no plane diagram if it is possible to gain the graph
(i.e. the complete graph K5) from the graph of the diagram enlarged by an additional edge connecting the lowest and the top most node by removing some of the edges and contracting others. It is obvious that the graph in Figure 7 (top) can be constructed from the one in Figure 6 by leaving out some of the edges. The sequence of drawings at the bottom of Figure 7 starts with the graph from the top of the ﬁgure enlarged by an additional edge connecting the top and the bottom node. Each remaining graph is gained from its left neighbor by contracting the emphasized edge (thick grey edge). As the ﬁnal graph is isomorphic to the graph , the sequence proves that it is impossible to draw a diagram of the concept lattice in Figure 6 without intersecting edges. Hence, the concept lattice of the formal context of our collection of phonological classes is not planar. It follows that it is impossible to construct pratya¯h¯ara su¯tras for the formal context in which each sound segment occurs only once. Hence, analogously to the S´ivasu¯tras for Sanskrit we are forced to repeat at least one sound segment for our praty¯ah¯ara su¯tras for German.
Thus, the next step towards pratya¯h¯ara su¯tras for German is the identiﬁcation of sound segments which are good candidates for duplication. Hence, we are interested in identifying those segments for which we can add a copy to our formal context in Figure 5 and distribute the crosses in the table between the two copies in such a way that the corresponding concept lattice gets planar. The aim thereby is to copy as few sound segments as possible. Note that the nodes

---

<!-- page 44 -->

32

W. Petersen and S. Hamann

Fig. 7. Non-planar concept lattice for a selection of the phonological classes of German (key: S → Ë℄, Z → ℄)
of the four minimal nonempty sets ({ ¸ Ô}, { }, {Ú¸ }, { }) in Figure 7 do not diﬀer structurally with respect to their position in the concept lattice. Thus, it is better to duplicate one of the segments ℄ or ℄ than one of the remaining four segments, as duplicating for example the segment ℄ would force one to duplicate the segment Ô℄ too, since these two segments are not distinguishable with respect to the chosen phonological classes. In what follows we will concentrate on the duplication of the segment ℄; the duplication of ℄ would give analogous results.
If in the formal context in Figure 5 the segment ℄ is replaced by two copies – one classiﬁed as ‘devoicing input’ and the other one as ‘nasal assimilation velar’ – a plane Hasse diagram of the resulting concept lattice can be drawn (cf. Figure 8). In the diagram in Figure 8, the top node of the concept lattice, which corresponds to the empty set, is left out. The boundary graph of the diagram is called the S-graph of the formal context. In [14] it has been proven that the S-graph of a formal context is unique up to isomorphism if the formal context can be encoded as praty¯ah¯ara su¯tras without duplicated elements. Furthermore, the main theorem on S-sortability [15,14] states that a formal context can be encoded as praty¯ah¯ara su¯tras without duplicated elements if and only if its

---

<!-- page 45 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

Fig. 8. Concept lattice without top node for the phonological classes of German (key: c → ℄, S → Ë℄, ? → È℄, Z → ℄, N → Æ℄, R → Ê℄, Y → ℄, A → ℄, @ → ℄, I → Á℄, E → ℄, O¨ → ℄, O → Ç℄, U → Í℄, ¨o → ℄, ¨o: → ℄, aI → Á℄, OI → ÇÁ℄, aU → Í℄, E: →
℄, tS → ØË)

33

---

<!-- page 46 -->

34

W. Petersen and S. Hamann

concept lattice is planar and its S-graph contains all nodes labeled by elements. The following procedure quoted from [15] allows one to read oﬀ praty¯ah¯ara su¯tras with a minimal number of markers from the S-graph of a formal context.

Procedure for the construction of S-alphabets (here: pratya¯h¯ara su¯tras) with minimal marker sets:

1. Start with the empty sequence and choose a walk through the S-graph that: – starts and ends at the lowest node, – reaches every node of the S-graph, – passes each edge not more often than necessary, – is oriented such that while moving downwards as few labeled nodes with exactly one upper neighbor as possible are passed.
2. While walking through the S-graph modify the sequence as follows: – While moving upwards along an edge do not modify the sequence. – While moving downwards along an edge add a new marker to the sequence unless its last element is already a marker. – If a labeled node is reached, add the labels in arbitrary order to the sequence, except for those labels which have already been added in an earlier step.

Applied to our context of phonological classes of German, an optimal walk through the S-graph is depicted in the lower right of Figure 8. It starts at the bottom node and runs ﬁrst through the consonantal part and then through the vowel part of the S-graph. The walk through the vowel part of the S-graph is oriented counter-clockwise since this guarantees that while moving downwards as few labeled nodes with exactly one upper neighbor as possible are passed. The orientation of the walk through the consonantal part can be arbitrarily chosen. By traversing the depicted walk the following eight praty¯aha¯ra su¯tras for German can be read oﬀ:

ØË Ø× Ê Ð Æ Ò Ñ È Ü M1 Ø × Ë Ô M2 Ô Ú M3 Þ M4 

Á Á Ý Ù Ó M5 Í Ç Í Ó Ù M6 Ý M7 ÇÁ

M8

The ﬁrst su¯tra results from collecting all unclassiﬁed sounds at the bottom node and then walking upwards to the nodes labeled ‘ ’ and ‘ ’. Since the walk goes downwards after reaching the node labeled ‘ ’, a ﬁrst marker M1 has to be added to the sequence. The other su¯tras are constructed analogously. One sound segment, namely [ ] occurs twice in the list of praty¯aha¯ra su¯tras, namely in the ﬁrst and the fourth su¯tra. It is obvious that the phonological classes of German do not uniquely determine a list of praty¯ah¯ara su¯tras.3 As mentioned, the praty¯aha¯ra su¯tras would diﬀer if another walk through the S-graph would be chosen which could for example go ﬁrst through the vowel part or traverse the consonantal part clockwise. Additionally, all sound segments by which a single node is labeled can be added to the praty¯ah¯ara su¯tras in any desired order.

3 As mentioned in section 2.2, there are nearly 12 000 000 pratya¯h¯ara su¯tras of the same length for Sanskrit from which P¯an. ini has chosen one sample (i.e., the S´ivasu¯tras).

---

<!-- page 47 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

35

Finally, instead of duplicating the sound segment [ ], the sound segment [ ] could have been duplicated, resulting in diﬀerent praty¯aha¯ra su¯tras.
The praty¯ah¯ara su¯tras given above yield the following praty¯aha¯ras for the 10 phonological classes from our formal context in Figure 5:

M1 : Input to velar nasal assimilation M3 : Input to labial nasal assimilation M4 : Input to ﬁnal devoicing M2 : Output to ﬁnal devoicing ÙM6 : Context of palatal fricative assimilation M6 : Input to umlaut Ý M8: Output to umlaut M7: Input to vowel shortening M5 : Output to vowel shortening M8 : Context of glottal epenthesis

In the remainder of this section we will demonstrate how the praty¯aha¯ras for German can be employed for the description of the phonological rules discussed in section 3.2. The problem we are faced with is that phonological rules treat phonological classes not always as plain sets. In a phonological rule only the left and right contexts are unordered sets; the input and the output class has to be linearly ordered. The reason for this is that if a phonological rule is viewed as a rewriting rule then it has to be ensured that each segment of the input class has to be rewritten by its corresponding segment of the output class; e.g., the rule for ﬁnal devoicing has to ensure that » » is rewritten as Ø℄ and not as ℄. P¯an. ini’s S´ivasu¯tras fulﬁll this constraint, his pratya¯h¯aras are considered to be linearly ordered sets. But our formal model of the pratya¯h¯ara technique so far does not take internally ordered sound classes into account. By our deﬁnitions pratya¯ha¯ras denote unordered sets. Our approach only guarantees that the resulting praty¯ah¯ara su¯tras oﬀer the possibility to form for each phonological class a praty¯ah¯ara which denotes the unordered set of the elements of the class. However, for the concrete example of phonological classes for German we were able to arrange the sounds in our praty¯aha¯ra su¯tras such that the order of the sounds in the input classes corresponds to the reversed order of the sounds in the output classes. Take for example the rule of ﬁnal devoicing (rule (3) in section 3.2):

(3)’ M4 → M2/ word boundary

ﬁnal devoicing

Here, the pratya¯h¯ara M4 denotes the class Ú Þ ℄ and M2 the class Ø × Ë Ô℄. Hence, M2 denotes the devoiced counterparts of the elements of M4 in reversed order. The remaining rules of section 3.2 can be stated in terms of
pratya¯h¯aras as follows:

(4)’ »Ò» → Æ℄ / M1 (5)’ »Ò» → Ñ℄ / M3 (6)’ { } → È℄ / word boundary M8

velar nasal assimilation labial nasal assimilation
glottal stop epenthesis

---

<!-- page 48 -->

36

W. Petersen and S. Hamann

(7)’

M7 → M5 / unstressed

(8)’ » » → Ü℄ / ÙM6

(9)’ M6 → Ý M8

vowel shortening palatal fricative assimilation
umlaut

Hence, all phonological processes of German described in section 3.2 can be rewritten with pratya¯h¯aras of our proposed pratya¯h¯ara su¯tras.

5 Discussion
By describing the sound classes and phonological alternations of German with P¯an. ini’s pratya¯h¯ara technique we have demonstrated that the pratya¯ha¯ra method is generalizable to the description of the phonological systems of other languages. P¯an. ini’s aim while constructing his S´ivasu¯tras was to allow the formation of a praty¯ah¯ara for every phonologically motivated class, i.e. for every class that is needed in the description of the phonological processes of Sanskrit. He did not construct pratya¯h¯aras for all phonetically-based classes of sounds in a fashion that modern phonological features do. In the present article, we applied both methods, namely the description with pratya¯h¯ara su¯tras based solely on phonological processes and the description with features based on phonetic criteria, to a sample of phonological processes of German.4 Our phonological system of German consisted of 52 sound segments. This yields a total of 252 = 4 503 599 627 370 496 potential sound classes; just 10 of those classes are actually required for the description of our sample of phonological processes of German.
Any method for describing phonological classes which is not simply listing their elements overgenerates in the sense that it allows the formulation of classes which are needed in no phonological rule. The ratio of describable to actual classes constitutes a quality criterion for class-description devices [10]. Considering our example of German phonology, we get the following results: The pratya¯h¯aras for the 10 required classes are given in section 4, but how many pratya¯h¯aras can be formed with our praty¯ah¯ara su¯tras? Figure 9 lists the praty¯ah¯ara su¯tras for German and calculates for each single su¯tra the number of pratya¯h¯aras which can be build with its sound elements. For instance, each of the 5 sound elements of the second su¯tra can be combined with any of the succeeding 7 markers M2 . . . M8 in order to form a pratya¯h¯ara. Altogether 268 pratya¯h¯aras can be formed.5 Although at ﬁrst glance the ratio of describable to actual classes seems low for the praty¯ah¯ara method, this method still performs better than the description with phonological features: In section 3 we used a total of 16 features to describe the phonological processes under consideration. But 16
4 [13] combined the praty¯aha¯ra account and the featural account in an analysis of the vowel system of German and a constructed language, by transferring the featural speciﬁcations for the vowels into praty¯ah¯aras. It turned out that this demanded the duplication of disproportionately many sounds.
5 Usually one would exclude praty¯aha¯ras which are formed by the ﬁnal sound segment and the marker of a praty¯aha¯ra su¯tra and which thus only denote single sound segments. Therefore, only 260 praty¯aha¯ras of our praty¯aha¯ra su¯tras are well-formed.

---

<!-- page 49 -->

On the Generalizability of P¯an. ini’s Praty¯aha¯ra-Technique

37

ØË Ø× Ê Ð Æ Ò Ñ È Ü

Ø × Ë Ô M2

Ô Ú M3

Þ M4

 Á Á Ý Ù Ó M5

Í Ç Í Ó Ù M6

Ý M7

ÇÁ

M8

M1 15 × 8 5×7 3×6 4×5 11 × 4 6×3 4×2 5×1

Fig. 9. The praty¯aha¯ra su¯tras for German in tabular form
features yield a total of 216 = 65 536 classes which can be described by feature sets, thus far more than by pratya¯ha¯ras. Even if one drops the requirement that features should have acoustic, articulatory or auditory deﬁnitions and allows for unnatural features, a featural description of the 10 phonological classes cannot perform better than our pratya¯h¯ara description. As none of our 10 classes can be described in terms of an intersection of some of the other classes, every featural description which is able to distinguish those 10 classes has to make use of at least 10 diﬀerent features. A minimal featural description of the 10 classes would be to use the class identiﬁers (e.g., ‘devoicing input’, ‘devoicing output’) as features. Such a description would be minimal since none of the features would be reducible to other features. 10 features still yield a total of 210 = 1 024 classes which can be described by feature sets; this is nearly four times more than by the praty¯aha¯ras we employed.
One objection against our approach could be that we are only considering seven phonological processes while P¯an. ini is describing many more processes in the A.s.t¯adhya¯y¯ı. The main reason for this is that German exhibits far less Sandhi phenomena than Sanskrit. Furthermore, there is no standard description of the complete phonological system of German comparable to the A.s.t¯adhya¯y¯ı. In this paper we refrained from testing how hyper-inclusive processes could yield a more economic description of German. The main reason for this is that our mathematical approach to the induction of the praty¯ah¯ara su¯tras is not yet able to automatically identify cases of harmless hyper-inclusivity. This is left for future research.
It is important to note that Pa¯n. ini pursues a mixed strategy for the description of phonological classes: they are denoted by pratya¯h¯aras (e.g., su¯tra 6.1.77), they are referred to by the older phonetical varga-classiﬁcation (e.g., su¯tra 3.1.8) or their elements are simply listed (e.g., su¯tra 1.1.24). In contrast to Pa¯n. ini we restricted ourselves to the pratya¯h¯ara-method.
References
1. Cardona, G.: Studies in Indian grammarians I: The method of description reﬂected in the S´iva-Su¯tras. Transactions of the American Philosophical Society 59(1), 3–48 (1969)

---

<!-- page 50 -->

38

W. Petersen and S. Hamann

2. Chomsky, N., Halle, M.: The Sound Pattern of English. Harper and Row, New York (1968)
3. Deshpande, M.M.: Ancient Indian phonetics. In: Koerner, E.F.K., Asher, R.E. (eds.) Concise History of the Language Sciences: From the Sumerians to the Cognitivists, pp. 72–77. Elsevier, Oxford (1995)
4. Ganter, B., Wille, R.: Formal Concept Analysis. Mathematical Foundations, Berlin (1999)
5. Hall, T.A.: Phonologie: Eine Einfu¨hrung. Walter de Gruyter, Berlin (2000) 6. Hamann, S.: The Phonetics and Phonology of Retroﬂexes. Ph.D. thesis, Utrecht
Institute of Linguistics (2003) 7. Jakobson, R., Fant, G., Halle, M.: Preliminaries to Speech Analysis: The Distinctive
Features and their Correlates. MIT Press, Cambridge (1952) 8. Kenstowicz, M.: Phonology in Generative Grammar. Blackwell, Cambridge (1994) 9. Kiparsky, P.: Economy and the construction of the S´ivasu¯tras. In: Deshpande,
M.M., Bhate, S. (eds.) P¯an. inian Studies, Ann Arbor, Michigan (1991) 10. Kornai, A.: The generative power of feature geometry. Annals of Mathematics and
Artiﬁcial Intelligence (8), 37–46 (1993) 11. Kuratowski, K.: Sur le probl`eme des courbes gauches en topologie. Fundamenta
Mathematicae 15, 271–283 (1930) 12. Misra, V.N.: The Descriptive Technique of P¯an. ini. An Introduction. Mouton &
Co., The Hague (1966) 13. Petersen, W.: A mathematical analysis of P¯an. ini’s S´ivasu¯tras. Journal of Logic,
Language, and Information 13(4), 471–489 (2004) 14. Petersen, W.: Zur Minimalit¨at von P¯an. inis S´ivasu¯tras – Eine Untersuchung mit
Methoden der Formalen Begriﬀsanalyse. Ph.D. thesis, University of Du¨sseldorf (2008) 15. Petersen, W.: On the construction of S´ivasu¯tras-alphabets. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 78–97. Springer, Heidelberg (2009) 16. Platt, C.R.: Planar lattices and planar graphs. Journal of Combinatorial Theory (B) 21, 30–39 (1976) 17. Staal, F.J.: A method of linguistic description. Language 38, 1–10 (1962) 18. Staal, F.J.: The Sanskrit of science. Journal of Indian Philosophy 23(1), 73–127 (1995) 19. Vennemann, T.: The German velar nasal: a case for abstract phonology. Phonetica 22(65-81) (1970) 20. Whitney, W.D.: Sanskrit Grammar. Harvard University Press, Cambridge (1889) 21. Wiese, R.: Phonology of German. Oxford University Press, Oxford (1996)

---

<!-- page 51 -->

Building a Prototype Text to Speech for Sanskrit
Baiju Mahananda1, C.M.S. Raju2, Ramalinga Reddy Patil2, Narayana Jha1, Shrinivasa Varakhedi3, and Prahallad Kishore2
1 SCSVMV University, Kanchipuram 2 International Institute of Information Technology, Hyderabad
3 Sanskrit Acadamy, Osmania University, Hyderabad {baijunanda,mouli.raju,patilrlreddy53,shrivara}@gmail.com,
kishore@iiit.ac.in http://www.iiit.ac.in
Abstract. This paper describes about the work done in building a prototype text to speech system for Sanskrit. A basic prototype text-tospeech is built using a simpliﬁed Sanskrit phone set, and employing a unit selection technique, where prerecorded sub-word units are concatenated to synthesize a sentence. We also discuss the issues involved in building a full-ﬂedged text-to-speech for Sanskrit.
Keywords: Text to Speech for Sanskrit, Festvox.
1 Introduction
Developing a text to speech (TTS) system for Sanskrit primarily involves studying its phonology and phonetics [2]. Sanskrit has a highly developed system of phonemic description, developed in ancient times mainly for preserving Vedic texts[3].
1.1 Goal
We try to develop a text to speech system for simple classical Sanskrit, using simpliﬁed phone set of Sanskrit. This uses Direct synthesis, in which the speech signal is generated by direct manipulation of its wave form representation. Wave form concatenation, is representative of this synthesis category. In this approach, several fundamental periods of pre-recorded phonemes are simply concatenated. The phonemes are then connected to form words and sentences [1].
1.2 Previous Work
Making a computer to talk in diﬀerent languages has been attempted by many scholars from many years and they are successful. We are making an attempt to take forward the work done on “Making a Computer to talk Sanskit”. The following are few studies in this path:
1. Vani - An Indian Language Text to speech Synthesizer for Sanskrit [15], is a speech synthesizer which employs formant synthesis, in which the basic
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 39–47, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 52 -->

40

B. Mahananda et al.

assumption is that the vocal tract transfer function can be satisfactorily modeled by simulating formant frequencies and formant amplitudes. The synthesis thus consists of the artiﬁcial reconstruction of the formant characteristics to be produced. This is done by exciting a set of resonators by a voicing source or noise generator to achieve the desired speech spectrum, and by controlling the excitation source to simulate either voicing and voicelessness. The addition of a set of anti-resonators furthermore allows the simulation of nasal tract eﬀects, fricatives and plosives [1]. 2. Text to speech synthesis for Indian languages ( Acharya), is a syllable level representation of the text and each syllable directly translates into a sound that can be synthesized or simply played from a prerecorded piece of audio [2]. 3. Text to Speech conversion systems developed by C-DAC (Centre for Development of Advanced Computing) for various Indian languages supplementing the GIST Card [3].
Speech synthesis by concatenation of sub-word units (e.g. diphones) has become basic technology. It produces reliable clear speech and is the basis for a number of commercial systems. However with simple diphones, although the speech is clear, it does not have the naturalness of real speech[16].
In this work we are going to present you the general issues in building a TTS for Sanskrit, which could help in building an eﬃcient Speaking system for Sanskrit.

2 Sanskrit Orthography
2.1 Nature of Sanskrit Scripts
The basic units of the writing system in Sanskrit are characters which are an orthographic representation of speech sounds [3]. A character in Indian language scripts is close to a syllable and can be typically of the form: C*VN, where C is a consonant, V is a vowel and N is anusvAra, visarha, jivhAmUllya e.tc. . There is fairly good correspondence between what is written and what is spoken [5]. Sanskrit has richer set of characters than many of the other Indian languages.

2.2 Phone Set
Most institutions and scholars propose “Pa¯n. in¯1ya - S´iks.a” as a reference for written form of Sanskrit[8], in this book it is said that “The speech-sounds in Prakrit and Sanskrit are 63 or 64, according to their origin, has been said by Brahman (Svyambhu¯) himself.” among which vowels are 21, and consonants are (included stop, approximent, sibilant, nasal, palatels) 43 [4]. We are using UTF-8 format to represent the text. In our system we use 8 vowels and 40 consonants including other symbols, which are given in the below picture (Fig. 2) with respective IT3 representations 1.
1 Since the present computers can only process ASCII characters at machine level, we use a codding mechanism to represent each character (may belong to any language) in an intermediate format. This format was formulated by CMU.

---

<!-- page 53 -->

Building a Prototype Text to Speech for Sanskrit

41

Fig. 1. Set of phones and their respective IT3 Format of Devanagari Script used in TTS
There has been many discussions on the character set of Sanskrit, but some say devanagari alphabets are developed for writing Sanskrit (which are descended from brahmi scripts) [9], however as we all can see Sanskrit can be written in multiple languages.
Letters not used in TTS -
2.3 Suitability of Sikshaa Granthas for Building a TTS
Shiksha (Phonetics) explains the proper articulation and pronunciation of vedic texts. There are six parts of Shiksha letters (varnas), accent (swara), time consumed in articulating vowel (matra), eﬀort (bala) Melodius chanting of mantras (sama) and conjugation of letters (sandhi). If some mistake is committed in any of the above six, instead of giving the desired result it can prove to be disastrous as well [8].
In order to make an eﬃcient talking system all the parts of shiksha are to be met, however the present day systems can only add some parts of siksha, research has to be done to add the above six to the synthesized speech.

---

<!-- page 54 -->

42

B. Mahananda et al.

3 System Architecture

Sanskrit TTS system is implemented within the Festival/Festvox framework. Segmentation, unit selection and synthesis are done using Festvox and Festival framework.

3.1 Why Festvox?
Frameworks are built to ease the software development. But the frameworks which can be customized for user need are mostly preferred. Festvox oﬀers such a facility and it is an open software.

4 Letter to Sound Rule
Letter-to-sound rules are almost straight forward in Indian languages, as they are phonetic in nature. We write what we speak and we speak what we write, and hence generally the necessity of a pronunciation dictionary does not arise in our case. The pronunciation for a Sanskrit word such as chatura (clever) (the word chatura is the IT3 representation of the word “ ” using the chart speciﬁed above)in terms of phones marked with syllable boundaries can be written as (( ch a ) 1 ) (( t u ) 0 ) (( r a ) 0 ). As the characters in Indian language are close to a syllable, clustering C*VN can be done easily taking into account a few exceptions [6].
In this work, simple syllabiﬁcation rules are followed. Syllable boundaries are marked at the vowel position. If the number of consonants between two vowels is more than one, then ﬁrst consonant is treated as coda of the previous syllable and the rest of the consonant cluster as the onset of the next syllable. For stress assignment, the primary stress is associated with the ﬁrst syllable and secondary stress with the remaining syllables in the word. The integer 1 assigned to ﬁrst syllable in the word chatura indicates the primary stress associated with it. Letter to sound rules, syllabiﬁcation rules and assignment of stress patterns are diﬀerent for diﬀerent languages, which has to be speciﬁed accordingly. The architecture of Festival synthesis engine allows these rules to be written in Scheme, so that they get loaded at the run time, essentially avoiding recompilation of the core code for every new language.

5 Creation of Speech Database
A common trend in concatenative approach for TTS system is to use large database of phonetically and prosodically varied speech.
5.1 Text Selection for Sanskrit The quality of data-driven synthesis approaches is inherently bound to speech database from which the units are selected. It is important to have an optimal text corpus balanced in terms of phonetic coverage and the diversity in the

---

<!-- page 55 -->

Building a Prototype Text to Speech for Sanskrit

43

realizations of the units. Sanskrit has a vast literature starting from Vedic text to latest classical literature. In this work, the test corpus was generated from a set of simple Sanskrit sentences selected from daily life conversations . Some of the example sentences are given below. A common trend in concatenative approach for TTS system is to use large database of phonetically and prosodically varied speech.

5.2 Speech Data Collection
The number of Sentences recorded to generate Sanskrit database is 852. In these sentences we tried to cover the possible conversations related to our daily life. As it is not possible to complete the recording in a single session, to ensure consistency, the recordings were made at the same time every day.
6 Speech Segmentation
One of the most important tasks in building speech databases is the annotation of speech data with its contents (labeling) and the time alignment between labeling and speech (segmentation). Phoneme segmentation and labeling are highly desirable and useful for TTS as this information is used for classifying the speech units that helps to select and concatenate the right units in terms of linguistic and acoustic features.
The most precise way to annotate speech data is manually by linguistic experts. However, manual phoneme labeling and segmentation are very costly and require much time and eﬀort. Even well trained, experienced phoneme labelers using eﬃcient speech display and editing tools require about 200 times real time to segment and align speech utterances. To reduce this eﬀort considerably and aid the phoneme labelers, an automated segmentation tool is required. For automatic phoneme segmentation, we have been using the most frequently used Tool EHMM based phoneme recognizer.
Spoken Sentence (UTF-8): Spoken Sentence (IT3): aagachhatu! kim aavashyakam?

---

<!-- page 56 -->

44

B. Mahananda et al.

Fig. 2. Sample speech used for training with its labels, spectrogram and wave form
7 Unit Clustering and Synthesis
Given these segments, the unit selection algorithm (a Statistical Parametric Synthesizer) in the framework clustered the phones based on their acoustic differences. These clusters are then indexed based on higher level features such as phonetic and prosodic features. During synthesis, the appropriate clusters are sought using phonetic and prosodic features of the sentence. A search is then made to ﬁnd a best path through the candidates of these clusters. Though the units used here are phones, the acoustic frame of previous unit is used during clustering as well as for concatenation.
Clustergen is a statistical parametric synthesizer released as part of the Festival distribution [11]. It predicts frame-based MFCCs clustered using phonetic, metrical, and prosodic contexts. Unlike CLUNITS, the unit size is one frame (5ms by default), and the signal is partitioned at the HMM-state size level (3 states per phone). The clustering, done via CART, optimizes the standard deviation of the frames in the cluster. The frames are 24 coeﬃcient MFCCs plus F0. Clustergen oﬀers a number of options for clusters which can be single frames, trajectories, or trajectories with overlap and add. We used the simplest model for our TTS. Synthesis is done by predicting the HMM-state duration, then predicting each frame with the appropriate CART tree. The track of MFCC plus F0 vectors is re-synthesized with the MLSA algorithm [13], as implemented in the HTS system and already implemented within Festival.
8 Evaluation
In order to evaluate we conducted subjective and objective evaluations. As part of subjective evaluation 10 samples were extracted from the database. These

---

<!-- page 57 -->

Building a Prototype Text to Speech for Sanskrit

45

Table 1. MOS Test Results

Sentence Name Least Score Best Score Average Score

1

3

4

3.4

2

3

5

4.2

3

2

4

3.1

4

4

5

4.5

5

1

3

2.2

6

2

4

3.3

7

4

4

4

8

5

5

5

9

3

4

3.5

10

2

5

3.4

Total Average

3.67

samples were played to 10 Sanskrit speakers for obtaining mean opinion scores (MOS), i.e., score between 1 (worst) to 5 (best) [7]. The results were given in the Table 1.
For objective evaluation we have choose MCD. Mel cepstral distortion (MCD) is an objective error measure used to compute cepstral distortion between original and the synthesized MCEPs. Lesser the MCD value the better is synthesized speech. MCD is essentially a Euclidean Distance deﬁned as

MCD

=

10 ln 10

∗

25
2 ∗ (mcti ∗ mcie)2

(1)

i=1

where mcti and mcei denote the target and the estimated MCEPs, respectively. MCD is used as an objective evaluation of synthesized speech. Informally it is observed in [11] that an absolute diﬀerence of 0.2 in MCD values makes a diﬀerence in the perceptual quality of the synthesized signal and typical values for synthesized speech are in the range of 5 to 8.

Table 2. MCD Test Results

Synthesis with Diphones

MCD

6.474

To compute MCD, we have taken 20 sentences from Sanskrit database and synthesized using diphone as unit.
9 Discussion and Future work
So far, we have discussed the build process of a prototype text-to-speech for Sanskrit. While we have demonstrated the usefulness of this prototype text-tospeech for Sanskrit by conducting listening tests, it should be noted that there

---

<!-- page 58 -->

46

B. Mahananda et al.

exists several research issues that need to be addressed in building a full-ﬂedged text-to-speech for Sanskrit. The following are a few research issues that need to be addressed in building a complete voice for Sanskrit.
1. Choice of Phoneset: In this work, we have used a simpliﬁed phoneset (mostly borrowed from Hindi) to develop this prototype text-to-speech system. A careful acoustic-phonetic study needs to be done to build a phone set for Sanskrit. Also, the relationship between Akshara and the sound is assumed to one-to-one in Sanskrit. However, it is often may not be the case. Typically it is known that the Sanskrit scholars in the Northern part of India drop Schwas at the end. For example, /raama/ is pronounced as /raam/. Hence a carefully analysis need to be done to derive a Akshara (written symbol) to phone (spoken sound) correspondence.
2. Choice of Unit: In this work, we have used diphone as a unit for concatenation. This type of unit is found to be useful for English. It is also well known that syllable is a better unit for Indian languages which are mostly derived from Sanskrit. Hence, it is important to study various levels of units (diphone, syllable, polysyllable) for the case of Sanskrit TTS.
3. Nature of Sanskrit Language: In this work, the prototype TTS is built for spoken on conversational form of Sanskrit. It is known that the Sanskrit comes in various ﬂavors such as Vedic. Poetry prose, classical etc. and hence the nature of the Sanskrit language has to be studied and considered in developing a complete text-to-speech for Sanskrit.
4. Prosody: Prosody is often found to be manifested in intonation (rhythm), stress (energy), and duration patterns. Sanskrit is known for its richness in prosody. Hence, a study on prosodic aspects of Sanskrit TTS has to be conducted to identify suitable acoustic properties that can incorporated in TTS.
5. Incorporation of Sandhi Rules: Sanskrit is also known for Sandhi rules. The eﬀect of these Sandhi rules has to be studied and understood in order to implement these rules in Sanskrit TTS.

Acknowledgments
We would like to thank all the persons who participated in conducting the subjective evaluation.

References
1. Formant Synthesis by Thomas Styger and Eric Keller, Laboratoire danalyse informatique de la parole (LAIP), Universit´e de Lausanne, Switzerland
2. Acharya Project by IIT, Madras. Multilingual computing fo r Literacy and Education, http://acharya.iitm.ac.in/disabilities/tts.php
3. Ramani, S., Chandrasekar, R., Anjaneyulu, K.S.R. (eds.): KBCS 1989. LNCS, vol. 444. Springer, Heidelberg (1990)

---

<!-- page 59 -->

Building a Prototype Text to Speech for Sanskrit

47

4.

verse 3 and 4.

5. Sarkar, T., Keri, V., Yuvaraj, S., Prahalad, K.: Building Bengali Voice Using Fes-

tival. In: Proceedings of ICLSI 2005, Hyderabad, India (2005)

6. Kishore, S.P., Sangal, R., Srinvas, M.: Building Hindi and Telugu Voices using

Festvox. In: Proceedings of International Conference on Natural Language Pro-

cessing, ICON (2002)

7. Raghavendra, E.V., Desai, S., Yegnanarayana, B., Black, A.W., Prahallad, K.:

Global Syllable Set for Building Speech Synthesis in Indian Languages. In: Proceed-

ings of IEEE workshop on Spoken Language Technologies, Goa, India (December

2008)

8. About Sanskrit, http://www.sanskrit.nic.in/ABOUTSANSKRIT1.htm

9. Ager, S.: Omniglot writing systems and languages of the world,

http://www.omniglot.com/writing/devanagari.htm

10. Veera Raghavendra, E., Prahallad, K.S.: Database Pruning for Indian Language

Unit Selection Synthesizers. In: ICON-2009, Hyderabad, India (December 2009)

11. Black, A.W.: CLUSTERGEN: a statistical parametric synthesizer using trajectory

modeling. In: Proceedings of Interspeech, pp. 1762–1765 (2006)

12. Black, A.W., Lenzo, K.: Building voices in the festival speech synthesis system

(2000), www.festvox.org/festvox/index.html

13. Tokuda, K., Yoshimura, T., Masuko, T., Kobayashi, T., Kitamura, T.: Speech pa-

rameter generation algorithms for HMM-based speech. In: Proceedings of ICASSP,

Istanbul, Turkey, pp. 1315–1318 (June 2000)

14. Black, A.W., Bennett, C.L., Blanchard, B.C., Kominek, J., Langner, B., Prahallad,

K., Toth, A.R.: CMU Blizzard 2007: A Hybrid Acoustic Unit Selection System from

Statistically Predicted Parameters. In: Blizzard Challenge 2007, Bonn, Germany

(2007)

15. Jain, H., Kande, V., Desikan, K.: Vani - An India Language Text to speech Syn-

thesizer. IIT, Mumbai

16. Black, A.W., Taylor, P.: Automatically Clustering Similar Units for Unit Selection

in Speech Synthesis (1997)

---

<!-- page 60 -->

Rule-Blocking and Forward-Looking Conditions in the Computational Modelling of P¯an. inian Derivation
Peter M. Scharf
Department of Classics, Brown University scharf@brown.edu
Abstract. Attempting to model Pa¯n. inian procedure computationally forces one to clarify concepts explicitly and allows one to test various versions and interpretations of his grammar against each other and against bodies of extant Sanskrit texts. To model P¯an. inian procedure requires creating data structures and a framework that allow one to approximate the statement of Pa¯n. inian rules in an executable language. Scharf (2009: 117-125) provided a few examples of how rules would be formulated in a computational model of P¯an. inian grammar as opposed to in software that generated speech forms without regard to P¯an. inian procedure. Mishra (2009) described the extensive use of attributes to track classiﬁcation, marking and other features of phonetic strings. Goyal, Kulkarni, and Behera (2009, especially sec. 3.5) implemented a model of the asiddhavat section of rules (6.4.22-129) in which the state of the data passed to rules of the section is maintained unchanged and is utilized by those rules as conditions, yet the rules of the section are applied in parallel, and the result of all applicable rules applying exits the section. The current paper describes Scharf and Hyman’s implementation of rule blocking and forward-looking conditions. The former deals with complex groups of rules concerned with domains included within the scope of a general rule. The latter concerns a case where a decision at an early stage in the derivation requires evaluation of conditions that do not obtain until a subsequent stage in the derivation.
1 Implementations of Sandhi and Inﬂection
Scharf and Hyman implemented Pa¯n. inian sandhi rules in a portable framework using modiﬁed regular expressions in an XML ﬁle to model Pa¯n. inian rules, as described in Scharf 2009: 118-120. Each rule is written as one or more XML rule tags each of which contains several parameters: source, target, lcontext, rcontext, optional, and c. The optional parameters lcontext and rcontext specify the left and right contexts for the replacement of the source by the target. The optional parameter optional speciﬁes that the current state is to be duplicated and subsequent parallel paths created, one in which the rule is implemented and the other in which it is not. The parameter c (for comment) contains the
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 48–56, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 61 -->

Rule-Blocking and Forward-Looking Conditions

49

number of the Pa¯n. inian rule implemented by the rule tag. The implementation utilizes the Sanskrit Library Phonetic encoding scheme SLP1, described in Scharf

and Hyman 2010, Appendix B, in which Sanskrit sounds and common phonetic

features such as tones and nasalization are each represented by a single character.

The rule syntax utilizes a number of macros that model Pa¯n. inian structures.

Ý Macros are used to
sam˙ pras¯aran. a, etc.;

model Pa¯n. inian sound to create pratya¯ha¯ras:

classes: varn. a, , ,,

va, regtac,.;gaunn.da,tov¦rgdrdohuip,

sounds with common phonetic features: aspirated sounds, unaspirated sounds,

voiced sounds, unvoiced sounds, etc. For example, the macros @(f) and @(x) in

Ê  1.1.9 vt. represent the varnas and respectively. The macros @(eN) in 6.1.109
and @(ac) in 6.1.78 represent the pratya¯h¯aras (monothongs) and (vow-

els), respectively. Mappings are used to map sets of sounds onto corresponding

sounds, such as short vowels onto long, and unvoiced stops onto voiced stops.

Functions, such as lengthen, guRate, and vfdDiize, utilize the mappings to

facilitate implementation of common operations, namely, the replacement of a

vowel by Rules

its corrresponding long vowel, gun. a vowel, or are not pre-selected by hand; rather they

av¦rreddthriigvgoewreedl,

respectively. by the data

that meets the conditions for the application of the rule. Yet rules are arranged

in sequence and placed in blocks to ensure appropriate application of general

rules and exceptions. In particular, negations and identical replacements that

are exceptions select paths that avoid the application of rules of which they

are negations and exceptions. Hyman wrote a Perl program that converts the

XML ﬁle of regular expressions to Perl executable code. The model succeeds in

encoding Pa¯n. inian rules in a manner that allows the rules that come into play to be tracked. Rule tracking has valuable research and pedagogical applications.

Hyman (2009) describes the procedure by which the XML vocabulary to express

P¯an. ini’s sandhi rules was developed and how a series of stages converts the rules not only into executable Perl code, but also into a network, and a ﬁnite state

transducer. The latter, being extremely fast, will permit realtime web use of the

models.

Scharf and Hyman augmented the XML data structures created to model

P¯an. inian sandhi to allow derivation of nominal stems, as described in Scharf 2009: 120-23. They introduced an additional parameter morphid in the XML rule

tag that utilizes Scharf’s (2002: 29-30) set of nominal inﬂection tags. They fur-

ther enriched the XML structure utilized for nominal declension to model verbal

conjugation. Scharf (2009: 123-125) described Scharf and Hyman’s implementa-

tion of a computational model of Pa¯n. inian verbal inﬂection in a single cascade of rules that apply to whatever strings meet their conditions. The procedure begins

with a single set of verbal terminations for all verbs, just as Pa¯n. ini does, and introduces replacements on the basis of phonetic context. They widened the set

of tags employed by the parameter morphid to utilize, in addition to nominal

inﬂection tags, Scharf’s (2002: 30-31) verbal inﬂection tags. They added two pa-

rameters to the rule tag: lexid, and root. The former allows reference to the

class of the root in the Pa¯n. inian Dh¯atup¯a.tha. The latter allows reference to the original form of the root even when the previous rules have modiﬁed the input

---

<!-- page 62 -->

50

P. Scharf

string. The implementations of P¯an. inian inﬂection include rule tracking so that a derivational history of the form can be provided.

2 Participles
In 2008, Scharf and Hyman enriched the XML tagset further to allow derivation of participle stems. A vlexid parameter was added to allow reference to the class of the verbal root in the Dh¯atup¯a.tha and an affix parameter to allow reference to the aﬃx in the form in which it was originally introduced. The implementation of 1.2.21 demonstrates both parameters. 1.2.21 is a negation rule that optionally
denies -marking to the aﬃxes and ÚØ that have the initial augment , when they occur after a verbal root with a penultimate short Ù.
<rule source="k" target="" lcontext="@(begin)[@(al)]*u[@(hal)]#i:(?:ta|tavat);[@(it)]*" rcontext="[@(it)]*$" vlexid="^vt?1" lexid="^(ppp|pap)$" affix="@(nizWA)" root="^[@(char)]*`?[@(char)]*u[@(hal)];?[@(char)]*$" optional="yes" c="1.2.21 udupaDAdBAvAdikarmaRoranyatarasyAm"/>
<!--Only roots with the stem-forming affix Ô, for now roots
of class 1 or 10, are subject to the negation of k-marking. K¯a-
s´ik¯a : ²ÝÚ ¹ÌØ Ú Õ £ÝÑº Ø£Ò Ö Ò Ñ£Ú Ú Øº Rule includes
vlexid.-->
The parameter source has the value of the to be deleted; the parameter target has the null string value. The parameter lcontext has the value of a regular expression matching strings preceding the source parameter. These include conditions speciﬁed in the ablative in the rule, namely, a string in which there is a
penultimate short Ù, as well as any markers that might occur prior to the marker
to be deleted. The pound sign in the string marks the morpheme boundary between the stem and the aﬃx. This is followed by the initial augment separated from the rest of the aﬃx by a colon. The subsequent parenthesis matches
either ta or tavat representing the phonetic strings Ø or ØÚØ respectively. A
semicolon separates the phonetic form of the aﬃx from its markers, regardless of whether they are initial or ﬁnal. The value of the lcontext parameter ends with an expression including a macro reference that matches any possible marker.
<macro name="it" value="ufkNcYRtnprlS" c="1.3.2-8"/>
The rcontext parameter in the implementation of 1.2.21 again has the value of any marker that might follow represented in the source parameter. Now
it is possible that the string Ø belongs to some aﬃx other than . It is also
possible that an aﬃx has a ﬁnal marker rather than an initial one. In order to ensure reference to the desired aﬃx, the original form of the aﬃx is included as the value of the affix parameter. Here the location of markers as initial or ﬁnal

---

<!-- page 63 -->

Rule-Blocking and Forward-Looking Conditions

51

is preserved. The aﬃxes in question are introduced with an initial marker and
Ò are termed . Initial and ﬁnal markers are separated from the phonetic form
of the aﬃx by a grave accent and a semicolon respectively. A macro implements
the classiﬁcation rule as follows:

<macro name="nizWA" value="k`ta|k`tavat;u" c="1.1.26 ktaktavatU nizWA"/>

Ò The macro name nizWA is then employed in the implementation of 1.2.21, just
as the technical term is in 1.2.19 from where it recurs. Recurring terms are

explicitly stated in XML implementations of rules. The option parameter has

the value yes which initiates two streams of derivation from this point forward,

one in which the rule is applied and one in which it is not.

Now the K¯a´sik¯a on 1.2.21 states that the option is speciﬁcally distributed

²ÝÚ ¹ÌØ (

) in that the rule applies only when the aﬃxes occur after roots to which

Ô ²ÝÚ ¹ÌØ Ú Õ £ÝÑº the stem-forming aﬃx (vikaran. a) will be introduced (

Ø£Ò Ö Ò Ñ£Ú Ú Øº). In order to limit the rule in accordance with the K¯a´si-

k¯a’s statement, the rule includes the parameter vlexid which has the value of the

lexical tag assocated with the verbal root in our digital Dh¯atup¯a.tha. Pertinently, vlexid contains the roots’ class. The example shown of the implementation of

1.2.21 demonstrates the utility of the two new parameters vlexid and affix.

3 Blocking

Scharf and Hyman enriched the structure of the xml ﬁle containing rules for par-

Ù´× ­ ÔÚ ticiple derivation to allow complex blocking relations. Pa¯n. ini formulates general

rules ( ) and exceptions (

). Exceptions take precedence over their

related general rule. Where the exception alters the string so that it no longer

meets the conditions for the application of the general rule, it is easy to imple-

ment exceptions by simply ordering the rules in such a way that the exceptions

have the opportunity to apply ﬁrst. This is achieved by placing them earlier

in the cascade of rules. However, rule ordering alone is insuﬃcient to capture

the structure of Pa¯n. ini’s blocking relations where the exceptions do not alter the string. This is particularly obvious where the exception takes the form of

a negation. In previous versions of their framework, Scharf and Hyman rewrote

general rules that had negative exceptions to reﬂect the narrower scope of ap-

plication in the conditions of the general rule itself. Such a procedure makes it

more diﬃcult to implement accurate rule tracking. Hence we have enriched the

framework of the XML rule ﬁle to reﬂect blocking.

Let’s take, as an example, rules concerning the provision of the initial aug-

Ý ment . 7.2.35 provides that the augment occurs as the initial part of an
a¯rdhadha¯tuka aﬃx that begins with a consonant other than .

<rule source="" target="i:" lcontext="#" rcontext="[@(val)][@(al)]*@(anta)" affix="^(@(ArDaDAtuka))$" c="7.2.35 ArDaDAtukasyeq valAdeH"/>

---

<!-- page 64 -->

52

P. Scharf

For the purposes of the participal derivation in this ruleset, the macro name ArDaDAtuka refers to any one of several aﬃxes that form what are typically called participals as follows:

<macro name="ArDaDAtuka" value="k`vas;u|k`Ana;c|k`ta|k`tavat;u|k`tvA|tum;un|@(kftya)" c="3.4.114 ArDaDAtukaM SezaH, 3.4.115 liw ca"/>

The macro kftya again refers to what are called gerundives:

<macro name="kftya"

value="tavya|tavya;t|anIya;r|ya;t|k`ya;p|R`ya;t"

c="3.1.95 kftyAH prANRvulaH"/>

Ð ÚØÑ The general rule above accounts for the -augment in the inﬁnitive

(<

Ð¡ ‘cut’ + - ØÑ) and the gerundive stem Ð ÚØ²Ý (< Ð¡ ‘cut’ + - Ø²Ý), for

example.

Several negations that disallow the addition of the initial augment are ex-

ceptions to 7.2.35. Their domains are entirely included within the domain of

the general rule; hence these negations would have no scope of application if

they were not given precedence over 7.2.35. For example, 7.2.8 provides that the

Ý initial augment does not occur in aﬃxes termed k.rt that begin with a voiced
consonant other than or . The domain of 7.2.8 is included within the domain

Ý Ý of 7.2.35 because all kr.t-aﬃxes that begin with a voiced consonant other than or are also a¯rdhadh¯atuka aﬃxes that begin with a consonant other than .
Ý Obviously the set of voiced consonants excluding and is a subset of the set Ý of consonants excluding . Moreover, most kr.t-aﬃxes are ¯ardhadha¯tuka; only
eight kr.t-aﬃxes are termed s¯arvadha¯tuka rather than a¯rdhadha¯tuka due to being marked with , but they all begin with a vowel, in particular with or .1

Since the domain of 7.2.8 is entirely included within the domain of 7.2.35, 7.2.8

is an exception to 7.2.35 and takes precedence over it. The XML rule 7.2.8 is

formulated as follows:

<rule source="" target="" lcontext="#" rcontext="[@(vaS)][@(al)]*;[@(it)]*k[@(it)]*$" affix="^(@(kft))$" c="7.2.8 neqvaSi kfti"/>

The rule includes reference in the affix parameter to the macro kft, which

lists several kr.t-aﬃxes relevant to participle formation , including absolutive and non-Vedic inﬁnitives.

Ø¢ 1 (3.2.124, 3.2.130), Ò (3.2.124), ÒÒ (3.2.128),  Ò Ã (3.2.129), (3.2.28,

Ýß ÝßÒ 3.2.83), (3.1.137, 3.3.100), and

and

(3.4.9). Note that the vikaran. as

ç çÑ ç (3.1.73, 3.1.82), (3.1.78), and (3.1.81, 3.1.83) are taught before the head-

ØÓ¸ ing

in 3.1.91; hence they are not subject to being termed kr. t according to

ØÓ¸ the K¯a´sika¯ on 3.1.93 which limits the rule to the range of the heading

in

3.1.91 ( ¹ÑÒ ´Ú £Ö, etc.). Although these vikaran. as are not subject to the

-augment’s negation by 7.2.8, they are not subject to its provision by 7.2.35 or any

other rule either.

---

<!-- page 65 -->

Rule-Blocking and Forward-Looking Conditions

53

<macro name="kft" value="S`at;f|S`Ana;c|S`Ana;n|c`Ana;S|k`vas;u|k`Ana;c|k`ta| k`tavat;u|k`tvA|tum;un|@(kftya)" c="3.1.93 kfdatiN"/>
The exception 7.2.8 does nothing to change the conditions that would allow the general rule 7.2.35 from applying subsequently; it replaces nothing by nothing at the beginning of the aﬃx. Now, if 7.2.8 were placed prior to 7.2.35 in the cascade of rules without any other restriction, 7.2.35 would proceed to add the
-augment there. This is not desired. 7.2.8 should prevent 7.2.35 from applying. To achieve this, Hyman created an XML structure similar to an otherwise statement found in some programming languages. The structure groups rules within a block that contains two subsections: a try section and an otherwise section, as shown:
<block> <try> <rule/> <rule/> ... </try> <otherwise> <rule/> <rule/> ... </otherwise>
</block>
To eﬀect the blocking of 7.2.35 by 7.2.8, then we write 7.2.8 in the try block and 7.2.35 in the otherwise block as follows:
<block> <try> ... <rule source="" target="" lcontext="#" rcontext="[@(vaS)][@(al)]*;[@(it)]*k[@(it)]*$" lexid="^(@(kft))$" c="7.2.8 neqvaSi kfti"/> ... </try> <otherwise> <rule source="" target="i:" lcontext="#" rcontext="[@(val)][@(al)]*@(anta)" affix="^(@(ArDaDAtuka))$" c="7.2.35 ArDaDAtukasyeq valAdeH"/> </otherwise>
</block>
All instances of exceptions whose domains are totally included within the domain of their related general rule can be handled similarly. In instances of

---

<!-- page 66 -->

54

P. Scharf

partial blocking, the rule that contains a domain partially included within the
domain of a related general rule must be split into a rule with a totally included
domain and a rule with an excluded domain. Only the rule with the totally included domain will be placed in the try block.2

4 Look Ahead

Some rules in the As..t¯adhya¯y¯ı apply only under conditions that are not created
ù until subsequent rules apply. Let’s consider the case of 7.2.67, necessary for the
derivation of perfect active participles. Rules in the -section (6.4.1–7.4.97)

âÚ­Ò£  apply before rules for doubling and related stem-internal changes (6.1.1 etc.).

1.1.59

provides that the replacement of a vowel whose replacement

Ó £â ÌÑ¹Ý is conditioned by a vowel-initial aﬃx has the status of its substituend for the
purpose of doubling in the section of rules headed by 6.1.1

(See Cardona 1997: 60). This implies that the augment precedes vowel dele-

tion which in turn precedes doubling. Likewise, rules providing the augment

× to the beginning of an aﬃx apply before rules that change the stem prior to the
augmented aﬃx. Hence 7.2.67 applies to add the augment to the aﬃx - be-

fore 6.4.98 applies to delete the penultimate vowel of the root before vowel-initial

Ð Î ØÓÖÒ Ý ×¹Ý aﬃxes. The augment must be provided ﬁrst because without it, the aﬃx would

not be vowel-initial. 6.4.98 in turn applies prior to 6.1.8

.

However, 7.2.67, the rule that provides the augment, includes among its condi-

tions that the root be single-syllabled, and the K¯a´sik¯a explains that this refers

to the root after doubling has applied. But doubling can’t apply until after the

augment is added, which conditions deletion of the penultimate vowel. It is

not possible to evaluate the condition of being a single-syllabled doubled root

at the time the augment is added. It is not possible to evaluate a state of aﬀairs

brought about subsequent to a rule as a condition at the time of application

of that rule. Hence it is necessary to apply the rule tentatively, then trace the

derivation subsequent to the application of the rule to the point where its con-

ditions can be evaluated before deciding whether to apply the rule or not. Our

XML framework implements look ahead to achieve this by deriving the form

both with and without the rule application, then abandoning the rejected line

Ñ of derivation at the point the decision is made. Let’s trace the derivation of the perfect active participle of the root ‘go’

to illustrate our implementation. The P¯an. inian derivation is shown in Table 1;

the Scharf-Hyman derivation in Table 2.

The Scharf-Hyman framework does not at present implement sth¯anivadbha¯va;

it does not reintroduce replaced sounds at certain points where they are required

in the conditions of subsequent rules. Instead, for the time being, rules are mod-

Ñ iﬁed to include the replacements in the conditions of the subsequent rule. Hence
our derivation of the perfect active participle of diﬀers from the Pa¯n. inian

2 See Scharf (forthcoming) for a thorough examination of principles for determining rule precedence in cases of conﬂict between rules that have independent as well as
overlapping domains ( Ú Ø£Õ ).

---

<!-- page 67 -->

Rule-Blocking and Forward-Looking Conditions

55

Table 1. Pa¯n. inian derivation

Ñ Perfect active participle of the root

1 Ñ( )

MDhP 1.702 Ñ ×¢ Ô ØÇ

2 Ñ-Ð( Î)[ ÐÎ] 3.2.115 ÔÖÓ £ ÐÎ

3 Ñ-Ú×( ) 3.2.107

×æ

4 Ñ- :Ú×( ) 7.2.67

Ú¹£Ú × Ñ

5 Ñ- :Ú×( ) 6.4.98

Ñ Ò ÒÃÒ × ÐÓÔ¸ Ê´ÝÒ Ê

6a Ñ- :Ú×

1.1.59

âÚ­Ò£ 

6 Å Ñ- :Ú× 6.1.8

Ð Î ØÓÖÒ Ý ×¹Ý

7 Ñ- :Ú×

7.4.60

Ð ¸ £Õ¸

8 Ñ- :Ú×

7.4.62

Óæ ¸

9 ÑÚ×

Delete morpheme boundaries

Table 2. Scharf-Hyman derivation

Ñ Perfect active participle of the root

1 Ñ( )

MDhP 1.702 Ñ ×¢ Ô ØÇ

2 Ñ-Ð( Î)[ ÐÎ] 3.2.115 ÔÖÓ £ ÐÎ

3 Ñ-Ú×( ) 3.2.107

×æ

4 Ñ- :Ú×( ) 7.2.67

Ú¹£Ú × Ñ

5 Å Ñ- :Ú×( ) 6.1.8

Ð Î ØÓÖÒ Ý ×¹Ý

6 Å Ñ- :Ú×( ) 6.4.98

Ñ Ò ÒÃÒ × ÐÓÔ¸ Ê´ÝÒ Ê

7 Ñ- :Ú×

7.4.60

Ð ¸ £Õ¸

8 Ñ- :Ú×

7.4.62

Óæ ¸

9 Ñ- :Ú×

7.2.67

Ú¹£Ú × Ñ

10 ÑÚ×

Delete morpheme boundaries

derivation. While Pa¯n. ini implements penultimate vowel deletion by 6.4.98 (Table 1, step 5) prior to doubling by 6.1.8 (Table 1, step 6), we implement doubling by 6.1.8 ﬁrst (Table 2, step 5) and then delete the penultimate vowel by 6.4.98 (Table 2 step 6), modifying the condition for deletion to accomodate the doubled root. To avoid dealing with the issue of stha¯nivadbha¯va, deletion of the penultimate vowel is implemented after doubling by including the parameters to match a doubled root in the conditions for the application of 6.4.98. The root parameter compensates for the overbroad lcontext parameter to ensure the application of the rule only to the proper roots.
<rule source="a" target="" lcontext="@(begin)(?:[ghjKG]a[mns][ghjKG])" rcontext="[mns]#(?!a;N@(anta))[@(ac)][@(al)]*@(kNit)" root="^(g\am;/x|h\an;/a|j/an;/I|j\an;/a|j/an;\I|K/an;^u|G/as;/x)$" c="6.4.98 gamahanajanaKanaGasAM lopaH kNityanaNi"/>

---

<!-- page 68 -->

56

P. Scharf

In either derivation, 7.2.67 at step 4 must anticipate the state of the derivation at a subsequent step (at least step 6 in our derivation or step 7 in the Pa¯n. inian derivation). Our framework implements 7.2.67 in two XML rules to separate the single-syllable condition, which requires look-ahead, from conditions that don’t require look-ahead. The single-syllable portion is written as follows:
<rule source="" target="i:" lcontext="^(?:@(upasarga)-|)[@(hal)]*[@(ac)][@(hal)]*#" rcontext="vas@(anta)" affix="^(k`vas;u|S`at;f)$" root="@(DpAdi)[@(hal)]*[^/\][@(ac)][@(hal)]*@(Dpanta)" c="7.2.67 vasvekAjAdGasAm"/>
At step 4 we begin two lines of derivation, one with the augment and one without. Only the one with is shown in Table 2. At step 9, we evaluate the condition in 7.2.67 and, ﬁnding that the string qualiﬁes for augmentation, throw out the derivation without the augment.
We look forward to utilizing the enriched framework created for participle derivation in a revised, more faithful model of Pa¯n. inian inﬂection and hope to go on to implement derivational morphology generally.

References
1. Cardona, G.: P¯an. ini: His Work and its Traditions. Vol. I, Background and Introduction, 2nd edn. Motilal Banarsidass, Delhi (1997)
2. Goyal, P., Kulkarni, A., Behera, L.: Computer Simulation of As..ta¯dhya¯yi: Some Insights. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 139–161. Springer, Heidelberg (2009)
3. Huet, G., Kulkarni, A., Scharf, P. (eds.): Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402. Springer, Heidelberg (2009)
4. Hyman, M.: From P¯an. inian Sandhi to Finite State Calculus. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 253–265. Springer, Heidelberg (2009)
5. Mishra, A.: Simulating the P¯an. inian System of Sanskrit Grammar. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 127–138. Springer, Heidelberg (2009)
6. Scharf, P. M.: Ra¯mopa¯khya¯na–the Story of Ra¯ma in the Mah¯abha¯rata: An Independent-study Reader in Sanskrit. Routledge Curzon, London (2002)
7. Scharf, P.: Modeling P¯an. inian Grammar. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 95–126. Springer, Heidelberg (2009)
8. Scharf, P.: Rule selection in the As..ta¯dhya¯yi or Is P¯an. ini’s grammar mechanistic? In: Proceedings of the 14th World Sanskrit Conference, Kyoto University, Kyoto, September 1-5 (2009) (forthcoming)
9. Scharf, P., Malcolm, H.: Linguistic issues in encoding Sanskrit. The Sanskrit Library; Providence. Delhi; Motilal Banarsidass (2010)

---

<!-- page 69 -->

Sanskrit Compound Processor
Anil Kumar1, Vipul Mittal2, and Amba Kulkarni1
1 Department of Sanskrit Studies, University of Hyderabad, India anil.lalit22@gmail.com, apksh@uohyd.ernet.in
2 Language Technologies Research Centre, IIIT, Hyderabad, India vipulmittal@research.iiit.ac.in
Abstract. Sanskrit is very rich in compound formation. Typically a compound does not code the relation between its components explicitly. To understand the meaning of a compound, it is necessary to identify its components, discover the relations between them and ﬁnally generate a paraphrase of the compound. In this paper, we discuss the automatic segmentation and type identiﬁcation of a compound using simple statistics that results from the manually annotated data.
Keywords: Sanskrit Compound Splitter, Sanskrit Compound Type Identiﬁer, Sanskrit Compounds, Optimality Theory.
1 Introduction
In recent years Sanskrit Computational Linguistics has gained momentum. There have been several eﬀorts towards developing computational tools for accessing Sanskrit texts ( [12], [14], [23], [16], [7], [1]). Most of these tools handle morphological analysis and sandhi splitting. Some of them ( [10], [13], [8]) also do the sentential parsing. However, there have been almost negligible eﬀorts in handling Sanskrit compounds, beyond segmentation.
Sanskrit is very rich in compound formation. The compound formation being productive, forms an open-set and as such it is also not possible to list all the compounds in a dictionary. The compound formation involves a mandatory sandhi1. But mere sandhi splitting does not help a reader in identifying the meaning of a compound. Typically a compound does not code the relation between its components explicitly. To understand the meaning of a compound, thus, it is necessary to identify its components, discover the relations between them, and ﬁnally produce a vigrahava¯kya2 of the compound. Gillon [6] suggests
1 Sandhi means euphony transformation of words when they are consecutively pronounced. Typically when a word w1 is followed by a word w2, some terminal segment of w1 merges with some initial segment of w2 to be replaced by a “smoothed” phonetic interpolation, corresponding to minimising the energy necessary to reconﬁgure the vocal organs at the juncture between the words. [11]
2 An expression providing the meaning of a compound is called a vigrahav¯akya.
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 57–69, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 70 -->

58

A. Kumar, V. Mittal, and A. Kulkarni

tagging of compounds by enriching the context free rules. He does so by specifying the vibhakti, marking the head and also specifying the enriched category of the components. He also points out how certain components such as ‘na’ provide a clue for deciding the type of a compound. Pa¯n. ini captures special cases and formulates rules to handle them. Implementing these rules automatically is still far from reality on account of the semantic information needed for the implementation. In the absence of such semantic information, statistical methods have proved to be a boon for the language engineers. These statistical tools use manually annotated data for automatic learning, and in turn develop a language model, which is then used for analysis. In what follows we discuss the automatic segmentation and type identiﬁcation of compounds using simple statistics that result from the manually annotated data.

2 Sanskrit Compounds
The Sanskrit word sam¯asah. for a compound means samasanam which means “combination of more than one word into one word which conveys the same meaning as that of the collection of the component words together”. While combining the components together, a compound undergoes certain operations such as loss of case suﬃxes, loss of accent, etc.. A Sanskrit compound thus has one or more of the following features ( [17], [6]):
1. It is a single word (ekapadam).3 2. It has a single case suﬃx (ekavibhaktikam) with an exception of aluk com-
pounds such as yudhi.s.tirah. , where there is no deletion of case suﬃx of the ﬁrst component. 3. It has a single accent(ekasvarah. ).4 4. The order of components in a compound is ﬁxed. 5. No words can be inserted in between the compounds. 6. The compound formation is binary with an exception of dvandva and bahupada bahuvr¯ıhi. 7. Euphonic change (sandhi) is a must in a compound formation. 8. Constituents of a compound may require special gender or number diﬀerent from their default gender and number. e.g. pa¯n. ipa¯dam, p¯acika¯bh¯aryah. , etc.
Though compounds of 2 or 3 words are more frequent, compounds involving more than 3 constituent words with some compounds even running through pages is not rare in Sanskrit literature. Here are some examples of Sanskrit compounds involving more than 3 words.
1. £Ú Ú£ ùØ Ú ¸5=Ú£ - £Ú ù - Ø Ú- ¸ 2. ÚÖÑ ÎÑ ÑÖ Ñ Ö Ý ­ØÖ Ý Ð6= ÚÖ - Ñ Î - Ñ - ÑÖ  - Ñ Ö -
Ý -  ­Ø - Ö - Ý Ð
3 aikapadyam aikasvaryam ca sam¯asatva¯t bhavati [K¯a´sika¯ 2.1.46]. 4 aikapadyam aikasvaryam ca sam¯asatva¯t bhavati [K¯a´sika¯ 2.1.46]. 5 Ra¯ma¯yan. am 1-1-14. 6 Pan˜catantram in katha. mukham.

---

<!-- page 71 -->

Sanskrit Compound Processor

59

Fig. 1. Constituency representation of Ú£ £Ú ùØ Ú

3. Ð ²Ý Ô Ô¢ ÌÚ ´Ú Ú ØÝÓ Ô¢ ÌÚ ´ÚÚØ 7= Ð Ú - ØÝÓ - Ô¢ ÌÚ ´ÚÚØ

- ²Ý Ô - Ô¢ ÌÚ ´Ú -

The compounds are formed with two words at a time and hence they can be represented faithfully as a binary tree, as shown in ﬁgure 1.
Semantically P¯an. ini classiﬁes the Sanskrit compounds into four major types:
– Tatpurus.ah. : (Endocentric with head typically to the right), – Bahuvr¯ıhih. : (Exocentric), – Dvandvah. : (Copulative), and – Avyay¯ıbha¯vah.: (Endocentric with head typically to the left and behaves as
an indeclinable).

This classiﬁcation is not suﬃcient for generating the paraphrase. For example, the paraphrase of a compound v.rks. amu¯lam is vr. ks.asya mu¯lam and gr. hagatah. is gr. ham gatah. , though both of them belong to the same class of tatpuru.sah. . Based on their paraphrase, these compounds are further sub-classiﬁed into 55 sub-types. Appendix-A provides the classiﬁcation and Appendix-B describes the paraphrase associated with each tag.

3 Compound Processor
Understanding a compound involves (ref Fig 2)
1. Segmentation (×Ñ ×Ô É £ ¸), 2. Constituency Parsing (×Ñ ×Ô ¦ÚÝ¸), 3. Compound Type Identiﬁcation (×Ñ¹ØÔ Ô Ö Ý ¸), and 4. Paraphrasing ( Ú -Ú Ñ).
These four tasks form the natural modules of a compound processor. The output of one task serves as an input for the next task until the ﬁnal paraphrase is generated. 7 Kevalavyatireki-prakaran. am : Man. ikan. a [22].

---

<!-- page 72 -->

60

A. Kumar, V. Mittal, and A. Kulkarni

Sanskrit Compound

Segmenter

Constituency Parser

Type Identifier

Paraphrase Generator

Paraphrase
Fig. 2. Compound Analyser

3.1 Segmenter
The task of this module is to split a compound into its constituents. For instance, the compound
sumitra¯nandavardhanah. is segmented as
sumitr¯a-a¯nanda-vardhanah. Each of the constituent component except the last one is typically a compounding form (a bound morpheme)8.

3.2 Constituency Parser
This module parses the segmented compound syntactically by pairing up the constituents in a certain order two at a time. For instance,
sumitra¯-¯ananda-vardhanah. is parsed as
<sumitr¯a-<a¯nanda-vardhanah. >>

3.3 Type Identiﬁer

This module determines the type on the basis of the components involved. For

instance,

<sumitra¯-<¯ananda-vardhanah. >> is tagged as

<sumitr¯a-<¯ananda-vardhanah. >T6>T6

.

where T6 stands for compound of type s. a.s.t¯ı-tatpuru.sa. This module needs an access to the semantic content of its constituents, and possibly even to the wider context. 8 With an exception of components of an ‘aluk’ compound.

---

<!-- page 73 -->

Sanskrit Compound Processor

61

3.4 Paraphrase Generator
Finally after the tag has been assigned, the paraphrase generator [16] generates a paraphrase for the compound. For the above example, the paraphrase is generated as:
a¯nandasya vardhanah. = a¯nandavardhanah. , sumitra¯ya¯h. a¯nandavardhanah. = sumitra¯nandavardhanah. .

4 Compound Segmenter
The task of a segmenter is to split a given sequence of phonemes into a sequence of morphologically valid segments [18]. The compound formation involves a mandatory sandhi. Each sandhi rule is a triple (x, y, z) where y is the last letter of the ﬁrst primitive, z is the ﬁrst letter of the second primitive, and x is the letter sequence resulting from the euphonic combination. For analysis, we reverse these rules of sandhi and produce y + z corresponding to a x. Only the sequences that are morphologically valid are selected. The segmentation being non-deterministic, segmenter produces multiple splits. To ensure that the correct output is not deeply buried down the pile of incorrect answers, it is natural to prioritize solutions based on some scores. We follow GENerateCONstrain-EVALuate paradigm attributed to the Optimality Theory [21] for segmentation. As is true of any linguistic theory, the Optimality Theory basically addresses the issue of generation. Nevertheless, there have been successful attempts ( [4], [3]) to reverse the process of generation. It will be really challenging to implement the sandhi rules from As..t¯adhy¯ay¯ı as CONstraints and then reverse them for splitting. In this attempt however, we simply use the ‘cooked’ sandhi rules in the form of triplets. We describe below the GENerate-CONstrainEVALuate cycle of the segmenter and the scoring matrix used for prioritizing the solutions.
4.1 Scoring Matrix
A parallel corpus of Sanskrit text in sandhied and unsandhied form is being developed as a part of the Sanskrit Consortium project in India. The corpus contains texts from various ﬁelds ranging from children stories, dramas, pura¯n. as to Ayurveda texts. From around 100K words of such a parallel corpus, 25K parallel instances of sandhied and unsandhied text were extracted. These examples were used to get the frequency of occurence of various sandhi rules. If no instance of a sandhi rule is found in the corpus, for smoothing, we assign the frequency of 1 to this sandhi rule.
We deﬁne the estimated probability of the occurrence of a sandhi rule as follows:
Let Ri denote the ith rule with fRi as the frequency of occurrence in the manually split parallel text. The probability of rule Ri is:

---

<!-- page 74 -->

62

A. Kumar, V. Mittal, and A. Kulkarni

PRi =

fRi

n j=1

fRj

where n denotes the total number of sandhi rules found in the corpus. Let a word be split into a candidate Sj with k constituents as < c1, c2, ..., ck >
by applying k − 1 sandhi rules < R1, R2, ..., Rk−1 > in between the constituents. It should be noted here that the rules R1, ..., Rk−1 and the constituents c1, ..., ck are interdependent since a diﬀerent rule sequence will result in a diﬀerent constituents sequence. The sequence of constituents are constrained by a language model whereas the rules provide a model for splitting. We deﬁne two measures each corresponding to the constituents and the rules to assign weights to the possible splits.

Language Model. Let the unigram probability of the sequence < c1, c2, ..., ck > be P LSj deﬁned as:
k
P LSj = (Pcx )
x=1
where Pcx is the probability of occurrence of a word cx in the corpus.
Split Model. Let the splitting model P SSj for the sandhi rules sequence < R1, R2, ..., Rk−1 > be deﬁned as:

k−1
P SSj = (PRx )
x=1

where PRx is the probability of occurrence of a rule Rx in the corpus.

Therefore, the weight of the split Sj is deﬁned as the product of the language

and the split model as:

WSj

=

P LSj

∗ P SSj k

where the factor of k is introduced to give more preference to the split with less number of segments than the one with more segments.

4.2 Segmentation Algorithm
The approach followed is GENerate-CONstrain-EVALuate. In this approach, all the possible splits of a given string are ﬁrst generated and the splits that are not validated by the morphological analyser are subsequently pruned out.
Currently we apply only two constraints viz.
– C1 : All the constituents of a split must be valid morphs. – C2 : All the segments except the last one should be valid compounding forms.
The system ﬂow is presented in Figure 3.

---

<!-- page 75 -->

Sanskrit Compound Processor

63

Fig. 3. Compound Splitter: System Data Flow
The basic outline of the algorithm is:
1. Recursively break a word at every possible position applying a sandhi rule and generate all possible candidates for the input.
2. Pass the constituents of all the candidates through the morph analyser. 3. Declare the candidate as a valid candidate, if all its constituents are recog-
nised by the morphological analyser, and all except the last segment are compounding forms. 4. Assign weights to the accepted candidates and sort them based on the weights as deﬁned in the previous subsection. 5. The optimal solution will be the one with the highest weight.
Results. The current morphological analyser9 can recognise around 140 million words. Using 2,650 rules and a test data of around 8,26010 words parallel corpus for testing, we obtained the following results:
– Almost 92.5% of the times, the ﬁrst segmentation is correct. And in almost 99.1% of the cases, the correct split was among the top 3 possible splits.
– The precision was about 92.46% (measured in terms of the number of words for which ﬁrst answer is correct w.r.t. the total words for which correct segmentation was obtained).
– The system consumes around 0.04 seconds per string of 15 letters on an average.11
9 Available at http://sanskrit.uohyd.ernet.in/ anusaaraka/sanskrit/samsaadhanii/ morph/index.html
10 The test data is extracted from manually split data of Mah¯abha¯ratam. 11 Tested on a system with 2.93GHz Core 2 Duo processor and 2GB RAM.

---

<!-- page 76 -->

64

A. Kumar, V. Mittal, and A. Kulkarni

Table 1. Rank-wise Distribution

Rank % of words

1

92.4635

2

5.0492

3

1.6235

4

0.2979

5

0.1936

>5

0.3723

The complete rank wise distribution is given in Table 1.

5 Constituency Parser

Segmenter takes a compound as an input and produces one or more possible segmentations conditioned by the morphological analyser and the sandhi rules. Constituency parser takes an output of the segmenter and produces a binary tree showing the syntactic composition of the compound corresponding to each of the possible segmentations. Each of these compositions show the possible ways various segments can be grouped. To illustrate various possible parses that result from a single segmentation, consider the segmentation a-b-c of a compound. Since a compound is binary, the three components a-b-c may be grouped in two ways as < a < bc >> or << ab > c >. Only one of the ways of grouping may be correct in a given context as illustrated by the following two examples.
1. < baddha- < ja¯mbu¯nada- srajah. >> 2. << tapas-sva¯dhy¯aya >- niratam >

With 3 components, only these two parses are possible. But as the number of constituents increase, the number of possible ways the constituents can be grouped grows very fast. The constituency parsing is similar to the problem of completely parenthesizing n+1 factors in all possible ways. Thus the total possible ways of parsing a compound with n + 1 constituents is equal to a Catalan number, Cn [13] where for n ≥ 0,

Cn

=

(2n)! (n + 1)!n!

The task of the constituency parser is then to choose the correct way of grouping the components together, in a given context. To the best of our knowledge no work has been initiated yet that produces the best constituency parse for a given segmentation, in a given context.

6 Type Identiﬁer
After getting a constituency parse of a compound, the next task in the compound analysis is to assign an appropriate operator (tag) to each non-leaf node. This operator will then operate on the leaf nodes to produce the associated meaning.

---

<!-- page 77 -->

Sanskrit Compound Processor

65

We use manually tagged corpus as a model for predicting the tags, given a pair of constituents of a compound. Manually tagged corpus consists of approximately 150K words which contain 12,796 compounds12. These texts were tagged using the tagset given in appendix-I. All these compounds are thus tagged ‘in context’ and contain only one tag. This corpus formed the training data. Another small corpus with 400 tagged compounds from totally diﬀerent texts, was kept aside for testing.

Some features of the manually tagged data
1. Around 10% of the compounds were repeated. 2. The 12,796 tokens of compounds contain 2,630 types of left word and 7,106
types of right word. 3. The frequency distribution of highly frequent tags is shown in Table 2. To
study the eﬀect of ﬁne-grained-ness we also merged the sub-types. Table 3 gives the frequency distribution of major tags, after merging the sub-types.

Table 2. Distribution of Fine-grain-Tags

Tag % of words

T6

28.35

Bs6

12.45

K1

9.63

Tn

8.56

Di

7.23

U

5.73

Table 3. Distribution of Coarse-Tags

Tag % of words

T

52.43

B

18.96

K

12.04

D

8.84

U

5.73

We deﬁne,

P (T /W1 − W2) = probability that a compound W1 − W2 has tag T.

Assuming that occurrence of W1 and W2 are independent,

P (T /W1 − W2) = P (T /W1) ∗ P (T /W2)

where

P (T /Wi) =

P (T ∗Wi) P (Wi)

,

i=

1,2.

Since the data is sparse, to account for smoothing, we deﬁne, for unseen in-

stances,

P (T.Wi)

=

1 F

,

P (Wi)

=

1 F

,

where F is the total number of manually tagged compounds.

12 Only compounds with 2 components were selected.

---

<!-- page 78 -->

66

A. Kumar, V. Mittal, and A. Kulkarni

6.1 Performance Evaluation
The test data of 400 words are tagged ‘in context’. While our compound tagger does not see the context, and thus suggests more than one possible tag, and ranks them. Normally a tool is evaluated for its coverage and precision. In our case, the tool always produces tags with weights associated with them. The coverage and precision therefore are evaluated based on the ranks of the correct tags. Table4 shows results of 400 words with a coarse as well as ﬁne grained tagset.

Table 4. Precision of Type Identiﬁer

with 55 tags

with 8 tags

Rank no of words % of words no of words % of words

1

252

63.0

291

72.7

2

44

10.9

53

13.2

3

29

7.2

38

9.5

Thus, if we consider only the 1st rank, the precision with 8 tags is 72.7% and with 55 tags, it is 63.0%. The precision increases substantially to 95.4% and 81.1% respectively if we take 1st three ranks into account.
The performance of the type identiﬁer can be further improved by using semantically tagged lexicon. There are around 200 rules in the A.sta¯dhy¯ay¯ı which provide semantic contexts for various compounds. One such example is the Pa¯n. ini’s su¯tra annena vyan˜janam (2.1.34). This su¯tra gives a condition for forming tr. t¯ıya¯ tatpuru.sah. compound. Thus what is required is a list of all words that denote eatables. A lexicon rich with such semantic information would enhance the performance of the tagger further. The compound processor with all the functionality described above is available online at http://sanskrit.uohyd.ernet. in/samAsa/frame.html
References
1. Bharati, A., Kulkarni, A.P., Sheeba, V.: Building a wide coverage Sanskrit Morphological Analyser: A practical approach. In: The First National Symposium on Modelling and Shallow Parsing of Indian Languages, IIT-Bombay (2006)
2. Bhat, G.M.: Sam¯asah. . Samskrita Bharati, Bangalore, Karnataka (2006) 3. Fortes, F.C.L., Roxas, R.E.O.: Optimality Theory in Morphological Analysis. In:
National Natural Language Processing Research Symposium (January 2004) 4. Fosler, J.E.: On Reversing the Generation Process in Optimality Theory. In: Pro-
ceedings of the Association for Computational Linguistics (1996) 5. Gillon, B.S.: Exocentric Compounds in Classical Sanskrit. In: Proceeding
of the First International Symposium on Sanskrit Computational Linguistics (SCLS 2007), Paris, France (2007) 6. Gillon, B.S.: Tagging Classical Sanskrit Compounds. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 98–105. Springer, Heidelberg (2009)

---

<!-- page 79 -->

Sanskrit Compound Processor

67

7. Hellwig, O.: Sanskrit Tagger: A Stochastic Lexical and POS Tagger for Sanskrit. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 266–277. Springer, Heidelberg (2009)
8. Hellwig, O.: Extracting Dependency Trees from Sanskrit Texts. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 106–115. Springer, Heidelberg (2009)
9. Hoeks, J.C.J., Hendriks, P.: Optimality Theory and Human Sentence Processing: The Case of Coordination. In: Proceedings of the 27th Annual Meeting of the Cognitive Science Society, Erlbaum, Mahwah, NJ, pp. 959–964 (2005)
10. Huet, G.: Shallow syntax analysis in Sanskrit guided by semantic nets constraints. In: Proceedings of International Workshop on Research Issues in Digital Libraries, Kolkata (2006)
11. Huet, G.: Lexicon-directed Segmentation and Tagging of Sanskrit. In: XIIth World Sanskrit Conference, Helsinki, Finland (August 2003); Tikkanen, B., Hettrich, H. (eds.) Themes and Tasks in Old and Middle Indo-Aryan Linguistics, Motilal Banarsidass, Delhi, pp. 307–325 (2006)
12. Huet, G.: Formal structure of Sanskrit text: Requirements analysis for a Mechanical Sanskrit Processor. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 162–199. Springer, Heidelberg (2009)
13. Huet, G.: Sanskrit Segmentation. In: South Asian Languages Analysis Roundtable XXVIII, Denton, Ohio (October 2009)
14. Jha, G.N., Mishra, S.K.: Semantic Processing in P¯an. ini’s K¯araka System. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 239–252. Springer, Heidelberg (2009)
15. Kulkarni, A.P., Shukla, D.: Sanskrit Morphological Analyser: Some Issues. To appear in Bh.K Festschrift volume by LSI (2009)
16. Kulkarni, A.P., Kumar, A., Sheeba, V.: Sanskrit compound paraphrase generator. In: Proceedings of ICON 2009: 7th International Conference on Natural Language Processing. Macmillan Publishers, India (2009)
17. Mahavira: P¯adnini as Grammarian (With special reference to compound formation). Bharatiya Vidya Prakashan, Delhi (June 1978)
18. Mittal, V.: Automatic Sanskrit Segmentizer using Finite State Transducers. In: Proceeding of Association for Computational Linguistics - Student Research Workshop (2010)
19. Murty, M.S.: Sanskrit Compounds-A Philosophical Study. Chowkhamba Sanskrit Series Oﬃce, Varanasi, India (1974)
20. Ishvarachandra, P.: As.ta¯dhya¯y¯ı. Chaukhamba Sanskrit Pratisthan, Delhi (2004) 21. Prince, A., Smolensky, P.: Optimality Theory: Constraint Interaction in Generative
Grammar. In: RuCCS Technical Report 2 at Center for Cognitive Science, Rutgers University, Piscataway (1993)
22. Sarma, E.R.S.: Man. ikan. a: A Navya-Nya¯ya Manual. The Adyar Library and research Centre, Madras (1960)
23. Scharf, P.M.: Levels in P¯an. ini’s As.ta¯dhya¯y¯ı. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 66–77. Springer, Heidelberg (2009)
24. Yuret, D., Bi¸cici, E.: Modeling Morphologically Rich Languages Using Split Words and Unstructured Dependencies. In: ACL-IJCNLP, Singapore (2009)

---

<!-- page 80 -->

68

A. Kumar, V. Mittal, and A. Kulkarni

A Appendix-A : Sanskrit Compound Type and Sub-type Classiﬁcation

²ÝÝ Ú¸

Ñ­ ÖÝ¸

Compound sub-types

Tags Compound sub-types

Tags

²ÝÝ-Ô¡ Ú­Ô ¸

A1 Ú £Õ -Ô¡ Ú­Ô - Ñ­ ÖÝ¸

K1

²ÝÝ-Ù ÖÔ ¸

A2 Ú £Õ -Ù ÖÔ - Ñ­ ÖÝ¸

K2

Ø ¢Ø

A3 Ú £Õ -Ù ÝÔ - Ñ­ ÖÝ¸

K3

×ÀÝ Ô¡ Ú­Ô -Ò ÖÔ

A4 ÙÔÑ Ò-Ô¡ Ú­-Ô - Ñ­ ÖÝ¸

K4

Ò ÖÔ - ¦ÝÔ Ì£­ × Ý Ñ A5 ÙÔÑ Ò-Ù Ö-Ô - Ñ­ ÖÝ¸

K5

×ÀÝ Ô¡ Ú­Ô -Ú ÝÓ ÖÔ ¸ A6 Ú Ö Ô¡ Ú­Ô ¸- Ñ­ ÖÝ¸

K6

Ô £Ö - ÑÝ£ - Ô¡ Ú­Ô Õ · ÖÔ A7 ×Å ÚÒ Ô¡ Ú­Ô - Ñ­ ÖÝ¸

K7

ÑÝÑÔ ÐÓÔ - Ñ­ ÖÝ¸

Km

Ø´Ô ÞÕ¸
Compound sub-types
ÌÑ Ø´ÔÞÕ¸ âØ Ý Ø´ÔÞÕ¸ Ø¢ Ø Ý Ø´ÔÞÕ¸ ØÌ ­Ø´ÔÞÕ¸ Ô Ñ Ø´ÔÞÕ¸ Õ Ø´ÔÞÕ¸ × Ñ Ø´ÔÞÕ¸ Ò Ø´ÔÞÕ¸ ×Ñ Ö- â ¸ Ø Ø Ì­ â ¸ Ù ÖÔ â ¸ Ø×Ñ ×¸ ×Ñ ×¸
×Ñ ×¸ ÑÝ¡ Ö²Ý× ¸ Ø´ÔÞÕ¸ Ô ¸ Ø´ÔÞÕ¸ ÙÔÔ ¸

Ú¸

Tags Compound sub-types

Tags

T1

T2 âØ Ý Ì­- Ú ¸(×Ñ Ò Ö ¸) Bs2

T3 Ø¢ Ø Ý Ì­- Ú ¸(×Ñ Ò Ö ¸) Bs3

T4 ØÄÝ­Ì­- Ú ¸(×Ñ Ò Ö ¸) Bs4

T5 Ô ÅÝÌ­- Ú ¸(×Ñ Ò Ö ¸) Bs5

T6 Õ ·Ì­- Ú ¸(×Ñ Ò Ö ¸)

Bs6

T7 × ÅÝÌ­- Ú ¸(×Ñ Ò Ö ¸) Bs7

Tn Ú  - Ú ¸(×Ñ Ò Ö ¸) Bsd

Tds Ö ÚÕÝ - Ú ¸(×Ñ Ò Ö ¸) Bsp

Tdt ÚÕÝ - Ú ¸(×Ñ Ò Ö ¸) Bsg

Tdu ¹´ÝÌ­ - ÑÝÑÔ ÐÓÔ (Ò )- Ú ¸ Bsmn

Tg

-Ú¸

Bvp

Tk ×ÀÝÓ ÝÔ - Ú ¸(×Ñ Ò Ö ¸) Bss

Tp ÙÔÑ ÒÔ¡ Ú­Ô - Ú ¸(×Ñ Ò Ö ¸) Bsu

Tm ²Ý Ö - Ú ¸

Bv

Tb ×öÓ ÖÔ ¸ ²Ý Ö - Ú ¸

Bvs

U × Ô¡ Ú­Ô -²Ý Ö - Ú ¸

BvS

ÙÔÑ ÒÔ¡ Ú­Ô -²Ý Ö - Ú ¸ BvU

Ô ¸- Ú ¸

Bb

â¦â¸

£ÚÐ

Compound type:

Tags Compound type:

Tags

Ø£ÖØÖÝÓ -â¦â¸

Di £ÚÐ ×Ñ ×¸

S

×Ñ Ö-â¦â¸

Ds

âÞ ¸

£Õ

E âÞ ¸

d

---

<!-- page 81 -->

Sanskrit Compound Processor

69

A : Rules for Paraphrase Generation
²ÝÝ Ú¸
1 <x-y>A1 => y{6} f{x} where f maps x to the noun with same semantic content. A function f needs to be deﬁned.
2 <x-y>A2 => x{3} ÚÔÖ ØÑ Ú¢ Ñ 3 <x-y>A4 => x{6} y{6} ×Ñ Ö¸ 4 <x-y>A5 => x’{1} y{1} Ý ¹ÑÒ £ £
x’ has same gender as that of y’.
5 <x-y>A6 => x{6} y{6} ×Ñ Ö¸ if x = â, both x and y will be in âÚÒÑ
6 <x-y>A7 => x{6} y
Ø´ÔÞÕ¸
7 <x-y> T n => x{n} y 2 ≤ n ≤ 7 8 <x-y>Tn => x{n} y
9 <x-y>Tds => x{6;ba} y{6;ba} ×Ñ Ö¸
10 <x-y-z>Tb = x{1} y{1} z{1}
Ñ­ ÖÝ¸ 11 <x-y>K1 => x{1} ØØ y{1}  12 <x-y>K2 => x{1}  y{1}  13 <x-y>K3 => x{1}  ×Ç y{1}  14 <x-y>K4 => x{1} Ú y{1} 15 <x-y>K5 => x{1} y{1} Ú 16 <x-y>K6 => x{1} Ú y{1} 17 <x-y>K7 => x{1} Ø y{1}
Ú¸ 19 <x-y>Bsd => x{6}  y{6}  Ý ¦ØÖ ÐÑ 20 <x-y>Bsp => x{3}  y{3}  ´Ý Ñ Ý Ñ Ú¢ Ñ 21 <x-y>Bsg => x{7}-y{7}+ ¢ ´Ú Ñ Ý Ñ Ú¢ Ñ 22 <x-y>Bsmn => x’-y{1} Ý¹Ý 23 <x-y>Bss = > x{1} Ú y{1} Ý¹Ý 24 <x-y>Bsu => x{1} Ú y{1} Ý¹Ý ¸ 25 <x-y>Bv => x y{1} Ý¹Ý 26 <x-y>Bvs => y{6} x’ Ý£ × ¦Ø Ø£ 27 <x-y>BvS => y{3} × 28 <x-y>BvU => x{6} Ú y Ý¹Ý
â¦â¸ 29 <x-y>Di => x{1}  y{1}  30 <x-y>Ds => x{1}  y{1} 
31 <x-y>S => y{1} x{1} 32 <x-y>d => x y

---

<!-- page 82 -->

Designing a Constraint Based Parser for Sanskrit
Amba Kulkarni, Sheetal Pokar, and Devanand Shukl
Department of Sanskrit Studies, University of Hyderabad, Hyderabad
apksh@uohyd.ernet.in {sjpokar,dev.shukl}@gmail.com

Abstract. Verbal understanding (´s¯abdabodha) of any utterance requires the knowledge of how words in that utterance are related to each other. Such knowledge is usually available in the form of cognition of grammatical relations. Generative grammars describe how a language codes these relations. Thus the knowledge of what information various grammatical relations convey is available from the generation point of view and not the analysis point of view. In order to develop a parser based on any grammar one should then know precisely the semantic content of the grammatical relations expressed in a language string, the clues for extracting these relations and ﬁnally whether these relations are expressed explicitly or implicitly. Based on the design principles that emerge from this knowledge, we model the parser as ﬁnding a directed Tree, given a graph with nodes representing the words and edges representing the possible relations between them. Further, we also use the M¯ıma¯m. s¯a constraint of a¯k¯an˙ k.s¯a (expectancy) to rule out non-solutions and sannidhi (proximity) to prioritize the solutions. We have implemented a parser based on these principles and its performance was found to be satisfactory giving us a conﬁdence to extend its functionality to handle the complex sentences.1
Keywords: Sanskrit, Constraint Based Parser, Information coding, a¯k¯an˙ ks. ¯a, sannidhi.

1 Introduction

S´¯abdabodha is the understanding that arises from a linguistic utterance. The

three fer in

schools of the chief

S´a¯bdabodha viz. qualiﬁcand of the

VS´ya¯a¯bkdaarbaon. dah, aN.yNa¯yeaveartnhdelMes¯ısmta¯ombse¯agimn awinitlyh,daifl-l

these three schools need an analysis of an utterance. This analysis expresses the

relations between diﬀerent meaningful units involved in an utterance. The ut-

terance may be as small as a single word or as big as a complete novel. In what

follows, however, we take a sentence2 as a unit, and as such we discuss only the

relations of words within a sentence and do not deal with the discourse analysis.

1 Thanks to G´erard Huet and Peter Scharf for their valuable remarks.
2 Roughly ekatin˙ va¯kyam (va¯rttika on tv¯amau dvit¯ıya¯ya¯h. 8.1.23, halantapum. llin˙ gaprakaran. am).

G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 70–90, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 83 -->

Designing a Constraint Based Parser for Sanskrit

71

A generative grammar of any language provides rules for generation. For analysis, we require a mechanism by which we can use these rules in a reverse way. The reversal in some cases is easy and also deterministic. For example, subtraction is an inverse operation of addition and is deterministic. The reversal may not always be deterministic. Let us see a simple example of non-deterministic reversal with which all of us are familiar. The multiplication tables or simple method of repetitive addition provides a mechanical way for multiplication. Given a product, to ﬁnd its factors is a reverse process. Multiplication of two numbers, say, 4 and 3 produces a unique number 12. But its decomposition into two factors is not unique. 12 may be decomposed into two factors as either {6,2} or {4,3} in addition to a trivial decomposition {12,1}. Thus the inverse process may at times involve non-determinism. Depending upon the context, if one factor is known, the other factor gets ﬁxed. For example, if you are interested in distributing 12 apples among 2 children, then one of the factors being 2, the other factor, viz. 6, is determined uniquely.
This is true of a generative grammar as well. To give an example, look at the following two su¯tras of Pa¯n. ini.
– anabhihite (2.3.1) – kartr. karan. ayos tr.t¯ıya¯ (2.3.18)
These two su¯tras together, in case of a passive voice (karman. i prayogah.), assign third case3 to both the kart¯a as well as karan. am k¯araka as in
(1) ra¯men. a b¯an. ena v¯alih. hanyate.
Now, when a hearer (who knows Sanskrit grammar) listens to this utterance, he notices two words ending in the third case suﬃx and that the construction is in passive voice. But unless he knows that ra¯ma is the name of a person and ba¯n. a is used as an instrument, he fails to get the correct reading. In the absence of such an ‘extra-linguistic’ knowledge, there are two possible interpretations viz. either ra¯ma is kart¯a and ba¯n. a is karan. am, or ba¯n. a is kart¯a and ra¯ma is karan. am leading to a non-determinism.4
The process of analysing a sequence of words to determine the underlying grammatical structure with respect to a grammar is parsing. There are two distinct ways of developing a parser for a language. The ﬁrst method which has gained recent predominance is to use statistical machine learning techniques to learn from a manually annotated corpus. This requires a large human annotated corpus. Second method is to use the grammar rules of generation to ‘guess’ the possible solutions and apply constraints to rule out obvious non-solutions. There have been notable eﬀorts in developing parsers by both the statistical methods as well as grammar based methods for various languages (Lin,1998; Marneﬀe, 2006; Sleator,1993). A parser based on Paninian Grammar Formalism for modern
3 The word ‘case’ is used for vibhakti. 4 There are two more possibilities, since both have the same gender, number, and
vibhakti, one can be an adjective of the other.

---

<!-- page 84 -->

72

A. Kulkarni, S. Pokar, and D. Shukl

Fig. 1. Semantic relations
Indian languages is described in Bharati, et. al. (1995; 85-100). This parser is modeled as a bipartite graph matching problem. A statistical parser for analysing Sanskrit is described in Hellwig (2008). The shallow parser of Huet (2006, 2009) uses bare minimum information of transitivity of a verb as a sub-categorisation frame and models it as a graph-matching algorithm. The main purpose of this shallow parser is to ﬁlter out non-sensical interpretations. It is therefore natural for Huet to develop small tools such as ‘ca’ handler with more priority to rule out non-grammatical solutions (rather than to develop a full-ﬂedged parser).
While designing a grammar based parser, two major design issues5 one has to address are: a) what should be the level of semantic analysis, and b) which relations to represent in the parsed output. In order to decide on these issues, in what follows, we ﬁrst look at the Sanskrit grammar to see what kind of semantic relations can be extracted from a language string, precisely where is the information about these relations coded, and whether the extracted relations are from primary sources or secondary. Later we discuss the issues the mechanical processing throws up, and the possible ways to handle them. Based on these observations, we decide various design parameters. The next section discusses mathematical formulation of the problem, its implementation and ﬁnally its performance analysis.
2 Encoding of Grammatical Relations in Sanskrit
Parsing unfolds a linear string of words into a structure which shows explicitly the relations between words. For example, the parse of
(2) ra¯ja¯ vipr¯aya g¯am. dada¯ti.
may be described as in Figure 1. The task of a parser involves identifying various relations between the words.
So the parser developer should decide on the nature of relations and the means
5 The issues in the development of a statistical parser are totally diﬀerent. They are related to the size of the annotated corpus, the number of annotated tags used, their ﬁne-grained-ness, etc.

---

<!-- page 85 -->

Designing a Constraint Based Parser for Sanskrit

73

to identify the relations. Sanskrit has the unique privilege of having an extant grammar in the form of As.t.a¯dhya¯y¯ı. It has been demonstrated (Bharati, forthcoming) that P¯an. ini had given utmost importance to the information coding and the dynamics of information ﬂow in a language string. In what follows we look at the information coding in Sanskrit from the point of view of designing a parser.

2.1 Semantic Content of the Relations
Though the correspondence between the semantic relations and the k¯araka relations is duly stated in the grammar, what is encoded in words is only the ka¯raka relations. There is no one-to-one relation between thematic and k¯araka relations. One k¯araka relation may correspond to more than one thematic relation and one thematic relation may be realised by more than one ka¯raka relations (Kiparsky, 2009: 49). What can be extracted from a language string alone without using any extra-linguistic information are the syntactico-semantic relations or the ka¯raka relations and not the pure semantic relations. We give below some examples in our support.
Svatantrah. kart¯a. The v¯arttikas under Pa¯n. ini’s su¯tra k¯arake (1.4.23) go like this6
In the sentence devadattah. pacati, the activity of cooking refers to the activity of devadattah. viz. putting a vessel on the stove, pouring water in it, adding rice, supplying the fuel etc. and this activity refers to the activity of the pradh¯ana kart¯a. In the sentence stha¯l¯ı pacati, the cooking activity refers to holding the rice and water till the rice cooks and this activity is that of a vessel. In the sentence edha¯h. paks. yanti, the cooking activity refers to the supply of suﬃcient heat by a piece of ﬁrewood and thus refers to the activity of an instrument.
In real world, devadattah. , sth¯al¯ı and edh¯ah. are the agent, locus and the instrument respectively. But what is expressed by these language strings is just the kartr. tva of the pradha¯na kart¯a, adhikaran. am and karan. am respectively and NOT the agent, locus and instrument.
´ses.e. Similarly the relation between vr. ks.a and ´s¯akh¯a, pitr. and putra, and ra¯jan and purus. a in the phrases vr. k.sasya ´s¯akha¯, pituh. putrah. and ra¯jn˜ah. puru.sah. is marked by the genitive case suﬃx, and Pa¯n. ini groups all of them under the su¯tra ´sa.s.th¯ı ´ses. e (2.3.50). Semantically however the ﬁrst is avayava-avayav¯ıbh¯ava (part-whole-relation), the second one is janya-janaka-bh¯ava (parent-childrelation), and the third one is sva-sva¯mi-bha¯va (owner-possession-relation).
6 adhi´srayan. odaka¯secanatan. d. ula¯vapanaidho’pakar.san. akriya¯h. pradha¯nasya kartuh. p¯akah. ||(ma. bha¯. 1.4.23. v¯a 8) || dron. am. pacatya¯d. hakam. pacat¯ıti sam. bhavanakriy¯a dha¯ran. akriya¯ c¯adhikaran. asya p¯akah. ||(ma. bha¯. 1.4.23.v¯a 9 )|| edh¯ah. paks. yantya¯ viklitter jvalis.yant¯ıti jvalanakriya¯ karan. asya p¯akah. ||(ma. bha¯. 1.4.23.v¯a 10) ||.

---

<!-- page 86 -->

74

A. Kulkarni, S. Pokar, and D. Shukl

adhi´s¯ın˙ stha¯sa¯m. karma (1.4.46). In the sentences
(3) harih. vaikun. .tham adhi´sete. (4) munih. ´sila¯pa.t.tam adhitis..thati. (5) s¯adhuh. parvatam adhya¯ste.
vaikun. .tha, ´sila¯pa.t.ta and parvata are in the second case, and P¯an. ini assigns them a karma role. However, semantically, all of them are the loci of the activities of the associated verbs viz. adhi-´s¯ın˙ , adhi-sth¯a, and adhi-a¯s. Hence the naiy¯ayikas, who want to map the ‘world of words’ to the real world, ﬁnd it diﬃcult to accept the karmatva of these words and they qualify this karmatva on the second case ending as ¯adh¯arasya anu´s¯asanika-karmatva (Dash, 1991;141). Thus, there is a deviation between the real world and what is expressed through the words.
sahayukte’apradh¯ane (2.3.19). In the sentence,
(6) m¯atra¯ saha ba¯lakah. a¯gacchati.
the agreement of the verb is with b¯alakah. , and not with ma¯tar¯a. According to the su¯tra (2.3.19), ‘saha’ is used with the apradha¯na (sub-ordinate) k¯araka. Thus in this example, m¯at¯a is sub-ordinate and b¯alaka is the main kart¯a. However, at another level of semantic analysis, the situation is reversed. It is m¯at¯a who carries the child in her arms and thus ba¯laka is apradha¯na and m¯at¯a is the pradh¯ana k¯araka. Thus again there is a mismatch between the reality and what sentence actually codes in terms of grammatical relations.
From all the above examples, it is clear that the world of words (´sabda-jagat ) is diﬀerent from the real world. To match the extracted relations with the experience of the real world, extra-linguistic information is needed. Since the extra-linguistic information is not easily accessible, and is open ended, we would extract only syntactico-semantic relations that depend solely upon the linguistic/ grammatical information in a sentence.

2.2 Clues for Extracting the Relations
Sanskrit being inﬂectionally rich, we know that suﬃxes mark the relation between words. Similarly certain indeclinables mark some grammatical relations. Agreement between the words also indicate certain grammatical relations. We discuss below these cases with examples.
1. Abhihitatva The Paninian su¯tra ‘anabhihite’ (2.3.1) (if not already expressed) is an important su¯tra that governs the vibhakti assignment to the nominals. The v¯arttika7 on this su¯tra explains abhihita as the one which is expressed either by tin˙ (a ﬁnite verbal suﬃx), k.rt (a non-ﬁnite verbal suﬃx), taddhita (derivational nominal suﬃx) or sam¯asa (compound). E.g. in the sentence
7 tin˙ k.rttaddhitasama¯saih. parisam. khy¯anam (ma. bha¯. 2.3.1. v¯a.)

---

<!-- page 87 -->

Designing a Constraint Based Parser for Sanskrit

75

(7) ra¯mah. vanam. gacchati.
the verb being in the active voice (kartari prayogah. ), the verbal suﬃx ‘ti’ expresses the kart¯a, while in the following sentence in passive voice (karman.i prayogah. )
(8) ra¯men. a vanam. gamyate.
the karma is expressed by the verbal suﬃx. As such, in both cases, the one which is expressed (karta¯ and karma respectively) is in the nominative case and shows number and person agreement with the verb form. Some of the kr. t suﬃxes also express the k¯arakas. For example, in
(9) dh¯avan a´svah. .
the k.rt suﬃx in ‘dh¯avan’ expresses the relation of karta¯ (kartari kr. t (3.4.68)).
2. Vibhakti The verbal as well as nominal suﬃxes in Sanskrit are termed vibhaktis. We have already seen that verbal suﬃxes (tin˙ ), through abhihitatva, mark the relations between words. Now we consider the nominal suﬃxes. They fall under two categories. (a) vibhakti indicating a ka¯raka relation This marks a relation between a noun and a verb known as a ka¯raka relation. Sanskrit uses seven case suﬃxes to mark six ka¯raka relations viz. karta¯, karma, karan. am, samprada¯nam, ap¯ad¯anam and adhikaran. am. The genitive suﬃx, in addition to marking a k¯araka relation8, is predominantly used to mark the noun-noun relation. There is no one-to-one mapping between the case suﬃxes and the k¯araka relations, which makes it diﬃcult to determine the relation on the basis of vibhakti alone.

(b) upapada vibhakti In addition to the noun-noun relations expressed by the sixth case, there are certain words, most of them indeclinables called upapadas, which also mark a special kind of noun-noun relation. These indeclinables, mark a relation of a noun with an another noun, and in turn demand a special case suﬃx for the preceding noun. For example, the upapada ‘saha’ demands a third case suﬃx for the preceding noun as in

(10) ra¯men. a saha s¯ıt¯a vanam. gacchati.
3. Indeclinables (avyaya) The indeclinables mark various kinds of relations such as negation, adverbial (manner adverbs only), co-ordination, etc. Sometimes they also provide information about interrogation, emphasis, etc. We distinguish the upapadas from the avyayas, mainly because, though most of the upapadas are also
8 kart.rkarman. oh. kr. ti (2.3.65).

---

<!-- page 88 -->

76

A. Kulkarni, S. Pokar, and D. Shukl

indeclinables, they demand a special case suﬃx on the preceding word, whereas it is not so with indeclinables.

For example, the relation of ‘na’ with ‘gacchati’ in the sentence

(11) ra¯mah. gr. ham. na gacchati. is that of ‘negation (ni.sedha)’. Similarly, the relation of ‘mandam’ with ‘calati’ in the sentence

(12) ra¯mah. mandam. calati. is that of ‘adverbial (kriya¯vi´se.san. a)’. The relation of ‘eva’ with ‘ra¯ma’ in the sentence

(13) ra¯mah. eva tatra upavi.s.tati. is that of ‘emphasis (avadh¯aran. a)’.
4. Sam¯an¯adhikaran. a Agreement in gender, number and case suﬃx marks sama¯n¯adhikaran. a (having the same locus), or the modiﬁer-modiﬁed relation between two nouns as in

(14) ´svetah. a´svah. dh¯avati. (15) a´svah. ´svetah. asti. In (14) as well as (15), the words a´svah. and ´svetah. have the same gender, number and vibhakti indicating sama¯n¯adhikaran. a. However, there is a slight diﬀerence between the information being conveyed. In (15), the word ´svetah. is a predicative adjective (vidheya vi´se.san. a), while in (14) it is an attributive adjective.

2.3 Explicit versus Implicit Relations
Relations need not always be encoded directly through suﬃxes or morphemes. Sometimes the information is coded in the ‘Language Convention’. The su¯tra
sama¯nakartr. kayoh. pu¯rvaka¯le (3.4.21)
states that the suﬃx ktv¯a is used to denote the preceding of two actions that share the same karta¯. Then the question is what relation does ktv¯a suﬃx mark? - the relation of kart.rtva or the relation of pu¯rvaka¯l¯ınatva? or both?
Bhartr.hari in va¯kyapad¯ıyam states (3.7.81-82),

---

<!-- page 89 -->

Designing a Constraint Based Parser for Sanskrit

77

pradh¯anetayoryatra dravyasya kriyayoh. p.rthak ´saktirgun. ¯a.sray¯a tatra pradha¯namanurudhyate 3.7.81 pradh¯anavis. ay¯a ´saktih. pratyayen¯abhidh¯ıyate yad¯a gun. e tad¯a tadvad anukta¯pi prak¯a´sate. 3.7.82

i.e., in case X is an argument of both the main verb as well as the subordinate verb, it is the main verb which assigns the case and the relation of X to the sub-ordinate verb gets manifested even without any other marking.
From the sentences
(16) ra¯mah. dugdham. p¯ıtva¯ ´s¯al¯am gacchati. (17) ra¯men. a dugdham. p¯ıtva¯ ´s¯ala¯ gamyate.
it is clear that the vibhakti of ra¯ma is governed by the main verb gam. And hence, the information that ra¯ma is also the kart¯a of the verb p¯a is not expressed through any of the suﬃxes. The ktv¯a suﬃx expresses only the precedence relation (pu¯rvaka¯l¯ınatva).
Similarly the su¯tra
sam¯anakartr. ke.su (iccha¯rthes. u) tumun (3.3.158)
states that in case of verbs expressing desire, the inﬁnitive verb in the subordinate clause will have the same kart¯a as that of the verb it modiﬁes. Here also the primary information available from the non-ﬁnite verbal suﬃx tumun is the relation of purpose.9
The sharing in case of ktv¯a and tumun suﬃxes is the result of the preconditions sam¯anakartr. kayoh. or sam¯anakartr. ke.su in 3.4.21 and 3.3.158 respectively which act as Language Conventions.
3 Factors Useful for S´a¯bdabodha
As mentioned above, the generation problem is a direct problem, and the analysis problem is a reverse problem, and is non-deterministic. This problem was well recognised by the m¯ıma¯m. sakas who proposed four conditions viz. ¯ak¯an˙ ks. a¯ (expectancy), yogyata¯ (mutual compatibility), sannidhi (proximity) and t¯atparya (intention of the speaker) as necessary conditions for proper verbal cognition. With the help of examples, we explain below, how the ﬁrst three factors play an important role in the rejection of non-solutions from among the several possibilities. We have not discussed the importance of the fourth factor, since the kind of analysis it involves is out of the scope of the present discussion. 9 tumunn. vulau kriy¯aya¯m kriya¯rthy¯aya¯m (3.3.10).

---

<!-- page 90 -->

78

A. Kulkarni, S. Pokar, and D. Shukl

3.1 A¯ka¯n˙ ks. a¯ (Expectancy) In the sentence, (18) ra¯mah. vanam. gacchati.
each of the 3 words in this sentence has multiple morphological analyses. r¯amah. = ra¯ma {gender=m, case=1, number=sg},
= ra¯10 {lak¯ara=lat., person=1, number=pl, voice=active, parasmaipad¯ı}.

vanam. = vana {gender=n, case=1, number=sg}, = vana {gender=n ,case=2, number=sg}.

gacchati = gam {lak¯ara=lat., person=3, number=sg, voice=active, parasmaipad¯ı},
= gacchat (gam ´satr.) {gender=m, case=1, number=sg}, = gacchat (gam ´satr.) {gender=n, case=1, number=sg}.
This may lead to the following two possible sentential analysis: – ra¯ma = karta¯ of the action indicated by gam, vana = karma of the action indicated by gam.

– vana = karma of the action indicated by ra¯, gacchati = simultaneity of the actions indicated by ra¯ and gam, vayam = kart¯a of the action indicated by the verb ra¯ (not expressed explicitly, but through the verbal suﬃx).11
Of these two analyses, the second analysis can be ruled out on the basis of non-fulﬁlment of kart¯a and karma expectancies of the verb gam, and the samprad¯anam expectancy of the verb ra¯. The ﬁrst analysis being complete in itself, it is preferred over the second one.

3.2 Yogyata¯ (Compatibility) Consider the sentence, (19) ´saka.tam. vanam. gacchati.
The possible morphological analyses of each of the three words are given below. ´sakat.am = ´sakat.a {gender=n, case=1, number=sg},
= ´sakat.a {gender=n, case=2, number=sg}.
vanam. = vana {gender=n, case=1, number=sg}, = vana {gender=n, case=2, number=sg}.

10 ra¯ in the sense of da¯ne from the second (ada¯di ) gan. ah. . 11 The sentence is interpreted as - (tasmin) gacchati (sati), vayam. vanam. ra¯mah.
As (he) goes, let us give the forest (to somebody).

---

<!-- page 91 -->

Designing a Constraint Based Parser for Sanskrit

79

gacchati = gam {person=3, laka¯ra=lat., number=eka, voice=active, parasmaipad¯ı},
= gacchat (gam+´satr.) {gender=m, case=1, number=sg}, = gacchat (gam+´satr.) {gender=n, case=1, number=sg}.
Now, more than one word can’t have the same k¯araka role unless it is already expressed (abhihita). This leads to the following possible sentential analyses12:
– ´saka.ta = karta¯ of the action indicated by gam, vana = karma of the action indicated by gam.
– vana = karta¯ of the action indicated by gam, ´saka.ta = karma of action indicated by gam.
– vana = karta¯ of the action indicated by gam, ´saka.ta = modiﬁer of vana.
– vana = karma of the action indicated by gam, ´saka.ta = modiﬁer of vana.
Out of these, the last two do not fulﬁl all the mandatory expectancies of a verb. Among the ﬁrst two, the ﬁrst one is preferable over the second one, since ´saka.ta has an ability to move while vana can not move. Hence ´saka.ta is preferable as a kart¯a of the verb gam than vana. Thus the yogyata¯ or the competency of the nouns to be eligible candidates for the ka¯raka roles plays an important role here. However, the context may overrule the condition of yogyata¯. It is possible to have a reading where, all the residents of vana are going to see the new ´saka.ta, and thus vana qualiﬁes to be a kart¯a. The yogyat¯a and the context thus compete with each other and hence one needs discourse analysis to prune some of the possibilities.

3.3 Sannidhi (Proximity)
Consider, (20) ra¯mah. dugdham p¯ıtva¯ ´s¯al¯am gacchati.
Here the possible analyses are:
– ra¯ma = kart¯a of gam, dugdha = karma of pa¯, ´s¯al¯am = karma of gam, p¯a = preceding action with respect to gam.
– ra¯ma = kart¯a of gam, dugdha = karma of gam, ´s¯al¯am = karma of p¯a, p¯a = preceding action with respect to gam.
12 Assuming that the modiﬁer is to the left, which need not be true in case of poetry.

---

<!-- page 92 -->

80

A. Kulkarni, S. Pokar, and D. Shukl

A competent speaker rules out the second solution on account of noncompatibility of the arguments viz. dugdha and ´sa¯la¯ do not have semantic competence to be the karma of gam and p¯a respectively.
The arguments in the correct solution are closer. We mark the words by their positions, and deﬁne the proximity measure of a relation as the distance between its two arguments, and the proximity measure of a solution as the sum of the proximity measures of the various relations in the parse. The proximity measure of the above two parses is
– ra¯ma = karta¯ of gam (dist = position of gam - position of ra¯ma = 5 -1 = 4) dugdha = karma of p¯a (dist = 3-2 = 1) ´sa¯la¯m = karma of gam (dist = 5-4 = 1) p¯a = preceding action with respect to gam (dist = 5-3 = 2) Thus the total distance = 4 + 1 + 1 + 2 = 8
– ra¯ma = karta¯ of gam (dist = 5-1 = 4) dugdha = karma of gam (dist = 5-2 = 3) ´sa¯la¯m = karma of p¯a (dist = 4-3 = 1) p¯a = preceding action with respect to gam (dist = 5-3 = 2) Thus the total distance = 4 + 3 + 1 + 2 = 10
The one with greater proximity (or smaller distance) is preferred as a solution. Though Sanskrit is a free-word-order language, the following sentence with exchange of the karmas is not acceptable.

(21) *ra¯mah. ´sa¯la¯m p¯ıtva¯ dugdham. gacchati. Equally unacceptable prose orders are

(22) *ra¯mah. p¯ıtva¯ ´sa¯la¯m dugdham. gacchati. (23) *ra¯mah. dugdham ´sa¯la¯m p¯ıtva¯ gacchati.
which involve crossing of links expressing the relations. A small pilot study of anvaya of Sam. ks.epa R¯am¯ayan. a (Kutumbashastri, 2002) sentences show no evidence of crossing of links.
It is worth exploring the Calder mobile model suggested by Staal (1967) and further worked out by Gillon (1993) in the light of the m¯ıma¯m. sa¯ principle of sannidhi. It may result in a better computational criterion for sannidhi.

4 Design Principles
The foregoing discussions lead to the following design principles for the constraint-based parser.
1. The relations will be marked as k¯araka relations. [Using these k¯araka relations and extra-linguistic knowledge, the seman-
tic analysis may be carried out in the next level of processing.]

---

<!-- page 93 -->

Designing a Constraint Based Parser for Sanskrit

81

2. Only those relations that are marked directly by the morphemes will be extracted. [No relations that require some post-processing, or are based on secondary information will be extracted in the ﬁrst step. The next level of processing will use this information to mark the unspeciﬁed or shared relations, if any.]
3. To prioritize the solutions, only the conditions of ¯ak¯an˙ ks. a¯ and sannidhi will be used. [The condition of yogyata¯ will be used as and when the information is available in machine usable form, with the understanding that this knowledge may not be relied on completely.]
4. While dealing with prose, it will be assumed that there is no cross-linking of the relations between the words.

5 Mathematical Model
Let each word in a sentence be represented as a node in a graph, and the nodes be connected by the directed labelled edges. Then the problem of parsing a sentence may be modelled as
Given a Graph G with n nodes, the task is to ﬁnd a sub-graph T which is a directed Tree.13
Assuming that the words can be partitioned into two classes viz. the words which have an expectancy called demand words and the words which satisfy the demand called source words, Bharati et. al. reduced the parsing problem to matching a bipartite graph (Bharati 1995: 96). But in reality, the words can not be partitioned into two classes. We come across words which can be demand words in some context and source words in some other context, or in the same context a kr. danta (primary derivative), e.g. can be both a demand word as well as a source word. Bharati et. al. (1995: 91) also needed the requirement of k¯arakas and their optionality for each verb. But then, a parser based on such information will fail to parse sentences with ellipsis, or the real corpus where we come across sentences with incomplete information.
With a robust parser, that produces at least partial solution in case of ellipsis, as an aim, we relax the above conditions. So we give away the constraint that a word can be exclusively either a demand or a source word. Further we treat all k¯arakas at the same level, irrespective of whether they are mandatory or optional, and assign penalty to lower the priority of those solutions which do not satisfy the mandatory expectancies. We divide the problem into three parts:
1. For a given sentence, draw all possible labeled directed edges among the nodes.
13 A tree is a graph in which any two vertices are connected by exactly one simple path.

---

<!-- page 94 -->

82

A. Kulkarni, S. Pokar, and D. Shukl

2. Identify a sub-graph T of G such that T is a directed Tree which satisﬁes the given constraints.
3. Prioritize the solutions, in case there is more than one possible directed Tree.

In what follows we describe our model. A matrix is a convenient way of representing the graphs for computing pur-
pose. In our case, each word represents a node of a graph, and with each pair of nodes is associated zero or more labels, indicating the possible relations between these nodes. The strong constraint on these relations is that there can be at the most one label associated with a pair of nodes. This then naturally suggests a 3D matrix representation, whose elements are either 0 or 1, where the 3 dimensions represent two nodes and a relation label. The task of the parser is to prune out all those relations which do not satisfy the given constraints, and ﬁnally rank them based on their weights. Further, each word has one or more morphological analyses. Hence, corresponding to each node there exists a record with one or more cells, each cell representing one morphological analysis of the word. Let the jth analysis of the ith node be represented by [i, j]. Thus the address of a typical element of the 3D matrix is ([i, j], R, [l, m]). The ﬁrst pair of letters i and j correspond to the source word analysis, while the second pair of letters l and m represent the demand word analysis. R is the name of the relation of the lth word to the ith word. j indicates the morphological analysis of the ith word responsible for this relation, and m indicates the morphological analysis of the lth word that triggers this relation. In short the tuple ([i, j], R, [l, m]) represents a relation R due to the mth morphological analysis of the lth word to ith word due to its jth morphological analysis. For ease of representation, we represent the tuple as (i, j, R, l, m). Thus, the initial graph with all possible relations between various nodes is represented as 5D matrix C such that
C[i, j, R, l, m] = 1, if such a relation exists,
= 0, otherwise.

Task 1. Based on the available information in a given sentence in the form of abhihitatva, vibhakti, sa¯ma¯n¯adhikaran. ya, and the expectancies the matrix C is populated with 0s and 1s.
Here are sample rules (just enough to illustrate an example), expressed in English.
Rule 1: If the sentence has
a noun(say ‘s’) in prathama¯ vibhkati, a verb(say ‘t’) in kartari prayogah., in 3rd person, and ‘s’ and ‘t’ agree in number, then ‘s’ is possibly a karta¯ of ‘t’.

---

<!-- page 95 -->

Designing a Constraint Based Parser for Sanskrit

83

Rule 2: If the sentence has
a noun(say ‘s’) in dvit¯ıya¯ vibhkati, a verb(say ‘t’) in kartari prayogah., and is sakarmaka (roughly transitive) then ‘s’ is possibly a karma of ‘t’.

Rule 3: If the sentence has
a noun(say ‘s’) in saptam¯ı vibhkati, and a verb(say ‘t’), then ‘s’ is possibly an adhikaran. a of ‘t’.
Now consider the sentence (24) ra¯mah. vanam. gacchati.
The analyses of various words are numbered as follows: [1, 1]: ra¯ma {gender=m, case=1, number=sg}, [1, 2]: ra¯ {gan. ah. =ad¯adi, laka¯ra=lat., person=1, number=pl, prayogah. =kartari, parasmaipad¯ı}.

[2, 1]: vana {gender=n, case=1, number=sg}, [2, 2]: vana {gender=n ,case=2, number=sg}.
[3, 1]: gam {laka¯ra=lat., person=3, number=sg, voice=active, parasmaipad¯ı}, [3, 2]: gacchat (gam ´satr.) {gender=m, case=1, number=sg}, [3, 3]: gacchat (gam ´satr.) {gender=n, case=1, number=sg}.
The above 3 rules with this input then produce the following output showing all possible relations between various analses:
[2, 2] is a possible karma of [3, 2] [2, 2] is a possible karma of [3, 3] [2, 2] is a possible karma of [1, 2] [2, 2] is a possible karma of [3, 1] [2, 1] is a possible karta¯ of [3, 1] [1, 1] is a possible karta¯ of [3, 1]

The resulting graph is shown in Figure 2.
Task 2. In order to get a Tree from this graph, we impose the following constraints.
1. A morpheme(vibhakti) marks only one relation. I.e., a node can have one and only one incoming arrow. j,R,k,l C[i, j, R, k, l] = 1, ∀ i.

---

<!-- page 96 -->

84

A. Kulkarni, S. Pokar, and D. Shukl

Fig. 2. Graph showing all possible relations
2. Each ka¯raka relation is marked by a single morpheme. There can not be more than one outgoing arrow with the same label from the same cell, if the relation marks a ka¯raka relation,14 i.e. there can not be two words satisfying the same ka¯raka role of the same verb.
i,j C[i, j, R, k, l] = 1, for each tuple (R, k, l).
3. A morpheme does not mark a relation to itself. A word can’t satisfy its own expectancy. i.e. a word can’t be linked to itself15. Or there can not be self loops in a graph.
j,R,k C[i, j, R, i, k] = 0, ∀i.
4. Only one valid analysis of every word per solution (a) If a word has both an incoming arrow as well as an outgoing arrow, they should be through the same cell.
∀i∀j R,l,n C[i, j, R, l, n] + a,b,R,k!=j C[a, b, R, i, k] ≤ 1.
(b) If there is more than one outgoing arrow through a node, then it should be through the same cell. if, for some i,j,R,l,m C[i,j,R,l,m] = 1,
then ∀a∀b∀R a,b,R,k!=j C[a, b, R, l, k] = 0. 5. All the words in a sentence should be connected.16
14 adhikaran. am is treated as an exception since one can have more than one adhikaran. am as in ra¯mah. adya pan˜ca va¯dane gr. ham agacchat.
15 In case of some of the taddhita suﬃxes which are in sva¯rtha, there will be self loops. But we do not consider the meaning of taddhita suﬃxes in the ﬁrst step, and thus can avoid the self loops.
16 This condition is not yet implemented.

---

<!-- page 97 -->

Designing a Constraint Based Parser for Sanskrit

85

6. There are no crossing of links If all the nodes are plotted in a straight line, then they should not intersect each other. i.e.,
if C[i, j, R, k, l] = 1, then ∀v∀yC[u, v, w, x, y] = 0, if i < x < k and u < i or u > k.
The resultant graph is a Tree provided:
1. It is connected17. 2. It has n-1 edges.
The fact that only sup / tin˙ suﬃx in every word marks a relation with some other word in a sentence, and abhihita ka¯raka is not expressed by any sup suﬃx, it is guaranteed that there are exactly n-1 edges.

Task 3. The solutions are prioritized using the conditions speciﬁed below. For each of the solutions, the cost is calculated as Cost = i,R,j ciRj , where
i) ciRj = |j − i| ∗ wtR, if C[i, a, R, j, b] = 1 for some a and b. = 0 otherwise.
ii) wtR = rank(R), if R is a k¯araka relation (appendix I shows the ranking) = 100, otherwise.
This cost ensures the following:
1. ¯ak¯an˙ ks. a¯ (ka¯raka relation) is preferred over other relations (rank18 of the relations takes care of this.).
2. The ranking of the solutions on the basis of distance-based weights takes care of sannidhih. .

6 Implementation
The ﬁrst task demands the inputs from grammar, whereas the second and the third tasks are purely mathematical ones, which can be handled by a constraint solver. The separation of tasks into three sub-tasks makes it not only modular, but also easy for a grammarian to test his/her rules independently. For the ﬁrst task, an expert shell CLIPS is being used, whereas for the second task, a constraint solver MINION is being used. The system is available at
http://sanskrit.uohyd.ernet.in/~anusaaraka/sanskrit/MT/test_skt.html
There is no speciﬁc reason behind using these special software tools except the familiarity and the availability under the General Public License. No special eﬀorts were put in towards the eﬃciency of the system since the main purpose of this exercise is to have a proof of the concept.
17 Since, this condition is not yet implemented, the resulting graph need not be a Tree. 18 Better ranking scheme needs to be developed to take care of default word order.

---

<!-- page 98 -->

86

A. Kulkarni, S. Pokar, and D. Shukl

7 Performance
The current system allows only padaccheda-sahita-eka-tin˙ -gadya-va¯kyam. To measure the performance of this parser, we used hand tagged data. Around 110 sentences with single ﬁnite verb were selected from a school book (see appendix A for a sample). These sentences were tagged manually showing the relation of each word in the context. The sentences being simple, each sentence had a single possible parse in the context. There were 525 token words. The average length of the sentences was approximately 5, with a maximum length of 14 words. Morphological analyser is a pre-requisite for a parser. In order to avoid the cascading eﬀect of errors due to non-availability of the morphological analysis, before running the parser, we ensured that the correct morphological analysis of all the words is being produced. Thus, given all possible correct analyses of the words, the task of the parser was to come up with a correct parse. Though the parser produces multiple parses, for the evaluation purpose, we chose only the ﬁrst parse. Among the 113 sentences, 97 (86%) sentences had the ﬁrst parse correct and 16 (14%) sentences had one relation wrong. Out of these 16, 10 relations had wrong label, 3 had wrong attachments and 3 went wrong in both the label as well as attachments.
The analysis of wrong results showed that most of the wrong relations were due to non-availability of appropriate knowledge to make the ﬁne-grained distinction. For example, manually tagged corpus makes a distinction between ka¯la-adhikaran. a and de´sa-adhikaran. a, gaun. a and mukhya karma in case of dvi-karmaka (di-transitive) verbs, hetu and karan. am, to name a few. Another cause of ambiguity was the verbs in the cur¯adi (10th) gan. a. For most of the verbs in this class, the causative and non-causative forms are the same. This then leads to a wrong parse, since we also allow elipsis. In case there are n (> 1) adjectives, there can be more than one possible way these adjectives can group with the following noun. But we produce a single parse where the adjectives are linked as a chain with the rightmost adjective qualifying the noun directly. This chain just indicates a chunk, and the internal grouping of these adjectives and also their relation with the head noun is left to the user for interpretation.

A sample output of a sentence

b¯alyaka¯le ra¯mah. da´sarathasya a¯jn˜aya¯ vi´sva¯mitrasya yajn˜am ra¯ks. asebhyah. rak.situm vanam agacchat.
is produced in Figure 3.

8 Challenges
The result with limited test cases is encouraging. The real corpus, even with small children’s stories involves much more complex constructions, not necessarily conﬁning to ‘eka tin˙ v¯akyam’. The constructions involve co-ordination between two or more verbs, sentence connectives such as ‘yad¯a-tad¯a, yatha¯-tath¯a,

---

<!-- page 99 -->

Designing a Constraint Based Parser for Sanskrit

87

Fig. 3. Sample parse output
atha, tasma¯t,’ etc. Thus, even at the level of simple texts, one can not do away with discourse analysis.
Another important problem that needs to be addressed is to handle a little more semantics than can be handled with syntactico-semantic relations. For example, it would be desirable to distinguish between hetu and karan. a at least, though not between mukhya karma and gaun. a karma.
Third problem is regarding the upapadas. Upapada acts more like a function word (dyotaka) than a content word (va¯caka). So in case of upapadas, it would be desirable to group the upapada together with the content word in the vibhakti it demands and then mark its relation with other content word. Thus e.g. in the sentence ra¯mah. munina¯ saha vanam. agacchat, it is desirable to parse it as in ﬁgure 4 than as in ﬁgure 5. This means an upapada should be treated as a function word, and as such should not be represented by a node.
The vibhaktis, as we know, denote more than one meaning. For example, the second case suﬃx denotes the meaning of kriya¯vi´se.san. a (manner), k¯ala (time) or adhvan (path) in addition to the karma. To decide an appropriate role, now what one requires is the knowledge of yogyata¯. In other words, our e-dictionaries should be rich with semantic properties of the words such as whether it denotes time, path or the manner, etc.
Since the parser does the analysis ‘mechanically’, it detects the problems of ‘violation’ of the rules more easily. We give just one example (more examples can be found in Gillon, 2002) from the anvaya of ‘Sam. ks.epa R¯am¯ayan. am’.
guhena lak.sman. ena s¯ıtaya¯ ca sahitah. ra¯mah. vanena vanam. gatv¯a bahu¯daka¯h. nad¯ıh. t¯ırtva¯ bharadv¯ajasya ´sa¯san¯at citraku¯.tam anupra¯pya vane ramyam ¯avasatham. kr. tv¯a devagandharvasan´k¯a´sa¯h. te trayah. ramama¯n. a¯h. sukham. nyavasan. (S´loka 30-32)

---

<!-- page 100 -->

88

A. Kulkarni, S. Pokar, and D. Shukl

Fig. 4. Saha-function

Fig. 5. Saha-content

This sentence poses the following problems:
a) Whom does the phrase ‘te trayah. ’ refer to? b) ra¯mah. does not agree with the ﬁnite verb nyavasan. Is it not a violation of
sama¯nakartr. kayoh. pu¯rvaka¯le? c) Does gatv¯a precede t¯ırtva¯ or nyavasan? d) In case of vanena vanam. what should be the meaning of the third case?
In spite of these problems, this parser can act as a tool to discover various kinds of semantic knowledge necessary to build a semantic parser.
Acknowledgement
This work is a part of the Sanskrit Consortium project entitled ‘Development of Sanskrit computational tools and Sanskrit-Hindi Machine Translation system’ sponsored by the Government of India.
References
1. Bharati, A., Sangal, R.: A Karaka Based Approach to Parsing of Indian Languages. In: COLING 1990: Proc. of Int. Conf. on Computational Linguistics, Helsinki, vol. 3. ACL, NY (August 1990)
2. Bharati, A., Chaitanya, V., Sangal, R.: NLP A Paninian Perspective. Prentice Hall of India, Delhi (1994)
3. Cardona, G.: P¯an. ini and P¯an. in¯ıyas on ´ses.a Relations. Kunjunni Raja Academy of Indological Research, Kochi (2007)

---

<!-- page 101 -->

Designing a Constraint Based Parser for Sanskrit

89

4. Dash, A.: The syntactic role of adhi in the P¯aninian k¯araka system. In: Deshpande,
M.M., Bhate, S. (eds.) Paninian Studies Prof. S. D. Joshi Felicitation Volume,
Center for South and Southeast Asian Studies, University of Michigan, U.S.A.
(1991) 5. Gent, I.P., Jeﬀerson, C., Miguel, I.: MINION: A Fast, Scalable, Constraint Solver.
In: The European Conference on Artiﬁcial Intelligence 2006, ECAI 2006 (2006) 6. Gillon, B.S.: Word Order in Classical Sanskrit. Indian Linguistics 57(1), 1–35
(1996) 7. Gillon, B.S.: Bhartr.hari’s rule for unexpressed k¯arakas: The problem of control in
Classical Sanskrit. In: Deshpande, H. (ed.) Indian Linguistic Studies, Festschrift in
Honor of George Cardona, Motilal Banarasidass, Delhi (2002) 8. Hellwig, O.: Extracting Dependency Trees from the Sanskrit Texts. In: Huet, G.,
Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics Symposium.
Springer, Heidelberg (2009) 9. Huet, G.: Formal Structure of Sanskrit Text: Requirements Analysis for a Mechan-
ical Sanskrit Processor. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Com-
putational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 162–199. Springer,
Heidelberg (2009) 10. Huet, G.: Shallow syntax analysis in Sanskrit guided by semantic nets constraints.
In: Majumder, Mitra, Parui (eds.) Proceedings of International Workshop on Re-
search Issues in Digital Libraries, ACM Digital Library (December 2006) 11. Jigyasu, B.: Ashtadhyayi (Bhashya) Prathamavrtti, Three volumes. Ramlal
Kapoor Trust Bahalgadh, Sonepat, Haryana (1979) (in Hindi) 12. Joshi, S.D. (ed.): Patanjali’s Vyakarana Mahabhashya(several volumes). Univ. of
Poona, Pune (1968) 13. Joshi, S.D., Roodebergen, J.A.F.: The A´st.¯adhya¯y¯ıof P¯an. ini (several volumes).
Sahitya Akademi, Delhi (1998) 14. Kiparsky, P.: On the Architecture of Panini’s Grammar. In: Huet, G., Kulkarni,
A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI),
vol. 5402, pp. 33–94. Springer, Heidelberg (2009) 15. Kutumbashastri, V.: Sam. ks.epa Ram¯ayan. am. Teach Yourself Samskrit Series.
Rashtriya Sanskrit Samsthanam, New Delhi (2002) 16. Lin, D.: Dependency-based evaluation of MINIPAR. In: Workshop on the evalua-
tion of Parsing Systems, Granada, Spain (1998) 17. Marneﬀe, M., MacCartney, B., Manning, C.D.: Generating Typed Dependency
Parses from Phrase Structure Parses. The Fifth International Conference on Lan-
guage Resources and Evaluation, LREC 2006, Italy (2006) 18. Pande, G.D.: Vaiy¯akaran. a Siddh¯antakaumud¯ı of Bhattojidikshita (Text only),
Reprint Edition. Chowkhamba Vidyabhavan, Varanasi (2000) 19. Ramakrishnamacharyulu, K.V.: Annotating Sanskrit Texts based on S´¯abdabodha
systems. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Lin-
guistics 2007/2008. LNCS (LNAI), vol. 5402, Springer, Heidelberg (2009) 20. Ramanujatatacharya, N.S.: S´¯abdabodha M¯ım¯am. s¯a. Institute Francis De
Pondicherry (2005) 21. Sharma, R.: V¯akyapad¯ıyam, Part III With commentary Prak¯a´sa by Helaraja and
Ambakartri. Varanaseya Sanskrit Visvavidyalaya, Varanasi (1974) 22. SK: Siddh¯antakaumud¯ı See Pande 23. Staal, J.F.: Word Order in Sanskrit and Universal Grammar. In: Foundations of
Language. Supplementary Series, vol. 5. Reidal, Dordercht (1967) 24. Sleator, D.D., Temperley, D.: Parsing English with a link grammar. In: Third
international Workshop on Parsing Technologies (1993)

---

<!-- page 102 -->

90

A. Kulkarni, S. Pokar, and D. Shukl

A Sample Story

nady¯ah. tat.e ekah. vr.ks.ah. asti| vr.ks.asya sam¯ıpam ek¯a ´sil¯a asti| vr.ks.asya ´s¯akha¯su n¯ıd. a¯h. santi| n¯ıd. es.u vihaga¯h. vasanti| n¯ıd. a¯h. vihaga¯n raks.anti| vr.ks.asya adhah. va¯nar¯ah. santi| kapayah. gr.ham na racayanti| te sarvada¯ itastatah. bhramanti| ekasmin divase ´s¯ıtam ta¯n p¯ıd. ayati| te ´s¯ıta¯t tr¯an. a¯ya agnim icchanti| kutra¯pi te agnim na vindanti| ekah. gun˜ja¯y¯ah. phala¯ni pa´syati| gun˜ja¯ya¯h. phala¯ni rakt¯ani santi| sah. agneh. sadr.´sa¯ni gun˜ja¯ya¯h. phala¯ni a¯nayati| t¯ani gun˜ja¯ya¯h. phala¯ni ´sil¯aya¯m sam. harati| te sarve gun˜ja¯-phalam paritah. upavi´santi| agneh. icchaya¯ te mukhaih. ta¯ni dhamanti| te agnim na vindanti| te v¯anara¯h. anala¯ya vr.th¯a ¯aya¯sam kurvanti| tes.¯am ´s¯ıtam na na´syati| kapayah. mu¯rka¯h. santi|

B Relations
The relations used, along with their ranks are given in Table 1.

Table 1. Relations

(0)

upapada vibhakti

(12) ka¯la-adhikaran. am.

(1)

kart¯a

(13) vis.aya-adhikaran. am.

(2)

prayojaka karta¯

(14) kart¯a-sama¯na¯dhikaran. am.

(3)

prayojya karta¯

(15)

vi´ses.an. am.

(4)

karma

(16) kriya¯-vi´ses˙an. am.

(5) reserverd for gaun. akarma (17)

ta¯darthya

(6) reserverd for mukhyakarma (18)

pu¯rvak¯al¯ına

(7)

karan. am.

(19)

(8)

samprad¯anam.

(20)

(9)

apa¯da¯nam.

(21)

(10)

adhikaran. am.

(22)

(11) de´sa-adhikaran. am.

sambandha
ka¯raka s.as.t.h¯ı nis. edha
sambodhana

---

<!-- page 103 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)
Rajesh Tavva and Navjyoti Singh
Center for Exact Humanities, International Institute of Information Technology,
Gachi Bowli, Hyderabad, India vrktavva@research.iiit.ac.in, navjyoti@iiit.ac.in
Abstract. NLP applications for Sanskrit so far work within computational paradigm of string grammars. However, to compute ‘meanings’, as in traditional ´sa¯bdabodha prakriya¯-s, there is a need to develop suitable graph grammars. Ontological structures are fundamentally graphs. We work within the formal framework of Neo-Vai´ses.ika Formal Ontology (NVFO) to propose a generative graph grammar. The proposed formal grammar only produces well-formed graphs that can be readily interpreted in accordance with Vai´ses. ika Ontology. We show that graphs not permitted by Vai´ses. ika ontology are not generated by the proposed grammar. Further, we write Interpreter of these graphical structures. This creates computational environment which can be deployed for writing computational applications of Vai´ses. ika ontology. We illustrate how this environment can be used to create applications like computing ´sa¯bdabodha of sentences.
Keywords: Formal Ontology, Vai´ses. ika, Punctuator, NVFO, ´sa¯bdabodha, Graph Grammar, Generative Grammar.
1 Introduction
Natural Language processing for Sanskrit like sandhi-splitting and parsing etc. are written on top of string grammars. Syntax of languages can be computationally handled with operations on generative string grammars. ‘Meaning’ of language, however, is a richer structure than the syntax of language. Words and inﬂexions therein can be linearly handled in terms of symbolic string manipulation and matching, whereas meanings of words are related to elements outside the linear sentence. Typically, speciﬁcation of the meaning of a sentence will involve insertion of information about classes, properties and events etc. in the middle of the symbolic string. Such information is a graph. Thus, we need graph grammar of symbols to specify meaning of sentences. Such grammars should provide for embedding and paraphrasing of graphs in the middle of strings. This is exactly what is done in the traditional Sanskrit semantics. To analyze meaning of Sanskrit sentences ´sa¯bdabodha prakriya¯-s have been traditionally evolved based on the contending perspectives of (1) Vy¯akaran. a , (2) Ny¯aya-Vai´ses.ika and (3)
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 91–105, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 104 -->

92

T. Rajesh and S. Navjyoti

M¯ıma¯m. sa¯. In these analytical models, a sentence is uniquely paraphrased into a graph which is the meaning of sentence.
In fact, our goal is much bigger than just solving the problem of ´sa¯bdabodha where one only tries to analyze the meaning of a sentence. Our goal is to construct a computational ontology which is foundational as well as generative in nature. We are aiming at generative graph grammar on which comprehensive ontology interpreter can be constructed. Once that task is accomplished, one could apply it to solve domain-speciﬁc problems like ´sa¯bdabodha . Hence the main focus of the paper is on the building of graph grammar suitable for ontology applications. Idea is to construct computational environment such that applications like ´sa¯bdabodha can be built.

Fig. 1. Computational environment
Most of the existing ontologies follow top-down approach they start with the names of the entities (real as well as imaginary) existing in the universe, they try to classify these names and in turn try to classify the actual objects in the universe. But this approach has a problem since in the process of classifying names, one cannot help placing a name under two classes. In other words one name/class might have to have two parent classes. This is called crossing. For instance if one has the classes ‘ﬂying objects’ and ‘horses’ in one’s classiﬁcation and now if one encounters a new object called ‘ﬂying horse’, in which of the above classes should he place this object? Obviously, both classes should be its parents since it has the features of both the classes, and hence there is crossing. A good ontological classiﬁcation is one in which there are no crossings. Having said this, we now elucidate an alternative bottom-up approach which we take to build not just any ontology but a formal, foundational and generative ontology. For this we utilized formalization of Vai´se.sika ontology which is a comprehensive foundational ontology. While formalizing it, there was some diﬀerence noted with classical Vai´se.sika traditions, hence our approach has been called Neo-Vai´ses.ika Formal Ontology (NVFO).

---

<!-- page 105 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)

93

There are many proposed foundational ontologies based on Aristotle’s ontology like BFO [1], GFO [2], OCHRE [3], DOLCE [4] etc. These ontologies are not generative, they are depictive; they declare categories and not formally derive categories. In contrast, NVFO is generative as its categories are formally derived from the ﬁrst principle and thus generative graph grammar for NVFO can be done as has been shown in the paper.

2 Neo-Vai´ses.ika Formal Ontology (NVFO)
Vai´se.sika ontology, due to Kan. a¯da [5], Pra´sastap¯ada [6] and Udayana [7] has been formalized by Navjyoti [8, 9, 10, 11]. The formalization is based on the idea of an ontological form which is recursive. This form is called punctuator. Using punctuators categories of Vai´se.sika ontology can be derived.
2.1 Punctuator
To understand diﬀerentiating features of categories, we introduce a form punctuator which takes contents strictly as its exteriors quite unlike forms such as ‘proposition’ or ‘set’. Two examples of this form are ‘locus-located’ punctuator (a¯dh¯ara-¯adheya bha¯va) and ‘predecessor-successor’ punctuator (k¯arya-ka¯ran¯a bh¯ava), which tell apart two entities or rather make two entities contiguants in the context of locational and temporal contiguum respectively. We shall develop this form to arrive at calculus that yields categories.
The idea of punctuation can be generalized as a form ‘punctuator’ which vacuously tells apart two content-full entities that are otherwise-bound by relational context. Generalized idea of punctuator holds for experience acquired through all sensory modalities and not just auditory modality. Rather it holds for all experience. Force behind this generalization is based on the insight that no real entity is given in experience without a punctuator. Any presentation in experience minimally has a punctuator and the entities it punctuates.
Punctuator is thus a general form that vacuously weaves two exterior entities as contiguants in the context of relational contiguum. Relational contiguum is made up of the rest of entities in the world. It is the rest of the entities in the world that go in making two punctuated entities contiguant in the ﬁrst place. Relational contiguum is determinable in terms of invariants that arrest inﬁnite regress in the system of entities and punctuators. Using these invariants, categories of entities can be characterized. Further, mutually distinguishing features of categories and shared features of categories can be exactly articulated. With these categories, well-formed punctuators with determinate relational context become knowable and pronounceable.
Punctuator between two entities ex and ey is represented as pr(ex|ey) where r is an underlying contiguum.

---

<!-- page 106 -->

94

T. Rajesh and S. Navjyoti

2.2 Fundamental Types of Punctuators
In Vai´se.sika, there are three basic relations enumerated - svarupa, samava¯ya, and sam. yoga-vibha¯ga. These will form the relational contexts for our three basic punctuators (a) Self-linking (b) Inseparable punctuator and (c) Separable punctuator respectively.
Self-linking Punctuator. Punctuator pφ(ex|ey) with structure ex|ey, φ is called self-linking punctuator where φ is an empty relational context. It can be represented using directed graph notations by representing entities as circular nodes and punctuator as line.

Inseparable Punctuator. Inseparable punctuator pσ(ex|ey) with structure ex|ey, pφ(ex|S)−pφ(S|ey) where S is an inert entity (the top one in the following ﬁgure) called inherence that inseparably binds ex and ey. It can be represented using directed graph notations by representing entities as nodes and punctuator as line with arrow. The full structure of inseparable punctuator will be as depicted below.

Separable punctuator. Separable punctuator pτ (ex|ey) can be represented using directed graph notations by representing entities as nodes and punctuator as line with arrow. pτ (ex|ey) is read as ‘conjunction/disjunction with ey inheres in ex and conjunction/disjunction with ex inheres in ey’ or simply as ‘ex is in conjunction/disjunction relation with ey’. Unlike inherence relation, conjunction/disjunction relations are mutually contingent like a switch device. The full structure of separable punctuator is depicted below. Here conjunct ‘J’ is represented by the top black entity, and disjunct ‘D’ is represented by the top white entity. At any instant of time only one of them can inhere in both ex and ey since those entities can only be in conjunct or disjunct at a time but not both.

One can further generalize this and go on to construct any arbitrary punctuator of complex shape consisting of these three basic punctuators. This can be done if one has a grammar to combine these fundamental punctuators. Our

---

<!-- page 107 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)

95

claim is that any such structure represents some portion of reality. Hence one can identify each of the entities of that structure as one of the fundamental categories of Vai´se.sika . This is possible if one has interpretation rules to interpret the structure generated by the above grammar. Thus the main agenda of this paper is to give the grammar rules (to generate arbitrary complex punctuator from the basic punctuators) as well as interpretation rules (to interpret this structure) after which one can deploy this knowledge for various applications like ´sa¯bdabodha etc.

3 Graph Grammars
Graph Grammars are more generalized versions of string grammars where the alphabet are nodes and edges. As we have observed above that the 3 fundamental punctuators are graphs, and they are suﬃcient to construct any complex punctuator, one would naturally get a doubt ‘How?’ For that we need to deﬁne the rules for combining the basic punctuators in diﬀerent ways.
Firstly, our grammar consists of a set of rules to generate a graph of arbitrary size composed of basic punctuators. Then we write an interpreter another layer of rules to identify the substructures of the graph with the above categories. Before we list the rules, let’s have a look at some of the technical details necessary to understand them.
3.1 Deﬁnitions
Graph. Given two ﬁxed alphabets ΩV and ΩE for node and edge labels, respectively, a (labelled) graph (over (ΩV , ΩE)) is a tuple G=(GV , GE, sG, tG, lvG, leG), where GV is a set of vertices (or nodes), GE is a set of edges (or arcs), sG, tG : GE −→ GV are the source and target functions, and lvG : GV −→ ΩV and leG : GE −→ ΩE are the node and edge labeling functions, respectively. [12]
Total graph morphism. A (total) graph morphism (mapping) f : G −→ G′ is a pair f = (fV : GV −→ G′V , fE : GE −→ G′E) of functions which preserve sources, targets, and labels, i.e., which satisﬁes fV o tG = tG′ o fE, fV o sG = sG′ o fE, lvG′ o fV = lvG, and leG′ o fV = leG. [12]
Partial graph morphism. A subgraph S of G, written as S ⊆ G or S ֒→ G, is a graph with SV ⊆ GV , SE ⊆ GE , sS = sG|SE , tS = tG|SE, lvS = lvG|SV , leS = leG|SE. A (partial) graph morphism g from G to H is a total graph morphism from some subgraph dom(g) of G to H, and dom(g) is called the domain of g. A partial morphism can also be considered as a pair of partial functions. [12]
Production. A production p : (L −→r R) consists of a production name p and of an injective partial graph morphism r, called the production morphism. The graphs L and R are called the left-hand side (LHS) and the right-hand side (RHS) of p, respectively [12].

---

<!-- page 108 -->

96

T. Rajesh and S. Navjyoti

Graph Grammar. A graph grammar G is a pair G = ((p : r)p∈P , G0) where (p : r)p∈P is a family of production morphisms indexed by production names, and G0 is the start graph of the grammar. [12]
The above details can be concisely captured in the following diagram.

If the match m ﬁxes an occurrence of L in a given graph G, then G =p,⇒mH denotes the direct derivation where p is applied to G leading to a derived graph H. Intuitively, H is obtained by replacing the occurrence of L in G by R.
Negative Application Conditions (NACs). Rules can have exceptions - it may not be likely to apply a rule in some particular cases. Those cases/conditions can also be depicted in the form of graphs. Hence each rule may (or may not) have one or more NACs. So a rule will be applied only when its LHS matches with some subgraph of the host graph, and none of its NACs matches with any subgraph of the host graph.
4 Generation Rules of NVFO Graph Grammar
In NVFO, as mentioned earlier, there are rules for generating graphs as well as rules for interpreting these generated graphs. For the generation rules, ΩV = {G, X, E, S, J, D} where
G – start node X – variable node E – anonymous entity (this will be identiﬁed as one of the categories during interpretation) S – inherence entity (samav¯aya) J – conjunct entity (sam. yoga) D – disjunct entity (vibha¯ga)
And the set of edge labels, ΩE = {in, con, dis} where
in – inherence con – conjunct/contact dis – disjunct

---

<!-- page 109 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)

97

The edge representing self-linking relation has no label. It is recognised as such. Though it is directed it can be considered as undirected edge since for a self-linking edge direction doesn’t matter.
The start graph, G0, consists of a single node labelled ‘G’. It is the same as the LHS of Rule 1 listed below. The following rules can be applied in any order, not necessarily in the order in which they are listed.

Rule 1 (Start). We start by replacing the start node, ‘G’, with anonymous entity, ‘E ’, and variable node, ‘X ’, which are self-linked.

Rule 2 (SelfLinking). Here LHS is replaced by a punctuator which self-links already existing ‘E’(1:E) with another ‘E’. ‘X’ s here are variable nodes.
Rule 3 (LeftInherence). Here LHS is replaced by Inherence punctuator where the new entity (E ) inheres in the old entity (1:E ). In the process, ‘S ’, is generated which is self-linked to both the entities.
Rule 4 (RightInherence). Here LHS is replaced by Inherence punctuator where the old entity (1:E ) inheres in the new entity (E ).
Rule 5 (Conjunct). LHS is replaced by separable punctuator where the new entity (E ) and the old entity (1:E ) are in contact with each other. In the process ‘J ’ is generated which inheres in both the entities.

---

<!-- page 110 -->

98

T. Rajesh and S. Navjyoti

Rule 6 (Disjunct). LHS is replaced by separable punctuator where the new entity (E ) and the old entity (1:E ) are in disjunct with each other. In the process ‘D’ is generated which inheres in both the entities.

Rule 7 (MereologyConjunct). Here the middle graph represents LHS of this rule, and the rightmost one, its RHS. It says that when some entity inheres in two other entities, a conjunct can be created in between them on the condition (NAC) that there is already no conjunct between them, which is represented by the leftmost graph in the above image. This rule is to model the conjunct between parts of a whole.
Rule 8 (MereologyDisjunct). It says that when some entity inheres in two other entities, a disjunct can be created in between them on the condition (NAC) that there is already no disjunct between them.
Rule 9 (ConjunctToDisjunct). Conjunct between two entities is replaced by disjunct. This rule is to accommodate such cases.
Rule 10 (DisjunctToConjunct). Disjunct between two entities is replaced by conjunct. This rule is to accommodate such cases.

---

<!-- page 111 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO)

99

Rule 11 (Termination). This rule is applied when no more new entities need to be generated.
5 Testing If Ill-Formed Graphs Are Constructed
Our claim is that the above rules generate only well-formed graphs (those which comply with Vai´se.sika Ontology) and not a single ill-formed graph. For instance one can show that the above rules do not generate the following ill-formed graphs. In NVFO grammar the rules in which only ‘S’ or ‘E’ appear (no ‘J’ or ‘D’) are rules 1,2,3,4 and 11. Let’s show that, using these rules, the following graphs cannot be generated (we will ignore the node ‘X’ and its edges for the time being since it can always be done away with the ‘Termination’ rule (Rule 11)).

To generate the ﬁrst graph, one can try applying the above rules in the following order: 1,3 (or 1,4). They would generate two ‘E’s and one ‘S’. But if one further tries to apply one more rule which produces a new ‘S’ one cannot do it without producing a new ‘E’. Hence there can be no graph with two ‘E’s and two ‘S’s. One needs minimum three ‘E’s to have two ‘S’s. This proves Vai´se.sika theorem that same pair of entities cannot inhere in each other, and that inherence is unidirectional.
One can get closest to the second graph by applying the rules 1,2,4 in order. But here the self-linking edge between ‘S’ and the top-right ‘E’ would be missing. There is no other rule with which this edge can be created. Hence this graph too cannot be generated with this grammar. It’s an ill-formed graph according to Vai´se.sika because the same ‘S’ can never be self-linked to more than two entities at a time.
The third graph can be discarded right away since there is no single rule in our grammar which has only ‘S’s in it. In other words, any given graph, generated using these rules, has to contain minimum one or more ‘E’. This is an ill-formed graph according to Vai´se.sika since two inherence entities cannot have an inherence relation between them this would lead to inﬁnite regress.
The 4th and 5th graphs can be rejected using similar arguments. One can get closest to them by applying rules 1,3,3 (or 1,3,4 or 1,4,3 or 1,4,4) in order. But at the end of none of these combinations does one get a cycle where the third ‘E’ inheres in the ﬁrst ‘E’ or vice-versa. This chain of inherences always remains open, never closed. This proves another theorem of Vai´se.sika that there can never be a closed chain consisting of inherence relations alone.

---

<!-- page 112 -->

100 T. Rajesh and S. Navjyoti
These are only some of the very large set of ill-formed graphs which are not generated by this grammar. One can test many other ill-formed graphs and ﬁnd that none of them will be generated by this grammar.
6 Interpretation Rules of NVFO Graph Grammar
Here we interpret the above generated graphs to identify each of the anonymous entities as one of the Vai´se.sika categories.
For the interpretation rules, ΩV′ = ΩV {U, U S, V, SW, SA, Q, A} where U – Universal (sa¯ma¯nya) US – Ultimate Substance (antya dravya) V – Ultimate Diﬀerentiator (vi´se.sa ) SW – Substantial Whole (avayavi) SA – Substantial Atom (parama¯n. u) Q – Quality (gun. a) A – Action (karma)
And the set of edge labels, ΩE′ = ΩE; and any of the graphs generated by applying the rules of generation can be considered as the start graph, G0, here. These rules, unlike the rules of generation, need to be applied in the order they are listed below (the reasons are mentioned inline).
Rule 1 (DeﬁneSubstantialWhole). A substantial whole is one in which something inheres, and also it itself inheres in some other entities. Hence ‘E’ is replaced by ‘Sw’ if at least one entity inheres in it, and it itself inheres in minimum two other entities (It has to inhere in minimum two entities for it to be diﬀerentiated from Qualities and Actions which can inhere only in one entity).
In Vai´se.sika , Universal means a class which has minimum two instances of it. Now Universal is deﬁned in three rules since an entity can be identiﬁed as a Universal in three diﬀerent cases. Each of these rules has the same NACs (4 in number) which are mentioned at the end of these three rules.
Rule 2 (DeﬁneUniversal(a)). Universal inhering in two anonymous entities which haven’t yet been identiﬁed.

---

<!-- page 113 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO) 101
Rule 3 (DeﬁneUniversal(b)). Universal inhering in one anonymous entity and one whole.
Rule 4 (DeﬁneUniversal(c)). Universal inhering in two wholes. None of the above 3 rules can be applied if at least one of the following
4 NACs is true which say that nothing can inhere nor be in contact with a Universal neither anonymous entity nor a whole.
In Vai´ses.ika, Ultimate Substance is the one which has no locus, but it itself can serve as a locus for other entities. Here it is deﬁned in three rules. Each of these rules has 2 NACs.
Rule 5 (DeﬁneUltimateSubstance(a)). An anonymous entity can inhere in Ultimate Substance.
Rule 6 (DeﬁneUltimateSubstance(b)). A Universal can inhere in Ultimate Substance.

---

<!-- page 114 -->

102 T. Rajesh and S. Navjyoti
Rule 7 (DeﬁneUltimateSubstance(c)). A whole can inhere in Ultimate Substance. The following 2 NACs (for each of the above 3 rules) state that Ultimate
Substance can inhere neither in an unidentiﬁed entity nor in a whole.
Vi´ses.a, in Vai´se.sika , can inhere in one and only one entity, that too Ultimate Substance, and nothing else inheres in vi´se.sa . These Ultimate Diﬀerentiators give volume to the Universe. It is deﬁned in one rule which has 6 NACs.
Rule 8 (DeﬁneVisesa). If an entity inheres in Ultimate Substance then it can be identiﬁed as vi´ses.a under the 6 NACs.
The 6 NACs state that neither an unidentiﬁed entity nor a Universal nor a whole can inhere or be in contact with vi´se.sa .
(Here we need not handle the case where vi´se.sa inheres in two or more places since all those entities will be replaced by a whole or a Universal by now since the earlier rules will be applied ﬁrst).
The only remaining pad¯artha-s are Quality and Action. We deﬁned them as those entities in which at least one Universal inheres, but they themselves can inhere in one and only one whole or one Ultimate Substance, not more. Hence when an entity satisﬁes these conditions, it can be identiﬁed as either a Quality or an Action non-deterministically. Hence Quality and Action are deﬁned in two rules each. Each of the following 4 rules has 4 NACs.

---

<!-- page 115 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO) 103
Rule 9 (DeﬁneQuality(a)). In a Quality at least one Universal inheres, and it itself inheres in one and only one whole (its inherence in two or more wholes is handled in NACs).
Rule 10 (DeﬁneQuality(b)). In a Quality at least one Universal inheres, and it itself inheres in one and only one Ultimate Substance.
Rule 11 (DeﬁneAction(a)). In an Action at least one Universal inheres, and it itself inheres in one and only one whole.
Rule 12 (DeﬁneAction(b)). In an Action at least one Universal inheres, and it itself inheres in one and only one Ultimate Substance.
The 1st NAC says that quality/action cannot inhere in any entity other than whole or Ultimate Substance. The remaining 3 NACs state that they cannot inhere in two or more entities, whatever they may be.
7 Application to ´sa¯bdabodha
Now one can easily verify that the above rules generate the following well-formed graph which represents the structure of an arbitrary Substantial Whole (here inherence entity ‘S’ and its edges are ignored). This is just one of the many wellformed graphs generated by this grammar. In fact, our claim is that each and every substructure of a graph generated by these rules represents some portion of reality or the other. But for now, we will be using the structure of a substantial whole to do ´sa¯bdabodha .

---

<!-- page 116 -->

104 T. Rajesh and S. Navjyoti
Let’s consider the sentence, ‘Jug is on the table’. Using standard NLP techniques, one can identify jug and table to be some objects and that table is used in the locative sense. This is all the meaning that could be drawn when this sentence is considered as such. But when we replace ‘Sw’ in the above structure with ‘jug’, and another ‘Sw’ (which is in contact with the earlier Sw) with ‘table’, we can draw the following inferences:
– Jug is in contact with table and vice-versa. – Jug has some qualities. – Table has some qualities. – Some actions can be performed on jug. – Some actions can be performed on table. – Jug has some parts. – Table has some parts. – Jug belongs to some class ‘jugness’ which indicates that there are probably
some other jugs in this Universe which may also have same qualities, and which may also be in contact with some table. – Similarly, table belongs to the class ‘tableness’ which indicates that there are probably some other tables in this Universe. This kind of reasoning has many applications. For instance one can write a query application which asks the user relevant queries when he gives the sentence, ‘Jug is on the table’, as input to the query system. The system can ask the following questions: – What is the color of the jug? – Are there some other jugs on the table? – What is the length of the table? – What is the texture of the surface of the table? – ...
8 Conclusion
S´a¯bdabodha is only one of the many applications of this grammar. Since Vai´se.sika is not a domain ontology but a foundational ontology, our grammar is a

---

<!-- page 117 -->

Generative Graph Grammar of Neo-Vai´ses.ika Formal Ontology (NVFO) 105
foundational framework upon which any domain ontology can be modeled, not just ´sa¯bdabodha . The power of this grammar lies in its generative nature which none of the other existing ontologies have.
References
1. BFO (Basic Formal Ontology), http://www.ifomis.org/bfo 2. GFO (General Formal Ontology), http://www.onto-med.de/ontologies/gfo/ 3. OCHRE (Object-Centered High-level REference Ontology),
http://ifomis.uni-leipzig.de/ 4. DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering),
http://www.loa-cnr.it/DOLCE.html 5. Kan. a¯da: The Vai´ses.ika sutras of Kan. a¯da, with the commentary of S´amkara Misra
and extracts from the gloss of Jayanarayana. Translated in English by Nandalal Sinha. Allahabad (1911); 2nd edn. Revised and enlarged, Allahabad (1923); Reprinted New York (1974), Delhi (1986) 6. Pra´sastap¯ada: Pad¯arthadharmasam. graha with Ny¯ayakandal¯ı of Sridhara. English Translation by Ganganatha Jha. Chowkhamba, Varanasi (Reprint 1982) 7. Udayana: Lakshan. a¯vali. In Musashi Tachikawa: The Structure of the World in Udayana’s Realism: A study of the Lakshan. ¯avali and Kiran. a¯vali. Springer, Heidelberg (1982) 8. Singh, N.: Comprehensive Schema of Entities Vai´sesika Category System. Science Philosophy Interface 5(2), 1–54 (2001) 9. Singh, N.: Formal Theory of Categories through the Logic of Punctuator (2002) (unpublished) 10. Singh, N.: Theory of Experiential Contiguum. Philosophy and Science Exploratory Approach to Consciousness, pp. 111–159. Ramakrishna Mission Institute of Culture, Kolkata (2003) 11. Singh, N.: Foundations of Ontological Engineering. Lecture slides of course at IIIT Hyderabad (2008) 12. Rozenberg, G., et al. (eds.): Foundations. Handbook of Graph Grammars and Computing by Graph Transformation, vol. 1. World Scientiﬁc, Singapore (1997) 13. The Attributed Graph Grammar System, http://user.cs.tu- berlin.de/~ gragra/agg/

---

<!-- page 118 -->

Headedness and Modiﬁcation in Nya¯ya Morpho-Syntactic Analysis: Towards a
Bracket-Parsing Model
Malhar Kulkarni, Anuja Ajotikar, Tanuja Ajotikar, Dipesh Katira, Chinmay Dharurkar, and Chaitali Dangarikar
Indian Institute of Technology, Bombay {malhar,anuja,tanuja,dipesh,chinmay,chaitali}@hss.iitb.ac.in
Abstract. The paper aims to develop a parsing model using the ny¯ayamorpho-syntactic analysis using the two terms namely, praka¯rata¯ and vi´se.syat¯a. The idea is that praka¯rata¯ and vi´se.syat¯a are to be seen as modiﬁcation (modiﬁedness) and headedness respectively. Several representative sentences have been exempliﬁed using the method developed. prak¯arata¯ and vi´ses. yat¯a not only come through to give a thorough analysis at word level, but may be extended, as it has been shown in this paper, to get a thorough analysis at syntactic and discourse level, as well.
Keywords: headedness, modiﬁcation, head-modiﬁer relationship, prak¯arata¯ and vi´se.syat¯a.
1 Introduction
Many systems that provide the morphological information of Sanskrit are available online. They are built by following scholars at following institutions- G´erard Huet, INRIA, Paris,1 Amba Kulkarni, University of Hyderabad,2 Peter Scharf, Brown University3 and Girish Nath Jha, JNU.4 Ramakrishnamacharyulu (2009) presented a tagset to be used for the processing of Sanskrit sentences. We base ourselves on these existing systems and aim to provide with a model to parse Sanskrit sentences with head and modiﬁer information. In order to do so we draw our material from the framework of the Navya-Nya¯ya school of Indian Philosophy. Several devices in Pa¯n. ini’s grammar like abhidha¯na, k¯araka have been employed to develop the analysis proposed. Several studies like Akshara Bharti (1995) and Pederson (2004), show use of Paninian framework in dependency parsing. They do not however, explicitly use the Navya-Nya¯ya technique of representing head and modiﬁer relation within a word and concentrate mainly on intra-word relations. Further, they try to adapt the Paninian framework to the parsing of other Indian and non-Indian languages and not Sanskrit. 1 http://sanskrit.inria.fr/DICO/reader.html 2 http://sanskrit.uohyd.ernet.in/lang-tech/lang-tech.html 3 http://sanskritlibrary.org/ 4 http://sanskrit.jnu.ac.in/index.jsp
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 106–123, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 119 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 107
1.1 Heading towards vi´ses. yata¯
The idea of head across the syntactic theories has been residing in the basic idea of category, i.e. head as the unit that gives category to a phrase. It is as if the phrasehood of a phrase depends on the head.
The head of X is the part which determines the category of X. Example: The category of ate the apple (VP) is determined by the verb ‘ate’, not by any other element. This explains why it coordinates with other phrases which begin with a verb, but not with phrases that share the nominal part: peeled the apple and ate the apple, *ate the apple and over the apple.
Head in X-bar theory is an oﬀshoot of the basic idea of phrase which is the centre of formalization. Here, though we would be using “head” as the English equivalent, it is strictly in the sense of vi´se.sya and so we would distance this vi´se.sya (head) from the head as in the linguistic theories.
The distinct nature of this headedness is that, save verb, for all the padas, it is the suﬃxes that hold the vi´se.syata¯. Here, head-modiﬁer relation is not of the kind that exists in X-bar theory. The prakr. ti-pratyaya analysis is used to speak in terms of prak¯arata¯ and vi´se.syata¯. So, in the analysis presented here (which takes inputs from nya¯ya, vya¯karan. a etc.), it is the pratyaya that is mostly the head and the prakr. ti that is the modiﬁer, and it is the relation between these two that exhausts the analysis.
On the absence of head in P¯an. ini. Pradh¯ana or vi´se.sya or anything that may express any sort of the dominant-subordinate relation is absent in Pa¯n. ini. Thus one may say that head is not deﬁned in Pa¯n. ini, neither the concept of head has been deployed in Pa¯n. ini. So, Pa¯n. ini is not bound to deﬁne head. The ensuing question would then be: why in Pa¯n. ini there is no idea or concept of head.
The reasons behind the development of the concept of head in GB or X-bar theory would be cognitive. In the sense that idea behind getting an abstract, generalized phrase structure through X-bar emerged as there was a need to understand the economy and speed in the acquisition. Head-modiﬁer abstraction in X-bar theory gives a general phrase structure for all the phrases, i.e. it successfully explains the common structure applicable to all the phrases. [15]
There are no such cognitive commitments in Pa¯n. ini. Also, it seems that phrase has never been the concern of Pa¯n. ini. In Paninian morphology it is the pada, which is at the center of analysis. It can also be said that no phrase-based analysis is carried out in P¯an. ini, overtly or covertly. Though Paninian grammar may be claimed to be v¯akya-centric, it is only through the consistent pada-analysis that va¯kya may be analyzed in the totality of pada. Phrase, as something possessing a category as its head, is simply impossible in Pa¯n. ini because categories have been fashioned diﬀerently in Pa¯n. ini.
Though the terms head and modiﬁer have strong aﬃliations to the generative grammars (which do not talk in terms of dependency, as dependency grammars

---

<!-- page 120 -->

108 M. Kulkarni et al.
do),5 we, in this paper, use the terms headedness for vi´se.syata¯ and modiﬁcation for praka¯rat¯a.
The analysis and parsing presented in this paper are distinct from the theories like dependency grammar or phrase structure grammar. Though we use terms like kart.r, karma which may be identiﬁed in parallel with the functional categories, one important diﬀerence to be noted is that our analysis presents an intra-lexical analysis that holds suﬃx as the head (save verbs) and inter-lexical analysis as well.6
We certainly do not attempt to fuse dependency or phrase structure grammars. We use the terms modiﬁcation and headedness as we ﬁnd them convenient and suitable equivalents for prak¯arata¯ and vi´ses. yata¯. These terms have not been used to evoke any resemblance or solidarity towards the linguistic theories. One straightforward aim of this paper is to represent the system of sentence analysis and parsing found in the traditional knowledge system of Ny¯aya with some inputs from Vy¯akaran. a.
1.2 Ny¯aya Terms Used in the Head-Modiﬁer Analysis
Following Sanskrit terms (with abbreviations) are used for analyzing head-modiﬁer relationship in Sanskrit sentences:
This terminology is used in the texts of Navya-Nya¯ya. We have seen this terminology being used in several Navya-Nya¯ya texts, but never in the context
5 See Ku¨bler, et al (2009: 2) While the dependency structure represents headdependent relations between words, classiﬁed by functional categories such as subject (SBJ) and object (OBJ), the phrase structure represents the grouping of words into phrases, classiﬁed by structural categories such as noun phrase (NP) and verb phrase (VP).
6 See Ku¨bler, et al (2009: 2) Other terms that are found in the literature are modiﬁer or child, instead of dependent, and governor, regent or parent, instead of head. Note that, although we will not use the noun modiﬁer, we will use the verb modify when convenient and say that a dependent modiﬁes its head. Also, Ku¨bler, et al (2009: 3). It is also worth noting that many syntactic theories make use of hybrid representations, combining elements of dependency structure with elements of phrase structure. Hence, to describe dependency grammar and phrase structure grammar as two opposite and mutually exclusive approaches to natural language syntax is at best an over-simpliﬁcation.

---

<!-- page 121 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 109
of parsing a sentence with special reference to head-modiﬁer representation. We explain below the three main terms brieﬂy:
1. vi´se.sya. This word is in use since P¯an. ini. It is a relative term and not absolute. It co-exists in relation with the state of being a modiﬁer. P¯an. ini in his grammar called A.s.t¯adhya¯y¯ı uses it in relation with another term called vi´se.san. a. The term vi´se.sya literally means something which is being distinguished and the term vi´se.san. a literally means the instrument which distinguishes. The term vi´se.sya indicates the element which can be said to function as a ‘head’ in a particular structure in the scheme proposed in this paper. The suﬃx t¯a indicates the state of being a head.
2. prak¯ara. - This word is proposed to be used in this scheme in the sense of a modiﬁer. This word came into circulation in this sense with the advent of Navya-Ny¯aya. The suﬃx t¯a indicates the state of being a Modiﬁer.
3. niru¯pita. - This word indicates the relation between the two concepts mentioned above. It means ‘in relation to’. It is used as an intra-lexical as well as inter-lexical metalinguistic connector.
The state of being a head and the state of being a modiﬁer are correlated, coexistent and are assumed to rest in the meaning of the word. This substratum is indicated here with the help of the word nis..tha.
Thus using this terminology we can present in brief the head modiﬁer relation for a representative word like gra¯mam. in the following way,
Analysis- gr¯ama-nis..tha-praka¯rat¯a-niru¯pita-karma-nis..tha-vi´se.syata¯ |7
2 Prak¯arata¯-Vi´ses. yat¯a Analysis
2.1 Sentence Level
Sanskrit scholars have proposed various ´s¯abdabodha theories. For grammarians meaning of the verb root is the most important element in the sentence. Therefore they have proposed dh¯atvartha-mukhya-vi´se.syaka-´s¯abdabodha. According to them words of any given sentence can be classiﬁed as either subanta or tin˙ anta. Since, the meaning of the verbal root is the most important component of the sentence, all subanta words will be connected to the tin˙ anta word. Therefore at the sentence level, only tin˙ anta becomes vi´se.sya. All the subantas become prak¯aras of the tin˙ anta word. Therefore, tin˙ anta word in the sentence, b¯alah. pa.thati will be tagged as follows:
(ba¯lah. ) praka¯rat¯a-niru¯pita (pa.thati) vi´se.syata¯ |
In some sentences, more than one subanta will have the same vibhakti. These subantas are grouped together as they have adjective-substantive relationship
7 The English paraphrase of the same would be- the state of being a head, residing in ‘karma’, in relation to the state of being a modiﬁer which resides in ‘village’. This provides us with the information that it is ‘village’ which is the head and ‘karma’ is the modiﬁer.

---

<!-- page 122 -->

110 M. Kulkarni et al.
between them. The adjectives are linked to the substantive by “non-diﬀerence” (abheda). For example:
“arun. aya¯ ekah¯ayanya¯ pin˙ g¯aks. ya¯ gav¯a somam. kr¯ın. a¯ti |” In this sentence there are four subantas with the same vibhakti arun. ay¯a, ekah¯ayanya pin˙ gaks. ya¯ gav¯a. Therefore they are grouped together. One subanta (here, gav¯a) is the substantive. The adjectives are shown to be linked with this substantive by the relation of non-diﬀerence (abhinna). This is shown below:
[(arun. ay¯a) a( ekaha¯yany¯a) a( pin˙ g¯aks. ya¯)a gava¯] somam. kr¯ın. a¯ti | But in some cases, some subantas will be linked to the verbal root directly and some will be linked via these directly linked subantas. This we show in the following ﬁgure:
Fig. 1. Direct and indirect relation of subantas with the tin˙ anta
Therefore, in this prak¯arat¯a- vi´se.syata¯ analysis, subantas that are linked to the tin˙ anta directly, are related to the tin˙ anta by the praka¯rat¯a-niru¯pita tag. Whereas, the subantas that are linked to the tin˙ anta-linked-subantas are grouped together. This group of vi´se.san. as is placed before the subanta to which they are linked. These subantas will also be linked by the tag prak¯arata¯- niru¯pita but instead of tin˙ anta they are linked to either karta¯ or karma. Therefore, the above mentioned sentence can be analyzed as:
Table 1. Direct and indirect relations of subantas with the verb (odanam. ) praka¯rat¯a- niru¯pita pacati | (stha¯ly¯am) prak¯arata¯- niru¯pita odanam. | (vahnin¯a) prak¯arata¯- niru¯pita pacati | (ka¯as.haih. ) prak¯arata¯- niru¯pita pacati | (gra¯m¯at) praka¯rata¯- niru¯pita agatah. | (a¯gatah. )-(devadattah. ) | (devadattah. ) prak¯arata¯-niru¯pita pacati |
Though all the subantas are ultimately linked to the tin˙ anta, there is one exception. The genitive case which expresses relations8 is not linked to the tin˙ anta. The genitive case shows a relation with another noun in the sentence. 8 P. II.3.50

---

<!-- page 123 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 111
Table 2. non-relatedness of the genitive case and verb
In this prak¯arata¯-vi´se.syata¯ analysis, such genitive cases will be linked to the nouns to which they are related. Further, the genitive case will be tagged as prak¯arata¯-niru¯pita as it is the modiﬁer of the noun. It is not the head of the noun to which it is related.
Thus the phrase da´sarathasya putrah. can be analyzed as (da´sarathasya) prak¯arata¯- niru¯pita putrah. . But the genitive word da´sarathasya will not be linked to the verb gacchati in the sentence da´sarathasya putrah. gacchati |
2.2 Word Level praka¯rata¯-vi´ses. yata¯ Analysis Rules Similar prak¯arata¯-vi´se.syata¯ can be analyzed at the word level too. Each word in the Sanskrit sentence can be segmented into two parts: (a) prakr. ti and (b) pratyaya. Prak¯arata¯-vi´ses. yata¯ analysis within a subanta word: Any subanta word in the sentence can be segmented into two parts: (1) prakr. ti or pra¯tipadika and (2) a suﬃx, sup. The meanings of these sup pratyayas are deﬁned in the Paninian grammar. (Table.3)
Here the pratyaya¯rtha is “head” so it is analyzed with ni.s.tha-vi´se.syata¯. The word ra¯mam will be analyzed as:
prakr. tyartha-ra¯ma-ni.s.tha- prak¯arata¯- niru¯pitapratyaya¯rtha-karmani.s.tha-vi´se.syata¯.
-This (i.e. karma-nis..tha etc.) particular tag is given when the particular ka¯raka is not expressed by the verbal suﬃx. Therefore (k¯araka) is variable.
-But the nominative singular suﬃx does not express any k¯araka relation and its meaning is pra¯tipadika only therefore the particular pra¯tipadika will be a part of the tag. In the case of indeclinables though vibhakti is deleted, the meaning of the suﬃx is vi´se.sya and is treated like prathama¯ thus in the following case:
ca+su ca+ 0 we observe following analysis: prakr. tyartha-cani.s.tha- prak¯arata¯- niru¯pita - pratyaya¯rtha - cani.s.tha- vi´se.syata¯

---

<!-- page 124 -->

112 M. Kulkarni et al. Table 3. Meanings of sup pratyayas9
Fig. 2. Diﬀerence between the internal meaning structure of impersonal and active/passive verbs Prak¯arat¯a-vi´ses. yat¯a analysis within tin˙ anta word: In the case of verbs, root meaning is “head” and suﬃx meanings are modiﬁers. The tin˙ anta suﬃx has four meanings (1) k¯araka, (2) purus.a, (3) vacana and (4) ka¯la. Tense or mood is related with the action and person and number are related with k¯arakas expressed by a tin˙ suﬃx. Overall two k¯arakas can be expressed by a tin˙ suﬃx and in the 9 Even though more than one k¯araka meaning is conveyed by one vibhakti we do
not go into all the details of these mappings. We restrict ourselves for the present purpose to the most common mappings. Needless to say that we assume that the same technique would be equally applicable to other k¯araka meanings as well.

---

<!-- page 125 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 113
absence of the expression of these ka¯rakas; bh¯ava or action is expressed by the tin˙ suﬃx. When bh¯ava is expressed by a suﬃx, person and number are not related to it. Only ka¯la is. Here suﬃx expresses action in general and there is non-diﬀerence (abheda) between root meaning and suﬃx meaning. (See Fig. 2.)
3 From the above Discussion, We Formulate the Following Rules on Which We Base Our Analysis
3.1 Minimal Set of Rules on the Basis of Which the Headedness and Modiﬁcation Will Be Determined at Diﬀerent Levels
Rule no. 1. Suﬃx meaning is head10 and root meaning is modiﬁer. Sub-rule a. In the verb,11 root-meaning is the head and the suﬃx-meanings
are the modiﬁers.
Rule no. 2. Modiﬁcation of verbal suﬃx meanings2.a The number and person (which are the suﬃx meanings) are the modiﬁers
of the ka¯raka. 2.b Time modiﬁes the action12 denoted by the verbal root.
Rule no. 3. The ka¯raka which is denoted by the tin˙ suﬃx matches with the nominative case in the sentence.13
Rule no. 4. All the ka¯rakas modify the action denoted by the verbal root. These rules can be said to be the rules for the head-modiﬁcation within the
pad¯artha After applying these rules we get the following rule for headedness and mod-
iﬁcation on the sentence level.
Rule no. 5. The element which invariably has the tag of nis..tha vi´ses. yata¯ is the mukhya vi´se.sya of the sentence.
After applying these rules we get the following general rule which is applicable on discourse level.
Rule no. 6. The head of the ﬁrst sentence remains a head till it is modiﬁed by a sentence connective or gerund.
3.2 Complete prak¯arata¯- vi´ses. yata¯ Analysis
If both, sentence level and word level, prakr. ti - pratyaya based analysis are combined, then the constituents of the meanings of the subanta words are linked as follows: 10 prak.rtipratyaya¯rthayoh. sah¯arthatve pratyay¯arthasya eva pra¯dh¯anyam. para-
malaghuman˜ju¯.s¯a dha¯tvarthaprakara´sam p. 29 11 tin˙ ante kriy¯aya¯h. eva pra¯dh¯anyam˙ ´s¯abdabodhe na pratyaya¯rthasya iti bodhyam.
k¯ala´sca vy¯apara vi´ses. an. am. ibid p. 29 12 ibid p.30 13 abhihite prathama¯. va¯rtika on A. 2.3.2

---

<!-- page 126 -->

114 M. Kulkarni et al.
Fig. 3. Complete analysis of a sentence prior to prak¯arata¯ and vi´ses.yat¯a tagging (Active Voice)
The tin˙ anta suﬃx has four meanings (1) k¯araka, (2) puru.sa, (3) vacana and (4) k¯ala. The subanta ending in the ﬁrst case-ending is identiﬁed with the meaning k¯araka of the tin˙ anta suﬃx. Therefore, it is placed or moved in the k¯araka meaning. Other two meanings of the tin˙ anta suﬃx namely, puru.sa, and vacana become the prak¯ara of the subanta in the nominative case, linked with the k¯araka meaning of the tin˙ anta suﬃx. The complete sentence meaning after prak¯arata¯ and vi´se.syata¯ analysis will be as follows.(Table.4)
If the sentence is transformed to or is in the passive or impersonal form then we get slightly diﬀerent sentences after the prak¯arata¯ and vi´se.syata¯ analysis. (Fig.4)
Since karma is expressed, (abhihita) in the passive voice, it is in the ﬁrst caseending. The tin˙ anta suﬃx in the passive verb has the meaning karma. Therefore, as per our rule no. 3 this subanta which is in nominative case will be linked to the meaning karma of the tin˙ anta.
The complete sentence after prak¯arata¯ and vi´se.syata¯ analysis of a passive voice will be as follows: Table 4. praka¯rata¯-vi´ses. yat¯a analysis of the active voice sentence ramah. gr¯amam˙ gacchati

---

<!-- page 127 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 115
Fig. 4. Complete analysis of a sentence prior to praka¯rata¯ and vi´ses.yat¯a tagging (Passive Voice) Table 5. praka¯rata¯-vi´ses. yat¯a analysis of the passive voice sentence ramen. a gramah. gamyate
Similarly, in the impersonal voice, the kart.r is linked with tin˙ anta but it is not expressed, abhihita by the tin˙ suﬃx. Therefore, kart.r in such sentences is in instrumental case.
Fig. 5. Complete analysis of a sentence prior to praka¯rata¯ and vi´ses. yat¯a tagging (impersonal voice)
Even though the suﬃx in the impersonal verb conveys two meanings (1) k¯ala, tense and (2) bh¯ava, the later meaning does not ﬁgure in the head-modiﬁer analysis because the meaning bh¯ava actually means the action in general and therefore is connected to the meaning of the verbal root with non-diﬀerence (abheda). The head-modiﬁer analysis of the sentence of the impersonal voice will be as shown below. (Table.6)

---

<!-- page 128 -->

116 M. Kulkarni et al. Table 6. praka¯rata¯-vi´se.syat¯a analysis of the impersonal voice sentence : r¯amen. a hasyate
In this way, we can show that with the help of these minimal set of seven concepts and six rules, we can analyze head-modiﬁer relationship in any Sanskrit sentence. In the following, we show how this analysis can be modeled formally and can be used along with the existing language processing tools for Sanskrit.
4 Automated or Semi-automated praka¯rata¯-vi´ses. yat¯a Analysis
This analysis can be modeled for the automated or semi-automated head and modiﬁer relationship analysis of Sanskrit sentences. We propose a model using the rules mentioned in the above section. Any non-verse prose sentence can be analyzed by this model. Technical terminology can be shortened and analysis can be made much simpler if presented formally. We propose following short-forms for the formal representation of these rules (Table 7).14
For example, the head and modiﬁer analysis for the active sentence “r¯amah. gr¯amam. gacchati” will be as follows:
14 TM1=k¯araka, (kart.r, karma), TM2=purus. a, TM3=vacana, TM4=k¯ala This is also mentioned in the discussion on ﬁg.2.

---

<!-- page 129 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 117 Table 7. Abbreviations used in the formal representation of the head-modiﬁer analysis in Sanskrit
5 Hierarchical Bracket Parsing
The model that is proposed here takes primarily into consideration the brackets consisting of words and shows with the help of rules how the system can reduce Table 8. Hierarchical bracket parsing of the active voice sentence ra¯mah. gr¯amam. gacchati

---

<!-- page 130 -->

118 M. Kulkarni et al.
them one by one and ultimately how all these brackets representing words get reduced to a bracket of a sentence with the information of the head and modiﬁer tagged to each bracket intact. We present below a brief description of the Hierarchical Bracket Parsing.

---

<!-- page 131 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 119 Table 9. Hierarchical Bracket Parsing of the passive voice sentence r¯amen. a gra¯mah. gamyate
Table 10. Hierarchical Bracket Parsing of the impersonal voice sentence r¯amen. a hasyate
This kind of analysis can be done not only on the simple sentences but also to the complex sentences from the literature. For example, we present the head and modiﬁer analysis of the complex sentence, praja¯su p¯alan¯ım. vr. ttim. veditum. yam. ayun˙ kta sa varn. ilin˙ g¯ı viditah. vanecarah. dvaitavane yudhi.s.thiram. sam¯ayayau |15
6 Application at Discourse Level
So far we presented analysis using the Navya-Ny¯aya terms of word-word meanings, and sentence-sentence meanings. We also presented this analysis in all the three voices and showed that the analysis does not get aﬀected by the functional categories. Now we show how this technique can be used for discourse level. We present below the analysis of a group of three sentences. We will show how one element can be considered as head within all these three sentences and the rest as modiﬁers using this technique. 15 Partial construal of Kiratarjuniyam 1.1

---

<!-- page 132 -->

120 M. Kulkarni et al.

Fig. 6.

---

<!-- page 133 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 121 Table 11. prak¯arata¯-vi´ses.yat¯a analysis of multiple sentences
Sentences: S1. ra¯mah. mandiram. gacchati| S2. tatah. vidya¯layam. gami.syati| S3. anantaram. g.rham. gami.syati|(Table.11) The last tag (ni.s.tha-vi´se.syata¯) in S3 indicates that the meaning of the verbal root in S3 remains a head in the context of (S1+S2). In other words, this tag shows the main meaning in the group of three sentences. This feature can be extended to a larger group of sentences.
7 Concluding Remarks and Future Work
Thus we showed that we can make optimal use of the existing theories within Sanskrit traditional ´sa¯stras for the purpose of parsing Sanskrit at the discourse level. Our approach combined insights from both Ny¯aya as well as Vy¯akaran. a for parsing at various levels. For a sentential analysis, we used the Vy¯akaran. a

---

<!-- page 134 -->

122 M. Kulkarni et al.
way of analysis and at the discourse level on the ﬁrst step when we have to connect one previous sentence to the next one, we used the Navya-Nya¯ya way of analysis and then again we used Vy¯akaran. a way of analysis.
Thus we have presented a model that suﬃciently and minimally represents the head-modiﬁer relationship between nominal and verbal elements. It is minimal in the sense that, it is the minimum number of terms employed from NavyaNy¯aya that would suﬃciently represent the analysis. We have also shown how it will be useful when we take into consideration the discourse level.
The analysis can be seen as an end in itself, such that it helps understand the sentence and words within it, in the scope of the proposed schema.
We propose to show in future how this model will capture the vi´se.san. a-vi´se.sya relation amongst nouns and also how it could prove useful for anaphora resolution in Sanskrit. We could also develop this model using M¯ıma¯m. sa¯ techniques to deﬁne sentence connectives that would prove useful for the purpose of discourse level analysis of Sanskrit. We presented an outline of a model that could very well be developed and tested in a full-ﬂedged bracket parsing grammar under whose purview would fall issues like anaphora resolution, ellipsis and coordination etc.
Acknowledgements. We wish to thank all the reviewers for their invaluable comments that helped us revise the draft of this paper. We also wish to thank the editor for co-operation.
References
1. Bharati, A., Chaitanya, V., Sangal, R.: Natural Language Processing: A Paninian Perspective. Prentice Hall of India, New Delhi (1995)
2. Bhattacharya, G.: Vis.ayat¯av¯ada. Prasad, Varanasi (1943) 3. Carnie, A.: Syntax A Generative Introduction. Blackwell Publishing, Oxford (2006) 4. Corbett, G.G., Fraser, N.M., Scott, M. (eds.): Heads in Grammatical Theory. Cam-
bridge University Press, Cambridge (1993) 5. Culicover, P.W.: Principles and Parameters: An Introduction to Syntactic theory.
Oxford University Press, New York (2005) 6. Jha, G.N., Sobha, L., Diwakar, M., Surjit, K.S., Praveen, P.: Anaphors in Sanskrit.
In: Johansson, C. (ed.) Proceedings of the Second Workshop on Anaphora Resolution, vol. 2. Cambridge Scholars Publishing, Cambridge (2008) ISSN 1736-6305 7. Jhalkikar, B.: Ny¯ayako´sa. Bhandarakar Oriental Research Institute, Pune (1893) 8. Ku¨bler, S., McDonald, R., Nivre, J.: Dependency Parsing. Morgan and Claypool Publishers, San Francisco (2009) 9. Mahalakshmi, G.S., Geetha, T.V., Kumar, A., Kumar, D., Manikandan, S.: Gautama - Ontology Editor Based on Nyaya Logic. In: Ramanujam, R., Sarukkai, S. (eds.) Logic and Its Applications. LNCS (LNAI), vol. 5378, pp. 232–242. Springer, Heidelberg (2009) 10. Mahalakshmi, G.S., Geetha, T.V.: Representing Knowledge Eﬀectively Using Indian Logic. In: Sajja, A. (ed.) TMRF e-book, Advanced Knowledge based Systems, Model, Applications, Research, vol. I, pp. 12–28 (2010), http://www.tmrfindia.org/eseries/ebookV1-C2.pdf

---

<!-- page 135 -->

Headedness and Modiﬁcation in Ny¯aya Morpho-Syntactic Analysis 123
11. Pedersen, M., Domenyk, E., Amin, S.K., Lakshmi P.: Relative clauses in Hindi and Arabic: a Paninian dependency grammar analysis. In: Coling 2004 workshop: Proceedings Recent Advances in Dependency Grammar. Prentice Hall of India Pvt. Ltd., Geneva (2004)
12. Potter, K.: Encyclopedia of Indian Philosophy. Motilal Banarasidas, Delhi (2000) 13. Sarma, V.V.S.: Survey of Indian Logic from the point of view of Computer Science.
In: Sadhana, vol. 19 pp.196971–196983 (1994),
http://www.springerlink.com/content/lnv6656gg37022t0 14. Shastri, G.: Patan˜jali’s Vy¯akaran. amah¯abha¯s.ya with Kaiyat.a’s Prad¯ıpa and
Bhat.t.oji D¯ıks.ita’s ´sabdakaustubha and N¯age´sabhat.t.a’s Udyota with commentary R¯ajalaks.m¯ı. Rashtriya Sanskrit Sansthan, New Delhi (Reprint 2006) 15. Smith, N.: Chomsky Ideas and Ideals. Cambridge University Press, New York (2004) 16. Bhagavat, P.V.B.: (Tr.(in Marathi)): Paramalaghuman˜jus. . Paramarsha Prakashan, Pune Vidyapith Tattvajnana Vibhaga, Pune (1984)

---

<!-- page 136 -->

Citation Matching in Sanskrit Corpora Using Local Alignment
Abhinandan S. Prasad and Shrisha Rao
International Institute of Information Technology, Bangalore abhinandan.sp@iiitb.net, srao@iiitb.ac.in
Abstract. Citation matching is the problem of ﬁnding which citation occurs in a given textual corpus. Most existing citation matching work is done on scientiﬁc literature. The goal of this paper is to present methods for performing citation matching on Sanskrit texts. Exact matching and approximate matching are the two methods for performing citation matching. The exact matching method checks for exact occurrence of the citation with respect to the textual corpus. Approximate matching is a fuzzy string-matching method which computes a similarity score between an individual line of the textual corpus and the citation. The SmithWaterman-Gotoh algorithm for local alignment, which is generally used in bioinformatics, is used here for calculating the similarity score. This similarity score is a measure of the closeness between the text and the citation. The exact- and approximate-matching methods are evaluated and compared. The methods presented can be easily applied to corpora in other Indic languages like Kannada, Tamil, etc. The approximatematching method can in particular be used in the compilation of critical editions and plagiarism detection in a literary work.
Keywords: citation matching, local alignment, Smith-Waterman-Gotoh algorithm, Sanskrit, Mah¯abha¯rata, Mah¯abha¯rata-T¯atparyanirn. aya.
1 Introduction
Citation matching in literature is the problem of ﬁnding which citations occur where in a given textual corpus. Citation matching is applied in various areas like authorship detection, content analysis, etc. Currently, citation matching is limited to scientiﬁc literature because most of the citation mapping work like autonomous citation matching, identity uncertainty, etc., are done on scientiﬁc literature. Autonomous citation matching identiﬁes and groups variants of the same paper [5]. Identity uncertainty in the context of citation matching decides whether a set of citations corresponds to the same publication or not [9]. Citation matching is an unexplored area in Sanskrit literature due to various reasons like lack of encoded texts, complexity of the Sanskrit language compared to English, lack of Sanskrit knowledge among computer scientists, etc. As far as we know, no one has seriously attempted citation matching on Sanskrit literature.
This paper presents two methods: exact matching and approximate matching, to perform citation matching in Sanskrit texts. Exact matching is based on the
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 124–136, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 137 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 125
idea of ﬁnding the precise character-by-character match between pattern and text. This method ﬁnds citations that are exactly the same as those in the corpus. The search space for a given text with citations is directly proportional to the size of the corpus from where citations are to be found. Sorting the corpus can help reduce the number of comparisons needed by obviating the need to make unnecessary comparisons. This method cannot ﬁnd citations if there are occurrences of p¯a.tha¯ntara (variant readings) or sandhi-viccheda (splits of compounds). Such occurrences provide the motivation for the approximate matching method.
The p¯a.tha¯ntara and sandhi-viccheda problems can be easily handled if we consider similarity or closeness. Approximate matching is based on this idea. This method is widely applied in bioinformatics, where a common technique called local alignment is used. The Smith-Waterman algorithm [14] is one of the predominant algorithms in local alignment. The Smith-Waterman algorithm ﬁnds a pair of segments in the nucleotide or amino acid (protein) sequences such that there is no other segment with greater similarity [14]. The SmithWaterman-Gotoh algorithm [4] is an extension of the Smith-Waterman algorithm which uses aﬃne gap penalty to reduce the computational overhead of the basic Smith-Waterman algorithm.
Our approximate matching method computes the Smith-Waterman-Gotoh distance [4] between citation and text. The results are ﬁltered based on the similarity cutoﬀ. As our intuition would suggest, this method is computationally intensive compared to exact matching.
An experiment is conducted using the Maha¯bh¯arata-T¯atparyanirn.aya as the base text where citations may exist, and the Maha¯bh¯arata [13] as the source text where to look for citations.1 The Maha¯bh¯arata-T¯atparyanirn.aya is a commentary on the Mah¯abha¯rata in digest form.2 Its author Madhva (1238–1317 CE) indicates that a lot of its verses are taken from the Maha¯bh¯arata directly:
ÖØ£ Ô ÝÌ Ó Ó Ò ­ÝÓ Ý Ñ£ Ø º ØÌ ­ Ý©Ý Ñ¹Øâ ß£ÖÚ ×Ú­ ¸ 2 - 53
However, a lot of the citations are yet to be traced. Madhva’s citation of untraceable sources has in general been the subject of some controversy since the 17th century.3
1 Mahoney [6] sorts some Sanskrit texts but as far as we know, no one has sorted the entire Mah¯abh¯arata. We have sorted the Mah¯abha¯rata to reduce the search size for exact matching. A previously unavailable sorted verse-index of the Maha¯bh¯arata has thus been created as part of this eﬀort. See the URL http://www.iiitb.ac.in/faculty/srao/other-information/ for a link to the same.
2 See [12] for more information on the Mah¯abh¯arata-T¯atparyanirn. aya and its author. 3 In this regard, see [12] for some general discussion. Mesquita claims [7] that Mad-
hva’s citations are his own inventions, a charge countered by Rao and Sharma [10]. Mesquita recently has repeated [8] the charge in the speciﬁc context of Madhva’s citations from the Maha¯bh¯arata.

---

<!-- page 138 -->

126 A.S. Prasad and S. Rao
Thus, beyond the general and computational aspects, we believe this work also has probative value in the context of this particular textual controversy.
The rest of the paper is structured as follows. Section 2 presents the similar work in other domains like bioinformatics. Section 3 describes the problem and the challenges. Section 4 presents the method to perform sorting of a Sanskrit corpus. Section 5 presents the exact matching method. Section 6 presents the approximate matching method. Section 7 presents some conclusions and suggestions for further work.
2 Related Work
Citation matching is one of the active areas of research. Citation matching is used for identifying authors of scientiﬁc papers [9] [5], knowledge discovery, etc. Citation matching is currently limited to scientiﬁc literature like research papers.
Sorting is performed to reduce the search space when we use the exact matching method. There are classical algorithms for performing sorting like heap sort, merge sort, etc.4 There is an x86 assembly language program [16] which sorts Sanskrit texts. Mahoney [6] implements sorting using Perl. Neither [16] nor [6] speciﬁes the maximum text size that these programs can handle. Also as far as our knowledge goes, nobody has sorted the entire Maha¯bh¯arata text. Gale and Church [3] describe a method for aligning sentences based on a sample statistical model of character length. This method is used by Csernel and Patte [2] for performing comparisons between Sanskrit manuscripts.
Local alignment is one of the sequence alignment techniques used in bioinformatics to ﬁnd the similarity regions between two DNA, RNA or protein sequences of unequal length. The Smith-Waterman algorithm [14] is used widely for performing local alignment. The Smith-Waterman algorithm is more accurate but computationally intensive as compared to other methods like BLAST. The Smith-Waterman-Gotoh algorithm [4] is an extension of the Smith-Waterman algorithm.
Symmetric [17] is an open source similarity measurement library implemented in Java. Basic algorithms like edit distance and Smith-Waterman-Gotoh [4] are implemented in this library, which we have used.
3 Problem Deﬁnition
Citation matching is an unexplored area in natural language texts, especially in Sanskrit literature. Table 1 shows examples of sources and citations.
Citation matching in Sanskrit literature is complex compared to the same problem with scientiﬁc literature because of the following reasons.
4 These classical algorithms can be used to sort the Sanskrit corpus by modifying the comparison function. There is no need for modiﬁcation in English corpora but we cannot apply this method to Sanskrit corpora because the order of the syllables in
the Sanskrit Ú ­Ñ Ð is diﬀerent from the Roman alphabet.

---

<!-- page 139 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 127

Table 1. Source and Citation Examples

Citation

Source

Ñ ÒÕ ØÒÑ éØ

Ñ ÒÕ ØÒ éØ

ÐÓ Ú Ö Ö Ó

ÐÓ Ú Ö Ö Ó

Ý ØÑÐ ÐÓÑ Õ­

Ý ØÑÐ ÖÓÑ Õ­

ì Ö ÇÑ Ö Ô Ô Ú¸ ì Ö ÇÑ Ö Ô Ô Ú¸

(i) The Sanskrit alphabetical system is entirely diﬀerent from that of the English language. In Sanskrit each letter is a combination of vowel and consonant like + = , but this kind of combination is not present in English. Modern English does not support ligatures whereas Sanskrit supports ligatures like
+ =

---

<!-- page 140 -->

. (ii) aInlsmo aarneyccaasseess,otfhdeiﬀcoerrepnucsehsadsupe¯at.toha¯snatnadrhais-vwicitchherdeasp(eec.tg.t,oØtÒheÑteéxtØ,ÑanadntdhØerÒe
éØÑ).
(iii) The size of the corpus may be very large (the ASCII text [13] of the Mah¯abh¯arata being about 8MB in size). It is challenging to handle these kinds of large data sets.
(iv) The conversion of Sanskrit texts into machine readable formats is prone to error as it involves human interaction. There is a high probability of error in the machine readable format which in turn aﬀects the result signiﬁcantly.
For both methods—exact matching and approximate matching—we use the Mah¯abh¯arata-T¯atparyanirn.aya as the base text where citations may exist, and the Maha¯bh¯arata [13] as the source text or corpus where to look for citations. The Mah¯abha¯rata and Mah¯abh¯arata-Ta¯tparyanirn.aya are both encoded in the ASCII-based Harvard-Kyoto format to evaluate these methods. The HarvardKyoto format is one of the common encoding schemes used to make Sanskrit texts machine readable.

4 Sorting

Exact matching compares each line of the source corpus with each citation. The

number of comparisons is directly proportional to both corpus size and citations.

If there are m lines of source corpus and n citations, then the total number of

comparisons needed in exact matching is m×n. Consider a corpus like the BORI

Mah¯abh¯arata which has around 80000 verses or 160000 lines, and a text set with

100 citations; then the total number of comparisons are 16 × 106.

One approach to reduce the number of comparisons is to sort the source cor-

pus. Sorting reduces the search space drastically. Consider a citation

Ø¹Ý

 Ø ¹ ¦ Ñ Ô¡ Ý­ Ú ØÑ. It is enough to compare with the Maha¯bh¯arata

hemistichs starting with , and we can ignore the rest of the verses. In this way,

sorting helps reduce the search space.

---

<!-- page 141 -->

128 A.S. Prasad and S. Rao

Table 2. Input and Output: Unix Sorting in Roman Order

Input

Output

Ì ÚÖ ÎÒ £Ö ÑÑ Ô¡ Ú­ ÔØ Ñ ¸ ØÚ × Ù ÕØ ÝÓ­ Ò Ý ­Ø ¸
ÒÑ£ Ý ÙÚ  ´Ú éÑ ì£ Ý ÀÝÇ

ØÚ × Ù ÕØ ÝÓ­ Ò Ý ­Ø ¸ ´Ú éÑ ì£ Ý ÀÝÇ ÒÑ£ Ý ÙÚ  Ì ÚÖ ÎÒ £Ö ÑÑ Ô¡ Ú­ ÔØ Ñ ¸

Sorting is not straight-forward in Sanskrit texts compared to English. Even the classical sorting tools like the Unix sort fail to sort Sanskrit text. Table 2 shows the input and output of the sort command in Unix, which sorts in Roman, rather than Sanskrit, alphabetical order.
In Sanskrit each letter is a combination of vowel and consonant. So the comparison function should look at both vowel and consonant during comparison of words.
Consider an example of and . should come before because = + and = + Á. Even though both have in common, they diﬀer in their vowels, and comes before Á in the Sanskrit alphabetical system. There are a large number of classical algorithms like quicksort, merge sort, heapsort, etc., to perform sorting [1]. Given that in our case the size of data involved is huge, quicksort, heapsort and merge sort are the candidate algorithms for performing sorting, because all these have log-linear time complexity. We prefer heapsort over the other two algorithms for the following reasons.
(i) The time complexity of heapsort in the worst case is O(n log n) whereas the time complexity of quicksort is O(n2).
(ii) The space complexity of heapsort is Θ(1) but the space complexity of merge sort is Θ(n).
Each character in the encoding scheme is assigned a positive integer corresponding to the position of the Sanskrit character it represents in the Sanskrit alphabetical system. In English, the ASCII values of the characters are implicitly used in the comparison, but this is not appropriate in Sanskrit. There should be a way of identifying which character appears before which other character. Hence we assign positive integers to the characters.
Let us consider an example. In the Harvard-Kyoto scheme, A represents and u represents Ù. According to the Sanskrit alphabetical system, the positions of and Ù in the Ú ­Ñ Ð are 2 and 5 respectively.
The pseudocode for the modiﬁed comparison function of heap sort is as given in Algorithm 1. CharV al(k) is the function which returns the positive number assigned to an encoded character k.
Let Si, Sj be two strings with length i and j respectively. In Algorithm 1, line 1 and line 2 check whether one of two strings is a substring of the other. Substrings appear before the base string in a lexicographic ordering. If two strings are not substrings, then the algorithm compares each character

---

<!-- page 142 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 129

input : Two strings Si, Sj of size i and j respectively output: An Integer

if Substring(Si, Sj) then return 1;

if Substring(Si, Sj) then return -1;

for k ← 0 to i do

if (Si[k] = Sj[k]) then continue;

if ( charVal(Sj [k]) > charVal(Si[k]) then return (charVal(Sj [k]) -

charVal(Si [k]));

else return(charVal (Si[k]) - charVal (Sj[k]));

end

return 0 ;

Algorithm 1. Comparison Subroutine

of the strings at position k. The for loop in line 3 compares the character at position k in both the strings. If the characters are not equal, then the comparison function returns the diﬀerence of the values assigned to two characters.
Table 3 shows a partial list of the sorted Mah¯abha¯rata.

Table 3. Partial Listing of the Sorted Mah¯abha¯rata

Line

Reference

Ñ­ Ó

Ú ¦Ø ¹Ì ÚÖ Ò£Ø£Ö Ò ¸ (03.033.003)

Ë ¹Ý Ú ¹Ý ß Ó´ Ö ¢ Ø ´ÑÒ¸

(13.024.053)

Ë Ó ÒÖ ÖÅ Ó Ð℄Ú ÖÓ Ø£ ¦ Ý¸ (03.080.032)

Ë Ó í Ø ­æ ì Ó ÖØÕ­

(13.024.030)

Ë Ý¦Ø  Ñ Ø ¢ ¸ ×ÑÒí¦Ø Ô Ý¸ (09.007.003) ËÑÕ¸ ËÑÕ Ø­ Ó éØ× Ø ×¸ (03.211.020)

5 Exact Matching
Exact matching is based on the idea of ﬁnding a precise character-by-character match between pattern and text. This method ﬁnds the citations which are exactly the same as those in the corpus.
The notations used in the pseudocode are:
(i) T : Input Sanskrit corpus. (ii) m: Size of the corpus T . (iii) C: Set of input citations. (iv) n: Cardinality of the citation set C. (v) R: The set of citations present in T —clearly, R ⊆ C.
The pseudocode for this method is presented in Algorithm 2. The complexity of this algorithm is O(mn). In Algorithm 2, each line of the source text is compared with each citation
in the citation set. If both match exactly (all characters are identical), then the

---

<!-- page 143 -->

130 A.S. Prasad and S. Rao
input : Sorted corpora T and set of citation C of size m and n respectively
Result: Set of citations R found in the corpus R←∅; for every line of corpus text T i in T do
for every citation Cj in C do if (T i = Cj ) then R ← R ∪ Cj
end end
Algorithm 2. Exact Matching
citation is included in the result set R; otherwise it is discarded. The source corpus is sorted using heap sort to reduce the search space.
The following table shows the partial result of the exact matching method.

Table 4. Partial Result Set for Exact Matching

Citation

Source

¹ÑÒ Ý £ Ñ×£Ò ´Ú Ý (2.160) ¹ÑÒ Ý £ Ñ×£Ò ´Ú Ý (05.075.018)

ÐÓ Ú Ö Ö Ó (30.36)

ÐÓ Ú Ö Ö Ó (05.130.015) (12.070.006)

Ø  Ø £ÚÒ (1.108)

Ø  Ø £ÚÒ (06.033.054)

This method ﬁnds those citations which are exactly the same in the text and in the source. Consider now the citation:
Ú Ò ¦Ø Ñ Ñ¡ Ñ ÒÕ ØÒÑ éØ and the source text Ú Ò ¦Ø Ñ Ñ¡ Ñ ÒÕ ØÒ éØ. Only the words ØÒÑ éØ and ØÒ éØ diﬀer in this case. This is an example of sandhi-viccheda, occurring perhaps due to scribal or editorial choice. Exact matching does not capture these kinds of citations.
Exact matching is the ﬁrst method that comes to our mind when we think of citation matching. Exact matching fails to consider similarity when citations are searched for. In Sanskrit literature, we have pa¯.tha¯ntaras of the same corpus occurring in diﬀerent sources. Most of the times these corpora diﬀer due to sandhi-viccheda also. Therefore, exact matching is not an ideal method when there are p¯a.tha¯ntara and sandhi-viccheda.
6 Approximate Matching
Sequence alignment is a technique from bioinformatics of arranging nucleotide or protein sequences to identify the similarity regions. This identiﬁcation of these similar regions in an important problem in molecular sequence analysis [14].
Global alignment and local alignment are the two types of sequence alignment. Global alignment is applied on sequences of almost equal length. Local alignment is applied on sequences with unequal length.

---

<!-- page 144 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 131
The Smith-Waterman algorithm, based on dynamic programming, is used in local alignment.
The lengths of citation and source text are unequal in the present domain of citation matching in Sanskrit texts. Hence local alignment is more appropriate than global alignment. The approximate method used by us is based on the Smith-Waterman-Gotoh algorithm, with each line of source and citation is considered as a sequence. The comparison between text and citation can be reduced to ﬁnding the maximum similarity score between two sequences. The SmithWaterman-Gotoh algorithm computes the similarity score of text and citation. Only the citations with scores which are equal or greater than some approximation cutoﬀ are included in the result set.

6.1 Smith-Waterman-Gotoh Algorithm
Consider two sequences A = a1a2 . . . am and B = b1b2 . . . bn. The SmithWaterman algorithm constructs a matrix H, where each cell hij in H is computed as follows [14]. It builds the matrix H based on the set of equations given below.
∀ 1 ≤ i ≤ n, 1 ≤ j ≤ m

⎧ ⎨

hi−1,j−1

+

s(ai,

bj )

hij = max max k≥1{hi−k,j − W k}

⎩ max l≥1{hi,j−l − W l}

if ai and bj are associated if a is at the end of deletion of length k if b is at the end of deletion of length l

hk0 = h0l = 0 ∀0 ≤ k ≤ n and 0 ≤ l ≤ m s(a, b) = Similarity between a and b. W k = Weight assigned to deletion of
length k. s(a, b) and W k are chosen on an a priori statistical basis.

(i) hi−1,j−1 + s(ai, bj) is the similarity, if ai and bj are associated. (ii) hi−k,j − W k is the similarity, if ai is at the end of a deletion of length k. (iii) hi,j−l − W l is the similarity, if bj is at the end of a deletion of length k. (iv) Zero is included to prevent negative similarity. Occurrence of zero indicates
absence of similarity between ai and bj.
The procedure to ﬁnd the the optimal local alignment is:

(i) Locate the highest similarity score in the matrix H. (ii) Go backwards from this cell until a cell with zero value is encountered. (iii) The path from the cell with maximum score to one with zero value gives
the maximum sequence.

Consider the biological sequences TACTAG and ACCTAG with s(match) = 2, s(mismatch) = W k = W l = −1.

---

<!-- page 145 -->

132 A.S. Prasad and S. Rao

The corresponding similarity matrix is

−ACCT AG

−⎛ 0 0 0 0 0 0 0 ⎞

T⎜0 1 1 0 2 1 0⎟

A

⎜ ⎜

0

2

1

0

1

4

3

⎟ ⎟

C

⎜ ⎜

0

1

4

3

2

3

2

⎟ ⎟

T

⎜ ⎜

0

0

3

2

5

4

3

⎟ ⎟

A

⎜ ⎝

0

2

2

2

4

7

6

⎟ ⎠

G 0111369

The optimal local alignment in the above example is -CTAG. However, in this paper we are not concerned about the optimal local alignment. Our interest is only in the maximum similarity score. The Smith-Waterman algorithm is computationally intensive compared to other methods like BLAST. The Smith-Waterman-Gotoh algorithm is an extension of the Smith-Waterman algorithm which uses aﬃne gap penalty [4] to reduce the computational overhead. We have redeﬁned the parameters costfunction, windowsize and the limits of gapfunction of the Smith-Waterman-Gotoh algorithm for performing citation matching. The new windowsize and gapfunction are as follows. We use windowsize ← 100 and 0 ≤ gapfunction ≤ 5. Table 5 shows the scores associated with diﬀerent matches. There are seven groups of characters. Let char1 and char2 be two characters in String1 and String2 at position k respectively. char1 and char2 are considered as being approximate match if char1 and char2 are any two characters in the same group. Table 6 shows these seven groups.

Table 5. Scores Associated With Diﬀerent Types of Matches

Matching Type Score

Exact

+5

Approximate +3

Mismatch

-3

Table 6. Groups and Characters Present in the Groups

Group Characters

I

d,t

II g,j

III l,r

IV m,n

V b,p,v

VI a,e,i,o,u

VII , and .

---

<!-- page 146 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 133
The Smith − Waterman − Gotoh − Distance(string1 , string2 ) function takes two strings string1 and string2 as arguments. It builds the similarity matrix between string1 and string2 similar to the above example with redeﬁned parameters, and ﬁnally returns the maximum similarity score in the matrix.

6.2 Algorithm
Algorithm 3 uses the notation cutoﬀ in addition to the notations used by Algorithm 2. cutoﬀ is deﬁned as the similarity score cutoﬀ.
The pseudocode for the approximate matching is presented below.
input : Corpus text T and set of citation C of size m and n respectively. cutoﬀ score cutoﬀ
Result: Set of citations R which are greater than cutoﬀ found in the corpus
R ← ∅; for every line of corpus T i in T do
for every citation Cj in C do if Smith-Waterman-Gotoh-Distance(T i, Cj) > cutoﬀ then R ← R ∪ Cj
end end
Algorithm 3. Approximate Matching
In Algorithm 3, Line 4 computes the Smith-Waterman-Gotoh distance between a citation and a line of text in the source corpus. The citation is included in the result set only if the Smith-Waterman-Gotoh distance is greater than the cutoﬀ . This step is repeated for every line of text in the corpos.
Table 7 shows the partial result set of this method.

Table 7. Partial Result Set for Approximate Matching

Citation

Source

×Ñ¹Ø Ø Ú Ö ¸ × × (22.285) ×Ñ¦Ø Ø Ú Ö ¸ × × (03.152.019)

ÑÓ ÝÓ­ Ò ¦Ø (21.350)

ÝÓ­ Ò ¦Ø (02.068.026)

Ý ØÑÐ ÐÓÑ Õ­ (27.66)

Ý ØÑÐ ÖÓÑ Õ­ (06.043.011)

ì Ö ÇÑ Ö Ô Ô Ú¸ (28.162) ì Ö ÇÑ Ö Ô Ô Ú¸ (05.057.001)

ÐÚ Ò × Ø¸ ¡ Ö¹ØÔ¹Ú (22.283) ÐÚ Ò × Ø¸ ¡ Ö× ØÖ¹Ú (03.152.017)

The exact matching method does not include ¡ Ö× ØÖ¹Ú and ÇÑ Ö

Ô

in the result set because of p¯a.tha¯ntara and sandhi-viccheda respectively. This shows that approximate method can handle p¯a.tha¯ntara and sandhi-viccheda.
If cutoﬀ ← 1 then approximate matching behaves exactly as the exact match-

ing method. This of course is tantamount to saying that if the similarity score

---

<!-- page 147 -->

134 A.S. Prasad and S. Rao
cutoﬀ is 1, then only exact matches are considered similar, so the approximate matching results are identical to the exact matching results.
This method takes closeness or similarity between text and citation into account when searching the citations. This is the strength of this method. However this method is computationally intensive as compared to exact matching and usually also requires manual review of results.
We performed the experiment with diﬀerent values of cutoﬀ . Initially we started with cutoﬀ = 0 .9 . In this case the number of valid results is 87 and the rest of the results are false positives or very small matches like ÙÑ ÙÚ . We repeated the same experiment with cutoﬀ = 0 .8 . In this case the number of valid results are 103 and there was also an increase in the count of false positives.
The similarity score is a measure of how one string can be transformed into another given string. If one of the strings is a substring of the other, then naturally the similarity score is high. This is the main reason for the rise in false positives when cutoﬀ is lowered. The number of false positives is inversely proportional to cutoﬀ .
7 Conclusions
Citation matching is one the active areas in research but unfortunately it is limited to scientiﬁc literature. We have presented approximate matching based on local alignment in this paper. The known limitations of exact matching provide the inspiration for approximate matching.
We can easily see that the results obtained with approximate matching are far superior to those with exact matching. The exact matching method is unable to identify even some well-known verses like Ú Ò ¦Ø Ñ Ñ¡ Ñ ÒÕ ØÒ éØÑ because of sandhi-viccheda, but the approximate matching method can.
Heap sort is the best sorting method, preferable to other methods like quick sort, merge sort, etc., for sorting Sanskrit corpora, due to its worst-case log-linear time complexity and constant space complexity.
Approximate matching can be extended to other Indic languages like Kannada. We can use this method as long as the encoding schemes used by both source and citation is consistent.
Citation matching is used in content analysis. We can extend this to Sanskrit literature using the approximate matching method. It is noteworthy that many classical authors and commentators in Sanskrit quote earlier texts implicitly, without indicating their sources or indicating that the words/sentences/verses used are not their own. To discover these hidden citations, given the prevalence of pa¯.tha¯ntaras and sandhi-vicchedas, our approach can be used.
The approximate matching method can be easily extended to detect plagiarism in literature because the Smith-Waterman algorithm is used elsewhere [15] to detect plagiarism. However, in our opinion, plagiarism is a modern concept and not likely to apply signiﬁcantly in the case of classical Sanskrit texts. However, critical editions of many texts like the Mah¯abh¯arata need to be prepared and revised, and in such cases variant readings recorded by long-ago authors and

---

<!-- page 148 -->

Citation Matching in Sanskrit Corpora Using Local Alignment 135
commentators may be utilized in coming up with a text that, while not certain to be the same as a putative ur -text, is nonetheless “the text that best explains all the extant documents” [11]. Approximate matching has a role in this, and local alignment is thus an important tool.
Acknowledgements
The work of S. Rao was supported in part by the Centre for Artiﬁcial Intelligence and Robotics, DRDO, under contract CAIR/CARS-06/CAIR-23/0910187/0910/170. His work was also partially supported by a UGSI Travel and Research Grant from Unisys.
References
1. Cormen, T.H., Leiserson, C.E., Rivest, R.L., Stein, C.: Introduction to Algorithms, 2nd edn. MIT Press/McGraw-Hill (2001)
2. Csernel, M., Patte, F.: Critical edition of Sanskrit texts. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 358–379. Springer, Heidelberg (2009)
3. Gale, W.A., Church, K.W.: A program for aligning sentences in bilingual corpora. In: Meeting of the Association for Computational Linguistics, pp. 177–184 (1991)
4. Gotoh, O.: An improved algorithm for matching biological sequences. Journal of Molecular Biology 162(3), 705–708 (1982)
5. Lawrence, S., Bollacker, K., Giles, L.C.: Autonomous citation matching. In: Etzioni, O. (ed.) Proceedings of the Third International Conference on Autonomous Agents. ACM Press, New York (1999)
6. Mahoney, R.: Arbitrary lexicographic sorting: Sort UTF-8 encoded Romanised Sanskrit, http://www.indica-et-buddhica.org/sections/repositorium-preview/ materials/software/sort-utf8-sanskrit
7. Mesquita, R.: Madhva’s Unknown Literary Sources: Some Observations. Aditya Prakashan, New Delhi (2000)
8. Mesquita, R.: Madhva’s Quotes from the Puranas and the Mahabharata: An Analytical Compilation of Untraceable Source-Quotations in Madhva’s Works along with Footnotes. Aditya Prakashan, New Delhi (January 2008)
9. Pasula, H., Marthi, B., Milch, B., Russell, S., Shpitser, I.: Identity uncertainty and citation matching (2002)
10. Rao, S., Sharma, B.N.K.: Madhva’s unknown sources: A review. Asiatische StudienE´tudes Asiatiques LVII 1, 181–194 (2003)
11. Robinson, P.: The one text and the many texts. Literary and Linguistic Computing 15(1), 5–14 (2000)
12. Sharma, B.N.K.: History of the Dvaita School of Vedanta and its Literature, 3rd edn. Motilal Banarsidass, Delhi (2000)
13. Smith, J.: The Mahabharata (2009), http://bombay.indology.info/mahabharata/statement.html
14. Smith, T.F., Waterman, M.S.: Identiﬁcation of common molecular subsequences. Journal of Molecular Biology 147(1), 195–197 (1981)

---

<!-- page 149 -->

136 A.S. Prasad and S. Rao
15. Su, Z., Ahn, B.R., Eom, K.Y., Kang, M.K., Kim, J.P., Kim, M.K.: Plagiarism detection using the Levenshtein Distance and Smith-Waterman algorithm. In: International Conference on Innovative Computing, Information and Control. IEEE Computer Society, Los Alamitos (2008)
16. Dudenskt, http://www.sanskritweb.net/koko/dudenskt.pdf 17. Chapman, S.: SimMetrics - open source Similarity Measure Library,
http://www.dcs.shef.ac.uk/~ sam/simmetrics.html

---

<!-- page 150 -->

RDBMS Based Lexical Resource for Indian Heritage: The Case of Mah¯abh¯arata
Diwakar Mani
Centre of Development of Advance Computing, Pune, India diwakarmani@gmail.com
http://sanskrit.jnu.ac.in/mb/index.jsp
Abstract. The paper describes a lexical resource in the form of a relational database based indexing system for Sanskrit documents Mah¯abha¯rata (MBh) as an example. The system is available online on http://sanskrit.jnu.ac.in/mb with input and output in Devan¯agar¯ı Unicode, using technologies such as RDBMS and Java Servlet. The system works as an interactive and multi-dimensional indexing system with search facility for MBh and has potentials for use as a generic system for all Sanskrit texts of similar structure. Currently, the system allows three types of searching facilities- ‘Direct Search’, ‘Alphabetical Search’ and ‘Search by Classes’. The input triggers an indexing process by which a temporary index is created for the search string, and then clicking on any indexed word displays the details for that word and also a facility to search that word in some other online lexical resources.
Keywords: Maha¯bh¯arata, Indexing, Mah¯abh¯arata Search Engine, Online Indexing, Mah¯abh¯arata Indexing System, Mah¯abh¯arata Indexer.
1 Introduction
MBh, the great epic of India ascribed to Veda Vya¯sa, can be un-hesitatingly given the honour of being the cultural encyclopaedia of India. It is the story of a great war that ended one age and began another. The story has been passed down to us in a classical canon of Sanskrit verses - some 90,192 stanzas (including additional Harivam˙ ´sa) long, or some 1.8 million words in total (among the longest epic poems worldwide) divided in 18 parvas and 97 upaparvas which are again divided into 1995 chapters.1 The MBh is about 12 times the length of the Bible and 8 times longer than the Iliad and the Odyssey. The work therefore holds a signiﬁcant place in the cultural history of India. An overview of structure of the MBh is given below (Table 1).
2 Why Is Indexing System Necessary for MBh?
The MBh extols its greatness itself in the following words: yadiha¯sti tadanyatra yanneha¯sti na tat kvacit. The saying vy¯asocchi.s.tam. jagatsarvam also stresses 1 The structure of Maha¯bh¯arata is based on BORI’s Critical Edition of Mah¯abh¯arata.
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 137–149, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 151 -->

138 D. Mani

Table 1. Structure of Maha¯bh¯arata (According to the BORI’s critical edition)

Parvan A¯ diparva

Sub-parvan A¯ khya¯na Adhya¯ya S´lokas

19

09

225

07197

Sabha¯parva

09

00

072

02390

A¯ ran. yakaparva

16

00

299

10338

Vira¯t.aparva

04

00

067

01824

Udyogaparva

12

05

197

06063

Bh¯ıs. maparva Dron. aparva Karn. aparva S´alyaparva

04

00

117

05406

08

00

173

08192

01

00

069

03871

04

00

064

03315

Sauptikaparva

02

00

018

00772

Str¯ıparva

03

00

027

00730

S´a¯ntiparva

03

00

353

12902

Anu´s¯asanaparva

02

22

154

06439

A´svamedhikaparva

02

A¯ ´sramav¯asikaparva

03

00

096

02743

00

047

01062

Mausalaparva

01

00

009

00273

Maha¯prastha¯nikaparva 01

00

003

00106

Svarga¯rohan. aparva

01

00

005

00194

Total (in 18 parvans) 95

36

1995 73,817

Harivam. ´sa (Khilaparva) 02

—

—

16,375

Total (including khila) 97

36

1995 90,192

this point. MBh is neither a history in the modern sense of the term, nor a chronicle. But it stands in incomparable isolation, defying all deﬁnitions. It is a veritable encyclopaedia comprising heterogeneous material from all branches of knowledge. Taking the core-story of the feud between two branches of a royal family and the circumstances leading to a catastrophic war, several branches of knowledge including philosophy, law, ethics, statecraft, warfare, history and ethnology are embodied in its structure. The MBh is a comment on the human condition with all its richness, complexity and subtlety. The MBh is the source of many compositions like- abhijn˜¯aana´s¯akuntalam of K¯alid¯asa, nais. adh¯ıya-caritam of ´sr¯ıhars.a etc. It is the text that is most sought for in order to enrich cultural, social and any other type of knowledge about Indian civilization.
While on the one hand, the text is very important, on the other, it is so huge that it becomes virtually very diﬃcult and time consuming for someone to search a speciﬁc keyword in it manually. The searching process combines the beneﬁt of search and extraction. The indices thus prepared will constitute a separate text in itself due to the size of the MBh and will be of tremendous use to the researchers and users.

2.1 Uses of the Indexing System
The indexing system of Sanskrit documents can be used in various NLP applications like building Sanskrit WordNet, dictionaries, Sanskrit- Indian Language

---

<!-- page 152 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 139
Machine Translation System (MTS) etc. Unique words are a basic need of a WordNet and a dictionary. Automatic indexing and sorting is a good tool to extract unique words from a given text. Though, there is not a direct use of indexing system in machine translation but can be helpful in generating a context lexicon (a lexicon with the entries including the uncommon words frequently occurring in the context of use of that particular word, which, later assigning the sense may be used as a lexicon for word sense disambiguation). This work, besides being an essential resource in NL system of Sanskrit, may also be useful for authentic and referential knowledge about Indian heritage. The system can also be very useful for the researches of historical, socio-political and geographical researches by providing the facts from the huge text which cannot be easily read.
3 Previous Work
The history of textual indexing is very rich in India. S´aunaka, a great scholar of Vedas, made a Vedic index named sarva¯nukraman.¯ı. “A Word Concordance of Maha¯bha¯rata” is a research tool supplying well alphabetized and grammatically analyzed record of each and every word-unit occurring in the text of diﬀerent Parvans of MBh. It is a gigantic collaboration project at Sanskrit evam Pra¯cya Vidya¯sam. stha¯na, Kurukshetra University. Six parts of the same have already been published. Seventh part is in press and press copies of next two parts are ready for publication and the tenth part is near completion. This work is based on BORI’s critical edition of MBh.
A western scholar S. S¨orensen created “An Index to the Names in the Maha¯bha¯rata” with short explanations and a concordance to the Bombay and Calcutta editions and P. C. Roy’s translation which was published from Williams and Norgate, London (1904-1925) and reprinted from Motilal Banarasidass, Delhi (1963). Here, all proper names are given with a complete listing of the places of their occurrence. It also contains, under the names of the 100 sub-parvans, very brief chapter by chapter summaries of the contents of the sub-parvans.
For the emerging R‘&’D area of Sanskrit informatics, it is necessary to make indices available online. Unfortunately, the task of electronic indices for Indian heritage has not attracted required attention of computational linguists. Some eﬀorts made in this area, directly and indirectly, are listed here:
1. The important work in the area of Online Indexing of Indian heritage has been done in University of Go¨ttingen, Germany. It includes a word indexing of complete MBh in Roman transliteration. It is accessible at http://www.sub.uni-goettingen.de/ebene_1/fiindolo/gretil/ 1_sanskr/2_epic/mbh/sas/mahabharata.html
2. The Indology Department, University of Wuerzburg, Germany has created “Multimedia Database to Sanskrit drama” which is mainly focused on word indexing of Bha¯sa’s drama but also includes mudra¯ra¯ks. asa of Vis.a¯khadatta. It is available online at http://www.indologie.uni-wuerzburg.de/bhasa/index.html

---

<!-- page 153 -->

140 D. Mani
3. Linguistics Research Centre of The University of Texas has an online .rgveda in Romanized transliteration format. This online text is based on the Barend A. Van Nooten and Gary B. Holland’s electronic version. This can be seen at- http://www.utexas.edu/cola/centers/lrc/RV/
4. A project on the complete text of the Critical Edition of Maha¯bha¯rata begun by J. A. B. Van Buitenen and now continued under the chief editorship of James Fitzgerald of Brown University. Van Buitenen (translated the ﬁrst three volumes, comprising the ﬁrst ﬁve major parvas of the epic) and Fitzgerald (translated volume seven, comprising str¯ıparva and the ﬁrst half of ´sa¯ntiparva) have translated the BORI version of MBh text into modern English prose. At present, ten volumes are projected, and four volumes have been published by the University of Chicago Press.
5. Barend A. Van Nooten, an emeritus Professor of Sanskrit at the University of California at Berkeley, has written “The Maha¯bh¯arata Attributed to Kr. .sn. a Dvaip¯ayana Vy¯asa” which was publish in 1971 by Twayne Publishers, New York. This work provides a well informed but non-technical overview of the MBh. It includes a detailed, book-by-book summary of the story, discussions of the religious, philosophical, and ethical components of the text, and an outline of the MBh’s inﬂuence since the eighteenth century.
6. “The Sanskrit Epics” - a comprehensive guide to the Maha¯bha¯rata and the R¯am¯ayan. a is written by Professor John Brockington (Leiden: Brill, 1998), former Head of the Department of Sanskrit at the University of Edinburgh and General Secretary of the World Sanskrit Association, gives an up to date, general survey of the history of the two Sanskrit epics and the scholarship upon them.
7. Paradigmatic index on ra¯mop¯akhya¯na of MBh is the work of Peter Scharf and Malcolm Hyman, which gives the Devana¯gar¯ı text, Roman transliteration, analysis of sandhi, inﬂection, glossary, prose paraphrases, syntactic and cultural notes, and English translation. It was described by Scharf (2001) at the international conference on Mah¯abha¯rata conference in Montreal (18-20 May 2001) and published in “The Maha¯bh¯arata: What is not here is nowhere else” by Munshiram Manoharlal, Delhi, 2005 (T.S. Rukmani (ed.)). It is available at http://sanskritlibrary.org
8. Electronic text of the Critical Edition of the MBh is available in downloadable text format of several commonly-used encodings, such as- Unicode Devanagri, Unicode Roman, ISCII, ASCII, Norman etc. at the home page of Professor John Smith, Cambridge University. Smith’s revision is based on Prof. Muneo Tokunaga’s ﬁrst digital and searchable version of the MBh text. It is available at
http://bombay.indology.info/mahabharata/statement.html 9. Maharshi University of Management has created PDF ﬁles of all 18 Parvas
of Maha¯bha¯rata. The site is
http://is1.mum.edu/vedicreserve//itihas.htm

---

<!-- page 154 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 141
10. Kishori Mohan Ganguli has translated the MBh in English which is available at- http://www.sacred-texts.com/hin/maha/
11. Aryabharati International Society for Hindu Ved Vignan & Atomic Research has created pages for complete MBh (in Unicode Devanagari & Roman transliteration format) on http://www.aryabharati.org/mahabharat/index.asp. This text has been cross-referenced with Kishori Mohan Ganguli’s English translation on a book-by-book basis.
12. http://sanskritdocuments.org/ has created online versions of Sanskrit documents including Vedas, MBh and many more in ITX, HTML, PS, XDVNG, GIF and PDF format.
13. A project to translate the full epic into English prose began to appear in 2005 from the Clay Sanskrit Library, co-published by New York University Press and JJC Foundation. The translation is based not on the Critical Edition but on the version known to the commentator N¯ılakan. t.ha. Currently sabh¯a, ¯aran. yaka, vira¯.ta, udyoga, bh¯ı.sma, dron. a, karn. a, ´salya, sauptika, str¯ı, and ´sa¯ntiparva are available. It is accessible athttp://www.claysanskritlibrary.org/
3.1 Distinction of Present System over Previous Ones
“Mahabharata Online” at University of Goettingen provides two services, book and chapter (parva and adhya¯ya)-wise browsing, and alphabetically sorted index, each entry linking to the part of the text where it occurs. Our system is a dynamic search indexer which provides three kinds of search facility - string input search, search by listing of words by ﬁrst letter, and browsing the word by parva>upaparva>adhya¯ya and a¯khya¯na. The search result displays information of the entry with detailed extracted information of the verse of its occurrence, including number and name of parva, upaparva, adhya¯ya, ´sloka number and ¯akhya¯na (if available). One more diﬀerence between the two is in their output format. The previous displays the text in Roman IAST scheme and later uses Devanagari Unicode for input and output.
4 Methodology for the MBh Indexer
The MBh, an encyclopedia of Indian civilization, has always remained attractive not only to Indian scholars, but also to the western. The MBh being a popular epic has several versions. The edition selected for this work is the critical edition of Maha¯bha¯rata, critically edited by V.S. Sukthankar and others and published by Bhandarkar Oriental Research Institute (from 1919 to 1966). It has been digitized by Prof. John Smith based on the work of Muneo Tokunaga in Unicode Devana¯gar¯ı Text format.
To provide more comprehensive search, the text is segmented according to Pa¯n. inian sandhi rules. The tokens so obtained are basically padas (word-forms). After this, the text has been adapted to the database system. The original and

---

<!-- page 155 -->

142 D. Mani segmented text has been stored in database tables. The other information of the structure of the text has been stored in diﬀerent tables and those are connected with each other. The connections of the table complete the reference of the searched query and connect the entire data with other relations. The database has ﬁve tables having the information of parva, upaparva, adhya¯ya, a¯khya¯na and the ´slokas respectively.
The structure for database storage is as follows: Table 2. The ‘shloka’ table
Table 3. The ‘adhyaya’ table

---

<!-- page 156 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 143 Table 4. The ‘akhyana’ table
Table 5. The ‘upaparva’ table
Table 6. The ‘parva’ table

5 Development of the MBh Indexer
A dynamic search engine-cum-indexer has been developed which is built in the front-end of Apache Tomcat Web server using JSP and Java servlets. It has its data in MS-SQL Server 2005 with Unicode. For connecting the front-end to the database server the MS-JDBC connectivity has been used. The following model describes the multi-tiered architecture of the MBh indexing system:

5.1 Process Flow of the System

There are three ways to give input to the system e.g. Direct Search, Alphabet search and Search by the structure of the text in Devana¯gar¯ı UTF-8 format.

Step I: Preprocessing. Preprocessing a text mainly consists of transformation

of raw data required to facilitate further cartographic processing. For example -

preprocessor will remove any non Devana¯gar¯ı characters, punctuations that may

have been inadvertently introduced by the user like “@es” in

and

other similar cases.

---

<!-- page 157 -->

144 D. Mani
Fig. 1. Multi-tiered architecture of the MBh indexing system Step II: MBh Indexer and Database. At this step, the indexer makes an indexed list of exact and partially matching words. Getting the query as an input, the indexer, after a light preprocessing, sends it to the database. If the word has its occurrence in the database, the system gives the output.
Fig. 2. Process ﬂow of the system Step III: Output level-1. At this level, the indexer gives all the occurrences of the searched query with its numerical reference in a hyperlinked mode. Step IV: Output level -2. Clicking any hyperlinked word, system shows its original place in the ´sloka and also gives its full reference in the text. It also asks for further information from other online lexical resources.

---

<!-- page 158 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 145 Step V: Output - ﬁnal level. Here, the indexer gives a list of online lexical resources and also gives the facility to do morphological analysis of the query with the help of POS Tagger2 and Subanta Analyzer.3 5.2 Front-End of the MBh Indexer The front-end of the system is developed in utf-8 enabled Java Server Pages (JSP) and HTML. The front-end of the software enables the user to interact with the indexing system with the help of Apache Tomcat web-server. The JSP technology helps to create web based applications by combining Java code with HTML. The web server runs the Java code and displays the results as HTML. For this system, there are two JSP pages, one is the main search page and the other is the cross-referential search page which searches the searched query in diﬀerent online lexical and linguistic resources. The snapshots of the indexing system are as follow:
Fig. 3. Homepage of the MBh Indexing System
Fig. 4. Search page of the MBh indexing system 2 http://sanskrit.jnu.ac.in/post/post.jsp 3 http://sanskrit.jnu.ac.in/subanta/rsubanta.jsp

---

<!-- page 159 -->

146 D. Mani
Fig. 5. Results of the searched query in hyperlinked mode with their numerical references
Fig. 6. Referential page for the searched query
Fig. 7. Cross-referential page where the user can click any one link to know further linguistic, grammatical or cultural knowledge

---

<!-- page 160 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 147 5.3 The Back-End of the System The back-end of the indexing system consists of RDBMS, which contains corelative data tables. This Tomcat server based program connects to MS-SQL Server 2005 RDBMS through JDBC connectivity. The lexical resources are stored as Devan¯agar¯ı utf-8. There are ﬁve tables namely; ‘shloka’, ‘adhyaya’, ‘akhyana’, ‘upaparva’ and ‘parva’.
A design of the indexing system of MBh database is given below:
Fig. 8. Diagram of the interconnection between the database tables
5.4 Database Connectivity The database connectivity is done through the JDBC driver software. JDBC Application Programming Interface (API) is the industry standard for database independent connectivity for Java and a wide range of database-SQL databases. JDBC technology allows to use the Java programming language to develop ‘Write once, run anywhere’ capabilities for applications that require access to large scale data. JDBC works as bridge between Java program and Database. SQL server 2005 and JDBC support input and output in Unicode, so this system accepts Unicode Devana¯gar¯ı text as well as prints result in the same format.4
6 Limitations of the System
1. The system has ﬁxed input and output mechanism. One can search his query in Unicode Devan¯agar¯ı only and the output will be in the same format. The work on transcoding of input and output in another format is being developed.
4 http://java.sun.com/javase/technologies/database/

---

<!-- page 161 -->

148 D. Mani
2. At present, the search facility is accessible only for previously displayed links. For enhancement of the system, we are planning to add other online lexical resources like MW Dictionary of Cologne Digital Sanskrit Lexicon (http://www.sanskrit-lexicon.uni-koeln.de/monier/indexcaller. php), The Sanskrit Library project at Brown University and Hindi WordNet (http://www.cfilt.iitb.ac.in/wordnet/webhwn/wn.php) of IIT, Mumbai. The reason to link with Hindi WordNet is because of a preponderance of Sanskrit words (tatsama) approximately 60-70% words in Hindi.5
3. At present, the system is unable to give the translation in other language. 4. In this version, it may fail to search a word which is in sandhi form. While
sandhi-split version of text has been stored for only ¯adiparva, eﬀorts are being made to do this for all other parvans. The sandhi splitting of the text has been done manually. 5. If a base word is searched it cannot be found in all its forms. For example, if “brahman” (pra¯tipadika) is searched, it will not return results for “brahma¯”, “brahman. i” etc. A subanta generation module is being developed separately to solve this problem. Alternatively, a subanta analyzer will enable the search to look for the stem if the pada is not found. At this point, the system directs the user to a subanta analyzer at the end of the search. The next version will make this module internal to the search. 6. It has only a string search facility so it cannot search synonymous words. For example, if ‘kr. s. n. a’ is searched, it cannot return ‘n¯ara¯yan. a’, ‘va¯sudeva’, ‘hari’, ‘mural¯ıdhara’, ‘yoge´svara’ etc. A separate module of Amarako´sa has been developed. In near future, this module will be used to handle this issue.
References
1. Bhise, U.R.: Na¯rad¯ıya¯ S´iks.a¯ with the Commentary of Bhat.t.a S´obha¯kara. Bhandarkar Oriental Research Institute, Poona (1986)
2. von B¨ohtlingk, O.: P¯an. ini’s Grammatik (Primary source text for our database). Olms, Hildesheim (1887)
3. Bronkhorst, J.: Greater Magadha Studies in the Culture of Early India. Brill, Leiden (2007)
4. Dhu¯pakara, A.S´.: S´r¯ıpin˙ galana¯ga-viracitam. Chandah.´s¯astram. Parimal Publications, Delhi (1985)
5. Deshpande, M.M.: Semantics of K¯arakas in P¯an. ini: An Exploration of Philosophical and Linguistical Issues. In: Matilal, B.K., Bilimoria, P. (eds.) Sanskrit and Related Studies: Contemporary Researches and Reﬂections, pp. 33–57. Sri Satguru Publications, Delhi (1990)
6. Gladigow, B.: Sequenzierung von Riten und die Ordnung der Rituale. In: Stausberg, M. (ed.) Zorostrian Rituals in Context, Numen Book Series, Studies in the History of Religions, vol. CII, pp. 57–76. Brill, Boston (1999)
7. Joshi, S.D., Roodbergen, J.A.F.: On siddha, asiddha and sth¯anivat, vol. LXVIII, pp. 541–549. Annals of the Bhandarkar Oriental Research Institute, Poona (1987)
5 http://www.cfilt.iitb.ac.in/gwc2010/pdfs/67_Sanskrit_Wordnet__ Kulkarni.pdf

---

<!-- page 162 -->

RDBMS Based Lexical Resource for Mah¯abha¯rata 149
8. Joshi, S.D., Roodbergen, J.A.F.: The As.t.¯adhya¯y¯ı of P¯an. ini, with Translation and Explanatory Notes, vol. II. Sahitya Akademi, New Delhi (1993)
9. Houben, J.E.M.: ‘Meaning statements’ in P¯an. ini’s grammar: on the purpose and context of the As.t.a¯dhya¯y¯ı. Studien zur Indologie und Iranistik 22, 23–54 (19992001)
10. Houben, J.E.M.: Memetics of Vedic Ritual, Morphology of the Agnis.t.oma. In: Griﬃths, A., Houben, J.E.M. (eds.) The Vedas: texts, language & ritual, pp. 23–
47. Forsten, Groningen (2004) 11. Katre, S.M.: As.t.¯adhya¯y¯ı of P¯an. ini. Motilal Banarsidass, Delhi (1989) 12. Lu¨ders, H.: Die Vyˆasa-C¸ ikshˆa besonders in ihrem Verh¨altnis zum Taittirˆıya-
Prˆati¸caˆkhya, G¨ottingen (1894) 13. Michaels, A.: ‘Le rituel pour le rituel’ oder wie sinnlos sind Rituale? In: Caduﬀ,
C., Pfaﬀ-Czarnecka, J. (eds.) Rituale heute: Theorien - Kontroversen - Entwu¨rfe,
pp. 23–47. Reimer, Berlin (1999) 14. Michaels, A.: The Grammar of Rituals. In: Michaels, A., Mishra, A. (eds.) Gram-
mar and Morphology of Ritual, Ritual Dynamics and the Science of Ritual, vol. I,
pp. 15–36. Harrassowitz Verlag, Wiesbaden (2010) 15. Mishra, A.: Simulating the P¯an. inian System of Sanskrit Grammar. In: Huet,
G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008.
LNCS (LNAI), vol. 5402, pp. 127–138. Springer, Heidelberg (2009) 16. Mishra, A.: Modelling the Grammatical Circle of the P¯an. inian System. In: Huet,
G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008.
LNCS (LNAI), vol. 5402, pp. 40–55. Springer, Heidelberg (2009) 17. Mishra, A.: On the Possibilities of a P¯an. inian Paradigm for a Rule-based Descrip-
tion of Rituals. In: Michaels, A., Mishra, A. (eds.) Grammar and Morphology of
Ritual, Ritual Dynamics and the Science of Ritual, vol. I, pp. 15–36. Harrassowitz
Verlag, Wiesbaden (2010) 18. Sarup, L.: The Nighan. t.u and The Nirukta. Motilal Banarsidass, Delhi (1967) 19. Oppitz, M.: Montageplan von Ritualen. In: Caduﬀ, C., Pfaﬀ-Czarnecka, J. (eds.)
Rituale heute: Theorien - Kontroversen - Entwu¨rfe, pp. 23–47. Reimer, Berlin
(1999) 20. Sarup, L.: The Nighan. t.u and the Nirukta. Motilal Banarasidass, Delhi (1967) 21. Shastri, K.: ¯age´sabhat.t.a-kr.ta Vaiya¯karan. a-siddh¯anta-parama-laghu-man˜ju¯s.¯a. Ku-
rukshetra University Press, Kurukshetra (1975) 22. Shastri, M.D.: The R. gveda-Pr¯ati´s¯akhya with the commentary of Uvat.a. Vaidika
Svadhyaya Mandir, Varanasi (1959) 23. Scharf, P.M.: Modeling P¯an. inian Grammar. In: Huet, G., Kulkarni, A., Scharf, P.
(eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp.
95–126. Springer, Heidelberg (2009) 24. Scharfe, H.: A new perspective on P¯an. ini. In: Indologica Taurinensia, vol. XII, pp.
1–273 (2009) 25. Staal, F.: Rules without meaning: ritual, mantras and the human sciences. Lang,
New York (1989) 26. Thieme, P.: Meaning and form of the ‘grammar’ of P¯an. ini. Studien zur Indologie
und Iranistik 8/9, 12–22 (1982) 27. Varma, V.K. (ed.): V¯ajasaneyi-Pr¯ati´s¯akhyam. Chaukhamba Sanskrit Pratishthan,
Delhi (1987) 28. Varma, V.K.: R. gveda-Pr¯ati´s¯akhyam. Banaras Hindu University Sanskrit Series,
Varanasi (1972) 29. Wezler, A.: On the quadruple division of the Yoga´s¯astra, the caturvyu¯hatva of the
Cikits¯a´s¯astra and the ‘four noble truths’ of the Buddha. In: Indologica Taurinensia,
vol. XII, pp. 289–337 (1984)

---

<!-- page 163 -->

Evaluating Tagsets for Sanskrit
Madhav Gopal1, Diwakar Mishra2, and Devi Priyanka Singh3
1 Centre for Linguistics, SLL & CS 2 Special Center for Sanskrit Studies 3 Centre for Indian Languages, SLL & CS Jawaharlal Nehru University, New Delhi {mgopalt,diwakarmishra,devisi.translation}@gmail.com
Abstract. In this paper we present an evaluation of available Part Of Speech (POS) tagsets designed for tagging Sanskrit and Indian languages which are developed in India. The tagsets evaluated are - JNU-Sanskrit tagset (JPOS), Sanskrit consortium tagset (CPOS), MSRI-Sanskrit tagset (IL-POST), IIIT Hyderabad tagset (ILMT POS) and CIIL Mysore tagset for the Linguistic Data Consortium for Indian Languages (LDCIL) project (LDCPOS). The main goal behind this enterprise is to check the suitability of existing tagsets for Sanskrit from various Natural Language Processing (NLP) points of view.
Keywords: As.t.¯adhya¯y¯ı, POS tagging, POS tagger, tagset, morphology, P¯an. ini, WSD, machine learning.
1 Introduction
POS tagging assigns a suitable part of speech label for each word in a sentence of a language. In other words, POS tagging is the process of identifying lexical/grammatical category of a word according to their function in the sentence. For NLP tasks, annotated corpora of a language have a great importance. Annotated corpora serve as an important resource for such well-known NLP tasks as POS-Tagging, chunking, parsing, structural transfer, word sense disambiguation (WSD) etc. POS tagging is also referred to as morpho-syntactic tagging or annotation. A POS Tagger (POST) is a piece of software that reads text in some language and assigns parts of speech to each word (and other token), such as noun, verb, adjective, etc., although generally computational applications use more ﬁne-grained POS tags like ’noun-masculine’ etc.
The quality of the POS annotation in a corpus is crucial for the development of POST. The design of the annotated Sanskrit corpus is rapidly going on in India. Natural languages are intrinsically very complicated and Sanskrit is not an exception to this. Sanskrit is morphologically and lexically very rich language. It has a variety of words, lexemes, morphemes, and a rich productive mechanism of forming new words. Due to identical inﬂections for various cases, many of its words are ambiguous and their disambiguation for NLP tasks is a must. Moreover, there are many factors involved in causing ambiguity in this
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 150–161, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 164 -->

Evaluating Tagsets for Sanskrit 151
language. A tagged Sanskrit corpus could be used for a wide variety of research like developing POS Taggers, chunkers, parser, WSD etc.
A tagged text corpus is useful in many ways. More abstract levels of analysis beneﬁt from reliable low-level information, e.g. parts of speech, so a good tagger can serve as a preprocessor. It is also useful for linguistic research for example to help ﬁnd instances or frequencies of particular constructions in large corpora. Apart from this it is good for stemming in information retrieval (IR), since knowing a word’s part of speech can help tell us which morphological aﬃxes it can host. Automatic POS taggers can help in building automatic word-sense disambiguating algorithms; POS taggers are also used in advanced ASR language models such as class-based N-grams. POS tagging is also useful for text to speech synthesis and alignment of parallel corpora.
2 Characteristics of the Sanskrit Language
Sanskrit is one of the most studied languages of the world. It has been analyzed through many schools of grammar in India and abroad as well. Traditionally, the number of grammatical categories of Sanskrit varies from one to ﬁve. According to Indra school of v yakaran. a there is only one category of words (arthah. padam). Pa¯n. ini recognizes two categories: nominal and verbal (suptin´antam padam - Pa¯n. ini 1.4.14). The Nyaya philosopher Jagadisha in his ´sabda´saktipraka´sika accepts only three categories of words: base, suﬃx and particles (prakr. ti, pratyaya and nipata). The most popular categorization is of Yaska who describes the language in four categories: nominal base, verb root, preﬁx and indeclinable (catv¯ari padaja¯t¯ani n¯am¯akhyate copasarganip¯at¯a´sca – Nirukta 1.1). The new grammarians (navya vaiya¯karan. a) add one more category to the list of Yaska, that is, karmapravacaniya and accept ﬁve categories of words. The diﬀerent views on number of word categories are given in Durga’s commentary on Nirukta [19]. If we take Yaska’s grammatical categories for POS tagging, it will be very coarse grained tagging. But it will help us give high accuracy result as less number of tags lead to eﬃcient machine learning. Moreover, two of these categories (preﬁx and indeclinable) belong to the closed class and the remaining two categories have totally diﬀerent set of inﬂectional suﬃxes which are relatively easily identiﬁable. Apart from this, the set of roots of one category (verb) is also a closed list, that is, dh¯atupa¯.tha (list of verb roots listed by Pa¯n. ini).With so shallow information this accuracy will not be of much help in many kinds of NLP tasks like in WSD which requires very ﬁne-grained analysis.
Sanskrit is a relatively free word order language. In Sanskrit, a syntactic unit is called pada. Cardona [3] posits the formula for Sanskrit sentence (N-En)p. . . (VEv)p. A pada can be a nominal (subanta) or verbal (tin´anta) expression. Padas with sup (nominal) inﬂections constitute the NPs (subanta padas), and those with tin´ (verbal) can be called constituting the VPs (tin´anta pada along with object subantas). In the former, the bases are called pra¯tipadikas which undergo sup suﬃxations under speciﬁcally formulated conditions of case, gender, number, and also the end-characters of the bases to yield nominalsyntactic words.

---

<!-- page 165 -->

152 M. Gopal, D. Mishra, and D. Priyanka Singh
The rules for subanta padas are found scattered in As..t¯adhy¯ay¯i mostly in chapters 7-1, 7-2, 7-3, 6-1, 6-4. However, these rules have been treated in the subanta chapter of Siddh¯anta Kaumuda¯ from rule number 177 to 446 [10].
The derivational morphology in Sanskrit studies primary forms (k.rdanta) and secondary forms (taddhita), compounds (sama¯sa), feminine forms (str¯ipratyaya¯nta) etc. These can be inﬂected for 21 case (7 cases x 3 number) aﬃxes to generate 21 inﬂected forms.
The verb morphology (tin˙ anta) is equally complex. Sanskrit has approximately 2014 verb roots including kan. va¯di according to Pa¯n. inian dh¯atupa¯ha classiﬁed in 10 gan. as to undergo peculiar operations; it can also be subclassiﬁed in 12 derivational suﬃxes. A verb root conjugates for tense, mood, number and person information. Further, these can have ¯atmanepad¯i and parasmaipad¯i forms in 10 laka¯ras and 3x3 person and number combinations. There are12 secondary suﬃxes added to verb roots to create new verb roots. A verb root may have approximately 2190 (tense, aspect, number etc.) morphological forms. Mishra et al. [17] have done a rough calculation of all potential verb forms in Sanskrit to be more than 1029,60,000.
3 Evaluation Discussion of Tagsets
This section presents a survey of tagsets designed speciﬁcally for Sanskrit or for all Indian languages and then their evaluation with respect to Sanskrit. The tagsets are given in tables in their respective sub-sections.
3.1 ILMT Tagset (IIIT-Hyderabad)
NLP researchers at IIIT-Hyderabad have designed a standard POS tagset called ILMT tagset, guidelines for POS tagging and Chunking for Indian Languages and also brought out a collection of Application Program Interfaces (APIs) and tools for NLP called Sanchay, which also includes syntactic annotation interface. Their tagset is a ﬂat one derived from the Penn tagset for English. They have made certain changes in the original tagset to make it suitable for Indian languages. Wherever the Penn tags were found to be inadequate for Indian languages, either new tags were introduced or existing tags were modiﬁed. It has less number of tags with the assumption that having less tags will facilitate machine learning and will give higher accuracy and coverage. This tagset covers mainly lexical categories and does not consider syntactic function of the word in the sentence, citing a reason that this reduces confusion involved in manual tagging. The machine is able to establish a word-tag relation which leads to eﬃcient machine learning. The following table (Table. 1) contains all the tags listed in this tagset.
Thus, this tagset allows only coarse linguistic analysis and avoids ﬁne-grained distinctions among linguistic items. At the same time, the designers of the tagset believe that “too coarse an analysis is not of much use”. They try to seek a balance between ﬁneness and coarseness. According to them, analysis should not be so ﬁne as to hamper machine learning and also should not be so coarse as

---

<!-- page 166 -->

Evaluating Tagsets for Sanskrit 153
Table 1. ILMT Tagset
to lose important information. This tagset does not include attributes of lexical categories such as gender, number, person etc. Apart from this the tags for incorporated adjective and adverb are not applicable in Sanskrit. In Sanskrit, like noun and verb, Particles also require more tags as they have diﬀerent and valuable function in the language, so in order to suit Sanskrit this tagset will have to be modiﬁed signiﬁcantly. Keeping in mind the complex morphology of Sanskrit this ﬂat tagset will hardly be able to do WSD. 3.2 JNU-Sanskrit Tagset (JPOS) R. Chandrashekar’s doctoral thesis titled Part-of Speech Tagging for Sanskrit [4] deals with the POS tagging problem for Sanskrit for the ﬁrst time. In the linguistic analysis, JPOS follows the Pa¯n. inian grammatical description very strictly. His classiﬁcation of Sanskrit linguistic items is very exhaustive and it provides a very unique tag applying the Sanskrit grammatical terms as much as possible. In the following table (Table. 2) the tag description of main categories is given.
In this tagset, there are 65 word class tags, 43 feature sub-tags, and 25 punctuation tags and one tag UN to annotate unknown words – a total of 134 tags. A single full tag is a combination of word class tag and feature sub-tags (indeclinable and punctuation tags do not have sub-tags). This is helpful in ambiguity resolution as person and number sub-tags have an agreement between the nouns and verbs in Sanskrit. The complete table for verb tags is not given here; I have given only two tags for it- Parasmai Pada Verb and Atmane Pada Verb. Verb takes laka¯ra, and person-number tags. Adjectives are included with their degrees, that is, they have 3 tags.

---

<!-- page 167 -->

154 M. Gopal, D. Mishra, and D. Priyanka Singh Table 2. JNU-Sanskrit Tagset
This is a ﬂat and ﬁne-grained tagset capturing linguistic features according to the traditional Sanskrit grammar. Its coverage is very high. Almost every kind of linguistic item was treated discretely (especially taddhita and k.ridanta constructions). This tagset is very informative but we assume that its speciﬁcity will suﬀer while tagging the data. For instance, among noun tags there are 8 tags and the basis of counting them separately seems to be the special morphology for these items like Patronymic Noun (e.g. ra¯ghavah. , ja¯nak¯i), Metronymic Noun (e.g. pa¯rthah. , saumitrih. ), (both tags could be treated as Proper Noun), Agent Noun (e.g. kartuh. , adhya¯pakah. ) (could be treated as Common Noun). Likewise under Compound category there are 14 types. Many of which could be clubbed

---

<!-- page 168 -->

Evaluating Tagsets for Sanskrit 155
Table 3. LDCIL Tagset
under other categories as well. For example, the words like ra¯japurusah. and devendrah. have been assigned Determinative Compound (genitive) which could be very well given Common noun and Proper noun respectively. The division of participle tags is also very lengthy; k.ridanta vartam¯ana has two separate tags which does not seem serving any purpose and the same is with k.ridanta vidhyarthaka which has 3 tags.
Apart from this, the human annotator will have enormous cognitive load as this tagset requires remembering this huge number of tags along with exhaustive knowledge of P¯an. inian grammar in order to apply them correctly. Only a sophisticated pundit of P¯an. inian grammar can handle this task. At experiment level, however, no data have been tagged to test its eﬃciency, so the above is our assumption only. Moreover, its adaptation for other Indian languages will invite enormous changes in the tagset. So the tagged multilingual corpora will hardly be compatible with each other.
3.3 LDCIL Tagset Linguistic Data Consortium for Indian Languages(LDC-IL) is a consortium for the development of language technology in India and was set up by a collective eﬀort of the Central Institute of Indian Languages, Mysore and several other like-minded institutions working on Indian Languages technology. LDCIL tagset is available in the website of Linguistic Data Consortium for Indian Languages: http://www.ldcil.org/POSTagSet.html. This tagset was formulated by the Standardization Committee on August 6, 2007 at IIIT, Hyderabad and is a further extension of ILMT tagset with some additional tags to achieve higher level of granularity. It is a standard tagset for annotating the corpora of Indian languages. It is a ﬂat tagset designed in the pattern of ILMT tagset and has a total of 26 tags. The table below (Table. 3) contains all the tags. This tagset is similar to ILMT tagset, so the same evaluation goes to this also.

---

<!-- page 169 -->

156 M. Gopal, D. Mishra, and D. Priyanka Singh Table 4. IL-POSTS Sanskrit tagset categories and their Types
Table 5. IL-POSTS Sanskrit tagset attributes and their values

---

<!-- page 170 -->

Evaluating Tagsets for Sanskrit 157
3.4 IL-POSTS Sanskrit Tagset
This tagset has been derived from IL-POSTS, a standard framework for Indian languages developed by MSRI. This is a hierarchical tagset which is based on guidelines similar to EAGLES. This tagset encodes information at three levelsCategories, Types, and Attributes. Till date (as far as we know) four language speciﬁc tagsets have been derived from this framework; Hindi, Bangla, Tamil and Sanskrit. The tagset for Sanskrit is given here in these two tables (Table. 4, 5)- one having categories and their respective types and the other containing attributes and their respective values:
The standard which has been followed in this tagset takes care of the linguistic richness of Indian languages including Sanskrit. It allows the “selective inclusion and removal of features for a speciﬁc language/project, thereby keeping the framework a common standard across languages/projects” [1]. This tagset is supposed to provide cross-linguistic compatibility, reusability, and interchangeability. Keeping in mind its higher accuracy results, it could prove a boon to Indian NLP which still needs to achieve a good position in the world as Indian languages are lacking adequate resources in terms of data and tools (see [1] and [11]).
This framework is very sophisticated in covering the linguistic features of Indian languages. The tags used are extremely ﬁne-grained, and incorporate a great deal of information about case, gender, number and so on. The IL-POST is able to accommodate all desired linguistic features of Sanskrit and the tagged corpus remains compatible with other languages tagged by a brethren tagset. Apart from this, as this tagset follows the standard of European languages it could enable us to access the European language data for Indian NLP and vice versa.
MSRI has developed an annotation tool called MSRI Part-of-Speech Annotation Interface which is a GUI for assigning the appropriate POS label for each word in a sentence. This is designed for annotating within the framework of a hierarchical tagset designed at MSRI. The tool also provides the facility to provide the morphological attributes with their values. The interface supports various operations for viewing and editing the POS labels and morphological information associated with the word. This tool reduces the cognitive load of the human annotator and enables one to speed up the tagging task.
3.5 Sanskrit Consortium Tagset (CPOS)
This tagset is designed for tagging sandhi-free Sanskrit corpus. It is based on traditional Sanskrit grammatical categorization. All the tags seem to be the extensions of Y¯aska’s four grammatical categories: n¯ama, ¯akhya¯ta, upasarga and nipa¯ta. This tagset has 28 tags. All the tags are given in the following table (Table. 6):
This is apparently a ﬂat tagset and allows the annotation of major categories only. Most of the categories appear to have been adapted either from the JPOS or the ILMT tagset. For morphological analysis it will take help from Morphological Analyzer, so morpho-syntactic features are not included in the tagset. It

---

<!-- page 171 -->

158 M. Gopal, D. Mishra, and D. Priyanka Singh Table 6. Sanskrit Consortium tagset
is supposed to give higher accuracy result by having less number of tags. A tool called Sanchay is being used to facilitate manual tagging and thus it reduces the cognitive load of annotator. For Sanskrit tagging, it can be useful as long as we know what will be the use of tagged data in this tagset. At an experimental level two taggers were developed using this tagset - a rule based and a statistical and have reported 79-81% results. The rule based tagger can be accessed using this link http://sanskrit.jnu.ac.in/cpost/post.jsp. As this tagset does not follow any standard framework the tagged data will hardly allow any sharing and reusability. Due to its coarse-grained tagging and unavailability of Indian language morph analyzers, it will be interesting to see how this tagset can be put to actual use.

---

<!-- page 172 -->

Evaluating Tagsets for Sanskrit 159
4 Conclusion and Further Research
From the above evaluation of the tagsets it appears that the most useful tagged corpus is the one that ensures the maximal use and sharing of it, and it will only be possible when it is tagged by a well-established standard tagset or paradigm. The tagsets that we have discussed in this article are of both kinds- those following global standards/guidelines and those which have evolved from particular language speciﬁc requirements. The tagsets like ILPOST, ILMT and LDCIL are designed to take care of all Indian languages, and this could provide resource sharing and reusability of the linguistic resources. The ﬂat tagsets may be easier to process but they cannot capture higher level of granularity without an extremely large list of independent tags. They are hard to adapt too. So far, ILPOSTS has been used for four languages Hindi, Tamil, Bangla and Sanskrit, and an adapted version is reportedly being used in the LDC-IL project at CIIL Mysore for many more languages. So, in order to enrich Indian NLP resources, ILPOSTS seems to be a better option. However, further research is needed to substantiate this claim.
For further research a certain amount of data could be manually tagged with the help of these tagsets by some (1 or 2) human annotator. And on the basis of the experience of these annotators certain facts can be discovered, for example, which tagset is easy to use for Sanskrit and which tagset gives better results and which is less confusing and so on. Thereafter, rule based or statistical taggers can be tested for the eﬃciency of these tagsets and also their compatibility across languages.
References
1. Baskaran, S., Bali, K., Bhattacharya, T., Bhattacharyya, P., Choudhury, M., Jha, G.N., Rajendran, S., Saravanan, K., Sobha, L., Subbarao, K.V.S.: A Common Parts-of-Speech Tagset Framework for Indian Languages. In: LREC, Marrakech, Morocco (2008)
2. Baskaran, S., et al.: Framework for a Common Parts-of-Speech Tagset for IndicLanguages (2007), http://research.microsoft.com/~baskaran/POSTagset
3. Cardona, G.: P¯an. ini: His work and its traditions. Motilal Banarasidass, Delhi (1988)
4. Chandrashekar, R.: Parts-of-Speech Tagging For Sanskrit. Ph.D. thesis submitted to JNU, New Delhi (2007)
5. Greene, B.B., Rubin, G.M.: Automatic grammatical tagging of English. Department of Linguistics, Brown University, Providence, R.I. (1981)
6. Hardie, A.: The Computational Analysis of Morphosyntactic Categories in Urdu. PhD Thesis submitted to Lancaster University (2004)
7. Hellwig, O.: SANSKRITTAGGER, A Stochastic Lexical and POS Tagger for Sanskrit. In: Huet, G., Kulkarni, A. (eds.) Sanskrit Computational Linguistics 2007. LNCS (LNAI), vol. 5402. Springer, Heidelberg (2009)
8. Huet, G.: The Sanskrit Heritage Site, http://sanskrit.inria.fr/ 9. IIIT-Tagset. A Parts-of-Speech tagset for Indian Languages,
http://shiva.iiit.ac.in/SPSAL2007/iiit_tagset_guidelines.pdf

---

<!-- page 173 -->

160 M. Gopal, D. Mishra, and D. Priyanka Singh
10. Jha, G.N.: Generating nominal inﬂectional morphology in Sanskrit. In: SIMPLE 2004, IIT-Kharagpur Lecture Compendium, Shyama Printing Works, Kharagpur (2004)
11. Jha, G.N., Gopal, M., Mishra, D.: Annotating Sanskrit Corpus: adapting ILPOSTS. In: Vetulani, Z. (ed.) Proceedings of the 4th Language and Technology Conference: Human Language Technologies as a Challenge for Computer Science and Linguistics, pp. 467–471 (2009)
12. Jha, G.N., Mishra, S.: Semantic processing in Panini’s karaka system. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402. Springer, Heidelberg (2009)
13. Kale, M.R.: A Higher Sanskrit Grammar. MLBD Publishers, New Delhi (1995) 14. Leech, G., Wilson, A.: Recommendations for the Morphosyntactic Annotation of
Corpora. EAGLES Report EAG-TCWG-MAC/R (1996) 15. Leech, G., Wilson, A.: Standards for Tag-sets. In: van Halteren, H. (ed.) Syntactic
Word class Tagging. Kluwer Academic, Dordrecht (1999) 16. Leech, G.: Grammatical Tagging. In: Garsire, Leech, McEnery (eds.) Corpus Anno-
tation: Linguistic Information for Computer Text Corpora. Longman, London (1997) 17. Mishra, S., Jha, G.N.: Identifying verb inﬂections in Sanskrit morphology. In: Pro-
ceedings of SIMPLE 2004, IIT Kharagpur (2005) 18. Ramkrishnamacharyulu, K.V.: Annotating Sanskrit Texts Based on Sabdabodha
Systems. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 26–39. Springer, Heidelberg (2009) 19. Rishi, U.S.S. (ed.): Yaska-pranitam niruktam, vol. I. Chowkhamba Vidyabhawan, Varanasi (2005) 20. Santorini, B.: Part-of-speech tagging guidelines for the Penn Treebank Project. Technical report MS-CIS-90-47, Dept. Of Computer and Information Science, University of Pennsylvania (1990)
Appendices

---

<!-- page 174 -->

Evaluating Tagsets for Sanskrit 161

---

<!-- page 175 -->

Performance of a Lexical and POS Tagger for Sanskrit
Oliver Hellwig
SAI, Universit¨at Heidelberg, Germany hellwig7@gmx.de
Abstract. Due to the phonetic, morphological, and lexical complexity of Sanskrit, the automatic analysis of this language is a real challenge in the area of natural language processing. The paper describes a series of tests that were performed to assess the accuracy of the tagging program SanskritTagger. To our knowlegde, it oﬀers the ﬁrst reliable benchmark data for evaluating the quality of taggers for Sanskrit using an unrestricted dictionary and texts from diﬀerent domains. Based on a detailed analysis of the test results, the paper points out possible directions for future improvements of statistical tagging procedures for Sanskrit.
1 Overview and Previous Research
The quality of automatic language analysis methods is one of the central issues in natural language processing (NLP). Most research in this area concentrates on English and the voluminous corpora available in this language. For example, the tagsets and the precision of the POS tagging applied to the Penn treebank were described in [6]. The authors used a small POS tagset that consisted of 48 categories and included tags such as “existential there” and “comma”. Applying “a cascade of stochastic and rule-based taggers” to the treebank, they obtained an error rate of 2-6% using this tagset. A similar approach is found in [5] where CLAWS4, a tagger for the British National Corpus, is described. The authors used a multi-level model for analysis and reported error rates of 1-5% for POS tagging. In more recent publications, however, it has been pointed out that many of the assumptions on which the popular NLP systems for English are based do not apply to other languages. For tagging Hungarian, for instance, a completely diﬀerent tagset was used in [2]. This tagset consisted of 744 tags, thus even exceeding the size of the tagset applied by SanskritTagger. Using a morphological analyzer and a maximum entropy model, the authors reported error rates of 1-3% for POS assignment in a Hungarian corpus.
Obviously, the precautions brought forward in [2] apply to the computational analysis of Sanskrit to an even higher degree. Like in Hungarian, the linguistic complexity of Sanskrit is partly caused by its inﬂectional nature. In addition, the automatic processing of Sanskrit faces a number of problems that occur on diﬀerent levels of language analysis and are not well studied in NLP literature dealing with European and especially Germanic languages:
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 162–172, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 176 -->

Performance of a Lexical and POS Tagger for Sanskrit 163
1. Segmenting a Sanskrit phrase into its inﬂected components is the ﬁrst and perhaps most demanding task in the analysis of Sanskrit texts. This situation is mainly caused by the phonetic rules called Sandhi, and it is aggravated by the almost complete absence of typographic conventions such as punctuation or the lower/upper case opposition, which is so useful in analyzing German texts. Similar problems are, for example, known from the automatic processing of Chinese, where word segmentation is a well-studied, though not satisfactorily solved problem (cmp. [8] for an overview of this area).
2. On a higher level of linguistic analysis, the large number of homonyms and the comparatively free word order complicate the automatic processing of Sanskrit. Studies performed for languages whose word order is less regimented than in English suggest that tagging strategies that are based on positional information are less successful in processing such languages (see, for example, [7, 280]). The situation is further complicated by the structure of digital dictionaries of Sanskrit. Many of these dictionaries are not designed for the needs of NLP, but are created from scanned versions of printed dictionaries. Due to the exigencies of philological work, many printed dictionaries contain collocations or inﬁnite verbal forms that may be interesting from a philological perspective, but deteriorate the quality of automatic processing.
This means that the stages of processing Sanskrit diﬀer strongly from what is known for European languages and especially English. To analyze Sanskrit phrases, a multi-level strategy had to be designed whose single components are much more entangled than in the processing of European languages (cmp. [4]). Due to these diﬀerences in the analysis process and thus in the test design, POS error rates found for European languages are hardly comparable with those for Sanskrit.
The following section ﬁrst sketches the basic ideas of the tagging process applied in SanskritTagger and then describes the testing procedure and its results.
2 Testing the SanskritTagger
2.1 The Test Design
In the statistical model used by SanskritTagger, the result of the analysis is inﬂuenced by two factors: The language data from which statistical key values are estimated and the procedures that make use of these statistical values to analyze a given piece of text. Since the procedures were outlined in [4], we will concentrate on the question of how the lexical data and the amount of data used for training inﬂuences the quality of the analysis.
To begin with, let us shortly reconsider some details of the analysis process to make clear on which kind of data the analysis is based. In the following, W denotes an uninterrupted string, this means a string of letters that does not contain break markers such as spaces or dan. d. as. If W is formed correctly, it can be split into at least one substring wi, which is a grammatically correct Sanskrit form. SanskritTagger divides the analysis of W roughly into three stages:

---

<!-- page 177 -->

164 O. Hellwig
1. Initially, a list of candidate solutions is generated for each substring wi that may be contained in W . The number of candidate solutions depends on the well-known features that complicate the computational (and human!) analysis of Sanskrit: the number of possible Sandhi breakpoints and the morphological and lexical complexity of wi.
2. In the second step, the program searches for a path through the elements of the candidate lists that is optimal from the perspective of phraseology or lexicography. The path is calculated using a ﬁrst-order Markov chain whose parameters (i.e., relative frequencies of single lexemes and transition probabilities between bigrams of lexemes) are the statistical key values mentioned above (cmp. [4, 273/74]). These values are estimated from the texts stored in the database of SanskritTagger. As a ﬁrst hypothesis, we may assume that the size of this text database strongly inﬂuences the quality of the estimated parameters and, therefore, also the accuracy of the analysis. At this point, it should be taken into consideration that previous research has shown that the correlation between the amount of training data and the analysis quality is not linear (see, e.g., [9, 363ﬀ.] for an early treatment of this problem). Therefore, we will variate the number of texts used to calculate these parameters for reaching a realistic picture of how the accuracy of the tagging is inﬂuenced by the size of the text database (cmp. page 168).
3. After the candidate lists have been ﬁltered by lexical criteria, the third stage of the analysis process uses similar methods to ﬁnd an optimal POS path through the remaining candidates. The role of the text database and the parameter estimation corresponds with the scenario described in the second step.
For performing the tests, we used the standard leave-one-out strategy with consistent train-test splits. First, the set T of all texts t that contain more than 10.000 words was retrieved from the corpus.1 Next, for each t ∈ T , the statistical data was rebuilt without including t, and t was analyzed using this data and the built-in routines of SanskritTagger. To evaluate the test result, the new analysis anew of each separable string was compared with the analysis of the string aDB that is stored in the program database. This step seems trivial at ﬁrst view. However, consider the following case:
String: k.r.sn. apa¯dasevanatatparah. aDB: k.rs. n. a-pa¯da-sevana-tatparah. anew: k.r.sn. a-pa¯dasevana-tatparah.
If the new analysis anew were marked as completely wrong, the error rate would be overestimated because 2 of 4 lexemes (kr. s. n. a and tatpara) were identiﬁed correctly. Therefore, we had to devise an evaluation procedure that was able to cope with such imperfect matches.
A simple solution of this problem is oﬀered by alignment techniques (see [3] for a survey of techniques for pairwise alignment and [1, 368ﬀ] for an Indological
1 The only large text that was skipped is the Maha¯bha¯rata, whose processing time would have amounted to several hours.

---

<!-- page 178 -->

Performance of a Lexical and POS Tagger for Sanskrit 165

application of such algorithms). The basic idea of these techniques can be sketched
as follows. Given two vectors of symbols v1 and v2, a matrix is created that has the dimensions (|v1|+1)·(|v2|+1). The ﬁrst row and the ﬁrst column of the matrix are ﬁlled with ascending numbers, i.e., c[i,1] = i − 1 for the ﬁrst row and c[1,i] = i − 1 for the ﬁrst column. Now, the comparison algorithm ﬁlls the remaining |v1| · |v2| cells of the matrix. The value c[x,y] of each cell [x, y] is calculated by inspecting the three preceeding cell values c[x,y−1], c[x−1,y] and c[x−1,y−1]:

⎧ ⎨

c[x,y−1]

+

γ

c[x,y] = min c[x−1,y] + γ

⎩ c[x−1,y−1] + compare(v1x, v2y)

γ is the gap penalty with which the non-alignment of two symbols is penalized.

compare(v1x, v2y) is a function that compares the symbols v1x and v2y, which are represented by the analysis of a substring stored in the database (v1x) and its new analysis (v2y) in our case. The value of compare ranges from 1 (= v1x and v2y are derived from diﬀerent lexemes) to 0 (= v1x and v2y are identical). It is calculated by inspecting to which degree the analyses of v1x and v2y are diﬀerent. A diﬀerence in the lexical analysis is the most severe kind of error

because it invalidates the following morphological and POS analysis. compare

returns 1 in this case. This kind of error is caused by two scenarios. In the

ﬁrst scenario, the string is segmented diﬀerently in the database and by the

new analysis. The string kr. s.n. ap¯adasevanena may, for instance, be analyzed as kr. .sn. a[comp.]-pa¯da[comp.]-sevanena[instr.] in the database, but as kr. .sn. a[comp.]p¯adasevanena[instr.] by the new analysis. In many cases, these errors are caused

by redundancies found in the Sanskrit dictionaries (cmp. page 163). In the second

scenario, both procedures have split the string in the same way, but have assigned

diﬀerent lexemes to at least one substring. In our example, this may result in

analyses such as “the worship of the feet of Kr.s.n. a” in the database and “the worship of black feet” by the new analysis due to the homonymy of the noun

and the adjective k.r.sn. a. A more detailed analysis of this class of errors is given in section 2.2. If the lexical analysis has succeeded, errors may occur in the

morphological and POS analysis of the words (third step of the analysis). The

most frequent types of errors are caused by bahuvr¯ıhi composites whose diﬀering

gender is not recognized correctly, and by morphologically ambiguous forms

such as vanam, which may be a nominative, an accusative, or a vocative. In

these cases, compare returns a positive value larger than zero that represents

the number of correct decisions the algorithm has made. Errors in the analysis

of a noun, for example, can occur during the four stages of lexical analysis, this

means in case, number, and gender. If the lexical analysis, case, and number

were

recognized

correctly,

compare

returns

3 4

=

0.75.

After the algorithm has traversed the whole matrix, the cell c[|v1|+1,|v2|+1]

contains the accumulated costs of the optimal alignment of v1 and v2. This

value may be used to calculate a measure of quality e for the analysis process:

e(v1, v2)

=

1

−

γ

c[|v1|+1,|v2|+1] · max(|v1|, |v2

|)

.

---

<!-- page 179 -->

166 O. Hellwig
Using γ · max(|v1|, |v2|) in the divisor is motivated by the fact that the accumulated costs amout to max(|v1|, |v2|) · γ if two sequences contain no pairwise identical symbols. Therefore, e(v1, v2) is in the range [0, 1] with e(v1, v2) = 1 for a perfect match. To extract the details about the errors made by the program, the matrix is traversed in backward direction by using pointers set during the forward pass. The error information gained in this step is examined in detail in the next section.

2.2 Results and Evaluation

All texts in the SanskritTagger database that contain more than 10.000 words were analyzed using the testing scenario described in the preceeding section. The test data will be evaluated in two steps. First, we will give an overview of general trends in the performance of the tagger, which includes questions such as the inﬂuence of the text genre and the style on the analysis accuracy (page 166). Second, we will have a closer look at the lexical errors, which constitute the most frequent class of errors (page 168).

The general performance. The raw test results are listed in table 1, which contains some types of information that need further explanation:

1. Lexical richness is the ratio of the number of diﬀerent lexemes divided by

the number of all words contained in a text (nT ). It ranges from

1 nT

(each

word of the text is derived from the same lexeme, something like ´siva ´siva

´siva)

to

nT nT

=1

(each word is

derived from another lexeme).

2. Six kinds of errors are distinguished in the tests. Apart from a lexical error

eLEX (cmp. page 165 and page 168 for a detailed analysis of this kind of error), a wrong POS tag can be assigned to a correctly identiﬁed lexeme

(eP OS1−5). eP OS1 occurs only when an inﬁnite verbal form is confused with a ﬁnite one.

3. The hit rate H records the overall hit rate of SanskritTagger. If C is the

number of words that were analyzed correctly and ω =

5 i=1

eP

OSi,

it

is

deﬁned as

H=

C

.

C + eLEX + ω

The lexical hit rate HLEX ignores POS errors because the lexeme has been recognized correctly in such cases:

HLEX

=

C

C +ω + eLEX

+

. ω

To compare the accuracy of SanskritTagger with that of other POS taggers,

the POS error rate can be calculated as follows (values not displayed in

table 1):

EP OS

=

C

ω +

. ω

---

<!-- page 180 -->

Performance of a Lexical and POS Tagger for Sanskrit 167
Table 1. Results of the leave-one-out tests; refer to page 166 for the exact meanings of the columns

Lexical richness Avg. phrase length Analyzed correctly (C) Error: lexical analysis (eLEX ) Error: diﬀ. word classes (eP OS1) Error: case, number (eP OS2) Error: gender (eP OS3) Error: tense, mode (eP OS4) More than one non-lexical error (eP OS5) Hit rate Lex. hit rate

Text

Rasaratnasamuccaya- 0.18 9.8 9986 800 8 357 299 1 234 0.855 0.932

t.¯ıka¯ Rasaman˜jar¯ı

0.22 7.2 10550 694 5 576 244 0 281 0.854 0.944

Bha¯vapraka¯´sa

0.25 7.0 11096 878 2 314 280 0 161 0.872 0.931

Lan˙ ka¯vata¯rasu¯tra

0.16 11.6 9305 1730 17 347 254 3 388 0.773 0.856

Rasendracinta¯man. i Bodhicarya¯vata¯ra

0.25 7.7 10845 922 4 555 337 0 244 0.840 0.929 0.21 7.4 11257 1219 10 520 288 5 198 0.834 0.910

Ya¯jn˜avalkyasmr. ti Gokarn. apura¯n. asa¯rah. S´a¯rn˙ gadharasam. hita¯-
d¯ıpika¯

0.27 7.0 11764 1059 19 557 234 1 150 0.853 0.923 0.19 6.6 12497 1100 18 431 220 4 144 0.867 0.924 0.17 8.1 12449 833 2 532 372 1 305 0.859 0.943

Da´sakuma¯racarita

0.28 16.9 12081 1283 19 439 357 5 252 0.837 0.911

Rasapraka¯´sasudha¯kara 0.19 7.4 13263 988 2 608 288 2 219 0.863 0.936

Skandapura¯n. a Rasendracu¯d. a¯man. i

0.20 6.8 13827 1242 15 559 317 6 157 0.858 0.923 0.21 7.2 15417 888 9 553 345 0 335 0.879 0.949

Vis.n. usmr. ti

0.24 5.7 15071 1378 29 809 371 4 257 0.841 0.923

Buddhacarita

0.20 9.1 15748 1485 22 723 536 5 237 0.840 0.921

Mr. gendrat.¯ıka¯ Sa¯tvatatantra

0.16 12.4 17443 1902 23 705 569 5 478 0.826 0.910 0.30 7.1 6240 1259 4 309 143 0 1923 0.632 0.873

Artha´sa¯stra

0.29 9.3 8877 962 5 450 318 0 248 0.817 0.911

Hitopade´sa

0.23 7.1 9822 900 12 414 167 3 77 0.862 0.921

Rasaratnasamuccaya 0.18 7.2 23311 1656 5 1175 672 1 546 0.852 0.939

Mugdha¯vabodhin¯ı

0.13 12.7 24613 2087 20 1268 797 0 443 0.842 0.929

Rasa¯rn. ava

0.13 6.8 26198 1895 10 1427 1031 1 711 0.838 0.939

Manusmr. ti A¯ yurvedad¯ıpika¯

0.17 7.0 31177 2728 57 1650 890 9 342 0.846 0.926 0.12 12.8 31355 2834 51 1259 902 10 545 0.848 0.923

Ku¯rmapura¯n. a Bha¯gavatapura¯n. a Br. hatkatha¯´sloka-

0.14 6.6 33308 2856 26 1244 715 17 391 0.864 0.926 0.17 7.1 33840 4076 76 1958 1062 22 625 0.812 0.902 0.12 6.8 49372 5482 114 1997 1401 28 864 0.833 0.907

sam. graha A¯ nandakanda

0.11 6.9 68767 5896 17 3720 1731 17 1791 0.839 0.928

Carakasam. hita¯ Skandapura¯n. a (2) Matsyapura¯n. a Lin˙ gapura¯n. a Su´srutasam. hita¯ Ra¯ma¯yan. a

0.11 10.5 73239 6830 157 3582 2189 79 1763 0.834 0.922 0.08 6.8 97348 7645 112 3951 1627 44 1250 0.869 0.932 0.10 6.8 101860 9805 141 3996 2518 25 1517 0.850 0.918 0.08 6.9 105185 10477 63 4137 3447 23 1557 0.842 0.916 0.09 8.9 113237 11904 209 5769 3809 30 2274 0.825 0.913 0.05 6.8 220398 18643 387 8292 4437 64 2619 0.865 0.927

---

<!-- page 181 -->

0.10 0.15 0.20 0.25

0.95

0.95

0.85

0.85

168 O. Hellwig
Figure 1 displays the boxplots of H, HLEX and EP OS. Since the analysis of Sanskrit diﬀers strongly from that of other languages, H and HLEX are hardly comparable with rates recorded in previous research. Obviously, however, both H and HLEX need signiﬁcant improvements in future versions of the program. If we take into account the complex considerations that the linguistic phenomena of composite creation and bahuvr¯ıhi make necessary for POS tagging of Sanskrit, the POS accuracy of SanskritTagger compares acceptably with POS error rates reported for less complex languages (μe P OS = 0.090, σe P OS = 0.035).
To go deeper into the details of table 1, we should try to determine the inﬂuence of literary features on the analysis quality. If lexical richness and the average phrase length are used to get an estimation of the complexity of a literary style, we get the four plots displayed in ﬁgure 2. Astonishingly, the correlations between these two features and the (lexical) hit rates are almost unnoticeable. This result is supported by inspecting linear regressions performed with these data none of whose parameters (intercept, slope) are signiﬁcant at the 10% level.
Fig. 1. Boxplots of the hit rates recorded in table 1; left: hit rate H, middle: lexical hit rate HLEX , right: POS error rate
In the introduction, we mentioned the theory that the amount of training data inﬂuences the analysis accuracy. To assess this theory, the analysis of the Rasaman˜jar¯ı was repeated using statistical key values that were calculated from randomly selected subsets of the text corpus. Figure 3 displays graphically the inﬂuence between the amount of training data and the analysis quality. Although the analysis accuracy obviously increases with the amount of training data, we achieve comparatively high rates of accuracy even when only 20% of the corpus are used for training. Therefore, it seems that substantial increases in the accuracy of the tagger cannot be achieved by increasing the size of the corpus, but only by improving the analysis procedures. Lexical errors. Errors in the lexical analysis constitute the major part of the errors made by SanskritTagger. Since a reduction of this class of errors would strongly increase the accuracy of the tagger, we should detail the subclasses of this kind of error:

0.75

0.75

---

<!-- page 182 -->

Performance of a Lexical and POS Tagger for Sanskrit 169

0.5 0.6 0.7 0.8 0.9 1.0

0.5 0.6 0.7 0.8 0.9 1.0

Lexical hit rate

Hit rate

6 8 10 12 14 16

6 8 10 12 14 16

Avg. phrase length

0.5 0.6 0.7 0.8 0.9 1.0

0.5 0.6 0.7 0.8 0.9 1.0

0.05 0.10 0.15 0.20 0.25 0.30

0.05 0.10 0.15 0.20 0.25 0.30

Lexical richness

Fig. 2. Correlation between the average phrase length (upper row)/lexical richness (lower row) and the hit rate (left column)/lexical hit rate (right column)

Confusion of (partly) homonymous words. In most cases, homonyms belonging to diﬀerent declensional classes (e.g., adjectives and nouns) such as pr. thu = “broad” and pr. thu = “name of a man” are confused in this subclass. One of the most productive pairs of words that belongs to this error class is tad = “this” and the suﬃx t¯a, which denotes abstract nouns. Since the nominative and accusative plural of t¯a are identical with the nominative/accusative plural fem. of the pronoun, the program selects the much more frequent pronoun for the conﬁguration any word - t¯ah. as long as no overwhelming testimony for the pair any word - t¯a is recorded in the database. Less frequent are confusions of two or more homonymous nouns that are entered as diﬀerent lexemes in the dictionary. Among these cases, we

---

<!-- page 183 -->

170 O. Hellwig

0.95

0.85

0.75

20% 40% 60%

80% 100%

Fig. 3. Accuracy of SanskritTagger (y-axis) correlated with the size of the training corpus (x-axis); the solid line indicates the lexical hit rate and the dashed line the hit rate (cmp. page 2)

ﬁnd, for example, the triple ´siva (m.) = “the god S´iva”, ´siva (n.) = “bliss”, and ´siva (adj.) = “auspicious”, some of whose inﬂected forms are identical. Another subtype comprised in this class pertains to comparatively few lexemes, but contributes much to the lexical error rate: When inﬂected forms of nouns or adjectives are recorded as independent lexical items in the dictionary, the lexical analysis often has problems to distinguish between these – ﬁnally identical – instances. Examples are pra¯ya (m.)/pra¯yen. a (adv.), pratyaha (adj.)/pratyaham or ¯a´su (adj.)/¯a´su (adv.).
Inﬁnite verbal forms. This category partly coincides with the preceeding one. Frequently, gerundives or participles are included as independent lexical items in the dictionary. Examples are h¯asya (adj.) = “ridiculous” and h¯asya as the gerundive of the root has or karta¯ = nom. sg. of kart.r (adj.) = “doing” or as the periphrastic future of the verb k.r. The Monier-Williams, from which the lexical database of SanskritTagger is built, contains a large number of such lemmatized participles. If the meaning of such lemmata can be derived directly from the meaning of the root (e.g., sam. jiha¯na), these lemmata are removed from the digital dictionary. Although this – still ongoing – manual cleanup is time consuming, it reduces the number of alternatives and thus the possibilities of lexical errors. Some few lemmatized participles have developed independent meanings and are therefore kept in the dictionary (e.g., vidagdha= “clever” or samuddhata = “arrogant”). In spite of these improvements, there remains a group of high frequency lemmatized participles such as sat = “good” or k.rta that are responsible for the majority of errors in this class.
Segmentation errors. In this class, two types of errors can be distinguished. The ﬁrst one is caused by redundancies found in the Monier-Williams. If the dictionary contains both a composite noun and the components constituting

---

<!-- page 184 -->

Performance of a Lexical and POS Tagger for Sanskrit 171
it, a substring wi corresponding to the composite noun can be analyzed in two ways. An example is the term suh.rdv¯akya for which the MonierWilliams gives the meaning “the advice of a friend” and whose components suh.rd and v¯akya are also recorded in the dictionary. Obviously, the lemma suh.rdv¯akya is redundant because its meaning can be derived directly from the meaning of its components when standard rules of compound analysis are applied. Similar to most of the lemmatized participles mentioned above, such lemmata should therefore be removed from the digital dictionary. The second class of errors are real missegmentations, which are comparatively rare.
3 Conclusions and Future Developments
To our knowledge, the tests described in this paper have yielded the ﬁrst reliable estimations of error rates that occur during the automatic processing of Sanskrit using an unrestricted dictionary and texts from diverse knowledge domains. The largest group of errors consists of lexical misinterpretations, which are mostly caused by high frequency homonyms and redundancies in the digital dictionary. While the redundancies will be reduced by an ongoing revision of the dictionary, the homonyms pose a serious challenge to the computational analysis of Sanskrit. Considering the weak correlation between the amount of training data and the accuracy of the tagger, we cannot expect these and similar errors will disappear with an increasing size of the text corpus. Manually designed decision rules or a more detailed context analysis may oﬀer a way out of this problem. When compared with results reported for other languages, the POS error rate of SanskritTagger is still too high. A combination of morphological and syntactic analysis steps may help to decrease the frequency of this error; however, the basic steps necessary for such an analysis have ﬁrst to be implemented in SanskritTagger. In conclusion, the results reported in this paper indicate that the three steps of analysis should be merged into one step in future versions of SanskritTagger.
References
1. Csernel, M., Patte, F.: Critical edition of Sanskrit texts. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 358–379. Springer, Heidelberg (2009)
2. Hal´acsy, P., Kornai, A., Oravecz, C., Tr´on, V., Varga, D.: Using a morphological analyzer in high precision POS tagging of Hungarian. In: Proceedings of 5th Conference on Language Resources and Evaluation (LREC), Citeseer, pp. 2245–2248 (2006)
3. Haque, W., Aravind, A., Reddy, B.: Pairwise sequence alignment algorithms: a survey. In: Proceedings of the 2009 conference on Information Science, Technology and Applications, pp. 96–103 (2009)
4. Hellwig, O.: SanskritTagger, a stochastic lexical and POS tagger for Sanskrit. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 266–277. Springer, Heidelberg (2009)

---

<!-- page 185 -->

172 O. Hellwig
5. Leech, G., Garside, R., Bryant, M.: CLAWS4: The tagging of the British National Corpus. In: Proceedings of the 15th International Conference on Computational Linguistics, Kyoto pp. 622–628 (1994)
6. Marcus, M.P., Marcinkiewicz, M.A., Santorini, B.: Building a large annotated corpus of English: The Penn Treebank. Computational Linguistics 19(2), 313–330 (1993)
7. Megyesi, B.: Improving Brill’s POS tagger for an agglutinative language, pp. 275– 284.
8. Sproat, R., Shih, C.: Corpus-based methods in Chinese morphology and phonology. In: Proceedings of the 19th International Conference on Computational Linguistics (2002)
9. Weischedel, R., Schwartz, R., Palmucci, J., Meteer, M., Ramshaw, L.: Coping with ambiguity and unknown words through probabilistic models. Computational Linguistics 19(2), 360–382 (1993)

---

<!-- page 186 -->

The Knowledge Structure in Amarako´sa
Sivaja S. Nair and Amba Kulkarni
Department of Sanskrit Studies, University of Hyderabad, Hyderabad
sivaja.s.nair@gmail.com, apksh@uohyd.ernet.in
Abstract. Amarako´sa is the most celebrated and authoritative ancient thesaurus of Sanskrit. It is one of the books which an Indian child learning through Indian traditional educational system memorizes as early as his ﬁrst year of formal learning. Though it appears as a linear list of words, close inspection of it shows a rich organisation of words expressing various relations a word bears with other words. Thus when a child studies Amarako´sa further, the linear list of words unfolds into a knowledge web. In this paper we describe our eﬀort to make the implicit knowledge in Amarako´sa explicit. A model for storing such structure is discussed and a web tool is described that answers the queries by reconstructing the links among words from the structured tables dynamically.
Keywords: Amarako´sa, Synset, Polysemy, Semantic relations, Ontology.
1 Introduction
The Indian tradition of transmitting knowledge orally is on the verge of extinction. As the oral transmission demands, Indian traditional educational culture was organised to be formal and intensive as opposed to the modern culture which is more informal and extensive (Wood, 1985). In traditional circumstances, a child would receive his education largely by oral transmission, mainly through rote-learning. The method employed was through recitation and remembering. A child is taught the alphabet (varn. am¯ala¯), he would memorise a few verses, subha¯s.itas, and then start reciting a dictionary of synonymous words – the Amarako´sa – till it is memorised. It typically would take anywhere between 6 months to a year to memorise a list of approximately 10,000 Sanskrit words arranged as a list of synonyms. The close inspection of the structure of the Amarako´sa gives much more insight into the way the words are organised. When a student memorises it, though in the beginning it appears as a linear list of words, as he starts understanding the meaning of the words, reads the commentaries on this text and starts using these words, the linear structure unfolds into a knowledge web with various links.
The Amarako´sa printed in the form of a book just shows the linear order, and the index at the end of the book point to various words for easy references. But there is much more to it than just a linear order. The knowledge a student acquires through various commentaries and also its practical use in his own ﬁeld of
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 173–189, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 187 -->

174 S.S. Nair and A. Kulkarni
expertise – be it A¯yurveda, Vy¯akaran. a or S¯ahitya, is in the form of various links. With the modern education culture that is dominated by the use of computers as a tool, which relies more on the secondary memories such as books, computers, and the World Wide Web, than the human memory, it is necessary to make the implicit knowledge in Amarako´sa explicit. The computers have an advantage over the printed books. Computers can represent multi-dimensional objects, and thus one can navigate through the whole structure and at the same time with the powerful search facilities can search complex queries. In this paper, we illustrate with examples various kinds of links one can ‘visualise’ in Amarako´sa, and provide a database model to store these links in order to facilitate automatic extraction of these links as an answer to a search query.
2 Amarako´sa
Amarako´sa primarily named N¯amalin˙ g¯anu´s¯asana (a work that deals with instructions related to the gender of nouns) is authored by Amarasim. ha - 4th century A.D. (Oka, 1981) - and is the most celebrated and authoritative ancient thesaurus of Sanskrit with around 60 commentaries and translations into modern Indian as well as foreign languages such as Chinese, Tibetan, French, etc. (Patkar, 1981). It is considered as an essential requisite for a Sanskrit scholar and as such a child is asked to memorise it even before he starts his studies formally. It consists of 1608 verses composed in anus.t.up meter1 and are divided into 3 chapters called K¯an. d. as.2
Classiﬁcation. Each of the three k¯an. d. as is further subdivided into various vargas. The classiﬁcation of three k¯an. d. as into 25 vargas is as given below.
– prathamak¯an. d. am: svargavargah. (heaven) vyomavargah. (sky) digvargah. (direction) k¯alavargah. (time) dh¯ıvargah. (cognition) ´sabda¯divargah. (sound) n¯at.yavargah. (drama) p¯ata¯labhogivargah. (nether world) narakavargah. (hell) v¯arivargah. (water)
– dvit¯ıyaka¯n. d. am: bhu¯mivargah. (earth) puravargah. (towns or cities)
1 ´sloke s.as.t.am. gurum. jn˜eyam. sarvatra laghu pan˜camam | dvicatuh. p¯adayorhrasvam. saptamam. d¯ırghamanyayoh. ||
2 And as such is known as Trika¯n. d.¯ı.

---

<!-- page 188 -->

The Knowledge Structure in Amarako´sa 175

´sailavargah. (mountains) vanaus.adhivargah. (forests and medicines) sim. h¯adivargah. (lions and other animals) manus.yavargah. (mankind) brahmavargah. (priest tribe) ks.atriyavargah. (military tribe) vai´syavargah. (business tribe) ´su¯dravargah. (mixed classes)
– tr. t¯ıyaka¯n. d. am: vi´ses.yanighnavargah. (adjective) sam˙ k¯ırn. avargah. (miscellaneous) n¯ana¯rthavargah. (polysemous) avyayavargah. (indeclinables) lin˙ ga¯disan˙ grahavargah. (gender)
Amarako´sa contains 11,580 content words (tokens). Some of the tokens are repeated either within a ka¯n. d. a or across the ka¯n. d. as leading to only 9,031 types. The k¯an. d. a-wise distribution of the tokens and types is shown in Table 1.

Table 1. Tokens and types in each k¯an. d. as

ka¯n. d. a

tokens types

prathamaka¯n. d. am 2465 2300

dvit¯ıyak¯an. d. am 5827 5282

tr. t¯ıyak¯an. d. am 3288 2271

Synset. A set of synonymous words is termed as a synset. Each synonym may span over one or more verses. The following verse, e.g., provides a synonym for the word jam. buka.
striy¯am ´siva¯ bhu¯rima¯yagom¯ayum.rgadhu¯rtak¯ah. | sr. g¯alavan˜cakakro.s.tupherupheravajambuk¯ah. ||2.5.5 ||
Polysemy. Amarako´sa has 4,017 synsets. Some of the words fall under more than one synset, and thus are ambiguous. Most of these polysemous words belong to the na¯n¯arthavarga of the third ka¯n. d. a which lists the polysemous words alphabetically according to their endings. The polysemy distribution in the Amarako´sa is summarised in Table 2. There is only one word hari in Amarako´sa which has as many as 14 senses, the word antara belongs to 13 synsets, and the word go has 12 synsets. We note that almost 65% words (7459 words) belong to a single synset and thus are not ambiguous.
Gender. A few verses in the beginning of the Amarako´sa describe the metalanguage and the techniques employed to indicate the gender of various words. The word striya¯m, for example, in (2.5.5) above is not a token but a word

---

<!-- page 189 -->

176 S.S. Nair and A. Kulkarni

Table 2. Polysemy distribution

No. of meanings No. of words Words

14

1

hari

13

1

antara

12

1

go

10

2

kriy¯a, ku¯.ta

9

2

rasa, vr. s. a

8

8

dh¯atu, dharma, vasu, ari.s.ta...

7

9

6

18

5

49

4

136

3

330

2

1015

1

7459

from the meta-language indicating the gender of the following word ´siv¯a to be feminine. In addition to these general guidelines, in the lin˙ g¯adisan˙ grahavarga Amarasim. ha gives certain grammatical and phonological clues for deciding the gender of a word. In the event of absence of any rule, the gender of the remaining words in 2.5.5, constituting two compound words ”bhu¯rim¯ayagoma¯yum.rgadhu¯rta k¯ah. ” and ”s.rg¯alavan˜cakakro.s.tupherupheravajambuka¯h. ” is inferred to be masculine from their compounding-forms.
The avyayavarga lists synsets consisting of indeclinables.
3 Organisation of Synsets within a Varga
Except the polysemous words (n¯an¯arthavarga), all other synsets in a varga show some semantic relation to the varga it belongs to and sometimes even to the preceding or following synsets. These semantic relations indicate various kinds of relations. They may be classiﬁed as hierarchical or associative. The hypernym indicating a more general term or the hyponym showing a more speciﬁc term are the examples of hierarchical relation. Similarly the holonym-meronym relation marking the whole-part relation is also a hierarchical relation. In addition various other relations are indicated by the adjacency of the synsets. These may be termed as associative relations, which indicate some kind of association of one synset with the other. This association may be the association among human beings, or the association of certain objects with certain other objects. We illustrate below some such relations with examples.
3.1 Example 1: Vis.n. uh.
The verses from 1.1.18 to 1.1.29 describe various synsets representing Vis. n. u, and objects related to/associated with Vis.n. u. The relations, as is evident from the

---

<!-- page 190 -->

The Knowledge Structure in Amarako´sa 177 following description, are kinship relations such as father, brother, son, grandson, wife, and also associated objects such as conch, discus, sword, vehicle, etc. (See Figure 1). Vis.n. uh. (1.1.18 - 1.1.22)3
Kr.s.n. a’s father (1.1.22) Kr.s.n. a’s elder brother (1.1.23 - 1.1.24) k¯amadevah. (1.1.25 - 1.1.26)
ﬂoral arrows of ka¯madevah. (1.1.26) physical arrows of ka¯madevah. (1.1.26) son of ka¯madevah. - aniruddhah. (1.1.27) wife of Vis.n. uh. - laks.m¯ı (1.1.27) Special devices/equipments of Vis.n. uh. (1.1.28) (conch, discus, sword, jewel, bow, horse, mark,etc.) Kr.s.n. a’s charioteer, minister (1.1.28) Kr.s.n. a’s younger brother (1.1.28) Vis.n. u’s vehicle - garud. ah. (1.1.29)
Fig. 1. Relations of Vis.n. u 3.2 Example 2: Samayah. The verses from 1.4.1 to 1.4.9 deal with words related to time, units of measurement, special names of special days, etc. Time (1.4.1)
Lunar day (1.4.1) First lunar day (1.4.1)
{Day (1.4.2) Morning (1.4.2 - 1.4.3)
3 The English translations of the subheadings, which are given here and in the following examples, describing the ´slokas are taken from Colebrooke’s commentary on Amarako´sa (Colebrooke, 1808).

---

<!-- page 191 -->

178 S.S. Nair and A. Kulkarni
Twilight (1.4.3) Evening (1.4.3) First four hours of a day (1.4.3) Second four hours of a day (1.4.3) Third four hours of a day (1.4.3) Period of the day (1.4.3) Night (1.4.3 - 1.4.4)
A dark night (1.4.5) A moonlight night (1.4.5) A night and two days (1.4.5) First part of night (1.4.6) Midnight (1.4.6) Sequence of nights (1.4.6) Space of three hours (1.4.6) } Last day of the half month (1.4.7) Precise moment of the full or the new moon (1.4.7) Full moon day (1.4.7) Full moon whole day(1.4.8) Full Moon with a little gibbous on part of a day (1.4.8) No moon day (1.4.8) wanning crescent (1.4.9) No moon whole day (1.4.9)
In this example we also see violation of nesting. In between the synsets related to lunar day and last day of the month, the synsets related to day (which refers to the apparent solar motion) are intervened.
3.3 Example 3: Ks.atriyah.
Here is a group of verses from 2.8.1 to 2.8.10 belonging to the k.satriyavarga. The words here refer to the king, military, ministers, various category of people engaged in the services of kings, etc.
Man of the military tribe (2.8.1) King (2.8.1) Universal monarch (2.8.2) An emperor (2.8.2) King over a country (2.8.2) Paramount sovereign (2.8.3) Multitude of kings (2.8.3) Multitude of military tribe (2.8.4) Minister (2.8.4) Deputy minister (2.8.4) Priest (2.8.5) Judge (2.8.5) King’s companions (2.8.5)

---

<!-- page 192 -->

The Knowledge Structure in Amarako´sa 179

(2.8.9)

Body guards of a king (2.8.6) Warder (2.8.6) Superintendent (2.8.6)
Village Superintendent (2.8.7) Superintendent of many villages (2.8.7) Superintendent of Gold (2.8.7) Superintendent of Silver (2.8.7) Superintendent of the womens’ appartments (2.8.8)
Outside guard of the womens’ appartment (2.8.8) attendant of a king (2.8.9)
eunuch (2.8.9) Prince whose territories lie on the frontiers of those of the enemy
Neighboring prince (2.8.9) Prince whose territories lie beyond those of the friend (2.8.10) Enemy in the rear (2.8.10)

3.4 Implicit Relations
These were three samples from three distinct topics involving totally diﬀerent kind of relations. All these relations are semantic in nature. A more detailed study of such examples showed that following relations occur more frequently.
– avayava¯vayav¯ı (part-whole relation) – para¯para¯ja¯ti (is a kind of relation) – janyajanaka (child-parent relation) – patipatn¯ı (husband-wife relation) – svasv¯ami (master-possession relation) – ¯aj¯ıvika¯ (livelihood)
There are a few other relations such as kinship relations, ¯adh¯ara-¯adheya, vam. ´savam. ´s¯ıya etc. The extraction of such relations and marking is still ongoing. But the instances of such relations were found to be rare.

4 Amarako´sa-jn˜¯ana-j¯ala
In the recent past there have been notable eﬀorts by Sanskrit computational linguists with focus on Amarako´sa. Jha et. al. (2010, Online Multilingual Amarakosha) have developed a searchable web interface to Amarako´sa which provides the Indian language equivalents of the Amarako´sa words in addition to the original sanskrit text. Bharati et. al. (2008) and Nair et. al. (2009) did comparative study of the Amarako´sa with the existing Hindi WordNet in order to ﬁnd the usefulness of Hindi WordNet in augmenting the Amarako´sa with relational information. There have been eﬀorts by Kulkarni et. al. (2008, 2010) that describe the development of Sanskrit WordNet. The present eﬀort is altogether an innovative eﬀort that helps reveal the internal structure of the Amarako´sa.

---

<!-- page 193 -->

180 S.S. Nair and A. Kulkarni
The Amarako´sa-jn˜a¯na-ja¯la is developed as a web application. The application provides a search result of a query dynamically generated using the structured lexicon of the Amarako´sa and the supplementary tables marking the relations.
The structured lexicon as well as the supplementary tables showing the explicit relations are simple ASCII text ﬁles. Sanskrit words are stored in a roman transliterated scheme (WX notation).4 There are two advantages of storing the text in WX notation. The ﬁrst advantage is, it facilitates a lexicographer to use simple unix tools such as grep, sed, etc. for her day-to-day work of updating the knowledge-base. Unicode for Devanagari mixes the phonemes with the syllables, making it un-natural to write the search expressions. The second advantage, of course, is the size. The size of the tables in UTF-8 for Devanagari is more than 2 times the corresponding ﬁles in roman transliteration such as WX notation.
4.1 Structured Lexicon
The main structured lexicon consists of synsets stored in the form of a set of records. Each record corresponds to a word in the Amarako´sa (excluding the meta-language words). It consists of 5 ﬁelds as described below.
Stem. Amarako´sa lists words in nominative cases. However, we decided to go for the nominal stem instead of the nominative case word form. In case of feminine words, this ﬁeld contains the feminine stem, i.e. the stem after adding the feminine suﬃx. In case of na¯n¯arthavarga (part of the Amarako´sa dealing with polysemous words), the polysemous word is entered in this ﬁeld.
The reason for choosing nominal stem over the nominative case form is the ease in linking the Amarako´sa words with the existing computational resources such as morphological analysers and generators and various e-lexicons, which typically expect a pra¯tipadikam and not a prathama¯nta (ending in nominative case).
Amarako´sa index. This ﬁeld contains a reference to an entry in the Amarako´sa, as a 5 tuple of numbers, separated by dots. The 5 numbers in the 5 tuple refer to the k¯an. d. a, varga, ´sloka, p¯ada and the word number respectively. Table 3 shows a sample entry corresponding to the following ´sloka,
svaravyayam. svargan¯akatridivatrida´s¯alaya¯h. | suraloko dyodivau dve striya¯m´ kl¯ıbe trivis..tapam || 1.1.6 ||
Lin˙ gam (gender). This ﬁeld contains the gender of the stem. The gender of a word in a ´sloka is decided with the help of meta-language employed by Amarako´sa. These are further cross checked with Devadatta Tiwari’s Devako´sa arth¯at Amarako´sa (Tiwari, 1989) and Colebrooke’s commentary on Amarako´sa (Colebrooke, 1808) when in doubt.
Sanskrit has 3 values for gender viz. masculine, feminine and neuter. Thus there are 8 possible combinations (an indeclinable is assigned no gender, and
4 http://sanskrit.uohyd.ernet.in/˜anusaaraka/sanskrit/samsaadhanii/wx.html

---

<!-- page 194 -->

The Knowledge Structure in Amarako´sa 181

Table 3. Words and references of the svarga-synset

Word Reference

svar

1.1.6.1.1

svarga 1.1.6.1.2

na¯ka

1.1.6.1.3

tridiva 1.1.6.1.4

trida´s¯alaya 1.1.6.1.5

suraloka 1.1.6.2.1

dyo

1.1.6.2.2

div

1.1.6.2.3

trivis.t.apa 1.1.6.2.4

the adjectives are the ones which take all the three genders). In addition, Amarako´sa also provides information about words that are always plural or dual by nature. Following combinations of gender, number information were found in the Amarako´sa.
– Indeclinable - (avya.) – Feminine - (str¯ı.) – Masculine - (pum. .) – Neuter - (napum. .) – Masculine and Feminine - (str¯ı-pum. .) [a´sani5] – Feminine and Neuter - (str¯ı-napum. .) [ud. u6] – Feminine dual - (str¯ı-dvi.) [dya¯v¯apr.thvyau7] – Feminine plural - (str¯ı-bahu.) [apsaras8] – Masculine and Neuter - (pum. -napum. .) [daivata¯ni9] – Masculine dual - (pum. -dvi.) [na¯satyau10] – Masculine plural - (pum. -bahu.) [gr.ha¯h. 11] – Neuter and indeclinable - (napum. -avya.) [apadi´sam. 12] – Adjective - (vi.)

Vargah. . This ﬁeld contains the name of the varga, as given in the commentaries to which the entry belongs.
Head Word. The ﬁrst four ﬁelds cover all the explicit information that can be easily extracted automatically. The important feature of Amarako´sa is that it provides synonymous words. The marking of synonymous words is obvious only
5 a´sanirdvayoh. (1.1.47) 6 ta¯raka¯pyud. u v¯a striya¯m. (1.3.21) 7 dy¯ava¯pr.thvyau (2.1.19) 8 striya¯m. bahus.vapsarasah. (1.1.52) 9 daivata¯ni pum. si va¯ (1.1.9) 10 na¯saty¯ava´svinau dasr¯av¯a´svineyau ca ta¯vubhau (1.1.51) 11 gr.h¯ah. pum. si ca bhu¯mnyeva (2.2.5) 12 kl¯ıb¯avyayam. tvapadi´sam (1.3.5)

---

<!-- page 195 -->

182 S.S. Nair and A. Kulkarni

through the world knowledge or through the commentaries. To provide a handle to each set of synonymous words – called as synset, we created a ﬁeld termed as Head Word which provides a name to each synset. Thus these Head Words are unique and act as a reference ID for a synset. The total number of Head Words give us the total number of synsets in the Amarako´sa. We denote the synset corresponding to a Head Word W by Syn(W).
The choice of Head-Words is mainly guided by the Bha¯nuji D¯ıks.ita¯’s Sudha¯ commentary on Amarako´sa (Pandit, 1915). When a better choice was available in the Malayalam commentary Triven.¯ı (Moosath, 1956) or Pa¯rame´svar¯ı (Moosath, 1914) or the Hindi commentary Prabh¯a, it was chosen. Table 4 shows an example of a ´sloka 2.5.5 converted to a structured table, and ﬁgure 2 shows the search result of the Amarako´sa-jn˜a¯na-j¯ala for the word ´sr.ga¯la.

4.2 Tables Marking Various Relations
The relations are among various Head Words and are marked as records. Each record corresponds to one synset ID. The ﬁrst ﬁeld of each record consists of the synset ID, and remaining six ﬁelds correspond to the Head Words that bear a relation of is a part of (avayav¯avayavi), is a kind of(par¯apara¯ja¯ti), janyajanaka-bha¯va, pati-patn¯ı-bha¯va, sva-sva¯mi-bha¯va, ¯aj¯ıvik¯a with the synset ID in the ﬁrst ﬁeld.

Table 4. Example of Head-Word

Token

Reference Gender Varga-name Head-Word

´siva¯

2.5.5.1.1

bu¯rim¯aya 2.5.5.1.2

gom¯ayu 2.5.5.1.3

mr.gadu¯rtaka 2.5.5.1.4

´sr. ga¯la

2.5.5.2.1

van˜jaka

2.5.5.2.2

kr.os.t.u pheru

2.5.5.2.3 2.5.5.2.4

pherava 2.5.5.2.5

jam. buka 2.5.5.2.6

str¯ı
pum. pum. pum. pum. pum. pum. pum. pum. pum.

sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah. sim. ha¯divargah. jam. bhu¯kah.

Fig. 2. Example of a synset

---

<!-- page 196 -->

The Knowledge Structure in Amarako´sa 183
1. Is a part of (avayava¯vayavi) This ﬁeld marks is a part of relation. Let W be the synset-ID. Then this ﬁeld will have an entry W’ if the member of SynW is a part of member of SynW’ (See Table 5).
For example, Syn(ra¯trih. )=´sarvar¯ı, k.san. ad¯a, k.sap¯a, ni´sa¯, ni´s¯ıthin¯ı, rajan¯ı, ra¯tri, vibha¯var¯ı, tamasvin¯ı, tam¯ı, triy¯ama¯, ya¯min¯ı, naktam, do.sa¯, vasati, ´sy¯ama¯. and Syn(ra¯trimadhyah. ) = ardhara¯tra, ni´s¯ıtha.
Now, ardhar¯atra, ni´s¯ıtha are part of ni´sa¯, rajan¯ı, r¯atri, etc.. Hence ra¯trimadhyah. is marked to be is a part of (avayava of) ra¯trih. Similarly prados. a, rajan¯ımukha (∈ Syn(ra¯tripra¯ram. bhah. )) are also part of ni´s¯a, rajan¯ı, r¯atri, etc.. Hence ra¯tripra¯ram. bhah. , where Syn (ra¯tripra¯ram. bhah. )= prados. a, rajan¯ımukha also bears a part of relation with ra¯trih. .
Table 5. Example of is-a-part relation
Head-Word W part (avayava)-of W r¯atrimadhyah. r¯atrih. r¯atripra¯ram. bhah. r¯atrih.

2. Is a kind of (para¯para¯j¯ati) This ﬁeld marks is a kind of relation. The entry contains the Head Word W’ such that synset ID W bears a relation of is a kind of with W’. The hypernymy and hyponymy relation can be extracted using this ﬁeld. Here are some entries: (see Table 6.)

Table 6. Example of is a kind of relations

Head-Word W kind (par¯aja¯tih. ) of W

gan˙ ga¯

nad¯ı

yamun¯a

nad¯ı

narmada¯

nad¯ı

3. Janya-janaka-bh¯ava (parent-child relation)
This ﬁeld marks the relation of parent-child (janya-janaka-bh¯ava). (see
Table 7.) Where Syn (jayantah. ) = pa¯ka´s¯asani, jayanta. and
Syn (indrah. ) = indra, bid. aujas, maghavan, marutvat, pa¯ka´sa¯sana, sun¯as¯ıra, vr. ddha´sravas, purandara, puruhu¯ta, ji.sn. u, lekhar.sabha, ´sakra, ´satamanyu, divaspati, vr. .san, v.rtrahan, gotrabhid, sutr¯aman, v¯asava, vajrin, bala¯ra¯ti,

---

<!-- page 197 -->

184 S.S. Nair and A. Kulkarni
´sac¯ıpati, surapati, v¯asto.spati, harihaya, jambhabhedin, namucisu¯dana, svar¯aj, meghav¯ahana, san˙ krandana, tura¯s.¯a, du´scyavana, a¯khan. d. ala, .rbhuks. in, sahasra¯ks. a, kaus. ika, ghan¯aghana, parjanya, hari.
Syn (sanatkuma¯rah. ) = sanatkum¯ara, vaidha¯tra and Syn (brahm¯a) = a¯tmabhu¯, brahman, catura¯nana, hiran. yagarbha, loke´sa, parames..thin, pita¯maha, surajye.s.tha, svayambhu¯, abjayoni, an. d. aja, ham˙ sav¯ahana, kamala¯sana, kamalodbhava, n¯abhijanman, nidhana, praja¯pati, pu¯rva, rajomu¯rtin, satyaka, sad¯ananda, sva.s.tr., vedhas, virin˜ci, vi´svas.rj, vidh¯atr. , vidhi, dh¯atr. , druhin. a, ka, ¯atman, ´sambhu.

Table 7. Example of Janya-janaka relation

Head-Word W Child (janya) of W

indrah.

jayantah.

brahm¯a

sanatkuma¯rah.

´sivah.

gan. e´sah.

4. Pati-patn¯ı-bha¯va (husband-wife relation)
This ﬁeld marks the husband-wife relation, as shown below. (see
Table 8.) Where Syn(lak.sm¯ı) = bh¯argav¯ı, haripriya¯, indiraa¯, kamal¯a, ks.¯ırasa¯garakanyak¯a, k.s¯ırodatanaya¯, laks. m¯i, lokajanan¯ı, lokam¯atr. , m¯a, padma¯, padm¯alaya¯, rama¯, ´sr¯ı, v.r.sa¯kap¯ay¯ı. and
Syn(vis. n. uh. ) = hr. .s¯ıke´sa, ke´sava, kr. .sn. a, m¯adhava, n¯ara¯yan. a, svabhu¯, vaikun. d. ha, vi.sn. u, vi.s.tra´sravas, d¯amodara, acyuta, garud. adhvaja, govinda, jan¯ardana, p¯ıt¯ambara, pun. d. ar¯ık¯aks. a, ´s¯arn˙ gin, vi.svaksena, daity¯ari, cakrap¯an. i, caturbhuja, indr¯avaraja, madhuripu, padmana¯bha, upendra, v¯asudeva, trivikrama, adhok.saja, balidhvam˙ sin, kam˙ s¯ara¯ti, purus.ottama, ´saur¯ı, ´sr¯ıpati, vanam¯alin, xevak¯ınandana, jala´s¯ayin, kai.tabhajit, mukunda, muramardana, narak¯antaka, pura¯n. apurus. a, ´sr¯ıvatsala¯n˜chana, vi´svambhara, vi´svaru¯pa, vidhu, yajn˜apurus. a, lak.sm¯ıpati, mura¯ri, aja, ajita, avyakta, vr. .sa¯kapi, babhru, hari, vedhas.

Table 8. Example of Pati-patn¯ı relation

Head-Word W Husband (pati ) of W

laks.m¯ı

vis.n. uh.

p¯arvat¯ı

´sivah.

lop¯amudra¯

agastyah.

---

<!-- page 198 -->

The Knowledge Structure in Amarako´sa 185

Table 9. Example of Sva-sv¯ami relation

Head-Word W master (sva¯mi ) of W

vis.n. oh. mantrih. vis.n. uh.

vis.n. oh. s¯arathih. vis.n. uh.

garud. ah.

vis.n. uh.

5. Sva-sv¯ami-bha¯va (master-possession relation) This ﬁeld marks the master-possession or sva-sv¯ami-bh¯ava relation as shown below: (see Table 9.)
6. A¯ j¯ıvika¯ (livelihood) This ﬁeld marks the livelihood relation between two syn-sets. For example, the synset with Head Word matsya is (an. d. aja, jhas. a, matsya, m¯ına, pr. thuroman, ´sakul¯ı, vais¯arin. a, vis¯ara, animi.sa) denotes objects which act as a livelihood for the objects expressed through the concept of dh¯ıvara, and hence the livelihood for the objects belonging to the synset dh¯ıvara is marked as a matsya. (see Table 10.)

Table 10. Example of A¯j¯ıvika¯ relation

Head-Word W Livelihood (A¯j¯ıvik¯a) of W

dh¯ıvarah.

matsyah.

nartak¯ı

nr.tyam

n¯avikah.

nauk¯a

sevakah.

sev¯a

4.3 Quantitative Analysis
For every headword, one or more of the relations as speciﬁed above are marked. As was expected, the hierarchical relations viz. is a kind of and is a part of appear prominently than the associative relations. The occurrence of various relations in terms of Head-Words and all the words belonging to the synsets denoted by these head words is shown in Table 1113.
4.4 Implementation
From the structured lexicon table and the table of relations we build data bases using the built-in dbm engines of unix and the programes are written in Perl. These dbm engines use hashing techniques to enable fast retival of the data by key.
Following three hash tables are built from the structured lexicon.
a) Head-word hash where Key=stem and Value=head-word
13 Till 16th April 2010

---

<!-- page 199 -->

186 S.S. Nair and A. Kulkarni

Table 11. Relational statistics

No. Relation Headwords Words

1 is a kind of 2239

6807

2 is a part of 560

1654

3 janya-janaka 17

193

4 sva-sv¯am¯ı 36

122

5 ¯aj¯ıvik¯a

30

106

6 pati-patn¯ı 25

105

b) Synset hash with Key=head-word and Value=synset
c) Word-info hash generated by Key=stem and Value=word-index and gender
From the table of relations, corresponding to each relation R, we built a hash table which returns the associates a head-Word W with another head-word W’, if W’ is related to W by relation R.
Amarako´sa-jn˜a¯na-ja¯la is presented as a web application developed with ’apache’ web server and ’perl’ for CGI script. User submits a query a word and a relation, machine produces all the words related to the given word by the chosen relation. The word here may be either a stem or an inﬂected word form. In the case of inﬂected word form, machine consults the morphological analyser to get the stem. Figures in appendix - 1 give sample results of queries for diﬀerent word-relation combinations. When a cursor is placed on a word a tool tip shows its word-index and gender(as shown in Fig. 2.).
5 Conclusion
The study of Amarako´sa from a point of view of exploring the relations was undertaken to reveal the implicit knowledge and make it explicit. The resulting computational tool helps a Sanskrit reader to get a feel for various kinds of relations mentioned in the Amarako´sa and thereby its richness as a knowledge source. The hierarchical relations such as is a part of and is a kind of will be of help in information extraction, while the associative relations help a reader to get the cultural knowledge.
Sanskrit has a rich tradition of ko´sas. Most of them are arranged as a list of words with similar meaning (synonymic) or a list of words indicating various shades of a given word (polesemic). N¯amama¯la¯, S´abdaratn¯akara, S´abdacandrik¯a are a few among the ﬁrst type and N¯ana¯rthasan˙ graha, Anek¯arthadhvaniman˙ jar¯ı, Vi´svapraka¯´sa are a few examples of the second type. Amarako´sa, Abhidh¯anaratnam¯ala¯ and Vaijayant¯ıko´sa has both kind of entries.

---

<!-- page 200 -->

The Knowledge Structure in Amarako´sa 187
This implementation may serve as a model to build similar tools for various other ko´sas mentioned above.
The Amarako´sa is now available with various kinds of search facilities as a web service at
http://sanskrit.uohyd.ernet.in/~anusaaraka/sanskrit/ samsaadhanii/amarakosha/home.html
References
1. Bharati, A., Kulkarni, A., Nair, S.S.: ‘Use of Amarakosha and Hindi WordNet in Building a Network of Sanskrit Words. In: International Conference On Natural Language Processing, C-DAC Pune (2008)
2. Colebrooke, H.T.: Kosha or Dictionary of the sungskrita language by Umura singha with an English interpretations and annotations. Serampore (1808)
3. Fellbaum, C.: WordNet An Electronic Lexical Database. MIT Press, Massachusetts (1999)
4. Jha, G.N., Chandrashekar, R., Singh, U.K., Jha, V.N., Pandey, S., Singh, S.K., Mishra, M.K.: Online Multilingual Amarako´sa: The Relational Lexical Database. In: 5th Global Wordnet Conference, IIT Mumbai (2010)
5. Kulkarni, M., Pushpak, B.: Verbal roots in the Sanskrit WordNet. In: 2nd International Sanskrit Computational Linguistics Symposium, Brown University (2008)
6. Kulkarni, M., Dangarikar, C., Kulkarni, I., Nanda, A., Bhattacharya, P.: Introducing Sanskrit Wordnet. In: 5th Global Wordnet Conference, IIT Mumbai (2010)
7. Moosath, P.T.C.: Paarameswarii: malayalam commentory of Amarakosha. National Book Stall, Kottayam (1914)
8. Moosath, P.T.C.: Triveni: malayalam commentory of Amarakosha. National Book Stall, Kottayam (1956)
9. Nair, S.S., Swain, P., Kulkarni, A.: Developing network of Sanskrit words across Part-Of-Speech categories. In: CSATS 2009, Rashtriya Sanskrit Vidhyapeeth, Tirupati (2009)
10. Oka, K.G.: The Namalinganushasana: Amarakosa of Amarasimha with the commentary (Amarakoshodghaatana) of Ksheraswamin. Upasana prakashan Delhi, Varanasi (1981)
11. Online Multilingual Amarakosha: http://sanskrit.jnu.ac.in/amara/index.jsp 12. Patkar, M.M.: History of Sanskrit Lexicography. Munshiram Manoharlal Publish-
ers Pvt. Ltd., Delhi (1981) 13. Pandit, S.: Namalinganusasana (Amarakosha) With the commentary of (Vyakhya-
sudha or Ramasrami) of Bhanuji Dikshit. Tukaram javaji proprietor of the “Nirnaya Sagar” Press, Bombay (1915) 14. Tiwari, D.: Devako`sah. ardha¯t amarako`sah. . Nag prakashak, Delhi (1989) 15. Wood, A.: Knowledge before printing and after – The Indian tradition in changing Kerala. Oxford University Press, Delhi (1985)

---

<!-- page 201 -->

188 S.S. Nair and A. Kulkarni
A Appendix - 1
Fig. 3. Example of ¯aj¯ıvika¯ Fig. 4. Example of avayav¯ı
Fig. 5. Example of avayava

---

<!-- page 202 -->

The Knowledge Structure in Amarako´sa 189 Fig. 6. Example of hypernymy Fig. 7. Example of hyponymy

---

<!-- page 203 -->

Gloss in Sanskrit Wordnet
Malhar Kulkarni, Irawati Kulkarni, Chaitali Dangarikar, and Pushpak Bhattacharyya
IIT Bombay, Mumbai, India {malhar,irawati,chaitali,pb}@iitb.ac.in
Abstract. Glosses and examples are the essential components of the computational lexical databases like, Wordnet. These two components of the lexical database can be used in building domain ontologies, semantic relations, phrase structure rules etc., and can help automatic or manual word sense disambiguation tasks. The present paper aims to highlight the importance of gloss in the process of WSD based on the experiences from building Sanskrit Wordnet. This paper presents a survey of Sanskrit Synonymy lexica, use of Navya-Ny¯aya terminology in developing a gloss and the kind of patterns evolved that are useful for the computational purpose of WSD with special reference to Sanskrit.
Keywords: Sanskrit Wordnet, Wordnet, Word Sense Disambiguation, Lexical databases, Sanskrit Lexicography.
1 Introduction
Wordnet is a lexical database. Words belonging to four lexical categories, i.e., noun, adjective, adverb and verb are stored in this database. Words are grouped in such a way that their cognitive synonym will form a set and this set will express a distinct concept. This set of cognitive synonyms is called ‘synset’. Synsets in a wordnet are interlinked by means of conceptual-semantic and lexical relations. The resulting network of meaningfully related words and concepts can be navigated with the browser.
The ﬁrst wordnet was built in 1985 for English language.1 Then followed wordnets for European languages: EuroWordNet.2 Since 2000, wordnets for a
1 WordNet R as a lexical database for English was developed at Princeton University under the direction of George A. Miller. The word “WordNet” (with capital N) is a registered trademark of Princeton English WordNet. Therefore, names of all other wordnets are written without capital N in it. WordNet’s latest version is 3.0. As of 2006, the database contains 155,287 words organized in 117,659 synsets for a total of 206,941 word-sense pairs. In a compressed form, WordNet database is about 12 megabytes in size. It is available for free online use at http://wordnetweb.princeton.edu/perl/webwn and can also be downladed from http://wordnet.princeton.edu/wordnet/download/
2 http://www.illc.uva.nl/EuroWordNet/
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 190–197, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 204 -->

Gloss in Sanskrit Wordnet 191
number of Indian languages are getting built, led by Hindi Wordnet3 eﬀort at Indian Institute of Techonlogy Bombay (IITB). All wordnets in the world are connected through Global Wordnet Association (GWA).4 Similar activity started in India with Hindi Wordnet. It was started in IIT Bombay and is going on for last eight years. As of now, wordnets are getting created for 16 out of 22 oﬃcial languages of India.5 IndoWordNet group is formed and wordnets for these 16 Indian languages are getting interlinked via Hindi Wordnet [3].
In this paper, we share our experience of building Sanskrit wordnet. Since it is built following expand model of wordnet creation, Sanskrit lexicographers create synsets based on base synsets of Hindi Wordnet. While creating synsets, lexicographers collect synonyms from traditional Sanskrit ko´sas and modern Sanskrit dictionaries. Ko´sas like S´abdakalpadruma and Va¯caspatyam contain Sanskrit glosses. These glosses are very much helpful in creating glosses in Sanskrit. But the etymology based approach of these traditional lexica can be very harmful in this ontology based lexical structure. Since glosses attached to the synsets can become helpful in disambiguating polysemous words, Sanskrit lexicographers take help from already existing wordnets and extract information from them to make Sanskrit glosses more reﬁned and apt. We also show how glosses, given in such a way can be helpful in disambiguating Sanskrit words in the context. Our approach draws a large amount of inputs from the challenegs IITB researchers faced while doing wordnet based word sense disambiguation task for Hindi and Marathi languages. We compare Hindi, Marathi and English glosses to make Sanskrit glosses more appropriate by adding distinct features of the concept in the gloss.
2 Importance of Gloss in Wordnet Structure
Synsets are the basic blocks of Wordnet. The member words of a synset perform the task of disambiguating the co-occurred words (which have multiple meanings). These words are helped in this task to a large extent by the glosses provided of the synsets. These glosses aim to capture the concept for which the words in the synset stand for. Thus they play a very crucial role from the structure of the Wordnet in particular and Word Sense Disambiguation (WSD) in general.
In general we attempt to study the various facets of this aspect of the Wordnet, namely ‘The Gloss’ on the basis of the experience in building Sanskrit Wordnet with expansion approach [4]. Further, in future, we aim to concentrate on the gloss of the verbs as given in the Sanskrit Wordnet and study the implications from WSD point of view.
3 http://www.cfilt.iitb.ac.in/wordnet/webhwn/ 4 List of all wordnets can be found at
http://www.globalwordnet.org/gwa/wordnet_table.htm 5 These languages are (1) Hindi, (2) Marathi, (3) Konkani, (4) Sanskrit, (5) Nepali,
(6) Kashimiri, (7), Assamese, (8) Tamil, (9) Malyalam, (10) Telugu, (11) Kannad, (12) Manipuri, (13) Bodo, (14) Bangla, (15) Punjabi and (16) Gujarati.

---

<!-- page 205 -->

192 M. Kulkarni et al.
2.1 Importance of Gloss in Wordnet from Computational Point of View
Computationally, the main importance of glosses attached to synsets is Word Sense Disambiguation. WSD is the problem of identifying the correct sense of the word given the context in which it appears. Many words have multiple senses. Humans can identify the correct sense of the word from the context. For example, when we encounter a sentence like shall we go to the bank for ﬁshing, we are able to recognize that the meaning of bank is river bank and not ﬁnancial institution from the contextual clue word ﬁshing. How can the computer do the same task?
WSD is important for any Natural Language Processing (NLP) application that involves understanding the meaning of words. These include Machine Translation (MT), Information Extraction (IE), Information Retrieval (IR), document summarization, question answering, etc. For example, in IR we can increase the precision of the retrieved documents by understanding the sense (meaning) of the words in user queries and retrieving documents pertaining to that sense.
WSD approaches can be divided into two broad categories: knowledge based and machine learning based. The latter again can be divided into supervised machine learning and unsupervised machine learning. We will describe the ﬁrst approach, viz., knowledge based approach which makes heavy use of glosses.
2.2 Knowledge Based Approach to WSD
Knowledge based approaches such as WSD using Selectional Preferences [8], Lesk’s algorithm [5], Walker’s algorithm [10], WSD using conceptual density [1] and WSD using Random Walk Algorithm [6] make use of dictionary deﬁnitions or glosses. They are easy to implement requiring only a lookup of a knowledge resource like a Machine Readable Dictionary (MRD). When the MRD is the wordnet, this lookup takes the form of consulting or overlapping gloss of synsets, synsets and recursively for semantically related synsets. Further, they do not require any corpus- tagged or untagged.
Illustration of the algorithm. Following Lesk (1986), we give an intersection similarity based WSD approach for Hindi WSD using Hindi Wordnet [7].6 For the word to be disambiguated, we call the collection of words from the CONTEXT of the word in question the Context Bag and the related words from the WORDNET as the Semantic Bag. Fig. 1 gives the pictorial view of the approach and table 1 gives the algorithm used in this approach.
The word ‘bag’ here means a set of words. ‘Context bag’ means the words in the context of the word that is candidate for disambiguation. Sense bag, on the other hand, means words which have various lexical and semantic links with the candidate word, as depicted in the wordnet. This would consist of synonyms, hypernyms, meronyms, words in gloss and so on.
We have used Intersection similarity to measure the overlap. The idea of Intersection similarity is to capture the belief that there will be high degree of
6 <http://www.cfilt.iitb.ac.in/wordnet/webhwn>

---

<!-- page 206 -->

Gloss in Sanskrit Wordnet 193
Fig. 1. Overlap of the Context Bag (words in the context) and Dictionary Bag (words of gloss and synsets
Table 1. Lesk like algorithm for WSD 1. For a polysemous word W needing disambiguation, a set of context words in its
surrounding window is collected. Let this collection be C, the context bag. The window is the current sentence and the preceeding and the f ollowing sentences. 2. For each sense s of W , do the following.
Let B be the bag of words obtained from the a. Synonyms in the synset. b. Glosses of the synsets. c. Example sentences of the synsets. d. Hypernyms (recursively up to the roots). e. Glosses of Hypernyms. f. Example sentences of Hypernyms (recursively up to the leaf). g. Glosses of Hyponyms. h. Example sentences of Hyponyms. i. Meronyms (recursively up to the beginner synset). j. Glosses of Meronyms. k. Example sentences of Meronyms.
Measure the overlap C and B using intersection similarity.7
overlap between the words in the context and the related words extracted from the WordNet for a sense, and that sense will be a winner sense. Evaluation. We perform Hindi WSD experiment on the corpora provided by Central Institute of Indian Languages (CIIL) , Mysore [9]. The system has been 7 The idea of intersection similarity is to capture the belief that there will be high
degree of overlap between words in a context and the related words extracted from wordnet for a sense, and that sense will be a winner sense [9].

---

<!-- page 207 -->

194 M. Kulkarni et al.

Fig. 2. Histogram showing the WSD accuracy across domains for Hindi Words

Table 2. WSD accuracy across domains for Hindi Words

Domain

Percentage of Accuracy

Agriculture

73.20

Science and Sociology

64.40

Sociology

60.22

Short-Story

42.22

Mass-Media

50.11

Children Literature

40.00

History

44.44

Science

65.00

Economics

40.55

tested on nouns. The domains of the experiment and the accuracy values are mentioned in the table 2. The histogram of ﬁgure 2 shows the WSD accuracy across domains.
In this paper an attempt is made to study gloss as designed in Sanskrit Wordnet. Thus we try to see if glosses in Sanskrit Wordnet provide us with surface cues that help get the selectional preferences of diﬀerent senses of a word.We describe below the glosses of a polysemous noun “hari” in Sanskrit. Below we discuss the structure of gloss and application of the algorithm.
Strcture of a Gloss. Verb sense deﬁnitions are, in general, inﬁnitive verb phrases with adverbials (often prepositional phrases) and additional restrictions on the semantic class of agents and objects [2]. Table 3 shows how structures can be derived from verb sense deﬁnition: Similarly, we can form structures using the Dh¯atup¯a.tha meanings as the class. For example table 4 shows the structure in the gloss of the verbal root cup. In such classiﬁcation, Navya-Nya¯ya terminology can be helpful for Sanskrit Wordnet. Therefore, an attempt is made to construct verbal glosses using some structures and combining these structures by either Navya-Ny¯aya terms or by use of certain cases-endings; like instrumental for instruments involved in performing that action, locative for the situation or the condition in which that action takes place.

---

<!-- page 208 -->

Gloss in Sanskrit Wordnet 195
Table 3. Structures in verb sense deﬁnition (Alshawi, 1987)
launch) (to send (a modern weapon or instrument) into the sky or space by means of scientiﬁc explosive apparatus) ((CLASS SEND) (OBJECT ((CLASS INSTRUMENT) (OTHER-CLASSES (WEAPON)) (PROPERTIES (MODERN)))) (ADVERBIAL ((CASE INTO) (FILLER (CLASS SKY))))
Table 4. Structure in the sense deﬁnition of the verb cup gatau
((CLASS gati) ((CLASS gati) (Manner manda) (AGENT (CLASS ANIMATE)) )

The motivation behind systematizing glosses came from lexicographer’s experience of understanding Hindi Wordnet (HWN) glosses in the expansion approach. Many times, when HWN glosses were not clearly understood, Sanskrit lexicographers looked for the glosses of the same concept in other wordnets; i.e., English WorNet (EWN) and Marathi Wordnet (MWN).

WSD using Sanskrit Wordnet Glosses. Sanskrit wordnet is still a small database compared to Hindi Wordnet. It contains 5000 synsets. We take following three cases to show how this database can be used in disambiguating polysemous words in following three cases.
1. Harih. v.rks. a´s¯akha¯m an˜cati| 2. Bhaktah. har¯ım an˜cati prasannah. m¯adhavah. tasya is..tam. varam. dad¯ati| 3. Harih. ´sa´sakam. bhaks. ayati|
Here noun hari and verb an˜cati are polysemous. In the existing Sanskrit Wordnet, noun hari has ﬁve senses. These senses are shown in the table 5 and their application in the WSD is shown below.

Table 5. Possible synsets for the word hari in the present Sanskrit Wordnet

Gloss

Synset members

1. Vanyapa´suh. - ma¯rj¯ara-j¯at¯ıyah. him. srah. sim. hah. ,

mr. gendrah. ,

harih.

tath¯a ca balava¯n pa´suh.

. . . pan˜c¯asyah. . . .

2. Devat¯a-vi´ses.ah. - hindudharma¯nus¯ar¯ı ja- vis. n. uh. ,

na¯r¯ayan. ah.

. . . ke´savah. ,

gatp¯alanakart¯a

harih. . . . ma¯dhavah. . . . cakrapa¯n. ih.

3. Yaduvam. ´s¯ıyasya vasudevasya putrah. kr. .sn. ah. , devak¯ınandanah. , . . . harih. ,

yah. vis. n. oh. avat¯arah. iti manyate

ma¯dhavah. , . . . kam. s¯arih. . . .

4. Vanyapa´suh. - yah. vr. ks.¯at vr.ks. am v¯anarah. ,

kapih. ,

. . . harih. ,

pucchena utplutya gacchati ya´sca . . . tarumr. gah.

manus. y¯an. ¯am. pu¯rvajatvena khya¯tah.

5. Ubhayacharah. pr¯an. ¯ı yah. var.s¯ar. tau man. d. u¯kah. ,

bhekah. ,

plavagah. ,

jal¯a´sayasya sam¯ıpe dr.´syate

. . . dardurah. , . . . harih.

---

<!-- page 209 -->

196 M. Kulkarni et al.
Sentence 1. Word hari in the sentence 1 can be disambiguated using the Lesk like algrithm described in the table 1 in the following way:
Context Bag C will consist {hari, vr.ks.a-´s¯akh¯a, an˜c} – Consider synset 1 as the ﬁrst candidate for the sentence 1.
The bag B for synset 1 mentioned above will consist {vanya-pa´su- m¯arj¯ara-j¯at¯ıya him. sra, balavat pa´su, sim. ha, mr.gendra, hari, pan˜ca¯sya, . . . }. Overlap between C and B will be 1 for synset 1 mentioned above. – Consider synset 2. The bag B for synset 2 mentioned above will consist {devat¯a-vi´ses.a, hindu-dharm¯anusa¯r¯ı jagat-p¯alana-kart¯a vis.n. u, n¯ar¯ayan. a, ke´sava, hari m¯adhava, cakrap¯an. i . . . } Overlap between C and B will be 1 for synset 2 mentioned above. – Consider synset 3. The bag B for synset 3 mentioned above will consist {yadu-vam. ´s¯ıya, vasudeva, putra, vis.n. u, avat¯ara,man, kr.s.n. a, devak¯ınandana, hari, kam. sa¯ri, . . . } Overlap between C and B will be 1 for synset 3 mentioned above. – Consider synset 4. The bag B for synset 4 mentioned above will consist {vanya-pa´su, vr.ks.a, puccha, utplu, gam, manus.ya, pu¯rvajatva, khy¯ata v¯anara, kapi, harih. , tarumr.ga. . . } Overlap between C and B will be 2 for synset 4 mentioned above. – Consider synset 5. The bag B for synset 5 mentioned above will consist {ubhayachara, pr¯an. in, vars.a¯-r.tu, jal¯a´saya, sam¯ıpe dr.´s, man. d. u¯ka, bheka, plavaga, dardura, hari,. . . } Overlap between C and B will be 1 for synset 5 mentioned above.
Synset 4 gets the highest overlapping score and therefore it can be considered as the most appropriate sense for the word hari in the sentence 1.
Sentence 2. If we perform similar analysis on the sentence 2, we ﬁnd that Context Bag C consists {bhakta, hari, an˜c, prasanna, ma¯dhava, is.t.a, vara, da¯}. We will get overlap score 2 for synsets 2 and 3 as hari, ma¯dhava these two candidates overlap. In this case, words i.s.ta, vara in the context bag indicate that the sense devat¯a should be selected.
Sentence 3. The Context Bag C for the sentence 3 consists {hari, ´sa´saka, bhaks.}. In this case, information extracted from the relation node of Hypernymy where the sense sim. ha of the word ‘hari’ is linked with the synset of ma¯m. sa¯h¯ar¯ı.
3 Conclusion and Future Work
In this paper, we have shown the importance of glosses in WSD in the context of the noun Hari. Same application can be extended to the verb ’ancati’. In the same way, at least primarily, same application can be extended across POS categories polysemous words in Sanskrit. In this task, the use of Navya-Nya¯ya terminology and semantic structure of the verb root may play a crucial role. We reserve to explore this aspect in future. Also in future, we propose to examine how Gloss in Sanskrit Wordnet becomes useful in the task of WSD across Indian languages, in the context of Indo-Wordnet (Wordnet eﬀort connecting all the available Wordnets of Indian languages). According to us, describing the application of the Sanskrit Wordnet glosses for the speciﬁc NLP task of WSD for Sanskrit is the ﬁrst attempt of its kind. We faced several challenges in building Sanskrit Wordnet through expansion approach. We also did not get much positive support from the traditional lexica in creating glosses. However, we tried to use the traditional ´s¯astraic background in creating glosses of verbs (in particular) and other POS categories to overcome such methodological problems. For one thing, we are sure at the moment that glosses specially designed in the way shown in this paper, certainly help WSD for Sanskrit.

---

<!-- page 210 -->

Gloss in Sanskrit Wordnet 197
Acknowledgements
Authors thank all the reviewers for their invaluable comments that helped revise the draft of this paper. Authors also thank the editor for cooperation.
References
1. Agirre, E., German, R.: Word sense disambiguation using conceptual density. In: Proceedings of the 16th International Conference on Computational Linguistics, COLING (1996)
2. Alshawi, H.: Processing dictionary deﬁnitions with phrasal pattern hierarchies. Computational Lingustics 13, 195–202 (1987)
3. Bhattacharyya, P.: Indowordnet. In: Lexical Resources Engineering Conference, Malta (May 2010)
4. Kulkarni, M., Dangarikar, C., Kulkarni, I., Nanda, A.P.B.: Introducing sanskrit wordnet. In: Bhattacharyya, P., Fellbaum, C., Vossen, P. (eds.) Proceedings on the 5th Global Wordnet Conference ( GWC 2010), Narosa,Mumbai, pp. 287–294 (2010)
5. Lesk, M.: Automatic sense disambiguation using machine readable dictionaries: how to tell a pine cone from an ice cream cone. In: Proceedings of the 5th annual international conference on Systems documentation, Toronto, Ontario, Canada, pp. 24–26 (1986)
6. Mihalcea, R.: Unsupervised large-vocabulary word sense disambiguation with graph-based algorithms for sequence data labeling. In: HLT/EMNLP 2005, Human Language Technology Conference and Conference on Empirical Methods in Natural Language Processing, Proceedings of the Conference, Vancouver, British Columbia, Canada, October,6-8 (2005)
7. Narayan, D., Chakrabarty, D., Pande, P., Bhattacharyya, P.: An experience in building the indo wordnet- a wordnet for hindi. In: International Conference on Global WordNet (GWC 2002), Mysore, India (2002)
8. Resnik, P.: Selectional preference and sense disambiguation. In: Tagging Text with Lexical Semantics: Why, What, and How? In: Proceedings of ACL SIGLEX Workshop on Tagging Text with Lexical Semantics: Why, What, and How?, pp. 52–57. ACL (1997)
9. Sinha, M., Reddy, M., Bhattacharyya, P.: An approach towards construction and application of multilingual indo-wordnet. In: 3rd Global Wordnet Conference (GWC 2006), Jeju Island, Korea (2006)
10. Walker, D., Amsler, R.: Analyzing Language in Restricted Domains. In: The Use of Machine Readable Dictionaries in Sublanguage Analysis, pp. 69–83. LEA Press (1986)

---

<!-- page 211 -->

Vibhakti Divergence between Sanskrit and Hindi
Preeti Shukla, Devanand Shukl, and Amba Kulkarni
Department of Sanskrit Studies, University of Hyderabad, Hyderabad
shukla.preetidev@gmail.com, dev.shukl@gmail.com, apksh@uohyd.ernet.in
Abstract. Translation divergence at various levels between languages arises due to the diﬀerent conventions followed by diﬀerent languages for coding the information of grammatical relations. Though Sanskrit and Hindi belong to the same Indo-Aryan family and structurally as well as lexically Hindi inherits a lot from Sanskrit, yet divergences are observed at the level of function words such as vibhaktis. P¯an. ini in his As.t.a¯dhya¯y¯ı has assigned a default vibhakti to k¯arakas alongwith many scopes for exceptions. He handles these exceptions either by imposing a new k¯araka role or by assigning a special vibhakti. However, these methods are not acceptable in Hindi in toto. Based on the nature of deviation, we propose seven cases of divergences in this paper.
Keywords: Pa¯n. ini, k¯araka, vibhakti, semantics, translation divergence.
1 Introduction
Diﬀerent languages may follow diﬀerent conventions for coding the information of grammatical relations. This leads to divergence between languages at various levels in translation in general and in Machine Translation(MT) in particular. Translation divergence patterns have been discussed by Dorr [Dorr,1994], and based on those patterns considerable work is done for Indian Languages, viz., English-Sanskrit-Hindi MT [Goyal and Sinha, 2009], English-Sanskrit MT [Mishra and Mishra, 2008], English-Hindi MT [Dave et al., 2002] to name a few.
Sanskrit and Hindi belong to the same Indo-Aryan family and Hindi inherits a lot from Sanskrit in terms of structure as well as lexicon. As such, when we look at the divergences between Sanskrit and Hindi, most of the cases discussed in Dorr’s divergence turn out to be either of rare occurrence, or do not pose much problem as far as accessing the source text using machine tools is concerned. On the contrary divergences are observed at the level of function words such as vibhaktis. While both Sanskrit and Hindi are inﬂectional languages, Sanskrit is synthetic in nature while Hindi is analytic [Dwivedi, 2006]. In Sanskrit both sup and tin˙ suﬃxes are termed as vibhakti pratyayas.1 Sup suﬃx is added to a nominal stem and tin˙ suﬃx is added to a verbal root. But in Hindi only the suﬃx added to the nominal stem is called as a vibhakti pratyaya. In this paper
1 Vibhakti´sca (suptin˙ au vibhaktisanjn˜au stah. -S.K.) (P-1.4.104).
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 198–208, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 212 -->

Vibhakti Divergence between Sanskrit and Hindi 199
we discuss the divergences in the use of nominal suﬃxes (vibhakti pratyayas) between Sanskrit and Hindi.
2 Classiﬁcation of Divergences
P¯an. ini uses k¯araka - a syntactico-semantic relation as an intermediary step to express the semantic relations through vibhaktis. The assignment of k¯araka to various semantic categories is not one-to-one. Rama Nath Sharma (2002) observes-
P¯an. ini speciﬁes his ka¯raka categories based upon the principle of s¯ama¯nya ‘general’, vi´ses. a ‘particular’ and ´se.sa ‘residual’. The six categories are identiﬁed by general rules formulated based upon linguistic generalizations. Particular rules form exceptions to them. Usage which cannot be accounted for by the above two rule types is governed by rules relegated to the residual category. It is obvious that these exceptions are necessary to capture the peculiarities of usage falling outside the scope of the general rules.
Each k¯araka in his system has a default vibhakti. But as is well-known, there are exceptions and hence there is no one-to-one mapping between the k¯arak a relations to vibhaktis. Pa¯n. ini handles these deviations by employing two methods: (a) imposing a ka¯raka role and (b) assigning a special vibhakti. For example through the su¯tra ¯adha¯ro’dhikaran. am (P-1.4.45) a locus is mapped to adhikaran. a and then it takes seventh case suﬃx by default (saptamyadhikaran. e ca P-2.3.36). However the locus of the action related to the verbal roots ´s¯ın˙ , sth¯a and ¯asa preceded by the upasarga adhi is termed as karma (adhi´s¯ın˙ stha¯sa¯m. karma P1.4.46) and then by the su¯tra karman. i dvit¯ıya¯ (P-2.3.2) this karma takes the second case suﬃx. Thus the deviation of the adhikaran. a taking the second case suﬃx instead of seventh is handled by imposing a karma ka¯raka role in place of adhikaran. a. Similarly, when the linguistic generalisations cannot be captured, he treats the cases as exceptional as in rucyartha¯n¯am pr¯ıyama¯n. ah. (P-1.4.33), where he assigns a samprada¯na k¯araka to the one who desires. In Fig 1, we summarise P¯an. ini’s way of mapping semantic relations to vibhaktis through ka¯rakas.
This classiﬁcation does not hold good as-it-is for Hindi. If a parallel grammar for Hindi in the As.t.a¯dhy¯ay¯ı style were available, it would have been a simple task to arrive at the divergence cases. In the absence of such a grammar, the grammar rules corresponding to exceptional cases and cases which can not be captured by linguistic generalisations, were all checked for corresponding vibhaktis in Hindi. Leaving aside those cases where vibhakti is the same in Sanskrit and Hindi and taking up those cases where it diverges, we found that the cases of divergences may be classiﬁed into seven types, such as -
1. Optional Divergence: Vibhaktis optionally found in Sanskrit but absent in Hindi. For instance, in Sanskrit the karma2 of the verb is expressed by the default second case suﬃx and optionally the fourth case suﬃx (ba¯laka¯h.
2 Roughly equivalent to the notion of object in western linguistics.

---

<!-- page 213 -->

200 P. Shukla, D. Shukl, and A. Kulkarni
Fig. 1. Semantic–Vibhakti Mapping vidya¯laya¯ya/vidya¯layam. gacchanti) but in Hindi it takes only the default second case suﬃx (b¯alaka vidya¯laya ja¯te haim˙ = ‘Boys go to school’). 2. Exceptional Divergence: Sanskrit has certain exceptional rules which block the default suﬃxes but Hindi uses only the default suﬃxes. For example, in Sanskrit the karma of the verb exceptionally takes the sixth case suﬃx (´sakunih. ´satasya d¯ıvyati) but in Hindi it takes the default second case suﬃx (´sakuni sau rupae j¯ıtat¯a hai = ‘Shakuni wins hundred rupees’). 3. Diﬀerential Divergence: Sanskrit and Hindi use diﬀerent nominal suﬃxes, for example, in Sanskrit, the person against whom the feeling of hatred druha is directed takes the fourth case suﬃx (durjan¯ah. sajjana¯ya druhyanti) while in Hindi it takes the ﬁfth case suﬃx (durjana sajjana se droha karte haim˙ = ‘The wicked hate the good’). 4. Alternative Divergence: Sanskrit uses more than one vibhaktis but Hindi takes only few among them. For instance, in Sanskrit alternately the sixth as well as the seventh case suﬃx is used after a word in conjunction with

---

<!-- page 214 -->

Vibhakti Divergence between Sanskrit and Hindi 201
a¯yukta (¯ayuktah. haripu¯jane/haripu¯janasya) but in Hindi only the seventh case suﬃx is applicable (hari k¯ı pu¯ja¯ mem˙ l¯ına = ‘Deeply absorbed in the worship of Hari’). 5. Non-k¯araka Divergence: Divergences at the level of non-k¯araka nominal suﬃxes, such as upapada vibhaktis, sambandha vibhaktis, etc. For instance, in Sanskrit the word takes ﬁfth case suﬃx when governed by the karmapravachan¯ıya prati (pradyumnah. kr. s.n. ¯at prati asti) while in Hindi it takes the sixth case suﬃx (pradyumna kr. s. n. a ke pratinidhi hai = ‘Pradyumna is the representative of Krishna’). 6. Verbal Divergence: Divergences due to the special demand of certain verbs. For example, the karma of the verb ¯a+ruh in Sanskrit (va¯narah. vr. ks.am a¯rohati) takes the seventh case suﬃx in Hindi (bandara pe.ra para car.hata¯ hai = ‘Monkey climbs on the tree’). 7. Complex-Predicate Divergence: This divergence results when a Sanskrit verb is mapped to a complex predicate in Hindi. For instance, the karma of the verb anu+s.r in Sanskrit (ra¯mam anusarati s¯ıta¯) is expressed by the genitive case in Hindi (ra¯ma ka¯ s¯ıta¯ anusaran. a karat¯ı hai = ‘Sita follows Rama’).
These cases are elaborated in detail.
2.1 Optional Divergence
When a su¯tra assigns optionally two diﬀerent vibhaktis in Sanskrit but Hindi allows only one vibhakti, we term the resulting divergence as Optional Divergence.
Illustration divah. karma ca (s¯adhakatamam and k¯arake) (P-1.4.43). That ka¯raka which is supplemental in the accomplishment of the action of the verbal root diva (to play) is termed as karma, in addition to karan. a. e.g.,
(1) San: aks. ¯an/aks.aih. d¯ıvyati Hin: pa¯som˙ se khelata¯ hai gloss: dice with plays Eng: ‘(He) plays with dice.’
In the above example (1), aks. a is the instrument of the verbal root diva expressed through the third case suﬃx derived from the general rule s¯adhakatamam. karan. am (P-1.4.42) but due to the optional rule divah. karma ca, aks. a optionally takes the second case suﬃx. Whereas in Hindi this optional rule does not apply and thus Hindi allows only the third case suﬃx.
Table 1 lists the su¯tras which account for an additional optional vibhakti in Sanskrit either on account of imposed ka¯raka (Nos.1-3) or on account of special vibhakti assignment. In all these cases Hindi allows only the default k¯araka and hence the default vibhakti.

---

<!-- page 215 -->

202 P. Shukla, D. Shukl, and A. Kulkarni Table 1. Optional Divergence

Sr.No.

Su¯tra

Default

Optional

k¯araka Vibhakti k¯araka Vibhakti

1 1.4.43 divah. karma ca

karan. a

2 1.4.44 parikrayan. e.

karan. a

3 1.4.53 hr.kronyatarasya¯m kart¯a

4 2.3.12 gatyarthakarman. i. karma

5 2.3.22 san˜jn˜o’nyatarasya¯m. . karma

6 2.3.31 enap¯a dvit¯ıy¯a

-

3 karma

2

3 samprada¯na 4

3 karma

2

2-

4

2-

3

6-

2

7 2.3.59 vibh¯as.opasarge

karma

2-

6

8 2.3.71 kr.ty¯ana¯m. karttari. kart¯a

3-

6

2.2 Exceptional Divergence
When su¯tras give exceptional rules for cases by restricting the general rules but these rules are not applicable in Hindi, the divergence is termed as Exceptional Divergence.
Illustration adhi´s¯ın˙ stha¯sa¯m. karma (a¯dha¯rah. and k¯arake) (P-1.4.46). That ka¯raka which is the locus of the verbal roots ´s¯ın˙ (to lie down), sth¯a (to stand), ¯asa (to sit), when preceded by the upasarga adhi is termed as karma. e.g.,
(2) San: ba¯lakah. paryan˙ kam adhi´sete Hin: lad. aka¯ palam. ga para sota¯ hai gloss: boy bed on sleeps Eng: ‘Boy sleeps on the bed’.
In this example, the locus paryan˙ ka of the verbal root adhi + ´s¯ın˙ is termed as karma and thus takes the second case suﬃx. But this rule does not apply in Hindi. So paryan˙ ka which is the locus and hence adhikaran. a by the rule ¯adha¯ro’dhikaran. am (P-1.4.45) takes the seventh case suﬃx. This applies to other verbs stha¯ and ¯asa with preﬁx adhi as well.
Table 2 lists the su¯tras which account for non-default vibhaktis in Sanskrit by imposing a new ka¯raka (as in Nos.1-3) or by imposing an altogether diﬀerent vibhakti for the k¯araka. In all these cases, Hindi however takes the default ka¯raka and hence default vibhakti.
2.3 Diﬀerential Divergence
All those cases where P¯an. ini’s rule assigns a certain vibhakti either through k¯araka or by direct case assignment and Hindi uses altogether diﬀerent vibhakti are termed as the case of Diﬀerential Divergence.

---

<!-- page 216 -->

Vibhakti Divergence between Sanskrit and Hindi 203 Table 2. Exceptional Divergence

Sr.No.

Su¯tra

Default

Exceptional

k¯araka Vibhakti k¯araka Vibhakti

1 1.4.46 adhi´s¯ın˙ stha¯s¯am. karma adhikaran. a 7 karma

2

2 1.4.47 abhinivi´sa´sca

adhikaran. a 7 karma

2

3 1.4.48 upa¯nvadhy¯an˙ vasah. adhikaran. a 7 karma

2

4 2.3.58 divah. tadarthasya karma

2-

6

5 2.3.61 pres.yabruvorhavis.o karma

2-

6

6 2.3.64 kr.tvo’rthapray¯oge adhikaran. a 7 -

6

Illustration apavarg¯e tr.t¯ıy¯a (k¯al¯adhvanoh. atyantasam˙ yoge) (P-2.3.6). The third case-suﬃx is employed after the words denoting the duration of time or place (adhvan), when accomplishment (apavarga) of the desired object is meant to be expressed. e.g.,
(3) San: ahna¯ anuva¯kah. adh¯ıtah. Hin: dinabhara mem˙ anuva¯ka (veda ka¯ eka bha¯ga) par.ha liya¯ gloss: whole day in anuvaka (veda of one part) read Eng: ‘Anuvaka was perseverely and eﬀectually studied (by him) in one
day’.
In example (3), the person not only studied anuva¯ka but completely understood and memorised them. Attainment of knowledge is the fruitful result and hence the word ahn¯a which denotes the duration of time takes the third casesuﬃx. But in Hindi it takes the seventh case-suﬃx.
Table 3 lists the su¯tras which describe cases where Hindi vibhakti diﬀers from the Sanskrit vibhakti.

2.4 Alternative Divergence
In case of Alternative Divergence Sanskrit allows more than one case suﬃxes and Hindi takes only a few of them, and rarely an altogether diﬀerent case suﬃx.
Illustration du¯r¯antik¯arthaih. s.as.t.hyanyatarasy¯am (pan˜cam¯ı) (P-2.3.34). When in conjunction with du¯ra (distant,far), and antika (near) and their synonyms, the sixth case suﬃx is optionally employed and alternately the ﬁfth. e.g.,
(4) San: gr¯amasya/gr¯ama¯t vanam. du¯ram asti Hin: ga¯nva se jan˙ gala du¯ra hai gloss: village from forest far is Eng: ‘Forest is far from the village’.

---

<!-- page 217 -->

204 P. Shukla, D. Shukl, and A. Kulkarni Table 3. Diﬀerential Divergence

Sr.No.

Su¯tra

Sanskrit

Hindi

k¯araka Vibhakti Vibhakti

1 1.4.34 ´sla¯ghahnun. sth¯a.

samprada¯na 4

2 1.4.35 dha¯reruttamarn. ah.

samprada¯na 4

3 1.4.37 krudhadruhers.ya¯su¯y¯a. samprada¯na 4

4 1.4.38 krudhadruhorupasr.s.ta. karma

2

5 1.4.39 r¯adh¯ıks.yoryasya.

samprada¯na 4

6 2.3.6 apavarg¯e tr.t¯ıya¯

-

3

7 2.3.17 manyakarman. yan¯adare. karma

2,4

8 2.3.23 hetau

-

3

2,4,6 6 5,7 5,7 6 7 6 4

9 2.3.37 yasya ca bh¯avena.

-

7

6

10 2.3.43 s¯adhunipun. a¯bhy¯am. 11 2.3.67 ktasya ca varttam¯ane -

7

4

6

3

In example (4), in Sanskrit gr¯ama takes optionally the sixth case suﬃx as well as the ﬁfth when combined with du¯ra as well as antika but Hindi takes only the ﬁfth case suﬃx.
Table 4 lists the su¯tras where Sanskrit takes more than one vibhaktis but Hindi takes only a few of them.
Table 4. Alternative Divergence

Sr.No.

Su¯tra

Sanskrit Hindi

Vibhakti Vibhakti

1 2.3.32 pr.thagvin¯ana¯na¯. 2 2.3.34 du¯ra¯ntik¯arthaih. . 3 2.3.36 saptamyadhikaran. e ca 4 2.3.39 sv¯am¯ı´svar¯adhipati.

2,3,5

5,6

5,6

5

2,3,5,7

0

6,7

6

5 2.3.40 a¯yuktaku´sal¯abhy¯am. . 6 2.3.41 yata´sca nirdh¯aran. am 7 2.3.44 prasitotsuk¯abhy¯am˙ .

6,7

7

6,7

7

3,7

2,7

8 2.3.72 tuly¯arthairatulopam¯abhy¯am˙ . 3,6

6

9 2.3.73 caturth¯ı ca¯´sis.ya¯yus.ya.

4,6

2,6

2.5 Non-k¯araka Divergence
Certain words known as upapada demand speciﬁc vibhaktis called Upapada Vibhaktis for nouns with which they combine. These are all typically exceptions to the .sas..th¯ı ´se.se (P-2.3.50). In Hindi, however, in most of the cases sixth case suﬃx is used.

---

<!-- page 218 -->

Vibhakti Divergence between Sanskrit and Hindi 205
Illustration
sahayukte apradh¯ane (tr.t¯ıy¯a) (P-2.3.19). The word denoting apradha¯na in conjunction with saha and its synonyms takes the third case suﬃx. e.g.,
(5) San: ra¯men. a saha s¯ıta¯ vanam˙ gacchati Hin: ra¯ma ke s¯atha s¯ıta¯ vana ja¯t¯ı hai gloss: rama with sita forest goes Eng: ‘Sita goes to forest with Rama’.
In example (5), in Sanskrit it is seen that s¯ıta¯ and vana are directly related to the verb in the form of karta¯ and karma but ra¯ma is not directly related to the verb and hence is called apradha¯na. The association of ra¯ma with s¯ıt¯a is denoted by the word saha due to which ra¯ma takes the third case suﬃx from the above rule. But in the case of Hindi, ra¯ma in conjunction with saha takes only the sixth case suﬃx.
Table 5 lists the su¯tras where Sanskrit generally takes the second case suﬃx barring the sixth case suﬃx but Hindi does not take this exemption into account and takes the sixth case suﬃx.

Table 5. Non-k¯araka Divergence

Sr.No.

Su¯tra

Sanskrit Hindi

Vibhakti Vibhakti

1 1.4.84 tr.t¯ıy¯arthe 2 1.4.85 h¯ıne

2

6

2

6

3 1.4.87 upo’dhike ca

2

6

4 1.4.89 laks.an. etthambhu¯t¯a. 5 1.4.90 abhirabha¯ge

2

6

2

6

6 1.4.95 atiratikraman. e ca

2

5,6

7 2.3.4 antara¯’ntaren. ayukte

2

6

8 2.3.5 ka¯l¯adhvanoratyantasanyoge

2

7

9 2.3.10 pan˜camyapa¯n˙ paribhih.

5

2

10 2.3.11 pratinidhipratida¯ne ca yasm¯at 5

6

11 2.3.16 namah. svastisva¯ha¯. 12 2.3.19 sahayukte apradha¯ne

4

2,4,6

3

6

13 2.3.26 any¯ara¯ditarartedik.

5

5,6

2.6 Hindi Speciﬁc Divergences
All the divergences we covered so far were speciﬁc to the As.t.¯adhya¯y¯ı, and some of them might be attributed to the characteristics of Sanskrit. The default vibhakti of karma in Sanskrit is dvit¯ıya¯. But in Hindi, the karma takes vibhakti other than dvit¯ıya¯. These divergences may be attributed to the nature of Hindi.

---

<!-- page 219 -->

206 P. Shukla, D. Shukl, and A. Kulkarni
On the face of it divergences may be classiﬁed into two classes depending upon whether the Sanskrit verb maps to a simple Hindi verb or a complex predicate.
(a) Verbal Divergence Consider the example,
(6) San: va¯narah. vr. ks.am a¯rohati Hin: bandara per. a para car.hata¯ hai gloss: monkey tree on climbs Eng: ‘Monkey climbs on the tree’.
Here, the karma of the verbal root ¯a + ruh is v.rks. a whereas in Hindi the karma vr. k.sa takes seventh case suﬃx. The important question from Hindi grammar point of view then is - whether vr. k.sa should be termed as a karma as in Sanskrit or should it be termed as an adhikaran. a? If we term it as a karma, then the treatment will be close to Sanskrit but one needs to impose a rule accounting for the divergence in the suﬃx. If we term it as an adhikaran. a, then we deviate from the Sanskrit grammar but can take an advantage of the default vibhakti mapping.
There are many such instances, and these should be treated carefully by Sanskrit scholars who know Hindi well, taking insights from how Pa¯n. ini handled such cases.
(b) Complex Predicate Divergence If a verb in Sanskrit maps to a complex predicate3 in Hindi, then the karma of the verb takes the sixth case suﬃx. e.g.,
(7) San: ra¯mam anusarati s¯ıta¯ Hin: ra¯ma k¯a s¯ıta¯ anusaran. a karat¯ı hai gloss: rama of sita follows Eng: ‘Sita follows Rama’.
Here in example (7), ra¯ma which is the karma is expressed with the genitive case in Hindi. This change is a systematic one which may be explained through the rule kartr. karman. oh. kr. ti (P-2.3.65). In Hindi anu + sr. is translated as a complex predicate anusaran. a karan¯a where anusaran. a is the kr. danta and karan¯a is the main verb.
It is necessary to study these divergences in karma vibhakti in detail. Sanskrit has approximately 2000 verbal roots and many more with the upasargas. Mapping the corresponding verb-frames in Sanskrit to the Hindi verb-frames may give some hints towards these divergences. Though it is a voluminous task, any MT system requires this study.
3 A complex predicate consists of a noun followed by a light verb such as karana¯, hon¯a, etc. e.g. viv¯aha karana¯, sna¯na karana¯, etc.

---

<!-- page 220 -->

Vibhakti Divergence between Sanskrit and Hindi 207
3 Conclusion
The cases of divergences may be summarised then as: (A) Divergences originating from Sanskrit Grammar (as shown below)

Sr.No. Cases

Sanskrit

Hindi

1 Optional Sanskrit uses optional vibhakti in Hindi allows only the default

addition to default vibhakti. vibhakti.

2 Exceptional Sanskrit uses diﬀerent vibhakti Hindi uses the default vibhakti.

than the default (Pa¯n. ini blocks the default vibhakti by treating

it as an exceptional case).

3 Diﬀerential Pa¯n. ini imposes certain k¯arakas Hindi uses diﬀerent vibhaktis. or vibhaktis which cannot be

captured through the semantic

generalisations.

4 Alternative Sanskrit uses more than one al- Hindi uses only one of them.

ternative vibhakti.

5 Non-k¯araka Sanskrit uses more than one al- Hindi uses the sixth vibhakti.

ternative vibhakti.

(B) Divergences due to the idiosyncrasy of Hindi:

1. Special vibhakti expectancy of verbs 2. Complex Predicate

These seven cases of divergence may prove useful in resolving the ambiguities at the level of nominal suﬃxes in Machine Translation and may serve as a platform for looking at vibhakti level divergences between Sanskrit and other Modern Indian Languages.

Acknowledgements. This work is a part of the Sanskrit Consortium project entitled ‘Development of Sanskrit computational tools and Sanskrit-Hindi Machine Translation system’ sponsored by the Government of India. We gratefully acknowledge Prof. Lakshmi Bai for the discussions at various stages.

References
1. Ramshastri, A.: Sam˙ skr.ta ´siks.an. a saran.¯ı. Acharya Ramshastri Jn˜¯anap¯ıt. ha (Hindi) (1998)
2. Cardona, G.: P¯an. ini and P¯an. in¯ıyas on ´ses.a Relations. Kunjunni Raja Academy of Indological Research, Kochi (2007)
3. Dorr, B.: Classiﬁcation of Machine Translation Divergence and a Proposed Solution. Computational Linguistics 20(4) (1994)
4. Dave, S., Parikh, J., Bhattacharya, P.: Interlingua Based English-Hindi Machine Translation and Language Divergence. Journal of Machine Translation (JMT) 17 (2002)
5. Dwivedi, K.D.: Bh¯as.a¯ vijn˜a¯na evam Bh¯as.a¯ ´s¯astra. Vi´svavidy¯alaya Prak¯a´sana, Varanasi (2006)

---

<!-- page 221 -->

208 P. Shukla, D. Shukl, and A. Kulkarni
6. Goyal, P., Sinha, R., Mahesh, K.: Translation Divergence in English-Sanskrit-Hindi Language Pairs. In: Kulkarni, A., Huet, G. (eds.) SCLS 2009. LNCS (LNAI), vol. 5406, Springer, Heidelberg (2009)
7. Mishra, V., Mishra, R.B.: Study of Example Based English to Sanskrit Machine Translation. Journal of Research and Development in Comp Sc. And Engg. (37) (January-June 2008)
8. Sharma, R.R., Sharma, M.: Vaiy¯akaran. a Siddh¯anta Kaumud¯ı of S´r¯ı Bhat.t.oji D¯ıks.ita (Ka¯raka Prakaran. am). Bharatiya Vidya Prakashan, Varanasi-Delhi (Hindi) (1997)
9. Sharma, R.N.: The As.t.¯adhya¯y¯ı of P¯an. ini, 2nd edn., vol. 1-3. Munshiram Manoharlal, Delhi (2002)
10. Vasu, S´.C.: The Siddh¯anta Kaumud¯ı of Bhat.t.oji D¯ıks.ita, vol. I. Motilal Banarsidass, Delhi (2003)

---

<!-- page 222 -->

Anaphora Resolution Algorithm for Sanskrit
Pravin Pralayankar and Sobha Lalitha Devi
AU-KBC Research Centre, MIT Campus of Anna University, Chennai, India
sobha@au-kbc.org
Abstract. This paper presents an algorithm, which identiﬁes diﬀerent types of pronominal and its antecedents in Sanskrit, an Indo-European language. The computational grammar implemented here uses very familiar concepts such as clause, subject, object etc., which are identiﬁed with the help of morphological information and concepts such as precede and follow. It is well known that natural languages contain anaphoric expressions, gaps and elliptical constructions of various kinds and that understanding of natural languages involves assignment of interpretations to these elements. Therefore, it is only to be expected that natural language understanding systems must have the necessary mechanism to resolve the same. The method we adopt here for resolving the anaphors is by exploiting the morphological richness of the language. The system is giving encouraging results when tested with a small corpus.
Keywords: Anaphora resolution, Rule based Technique, Finite State Automata, Sanskrit.
1 Introduction
Sanskrit, the language of the Indo-European family has very long writing tradition available in both poetry and prose. It contains many linguistic elements in its rich grammatical and philosophical tradition but Sanskrit syntax has been least focused by the modern linguist. Speyer [15] and Hock [4] have looked on many syntactic aspects of Sanskrit language.
In recent years Sobha et al [11,12,13] has looked on anaphora resolution for Indian languages including Sanskrit in detail from computational perspective. Jha et al [5,6] has discussed about anaphora resolution techniques and the concept of anaphora in diﬀerent knowledge tradition of Sanskrit including Vya¯karan. a, Nya¯ya, and M¯ım¯am. s¯a. Keeping these in mind, this paper discusses about various types of pronominal constructions in Sanskrit and an algorithm to resolve it.
Anaphora resolution refers to the problem of determining the antecedent of an anaphora in a document. The most common type of anaphora is pronominal anaphora and it can be exhibited by personal, possessive or reﬂexive pronouns. There are many approaches to solve this problem such as rule based [1,2,3], statistical and machine learning based techniques [7,8,9,10]. This paper describes about a rule based pronominal resolution for Sanskrit and its scope is limited only to the simple prose sentences.
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 209–217, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 223 -->

210 P. Pralayankar and S.L. Devi
2 Sanskrit Anaphora
There are two types of anaphoric construction available in Sanskrit; anaphora proper and anaphora-like cases [6] . Sobha et al [13] gives a theoretical description of anaphora proper and in this paper its computational aspects are presented.
2.1 Classiﬁcation of Sanskrit Anaphora The diﬀerent types of anaphora proper are pronominal, reﬂexives, and reciprocals in a context. Below is the list of Sanskrit anaphora. The reﬂexive (sva and ¯atman) and reciprocal (parasparam and anyonyam) does not have gender feature so they do not exhibit the gender agreement with their antecedent.

Table 1. Sanskrit anaphora

Anaphors Sanskrit Anaphor

Pronominal tat

Demonstrative idam, etat, adas

Reﬂexive

sva, a¯tman

Reciprocal parasparam, anyonyam

Pronominal Anaphors. The major classiﬁcation in pronominal is the ﬁrst, second, and third person pronoun. First and second person are commonly used as deictic, though they are used in discourse. The third person pronoun is the most commonly used anaphora in a language. In Sanskrit tat is the third person pronoun which has the following separate forms in diﬀerent cases for masculine and feminine gender.1
In the following set of examples (1-4), we see the distribution of third person pronoun tat and its antecedent; a phrase or clause that is referred to by an anaphoric pronoun. Example (1-3) is grammatical because there is a person, number and gender (PNG) agreement between the antecedents and pronominal while (4) is ungrammatical because there is no PNG agreement between them. In example (1a) antecedent s¯ıta¯ is in feminine singular form so its anaphor in (1b) s¯a is in feminine singular form. In example (2) antecedent ch¯atra¯h. and the anaphor te is in masculine plural form while in example (3) antecedent k¯alida¯sah. and anaphor sah. is in masculine singular form. But in example (4) antecedent k¯artikah. is in masculine singular form but the anaphor te is in masculine plural form. This violates the PNG agreement and the sentence is ungrammatical. From the above we ﬁnd that there should be PNG agreement between pronominal and its antecedent.
1 Although neuter gender is also available in Sanskrit but we are not giving here the neuter forms because they are same as masculine except in nominative and accusative. In nominative and accusative, the forms are tat, te, t¯ani respectively for singular, dual and plural.

---

<!-- page 224 -->

Anaphora Resolution Algorithm for Sanskrit 211

Table 2. Forms of pronominal tat in diﬀerent cases

Masculine Gender

Feminine Gender

Singular Dual Plural Singular Dual Plural

Nominative sah. Accusative tam

Instumental tena

Dative

tasmai

Ablative tasma¯t

Genitive tasya

tau

te

s¯a

tau

ta¯n ta¯m

ta¯bhy¯am taih. taya¯ ta¯bhy¯am tebhyah. tasyai ta¯bhy¯am tebhyah. tasya¯ tayoh. tesa¯m tasya¯h.

te

ta¯h.

te

ta¯h.

ta¯bhya¯m ta¯bhi

ta¯bhya¯m ta¯bhy¯ah.

ta¯bhya¯m ta¯bhy¯ah.

tayoh. ta¯s¯am

Locative tasmin tayoh. tes.u tasya¯m tayoh. ta¯su

1.a. [ s¯ıtai

mama

svasa¯

s¯ıta¯.f.nom.sg i.gen.sg

sister.f.nom.sg

b. [s¯ai

pa¯t.aliputre

nivasati]MC

she.f.nom.sg p¯at.aliputra.loc.sg live.prest.rd pl ‘Sitai is my sister. Shei lives in Pataliputra’.

asti]MC is.prest 3rd sg

2.a. [atra here

ch¯atr¯ah. i

nivasanti.] MC

student.m.nom.pl live.prest.3rd.pl

b. [tei

adhyayanam

kurvanti] MC

he.m.nom.pl study.m.acc.g

do.prest.3rd.pl

‘Studentsi live here. Theyi do study.’

3.a. [k¯alid¯asah. i

asm¯akam priya-kavih.

asti.] MC

k¯alid¯asa.m.nom.sg i.gen.pl favourite-poet.m.nom.sg is.prest.3rd sg

b. sah. i

meghadu¯tasya

pran. et¯a

he.m.nom.sg meghadu:ta.gen.sg write

asti.] MC is.prest.3rd sg

‘Kalidasai is our favourite poet. Hei is the writer of Meghaduta.

4.a. *[mama i.gen.sg

bhr¯ata¯

k¯artikah. i

asti.] MC

brother.m.nom.sg k¯artika.m.nom.sg is.presr.3rd sg

b. [tei

pa¯t.aliputre

nivasanti] MC

he.m.nom.pl p¯at.aliputra.m.loc.sg live.prest.3rd pl

‘Kartiki is my brother. Theyi live in Pataliputra.’

The above example shows the distribution of pronominal at the inter-sentential level. In sentence (1a) s¯ıta¯ is in nominative form and it is the subject of the sentence and the pronoun is in the next sentence, (1b) takes s¯ıt¯a as the antecedent. In sentence (2a) and (3a) ch¯atra¯h. and ka¯lida¯sah. having nominative case, are the subject of the sentence and the pronominals te and sah. are in the next sentence.

Demonstrative Pronoun. Demonstrative pronouns idam, etat, adas are other anaphoric expression in Sanskrit and their uses are often related to the spatial distance. etat is used for very close objects, while idam is used for distantly

---

<!-- page 225 -->

212 P. Pralayankar and S.L. Devi

situated objects and if the object is beyond the eyes then adas is used. In the classical Sanskrit, the use of idam and etat has hardly any diﬀerences. All these have diﬀerent declinable forms for masculine, feminine and neuter gender. The anaphoric distribution of demonstrative pronoun in Sanskrit can be seen in examples (5-8).

5.a. [ayam

asm¯akam

this.m.nom.sg i.m.gen.pl

vidy¯alayah. i school.m.nom.sg

asti.] MC is.prest.3rd sg

b. [asyai

bhavanam

bhavyam

asti.] MC

it.m.gen.sg building

beautiful

is.prest.3rd sg

‘This is our schooli. Itsi building is beautiful.’

6.a. [mama i.m.gen.sg

gr¯amah. i

biha¯r-pra¯nte

asti.] MC

village.m.nom.sg bih¯ar-state.m.loc.sg is.prest.3rd sg

b. [ay¯ami

gan˙ ga¯ya¯h.

tat.e

this.m.nom.sg Ganga.f.gen.sg bank.m.loc.sg

asti.] MC is.prest.3rd sg

‘My villagei is in Bihar. Thisi is situated on the bank of Ganga.’

7.a. [gan˙ ga¯i

asm¯akam

pavitra-nadi

vartate.] MC

Ganga.f.nom.sg i.m.gen.pl

pious-river.f.nom.sg is.prest.3rd sg

b. [iyami

hima¯laya¯t

nih. sr.tya

ban˙ gasa¯gare

this.f.nom.sg himalya.m.abl.sg originate.ppl bay of benga.loc.sg

patati.] MC

fall.prest.3rd.sg

‘The Gangai is our pious river. Having originated from Himalaya, thisi

falls into bay of bengal.

8.a. sam. skr.ta-bh¯as.¯ai

deva-bha¯s.¯a

kathyate.] MC

sanskrit-language.f.nom.sg god-language.f.nom.sg say.pst.3rd sg

b. [es.¯ai

vi´svasya

pra¯c¯ınatama-bha¯s.a¯.] MC

this.f.nom.sg world.m.gen.sg oldest-language.f.nom.sg

‘Sanskrit languagei is called language of God. Thisi is the oldest

language of the world.

In the sentence (5b) the PNG features of demonstrative pronoun asya (5b) matches with vidya¯layah. in (5a), which is the antecedent of asya . Similarly the demonstrative pronoun ayam in (6b) has antecedent gr(ma( in (6a). Here also there is PNG agreement between the pronoun and its antecedent. In sentence (7) gan˙ g¯a is the subject of the sentence and is the antecedent of the demonstrative pronoun iyam of (7b). Sentence (8a) is in passive voice and the antecedent sanskrit-bha¯s. a¯ is the direct object position. The pronoun e.s(a¯ is in sentence (8b) and it has PNG agreement with its antecedent sanskrit- bha¯.sa¯.
From the above we arrive at the following algorithm:

1. A pronoun P is coreferential with an NP iﬀ the following conditions hold: (a) P and NP have compatible P, N, G features. (b) P does not precede NP (c) If P is possessive, then NP is the subject of the clause which contains P. If P is non-possessive, then NP is the subject of the immediate clause which does not contain P.

---

<!-- page 226 -->

Anaphora Resolution Algorithm for Sanskrit 213

Reﬂexive Pronoun. sva and a¯tman are reﬂexive pronoun in Sanskrit. In Sanskrit unlike the above pronominal, the antecedent and the reﬂexives are bound and the antecedent is always the subject of the sentence in which the reﬂexive occurs. For example, in sentence (9) ra¯mah. is the antecedent of the reﬂexive pronoun sva and it is the subject of the sentence. In sentence (10) antecedent p¯atravargaih. and reﬂexive sves. u, which is in re-duplicated form is bound to each other and they are local. Similarly in sentence (11) antecedent e.sa¯ and reﬂexive ¯atma¯nam are locally bound to each other. But here reﬂexive is preceding the antecedent due to relatively free word order and focus function.

9. r¯amah. i ram.m.nom.sg

svai-grham

gacchati.

own-house.loc.sg go.prest.3rd sg

‘Ram is going to his own house

10. tad then

ucyat¯am tell

p¯atravargaih. i sves.u-sves.ui actor.m.nom.pl own.m.loc.pl-own.loc.pl

pa¯t.hes.u a-samud. haih. bhavitvyam

iti

leson.loc.pl not-carefree become

so

‘So let the actors are told to be careful about thir own lessons.’

11. bhartr.-gatayaa¯ cintaya¯

¯atm¯anami

api

husband-go

contemplation self

even

na

es.¯ai

vibha¯vayati.

not

she

conscious.prest.eg

‘Owing to her contemplation regarding her husband, she is not conscious

of even herelf.’

2. A pronoun P is coreferential with an NP iﬀ the following conditions hold: (a) Reﬂexive and NP have compatible Number features. (b) Reﬂexive does not precede NP (c) The NP is the subject of the clause which contains Reﬂexive.

3 Architecture
3.1 Pre-processing
The position of the noun plays a major role in identifying the antecedent of a pronoun. From the above examples we could see that the antecedent is mostly the subject or the direct object and it can be in the same sentence or in the preceding sentence. Another feature is the position of the noun with respect to the clause, whether it is in the main clause or subordinate clause. Depending on this we can identify whether the noun is the antecedent of the pronominal or not. For this the clause boundaries have to be identiﬁed. We use simple linguistic rules to identify the clause boundaries. In the following paragraphs we discuss about how we identify the clause boundary and the subject and object.

---

<!-- page 227 -->

214 P. Pralayankar and S.L. Devi

Subject/object Identiﬁcation. We identify subject and direct object using the morphological markings on the nouns. In this we use that all nominative nouns are probable candidate for subject hood, all dative nouns if the verb is a cognitive verb is probable candidate for subject hood and ﬁnally possessive nouns with nominative head or dative head are also possible noun for subject hood. Nouns inﬂected for all other cases are considered as direct object.

Clause Identiﬁcation. yat is the complement marker in Sanskrit. With the help of yat we identify the main clause and the subordinate clause. In both the clause there will be a ﬁnite verb. For example,

12. [s¯ıta¯ sita.f.nom.sg

avadat]MC say.pst.3rd sg

[yatcomp that

tasy¯ah. she.f.gen.sg

svas¯a

delhi-nagare

nivasati]SC

sister.f.nom.sg delhi-city.m.loc.sg live.prest 3rd sg

‘Sita aid that her sister lives in Delhi city.’

To mark the conditional clause the, conditional marker yadi is used. The main clause in this case contains the use of tarhi, which is optional. Both the clause will have ﬁnite verb. For example,

13. yadi if

ra¯mah. he.m.nom.sg

adya toay

a¯gamis.yati]COND come.fut.3rd sg

[(tarhi) then

sah. he.m.nom.sg

´svah. tomorrow

gamis.yati]MC go.fut.3rd sg

‘If Ram comes today, then he will go tomorrow.’

We use the clause marker for identifying the presence of the clause. The boundaries are identiﬁed using the yadi as the beginning and tarhi as the end for the conditional clause. Similarly we use yat as the marker for complement clause and the ﬁnite verb before yat is considered as the end of the main clause and ﬁnite verb after yat as the end of subordinate clause. The beginning of the clause is identiﬁed using the noun nominative immediately following yat as the beginning of the subordinate clause and the noun nominative before the yat as the beginning of the main clause. We have similar rules for other types of clauses and for multiple embedding of clauses. Though this does not resolve all the sentences we got a reasonably good result.

Morphological Analyzer. The anaphora resolution system for Sanskrit is based on the hypothesis that any noun in Sanskrit is the combination of root and case suﬃxes where case suﬃxes carry information about PNG features. A morphological generator has been developed using Finite State Automata (FSA) and paradigm based approach. The FSA is built using all possible suﬃxes and the root dictionary is classiﬁed based on paradigms [16] . The suﬃxes, used in FSA are listed with its grammatical features, is utilized, while giving the output of the morphological analyzer to give the syntactic features of the morphemes. The parse for the words from the FSA are validated with morphosyntactic rules.

---

<!-- page 228 -->

Anaphora Resolution Algorithm for Sanskrit 215 3.2 Algorithm for Anaphor Resolution Hence the algorithm we use for identifying the antecedent NPs is as follows:
Consider all the NPs Preceding the pronoun in sentence (S). If the clause marker (CM) is present in S
Then, Identify the Main (M) clause and the Subordinate (Sub) clause of S
Identify the Subject and object of the S. Consider all the Nouns in the sentence that precede the pronoun.
Identify the Pronoun (P) / Reflexive (R) and the Nouns (N) preceding the P/R
If P is non-possessive then Check the PNG of P and N If PNG agrees, then check for subject or object marker If N is the subject/object of the clause where P does not occur Then N is identified as the antecedent
If P is possessive then Check the PNG of P and N If PNG agrees, then check for subject or object marker If N is the subject of the clause where P occur Then N is the antecedent
If R then Check the PNG of P and N If PNG agrees, then check for subject or object marker If N is the subject of the clause where P occur Then N is identified as the antecedent

---

<!-- page 229 -->

216 P. Pralayankar and S.L. Devi
4 Anaphora Resolution System
The input to the anaphora resolution component is the parsed output which identiﬁes the subject, object and the clause boundaries (The parser is not a sophisticated one, we are identifying it using linguistic rules and a small Dictionary). The diﬀerent types of clauses present in the input sentence are identiﬁed (We are using a rule based approach for identifying the clause boundaries). The NPs which precede P are identiﬁed. The NPs which matches according to the pronominal algorithm are identiﬁed and checked for PNG agreement between the pronoun and reﬂexives and the NPs. The NP which matches in PNG and the algorithm is identiﬁed as the antecedent of the Pronoun.
5 Evaluation
We have tested the system using 200 sentences taken from the book titled Sanskr. it Sahacara. It contains simple sentences. The number of pronominal present in 200 sentences was 40. Among the 40 pronominal only 26 were correctly identiﬁed. The details about the correct and wrong identiﬁcation are given in the table 3 below.
Table 3. Evaluation result of Sanskrit pronominal
Correct Wrong No. of Sentences 200 No. of Pronominals 40 26 14
6 Conclusion
This is an algorithm we have developed to identify pronominal in Sanskrit. The approach outlined here does not exploit the hierarchy, but exploits the nominal morphology. The work is still in progress and we are reporting an on going work. Hence the system is evaluated with a very small data. Pronominal resolution is necessary for any understanding systems such as question answering systems, information extraction and machine translation.
References
1. Byron, D., James, A.: Applying Genetic Algorithms to Pronoun Resolution. In: Proceedings of the Sixteenth National Conference on Artiﬁcial Intelligence AAAI (1999)
2. Carbonell, J., Brown, R.: Anaphora Resolution: A Multistrategy Approach. In: Proceedings of the 12th International Conference on Computational Linguistics, pp. 96–101 (1988)
3. Hobbs, J.: Resolving pronoun references. Lingua 44, 311–338 (1978)

---

<!-- page 230 -->

Anaphora Resolution Algorithm for Sanskrit 217
4. Hock, H.H.: Studies in Sanskrit Syntax. Motilal Banarasidas, Delhi (1991) 5. Jha, G.N., Sobha, L., Mishra, D., Singh, S.K., Pralayankar, P.: Anaphors in San-
skrit. In: Proceedings of the Second Workshop on Anaphora Resoplution (WAR-II). Nealt Proceedings Series, vol. 2, pp. 11–25 (2008) 6. Jha, G.N., Sobha, L., Mishra, D.: Discourse Anaphor and Resolution Techniques in Sanskrit. In: Proceedings of the 7th Discourse Anaphora and Anaphora Resolution Colloquium, Goa, pp. 135–150 (2009) 7. Kennedy, C., Boguraev, B.: Anaphora for Everyone: Pronominal Anaphora Resolution without a Parser. In: Proceedings of the 16th International Conference on Computational Linguistics (COLING 1996), Denmark, pp. 113–118 (1996) 8. Lappin, S., Mccord, M.: Anaphora Resolution in Slot grammar. Computational Linguistics 16(4), 197–210 (1990) 9. Lappin, S., Leass, H.: An Algorithm for Pronominal Anaphora Resolution. Computational Linguistics 20(4), 535–561 (1994) 10. Mitkov, R.: Factors in Anaphora Resolution: They are not the only Things That Matter. A Case Study Based on Two Diﬀerent Approaches. In: Proceedings of the ACL 1997/EACL 1997 Workshop on Operational Factors in Practical, Robust Anaphora Resolution, Spain, pp. 14–21 (1997) 11. Sobha, L., Patnaik, B.N.: An Algorithm for Pronoun and Reﬂexive Resolution in Malayalam. In: International Conference on Computational Linguistics, Speech and Document processing, pp. 63–66 (1998) 12. Sobha, L., Patnaik, B.N.: A Quantitative and a Non-Quantitative Approach to Resolve Reﬂexives and Pronouns in Malayalam. IJDL 27(1), 33–40 (1999) 13. Sobha, L.: An Anaphora Resolution System for Malayalam and Hindi (An unpublished doctoral thesis) Mahatma Gandhi University, Kottayam (1999) 14. Sobha, L., Pralayankar, P.: Anaphors in Sanskrit. In: International Conference on Referential Entity Resolution. AU-KBC, Chennai (2007) 15. Speyer, J.S.: Sanskrit Synta. E.J. Brill, Leyden (1886) 16. Viswanathan, S., Ramesh Kumar, S., Kumara Shanmugam, B., Arulmozi, S.: A Tamil Morphological analyser. In: Proceedings of International Conference on Natural Language Processing, pp. 31–39 (2003)

---

<!-- page 231 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit
Brendan S. Gillon
McGill University Montreal, Quebec brendan.gillon@mcgill.ca
Abstract. Ellipsis is a common phenomenon of Classical Sanskrit prose. No inventory of the forms of ellipsis in Classical Sanskrit has been made. This paper presents an inventory, based both on a systematic investigation of one text and on examples based on sundry reading.
Keywords: anaphora, antecedent, ellipsis, gapping.
1 Introduction
Most, if not all, Sanskritists would agree that ellipsis is a common feature of Classical Sanskrit. Yet, what ellipsis is in Classical Sanskrit and which grammatical factors determine under which conditions it is permitted are questions which, to my knowledge, have never been raised in modern studies of Classical Sanskrit. The aim of this paper is to direct the attention of the community of Sanskrit scholars to these questions.
Below, I report on the forms of ellipsis which I have found in two corpora and discuss their bearing on possible answers to the questions raised above. The two corpora are the prose sentences found in V. S. Apte’s The Student’s Guide to Sanskrit Composition and the sentences up to the thirty-eighth verse of the Sv¯arth¯anuma¯na chapter of Dharmak¯ırti’s Prama¯n. av¯arttika (PVS). I also supplement the discussion with cases found in sundry sentences outside of the corpora.
The term ellipsis is often used broadly and without much care, with the result that it fails to encompass anything which would be taken by linguists as a uniﬁed phenomenon. To arrive at a linguistically useful characterization, let us consider the English expression Yajn˜adatta lentils. This expression is not a sentence. It seems somehow defective and it fails to express a proposition. Yet, if it is preceded by the English sentence Devadatta cooked rice, as in (1.1) below, the expression Yajn˜adatta lentils no longer appears defective and it conveys a proposition, namely the one expressed by the sentence Yajn˜adatta cooked lentils. It is surely no coincidence that what the defective expression Yajn˜adatta lentils conveys when it is immediately preceded by the sentence Devadatta cooked rice is precisely what is expressed by the sentence which results from inserting the verb cooked, found in the preceding sentence, into the defective expression Yajn˜adatta
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 218–230, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 232 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 219
lentils. Moreover, as illustrated by the pair of sentences in (1), what the defective expression Yajn˜adatta lentils conveys varies with proposition expressed by the sentence preceding it.
(1.1) Devadatta cooked rice; Yajn˜adatta lentils. (1.2) Devadatta grew rice; Yajn˜adatta lentils.
Generalizing from this example, I say that an expression contains ellipsis just in case the expression, by itself, does not form an acceptable constituent, but which, when supplemented by suitable expressions from its preceding or succeeding text, or cotext1, with little or no modiﬁcation to it, yields an expression which forms a constituent and the resulting expression expresses what the unsupplemented expression conveys, relative, of course, to the given cotext. I call the point of ellipsis the point in an otherwise defective expression where the insertion of an expression taken from the cotext turns the defective expression into one which is not defective and which conveys what the defective expression conveys relative to the cotext. I call the expressions which are supplied the antecedent.2
The notation I use below is the familiar notation of labelled bracketing. To enhance readability, I omit all pairs of labelled brackets not essential to the discussion. To explain uses of the notation speciﬁc to this paper, let me begin with an application of the notation to the ﬁrst example in (1).
(2) [S Devadatta [V cooked 1] rice ]; [S Yajn˜adatta [V E 1] lentils ]
‘S’ is the label for sentence or clause and ‘V’ is the label for verb. The antecedent of the point of ellipsis has a numerical index preﬁxed to its right hand bracket and the point of ellipsis is marked by a pair of square brackets enclosing ‘E’ and having the same labels as those of its antecedent. Of course, the notation of labelled brackets was devised for languages such as English in which the linear order of expressions play a syntactic role. As is well known, linear order plays a reduced role in Classical Sanskrit prose. The reader, then, should understand the notation applied to expressions of Classical Sanskrit as indicating solely constituency. Thus, in terms of this use of the notation, the placement of ‘E’ with the constituent immediately containing the point of ellipsis is arbitrary. However, from the cases examined, it appears that the order of the words within the constituent immediately containing the antecedent of the ellipsis and the order of the words in the constituent immediately containing the point of ellipsis are parallel. For that reason, I have placed the ‘E’ in the same linear position relative to its sister constituents as its antecedent has relative to its sister constituents. Finally, I have supplemented the usual categorial labels for adjective, noun,
1 It is useful to distinguish between the physical situation, or setting, in which an expression is uttered and the text, or cotext, which either precedes or succeeds it. I shall use these technically deﬁned terms, rather than the more common but very imprecise term context.
2 As is well known, ellipsis and anaphora are very similar phenomena.

---

<!-- page 233 -->

220 B.S. Gillon
adjective phrase and noun phrase with numerical indices corresponding to the standard enumeration in Pa¯n. inian grammar of the cases. To highlight structural properties of the Sanskrit expressions, I have also taken the liberty of eliminating sandhi.
There is no exceptionless linguistic regularity. Due to limitations of space and time, I have not mentioned well known exceptions to generally recognized linguistic regularities, nor have I considered alternative analyses to the various examples adduced below.
The predominant forms of ellipsis are those of the ellipsis of the head verb of a verb phrase and of a head noun of a noun phrase. In addition, I have found some cases where the point of ellipsis is the point of a complement to a head verb or a head adjective. I begin by reviewing ﬁrst the forms of ellipsis within a verb phrase, second the forms within a noun phrase and third the forms within an adjective phrase. I end by bringing to the reader’s attention a form of ellipsis which I call denial ellipsis.
2 Ellipsis within the Verb Phrase
The most commonly encountered pattern of ellipsis within a verb phrase is the one where the verb itself is ellipted3, similar to the English case given above. (The English case is known in the literature as gapping.) Verb head ellipsis may occur when the ellipted verb occurs in one coordinated clause and the antecedent in another. Thus, in the example here, the verb vidh¯ıyeta (can be aﬃrmed) occurs in the ﬁrst clause and it serves as the antecedent for the verbless second clause.
(3) PVS 5.10 [S vidhau [S viruddhah. v¯a [V vidh¯ıyeta 1] ] [S a-viruddhah. va¯ [V E 1] ] ] When there is an aﬃrmation, either what is incompatible can be aﬃrmed or what is not incompatible can be aﬃrmed.
Such ellipsis may also occur when the clauses are asyndetically coordinated, that is, coordinated without a conjunction.
(4) MBh 1.241.7 (cited in Scharf [8] p. 110) [S loke ca [S ekasmin vr.ks.ah. iti [V prayun˜jate 1] ] [S dvayoh. vr.ks.au iti [V E 1] ] [S bahus.u vr.ks.a¯h. iti [V E 1] ] ] In ordinary speech, the word ‘tree’ applies to a single thing, the word ‘tree’ [in the dual] to two things and the word ‘trees’ to many things.
Verb head ellipsis is found when the point of ellipsis occurs in a main clause and the antecedent in a subordinate one. In the next example, the point of ellipsis is in the verbless main clause atra tath¯a viraktah. api (now in the same way an unimpassioned person too). Its antecedent is the verb of the subordinate clause yath¯a raktah. brav¯ıti (as an impassioned person speaks), which precedes the point of ellipsis.
3 I follow here the useful coinage of Quirk et al [6], who introduced the verb to ellipt, corresponding to the noun ellipsis.

---

<!-- page 234 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 221
(5) PVS 9.7 [S atra [S yatha¯ raktah. [V brav¯ıti 1] ] tatha¯ viraktah. api [V E 1] ] Now an unimpassioned person speaks in the same way as an impassioned one does.
Here is another such case example, this one taken from S´abarabh¯as. ya.
(6) S´Bh (cited in Scharf [8] p. 286) [S na ca [S yatha¯ dan. d. i-´sabdah. na dan. d. e [V prayuktah. 1] ] evam go´sabdah. na a¯kr.tau [V E 1] ] And it is not the case that the word ‘cow’ does not apply to the form in the same way as the word ‘stick possessor’ does not apply to a stick.
Verb head ellipsis may also occur when the antecedent is in a preceding sentence. For example, sa¯dhyate (is established ) occurs in the ﬁrst sentence and serves as the antecedent for the point of ellipsis of the verbless main clause of the second sentence.
(7) PVS 5.24 [S tatra kevalam vis.ay¯ı [V s¯adhyate 1] ] [S asya¯m api [S yada¯ vya¯paka-dharma-anupalabdhya¯ vya¯pya-abha¯vam [V a¯ha 1] ] tada¯ abha¯vah. api [V E 1] iti ] In this case, only intentional activity [pertaining to an absence] is established. In this case too, an absence also is established when one states the absence of a pervadee on the basis of a non-apprehension of [its] pervader property.
Like ellipsis in other languages which have been well studied, features required at the point of ellipsis of a word and the features of the antecedent expression may diﬀer. Thus, in the next sentence, uktau, a past participle being used as a main verb, is in the neuter dual, whereas the point of ellipsis requires the form of masculine singular.
(8) PVS 2.13 [S etena anvaya-vyatirekau yatha¯svam pram¯an. ena ni´scitau [V uktau 1] ] [S paks.a-dharmah. ca [V E 1] ] Concomitance and contra-concomitance, ascertained by [their] respective means of epistemic cognition, are thereby mentioned. The paks.aproperty is also [thereby stated].
Unusual for Sanskritists whose ﬁrst language is a Western European language is the fact that the point of ellipsis may precede the antecedent for the point of ellipsis. Although I have not come across examples in the Sv¯arth¯anuma¯na chapter of the Prama¯n. av¯arttika so far, I have found examples in Karn. akagomin’s .t¯ıka¯ on Dharmak¯ırti’s text. In the example adduced below, the ﬁrst two clauses are verbless and the antecedent for their points of ellipsis is the verb kathyate, which occurs in the last clause.

---

<!-- page 235 -->

222 B.S. Gillon
(9) PVST. 108.8 [S atra [S [S [NP3 prathamaya¯ ka¯rikaya¯ ] [NP1s dharma-kalpana¯-b¯ıjam ] [V E 1] ] [S [NP3 dvit¯ıyaya¯ ] [NP1s dharma-kalpa¯ ] [V E 1] ] [S [NP3 tr.t¯ıyaya¯ ] [NP1s pratij na¯-artha-ekade´sat¯a-pariharah. ] ca [V kathyate 1] ] ] iti samuda¯ya-arthah. ] The overall meaning here is this: the seed for the conceptualization of properties is mentioned by the ﬁrst verse; the conceptualization of properties by the second; and the rejection of [an inference’s grounds] forming part of the state of aﬀairs of [its] conclusion by the third.
This conﬁguration, in which the point of ellipsis precedes its antecedent, does not appear to be uncommon, as I have come across two examples outside my two corpora.
(10) S´Bh (cited in Scharf [8] p. 283) [S tena atra [S a¯kr.tih. gun. a-bha¯vena [V E 1] ] [S vyaktih. pradha¯nabha¯vena [V vivakys.ate 1] ] iti Therefore here a form will be accepted as subordinate, the individual as principal.
(11) Candrak¯ırti on A¯ ryadeva’s Catuh. ´sataka 14.10 [S tatra [S yatha¯ ekasya ru¯pasya ghat.atvena avastha¯nam [V E 1] ] tatha¯ anyasya api pat.a-¯adi-sambandhinah. ru¯pasya kasma¯t ghat.atvena avastha¯nam na [V is.yate 1] ] Now, why is a material form which is connected with such things as cloth not accepted as abiding as a pot in the same way as another material form [is accepted] as abiding as a pot?
The question arises whether or not ellipsis within a verb phrase is conﬁned to the head verb. I have found three cases where, besides the verb, other material in the verb phrase is ellipted. In the ﬁrst case, the verb and the negative adverb na are required for the point of ellipsis.
(12) PVS 18.5 [S tatha¯ [AC prasiddhe tat-bha¯ve hetu-bha¯ve va¯ ] [S anityatva-abha¯ve kr.takatvam [VP [ADV na 1] [V bhavati 2] ] [S dahana-abha¯ve ca dhu¯mah. [VP [ADV E 1] [V E 2] ] ] ] ] In this way, when [either the relation of something] being something or [the relation of something] being the cause [of something] is established, neither does artiﬁciality exist in the absence of non-eternality nor does smoke exist in the absence of ﬁre.
One might wonder whether or not this case of ellipsis might be better described as the ellipsis of the entire verb phrase. There is some evidence to support this analysis. Thus, in the next example, the verb phrase of the ﬁrst sentence comprises a direct object and the verb, ka¯ran. am anuma¯payati (implies a cause). Both are required for the point of ellipsis in the following sentence.

---

<!-- page 236 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 223
(13) PVS 10.6 [S tasm¯at na¯ntar¯ıyakam eva ka¯ryam [NP2 ka¯ran. am 2] [V anuma¯payati 3] tat-pratibandha¯t ] [S na anyat [VP [NP2 E 2] [V E 3] ] vipaks.e a-dar´sane api ] Therefore, only an immediate eﬀect implies a cause because of [its] relation to it [sc., the cause]. No other does, even if there is no observation [of it] in the vipaks.a.
However, it does happen that the head verb and only some, and not all, of its complements are ellipted. Thus, the ﬁrst subordinate clause below contains a verb cintayati (was wondering) and two complements, second case noun phrase complement kim (what ) and a prepositional phrase complement ma¯m antaren. a (lit. about me; about him). Yet, the succeeding two clauses omit only the verb and the prepositonal phrase and repeat the second case noun phrase.
(14) K 178.23–179.2 (as cited in SG 3.1.13) [S asya¯m vel¯aya¯m [S [NP2 kim nu ] khalu [PP ma¯m antaren. a 1] [V cintayati 2] ] Vai´sam˙ pa¯yanah. ] [S [NP2 kim ] va¯ [PP E 1] [V E 2] vara¯k¯ı Patralekha¯ ] [S [NP2 kim ] va¯ [PP E 1] [V E 2] ra¯ja-putra-lokah. ] iti cintayan eva sah. nidra¯m yayau ] At that moment, he went to sleep just while wondering what Vai´sam˙ pa¯yana was wondering about him, what poor Patralekha¯ was wondering about him and what the prince’s retinue was wondering about him.
3 Ellipsis in Noun Phrase
I now turn to ellipsis within the noun phrase. I begin with ellipsis in non-subject noun phrases, since subject noun phrase present complicating factors whose consideration it is best to put oﬀ for the moment. As with verb phrases, so with noun phrases, the head can be ellipted. The next sentence, discussed above, contains both the ellipsis of a head verb and the ellipsis of a head noun. Here, the third case noun phrase prathamaya¯ k¯arikaya¯ (by the ﬁrst verse) in the ﬁrst subordinate clause is reduced to the adjective phrases dvit¯ıyaya¯ (by the second ) and tr. t¯ıyaya¯ (by the third ) in the second and third clauses respectively.
(15) PVST. 108.8 (same as (9) above) [S atra [S [S [NP3 [AP3 prathamaya¯ ] [N3 ka¯rikaya¯ 2] ] [NP1s dharmakalpana¯-b¯ıjam ] [V E 1] ] [S [NP3 dvit¯ıyaya¯ [N E 2] ] [NP1s dharma-kalpa¯ ] [V E 1] ] [S [NP3 tr.t¯ıyaya¯ [N3 E 2] ] [NP1s pratij na¯-artha-ekade´sat¯apariharah. ] ca [V kathyate 1] ] ] iti samuda¯ya-arthah. ] The overall meaning here is this: The seed for the conceptualization of properties is mentioned by the ﬁrst verse; the conceptualization of properties by the second; and the rejection of [an inference’s grounds] forming part of the state of aﬀairs of [its] conclusion by the third.
What is noticeable about the next case is that the antecedent is the single noun of an absolute phrase and the point of ellipsis is the position the noun would occur in in the absolute phrase of the following clause.

---

<!-- page 237 -->

224 B.S. Gillon
(16) PVS 5.12 [S [NP7 [NP6 a-viruddhasya ] [N7 vidhau 1] ] sahabha¯va-virodha-abha¯va¯t a-pratis.edhah. ] [S [NP7 [NP6 viruddhasya [PRT api ] ] [N7 E 1] ] anupalabdhi-abha¯vena virodha-a-pratipattih. ] When there is an aﬃrmation of what is not incompatible [with anything else], then there is no denial [of anything else], because there is no incompatibility of [its] co-occurrence [with anything else]. [And] even when there is an aﬃrmation of what is incompatible, without non-apprehension, there is no awareness of the incompatibility.
Ellipsis also occurs in a predicate noun phrase. In the second sentence of the example below, predicated of its subject noun phrase ¯akr. ti-pratyayah. (understanding of a form) is vyakti-pratyayasya (understanding of the particular ), from which nimittam (basis), the head of the predicate noun phrase in the ﬁrst sentence, has been ellipted.
(17) S´Bh (as cited in Scharf [8] p. 285) tasm¯at [S [NP1s ´sabdah. ] [NP1 [NP6 a¯kr.ti-pratyayasya ] [N1 nimittam 1] ] ] [S [NP1s a¯kr.ti-pratyayah. ] [NP1 [NP6 vyakti-pratyayasya ] [N1 E 1] ] ] iti. Therefore a word is a basis for the understanding of form, the understanding of a form for the understanding of the particular.
3.1 Ellipsis in Subject Noun Phrase
I now turn to ellipsis in the subject noun phrase. As is well known, an independent clause in Classical Sanskrit does not require a subject noun phrase. Some cases are clearly not cases of ellipsis, for no antecedent is required for understanding the subjectless clause. Thus, for example, the following clause has no subject noun phrase. The agent of the verb a¯ha is Digna¯ga, but Digna¯ga is mentioned no where in the work.
(18) PVS 2.22 [S tatha¯ ca ¯aha [S sarvah. eva ayam anuma¯na-anumeya-vyavaha¯rah. buddhia¯ru¯d. hena dharma-dharmi-bhedena iti ] ] And in this way, one [i.e., Digna¯ga] has said that the entire diﬀerence between grounds for inference and what is to be inferred is due to differentiation between property and property-possessor, which falls within the purview of the intellect.
However, there are cases which satisfy all the usual conditions for ellipsis: while there is no noun in the nominative case, there is a subordinate constituent which make sense only relative to a noun in the nominative case; and, in the preceding cotext, there is a noun in the nominative case whose sense is the sense

---

<!-- page 238 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 225
which is relevant the subordinate constituent. Though the following example contains a case of verb head ellipsis, what is relevant here are the two cases of head noun ellipsis. The head noun of the subject noun phrase of the ﬁrst sentence bhedah. (diﬀerence) and the head noun bh¯av¯an¯am (of things) of the subordinate noun phrase bh¯av¯an¯am abhinn¯an¯am (of similar things) are both omitted from the following sentence, whose verb is also to be supplied from the ﬁrst sentence, as we saw above.
(20) PVST. 108.17 [S na [NP3 [N3 ja¯ti-¯adina¯ 1] ta¯vat ] [NP1s [NP6 [N6 bha¯va¯na¯m 2] [AP6 abhinna¯na¯m ] ] [N1 bhedah. 3] ] [VP [V kriyate 4] ] . . . ] [S na api [NP3 [N3 E 1] ] [NP1s [NP6 [N6 E 2] [AP6 bhinna¯na¯m ] ] [N1 E 3] ] [VP [V E 4] ] . . . ] No universal makes similar things diﬀerent, . . ., neither does it make dissimilar things diﬀerent, . . ..
The sentences in the next two examples are verbless sentences. In each example, the second sentence contains the point of ellipsis associated with which is a subordinate noun phrase whose proper interpretation requires the head noun of the subject of the preceding sentence.
(21) PVS 8.5 [S iti tatra api [NP1s at¯ıta-eka-k¯ala¯na¯m [N1 gatih. 1] ] ] [S na [NP1s [NP6 an-a¯gata¯na¯m ] [N E 1] ] vyabhica¯ra¯t ] So, in this case, there is knowledge of things contemporaneous and antecedent [to the observation of the ground]. There is no knowledge of things future, because of deviation [from them].
(22) PVS 23.18 [S katham tarhi ida¯n¯ım [NP1s bhinna¯t sahaka¯rin. ah. [N1 ka¯rya-utpattih. 1] ] [S yatha¯ [NP1s caks.ur-ru¯pa-a¯deh. vijn˜a¯nasya [N1 E 1] ] ] ] How then now does an eﬀect arise from distinct ancillary causes, as when there is the arising of awareness from [a variety of ancillary causes such as] eye and form?
Remarkably, the antecedent for noun ellipsis may be part of a compound. In the next case, the antecedent is the head prati.sedhah. (ruling out) of the compound eka-siddha-pratis. edhah. (ruling out what is established for one).
(23) PVS 11.3 [S dvayoh. iti eka-siddha-(pratis.edhah. 1) ] [S prasiddha-vacanena sam. digdhayoh. ´ses.avat-as¯adha¯ran.ayoh. sapaks.a-vipaks.ayoh. api [N1 E 1] ] The expression ‘for both’ rules out anything which is established for [just] one [of the two interlocutors]. The expression ‘established’ rules out doubtful properties which are deﬁcient and undistributed with respect to the sapaks.a and vipaks.a.

---

<!-- page 239 -->

226 B.S. Gillon
Such cases are not rare. Next is a case where the required antecedent for the second sentence is pratipattih. (knowing), the head of the compound which is the head of the subject noun phrase, again, of a verbless sentence.
(24) PVS 9.8 [S [NP1s [NP5 vacana-m¯atra¯t ] a-(pratipattih. 1) ] ] [S na api [NP1s [N1 E 1] [NP5 vi´ses.¯at ] ] abhipra¯yasya durbodhatva¯t vyavah¯ara-sam. karen. a sarves.¯am vyabhica¯ra¯t ] So, there is no knowing [whether or not someone is impassioned] from his merely speaking. Nor is [there any knowing whether or not someone is impassioned] from a special kind [of speaking], because, [a speaker’s] intentions’ being diﬃcult to know, [his various forms of] behavior are diverse and so all [forms of his speaking] are deviant [with respect to whether or not he has passion].
The next example contains head noun ellipsis both in the subject noun phrase and in the predicate noun phrase of the second sentence.
(25)S´Bh (as cited in Scharf [8] p. 286) [S na tu [S [NP1s [N1 go-´sabda-avayavah. 1] [AP1 ka´scit ] ] [NP1 [NP6 ¯akr.teh. ] [N1 pratya¯yakah. 2] ] ] [S [NP1s [N E 1] anyah. ] [NP1 [NP6 vyakteh. ] [N1 E 2] ] ] ] But it is not the case that some part of the word ‘cow’ makes one aware of the form, another of the particular.
To see how subtle the question of whether or not the absence of a subject noun phrase is a matter of ellipsis or not, let me explain, using an example from English, an important distinction which can be easily overlooked. There is an important contrast in English between the pronoun it and the pronoun one, as seen from considering the following minimally contrasting pair of sentences.
(26.1) Devadatta bought a mango and Yajn˜adatta too bought it. (26.2) Devadatta bought a mango and Yajn˜adatta too bought one.
For the ﬁrst sentence to be true, Devadatta and Yajn˜adatta must have bought the very same mango. For the second sentence to be true, it is required only that each bought a mango. The point can be made in another way: should the pronoun in each sentence in (3) be replaced by its antecedent, the replacement preserves truth conditions in the second case but not the ﬁrst.
(27.1) Devadatta bought a mango and Yajn˜adatta too bought a mango. (27.2) Devadatta bought a mango and Yajn˜adatta too bought a mango.
The diﬀerence between it and one is that the semantic value of it, when it has an antecedent, must be a unique value of its antecedent, whereas the value of one is any of several values, all of which are in the extension of the antecedent.
How does this bear on ellipsis? According to the characterization of ellipsis given at the start, ﬁlling a point of ellipsis with its antecedent (modulo gender

---

<!-- page 240 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 227
and number) yields an expression which expresses what the expression containing the ellipsis conveys.
Consider now the next example.
(28) PVS 2.16 [S [NP7 prade´sa-vi´ses.e kva-cit 1] na [NP1s [N1 ghat.ah. 2] ] upalabdhilaks.an. a-pra¯ptasya anupalabdheh. ] [S [S yadi [NP7 E 1] sya¯t [NP1s [N1 E 2] ] ] [NP1s [N1 E 2] ] upalabhyasattvah. eva sy¯at ] There is no pot in a certain particular place, since [it], satisfying the conditions for apprehensibility, is not apprehended [there]. If one were to exist [there], [then] it would be precisely that thing whose presence is to be apprehended.
There are three points of ellipsis in the second sentence, two of them ellipted subject noun phrases and one of them an ellipted verb complement noun phrase. The value of the ﬁrst ellipted subject noun phrase can not be the value of its antecedent, for the preceding sentence denies the existence of any pot. This means that the value assigned to it is any value which is in the extension of gha.tah. (pot ). This is reﬂected in the translation of the ellipted subject noun phrase by the English pronoun one. In contrast, the value of the second ellipted subject noun phrase must be the very value assigned to the ﬁrst ellipted subject noun phrase. This is reﬂected in the translation of that ellipted subject noun phrase by the English pronoun it. Finally, the value of the ellipted verb complement noun phrase must be the value of its antecedent noun phrase. This is reﬂected in the translation of that ellipted noun phrase by the English pronoun there.
4 Ellipsis in Adjective Phrase
Ellipsis in adjective phrases appears to be not so common. The only case found in the two corpora is a case where the adjective head, itself a compound, serves as the antecedent for the point of ellipsis in the second sentence.
(30) PVS 3.1 [S bhedah. dharma-dharmitaya¯ [A1 buddhi-a¯ka¯ra-kr.tah. 1] ] [S na arthah. api [A1 E 1] vikalpa-bheda¯na¯m svatantra¯n. ¯am an-arthaa¯´srayatva¯t ] Diﬀerentiation [of them] as property and property-possessor is brought about through an image of the intellect. It is not that a thing too is so brought about, since conceptual diﬀerentiation, being independent [of things], does not have a basis.
The only other case I am aware of occurs in the Maha¯bh¯a.sya, where the point of ellipsis is the complement to an adjective.

---

<!-- page 241 -->

228 B.S. Gillon
(31) MBh 1.220.22 (cited in Bronkhorst [2] p. 57) [S [S yatha¯ tarhi ratha-an˙ ga¯ni vihr.ta¯ni pratyekam [PP vrajikriya¯m prati 1] asamartha¯ni bhavanti ] [S tat-samuda¯yah. ca rathah. [PP E 1] samarthah. ] evam . . . ] Just, then, as the parts of a chariot when taken apart are individually incapable of movement yet the whole of them, the chariot, is capable, so ...
5 Denial Ellipsis
Let me conclude by drawing attention to what might be still another form of ellipsis, though this is not so clear, as I think the examples below will show. What I call denial ellipsis is what occurs when an author wishes to deny an antecedently made claim. It has the form of the negative adverb na followed by a ﬁfth case noun phrase which gives the grounds for the denial. Its antecedents are either clauses or noun phrases.
In the ﬁrst case below, the ﬁrst sentence is a verbless clause expressing a negative existential. The negative existential is within the scope of a seventh case noun phrase tat-¯atmatve (having the other for its nature), best taken as a verbless absolutive. The object of the denial in the second sentence is the preceding verbless clause, under the scope of the verbless absolutive.
(32) PVS 2.21 [S [NP7 tat-a¯tmatve ] [NP1s s¯adhya-s¯adhana-bheda-abha¯vah. ] iti cet ] [S na E dharma-bheda-parikalpana¯t ] It might be argued that there is no diﬀerence between the establishable and the establisher when [the one] has the other for its nature. [This is] not [so], since diﬀerentiation among properties is conceptualized.
In the next case, the antecedent for the point of ellipsis is a ﬁfth case noun phrase prayojana-abh¯av¯at (because of having no point), which, at the point of ellipsis, must be understood to have propositional content.
(33) PVS 1.12 [S [NP5 prayojana-abha¯va¯t ] [NP1s an-upaca¯rah. ] iti cet ] [S na E sarva-dharmi-dharma-pratis.edha-artha-tva¯t ] It might be argued that there is no synecdoche [here] since [it] would have no point. [This is] not [so], since [it] has the purpose of prohibiting [from being a ground] a property property-possessors of which are everything [but the paks.a].
6 Conclusion
Above, I have examined a diverse set of examples of ellipsis in Classical Sanskrit. The preponderance of cases are those in which the antecedent of the point of

---

<!-- page 242 -->

Linguistic Investigations into Ellipsis in Classical Sanskrit 229
ellipsis is a head verb or a head noun. There is only one case where the antecedent is a head adjective. The few remaining cases are those in which a complement of a verb or an immediately subordinate constituent of a noun phrase. The forms of ellipsis diﬀer in important respects from the forms of ellipsis for English known as gapping, verb phrase ellipsis and copular complement ellipsis. Also noteworthy are cases of ellipsis where the antecedent is the head of a compound and cases of ellipsis where the antecedent comes after the point of ellipsis in spite of the fact that the antecedent and the point of ellipsis are in coordinated clauses. Both of these patterns are unknown in English.
The foregoing raises three questions. First, are there other forms of ellipsis in Classical Sanskrit? Second, under what conditions may one expression serve as an antecedent to a point of ellipsis? Third, how is the value of a constituent containing a point of ellipsis determined? To answer these questions satisfactorily, further extensive and careful empirical investigation of prose texts must be undertaken. This requires that texts of Classical Sanskrit be suitably annotated so that facts pertaining to ellipsis can be characterized. The annotation must be ﬁne-grained enough so that the phenomena does not slip through undetected, but not so ﬁne-grained that it prejudices the possiblity of ﬁnding data which might draw into question working hypotheses regarding the nature of ellipsis. The preceding presents a ﬁrst stab at such an annotation.
In closing, let me bring to the reader’s attention an observation well known to linguists, especially descriptive linguists (Quirk et al. [6] ch. 12.), which will be useful to bear in mind while pursuing answers to the last two questions. There is a close parallel between ellipsis, which, as we saw, requires an antecedent, and anaphora, which comprises a proform with an antecedent. Indeed, it is no coincidence that linguists use the term antecedent in connection with both phenomena. This is well illustrated by English nominal head ellipsis, where the pronoun one and a point of ellipsis are in complementary distribution.
Table 1. Abbreviations
A = A.s.ta¯dhya¯y¯ı reference: adhy¯aya.p¯ada.su¯tra
K = K¯adambar¯ı, Peterson (ed) [5]. reference: page.line
MBh = Maha¯bha¯.sya, Kielhorn (ed) [4]. reference: volume.page.line
PVS = Prama¯n. ava¯rttika, sv¯artha¯numa¯na chapter, Gnoli (ed) [3]. reference: page.line
PVST. = Prama¯n. ava¯rttikasv¯artha¯numa¯na.t¯ık¯a, S¯an˙ kr.ty¯ayana (ed) [7]. reference: page.line (of t.¯ık¯a)
SG = Student Guide to Sanskrit Composition, Apte [1]. reference: chapter.exerciseset.example
S´Bh = S´abarabha¯.sya, Scharf [8].

---

<!-- page 243 -->

230 B.S. Gillon
(34.1) The performance by Alex of Bach is better than the *E/one by Bill of Chopin.
(34.2) Alex’s performance of Bach is better than Bill’s E/*one of Chopin.
Whether the head noun of a noun phrase in which a determiner or a possessive noun phrase immediately precedes the head noun can be ellipted or replaced by the pronoun one depends on the choice of determiner or of a possessive noun phrase. This close parallel between ellipsis and anaphora suggests that investigation into either phenomena should pay attention to the results of investigation into the other.
References
1. Apte, V.S.: The student’s guide to Sanskrit composition. A treatise on Sanskrit syntax for use of schools and colleges. Lokasamgraha Press, Poona (1960)
2. Bronkhorst, J.: Three problems pertaining to the Mah¯abh¯as.ya. Bhandarkar Oriental Research Institute, Pune (1987)
3. Gnoli, R. (ed.): The Pram¯an. ava¯rttikam of Dharmak¯ırti, the ﬁrst chapter with the autocommentary, text and critical notes. Istituto Italiano per il Medio ed Estremo Oriente, Rome (1960)
4. Kielhorn, F.: Mah¯abh¯as.ya. 4th edition revised by R. N. Dandekar, 4th edn. Bhandarkar Oriental Research Institute, Pune (1985)
5. Peterson, P. (ed.): K¯adambar¯ı. Government Central Book Depot, Bombay (1885) 6. Quirk, R., Greenbaum, S., Leech, G., Svartik, J.: A Comprehensive Grammar of the
English Language. Longman, London (1985) 7. Sa¯n˙ kr.tya¯yana, R. (ed): A¯ ca¯rya-Dhamrak¯ırteh. Prama¯n. ava¯rttikam (sv¯artha¯num¯ana-
paricchedah. svopajn˜avr.tty¯a, Karn. akagominviracitay¯a tat.t.¯ıkay¯a ca sahitam. Kitab Mahal, Allahabad (1943) 8. Scharf, P.: The denotation of generic terms in ancient Indian philosophy: grammar, Ny¯aya, and M¯ım¯am. s¯a. American Philosophical Society, Philadelphia (1996)

---

<!-- page 244 -->

Asiddhatva Principle in Computational Model of As.t.¯adhy¯ay¯ı
Sridhar Subbanna1 and Shrinivasa Varakhedi2
1 Rashtriya Sanskrit Vidyapeetha, Tirupati, India sridharsy@gmail.com
2 Samskrita Academy, Osmania University, Hyderabad, India shrivara@gmail.com
Abstract. P¯an. ini’s As.t.¯adhya¯y¯ı can be thought of as an automaton to generate Sanskrit words and sentences. As.t.¯adhy¯ay¯ı consists of su¯tras that are organized in a systematic manner. The words are derived from the roots and aﬃxes by the application of these su¯tras that follow a well deﬁned procedure. Therefore, As.t.¯adhy¯ay¯ı is best suited for computational modeling. A computational model with conﬂict resolution techniques was discussed by us (Sridhar et al, 2009)[12]. In continuation with that, this paper presents, an improvised computational model of As.t.¯adhy¯ay¯ı. This model is further developed based on the principle of asiddhatva. A new mathematical technique called ‘ﬁlter’ is introduced to comprehensively envisage all usages of asiddhatva in As.t.¯adhya¯y¯ı.
1 Introduction
We (Sridhar et al, 2009)[12] have discussed computational structure and conﬂict resolution techniques of As.t.¯adhya¯y¯ı. In the current paper, the computational model has been restructured and developed further incorporating the principle of asiddhatva. In the earlier model, asiddha for s. atva and tuk were not handled. This model moves closer to the traditional view of As.t.¯adhya¯y¯ı.1
In As.t.a¯dhya¯y¯ı the su¯tras are declared as asiddha in the following instances: 1. pu¯rvatra¯siddham (8.2.1)
Su¯tras from 8.2.1 to 8.4.68 (tripa¯d¯ı) are asiddha to su¯tras from 1.1.1 to 8.1.74 (sapa¯dasapt¯adhya¯y¯ı). Also, in tripa¯di the successive su¯tras are asiddha to their previous su¯tras. 2. asiddhavadatr¯abha¯t (6.4.22) The su¯tras from 6.4.22 to 6.4.175 are deemed as asiddha to each other. 3. .satvatukorasiddhah. (6.1.86) The su¯tras 6.1.87 to 6.1.111 are asiddha to .satva su¯tras (8.3.39 to 8.3.119) and tuk su¯tras (6.1.70 to 6.1.75)
1 There were objections from the traditional grammarians on the assumption of linear application of tripa¯d¯ı su¯tras in the earlier model. The present model doesn’t have any such assumption. The environment is visible through ﬁlters to sap¯adasapta¯dhy¯ay¯ı even after the application of tripa¯d¯ı su¯tras.
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 231–238, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 245 -->

232 S. Subbanna and S. Varakhedi
The concept of asiddhatva is used in As.t.a¯dhya¯y¯ı:
– to prevent the application of su¯tra on the substitute – to enable the application of su¯tra on the substituent2 and – to mandate the order of application of su¯tras3
When su¯tra A is declared as asiddha to su¯tra B, then the transformed state obtained by application of su¯tra A is invisible to B. This concept of asiddhatva ﬁnds its application in vidhi su¯tras.4
Vidhi su¯tras describe context sensitive transformations. It deﬁnes the operation to take eﬀect in a particular context. Each vidhi su¯tra will inspect the environment to ﬁnd the context for its application. The environment contains all the transformations that happened due to application of su¯tras. Even though there is only one environment, for su¯tras, the object of inspection need not be same as the object of application. It will be same when there is no previous application of another su¯tra in the environment that is asiddha to this su¯tra. Otherwise, the object of inspection and the object of application will be diﬀerent.5 The su¯tra inspects the state just before the application of the ﬁrst asiddha su¯tra. But the application will be on the transformed state due to application of the most recent su¯tra. This can be explained in following example:
1. ´sas hi
↓ 6.4.35
2. ´s¯a hi
↓ 6.4.101
3. ´s¯a dhi
Suppose the environment is ´sas hi then the condition for su¯tras ´s¯a hau (6.4.35) and hujhalbhyo herdhih. (6.4.101) are satisﬁed. As only one su¯tra is applicable at any given point of time, one of them will be selected by the conﬂict resolver. Assume that 6.4.35 is applied. Then in the new transformed environment - ´s¯a hi - the condition for 6.4.101 is not satisﬁed. However, the su¯tra 6.4.35 is asiddha to 6.4.101. Therefore, the su¯tra 6.4.101 inspects the state 1 - ´sas hi and ﬁnds the condition satisﬁed. But, when this su¯tra is applied, the object of application will be state 2 - the latest environment resulted after the application of 6.4.35 ´s¯a hi.
The object of inspection for any given su¯tra can be obtained using a technique called Filter. Filter is a mathematical function that gives an inspection environment for a su¯tra. The pre-image for the function is the current environment. The object of inspection is the state that exists prior to the ﬁrst application of any su¯tra that is asiddha to the su¯tra in question.
2 Asiddhavacanam a¯de´salaks.an. apratis.edh¯artham utsargalaks.anabha¯v¯artham ca - vartika 6.1.86.1.
3 See [12]. 4 Vidhi su¯tra is one among the various types of su¯tra discussed in the paper[12]. 5 This is similar to the story of matsya yantra bhedana during the svayamvara of
Draupad¯ı in Mah¯abha¯rata. Here the participant is supposed to look into the reﬂection in water of a rotating ﬁsh and target the real ﬁsh.

---

<!-- page 246 -->

Asiddhatva Principle in Computational Model of As.t.a¯dhy¯ay¯ı 233
2 Model of As.t.¯adhy¯ay¯ı
The principle of asiddhatva discussed above is an important device in the operation of As.t.a¯dhya¯y¯ı. A complete and consistent process to operationalize As.t.¯adhya¯y¯ı can be visualized as an engine comprising of devices like asiddhatva, paribha¯s. a¯ etc. This engine generates words from roots and aﬃxes by following a completely mechanical process.
The core of the engine is built on conventions deﬁned in paribha¯.sa¯ su¯tras. These conventions are framed to interpret metadata. The metadata describe mode of operation, context and the object of operation. The vidhi su¯tras consist of data marked with these metadata. Interpreting the metadata, the engine carries out the operation on the object with the data supplied.
The mechanics of the engine can be summarized as follows: The vidhi su¯tras keep inspecting the object(environment) supplied. The su¯tra that ﬁnds the condition satisﬁed, sends a request to the conﬂict resolver. More than one su¯tra may send a request in any particular context. Conﬂict resolver adopts the resolution techniques and unambiguously selects one among them for application. The selected su¯tra will be applied to transform the environment.
As described earlier the object of inspection needs to take into account the principle of asiddhatva. To achieve this ﬁlters at various levels are introduced that are mathematically formulated. The ﬁlter f (A, B, α, x) returns the object of inspection α′ for su¯tra x in the environment α, where A and B are set of su¯tras such that ∀ su¯tra a ∈ A, every su¯tra b ∈ B is asiddha. Set C is an ordered set of su¯tras that are applied in the environment α arranged in the order of their application. The ﬁlter has the following algorithm to return the object of inspection:
If x ∈ A and (C ∩ B) = ∅ then return the state before application of su¯tra g ∈ α, where g is the
ﬁrst element ∈ (C ∩ B)6 else return α
Now, the following sets are deﬁned for usage in speciﬁc ﬁlter deﬁnitions:
1. SA = {1.1.1, 1.1.2, ...... , 8.1.140} - sap¯adasapta¯dhya¯y¯ı su¯tras 2. TP = {8.2.1, 8.2.1, ...... , 8.4.68} - tripa¯d¯ı su¯tras 3. TU = {6.1.70, 6.1.71, ...... , 6.1.75} - tuk su¯tras 4. AV = {6.4.23, 6.4.24, ...... , 6.4.175} - asiddhavat su¯tras 5. SH = {8.3.39, 8.3.40, ...... , 8.3.48} ∪ {8.3.55,8.3.56, ...... , 8.3.119} - s.atva
su¯tras 6. EA = {6.1.87, 6.1.88, ...... , 6.1.111} - eka¯de´sa su¯tras and 7. PP = g(x) = { x+1, x+2, ...... , 8.4.68} : x ∈ TP , which is a dynamic set.
Using these set deﬁnitions, speciﬁc ﬁlter functions can be mapped to the asiddha declarations.
6 C ∩ B is also an ordered set arranged by the order of C.

---

<!-- page 247 -->

234 S. Subbanna and S. Varakhedi
Fig. 1. Computational Structure of A´s.t¯adhya¯y¯ı with Asiddhatva Principle
Trip¯ad¯ı Filter T F (α, x) = f (SA, T P, α, x) pu¯rvatr¯asiddham (8.2.1) Asiddhavat Filter AF (α, x) = f (AV, AV, α, x) asiddhavadatra¯bha¯t (6.4.22) Ek¯ade´sa Filter EF (α, x)= f (SH ∪ T U, EA, α, x) s. atvatukorasiddhah. (6.1.86) Pu¯rvamprati Filter P F (α, x) = f (T P, P P, α, x) pu¯rvatra¯siddham (8.2.1) is a
dynamic ﬁlter. These ﬁlters as part of the A´s.t¯adhya¯y¯ı engine are depicted in ﬁgure 1. In this ﬁgure, the environment (ENV) contains all the states due to linear application of all the relavant su¯tras. Block SA represents the sap¯adasapta¯dhya¯y¯ı su¯tras, deﬁned as set SA above. All the su¯tras in this block will be inspecting ENV through the ﬁlter TF, as the tripa¯di su¯tras are asiddha for the entire sap¯adasapta¯dhya¯y¯ı. Block AV stands for the asiddhavat section of sapa¯dasapt¯adhya¯y¯ı, deﬁned as set AV earlier. The su¯tras in this block have the ﬁlter AF along with ﬁlter TF. Block TU denotes the tuk section of su¯tras of sap¯adasapta¯dhya¯y¯ı, deﬁned as set TU previously. In addition to the ﬁlter TF this block has an additional ﬁlter EF.
Block TP represents tripa¯d¯ı, deﬁned as set TP above. In tripa¯d¯ı for every su¯tra the successive su¯tras are asiddha. Each su¯tra needs a diﬀerent form of ﬁlter. Hence, this ﬁlter has been deﬁned previously as a dynamic ﬁlter varying as a function of the given su¯tra. This dynamism has been represented as a group of multiple ﬁlters PF. Block SH denotes the s. atva section of tripa¯d¯ı, denoted by set SH earlier. This block has an additional ﬁlter EF along with the PF ﬁlter. The ﬁlter EF is common for Blocks TU and SH as per su¯tra ´satvatukorasiddhah. (6.1.86).7
The Block CR represents the Conﬂict Resolution device which receives requests from all the su¯tras that are applicable in the context and determines a su¯tra for application by applying the resolution techniques[12]. 7 It is to be noted that set EA is asiddha to set SH⊂ SA, which is the converse to the
general rule that TP is asiddha to SA.

---

<!-- page 248 -->

Asiddhatva Principle in Computational Model of As.t.¯adhy¯ay¯ı 235
3 Examples
The following examples illustrate the current model of As.t.a¯dhya¯y¯ı and the role of asiddhatva in various scenarios:
Example 1. vanena (vana case 3, number 1)
1. vana .ta¯
↓ 7.1.12
2. vana ina
↓ 6.1.87
3. vanena
This is a simple example where asiddhatva has no role. Initially the word vana in case 3, number 1 gets the .ta¯ pratyaya from the su¯tra svaujas... (4.1.2) The su¯tra .t¯an˙ asin˙ asamina¯tsy¯ah. (7.1.12) ﬁnds the condition and sends a request to conﬂict resolver. The resolver ﬁnds no other competing su¯tra and hence allows this su¯tra (7.1.12) for application on the environment. It transforms the object of application by changing .ta¯ to ina and pushes to the environment stack. Then the su¯tra a¯dgun. ah. 6.1.87 goes through similar process and gets applied. The stage vanena does not satisfy the condition for any su¯tra and remains as the ﬁnal form.
Example 2. ´sa¯dhi
1. ´sas hi
↓ 6.4.35
2. ´s¯a hi
↓ 6.4.101
3. ´s¯a dhi
In this example when the environment is in state 1, two su¯tras ´sa¯ hau 6.4.35 and hujhalbhyo herdhih. 6.4.101 ﬁnd the condition and request the resolver. There is no conﬂict between these two but only one su¯tra can be applied at a time, hence resolver chooses one among them and applies it. Let us say it picks 6.4.35. After the application of this su¯tra, the state will be moved to state 2 as shown. The su¯tras in Block AV will still see state 1, since they are seeing through ﬁlter AF. Even at state 2, both the above mentioned su¯tras ﬁnd the condition for application as they are seeing through the ﬁlter AF. However, the su¯tra 6.4.35 is not permitted for second application.8. Therefore the su¯tra 6.4.101 will request and is applied on the environment. The object of application will be state 2, even though the object of inspection is state 1. This application transforms the environment to state 3. This state does not satisfy the condition for any su¯tra and remains as the ﬁnal form.
8 laks.ye laks. an. am. sak.rdeva pravartate [5]

---

<!-- page 249 -->

236 S. Subbanna and S. Varakhedi
Example 3. jahi
1. jan hi
↓ 6.4.36
2. ja hi When the environment in state 1, hanter jah¯ 6.4.36 is the only su¯tra that
ﬁnds the condition and is applied on the environment to transform to state 2. Here the condition is satisﬁed for the su¯tra ato heh¯ 6.4.105. Because this su¯tra is in Block AV, it views the environment through ﬁlter AF. Hence the object of inspection for this su¯tra is state 1 but not state 2. Therefore this su¯tra is prevented from application. State 2 remains as the ﬁnal form.
Example 4. dv¯a atra
1. dvau atra
↓ 6.1.78
2. dv¯av atra
↓ 8.3.19
3. dv¯a atra
The environment is as in state 1, the su¯tra ecoyava¯ya¯vah. 6.1.78 ﬁnds the condition and is applied. Then environment is transformed to state 2. The su¯tra lopah. ´sakalyasya 8.3.19 will be applied through similar process. Now the transformed environment is state 3. The question is whether the su¯tra akah. savarn. e d¯ırghah. 6.1.101 will be able to ﬁnd the condition in this state. The answer is no. The su¯tra 6.1.101 being in block SA it inspects at the environment through the ﬁlter TF. It gets state 2 as the object of inspection, where it does not ﬁnd condition. Therefore this su¯tra cannot be applied and the ﬁnal form is state 3.
Example 5. kosya
1. ko asya
↓ 6.1.109
2. kosya
In state 1 the rule en˙ ah. pad¯ant¯adati 6.1.109 is applied. Even though in this state, the su¯tra in. ah. s. ah. (8.3.39) can ﬁnd the condition satisﬁed, but this rule belongs to set SH and inspect ENV through ﬁlter EF. So, the su¯tra 8.3.39 gets state 1 as object of inspection, where it does not ﬁnd the condition satisﬁed. Therefore this su¯tra will not be applied. Hence, state 2 is the ﬁnal form.
Example 6. pretya
1. pra i ya
↓ 6.1.87
2. pre ya
↓ 6.1.71
3. pretya

---

<!-- page 250 -->

Asiddhatva Principle in Computational Model of As.t.a¯dhya¯y¯ı 237
In state 1 the rule aadgunah. 6.1.87 is applied. This transforms the environment to state 2. The rule hrasvasya piti k.rti tuk (6.1.71) belongs to TU inspects ENV through the ﬁlter EF, and gets the object of inspection as state 1. Here, the su¯tra 6.1.71 ﬁnds the condition and applied on the object of application, that is, state 2. Thus, transforming to state 3. It can be seen that in state 2 the su¯tra do not ﬁnd the condition satisﬁed, but this state is not the object of inspection. The ﬁnal form is state 3.
Example 7. manorathah.
1. manasrathah.
↓ 8.2.66
2. manarrathah.
↓ 6.1.114
3. manaurathah.
↓ 6.1.87
4. manorathah. In state 1 the su¯tra sasajus. o ruh¯ (8.2.66) is applied transforming to state 2.
This is a rutva vidhi and is considered as an exception to asiddha declaration in the Pa¯h. inian tradition. Hence ha´si ca (6.1.114) should ﬁnd the object of inspection as state 2 not state 1. This is handled in the TF deﬁnition. In this context, the su¯tras 6.1.114 and rori 8.3.14 ﬁnd the condition. su¯tra 6.1.114 is applied instead of 8.3.14 as per resolution technique of siddha su¯tra precedence. With this application the context is transformed to state 3. Then su¯tra aadgunah. (6.1.87) is applied to get the ﬁnal form. This has been dealt by Cardona[11]
4 Conclusion
In this paper, the concept of asiddhatva has been mapped to the mathematically deﬁned new concept called ﬁlter. This deﬁnition comprehensively envisages all applications of asiddhatva without deviating from the traditional interpretation. Further empirical study to validate the current model will throw more light on apt mathematical representation of asiddhatva.
Cardona[11] has discussed many illustrations that show exceptions to asiddhatva principle. He has shown that without these exceptions there will be su¯tras that become purposeless as they would have no scope for application. The feasibility of incorporating these exceptions into the current computational model and ﬁlter technique needs a detailed study and further research.
References
1. Giri, S.P., Satyanarayanashastri.: Pan. in¯ıyah. As.t.¯adhya¯y¯ı. Krishnadas Academy, Varanasi (1984)
2. Bhargava Sastri, B.J.: The Vy¯akaran. amah¯abha¯s.ya of Patan˜jali. Chaukhamba Sanskrit Pratishtan, Delhi (1872)

---

<!-- page 251 -->

238 S. Subbanna and S. Varakhedi
3. Kielhorn, F.: Paribh¯as.endu´sekhara of N¯agojibhat.t.a. Parimal Publications, Delhi 4. Mishra, S.: K¯a´sik¯a. Chaukamba Samskrita Samsthan, Varanasi (1979) 5. Abhyankar, K.V.: Paribhashasamgraha. Bhandarkar Research Instt, Puna (1967) 6. Kak, S.: The Paninian approach to natural language processing. International Jour-
nal of Approximate Reasoning 1, 117–130 (1987) 7. Kiparsky, P.: On the Architecture of Panini’s Grammar 8. Bhate, S., Kak, S.: Panini’s Grammar and Computer Science 9. Vasu, S.C.: The As.t.¯adhya¯y¯ı of P¯an. ini. Motilal Banarasidas Publishers, New Delhi
(2003) 10. Vasu, S.C.: Siddh¯anta Kaumudi, Motilal Banarasidas Publishers, New Delhi (2002) 11. Cardona, G.: pu¯rvatr¯asiddham and ¯asraya¯tsiddham, MS 12. Sridhar, S., Srinivasa, V.: Computational Structure of As.t.¯adhya¯y¯ı and Conﬂict
Resolution Techniques. In: Kulkarni, A., Huet, G. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406. Springer, Heidelberg (2009)

---

<!-- page 252 -->

Modelling As.t.¯adhy¯ay¯ı: An Approach Based on the Methodology of
Ancillary Disciplines (Veda¯n˙ ga)
Anand Mishra
Department of Classical Indology Ruprecht Karls University, Heidelberg, Germany
anand.mishra@urz.uni-heidelberg.de
Abstract. This article proposes a general model based on the common methodological approach of the ancillary disciplines (Veda¯n˙ ga) associated with the Vedas taking examples from S´iks.¯a, Chandas, Vy¯akaran. a and Pr¯ati´sa¯khya texts. It develops and elaborates this model further to represent the contents and processes of As.t.a¯dhya¯y¯ı. Certain key features are added to my earlier modelling of P¯an. inian system of Sanskrit grammar. This includes broader coverage of the P¯an. inian meta-language, mechanism for automatic application of rules and positioning the grammatical system within the procedural complexes of ancillary disciplines.
Keywords: Sanskrit Grammar, Modelling, As.t.¯adhya¯y¯ı, Ancillary Disciplines, Ved¯an. ga, Computer Simulation, Natural Language Processing.
1 The Methodological Approach of the Ancillary Disciplines
The ancillary disciplines (Ved¯an˙ ga) associated with the Vedas exhibit a certain degree of commonality in their general methodological approach. These disciplines were developed with the principal aim of retaining the given vedic phenomena by envisaging a system for its structured and standardized transmission. The main object of their enquiry are vedic utterances and sacriﬁcial activities which can be empirically observed and analysed.
These disciplines were regarded as empirical sciences (apara¯-vidya¯) in contradistinction to the knowledge of the Absolute (para¯-vidya¯). For example, in Mun. d. akopanis.ad it is stated that “Those who know brahman say that there are two sciences which should be known—the spiritual (para¯) and the empirical (apara¯). The empirical sciences are (the mastering of) R. gveda, Yajurveda, S¯amaveda, Atharvaveda (and the ancillary disciplines) S´ik.sa¯ (phonetics), Kalpa (ritual sciences), Vy¯akaran. a (grammar), Nirukta (etymology) and Jyoti.sa (astrology). The spiritual knowledge, however, is the one through which that
G.N. Jha (Ed.): Sanskrit Computational Linguistics, LNCS 6465, pp. 239–258, 2010. c Springer-Verlag Berlin Heidelberg 2010

---

<!-- page 253 -->

240 A. Mishra
Absolute is realized.”1 According to S´an˙ kara¯c¯arya the word ‘Veda’ here (as elsewhere in this context) means the collection of vedic utterances.2 The upani´sadic approach is to know that, which is beyond and behind the given and their eﬀort is not to return back to the given but to cross it. Similarly, the emphasis of the Yoga as well as the buddhist tradition is to get rid of the given. It is heya, that which is to be avoided, for which the cause (hetu) must be realized, a solution (ha¯na) is to be found and the corresponding prescription (ha¯nop¯aya) must be instructed.3
The general procedure employed by the ancillary disciplines can be perceived as consisting of observing a given phenomenon, recording of the observed facts and comprehending the given through these observed facts. The main eﬀort of the authors of the texts belonging to these disciplines is to develop a systematic framework for the description of a given phenomenon. Such a descriptive framework provides
– constituent units associated with a given phenomenon, – their characterizing features or attributes and – such statements which interconnect these units and attributes with a view
to correlate the description with the original.
In the following, we take up some of the texts of the ancillary disciplines in order to represent them in this framework.
1.1 Pr¯ati´s¯akhya
The given phenomena in this case are the utterances of sam. hit¯a-p¯a.tha. The constituent padas are units that convey some meaning4 and these are collected in the pada-p¯a.thas associated with a particular sam. hit¯a-pa¯.tha. The main aim of Pra¯ti´s¯akhya texts is to synthesize vedic utterances contained in sam. hit¯a-pa¯.tha out of constituent units, namely, the padas. In this way the constituent padas are correlated with the original sam. hit¯a-p¯a.tha.
It may be objected that Pra¯ti´s¯akhya texts consider sam. hit¯a-p¯a.tha to be a modiﬁcation of the pada-p¯a.tha as, for example, the statement sam. hit¯a padaprakr. tih. in R. gveda-Pra¯ti´sa¯khya (2.1). Commenting on this, Uvat.a ([22]) says that sam. hit¯a, whose constituents are padas, is here a modiﬁcation of the constituting padas. For example, the modiﬁcations .satva or n. atva occur in sam. hit¯a only. Because they are the constituents, therefore, the padas are established original forms.5 Ya¯ska in his Nirukta ([18]) also states that sam. hit¯a is the one
1 dve vidye veditavye iti ha sma yadbrahmavido vadanti par¯a caiv¯apara¯ ca. tatra¯par¯ar.gvedo yajurvedah. s¯amavedo’tharvavedah. ´siks.¯a kalpo vy¯akaran. am. nirukto chando jyotis.amiti. atha para¯ yay¯a tadaks.aramadhigamyate (Mu. 1.4-5).
2 veda-´sabdena tu sarvatra ´sabdar¯a´sirvivaks.itah. (Mu. Bha¯. 1.5). 3 For an analysis of this caturvyu¯ha approach see [29]. 4 arthah. padam (V¯a. Pr¯a. 3.2). 5 pad¯ani prakr.tibhu¯t¯ani yasya¯h. sam. hita¯y¯ah. s¯a padaprakr.tih. sam. hit¯atra vika¯rah. . tatha¯
his.atvan. atv¯adayo vik¯ara¯h. sam. hit¯aya¯ eva bhavanti. prakr.tibhu¯tatv¯acca pada¯na¯m. siddhatvam. (Uv. 2.1).

---

<!-- page 254 -->

Modelling As.t.¯adhy¯ay¯ı 241
having padas as its constituent and all the branches of the Veda consider it to be so.6 Commenting upon this, Durga¯ca¯rya takes up the question in a detailed manner and puts forward two possible cases:
1. That, which is the cause of padas, that (sam. hit¯a) is padaprakr. ti. Why? Padas are formed out of sam. hit¯a. Therefore, some consider sam. hit¯a to be the original form (prakr. ti) and padas to be their modiﬁcations (vika¯ra).
2. Others, however, understand the statement padaprak.rtih. sam. hit¯a to be sam. hit¯a, whose cause are the padas. Why? Because sam. hit¯a is gained out of the combinations of padas only. Therefore, padas are the original form and sam. hit¯a is their modiﬁcation.7
He further raises the question, which option is better: to consider padas to be the original form and the sam. hit¯a to be their modiﬁcation or vice versa and decides for the latter giving several justiﬁcations based on the earlier usage of sam. hit¯a-p¯a.tha.8
The original phenomena in this case are the given set of vedic utterances, the sam. hit¯a-p¯a.tha. The set of constituent units consists of the padas as well as the basic speech-sounds of vedic utterances (varn. a) and syllables (aks. ara) etc. The rules of Pra¯ti´s¯akhya now characterize and combine these constituent units with the aim of correlating them to the original utterances. In this way, they describe the given set and provide a mechanism to retain the original by means of constituents and rules prescribed in a systematic framework. As an example, let us take the following statement:
vi´sva sahabhuvapu.savasus. u (V¯a. Pr¯a. 3.101). The last vowel /a/ of vi´sva becomes long (d¯ırgha) in case saha, bhuva, pus.a or vasu follow. For instance: gandharvastv¯a vi´sva¯vasuh. (S´u. Yaj. 2.3).
This rule operates on constituents like /a/, vi´sva, pu.sa etc. with the help of attributes like d¯ırgha, svara etc. and statements like ‘add the attribute d¯ırgha to the last svara of vi´sva if the unit vasu follows’ are meant to connect the word vi´sva with the original utterances of the Veda. Without this rule one would have combined vi´sva with vasu but would not have changed the concerned vowel long. This would have led the formation of *vi´svavasuh. which is not to be found in the original utterances.
6 padaprakr.tih. sam. hit¯a. padaprakr.t¯ıni sarvacaran. ¯ana¯m. p¯ars.ada¯ni. (Ni. 1.17). 7 pad¯ana¯m. ya¯ prakr.tih. seyam. padaprakr.tih. . kim. ka¯ran. am? sam. hit¯ato hi pada¯ni
prakriyante. tasm¯atsam. hitaiva prakr.tirvik¯arah. pad¯an¯ıtyevameke manyante. apare punah. padaprakr. tih. sam. hiteti pada¯ni prak.rtiryasy¯ah. seyam. padaprakr. tiriti. kim. k¯aran. am? pada¯nyeva hi sam. hanyama¯na¯ni sam. hita¯ bhavati. tasm¯at pada¯nyeva hi prak.rtirvik¯arah. sam. hiteti. (Durga. 1.17 [28]). 8 ¯aha. kim. punaratra s¯adh¯ıyah. pad¯ana¯m. prakr.titvam. sam. hita¯y¯a vik¯aratvamuta va¯ vik¯aratvam. pad¯ana¯m. prakr.titvam. sam. hit¯ay¯a iti? ucyate sam. hit¯aya¯h. prakr.titvam. jya¯yah. . ¯aha. kim. ka¯ran. am? ucyate. mantro hyabhivyajyama¯nah. pu¯rvamr.s.ermantradr.´sah. sam. hitayaiv¯abhivyajyate na padaih. . (Durga. 1.17 [28]).

---

<!-- page 255 -->

242 A. Mishra
1.2 S´iks.¯a
The S´ik.sa¯ texts, e.g. the Vya¯sa-S´iks.a¯ [12] or Na¯rad¯ıya¯-S´iks.a¯ [1] undertake a detailed enquiry into the sound units, attach a number of attributes like svara, vyan˜jana, spar´sa etc. and also make a number of statements as to the combinations of these units and/or their attributes.9 For example:
ik¯aram. yatra pa´syeyurika¯ren. aiva sam. yutam | ud¯attamanud¯attena pra´sli.s.tam. tam. nibodhata | | (N¯a. S´i. 2.1.6). Where a short uda¯tta /i/ is seen to join a short anuda¯tta /i/ the resulting svarita should be known as pra´sli.s.ta ([1] p. 109).
Here again a statement is made as to the characterization of a constituent which is the result of some other operation, which in turn is conditioned in terms of certain constituents like /i/ and attributes like ud¯atta and anuda¯tta sounds.
1.3 Chandas
The texts concerned with metrical systems (chandas) also function in a similar manner. The given phenomena here are the vedic and secular (laukika) Sanskrit expressions. The constituent units in this case are the fundamental sound units (varn. a). It is this much smaller set with which the science of prosody works. The attributes are assigned either to a single sound unit or to syllables (aks. ara) which are certain speciﬁc sequences of basic sound units. The statements or rules specify which attribute should be assigned to which particular unit or to which speciﬁc sequence. An example from the Chandah. ´sa¯stra of Pin˙ gala [4]:
g¯ayatrya¯ vasavah. | (Cha. S´a¯. 3.3). A verse quarter (pa¯da) containing eight (vasu) syllables (aks. ara) is called g¯ayatr¯ı.
The most important unit in case of Chandah. ´sa¯stra is an aks.ara or syllable. This unit has two basic attributes, namely light (laghu) and heavy (guru). A verse or linguistic expression is seen as a sequence of syllables. Depending upon the number and distribution of syllables in a verse, diﬀerent verse names or characterizing attributes are assigned to that sequence. The conditions are expressed using one or more of the following considerations:
1. Number of syllables in a sequence 2. Sum of the weights (m¯atra¯) of the syllables in a sequence 3. Distribution of syllables in a sequence 4. Number of sub-sequences (pa¯das) 5. Syllable at which a p¯ada or word starts 6. Syllable after which a pause is to be made
9 For an exhaustive list of the topics covered in the Vya¯sa-S´iks.a¯ see [12] pp. 5-16.

---

<!-- page 256 -->

Modelling As.t.a¯dhy¯ay¯ı 243
The only operation here is that of attribute assignment. The entire ﬁeld of operation is considerably simple and straight forward compared, for example, to the operations of As.t. a¯dhya¯y¯ı. Chandah.´sa¯stra deals primarily with numbers. It uses various names for numbers and provides groupings based on numerical values. Since, there are two basic attributes laghu and guru which a syllable can take, it is akin to the binary sequences of 0 and 1. The conditions are such, that the numerical characteristics are to be exploited.
Methodologically, however, the process can again be seen as follows: Given a linguistic expression, it is ﬁrst analyzed into constituent units. In this case the units are syllables and the process of analysis can also be automatic and rule-based. The units are characterized by using the two basic attributes (laghu and guru) which sometimes depend on the neighboring units as well. Now the combination of these units in that sequence provides conditions for assigning the verse characterizing attributes to that linguistic expression. In this manner, the expression gets a prosodical identity. This assures the reproduction of that expression according to its standard rendering. This way, the prosodical characteristics of a given expression are retained.
1.4 Vy¯akaran. a
The given phenomena which the grammarians like Pa¯n. ini are representing are vedic utterances as well as the correct Sanskrit expressions according to the standard usage prevalent among the cultivated people during their time.10 Given a collection of such linguistic expressions, As.t. a¯dhya¯y¯ı provides a description in terms of constituent units out of which they are composed. It characterizes these units by attaching a number of attributes to them and provides for their appropriate combinations. A process of synthesis is speciﬁed which forms the given linguistic expressions from these building blocks. The grammar, thus, connects the basic units with the original expressions. The constituent units and the rules of synthesis together provide a systematic structure to represent the standard usage. In this way, grammar provides a description of the object set and helps in retaining and upholding the given. This is one of the main purposes of its composition (See Sect. 3).
The brief account of the basic methodological approach of some of the Ved¯an˙ ga texts is to illustrate the possibility to read them from the perspective of the framework mentioned above. This involves recognizing and identifying the components, scrutinizing their character and detecting the relationships between these components. A model which may account for a broader coverage of the processes of ancillary disciplines (Ved¯an˙ ga) should ﬁrst and foremost concentrate on these core processes. A particular system can then be modelled as a special instance of this general model. We now turn our attention to propose a general model ﬁrst.
10 The question as to what exactly is the content of this object set is of no direct relevance to the model presented in this chapter. What is necessary is to acknowledge that some object set is being analyzed and described. For a discussion about the nature of this set see [3] pp. 183-206.

---

<!-- page 257 -->

244 A. Mishra

2 A Model for the General Methodology of Ved¯an˙ ga

2.1 Phenomenon, Description and Its Model

The general eﬀort which is evident in the ancillary texts is towards observing and describing a set of some given phenomena. An instance can be the collection of utterances (sam. hit¯a-p¯a.tha) in the S´ukla-Yajurveda or the collection of correct and standard Sanskrit expressions. Yet another example may be even the rituals performed during a vedic sacriﬁce. Let us say, we represent this set of given phenomena by the symbol Ω. The object set Ω, therefore, is the collection of given phenomena which is to be analysed and described.

Ω : a set of given phenomena

(1)

Let us now represent by the symbol ∆ the description of the object set Ω. This is what the diﬀerent ancillary disciplines provide.

∆ : a description of Ω

(2)

We can now specify the relationship between the object set (Ω) and the descrip-

tion (∆) as follows:

Ω≈∆

(3)

This description ∆ represents the works like the Chandah. ´sa¯stra of Pin˙ gala, the As.t. a¯dhya¯y¯ı of Pa¯n. ini or the Va¯jasaneyi-Pra¯ti´sa¯khya. A model M for this description ∆ is what we seek. Let the symbol M∆ represent this model.

M∆ : a model of ∆

(4)

We specify this relationship as follows:

∆ ≃ M∆

(5)

Now let us say that ∆p represents the descriptions as mentioned in the Va¯jasaneyi-Pra¯ti´sa¯khya. Then M∆p is the corresponding model of this description. Similarly, if ∆c represents the description which the Chandah. ´sa¯stra provide and ∆a represents the description which the As.t. a¯dhya¯y¯ı gives, then
the corresponding models would be given by M∆c and M∆a respectively. The hypothesis is that the models M∆p , M∆c and M∆a can be generalized
to a general model M∆ which corresponds to the core structure and processes common to all the descriptions.11 In the following, we specify a general model

11 Owing to the constraints of space, only the above mentioned three descriptions are dealt with. The hypothesis can include descriptions coming from S´ik.s¯a, Nirukta, Kalpa and Jyotis. a texts as well. Apart from the linguistic aspects which these texts contain, the other facets, e.g. the performances of sacriﬁcial rituals as contained in the Gr. hya-su¯tra also exhibit a similar approach. The structural analysis of rituals
is one of the prime foci of the ongoing special research area “The Dynamics of
Rituals (Ritualdynamik)” at the University of Heidelberg (www.ritualdynamik.de).
Ritual experts (Staal [25], Oppitz [19], Michaels [13] [14], Houben [10]) acknowledge
the compositional character of rituals. Mishra [17] connects it with the grammatical process of As.t. a¯dhya¯y¯ı.

---

<!-- page 258 -->

Modelling As.t.¯adhy¯ay¯ı 245
of this methodological approach and then show that the descriptive techniques employed by the As.t. a¯dhya¯y¯ı of P¯an. ini can be modelled within this general framework.
2.2 Towards a General Model for the Ancillary Disciplines
First let us look into the description ∆. What does ∆ look like? For that, we ﬁrst consider the descriptions as provided by
∆p : the Va¯jasaneyi-Pra¯ti´sa¯khya ∆c : the Chandah. ´sa¯stra of Pin˙ gala and ∆a : the As.t. a¯dhya¯y¯ı of Pa¯n. ini.
Three basic categories are evident here with which the descriptive technique works. These are:
U : the constituent units of a given phenomenon A : the nature, characteristics or attributes of these constituent units S : statements about constituent units, attributes and about the statements
themselves.
Constituent Units. If we look into the corpus of these texts, a big collection of constituent units can be identiﬁed: speech-sounds or phonemes like a, i, u etc., morphemes like bhu¯, l(a)(.t), (´s)a(p), ti(p) etc. and words like sarva, ananta etc.
Attributes. The constituent units possess a number of attributes that reﬂect their physical, linguistic or structural peculiarities. We use the general term attribute to represent a broader category of designations (sam. jn˜a¯) or expressions that encode some information — be it the system internal or the system external — and associate it with the appropriate unit. For example, the technical term guru is an attribute carrying information that is gained from the distribution of sound units in a string. On the other hand, belongingness to a particular group of literature is an attribute that carries system external information.12
Statements. The Ved¯an˙ ga texts enunciate constituent units together with their attributes. Further, they correlates them. For this purpose, a number of statements are made. Given units and attributes, the statements tell us which attributes are associated with which units or how are two units connected with each other. Many of them tell us the consequences when certain units come closer or are present adjacent to each other. Some statements also inform us about the
12 These external world information can be of diﬀerent sorts: phonetic peculiarities, concepts, meanings, pragmatic considerations, some special occasion, opinions, social conventions, a particular group of texts, special geographical regions etc. See, for example alam. khalvoh. prati.sedhayoh. pra¯c¯am. ktv¯a (A. 3.4.018), ud¯ıc¯am. m¯an˙ o vyat¯ıh¯are (A. 3.4.019), lin˙ a¯´si.si (A. 3.4.116), chandasyubhayatha¯ (A. 3.4.117) and a number of such rules.

---

<!-- page 259 -->

246 A. Mishra

working of the system, the meta-level information for proper interpretation and application of other rules. By providing the combinational possibilities of units, statements constitute a connecting link between these units and the original or given linguistic expression.
The description ∆ as provided in texts like As.t. a¯dhya¯y¯ı can be modelled on the basis of these three categories.13 We propose:
Proposition 1 (A General Model M∆ for ∆). Given a description ∆ of some object set Ω. A general model M∆ of this description consists of a triplet (U, A, S), where U is the set of constituent units, A the set of attributes and S the set of statements.

M∆ = (U, A, S)

(6)

To sum up, our hypothesis is as follows:

1. There is a methodological similarity in the approach of ancillary disciplines (Veda¯n˙ ga).
2. They start with observing a set of given phenomena (Ω). 3. They provide a description (∆) of the given phenomena Ω. 4. This description is achieved by providing the constituent units U , assigning
them attributes A and making a number of statements S. We represent this through the symbol M∆. 5. M∆ ﬁnally connects the constituent units to the original or the given phenomenon.

Symbolically, the methodological approach can be represented as:

Ω ≈ ∆ ≃ M∆ = (U, A, S)

(7)

Before we make some observations on this hypothesis (in Sect. 3.1 and 4), a few examples are needed to elucidate the model and to indicate its feasibility.

2.3 Enunciating the Units, Specifying Attributes and Operations
The authors of Veda¯n˙ ga texts can be seen as constantly and consistently forming groups and sub-groups of units they enunciate. The purpose of group formation is to club together necessary constituents which undergo some similar operation. This way higher degree of generalization is possible. This is the core philosophy of la¯ghava: to reduce the load by specifying some statement for all the units which share the relevant characteristics and do not handle them individually.
Every element of a group shares a common characteristic: this is the characteristic that it is a part of that group. This characteristic can be expressed in terms of an attribute. The name of the subset is the attribute deﬁned and each element of that subset is assigned that attribute. Grouping together related units is one way of assigning an attribute to them.
13 For the purpose of computer modelling an appropriate data structure is required (see Sect. 3.3).

---

<!-- page 260 -->

Modelling As.t.¯adhy¯ay¯ı 247
Example 1. Consider the subset a(c) formed in S´ivasu¯tras:14
a(c) = {a, i, u, r. , .l, e, o, ai, au}15
This is equivalent to the statement that the units {a, i, u, .r, .l, e, o, ai, au} are assigned the attribute a(c).
a-a(c), i-a(c), u-a(c) etc.
Every set of units can be seen as unit-attribute pair and conversely unit-attribute pairs can be seen as constituting a set. Looking from this perspective, the praty¯ah¯ara, for example, are nothing but attributes.
Example 2. Let us now look at the enunciation of the basic speech-sounds in Va¯jasaneyi-Pra¯ti´sa¯khya.16 Here there is a very clear grouping of the listed speech-sounds in diﬀerent sets like varn. a, svara, sandhyak.sara, vyan˜jana, kavarga, spar´sa etc.
svara = {a, a¯, a¯3, i, ¯ı, ¯ı3, . . . , au, au3 } sandhyaks. ara = {e, e3, ai, ai3, o, o3, au, au3 }
This again can be seen as assigning the attribute svara or sandhyak.sara to each element of the corresponding set. In other words, the units like a get the attributes like svara. Symbolically, a-svara, e-{svara, sandhyaks. ara}.
Example 3. Consider the rule A. 1.1.001: vr. ddhira¯daic [Assign vr. ddhi to units having ¯a(t) or ai(c)].
This rule performs the operation of attaching an attribute to certain speciﬁc units. The condition is that the units to which this attribute can be attached must possess either the attribute a¯(t) or ai(c). Let us say, we have a unit ui with either a¯(t) or ai(c):
ui-{¯a(t), ai(c)}
Then the present rule stipulates that the attribute v.rddhi is to be assigned to that unit:
ui-{a¯(t), ai(c)} ⇒ ui-{vr. ddhi}17
The conditions are expressed here in terms of attributes and the operation performed is assignment of an attribute.
14 a i u (n. ) | r. l. (k) | e o (n˙ ) | ai au (c) | . . . h (l) | (S´ivasu¯tra 1-14). 15 The sub-sets are formed using the it-markers and the rule A. 1.1.071: a¯dirantyena
sahet¯a [The ﬁrst sound and the last it sound includes the units occuring in between the sequence]. 16 atha¯to varn. asam¯amn¯ayam. vya¯khya¯sy¯amah. | tatra svara¯h. prathamam | a iti a¯ iti a¯3 iti . . ..¯l3 iti | atha sandhyak.sar¯an. i | e iti e3 iti ai iti ai3 iti o iti o3 iti au iti au3 iti | iti svara¯h. | . . . ete pan˜cas. as..tivarn. ¯a brahmara¯´sira¯tmav¯acah. | (V¯a. Pr¯a. 8.1-25). 17 Notation: A ⇒ B: State B results from state A after the application of a rule.

---

<!-- page 261 -->

248 A. Mishra
Example 4. Let us take another example of attribute addition. The groupings in the Dha¯tu-pa¯t. ha can be seen as assigning the attributes like bhv¯adi, cur¯adi etc. to respective units. The rule bhu¯va¯dayo dh¯atavah. (A. 1.3.001) assigns the attribute dha¯tu to certain units grouped in a collection. So a unit like bhu¯ gets this attribute. The condition here is expressed not in terms of attributes but in terms of certain units like bhu¯, ad(a), hu etc. If there is a unit ui which is identiﬁed as bhu¯, then that unit gets the attribute dh¯atu:
ui-{bhu¯ } ⇒ ui-{dh¯atu}
Example 5. The rule halo’nantara¯h. sam. yogah. (A. 1.1.007) assigns the attribute to two units sharing the attribute h[a](l) if they occur consecutively.18 This condition is based on the phonetic characteristics as well as their positional (or structural) relatedness.
Example 6. The assignment of the attribute sampras¯aran. a in the rule igyan. ah. sampras¯aran. am (A. 1.1.045) is based not only upon the attribute i(k) but also upon the process of vocalization.19 So, an operation or a statement can also be a condition for another operation or statement.
Example 7. Let us now take an example for combination of units. The rule guptijkidbhyah. san (A. 3.1.005) stipulates the combination of units gup(a), tij(a) and kit(a) with the unit sa(n). Now, the units gup(a), tij(a) and kit(a) get the attribute dh¯atu by the rule bhu¯va¯dayo dh¯atavah. (A. 1.3.001). The rule pratyayah. (A. 3.1.001) assigns the attribute pratyaya to the unit sa(n). Now, the rule para´sca (A. 3.1.002) says that those units, which are having pratyaya as attribute must be attached after the units having the attribute dh¯atu. In the light of all this information, it can be said that sa(n)-pratyaya is added after gup(a)-dha¯tu etc.
ui-{gup(a), tij(a), kit(a)} ⇒ ui ≺ uj-sa(n)20 ui-dh¯atu ≺ uj-pratyaya
Example 8. The statement vartam¯ane la.t (A. 3.2.123) facilitates the addition of the unit l(a)(.t) after a unit having the attribute dh¯atu. The condition for introduction is told in terms of a semantic attribute vartam¯ana. It can be seen as a statement which says that the unit l(a)(.t) can be introduced after a dha¯tu if the semantic attribute vartam¯ana is present.21
These few examples are to illustrate the possibility to read these texts from the perspective of the model mentioned above. This framework needs to be
18 Anantaram. sam. yogah. (Va¯. Pr¯a. 1.48). 19 Vocalization is mentioned in the As.t. a¯dhya¯y¯ı from s. yan˙ ah. samprasa¯ran. am.
putrapatyostatpuru.se (A. 6.1.013) to vibh¯a.sa¯ pareh. (A. 6.1.044). 20 Notation: x ≺ y represents ‘y follows x’. 21 The question as to how the semantic attributes like vartam¯ana be made available is
an important aspect for computer implementation of the rules. See Sect. 3.4.

---

<!-- page 262 -->

Modelling As.t.a¯dhy¯ay¯ı 249
tested further for its applicability. One way of testing it is to develop a computer implementation of the same. Next, we mention the main features of the computer implementation of the general model and then its special instance in case of the As.t. a¯dhya¯y¯ı.
3 Computer Implementation of M∆
In Sect. 2.2 we proposed a model M∆ for representing the description ∆ of some phenomena Ω. The description ∆ here denotes the texts like As.t. a¯dhya¯y¯ı corresponding to the set Ω of linguistic expressions. This model M∆ consists of a set of constituent units U , attributes A which characterize them and a number of statements S which tell us which unit gets which attribute and how the units can be modiﬁed. All three — units, attributes and statements — can appear as a condition for some operation. Within the context of a particular description, e.g. the As.t. a¯dhya¯y¯ı ∆a, there are many conventions which make the description understandable, explicit and precise.
A computer implementation of this model has two concurrent goals: ﬁrstly, it serves as a tool to check the suitability of the proposed model for representing the ancillary disciplines; and secondly, it explores the possibility of rendering these texts in a programmed manner, thus underlying their structured composition as well as bringing to surface the structures of the objects of these description.
3.1 Some Pre-suppositions
There are certain assumptions regarding the nature of the grammatical system of P¯an. ini that shape the overall architecture of its computer implementation. Without entering into the discussions associated with some of these pre-suppositions (sometimes spanning over more than two millenia) for the sake of presenting a clear picture of the architecture, I think it is appropriate to mention them.22
I see As.t. a¯dhya¯y¯ı within the overall context of the nature of enquiry as contained in the ancillary disciplines (Ved¯an˙ ga) and the methodological approach adopted by them. There are striking similarities (see Sect. 1). The main objective of these disciplines is to retain and carry the given (vedic phenomena) and use it correctly. In the Paspa´sa¯hnika, while enunciating the purpose of grammar, Va¯rtikaka¯ra mentions preservation or retention to be the ﬁrst goal.23 This is possible only when an exact description of the essential characteristics of the original is composed. It is desired that this description be shorter than the original. Only then can it facilitate a feasible retention of the original. This is
22 There is, for example, a diﬀerence of opinion as to how exactly the P¯an. inian process works: whether it is an automatic device to generate correct Sanskrit sentences, starting from meaning and providing at the end valid linguistic expressions or rather it is a reconstitutive or cyclical process beginning with provisional statements and resulting in perfected (sam. sk.rta) expressions [9]. For a recent update in some of the important, but still unresolved issues, see [24].
23 raks.oha¯gamalaghvasam. deh¯ah. prayojanam (Pas. V¯a. 2).

---

<!-- page 263 -->

250 A. Mishra
sought to be achieved by identifying those units which appear recurrently in the original. For reproducing the original, the units need to be combined. For this purpose rules are to be formulated. These rules of synthesis are the connecting threads which connect the description with the original. Securing this connection is of utmost importance. A description that is not properly related with the original is not authoritative. This, for example, is what the Pra¯ti´s¯akhyas seek to achieve: to connect the pada-p¯a.tha with the original sam. hit¯a-p¯a.tha. And this is what a grammarian does by formulating the rules of grammar: connecting the constituents with the original.
A grammarian, however, crystallizes two substantial new steps. Firstly, he opens the object set for expressions which do not necessarily and exclusively belong to vedic expressions.24 Secondly, he increasingly employs non-real (k¯alpanika) constituent units which do not have any correspondence in the real or given world. N¯age´sabhat.t.a in his Vaiya¯karan. a-siddha¯nta-parama-laghu-man˜ju¯s.a¯ remarks the imaginary nature of the constituent units that are improvised by the teachers and employed only within the grammatical system.25 For example, units like l(a)(.t) or jhi are not to be found in the world, but are stipulated by the grammarian. This implies, now it is all the more incumbent to provide the connection with the original through the formulation of precise rules. Through his grammar P¯an. ini, so to say, converts the imaginary constituent units into real utterances — a kind of satyakriya¯.26 Evidently, there is a direct proportionality between the number of imaginary units in a system and the number of rules as well as the complexity of their interdependence. The number of rules to handle the interconnections between abstract units increases with the increase in abstract units.
Why should new imaginary units be introduced at all? For the sake of a compact and concise formulation of the description. Each imaginary unit carries with it the potential to evolve into a much larger number of ﬁnished forms. Brevity (la¯ghava), therefore, is not only a feature of the meta-language of Pa¯n. ini, but the main idea behind this style of description, namely, to represent an object set through a description set which is less voluminous than the original. This becomes a necessity as the object set expands immensily once opened up for non-vedic expressions as well.27
24 Patan˜jali, right in the beginning of the Paspa´sa¯hnika, mentions ﬁrst the non-vedic expressions and then the vedic ones, which are sought to be instructed. kes. ¯am. ´sabda¯n¯am (anu´sa¯sanam)? laukik¯ana¯m. vaidika¯na¯m. ca | . . . vaidik¯ah. khalvapi | (Pas. Bha¯. 2-3).
25 tatra prativa¯kyam. sam. ketagrah¯asambhav¯ad v¯aky¯anv¯akhy¯anasya laghu¯pa¯yena a´sakyatv¯acca kalpanaya¯ pad¯ani pravibhajya pade prakr.tipratyayabh¯aga¯n pravibhajya kalpit¯abhy¯am anvayavyatirek¯abhy¯am. tattadarthavibha¯gam. ´s¯astram¯atravis.ayam. parikalpayantism¯aca¯ry¯ah. (V. L. [21] p. 7).
26 Thieme suggested this to be the purpose of grammar, although his idea behind this suggestion was that grammar is a device having magical eﬀect which ‘works the truth’ of the special nature of Sanskrit, sam. sk.rtasya sam. skr. tatvam [26]. Houben diﬀers [9], but Scharfe suggests that this direction deserves to be explored further [24] p.87.
27 raks.oha¯gamalaghvasam. deh¯ah. prayojanam | (Pas. V¯a. 2). laghvartham. c¯adhyeyam. vya¯karan. am | (Pas. Bha¯. 20) l¯aghavena ´sabdajn˜¯anamasya prayojanam | (Prad¯ıpa on Pas. Bha¯. 20).

---

<!-- page 264 -->

Modelling As.t.a¯dhya¯y¯ı 251
This also explains the generative potential inherent in the process of synthesis in the As.t. a¯dhya¯y¯ı. This process of synthesis presupposes an analytical phase. The process of analysis itself is not recorded in the grammatical corpus, but only its results [5]. The process of synthesis from constituent units to the ﬁnal linguistic expressions is provided in terms of a number of rules allowing certain combinations of units and restricting others. It is this process which the following computer application aims to implement.

3.2 Architecture and Implementation
A brief sketch of the overall architecture of the computer implementation of the entire process is provided in [16] pp. 53-54. Two basic modules are mentioned there: an Analyzer and a Synthesizer. In the following, I mention a few improvements undertaken since then, especially within the Synthesizer module. These improvements are aimed towards incorporating the following features:
1. The modelling for the process of synthesis as implemented in the Synthesizer module now reﬂects the general model for representing the core processes of ancillary disciplines. It thus percieves As.t. a¯dhya¯y¯ı in the general context of the methodology of Ved¯an˙ ga. This accounts better for the evolution and development of As.t. a¯dhya¯y¯ı.
2. While the basic data structure is kept as in [15], a modiﬁcation in the ProcessStrips is implemented to facilitate a better capability for checking conditions for applicability of operations.
3. A key improvement is now towards automatic application of rules. For this several strategies are incorporated (see below).
4. There is now a possibility to ask the user for information in case it is not available within the system.
We now provide a brief account of the main features of the computer implementation of the structure and processes of As.t. a¯dhya¯y¯ı.

3.3 Basic Data Structure

Language Components and Sound Sets. The core data structure is de-

signed with a view to facilitate the execution of grammatical operations. At any

stage of processing, there is string of speech-sounds which gets modiﬁed. Certain

speech-sounds get added and others get replaced or deleted. This changing string

of speech-sounds is represented through a LanguageComponent which is a list of

sets.

LanguageComponent = [{}, {}, {}, . . .]

(8)

Each set of this list (called SoundSet) represents a speech-sound or a phoneme. It contains attributes which this speech-sound possesses. Moreover, it also contains attributes of units to which it is a part.

bhu¯ = [{bh, dh¯atu, . . .}, {u, a(c), d¯ırgha, dh¯atu, . . .}]

(9)

---

<!-- page 265 -->

252 A. Mishra

Sound Sets

Lang. Comp.

Fig. 1. Sound Sets and Language Components

The LanguageComponent represents linguistic units at all levels: phonemes, morphemes, words, compounds, sentences etc. On the one hand there is no rigid boundary between two units, allowing them to conjoin at ease, and on the other hand, individual units can be identiﬁed on the basis of the characterizing attributes. Another advantage is that it allows, for example, changes at the level of a phoneme, conditioned upon semantic or syntactic attributes. In fact, there is no categorization in terms of phonology, morphology, syntax and semantics; there are only constituent units and attributes. Attributes reﬂect these characters, e.g. a(c) is an attribute reﬂecting phonetic characteristics, dh¯atu a morphological one, apa¯d¯ana a syntactic one and vartam¯ana has semantic nature. But in the LanguageComponent they all occur as an attribute of the corresponding units. The units are, so to say, marked up with the attributes and the appropriate sub-string which corresponds to some attribute can be obtained by performing simple set intersections. For example, consider the following LanguageComponent at some stage of derivation:

[{bh, bhu¯, dh¯atu, . . .}, {u, bhu¯, a(c), d¯ırgha, dh¯atu, . . .}]

(10)

Here, the vowel phoneme can be obtained by intersecting the sound sets with the set {a(c)} and the morpheme denoting a verbal root can be gained by noting the SoundSets which intersect with the set {dh¯atu}.

Basic Operations. An operation brings about some change in the LanguageComponent. This can be of two types: either an attribute is added to one or more SoundSets or the LanguageComponent gets extended at some index. The operations of As.t. a¯dhya¯y¯ı can be implemented on the basis of these two fundamental operations.

Representing operational stages. The basic data structures and operations reﬂect the state of the LanguageComponent at a particular stage in the process of synthesis. This is not enough for the application of many rules, where the conditions include information like how the current rule being applied is related to the rule applied in the previous step. In other words, the successful advancement of the process is not just dependent upon a particular stage but sometimes on previous stages as well. The system must, therefore, be aware of not just a particular stage, but the entire process itself. The entire process is now modelled as a chain of Slices with each Slice representing a given stage in the process of derivation.28
28 This and the following features are new improvements from the previous versions mentioned in [15] and [16].

---

<!-- page 266 -->

Modelling As.t.a¯dhy¯ay¯ı 253
Slices correspond to those operational statements which bring about some modiﬁcation in the LanguageComponent. It consists of an InitialLanguageComponent and a FinalLanguageComponent; the latter one is obtained after the application of an operational rule.

Initial LangComp

Final LangComp

Fig. 2. A Slice
ConditionCodes is a dictionary which stores the necessary information about the speciﬁc operation which is executed at a particular stage. The information is gathered by applying the conditionsCheck functions. These functions check the applicability of an operation at a given stage. In case the function is applicable, they set the corresponding parameters. ConditionCodes associated with each Slice make it possible to trace back the operational steps, thus allowing e.g. the application of rules from tripa¯d¯ı section.
Ancillary Strip. There is an AncillaryStrip now which is the place to assign static attributes to a unit which is to be added. Static attributes are those attributes which are inherently associated with a unit and do not change once assigned, e.g. the attribute a(c) or h[a](l).29 From the point of view of data structure, it is similar to the ProcessStrips.
Process Strip now is a list of Slices. This data structure reﬂects the entire process of synthesis. During the process of synthesis ProcessStrip gets extended, one Slice is added at each operational step. We now present a trace of the important procedural steps.

Fig. 3. Ancillary Strip / Process Strip
3.4 Procedural Steps The process of synthesis is carried on the ProcessStrip which carries with it the necessary information about the current and previous stages of development. 29 For more information, see [16].

---

<!-- page 267 -->

254 A. Mishra
Step 1. The ﬁrst step is to look at the last Slice of the given ProcessStrip, take the FinalLanguageComponent and initialize the next Slice by adding it as the InitialLanguageComponent.

Fig. 4. Step 1: Initializing a new Slice

Step 2. The ProcessStrip is sent to ConditionsCheck module. At this stage conditions are veriﬁed as to which rules can be applied at the current status of the ProcessStrip. It results in a set of ConditionCodes corresponding to applicable rules. For the sake of checking the conditions, certain dynamic attributes (e.g. sam. yoga, .ti etc.) are assigned if required.

Conditions Check

Applicable Rules

Fig. 5. Step 2: Condition Check
Step 3. The next major step is to select one rule from among the set of applicable rules. This is done in a Selector module. The main function of this module takes the set of applicable ConditionCodes and makes it a singelton set.
Here, there are diﬀerent kinds of selection which are to be accounted for.
1. Selection on the basis of semantic conditions / attributes: Even if there is only one rule available for application, there is sometimes a need to select the right unit. For example the rule: tip tas jhi sip thas tha mip vas mas ta a¯t¯am jha tha¯s a¯th¯am dhvam i.t vahi mahin˙ (A. 3.4.078). If the condition is fulﬁlled (e.g. the presence of a laka¯ra) still a selection process is required. This is facilitated by rules like tin˙ as tr¯ın. i tr¯ın. i prathama madhyama uttama¯h. (A. 1.4.101) and t¯ani ekavacana dvivacana bahuvacan¯ani eka´sah. (A. 1.4.102). The attributes prathama, ekavacana etc. are needed to decide with the help of these rules, which suﬃx is to be chosen. From an operational perspective, it is not enough to deﬁne prathama, ekavacana etc. It is required to know whether this attribute is acceptable to the ProcessStrip. There are two ways to determine this: (i) either from the analyzedSet gained from the Analyzer module (see [16]) or (ii) from the user.

---

<!-- page 268 -->

Applicable Rules

Modelling As.t.¯adhya¯y¯ı 255
Selector

Fig. 6. Step 3: Selecting one rule from the set of applicable rules
2. Selection when two applicable operations have two completely unrelated sth¯anins: Here it is required to select between two operations, which are both applicable at a given stage, but have completely unrelated place of application within the ProcessStrip. This can happen e.g. in cases when more than one word is to be processed simultaneously in a linguistic expression. This issue needs more attention in the future development of the system.
3. Conﬂict Resolution: This is the case when given two applicable rules r1 and r2 a deﬁnite order, say ﬁrst r1 then r2, must be followed. Otherwise, it leads to wrong results. Here we use primarily the siddha principle [7], [8], which involves copying the current ProcessStrip, applying both the rules and checking whether one destroys the nimitta for the other (see [16]).
4. There is a mechanism to test the mutual rule ordering between two rules which come closer during the process of synthesis. It is eﬀected by noticing the mutual order in their ConditionCodes. This may later result in a kind of rule dependency graph of As.t. a¯dhya¯y¯ı.
The selected ConditionCode becomes now a part of the Slice.
Step 4. The entire ProcessStrip now enters the Operations module where, depending upon the values in ConditionCode, an operation is performed. It modiﬁes the LanguageComponent, adds it as the FinalLanguageComponent to the Slice and returns the ProcessStrip.
Modiﬁcation of the LanguageComponent is undertaken in the following steps: If a new unit is to be added, then it is passed through a sub-module named StaticAttributes. Here a unit is rendered in the form of a LanguageComponent and one after another the rules for addition of static attributes (like a(c), h[a](l) etc.) are assigned. In this module the order of applicability is linear and the attributes which are used as condition for other rules are assigned before that rule. There is no conﬂict resolution here as it is not needed. Not all the attributes but only the static ones are assigned. This is to improve the performance of the system. ProcessStrip is extended as long as there is some rule which is available for application. During the applicability check, it is taken care of that the rules do not get applied inﬁnitely. This is achieved in that the condition is so formulated that the application of some rule makes its further application at the same location (sth¯anin) on same conditions (nimitta) impossible.

---

<!-- page 269 -->

256 A. Mishra

Static

DB

Attributes Operations

Fig. 7. Step 4: Applying the selected rule

For example, once l(a)(.t) is introduced after a dh¯atu, it is not introduced again. So the condition check includes checking for the already presence of l(a)(.t).

4 Some Observations
The model presented above and the corresponding implementational design is aimed to facilitate the representation of the content, structure and operations of the methodological enquiry of ancillary disciplines (Ved¯an˙ ga) in general and the As.t. a¯dhya¯y¯ı of Pa¯n. ini in particular.
The entire framework is based on a minimal set of categories (U nits, Attributes, Statements). The scheme of the general architecture and the core data structures is such as to allow to represent the functionalities of interpretative procedures (e.g. paribha¯s. a¯s, siddha-principle [7]) and additional amendments (e.g. V¯artika).
The system is not guided by any ﬁxed external organization, for example, the division of the grammatical corpus in ´siva-su¯tra, su¯tra-pa¯.tha, dh¯atu-pa¯.tha, gan. a-pa¯.tha, un. ¯adi-su¯tra etc. or any reorganization of these under categories of modern linguistics (see e.g. [23] p. 97), but focuses on the core methodology. There is, however, a possibility to make the system aware of these divisions. The approach is to identify the constituent units and assign a number of attributes to them and then on the basis of these represent the external structures.

Table 1. Abbreviations

A.

As.t. a¯dhya¯y¯ı

Uv.

Uvat. a-bha¯s.ya on R. gveda-Pra¯ti´sa¯khya

Cha. S´¯a. Chanda-S´a¯stra of Pin˙ gala

Ni.

Nirukta

Pas.

Paspa´sa¯hnika

Pas. B¯a. Paspa´sa¯hnika Bha¯s.ya

Pas. V¯a. Paspa´sa¯hnika Va¯rtika

Mu.

Mun. d. akopanis.ad

Mu. Bh¯a. Mun. d. akopanis.ad S´a¯n˙ kara-Bha¯s.ya

V. L.

Vaiya¯karan. a-siddha¯nta-parama-laghu-man˜ju¯s.a¯

Va¯. Pr¯a. Va¯jasaneyi-Pra¯ti´sa¯khya S´u. Yaj. S´ukla-Yajurveda

---

<!-- page 270 -->

Modelling As.t.¯adhya¯y¯ı 257
The system allows for the representation of the content, structures and processes of other ancillary disciplines (e.g. S´ik.sa¯, Chandas, Nirukta, Pra¯ti´sa¯khya etc.) thus facilitating a more comprehensive and comparative study of these sciences. The possibility of system external (human) input during the process of synthesis is now taken into account.
References
1. Bhise, U.R.: N¯arad¯ıy¯a S´iks.¯a with the Commentary of Bhat.t.a S´obha¯kara. Bhandarkar Oriental Research Institute, Poona (1986)
2. von B¨ohtlingk, O.: P¯an. ini’s Grammatik. Olms, Hildesheim (1887) 3. Bronkhorst, J.: Greater Magadha. Studies in the Culture of Early. Brill, Leiden
(2007) 4. Dhu¯pakara, A.S´.: S´r¯ıpin˙ galan¯aga-viracitam. Chandah.´s¯astram. Parimal Publica-
tions, Delhi (1985) 5. Deshpande, M.M.: Semantics of K¯arakas in P¯an. ini: An Exploration of Philosoph-
ical and Linguistical Issues. In: Matilal, B.K., Bilimoria, P. (eds.) Sanskrit and Related Studies: Contemporary Researches and Reﬂections, pp. 33–57. Sri Satguru Publications, Delhi (1990) 6. Gladigow, B.: Sequenzierung von Riten und die Ordnung der Rituale. In: Stausberg, M. (ed.) Zorostrian Rituals in Context. Numen Book Series, Studies in the History of Religions, vol. CII, pp. 57–76. Brill, Leiden (1999) 7. Joshi, S.D., Roodbergen, J.A.F.: On siddha, asiddha and sth¯anivat. Annals of the Bhandarkar Oriental Research Institute, Bhandarkar Oriental Research Institute, vol. LXVIII, pp. 541–549. Bhandarkar Oriental Research Institute, Poona (1987) 8. Joshi, S.D., Roodbergen, J.A.F.: The As.t.¯adhya¯y¯ı of P¯an. ini. With Translation and Explanatory Notes, vol. II. Sahitya Akademi, New Delhi (1993) 9. Houben, J.E.M.: ‘Meaning statements’ in P¯an. ini’s grammar: on the purpose and context of the As.t.a¯dhya¯y¯ı. Studien zur Indologie und Iranistik 22, 23–54 (19992001) 10. Houben, J.E.M.: Memetics of Vedic Ritual, Morphology of the Agnis.t.oma. In: Griﬃths, A., Houben, J.E.M. (eds.) The Vedas: Texts, Language & Ritual, pp. 23–47. Forsten, Groningen (2004) 11. Katre, S.M.: As.t.a¯dhya¯y¯ı of P¯an. ini. Motilal Banarsidass, Delhi (1989) 12. Lu¨ders, H.: Die Vyˆasa-C¸ ikshˆa besonders in ihrem Verh¨altnis zum TaittirˆıyaPrˆati¸caˆkhya. G¨ottingen (1894) 13. Michaels, A.: ‘Le rituel pour le rituel’ oder wie sinnlos sind Rituale? In: Caduﬀ, C., Pfaﬀ-Czarnecka, J. (eds.) Rituale heute: Theorien - Kontroversen - Entwu¨rfe, pp. 23–47. Reimer, Berlin (1999) 14. Michaels, A.: The Grammar of Rituals. In: Michaels, A., Mishra, A. (eds.) Grammar and Morphology of Ritual, pp. 15–36. Harrassowitz Verlag, Wiesbaden (2010) 15. Mishra, A.: Simulating the P¯an. inian System of Sanskrit Grammar. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics. LNCS (LNAI), vol. 5406, pp. 127–138. Springer, Heidelberg (2009) 16. Mishra, A.: Modelling the Grammatical Circle of the P¯an. inian System. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 40–55. Springer, Heidelberg (2009) 17. Mishra, A.: On the Possibilities of a P¯an. inian Paradigm for a Rule-based Description of Rituals. In: Michaels, A., Mishra, A. (eds.) Grammar and Morphology of Ritual, pp. 91–104. Harrassowitz Verlag, Wiesbaden (2010)

---

<!-- page 271 -->

258 A. Mishra
18. Lakshman, S.: The Nighan. t.u and The Nirukta. Motilal Banarsidass, Delhi (1967) 19. Oppitz, M.: Montageplan von Ritualen. In: Caduﬀ, C., Pfaﬀ-Czarnecka, J. (eds.)
Rituale heute: Theorien - Kontroversen - Entwu¨rfe, pp. 73–95. Reimer, Berlin (1999) 20. Sarup, L.: The Nighan. t.u and the Nirukta. Motilal Banarasidass, Delhi (1967) 21. Shastri, K.: N¯age´sabhat.t.a-kr.ta Vaiya¯karan. a-siddh¯anta-parama-laghu-man˜ju¯s.a¯. Kurukshetra University Press, Kurukshetra (1975) 22. Shastri, M.D.: The R. gveda-Pr¯ati´s¯akhya with the commentary of Uvat.a. Vaidika Svadhyaya Mandir, Varanasi (1959) 23. Scharf, P.M.: Modeling P¯an. inian Grammar. In: Huet, G., Kulkarni, A., Scharf, P. (eds.) Sanskrit Computational Linguistics 2007/2008. LNCS (LNAI), vol. 5402, pp. 95–126. Springer, Heidelberg (2009) 24. Scharfe, H.: A new perspective on P¯an. ini. In: Indologica Taurinensia, vol. XII, pp. 1–273 (2009) 25. Staal, F.: Rules without meaning: ritual, mantras and the human sciences. Lang, New York (1989) 26. Thieme, P.: Meaning and form of the ‘grammar’ of P¯an. ini. Studien zur Indologie und Iranistik 8/9, 12–22 (1982) 27. Varma, V.K. (ed.): V¯ajasaneyi-Pr¯ati´s¯akhyam. Chaukhamba Sanskrit Pratishthan, Delhi (1987) 28. Varma, V.K.: R. gveda-Pr¯ati´s¯akhyam. Banaras Hindu University Sanskrit Series, Varanasi (1972) 29. Wezler, A.: On the quadruple division of the Yoga´s¯astra, the caturvyu¯hatva of the Cikits¯a´s¯astra and the ‘four noble truths’ of the Buddha. In: Indologica Taurinensia, vol. XII, pp. 289–337 (1984)

---

<!-- page 272 -->

Author Index

Ajotikar, Anuja 106 Ajotikar, Tanuja 106
Bhattacharyya, Pushpak 190
Dangarikar, Chaitali 106, 190 Devi, Sobha Lalitha 209 Dharurkar, Chinmay 106
Gillon, Brendan S. 218 Gopal, Madhav 150
Hamann, Silke 21 Hellwig, Oliver 162
Jha, Narayana 39
Katira, Dipesh 106 Kishore, Prahallad 39 Kulkarni, Amba 57, 70, 173, 198 Kulkarni, Irawati 190 Kulkarni, Malhar 106, 190 Kumar, Anil 57
Mahananda, Baiju 39 Mani, Diwakar 137

Mishra, Anand 239 Mishra, Diwakar 150 Mittal, Vipul 57 M. Scharf, Peter 48
Nair, Sivaja S. 173
Patil, Ramalinga Reddy 39 Petersen, Wiebke 21 Pokar, Sheetal 70 Pralayankar, Pravin 209 Prasad, Abhinandan S. 124
Raju, C.M.S. 39 Rao, Shrisha 124
Sharma, Rama Nath 1 Shukl, Devanand 70, 198 Shukla, Preeti 198 Singh, Devi Priyanka 150 Singh, Navjyoti 91 Subbanna, Sridhar 231
Tavva, Rajesh 91
Varakhedi, Shrinivasa 39, 231