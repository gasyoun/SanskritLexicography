_Created: 28-08-2026 · Last updated: 05-09-2026_

# Blind judging brief - 10 PWG TM fragments

_Created: 28-08-2026 - Last updated: 28-08-2026_

Judge model required: **Grok 4.5 (`grok-4.5`)**. Grok 4.6 may NOT run this as an independent gate - it generated the targets, and `pwg_tm_quality.independence_errors` refuses it.

## Rules

You are an independent adjudicator for a German-to-Russian scholarly dictionary translation memory (Petersburger Woerterbuch, Boehtlingk-Roth). You judge one fragment at a time, against its German source only. You never see, and must never assume, how the target was produced.

House conventions that are CORRECT and must not be penalised:
- Sanskrit in `{#...#}`, literary sigla in `<ls>...</ls>`, and lexicographic abbreviations in `<ab>...</ab>` are kept VERBATIM in the target. An `<ab>` token identical to its source is correct, not untranslated.
- `{%...%}` spans hold natural-language gloss prose and are the part that gets translated into Russian.

Return STRICT JSON only, no prose outside it, with exactly these keys:
  "defect_class": one of german_residue, markup_drift, none, placeholder_rendered_as_content, register_or_style, sanskrit_dropped_or_altered, sense_absent_or_inverted, target_typo, unfaithful_to_source, wrong_lexical_meaning
  "fidelity": "pass" or "fail"   (is the target faithful to the source, with nothing invented and nothing silently dropped?)
  "equivalence": "correct" or "fail"   (does the target carry the same meaning a Russian lexicographer would accept?)
  "notes": one short English sentence naming the exact span at fault, or why it is clean.

Definitions of defect_class you must use:
  none                            - faithful and equivalent
  placeholder_rendered_as_content - an argument-slot placeholder such as "Jmd" rendered as a content phrase
  wrong_lexical_meaning           - a gloss translated to the wrong sense
  sense_absent_or_inverted        - a sense dropped or reversed
  sanskrit_dropped_or_altered     - `{#...#}` or `<ls>` content changed
  unfaithful_to_source            - target asserts something the source does not
  german_residue                  - a `{%...%}` span left in German
  markup_drift                    - a preserved span altered in form
  register_or_style               - meaning holds, register is off
  target_typo                     - a typo in the Russian only

Pick the SINGLE most severe applicable class. Do NOT output a severity or seriousness field: severity is derived from defect_class downstream.

## Output

Return one JSON object per fragment, in packet order, as a JSON array. Each object carries `record_id`, `defect_class`, `fidelity`, `equivalence`, `notes`. Do NOT output a seriousness field.

## The 10 fragments

### 0. `pwg.frag.v1:definition_gloss:1629a1acc1604b4f952cb4c` (definition_gloss, headword `ruh`)

**German source:**

```
{%gewachsen%}
```

**Russian target:**

```
{%gewachsen%}
```

### 1. `pwg.frag.v1:definition_gloss:3e0c74c36621b288644df27` (definition_gloss, headword `arTay`)

**German source:**

```
{%Jmd%}
```

**Russian target:**

```
{%Jmd%}
```

### 2. `pwg.frag.v1:definition_gloss:731a0d4153badfa579b3aa5` (definition_gloss, headword `2`)

**German source:**

```
{%die%}
```

**Russian target:**

```
{%die%}
```

### 3. `pwg.frag.v1:definition_gloss:e747ebfbdbc3635b37f0531` (definition_gloss, headword `krand`)

**German source:**

```
{%Jmd%}
```

**Russian target:**

```
{%Jmd%}
```

### 4. `pwg.frag.v1:definition_gloss:ff034285d0dd2872f142bce` (definition_gloss, headword `saYj`)

**German source:**

```
{%Jmd%}
```

**Russian target:**

```
{%Jmd%}
```

### 5. `pwg.frag.v1:recurring_formula:ef89c1f46831f94c731cd6` (recurring_formula, headword `taruRa`)

**German source:**

```
<ab>v. a.</ab>
```

**Russian target:**

```
<ab>v. a.</ab>
```

### 6. `pwg.frag.v1:sense:13d4c386bd092c45c0eaa9fa197809b850` (sense, headword `gam`)

**German source:**

```
4〉 {%Jmd%} (<ab>acc.</ab>) {%zu Etwas%} (<ab>acc.</ab>) {%erwählen%}: {#yaM snAtanaH pitaramupAgamatsvayam#} <ls>BHAṬṬ. 1,1*.</ls>
<div n="1">— 
```

**Russian target:**

```
4〉 {%Jmd%} (<ab>acc.</ab>) {%для чего-л.%} (<ab>acc.</ab>) {%избирать%}: {#yaM snAtanaH pitaramupAgamatsvayam#} <ls>BHAṬṬ. 1,1*.</ls>
<div n="1">— 
```

### 7. `pwg.frag.v1:sense:19b09d8cde04872f635fe6cddf55f7ce43` (sense, headword `upakrama`)

**German source:**

