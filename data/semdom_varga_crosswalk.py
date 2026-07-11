"""Build data/semdom_varga_crosswalk.csv — SIL semantic domains <-> Amarakosha vargas (Level A).

Level A deliverable of H742 (semdom <-> kosha crosswalk build), executing the GO
verdict of papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md (H725). The varga -> domain
mapping itself is hand-authored expert judgment (Fable 5, claude-fable-5),
grounded in per-varga synset samples drawn from the AMAR digitization; this
script holds that mapping as data, validates every ID against the two live
sources, joins in GUIDs/names/counts, and emits the CSV deterministically.

Inputs (defaults, override via argv):
  1. semdom.json  — sillsdev/LfMerge data/semantic-domains/semdom.json
                    (1,792 domains; data CC BY-SA 4.0). Fetched to a local
                    cache file if absent.
  2. amar.txt     — sanskrit-lexicon/AMAR amar.txt (24 vargas, 5,590 eid
                    synsets; sibling clone ../../AMAR/amar.txt).

Output: semdom_varga_crosswalk.csv next to this script (ID pairs only — no
prose content from either source; table licence CC BY-SA 4.0).

Usage: python data/semdom_varga_crosswalk.py [path/to/semdom.json] [path/to/amar.txt]
"""

import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
SEMDOM_URL = (
    "https://raw.githubusercontent.com/sillsdev/LfMerge/master/"
    "data/semantic-domains/semdom.json"
)
SEMDOM_CACHE = HERE / "semdom.json"  # gitignored cache, not committed
AMAR_DEFAULT = HERE.parent.parent / "AMAR" / "amar.txt"
OUT_CSV = HERE / "semdom_varga_crosswalk.csv"

# The 24 vargas in amar.txt file order, with canonical kanda.position IDs.
# (id, slp1 name, iast name, kanda number)
VARGAS = [
    ("AK-1.1", "svargavargaH", "svargavargaḥ", 1),
    ("AK-1.2", "vyomavargaH", "vyomavargaḥ", 1),
    ("AK-1.3", "digvargaH", "digvargaḥ", 1),
    ("AK-1.4", "kAlavargaH", "kālavargaḥ", 1),
    ("AK-1.5", "DIvargaH", "dhīvargaḥ", 1),
    ("AK-1.6", "SabdAdivargaH", "śabdādivargaḥ", 1),
    ("AK-1.7", "nAwyavargaH", "nāṭyavargaḥ", 1),
    ("AK-1.8", "pAtAlaBogivargaH", "pātālabhogivargaḥ", 1),
    ("AK-1.9", "narakavargaH", "narakavargaḥ", 1),
    ("AK-1.10", "vArivargaH", "vārivargaḥ", 1),
    ("AK-2.1", "BUmivargaH", "bhūmivargaḥ", 2),
    ("AK-2.2", "puravargaH", "puravargaḥ", 2),
    ("AK-2.3", "SElavargaH", "śailavargaḥ", 2),
    ("AK-2.4", "vanOzaDivargaH", "vanauṣadhivargaḥ", 2),
    ("AK-2.5", "siMhAdivargaH", "siṃhādivargaḥ", 2),
    ("AK-2.6", "manuzyavargaH", "manuṣyavargaḥ", 2),
    ("AK-2.7", "brahmavargaH", "brahmavargaḥ", 2),
    ("AK-2.8", "kzatriyavargaH", "kṣatriyavargaḥ", 2),
    ("AK-2.9", "vESyavargaH", "vaiśyavargaḥ", 2),
    ("AK-2.10", "SUdravargaH", "śūdravargaḥ", 2),
    ("AK-3.1", "viSezyaniGnavargaH", "viśeṣyanighnavargaḥ", 3),
    ("AK-3.2", "saNkIrRavargaH", "saṅkīrṇavargaḥ", 3),
    ("AK-3.3", "nAnArTavargaH", "nānārthavargaḥ", 3),
    ("AK-3.4", "avyayavargaH", "avyayavargaḥ", 3),
]

