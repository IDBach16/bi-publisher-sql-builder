# Item Tables — Re-Verification against Oracle Fusion SCM **Release 26B**

**Date:** 2026-06-01
**Scope:** All Item Master / Inventory tables & views in `schema_items_inventory.py`, plus the item tables that were *referenced but never defined*.
**Source of truth:** Oracle's official *Tables and Views for SCM*, **Release 26B** (doc **G51993-01**, ©2026) — `https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/`
**Method:** 5 parallel agents, one group of tables each. For every table: web-search the `oedsc` page, fetch it, and re-check the specific claim from `SCHEMA_AUDIT_2026-05-29.md` against 26B.

---

## ⚠️ Methodology caveat (read first)
The **26B doc set is confirmed live** — a few item pages resolve directly to 26B (`egpsystemitemsb-4735`, `egpcategoriestl-29311`, `egoitemrevisionefftl-20755`). **But** Oracle's per-table numeric page IDs change every release and the 26B IDs are **not yet web-search-indexed** for most tables. When a 26B deep-link couldn't be found, the agent verified column-level facts on the **nearest published release (25C / 25D / 26A)** and noted it. Oracle core item structures are stable across 25B–26B, so these are reliable — but rows marked with an older release were not read off a literal 26B page.

---

## 🔴 Biggest correction — the prior audit was WRONG here

### `EGP_SYSTEM_ITEMS_B` — TP columns **DO** exist on the table
The 2026-05-29 audit said `TRADING_PARTNER_ID`, `TP_TYPE`, `TP_ITEM_NUMBER` are **not** on this table (and that you must go to `EGP_TRADING_PARTNER_ITEMS`). **The live 26B page disproves this:** all three are real columns on `EGP_SYSTEM_ITEMS_B`, and together they form part of unique index **`EGP_SYSTEM_ITEMS_B_U3`** = `(ORGANIZATION_ID, ITEM_NUMBER, TRADING_PARTNER_ID, TP_TYPE, TP_ITEM_NUMBER)`. `TP_TYPE` values: CUSTOMER / MANUFACTURER / COMPETITOR / SUPPLIER.
- **Source:** [26b/egpsystemitemsb-4735.html](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/egpsystemitemsb-4735.html)
- **Impact:** SQL that reads TP columns directly off the item base table is **valid**. The earlier "ORA-00904" warning for those columns was a false alarm.

---

## Full results

### Item Master core
| Table | In 26B? (release verified) | Primary Key | Verdict vs prior audit |
|---|---|---|---|
| `EGP_SYSTEM_ITEMS_B` | ✅ **26B** | INVENTORY_ITEM_ID, ORGANIZATION_ID | **CORRECTED** — TP columns present (index U3). |
| `EGP_SYSTEM_ITEMS_TL` | ✅ 25D (in 26B index) | INVENTORY_ITEM_ID, ORGANIZATION_ID, LANGUAGE | CONFIRMED |
| `EGP_SYSTEM_ITEMS` (view) | ✅ 25C | view on `EGP_SYSTEM_ITEMS_VL` | CONFIRMED |
| `EGP_SYSTEM_ITEMS_B_V` (view) | ✅ 25C | — | CONFIRMED |
| `EGP_SYSTEM_ITEMS_TL_ALL_V` (view) | ✅ 25C | — | CONFIRMED |
| `EGP_SYSTEM_ITEMS_VL` (view) | ✅ 25D | — | CONFIRMED — real view (was only *referenced* before) |
| `EGP_SYSTEM_ITEMS_INTERFACE` | ✅ exists (26B index; deep-link bounced) | n/a (not extracted) | CONFIRMED existence |
| `EGP_TRADING_PARTNER_ITEMS` | ✅ exists (deep-link bounced) | n/a (not extracted) | CONFIRMED existence — but **not** the sole home of TP columns |