```
4〉 {%Antritt, Anfang, Beginn%} <ls>AK. 3,3,26</ls>. <ls>H. 1510</ls>. <ls n="H.">an. 4,216</ls>. <ls>VEDĀNTAS.</ls>_in_<ls>BENF. Chr. 216,3</ls>. <ls>MADHUS.</ls>_in_<ls>Ind. St. 1,15, ult.</ls> {#pUrvaraNga upakramaH#} ({#nAwyasya#}) <ls>H. 282</ls>. {#upopakramatvAdupadravasya#} {%weil%} {#upadrava#} {%mit%} {#upa#} {%beginnt%} <ls>ŚAṂK.</ls>_zu_<ls>CHĀND. UP. 2,8,2</ls>.
<div n="1">— 
```

**Russian target:**

```
4〉 {%Antritt, Anfang, Beginn%} <ls>AK. 3,3,26</ls>. <ls>H. 1510</ls>. <ls n="H.">an. 4,216</ls>. <ls>VEDĀNTAS.</ls>_in_<ls>BENF. Chr. 216,3</ls>. <ls>MADHUS.</ls>_in_<ls>Ind. St. 1,15, ult.</ls> {#pUrvaraNga upakramaH#} ({#nAwyasya#}) <ls>H. 282</ls>. {#upopakramatvAdupadravasya#} {%так как%} {#upadrava#} {%mit%} {#upa#} {%beginnt%} <ls>ŚAṂK.</ls>_zu_<ls>CHĀND. UP. 2,8,2</ls>.
<div n="1">— 
```

### 8. `pwg.frag.v1:sense:92067db6cb8342b92fb732f78ed2dfcce8` (sense, headword `AtmasAt`)

**German source:**

```
{#AtmasAt#}¦ (von {#Atman#}) <lex>adv.</lex> {%an sich, zu sich, auf sich%}. Nur in Verbindung mit {#kar#} {%thun%}:
<div n="1">
```

**Russian target:**

```
{#AtmasAt#}¦ (von {#Atman#}) <lex>adv.</lex> {%an sich, zu sich, auf sich%}. Nur in Verbindung mit {#kar#} {%thun%}:
<div n="1">
```

### 9. `pwg.frag.v1:sense:c3c9cd88694d804ebd7b5222c0afb78e3d` (sense, headword `vid`)

**German source:**

```
1〉 {%anreden, einladen; ankündigen%} <ls>ṚV. 4,36,2</ls>. <ls n="ṚV. 4,36,">7</ls>. <ls n="ṚV.">10,151,1</ls>. <ls>ŚAT. BR. 5,3,5,31</ls>. {%kund thun, mittheilen, melden, anzeigen%} <ls>YĀJÑ. 2,5</ls>. <ls n="YĀJÑ. 2,">6</ls>. <ls>MBH. 1,3820</ls>. <ls n="MBH.">15,1083</ls>. <ls>HARIV. 9128</ls>. <ls>R. 1,1,60</ls>. <ls>R. GORR. 1,19,1</ls>. <ls n="R. GORR.">2,3,5</ls>. <ls n="R. GORR. 2,3,">7</ls>. <ls n="R. GORR.">4,39,43</ls>. <ls n="R. GORR.">5,56,133</ls>. <ls>KUMĀRAS. 6,21</ls>. {#AtmanaH sumahatkarma vraRErAvedya#} <ls>RAGH. 12,55</ls>. <ls>ŚĀK. 112,15</ls>. {#SayanagfhamArgamAvedaya#} (<ab>v. l.</ab> {#AdeSaya#}) <ls n="ŚĀK.">72,12</ls>, <ab>v. l.</ab> <ls n="ŚĀK.">94,2</ls>, <ab>v. l.</ab> <ls>VIKR. 82,18</ls>. <ls>MĀLAV. 10,7</ls>. <ls>Spr. 1755</ls>. <ls>VARĀH. BṚH. S. 12,15</ls>. <ls>KATHĀS. 3,70</ls>. <ls n="KATHĀS.">18,76</ls>. <ls n="KATHĀS.">22,72</ls>. <ls n="KATHĀS.">25,69</ls>. <ls n="KATHĀS. 25,">280</ls>. <ls n="KATHĀS.">26,50</ls>. <ls n="KATHĀS. 26,">278</ls>. <ls n="KATHĀS.">29,29</ls>. <ls n="KATHĀS.">39,164</ls>. <ls n="KATHĀS.">52,5</ls>. <ls>PRAB. 78,8</ls>. <ls n="PRAB.">83,9</ls>. <ls>BHĀG. P. 1,13,12</ls>. <ls n="BHĀG. P.">3,4,19</ls>. <ls n="BHĀG. P.">7,8,2</ls>. <ls n="BHĀG. P.">10,41,18</ls>. <ls>HIT. 97,13</ls>. {#AtmAnam#} {%sich anmelden, seinen Namen nennen%} <ls>KATHĀS. 22,110</ls>. {#purogAveditaScEnamaByagAtsa purohitam#} {%angemeldet von%} <ls n="KATHĀS.">24,122</ls>. <ls n="KATHĀS.">50,164</ls>. <ls>RĀJA-TAR. 3,116</ls>. <ls n="RĀJA-TAR. 3,">371</ls>. <ls n="RĀJA-TAR.">5,450</ls>. {#rAjYa AvedayaDvaM mAM saMprAptam#} {%meldet, dass%} <ls>R. 1,20,5</ls> (<ls n="R. 1,">21,4 GORR.</ls>). <ls n="R. 1,20,">7</ls>. <ls>R. GORR. 2,3,18</ls>. <ls n="R. GORR. 2,">34,28</ls>. <ls>ŚĀK. 30,4</ls>. <ls>BHAṬṬ. 3,49</ls>. {#yAvadAvedyate rAjYe hataH karRo 'rjunena vE#} <ls>MBH. 8,4992</ls>. {%Jmd%} (<ab>acc.</ab>) {%benachrichtigen%}: {#Avedita#} <ls>RAGH. 5,23</ls>. <ls>RĀJA-TAR. 1,224</ls>.
<div n="1">— 
```

