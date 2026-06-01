# Oracle Fusion Schema Audit — BI_Publisher_App

**Date:** 2026-05-29
**Scope:** All 77 table/view definitions across `schema.py`, `schema_items_inventory.py`, `schema_om_ship_fin.py`, `schema_suppliers.py`, `schema_workflow.py`
**Method:** One research agent per table compared the app's declared columns against Oracle's current *Tables and Views for Oracle Fusion Cloud* documentation (releases 25B–26B). 76/77 returned verdicts; `EGP_MFG_PART_NUMBERS` (the 4-column view) timed out and was not verified.

> **⚠️ UPDATE 2026-06-01 — the Item tables were re-verified against Release 26B.** See **`SCHEMA_AUDIT_ITEMS_26B_2026-06-01.md`**. That pass **overturned** several findings below for the Items module:
> - **`EGP_SYSTEM_ITEMS_B`** — the claim that `TRADING_PARTNER_ID`/`TP_TYPE`/`TP_ITEM_NUMBER` are *not* on the table is **WRONG**; they exist (index `U3`). Disregard the corresponding ORA-00904 warning.
> - **`EGO_ITEM_ASSOCIATIONS`** — PK is a 7-column composite, **not** `ASSOCIATION_ID`; `ITEM_ASSOCIATION_ID` does not exist.
> - **`EGP_FULL_CATEGORY_LIST`** is a TABLE (PK incl. `LOAD_ID`); **`EGP_ITEM_CATEGORIES`** is a VIEW; **`EGP_CATG_MAP_HDRS_B`** is published only as the `_VL` view.
> Item findings that **held up** in 26B: `EGP_CATEGORIES_B`/`EGP_ITEM_REVISIONS_B` sizes, `EGP_ITEM_RELATIONSHIPS_B` renames, `EGP_ITEM_CLASSES_B` PK rename, `EGP_ITEM_ORG_ASSOCIATIONS` and `INV_ORGANIZATION_DEFINITIONS_V` missing columns.

---

## How to read this

Your schema files deliberately list only a **subset** of each table's columns, so "columns Oracle documents that we don't list" are **not** problems — they're omitted below except where useful. The findings that matter are:

- **Table not found / renamed** — the object name itself doesn't exist in current Oracle docs.
- **Missing column** — a column *we declare and rely on* is absent from current Oracle docs (renamed, removed, or moved to another table/view). These cause `ORA-00904: invalid identifier` at runtime.
- **Type/size change** — column exists but the data type/length differs. Harmless for `SELECT`; matters only for inserts/binds/DDL.

### ⚠️ The single biggest theme: base table vs. view

Many "missing column" findings are because the app declares a **base table** (`_B`, `_ALL_M`) but the columns it lists actually live on the corresponding **view** (`_V`, `_VL`). BI Publisher SQL should generally query the **views**. For several tables below, the fix is simply *"point at the `_V`/`_VL` view, not the base table."*

---

## Scoreboard

| Status | Count | Meaning |
|---|---:|---|
| ✅ Unchanged | 29 | All declared columns verified present with compatible types |
| 🟡 Type/size only | 3 | Columns exist; only width/precision differs (non-breaking for SELECT) |
| 🟠 Missing/renamed columns | 33 | At least one relied-upon column is absent/renamed → SQL will fail |
| 🔴 Table not found | 6 | Object name absent from current Oracle docs |
| ❓ Undocumented (SOA-internal) | 5 | Not in Oracle's published EDM, but may exist on-pod (see notes) |
| ⏳ Not verified | 1 | `EGP_MFG_PART_NUMBERS` timed out |

---

## 🔴 Tier 1 — Table name not found in current Oracle docs

These names don't appear in Oracle's published *Tables and Views* guides at all. Some are genuinely renamed/replaced; some may be SOA-internal or custom. **Verify each against a live pod before trusting generated SQL.**