### Categories & Catalogs
| Table | In 26B? (release verified) | Primary Key | Verdict vs prior audit |
|---|---|---|---|
| `EGP_CATEGORIES_B` | ✅ 25D | CATEGORY_ID | CONFIRMED — `CATEGORY_CODE` VARCHAR2(**820**), `ATTRIBUTE1`(**150**), `SUMMARY_FLAG` **NOT NULL** |
| `EGP_CATEGORIES_TL` | ✅ **26B** | CATEGORY_ID, LANGUAGE | CONFIRMED |
| `EGP_CATEGORIES_VL` (view) | ✅ 25D | logical CATEGORY_ID | CONFIRMED — real view |
| `EGP_CATEGORY_SETS_B` | ✅ 25C | CATEGORY_SET_ID | CONFIRMED |
| `EGP_CATEGORY_SETS_VL` (view) | ✅ (view family; 26B id stale) | logical CATEGORY_SET_ID | CONFIRMED |
| `EGP_ITEM_CAT_ASSIGNMENTS` | ✅ 25C | INVENTORY_ITEM_ID, ORGANIZATION_ID, **CATEGORY_SET_ID, CATEGORY_ID** | CONFIRMED — note PK order (SET before CATEGORY) |
| `EGP_ITEM_CAT_ASSIGNMENTS_PUB_V` (view) | ⚠️ 24c page only | — | EXISTS historically; 26B page unconfirmed |
| `EGP_CATEGORY_SET_VALID_CATS` | ✅ 22b/22c | (not re-extractable) | CONFIRMED documented; 26B id not surfaced |
| `EGP_DEFAULT_CATEGORY_SETS` | ❌ no standalone page (18b–26B) | n/a | **NOT DOCUMENTED** — keep "treat as OK" |
| `EGP_FULL_CATEGORY_LIST` | ✅ 25D | CATEGORY_SET_ID, CATEGORY_ID, **LOAD_ID** | **CORRECTED** — it's a **TABLE**, not a view |
| `EGP_FLATTENED_VALID_CATS_VL` (view) | ✅ 24b | — | CONFIRMED view |
| `EGP_ITEM_CATEGORIES` | ✅ 25D | logical (ITEM, ORG, CAT_SET, CAT) | **CORRECTED** — it's a **VIEW**, not a table |
| `EGP_CATG_MAP_HDRS_B` | ⚠️ only `_VL` view documented | (base `CATG_MAP_HDR_ID`) | **CORRECTED** — no standalone `_B` page; published as `EGP_CATG_MAP_HDRS_VL` |

### Revisions & Extensible Flexfields (EFF)
| Table | In 26B? (release verified) | Primary Key | Verdict vs prior audit |
|---|---|---|---|
| `EGP_ITEM_REVISIONS_B` | ✅ 25C | REVISION_ID | CONFIRMED — `ATTRIBUTE1`(**150**), `ALT_REVISION_CODE`(**40**) |
| `EGP_ITEM_REVISIONS_TL` | ✅ 25C | REVISION_ID, LANGUAGE | CONFIRMED |
| `EGP_ITEM_REVISIONS_V` (view) | ✅ 25D | — | **size NOT verifiable from view page** — inherited from `_B`(40), not published on the view |
| `EGP_ITEM_REVISIONS_B_V` (view) | ✅ 24D | — | CONFIRMED exists |
| `EGO_ITEM_EFF_B` | ✅ 25D | EFF_LINE_ID | CONFIRMED — `ACD_TYPE` VARCHAR2(30) NOT NULL present |
| `EGO_ITEM_EFF_TL` | ✅ **26A** | EFF_LINE_ID, LANGUAGE, +audit | CONFIRMED exists |
| `EGO_ITEM_REVISION_EFF_B` | ✅ 25D | EFF_LINE_ID, +audit | CONFIRMED (sibling `_TL` is a real 26B page) |
| `EGO_VERSIONS_B` | ✅ 25D | VERSION_ID | CONFIRMED exists (item version control) |
| `EGP_ITEM_TEXT_TL` | ✅ 25C | ITEM_ID, ORG_ID, LANGUAGE | CONFIRMED exists (item long-text index) |