# Grammatical/structural vargas excluded from the semantic crosswalk (the
# exclusion is itself a reportable finding — see the companion doc).
EXCLUDED = {"AK-3.1", "AK-3.2", "AK-3.3", "AK-3.4"}

# match_type semantics (defined relative to the AK material that motivates the
# pair, not the varga as a whole — vargas are internally heterogeneous):
#   close   — domain scope corresponds closely to a coherent varga section
#   broad   — domain is broader than the motivating AK section (the section
#             fills only part of the domain, often one level-4 child)
#   narrow  — domain covers only a sliver of the motivating AK section
#   related — genuine topical overlap without containment either way
# Evidence lemmas are SLP1, quoted from amar.txt synset heads.
MAPPING = {
    "AK-1.1": [
        ("4.9.1", "close", "deity synonym sets: vizRu, brahman, kArtikeya, aniruddha, indra circle (mAtali, jayanta, pulomajA)"),
        ("4.9.2", "close", "supernatural-being classes: vidyADara, apsaras, rakza, piSAca, BUta, gandharva (hUhU), guhyaka"),
        ("4.9.4", "close", "the eight siddhis: aRiman, laGiman, ISitva ..."),
        ("4.9.6", "broad", "heaven names only (svar, svarga, nAka, tridiva, suraloka); hell is AK-1.9"),
        ("5.5", "close", "agni section: fire names, flame, spark, smoke, forest fire (dAva), submarine fire (Orva)"),
        ("1.1.2", "close", "vAyu section: wind names, gale (JaYJAvAta), whirlwind, the five vital airs (samAna ...)"),
    ],
    "AK-1.2": [
        ("1.1", "close", "sky synonyms: dyo, vihAyas ..."),
    ],
    "AK-1.3": [
        ("8.5.2", "close", "quarters and direction terms: diS, avAcI, pratIcI, udagBava, apadiSam"),
        ("1.1.1", "close", "sun section: sUra, sUrya, Aditya, divAkara, dvAdaSAtman"),
        ("1.1", "close", "other celestial bodies: moon (viDu, himAMSu), planets (Sukra, aNgAraka), nakzatras (puzya, mfgaSIrza), rAhu (svarBAnu), horizon (cakravAla)"),
        ("1.1.3", "close", "weather run: clouds (kAdambinI), thunder (stanita, sPUrjaTu), rain (vfzwi, DArAsampAta), rainbow (indrAyuDa), overcast (durdina), dew/frost (avaSyAya), cold (SIta)"),
        ("4.9.2", "related", "mythic elephants of the quarters (diggaja: puRqarIka, kumuda, supratIka) and their cows (aBramu, piNgalA)"),
    ],
    "AK-1.4": [
        ("8.4", "close", "time core: kAla, day parts (pratyUza, maDyAhna, pradoza), tiTis (amAvAsyA, kuhU), months, seasons (hemanta, vasanta), year (saMvatsara), aeon (kalpa)"),
        ("8.4.1", "close", "named time units and divisions: kalA, muhUrta, yAma, pakza, ftu"),
        ("4.3.1", "related", "philosophical tail: Darma, puRya, sukfta (merit/virtue terms)"),
        ("3.1", "related", "philosophical tail: kzetrajYa (soul), the guRas (rajas, sattva, tamas)"),
        ("1.4", "related", "philosophical tail: creature terms prARin, vyakti"),
    ],
    "AK-1.5": [
        ("3.2", "close", "cognition run: budDi, meDA, saNkalpa, avaDAna, vimarSa, nirRaya, jYAna, BrAnti, vicikitsA"),
        ("2.3", "close", "sense apparatus: DIndriya/karmendriya organ sets, the five vizayas (rUpa, Sabda, ganDa, rasa, sparSa)"),
        ("2.3.3", "close", "the six tastes: maDura, lavaRa, kawu, tikta, amla, tuvara"),
        ("2.3.4", "close", "smell terms: parimala, Amoda, suraBi, pUtiganDi, visra"),
        ("8.3.3", "broad", "colour terms (Sukla, kfzRa, pIta, lohita, SoRa, pAlASa) — semdom files colour under Light"),
        ("4.9.3", "related", "liberation cluster: mukti and synonyms"),
    ],
    "AK-1.6": [
        ("3.5", "close", "speech and utterance as a whole: vAc, vAkya, sound and voice terms"),
        ("3.5.1", "close", "utterance-type inventory: praSna, vivAda, stava, Bartsana, vilApa, saMlApa, apalApa, SApa, pralApa"),
        ("3.5.3", "close", "language-register terms: brAhmI (speech), apaBraMSa (corrupt speech), grAmya (vulgar), mlizwa"),
        ("3.6.3", "close", "the vidyA list (branches of learning): SikzA, trayI, itihAsa, smfti, daRqanIti, vArtA"),
        ("4.9.3", "related", "scripture names: trayI, sAman, Sruti"),
        ("2.3.2", "broad", "noise and sound words: praRAda, uccErGuzwa, marmara, prakvARa, vASita (animal cries)"),
    ],
    "AK-1.7": [
        ("4.2.3", "close", "music core: the seven svaras (zaqja, nizAda, paYcama), instrument classes (tata, Gana), drums (muraja, Anaka, qamaru, JarJara)"),
        ("4.2.4", "close", "dance terms: nartakI, tARqava, lAsya"),
        ("4.2.5", "close", "theatre terms and roles: nAwya vocabulary, gaRikA, stage figures"),
        ("3.4", "close", "the rasa/bhAva inventory: karuRA, BayAnaka, vismaya, garva, asUyA, paScAttApa, unmAda, lAlasA, cintA, kOtUhala, romAYca"),
    ],
    "AK-1.8": [
        ("4.9.6", "broad", "underworld (pAtAla) names: aDoBuvana — semdom heaven/hell is the nearest region slot"),
        ("4.9.2", "related", "nAga kings: Seza, vAsuki"),
        ("1.6.1", "broad", "snake species run: gonasa, ajagara, alagarda, rAjila, sarpa, mAluDAna"),
        ("8.3.3", "broad", "darkness terms (anDakAra, anDatamasa, avatamasa, santamasa) — semdom files dark under Light"),
        ("2.5.3", "broad", "poison run: kzveqa, kAkola, kAlakUwa, halAhala, vatsanABa, dArada — semdom files poison under Injure"),
        ("1.2.1", "related", "cavity/hole terms: kuhara, garta, suzira"),
    ],
    "AK-1.9": [
        ("4.9.6", "broad", "hell names only (avIci, rOrava, mahArOrava, kAlasUtra, tapana) and the VEtaraRI river; heaven is AK-1.1"),
        ("4.4.2", "related", "misery terms: alakzmI, pIqA"),
        ("4.7.7", "related", "torment/forced-labour terms: kAraRA, vizwi"),
    ],
    "AK-1.10": [
        ("1.3", "close", "water core: ap and water synonyms, waves (ullola), shore (pAra, pulina)"),
        ("1.3.1", "close", "bodies of water: samudra, named rivers (kAlindI, kAverI, SoRa, vetravatI), tanks (vApI), lotus ponds (padmAkara), wells"),
        ("7.2.4", "broad", "boat and navigation terms (nO, karRaDAra, Atara, nOkAdaRqa) — semdom files water travel under Travel"),
        ("6.4.5", "close", "fishing gear: net (AnAya), hook (baqiSa), fisher terms"),
        ("1.6.1", "broad", "fish and aquatic-animal run: Sakula, madgura, nalamIna, kUrma, SambUka, yAdas"),
        ("1.5", "related", "water-plant section: padma, kumuda, hallaka, jalanIlI, nAla, bIjakoSa"),
    ],
    "AK-2.1": [
        ("1.2", "close", "earth/world synonyms: BU, jagatI, dyAvApfTivyO"),
        ("1.2.1", "close", "soil and terrain types: mfd, urvarA (fertile), Uza (saline), maru (desert), SarkarA/sikatA (gravel/sand), SAdvala (grassy), naqvat (reedy)"),
        ("4.6.7", "close", "region and country terms: deSa, nIvfd, BArata, maDyadeSa, AryAvarta, prAcya, udIcya"),
        ("6.5.4", "broad", "road run (ayana, GaRwApaTa highway, SfNgAwaka crossroads, atipaTin) and dam (setu) — semdom files roads under Infrastructure"),
        ("6.2.9", "related", "field-quality terms: urvarA, Kila (fallow), nadImAtfka (river-fed), devamAtfka (rain-fed)"),
        ("8.2.8", "broad", "distance measures: gavyUti, nalva"),
    ],
    "AK-2.2": [
        ("6.5.1", "close", "dwelling and mansion types: gfha, veSman, parRaSAlA, maWa, harmya, prAsAda, sODa, maRqapa, upakAryA (tent)"),
        ("6.5.2", "close", "building parts: Bitti (wall), vAtAyana (window), dvAr and pakzadvAra (doors), gopAnasI (rafter), kuwwima (floor), aNgaRa (courtyard), awwa (watchtower)"),
        ("4.6.7", "broad", "city/town words (pur, pura, SAKAnagara) — semdom files settlements under Region"),
        ("6.9.4", "related", "market terms: ApaRa, vipaRi, raTyA (street rows)"),
        ("4.9.8", "related", "shrine terms: cEtya, eqUka"),
    ],
    "AK-2.3": [
        ("1.2.1", "broad", "mountain vocabulary: named ranges (himavat, vinDya, mAlyavat), peak (kUwa), slope (kawaka, snu), cave (darI), plateau (aDityakA), foothill (upatyakA)"),
        ("1.2.2", "broad", "stone and mineral terms: pAzARa, gaRqaSEla (boulder), DAtu (mineral), gErika (red ochre)"),
        ("1.3.1", "related", "mountain springs and streams: utsa, vAripravAha, prapAta (cascade)"),
    ],
    "AK-2.4": [
        ("1.5", "close", "the plant kingdom as a whole: awavI (forest) onward, 379 synsets"),
        ("1.5.1", "close", "tree species runs: plAkza, udumbara, tiniSa, tinduka, nIpa, SirIza, vetasa"),
        ("1.5.3", "close", "herbs, creepers and grasses: apAmArga, kfzRA (pippalI), punarnavA, ajamodA, kuSa, naqa, ketakI"),
        ("1.5.5", "close", "plant-part terms: pallava (shoot), sAra (pith), gucCaka (cluster), ucCrAya (height)"),
        ("1.2.1", "broad", "forest/wilderness terms (awavI) — semdom files forest under Land"),
        ("2.5.7", "related", "many entries are Ayurvedic simples (ozaDi): fkzaganDA, sahasraveDin, SatapuzpA"),
    ],
    "AK-2.5": [
        ("1.6", "close", "the animal kingdom section as a whole"),
        ("1.6.1", "close", "species runs: mammals (siMha, varAha, mfga, eRa, camara), birds (pArAvata, kAka, haMsa, tittiri, cAza), insects (Kadyota, ganDolI)"),
        ("1.6.2", "close", "animal-part terms: garut (wing), SiKaRqa (peacock tail), sPawA (hood in AK-1.8 excepted)"),
        ("1.6.4", "related", "animal behaviour terms: praqIna (flight modes), kekA (peacock cry)"),
        ("1.6.6", "close", "collective terms placed here: samUha, kula, samAja, vfnda"),
    ],
    "AK-2.6": [
        ("2.1", "close", "the human-body run: jaNGA, hasta, GrARa, BrU, roman, kaNkAla, internal parts"),
        ("2.5", "close", "disease inventory: ruj, jvara (fever), visPowa, pAman (scabies), kilAsa; body defects (Karva)"),
        ("2.6", "close", "life-cycle and gender terms: woman typology (nitambinI, prAjYI), pregnancy (ApannasattvA), life stages (SiSutva, varzIyas)"),
        ("4.1.9", "close", "kinship terms: tAta, pitfvya, sapiRqa, BrAtfBaginyO"),
        ("5.3", "close", "garment section: vastra, vasana, aMSuka, cela, rallaka (woolen)"),
        ("5.4", "close", "ornament and grooming: cUqAmaRi, aNgulimudrA (ring), parikarman (toilette), aDivAsana (perfuming), aromatics (lavaNga, kolaka)"),
        ("5.1", "related", "household items in the toilette run: upaDAna (pillow), darpaRa (mirror)"),
    ],
    "AK-2.7": [
        ("4.9.5", "close", "rite and observance core: yajYa, tarpaRa, izwa/tyAga, mOna (silence vow), Opavasta (fasting), varivasyA (worship)"),
        ("4.9.8", "close", "ritual apparatus: vedi (altar), yUpa (post), AhavanIya (fire), caru/paramAnna/sAMnAyya (oblations)"),
        ("4.9.7", "broad", "religious roles: aDvaryu, agnicit, tapasvin, fzi, vedAntin, syAdvAdin, DarmaDvajin (hypocrite)"),
        ("3.6", "related", "teacher-student terms: guru, CAtra"),
        ("2.6.4", "related", "ASrama stage terms: vAnaprasTa"),
    ],
    "AK-2.8": [
        ("4.6", "close", "royal administration: court officials (sOvidalla), counsel, insignia (nfpalakzma), retinue (rakzivarga)"),
        ("4.6.1", "close", "king terms: mUrDABizikta, rAjan, rAjanyaka (royalty collective)"),
        ("4.8", "close", "conflict terms: ripu (enemy), pratApa (might), ahampUrvikA (rivalry)"),
        ("4.8.3", "close", "war machinery: army (bala, camU), weapons (astra, Salya), bowstring (mOrvI), armour (kaYcuka), infantry/cavalry (padAti, aSvAroha), victory (vijaya), march (yAtrA)"),
        ("6.3.1", "broad", "the horse run (aSva, kAmboja breeds, ASvIya) and elephant run (praBinna, kumBa) — semdom files both under Domesticated animal"),
        ("7.2.4", "related", "royal vehicles: SibikA (palanquin), raTANga (chariot parts), anukarza"),
        ("4.7.7", "related", "prison and restraint: kArA"),
    ],
    "AK-2.9": [
        ("6.2", "close", "agriculture core: grains (SUkaDAnya, kalAya, yAvaka, aRu), gleaning (uYCaSila), threshing refuse (kaqaNgara), processing (DAnA roasted grain)"),
        ("6.3", "close", "cattle husbandry: gopa (cowherd), gavyA (herd), trihAyaRI (3-year-old cow), sarvaDurIRa (draft ox), Sakftkari (dung)"),
        ("6.3.3", "close", "dairy: payasya, udaSvit (buttermilk), kzIra products"),
        ("5.2", "close", "food and condiments: yavAgU (gruel), rasAlA, vezavAra (spice mix), SuRWI (ginger), sammfzwa"),
        ("6.9.4", "close", "trade terms: krAyaka (buyer), pratidAna (barter), vipaRi dealings"),
        ("8.2.8", "broad", "weights and measures: tulA (scales), droRa, AQaka"),
        ("1.2.2", "broad", "metals, gems and materials run: tAmraka (copper), mOktika (pearl), maDUcCizwa (beeswax), gavala (buffalo horn)"),
        ("6.7.7", "related", "vessels: aliYjara, kutU (oil jar), druvaya (wooden ware)"),
    ],
    "AK-2.10": [
        ("4.1.2", "close", "caste, mixed-caste and tribe terms: SUdra, ambazWa, mAgaDa, kzattf, caRqAla, kirAta, pulinda"),
        ("6.6", "close", "artisan catalogue: mAlAkAra (garland-maker), tunnavAya (tailor), vyokAra (smith), takzan (carpenter), nirRejaka (washerman), SANKika (conch-worker)"),
        ("6.1.1", "close", "servant run: Bftya, dAsa, dAseya, cewaka"),
        ("6.4", "close", "hunting terms: vyADa (hunter), vEtaMsika (fowler), snares (vAgurA, vItaMsa)"),
        ("6.7", "close", "craft tools: vraScana (chisel), AsPowanI (drill), kaSA (whip), sUtra (thread), Sikya (carrying sling), piwaka (basket)"),
        ("6.3.1", "related", "hunting dogs: alarka, saramA"),
        ("4.2.3", "related", "performer types: mArdaNgika (drummer), veRuDma (flutist), SElAlin (actor)"),
        ("4.7.3", "related", "theft terms: cOrikA"),
    ],
}