| Table (file) | What Oracle docs show instead |
|---|---|
| **POZ_SUP_THIRD_PARTY_REL** (`schema_suppliers.py`) | Renamed to **`POZ_SUP_THIRDPARTY_PAYMENT_REL`**. PK `THIRD_PARTY_REL_ID`→`TPP_RELATIONSHIP_ID`; `THIRD_PARTY_VENDOR_ID`→`REMIT_TO_SUPPLIER_ID`; `THIRD_PARTY_VENDOR_SITE_ID`→`REMIT_TO_ADDRESS_ID`; `START_DATE`/`END_DATE`→`FROM_DATE`/`TO_DATE`; `VENDOR_ID` removed. Heavily restructured. |
| **POZ_BUS_CLASS_REFERENCES** (`schema_suppliers.py`) | Replaced by **`POZ_CERTIFYING_AGENCIES`** (PK `AGENCY_ID`, `NAME` not `AGENCY_NAME`, `END_DATE` not `STATUS`). All 7 declared columns differ. |
| **POZ_SUPP_PROD_SERV_CAT** (`schema_suppliers.py`) | Only documented object is the view **`POZ_PROD_SERV_CATEGORY_V`** (3 cols). None of the 6 declared columns match. |
| **POZ_QUAL_REC_OWNERSHIPS** (`schema_suppliers.py`) | No `POZ_QUAL*` table exists; qualification data is under the **`POQ_`** prefix (`POQ_QUALIFICATIONS`, etc.). Possibly custom/undocumented. |
| **POZ_SUPPLIER_NOTES** (`schema_suppliers.py`) | Not in any 25D Procurement TOC. Likely custom/non-standard — not an Oracle-shipped object. |
| **POZ_SUPPLIER_ATTACHMENTS** (`schema_suppliers.py`) | Not documented in any release 25B–26B. Oracle stores supplier attachments in the generic **`FND_ATTACHED_DOCUMENTS`/`FND_DOCUMENTS`** framework; only `POZ_SUP_ATTACHMENTS_INT` (import staging) exists. Likely custom/fabricated. |
| **HWF_TASKS_B** (`schema_workflow.py`) | Not in EDM. Documented equivalent is **`FND_BPM_TASK_B`** / `FND_BPM_TASK_VL` with very different columns (`STATE`→`STATUS_CODE`, `OUTCOME`→`OUTCOME_CODE`, `TASK_ID` is `VARCHAR2(64)` not `NUMBER`). |

---

## ❓ Tier 1b — Undocumented SOA-infrastructure tables (likely real on-pod)

These live in the **`FA_FUSION_SOAINFRA`** schema (BPM/workflow dehydration store). Oracle does **not** publish them in the EDM guides, so the audit couldn't verify columns — but they are real objects that practitioners query against live Fusion pods. Treat with caution and verify column names directly via SQL.

- **WFASSIGNEE** — base SOA DDL has only `TASKID, VERSION, ASSIGNEE, GUID, ISGROUP`. Columns we add (`ASSIGNEETYPE, DISPLAYNAME, ROLENAME, STATE, ACQUIREDBY, ISADHOC`) are Fusion runtime extensions used in practice but undocumented.
- **WFATTACHMENT** — SOA DDL composite PK `(taskId, version, name, updatedBy)`; our `ATTACHMENTID`, `MIMETYPE`, `CREATEDBY`/`CREATEDDATE` may not match the real DDL.
- **HWF_TASK_ASSIGNMENTS_B**, **HWF_TASK_HISTORY** — internal `HWF_` tables; Oracle's documented equivalents are the `FND_BPM_TASK*_VL` views.

> **Recommendation for the whole Workflow module:** Oracle's *documented, supported* path for workflow/approval reporting is the **`FND_BPM_TASK_VL` / `FND_BPM_TASK_HISTORY_VL`** views, not the raw `WF*`/`HWF*` SOA tables. Consider migrating `schema_workflow.py` to those views.

---

## 🟠 Tier 2 — Valid tables with missing/renamed columns (SQL will break)

These tables exist, but specific columns we declare are gone/renamed. **Each will throw `ORA-00904` if used in generated SQL.**