### Relationships / Classes / Associations / MFG / BOM / Org
| Table | In 26B? (release verified) | Primary Key | Verdict vs prior audit |
|---|---|---|---|
| `EGP_ITEM_RELATIONSHIPS_B` | ✅ 25C | ITEM_RELATIONSHIP_ID | CONFIRMED — `ITEM_RELATIONSHIP_TYPE` (not `RELATIONSHIP_TYPE_ID`); `START/END_DATE_ACTIVE` |
| `EGP_ITEM_RELATIONSHIPS_TL` | ✅ 25D | ITEM_RELATIONSHIP_ID, LANGUAGE | CONFIRMED |
| `EGP_ITEM_CLASSES_B` | ✅ 25D | ITEM_CLASS_ID | CONFIRMED — `PARENT_ITEM_CLASS_ID`; old catalog-group cols & `INTERNAL_NAME` absent |
| `EGP_ITEM_CLASSES_TL` | ✅ 24B | ITEM_CLASS_ID, LANGUAGE | CONFIRMED |
| `EGO_ITEM_ASSOCIATIONS` | ✅ 25C | **7-col composite** (INVENTORY_ITEM_ID, ORGANIZATION_ID, ACD_TYPE, CHANGE_LINE_ID, VERSION_ID, SUPPLIER_ID, SUPPLIER_SITE_ID) | **CORRECTED** — `ITEM_ASSOCIATION_ID` doesn't exist; `ASSOCIATION_ID` is non-key. Supplier cols & `VERSION_START/END_DATE` confirmed |
| `EGP_ITEM_ORG_ASSOCIATIONS` | ✅ 25D | ORGANIZATION_ID, INVENTORY_ITEM_ID | CONFIRMED — `MASTER_ORGANIZATION_ID` absent; use `INVENTORY_ORGANIZATION_ID`/`ITEM_DEFINITION_ORG_ID` |
| `EGP_MFG_PART_NUMBERS` (view) | ⚠️ JS-rendered page | not extractable | **NOT verifiable via this method** |
| `EGP_MFG_PART_NUMBERS_B` / `_B_V` | ⚠️ `_B_V` view exists; page not parseable | not extractable | PARTIAL — existence ok; `MFG_PART_NUM_ID→ITEM_RELATIONSHIP_ID` claim **unverified** |
| `EGP_STRUCTURES_B` (BOM) | ✅ 25C | **BILL_SEQUENCE_ID** | CONFIRMED cols (`COMMON_ORGANIZATION_ID`, `COMMON_ASSEMBLY_ITEM_ID`, `PK1_VALUE`=item, `ALTERNATE_BOM_DESIGNATOR`(80)) — but PK is `BILL_SEQUENCE_ID`, **not** PK1_VALUE |
| `EGP_COMPONENTS_B` (BOM) | ✅ 25D | **COMPONENT_SEQUENCE_ID** | CONFIRMED — `COMPONENT_ITEM_ID` absent; component item in `PK1_VALUE` |
| `INV_ORG_PARAMETERS_V` (view) | ✅ **26A** | — | CONFIRMED |
| `INV_ORGANIZATION_DEFINITIONS_V` (view) | ✅ 25C | — | CONFIRMED — `OPERATING_UNIT` absent; use `BUSINESS_UNIT_ID`/`BUSINESS_UNIT_NAME` |

---

## Corrections to apply to `SCHEMA_AUDIT_2026-05-29.md` / schema
1. **`EGP_SYSTEM_ITEMS_B`** — remove the "TP columns not on table" finding. They exist (index U3). ⬅ highest priority.
2. **`EGO_ITEM_ASSOCIATIONS`** — fix the PK: it is the 7-column composite, **not** `ASSOCIATION_ID`; `ITEM_ASSOCIATION_ID` does not exist.
3. **`EGP_FULL_CATEGORY_LIST`** — reclassify as a **TABLE** with PK `(CATEGORY_SET_ID, CATEGORY_ID, LOAD_ID)`.
4. **`EGP_ITEM_CATEGORIES`** — model as a **VIEW** (no PK), not a base table.
5. **`EGP_CATG_MAP_HDRS_B`** — point at the documented **`EGP_CATG_MAP_HDRS_VL`** view.
6. **`EGP_STRUCTURES_B` / `EGP_COMPONENTS_B`** — PKs are `BILL_SEQUENCE_ID` / `COMPONENT_SEQUENCE_ID` (PK1_VALUE/PK2_VALUE are generic object-key columns).

## Confirmed unchanged from prior audit (claims held up against 26B)
`EGP_CATEGORIES_B` sizes • `EGP_ITEM_REVISIONS_B` sizes • `EGP_ITEM_RELATIONSHIPS_B` renames • `EGP_ITEM_CLASSES_B` PK rename • `EGP_ITEM_ORG_ASSOCIATIONS` (`MASTER_ORGANIZATION_ID` absent) • `INV_ORGANIZATION_DEFINITIONS_V` (`OPERATING_UNIT` absent).

## Still open (verify against a live pod or Oracle's 26B A–Z index)
- `EGP_MFG_PART_NUMBERS` / `_B` / `_B_V` — JS-rendered doc pages; columns/PK not machine-readable.
- `EGP_DEFAULT_CATEGORY_SETS` — no standalone `oedsc` page in any release.
- Exact 26B PKs for `EGP_TRADING_PARTNER_ITEMS`, `EGP_SYSTEM_ITEMS_INTERFACE`, `EGP_ITEM_CAT_ASSIGNMENTS_PUB_V`, `EGP_CATEGORY_SET_VALID_CATS` (existence confirmed; deep-links bounced).
</content>
</invoke>