def load_semdom(path_or_none):
    if path_or_none:
        p = Path(path_or_none)
    else:
        p = SEMDOM_CACHE
        if not p.exists():
            print(f"fetching semdom.json -> {p}")
            urllib.request.urlretrieve(SEMDOM_URL, p)
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    return {it["key"]: it for it in data["items"]}


def load_vargas(path):
    """Return {slp1 varga name: synset count} from amar.txt, in file order."""
    counts = {}
    order = []
    cur = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.match(r";v\{<s>(.*?)</s>\}", ln.strip())
            if m:
                cur = m.group(1)
                order.append(cur)
                counts[cur] = 0
            elif cur and re.search(r"<eid>\d+", ln):
                counts[cur] += 1
    return order, counts


def main():
    semdom_path = sys.argv[1] if len(sys.argv) > 1 else None
    amar_path = Path(sys.argv[2]) if len(sys.argv) > 2 else AMAR_DEFAULT

    domains = load_semdom(semdom_path)
    order, counts = load_vargas(amar_path)

    # Validate sources against the pinned inventory.
    assert len(order) == 24, f"expected 24 vargas in amar.txt, got {len(order)}"
    assert [v[1] for v in VARGAS] == order, "varga order mismatch vs amar.txt"
    total = sum(counts.values())
    assert total == 5590, f"expected 5590 synsets, got {total}"

    rows = []
    for vid, slp1, iast, kanda in VARGAS:
        if vid in EXCLUDED:
            continue
        pairs = MAPPING[vid]
        codes = [c for c, _, _ in pairs]
        assert len(set(codes)) == len(codes), f"duplicate semdom code in {vid}"
        for code, match, evidence in sorted(pairs):
            d = domains.get(code)
            assert d is not None, f"unknown semdom code {code} in {vid}"
            level = code.count(".") + 1
            assert level <= 3, f"{code} exceeds the level-2/3 policy ({vid})"
            rows.append(
                {
                    "ak_varga_id": vid,
                    "varga_slp1": slp1,
                    "varga_iast": iast,
                    "kanda": kanda,
                    "varga_synsets": counts[slp1],
                    "semdom_code": code,
                    "semdom_guid": d["guid"],
                    "semdom_name": d["value"],
                    "match_type": match,
                    "evidence": evidence,
                }
            )

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Summary for the companion doc.
    mapped_vargas = sorted({r["ak_varga_id"] for r in rows})
    dom_codes = sorted({r["semdom_code"] for r in rows})
    by_match = {}
    for r in rows:
        by_match[r["match_type"]] = by_match.get(r["match_type"], 0) + 1
    by_top = {}
    for c in dom_codes:
        by_top[c.split(".")[0]] = by_top.get(c.split(".")[0], 0) + 1
    print(f"wrote {OUT_CSV.name}: {len(rows)} pairs, "
          f"{len(mapped_vargas)} thematic vargas, {len(dom_codes)} distinct domains")
    print("pairs by match_type:", dict(sorted(by_match.items())))
    print("distinct domains per semdom top-level:", dict(sorted(by_top.items())))


if __name__ == "__main__":
    main()