### Procurement / Suppliers
| Table | Broken columns → fix |
|---|---|
| **POZ_SUPPLIERS** (26B ✓) | These 7 are **not on the supplier header** in 26B — they live at site level / in TCA: `TERMS_ID`, `PAYMENT_CURRENCY_CODE`, `INVOICE_CURRENCY_CODE`, `TAXPAYER_ID` (→`VAT_REGISTRATION_NUM`/`TAXPAYER_COUNTRY`), `SUPPLIER_NOTIF_METHOD`, `EMAIL_ADDRESS` (→ TCA via `PARTY_ID`), `STATUS` (→`POZ_SUPPLIER_REGISTRATIONS`). The other 19 cols are fine. |
| **POZ_SUPPLIER_CONTACTS** (26B ✓) | Base table is lean — **14 declared columns aren't on it**. Most (`FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, JOB_TITLE, STATUS`…) exist only on the view **`POZ_SUPPLIER_CONTACTS_V`**. And `PHONE_NUMBER`→`PHONE`, `FAX_NUMBER`→`FAX`, `MOBILE_NUMBER`→`MOBILE`; `VENDOR_ID`, `REL_PARTY_ID`, `CONTACT_TYPE` aren't even on the view. **Fix: query the `_V` view + correct names.** |
| **POZ_SUPPLIER_SITES_ALL_M** | `INVOICE_MATCH_OPTION`→`MATCH_OPTION`; `PROCUREMENT_BU_ID`→`PRC_BU_ID` (only); `SUPPLIER_ADDRESS_ID`→`PARTY_SITE_ID`; `PAYMENT_METHOD_CODE`→`PAYMENT_METHOD_LOOKUP_CODE`; `BILL_TO_LOCATION_ID`, `SHIP_TO_LOCATION_ID` not found. |
| **POZ_SUPPLIER_ADDRESSES** | Documented object is the view **`POZ_SUPPLIER_ADDRESS_V`**, keyed by `PARTY_SITE_ID` (not `SUPPLIER_ADDRESS_ID`). `ADDRESS_NAME`→`PARTY_SITE_NAME`; purpose flags renamed (`..._ORDERING_FLAG`→`ADDRESS_PURPOSE_ORDERING`, `..._PAY_FLAG`→`ADDRESS_PURPOSE_REMIT_TO`, `..._RFQ_FLAG`→`ADDRESS_PURPOSE_RFQ_OR_BIDDING`); no billing-purpose column. |
| **POZ_BUSINESS_CLASSIFICATIONS** | PK `BUS_CLASSIFICATION_ID`→`CLASSIFICATION_ID`; `CLASSIFICATION_CODE`→`LOOKUP_CODE`; `CLASSIFICATION_NAME`, `SUB_CLASSIFICATION_CODE`, `MINORITY_TYPE_LOOKUP_CODE` (→`EXT_ATTR_1`) absent. `STATUS`/`START_DATE_ACTIVE` flagged **obsolete** (→`CLASS_STATUS`/`START_DATE`). |
| **POZ_PRODUCTS_AND_SERVICES** | Table is named **`POZ_SUP_PRODUCTS_SERVICES`**; PK `PROD_SERV_ID`→`CLASSIFICATION_ID`; `CATEGORY_TYPE`, `START_DATE_ACTIVE`, `END_DATE_ACTIVE` absent; `STATUS` is `VARCHAR2(30)` not `(1)`. |
| **POZ_SUPPLIER_TAX_PROFILES** | Real table is **`ZX_PARTY_TAX_PROFILE`** (ZX/Tax schema). `REPORTING_AUTHORITY_ID`→`REPORTING_AUTHORITY_FLAG` (Y/N). Other 10 cols match. |
| **POZ_SUPPLIERS_INT** | `REJECT_REASON` absent; `STATUS` is `VARCHAR2(20)` not `(30)`. |