**Russian target:**

```
1〉 {%обращаться, приглашать; возвещать%} <ls>ṚV. 4,36,2</ls>. <ls n="ṚV. 4,36,">7</ls>. <ls n="ṚV.">10,151,1</ls>. <ls>ŚAT. BR. 5,3,5,31</ls>. {%давать знать, сообщать, извещать, объявлять%} <ls>YĀJÑ. 2,5</ls>. <ls n="YĀJÑ. 2,">6</ls>. <ls>MBH. 1,3820</ls>. <ls n="MBH.">15,1083</ls>. <ls>HARIV. 9128</ls>. <ls>R. 1,1,60</ls>. <ls>R. GORR. 1,19,1</ls>. <ls n="R. GORR.">2,3,5</ls>. <ls n="R. GORR. 2,3,">7</ls>. <ls n="R. GORR.">4,39,43</ls>. <ls n="R. GORR.">5,56,133</ls>. <ls>KUMĀRAS. 6,21</ls>. {#AtmanaH sumahatkarma vraRErAvedya#} <ls>RAGH. 12,55</ls>. <ls>ŚĀK. 112,15</ls>. {#SayanagfhamArgamAvedaya#} (<ab>v. l.</ab> {#AdeSaya#}) <ls n="ŚĀK.">72,12</ls>, <ab>v. l.</ab> <ls n="ŚĀK.">94,2</ls>, <ab>v. l.</ab> <ls>VIKR. 82,18</ls>. <ls>MĀLAV. 10,7</ls>. <ls>Spr. 1755</ls>. <ls>VARĀH. BṚH. S. 12,15</ls>. <ls>KATHĀS. 3,70</ls>. <ls n="KATHĀS.">18,76</ls>. <ls n="KATHĀS.">22,72</ls>. <ls n="KATHĀS.">25,69</ls>. <ls n="KATHĀS. 25,">280</ls>. <ls n="KATHĀS.">26,50</ls>. <ls n="KATHĀS. 26,">278</ls>. <ls n="KATHĀS.">29,29</ls>. <ls n="KATHĀS.">39,164</ls>. <ls n="KATHĀS.">52,5</ls>. <ls>PRAB. 78,8</ls>. <ls n="PRAB.">83,9</ls>. <ls>BHĀG. P. 1,13,12</ls>. <ls n="BHĀG. P.">3,4,19</ls>. <ls n="BHĀG. P.">7,8,2</ls>. <ls n="BHĀG. P.">10,41,18</ls>. <ls>HIT. 97,13</ls>. {#AtmAnam#} {%представляться, называть своё имя%} <ls>KATHĀS. 22,110</ls>. {#purogAveditaScEnamaByagAtsa purohitam#} {%возвещённый%} <ls n="KATHĀS.">24,122</ls>. <ls n="KATHĀS.">50,164</ls>. <ls>RĀJA-TAR. 3,116</ls>. <ls n="RĀJA-TAR. 3,">371</ls>. <ls n="RĀJA-TAR.">5,450</ls>. {#rAjYa AvedayaDvaM mAM saMprAptam#} {%возвещает, что%} <ls>R. 1,20,5</ls> (<ls n="R. 1,">21,4 GORR.</ls>). <ls n="R. 1,20,">7</ls>. <ls>R. GORR. 2,3,18</ls>. <ls n="R. GORR. 2,">34,28</ls>. <ls>ŚĀK. 30,4</ls>. <ls>BHAṬṬ. 3,49</ls>. {#yAvadAvedyate rAjYe hataH karRo 'rjunena vE#} <ls>MBH. 8,4992</ls>. {%Jmd%} (<ab>acc.</ab>) {%уведомить%}: {#Avedita#} <ls>RAGH. 5,23</ls>. <ls>RĀJA-TAR. 1,224</ls>.
<div n="1">— 
```

_Dr. Mārcis Gasūns_
