# Alexey Vigasin corpus — index

_Created: 22-07-2026 · Last updated: 22-07-2026_

This folder holds full-text `.mdx` conversions of A.A. Vigasin's *Изучение Индии в России
(очерки и материалы)* — 26 Word files split across two distinct works, converted via
LibreOffice `.doc`→`.docx` headless then Pandoc `.docx`→`.mdx`
([`/docx-to-md`](https://github.com/gasyoun/claude-config/blob/main/commands/docx-to-md.md)).
The raw `.doc`/`.docx`/PDF sources stay local-only under `literature/Alexey_Vigasin/`
(gitignored per `literature/*` — see the top-level `literature/md/README.md` convention);
this directory is the tracked, published home for the full-text conversions themselves.
**Published as full text, risk accepted by the repo owner 22-07-2026** — no prior rights
review existed for this specific corpus (unlike the nine foreign works reviewed 15/21-07-2026
noted in `literature/md/README.md`); this is a fresh, explicit per-corpus ruling, not an
extension of that one. This index is the routing map for H1443
(`Uprava/handoffs/H1443-Sonnet_IndologyScholars_vigasin-corpus-extract-route_22.07.26.md`).

## Work A — *Изучение Индии в России* (history of Russian Indology)

Biographies + archival primary documents. Landed into
[IndologyScholars](https://github.com/gasyoun/IndologyScholars) — see
`sources/vigasin/README.md` there for the per-scholar routing and registry-coverage notes.

| File | Landed at (IndologyScholars) |
|---|---|
| `Введение.mdx`, `Оглавление к истории индологии.mdx`, `Список иллюстраций для индологии.mdx`, `Список использованных архивов.mdx` | `sources/vigasin/front-matter/` |
| `I. образ в древней руси.mdx` | `sources/vigasin/chapters/` |
| `III. ИЗУЧЕНИЕ ИНДИЙСКОЙ КУЛЬТУРЫ В РОССИИ.mdx` | `sources/vigasin/chapters/` |
| `IV. Дело о санскритском словаре.mdx` | `sources/vigasin/chapters/` (**also here**, see below) |
| `V. Иван минаев.mdx`, `VI. Поездка Минаева.mdx`, `пр. 6. записка минаева.mdx` | `sources/vigasin/scholars/minaev-ivan/` |
| `VII. Университетская санскритология.mdx` | `sources/vigasin/chapters/` |
| `VIII.Сергей ольденбург.mdx`, `пр. 7. Личное дело С.Ольденбурга.mdx` | `sources/vigasin/scholars/oldenburg-sergei/` |
| `XI. Письма Розенберга.mdx` | `sources/vigasin/scholars/_unregistered/rosenberg/` |
| `XII. миронов и сталь-гольштейн.mdx` | `sources/vigasin/scholars/_unregistered/mironov/` + `sources/vigasin/scholars/stal-fon-golshtein-aleksandr/` |
| `XIII Александр и Людмила Мерварт.mdx` | `sources/vigasin/scholars/mervart-aleksandr/` + `sources/vigasin/scholars/_unregistered/mervart-lyudmila/` |
| `пр. 8 Автобиография щербатского.mdx` | `sources/vigasin/scholars/shcherbatskoi-fedor/` |
| `пр.1 паллас.mdx` | `sources/vigasin/scholars/_unregistered/pallas/` |
| `пр. 2. дворянин ...сунгара.mdx`, `пр. 3.Реестр Московского Главного Архива.mdx`, `пр.4. Об одной журнальной публикации середины XIX века.mdx`, `пр. 5.Бенгальский Литератор.mdx`, `пр.9. об одном браке.mdx` | `sources/vigasin/archival/` |

### Chapter IV — the Böhtlingk/Petersburg dictionary affair

`IV. Дело о санскритском словаре.mdx` is Vigasin's essay on the "Дело об издании академиком
Бетлингком Санскритского лексикона" — directly relevant to this repo's own PW/PWG dictionary
history. **The handoff routed this to "SanskritLexicography §8.11"; no such numbered section
exists anywhere in this repo** (verified by grep across every `.md` file for `8.11` and for a
`## 8.` / `### 8.11` heading pattern — the only `## 8.` heading in the repo is
[`MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md`](../../../MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md)'s flat,
non-decimal "8. Сколько сессий на аккаунт", an unrelated ops-manual section). No file in this
repo previously cited Vigasin at all. Rather than force a citation into a nonexistent numbering
scheme, the essay is landed here as a primary source (`IV. Дело о санскритском словаре.mdx`,
also mirrored to IndologyScholars per the table above); a future dictionary-history chapter
that wants a real `§8.11` should cite this file directly. Flag this numbering assumption as
false when closing H1443.

## Work B — *Работы разных лет* / *Этюды* (reference-only)

Vigasin's own Indological research (Arthaśāstra, Dharmaśāstra, царь/бог, Ṛgveda) — **not**
biography, **not ingested as data** this pass.

| File | Status |
|---|---|
| `все.mdx` (*Работы разных лет*) | Converted, parked here as bibliographic reference only. Per-topic fragments may later cite into [CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) (dharmaśāstra) — not this pass. |
| `Этюды о людях науки.mdx` (biographical, overlaps Work A) | Converted; also landed into IndologyScholars `sources/vigasin/work-b/` (biographical overlap). |
| `Предисловие к Этюдам.mdx` | Converted; also landed into IndologyScholars `sources/vigasin/work-b/`. |

## Source

`Вигасин А.А. Изучение Индии в России (очерки и материалы).pdf` (19 MB) stays as-is per H1443 —
not converted, not split.

---

_Dr. Mārcis Gasūns_