### Financials (Payables / Payments / Cash)
| Table | Broken columns → fix |
|---|---|
| **CE_BANK_ACCOUNTS** | `BANK_NAME`, `BRANCH_NAME`, `COUNTRY_CODE`, `CASH_ACCOUNT_CCID` not on the table (on related party entities). `BRANCH_ID`→`BANK_BRANCH_ID`; `ACCOUNT_TYPE`→`BANK_ACCOUNT_TYPE`. |
| **AP_HOLDS_ALL** | `HOLD_TYPE`, `RELEASED_BY`, `RELEASED_DATE` absent (EBS-era). ⚠️ `HELD_BY` changed **`NUMBER`→`VARCHAR2(64)`** (username, not ID); `HOLD_DATE` `DATE`→`TIMESTAMP`. |
| **AP_CHECKS_ALL** | `SET_OF_BOOKS_ID` absent (legacy EBS; use `LEGAL_ENTITY_ID`/`ORG_ID`). Plus width changes on `CITY/COUNTRY/ZIP/PAYMENT_TYPE_FLAG`. |
| **AP_INVOICE_DISTRIBUTIONS_ALL** | `ACCRUAL_POSTED_FLAG`, `CASH_POSTED_FLAG` absent (those live on payment-side tables). 32 other cols fine. |
| **AP_INVOICE_PAYMENTS_ALL** | `ACCRUAL_POSTED_FLAG`, `CASH_POSTED_FLAG` absent (EBS-era). |
| **AP_PAYMENT_SCHEDULES_ALL** | `FUTURE_PAY_DUE_DATE` absent; `IBY_HOLD_REASON` `(25)`→`(2000)`, `PAYMENT_STATUS_FLAG` `(1)`→`(25)`. |
| **AP_PREPAY_HISTORY_ALL** | `PREPAY_LINE_NUMBER`→`PREPAY_LINE_NUM`; `PREPAY_AMOUNT_APPLIED`, `PREPAY_AMOUNT_REMAINING` don't exist on this history table. |
| **AP_TERMS_B** | `DISCOUNT_CUTOFF_DAY` absent (only `DUE_CUTOFF_DAY`); `TYPE` `(25)`→`(15)`. |
| **IBY_PAYMENTS_ALL** | `PAYMENT_DOCUMENT_ID` absent here — it belongs to `IBY_PAY_INSTRUCTIONS_ALL` (mis-assigned table). |
| **IBY_PAYMENT_METHODS_B** | `PAYMENT_METHOD_NAME` is on `_TL` (use view `IBY_PAYMENT_METHODS_VL`); `ENABLED_FLAG` doesn't exist (use `INACTIVE_DATE`/`START_DATE`/`END_DATE`). |
| **IBY_PAY_INSTRUCTIONS_ALL** | `PAYMENT_AMOUNT`, `PAYMENT_METHOD_CODE` not on this batch-level table. |

### HCM / Inventory
| Table | Broken columns → fix |
|---|---|
| **PER_USERS** | `EMAIL_ADDRESS` not on `PER_USERS` — join **`PER_EMAIL_ADDRESSES`** on `PERSON_ID`. |
| **INV_ORGANIZATION_DEFINITIONS_V** | `OPERATING_UNIT` absent — Fusion uses `BUSINESS_UNIT_ID`/`BUSINESS_UNIT_NAME`. |

### Product Management (Items / BOM)
| Table | Broken columns → fix |
|---|---|
| **EGO_ITEM_ASSOCIATIONS** | PK `ITEM_ASSOCIATION_ID`→`ASSOCIATION_ID`; `TRADING_PARTNER_ID`/`TP_TYPE`/`TP_ITEM_NUMBER`→`SUPPLIER_ID`/`SUPPLIER_SITE_ID`; `START_DATE`/`END_DATE`→`VERSION_START_DATE`/`VERSION_END_DATE`. 6 of 8 cols changed. |
| **EGP_ITEM_CLASSES_B** | PK `ITEM_CATALOG_GROUP_ID`→`ITEM_CLASS_ID`; `PARENT_CATALOG_GROUP_ID`→`PARENT_ITEM_CLASS_ID`; `INTERNAL_NAME` absent. |
| **EGP_ITEM_RELATIONSHIPS_B** | `RELATIONSHIP_TYPE_ID`→`ITEM_RELATIONSHIP_TYPE` (now a VARCHAR2 code); `START_DATE`/`END_DATE`→`START_DATE_ACTIVE`/`END_DATE_ACTIVE`. + ATTRIBUTE width changes. |
| **EGP_STRUCTURES_B** | `ORGANIZATION_ID`→`COMMON_ORGANIZATION_ID`; `ASSEMBLY_ITEM_ID`→`COMMON_ASSEMBLY_ITEM_ID`/`PK1_VALUE`. `ALTERNATE_BOM_DESIGNATOR` `(40)`→`(80)`. |
| **EGP_COMPONENTS_B** | `COMPONENT_ITEM_ID` absent — component item is in `PK1_VALUE` (`VARCHAR2`, cast to NUMBER to join). |
| **EGP_ITEM_ORG_ASSOCIATIONS** | `MASTER_ORGANIZATION_ID` absent — use `INVENTORY_ORGANIZATION_ID`/`ITEM_DEFINITION_ORG_ID`. |
| **EGP_SYSTEM_ITEMS_B** | `TRADING_PARTNER_ID`, `TP_TYPE`, `TP_ITEM_NUMBER` not on this table (they're in `EGP_TRADING_PARTNER_ITEMS`). Plus several VARCHAR2/NUMBER width diffs (non-breaking for SELECT). |
| **EGP_MFG_PART_NUMBERS_B** | In 26B exposed as view `EGP_MFG_PART_NUMBERS_B_V`; PK `MFG_PART_NUM_ID`→`ITEM_RELATIONSHIP_ID`; `START_DATE`/`END_DATE`→`START_DATE_ACTIVE`/`END_DATE_ACTIVE`. |

### Workflow (SOA tables — see Tier 1b caveat)
| Table | Broken columns → fix |
|---|---|
| **WFTASK** | `ROOTTASKID`, `PARENTTASKID`, `PRODUCTNAME`, `PRODUCTTYPE`, `CATEGORY`, `TASKDISPLAYURL` not in base DDL/queries. 5 date cols typed `DATE` not `TIMESTAMP`. |
| **WFCOMMENTS** | `COMMENTID`, `CREATEDBY`, `CREATEDDATE` don't exist; comment text is **`WFCOMMENT VARCHAR2(2000)`** not `TASKCOMMENT CLOB`. PK is composite `(taskId, version)`. |
| **WFTASKHISTORY** | `COMMENTS`→**`USERCOMMENT`**; `UPDATEDDATE` `TIMESTAMP`→`DATE`. |

---

## 🟡 Tier 3 — Type/size differences only (won't break SELECT)

- **EGP_CATEGORIES_B** — `CATEGORY_CODE` `(40)`→`(820)` ⚠️ (could truncate); `ATTRIBUTE1` `(240)`→`(150)`; `SUMMARY_FLAG` should be NOT NULL.
- **EGP_ITEM_REVISIONS_B** — `ATTRIBUTE1` `(240)`→`(150)`; `ALT_REVISION_CODE` `(30)`→`(40)`.
- **EGP_ITEM_REVISIONS_V** — `ALT_REVISION_CODE` `(30)`→`(40)`.

---

## ✅ Tier 4 — Verified unchanged (29 tables)

All declared columns present with compatible types — safe as-is:

`AP_INVOICES_ALL`, `AP_INVOICE_LINES_ALL`, `AP_PAYMENT_HISTORY_ALL`, `AP_TERMS_LINES`, `AP_TERMS_TL`, `RA_CUSTOMER_TRX_ALL`, `RA_CUSTOMER_TRX_LINES_ALL`, `PER_PERSON_NAMES_F_V`, `INV_ORG_PARAMETERS_V`, `DOO_HEADERS_ALL`, `DOO_LINES_ALL`, `PO_ACTION_HISTORY`, `PO_DISTRIBUTIONS_ALL`, `PO_HEADERS_ALL`, `PO_LINES_ALL`, `PO_LINE_LOCATIONS_ALL`, `EGO_ITEM_EFF_B`, `EGO_ITEM_REVISION_EFF_B`, `EGP_CATEGORIES_TL`, `EGP_CATEGORY_SETS_B`, `EGP_CATEGORY_SET_VALID_CATS`, `EGP_ITEM_CAT_ASSIGNMENTS`, `EGP_ITEM_REVISIONS_TL`, `EGP_SYSTEM_ITEMS`, `EGP_SYSTEM_ITEMS_TL`, `EGP_SYSTEM_ITEMS_TL_ALL_V`, `WSH_DELIVERY_ASSIGNMENTS`, `WSH_DELIVERY_DETAILS`, `WSH_NEW_DELIVERIES`.

(`EGP_DEFAULT_CATEGORY_SETS` — no standalone doc page, but its 2 columns are consistent with the referenced FK in `EGP_CATEGORY_SETS_B`; treat as OK.)

---

## Caveats

1. **Not a live-DB check.** Findings are vs. Oracle's *published documentation*. Oracle docs cover application-layer EDM tables; they exclude SOA-internal (`WF*`/`HWF*`) tables, which can still exist on your pod. Confirm the highest-impact items with a real `SELECT` once the Fusion login works.
2. **Release coverage.** Many 26A/26B deep-links redirect to landing pages, so several tables were verified at 25C/25D — the most recent fully-published page. Core structures are stable across these releases.
3. **`EGP_MFG_PART_NUMBERS`** (4-col view) wasn't verified (agent timeout). Re-run if needed.
4. **Strongest single fix:** for the Procurement/Suppliers and Item tables, point SQL generation at the documented **views** (`_V`/`_VL`) rather than base tables (`_B`/`_ALL_M`) — that resolves a large share of the Tier 2 findings at once.
