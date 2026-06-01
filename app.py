"""
BI Publisher SQL Query Builder for Oracle Fusion Cloud
Covers: Procurement, Order Management, Shipping & Financials (AP/AR)
Uses Claude API to generate SQL queries from natural language descriptions.
"""


import os
import io
import re
import glob
import zlib
from urllib.parse import unquote
import streamlit as st
import anthropic
import pandas as pd
from dotenv import load_dotenv

# JDBC bridge to live Fusion BI Publisher is local-only — Streamlit Community
# Cloud has no JVM, so wrap these so the module imports even when they fail.
try:
    import jpype
    import jaydebeapi
    JDBC_AVAILABLE = True
except Exception:
    JDBC_AVAILABLE = False

# Optional extra AI providers — only needed to validate/use OpenAI or Gemini
# keys. Wrapped so the app still imports when these packages aren't installed.
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


def _get_secret(key, default=""):
    """Prefer st.secrets (cloud) then env vars (local .env)."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


# ---------------------------------------------------------------------------
# AI provider key validation + sidebar UI
# ---------------------------------------------------------------------------
def _validate_anthropic(key):
    """Lightweight auth check for an Anthropic (Claude) key."""
    try:
        anthropic.Anthropic(api_key=key).models.list()
        return True, None
    except anthropic.AuthenticationError:
        return False, "Invalid API key"
    except Exception as e:
        return False, str(e)


def _validate_openai(key):
    """Lightweight auth check for an OpenAI key."""
    if not OPENAI_AVAILABLE:
        return False, "openai package not installed (add 'openai' to requirements)"
    try:
        OpenAI(api_key=key).models.list()
        return True, None
    except Exception as e:
        return False, str(e)


def _validate_gemini(key):
    """Lightweight auth check for a Google Gemini key."""
    if not GEMINI_AVAILABLE:
        return False, "google-generativeai package not installed"
    try:
        genai.configure(api_key=key)
        list(genai.list_models())
        return True, None
    except Exception as e:
        return False, str(e)


def _provider_key_ui(label, secret_name, validator, help_text):
    """Render a provider API-key input in the sidebar.

    Resolves the key from secrets/env (or a password field), auto-validates it
    once per distinct value with a popup toast, and offers a manual re-test
    button. Returns the resolved key string (may be '').
    """
    loaded = _get_secret(secret_name, "")
    if loaded:
        key = loaded
        st.caption(f"{label}: loaded from secrets 🔒")
    else:
        key = st.text_input(f"{label} API Key", type="password", help=help_text)

    # Auto-validate once whenever the key value changes -> popup confirmation.
    state_key = f"_validated_{secret_name}"
    if key and st.session_state.get(state_key) != key:
        ok, err = validator(key)
        st.session_state[state_key] = key
        st.session_state[f"_ok_{secret_name}"] = ok
        if ok:
            st.toast(f"{label} API key works! ✅", icon="✅")
        else:
            st.toast(f"{label} key error: {err}", icon="⚠️")

    # Manual re-test button (also a popup).
    if st.button(f"Test {label} key", width="stretch",
                 disabled=not key, key=f"btn_test_{secret_name}"):
        ok, err = validator(key)
        if ok:
            st.toast(f"{label} API key works! ✅", icon="✅")
            st.success(f"{label} API key is valid and working.")
        else:
            st.toast(f"{label} key failed ❌", icon="❌")
            st.error(f"{label} key invalid: {err}")

    return key


# ---------------------------------------------------------------------------
# BIP Catalog (.xdm.catalog) loader - RAG knowledge base
# (defined early so the sidebar can call load_catalog_library() at import time)
# ---------------------------------------------------------------------------
def _decompress_catalog(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return zlib.decompress(raw).decode("utf-8", errors="replace")
    except zlib.error:
        return zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8", errors="replace")


def parse_xdm_catalog(path):
    """Parse a .xdm.catalog file and pull out the data model XML, its
    description, SQL datasets, and parameters."""
    file_name = os.path.basename(path)
    try:
        decoded = _decompress_catalog(path)
    except Exception as e:
        return {"name": file_name, "error": f"decompress failed: {e}"}

    xml_start = decoded.find("<?xml")
    xml_end = decoded.rfind("</dataModel>")
    if xml_start == -1 or xml_end == -1:
        return {"name": file_name, "error": "no <dataModel> XML found"}
    xml = decoded[xml_start:xml_end + len("</dataModel>")]

    desc_match = re.search(
        r"<description>\s*<!\[CDATA\[(.*?)\]\]>\s*</description>", xml, re.DOTALL
    )
    description = unquote(desc_match.group(1)) if desc_match else ""

    sql_datasets = []
    for ds in re.finditer(
        r'<dataSet\s+name="([^"]+)"[^>]*>(.*?)</dataSet>', xml, re.DOTALL
    ):
        sql_match = re.search(
            r"<sqlStatement[^>]*>\s*<!\[CDATA\[(.*?)\]\]>\s*</sqlStatement>",
            ds.group(2), re.DOTALL,
        )
        if sql_match:
            sql_datasets.append({
                "name": ds.group(1),
                "sql": sql_match.group(1).strip(),
            })

    parameters = []
    for p in re.finditer(r"<parameter\s+([^>]+?)/?>", xml):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', p.group(1)))
        if attrs.get("name"):
            parameters.append({
                "name": attrs.get("name", ""),
                "type": attrs.get("dataType", ""),
                "default": attrs.get("defaultValue", ""),
            })

    return {
        "name": file_name,
        "description": description,
        "sql_datasets": sql_datasets,
        "parameters": parameters,
        "error": None,
    }


@st.cache_data(show_spinner=False)
def load_catalog_library():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    return [parse_xdm_catalog(p) for p in sorted(glob.glob(os.path.join(app_dir, "*.xdm.catalog")))]


def build_catalog_context(catalogs, max_chars=30000):
    """Compact bundle of catalog SQL to inject as RAG context for Claude."""
    parts = ["## REFERENCE: Existing BI Publisher Data Models in this workspace.",
             "Use these production-tested SQL patterns as guidance when generating new queries.\n"]
    total = sum(len(p) for p in parts)
    for cat in catalogs:
        if cat.get("error") or not cat.get("sql_datasets"):
            continue
        block = [f"### {cat['name']}"]
        if cat.get("description"):
            block.append(f"_{cat['description'][:300]}_")
        for ds in cat["sql_datasets"]:
            sql = ds["sql"]
            if len(sql) > 4000:
                sql = sql[:4000] + "\n-- ... (truncated)"
            block.append(f"-- DataSet: {ds['name']}\n```sql\n{sql}\n```")
        block_text = "\n".join(block) + "\n"
        if total + len(block_text) > max_chars:
            parts.append("\n-- (additional catalogs omitted to stay within context budget)")
            break
        parts.append(block_text)
        total += len(block_text)
    return "\n".join(parts)
from schema import (
    ALL_TABLES, RELATIONSHIPS, SUPPORTING_TABLES, VIEWS,
    LOOKUP_VALUES, PO_HEADERS_ALL, PO_LINES_ALL,
    PO_LINE_LOCATIONS_ALL, PO_DISTRIBUTIONS_ALL, PO_ACTION_HISTORY,
)
from schema_om_ship_fin import (
    ALL_OM_SHIP_FIN_TABLES, OM_SHIP_FIN_RELATIONSHIPS,
    OM_SHIP_FIN_LOOKUP_VALUES,
)
from schema_items_inventory import (
    ALL_ITEM_TABLES, ITEM_RELATIONSHIPS, ITEM_LOOKUP_VALUES,
)
from schema_suppliers import (
    ALL_SUPPLIER_TABLES, SUPPLIER_RELATIONSHIPS, SUPPLIER_LOOKUP_VALUES,
)
from schema_workflow import (
    ALL_WORKFLOW_TABLES, WORKFLOW_RELATIONSHIPS, WORKFLOW_LOOKUP_VALUES,
    WORKFLOW_SQL_PATTERNS,
)
from examples import EXAMPLES

# Merge all tables into one dict for the schema browser
COMBINED_TABLES = {**ALL_TABLES, **ALL_OM_SHIP_FIN_TABLES, **ALL_ITEM_TABLES, **ALL_SUPPLIER_TABLES, **ALL_WORKFLOW_TABLES}
COMBINED_RELATIONSHIPS = {**RELATIONSHIPS, **OM_SHIP_FIN_RELATIONSHIPS, **ITEM_RELATIONSHIPS, **SUPPLIER_RELATIONSHIPS, **WORKFLOW_RELATIONSHIPS}
COMBINED_LOOKUPS = {**LOOKUP_VALUES, **OM_SHIP_FIN_LOOKUP_VALUES, **ITEM_LOOKUP_VALUES, **SUPPLIER_LOOKUP_VALUES, **WORKFLOW_LOOKUP_VALUES}

# Module -> table-name-prefix map, shared by the sidebar Schema Browser and the
# Schema Explorer tab. str.startswith() accepts a tuple, so str and tuple prefixes
# are handled uniformly.
MODULE_PREFIX_MAP = {
    "All": None,
    "Procurement (PO)": "PO_",
    "Suppliers (POZ)": "POZ_",
    "Workflow (BPM)": ("WF", "HWF_", "PER_"),
    "Order Mgmt (DOO)": "DOO_",
    "Shipping (WSH)": "WSH_",
    "Payables (AP)": "AP_",
    "Receivables (AR)": "RA_",
    "Items (EGP)": ("EGP_", "EGO_", "INV_"),
    "Payments (IBY)": "IBY_",
    "Cash Mgmt (CE)": "CE_",
}


def filter_tables_by_module(module_name):
    """Return the subset of COMBINED_TABLES belonging to the selected module."""
    prefix = MODULE_PREFIX_MAP.get(module_name)
    if prefix is None:
        return COMBINED_TABLES
    return {k: v for k, v in COMBINED_TABLES.items() if k.startswith(prefix)}

# Load .env file for API key
load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Terillium - BI Publisher SQL Builder",
    page_icon="terillium_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark theme - main app background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    /* Header bar accent */
    .stApp > header {
        background-color: #1a1a2e;
    }
    /* Sidebar styling - dark */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        color: #e0e0e0;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 600;
        color: #c9d1d9;
    }
    /* Code block styling */
    .stCodeBlock {
        border-left: 3px solid #0066cc;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161b22;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-weight: 600;
        color: #c9d1d9;
    }
    /* Container borders */
    [data-testid="stExpander"] {
        border: 1px solid #30363d;
        border-radius: 8px;
        background-color: #161b22;
    }
    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #21262d;
        color: #e0e0e0;
        border-color: #30363d;
    }
    /* Markdown text */
    .stMarkdown {
        color: #e0e0e0;
    }
    /* Success/info boxes */
    .stSuccess {
        background-color: #1a2e1a;
        color: #56d364;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar - API key & schema browser
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("terillium_logo.png", width=180)
    st.markdown("---")
    st.title("Settings")

    st.subheader("🔑 AI Provider Keys")

    # Anthropic (Claude) is the key used to generate SQL.
    api_key = _provider_key_ui(
        "Anthropic (Claude)", "ANTHROPIC_API_KEY", _validate_anthropic,
        "Set ANTHROPIC_API_KEY in .env (local) or Streamlit secrets (cloud), or enter here.",
    )

    # Optional extra providers — stored for future use.
    openai_key = _provider_key_ui(
        "OpenAI", "OPENAI_API_KEY", _validate_openai,
        "Optional. Set OPENAI_API_KEY in .env / Streamlit secrets, or enter here.",
    )
    gemini_key = _provider_key_ui(
        "Google Gemini", "GEMINI_API_KEY", _validate_gemini,
        "Optional. Set GEMINI_API_KEY in .env / Streamlit secrets, or enter here.",
    )
    st.session_state["openai_key"] = openai_key
    st.session_state["gemini_key"] = gemini_key

    st.divider()
    st.subheader("🔌 Fusion Connection (ofjdbc)")
    if not JDBC_AVAILABLE:
        st.info("Live Fusion testing is disabled in this environment "
                "(no JVM available). SQL generation still works.")

    fusion_host = st.text_input(
        "Fusion Host",
        value=_get_secret("FUSION_HOST", ""),
        placeholder="your-server.oraclecloud.com",
        help="e.g. ecog-test.fa.ocs.oraclecloud.com",
        disabled=not JDBC_AVAILABLE,
    )
    fusion_user = st.text_input(
        "Fusion Username",
        value=_get_secret("FUSION_USERNAME", ""),
        disabled=not JDBC_AVAILABLE,
    )
    fusion_pass = st.text_input(
        "Fusion Password",
        type="password",
        value=_get_secret("FUSION_PASSWORD", ""),
        disabled=not JDBC_AVAILABLE,
    )
    fusion_report_path = st.text_input(
        "Report Path",
        value=_get_secret("FUSION_REPORT_PATH", "/~scm_impl/Ian_TEST/RP_ARB.xdo"),
        help="Path where you deployed the ofjdbc catalog files in BI Publisher.",
        disabled=not JDBC_AVAILABLE,
    )

    # Store connection info in session state
    if JDBC_AVAILABLE and fusion_host and fusion_user and fusion_pass:
        st.session_state["fusion_connected"] = True
        st.session_state["fusion_host"] = fusion_host
        st.session_state["fusion_user"] = fusion_user
        st.session_state["fusion_pass"] = fusion_pass
        st.session_state["fusion_report_path"] = fusion_report_path
        st.success("Fusion credentials set")
    else:
        st.session_state["fusion_connected"] = False
        if JDBC_AVAILABLE:
            st.caption("Enter Fusion credentials to enable live query testing.")

    st.divider()
    st.subheader("📋 Schema Browser")

    # Module filter
    module_filter = st.radio(
        "Module",
        list(MODULE_PREFIX_MAP.keys()),
        horizontal=True,
    )
    filtered_tables = filter_tables_by_module(module_filter)

    # Table selector
    selected_table = st.selectbox(
        "Explore Table",
        options=list(filtered_tables.keys()),
        index=0,
    )

    if selected_table:
        tbl = COMBINED_TABLES[selected_table]
        desc = tbl["description"] if isinstance(tbl.get("description"), str) else " ".join(tbl.get("description", ""))
        st.caption(desc)
        pk = tbl.get("primary_key", "N/A")
        if isinstance(pk, list):
            pk = ", ".join(pk)
        st.caption(f"**Primary Key:** `{pk}`")

        # Support both "columns" (full schema) and "key_columns" (summary)
        cols_dict = tbl.get("columns") or tbl.get("key_columns") or {}

        # Column search
        col_search = st.text_input("Search columns", key="col_search")
        cols = cols_dict
        if col_search:
            cols = {
                k: v for k, v in cols.items()
                if col_search.upper() in k or col_search.lower() in v.get("desc", "").lower()
            }

        with st.expander(f"Columns ({len(cols)})", expanded=True):
            for col_name, col_info in cols.items():
                nullable_val = col_info.get("nullable")
                nullable = "" if nullable_val is False else (" NULL" if nullable_val is True else "")
                st.markdown(
                    f"**`{col_name}`** `{col_info['type']}{nullable}`  \n"
                    f"_{col_info.get('desc', '')}_"
                )

    st.divider()
    st.subheader("📚 BIP Catalog (RAG)")
    catalogs = load_catalog_library()
    loaded = sum(1 for c in catalogs if not c.get("error"))
    failed = len(catalogs) - loaded
    use_catalog_rag = st.checkbox(
        "Use catalog as RAG context",
        value=False,
        help="When enabled, SQL from your local .xdm.catalog files is injected into Claude's prompt as reference patterns.",
    )
    st.caption(f"{loaded} catalog(s) loaded" + (f", {failed} failed" if failed else ""))

    st.divider()
    with st.expander("🔗 Table Relationships"):
        for rel, join_clause in COMBINED_RELATIONSHIPS.items():
            st.code(join_clause, language="sql")

    with st.expander("📚 Supporting Tables"):
        for tbl_name, desc in SUPPORTING_TABLES.items():
            st.markdown(f"**`{tbl_name}`** - {desc}")

    with st.expander("👁️ Views"):
        for view_name, desc in VIEWS.items():
            st.markdown(f"**`{view_name}`** - {desc}")

    with st.expander("🔍 Lookup Values"):
        for lookup_name, values in COMBINED_LOOKUPS.items():
            st.markdown(f"**{lookup_name}:**")
            for val in values:
                st.markdown(f"- `{val}`")


# ---------------------------------------------------------------------------
# Build the system prompt for Claude
# ---------------------------------------------------------------------------
def build_system_prompt():
    """Assemble the full schema context for Claude."""
    schema_text = """You are an expert Oracle Fusion Cloud SQL developer specializing in BI Publisher reports.
You write SQL queries that run inside Oracle BI Publisher against the FUSION schema.
You have deep knowledge of: Procurement (PO), Order Management (DOO), Shipping (WSH), Accounts Payable (AP), and Accounts Receivable (AR).

## CRITICAL RULES FOR BI PUBLISHER SQL:
1. Use Oracle SQL syntax (not MySQL/PostgreSQL/SQL Server)
2. Use the WHERE 1=1 pattern for easy predicate management
3. Use Oracle outer join syntax with (+) for optional joins: AND table1.col = table2.col (+)
4. Always alias tables with short meaningful names (PHA, PLA, PLLA, PDA, PS, HP, ESI, etc.)
5. For BI Publisher parameters, use :P_PARAM_NAME syntax (e.g., :P_PO_NUMBER, :P_BU_ID)
6. Always include PHA.SEGMENT1 IS NOT NULL to exclude incomplete drafts
7. Use NVL() for nullable columns in calculations: NVL(PLLA.QUANTITY_RECEIVED, 0)
8. Use NVL(PHA.CANCEL_FLAG, 'N') = 'N' to filter out cancelled records
9. SEGMENT1 in PO_HEADERS_ALL is the human-readable PO Number
10. Always ORDER BY the most logical columns (PO number, line number, etc.)
11. NEVER use PS.VENDOR_NAME - that column does NOT exist on POZ_SUPPLIERS. The supplier name is ALWAYS HZ_PARTIES.PARTY_NAME (aliased as HP.PARTY_NAME). You MUST join POZ_SUPPLIERS to HZ_PARTIES via PS.PARTY_ID = HP.PARTY_ID to get the supplier name.
12. POZ_SUPPLIERS key columns are: VENDOR_ID, PARTY_ID, SEGMENT1 (supplier number), VENDOR_TYPE_LOOKUP_CODE, END_DATE_ACTIVE. It does NOT have VENDOR_NAME, SUPPLIER_NAME, or any name column.
13. For supplier number use POZ_SUPPLIERS.SEGMENT1 (alias as SUPPLIER_NUMBER to avoid confusion with PHA.SEGMENT1 which is the PO Number).
14. ALWAYS include BOTH POZ_SUPPLIERS and HZ_PARTIES when the user asks for supplier information. Never use just one without the other.
15. CRITICAL EBS vs FUSION CLOUD DIFFERENCE: The columns UNIT_OF_MEASURE and UNIT_MEAS_LOOKUP_CODE do NOT exist on ANY table in Fusion Cloud. Those are EBS-only column names. In Fusion Cloud the column is ALWAYS UOM_CODE (VARCHAR2(3) code like 'EA'). This applies to ALL tables: PO_HEADERS_ALL, PO_LINES_ALL, PO_LINE_LOCATIONS_ALL, PO_DISTRIBUTIONS_ALL, RCV_TRANSACTIONS, RCV_SHIPMENT_LINES, etc. NEVER use UNIT_OF_MEASURE or UNIT_MEAS_LOOKUP_CODE — ALWAYS use UOM_CODE.
16. NEVER use GL_CODE_COMBINATIONS_KFV - it does NOT exist in Fusion Cloud. That is an EBS-only view. Use GL_CODE_COMBINATIONS instead and manually concatenate segments: GCC.SEGMENT1 || '.' || GCC.SEGMENT2 || '.' || GCC.SEGMENT3 || '.' || GCC.SEGMENT4 || '.' || GCC.SEGMENT5 AS ACCOUNT.
17. For requisitions, the Fusion Cloud tables are: POR_REQUISITION_HEADERS_ALL (PRH), POR_REQUISITION_LINES_ALL (PRL), POR_REQ_DISTRIBUTIONS_ALL (PRD). Key joins: PRH.REQUISITION_HEADER_ID = PRL.REQUISITION_HEADER_ID, PRL.REQUISITION_LINE_ID = PRD.REQUISITION_LINE_ID. The req number is PRH.REQUISITION_NUMBER.
18. CRITICAL requisition column differences from PO tables: On POR_REQ_DISTRIBUTIONS_ALL the distribution number column is DISTRIBUTION_NUMBER (not DISTRIBUTION_NUM). Quantity is DISTRIBUTION_QUANTITY (not QUANTITY_ORDERED). Amount is DISTRIBUTION_AMOUNT (not AMOUNT_ORDERED). PRD does NOT have DELIVER_TO_PERSON_ID, DELIVER_TO_LOCATION_ID, or DESTINATION_ORGANIZATION_ID - those columns are on POR_REQUISITION_LINES_ALL (PRL). Use PRL.REQUESTER_ID (not DELIVER_TO_PERSON_ID) for the requester, PRL.DELIVER_TO_LOCATION_ID for deliver-to location, PRL.DESTINATION_ORGANIZATION_ID for destination org. The line number column is PRL.LINE_NUMBER (not LINE_NUM).
19. POR_REQUISITION_HEADERS_ALL does NOT have CANCEL_FLAG. To exclude cancelled reqs, use PRL.CANCEL_FLAG on the LINES table: NVL(PRL.CANCEL_FLAG, 'N') = 'N'. For header-level status filtering use PRH.DOCUMENT_STATUS (values like APPROVED, REJECTED, WITHDRAWN, IN PROCESS, INCOMPLETE). Other useful header flags: ACTIVE_REQUISITION_FLAG, HAS_CANCELED_LINES, LIFECYCLE_STATUS.
20. ADDITIONAL TABLES from real production reports:
  - AP_INVOICE_PAYMENTS_ALL (AIP): Invoice payments. Key cols: INVOICE_ID, CHECK_ID, AMOUNT, ACCOUNTING_DATE, PERIOD_NAME, POSTED_FLAG, DISCOUNT_LOST, DISCOUNT_TAKEN, REVERSAL_FLAG, INVOICE_PAYMENT_TYPE. Join: AIP.INVOICE_ID = AIA.INVOICE_ID, AIP.CHECK_ID = AC.CHECK_ID
  - AP_CHECKS_ALL (AC): Payment checks/disbursements. Key cols: CHECK_ID, CHECK_NUMBER, CHECK_DATE, AMOUNT, VENDOR_NAME, VENDOR_ID, VENDOR_SITE_CODE, BANK_ACCOUNT_NAME, ADDRESS_LINE1-4, CITY, STATE, COUNTRY, ZIP, PAYMENT_ID, VOID_DATE, CLEARED_AMOUNT, CLEARED_DATE, CHECKRUN_NAME. Note: AC.VENDOR_NAME exists on AP_CHECKS_ALL (unlike POZ_SUPPLIERS)
  - IBY_PAYMENTS_ALL: Payment method details. Join: AC.PAYMENT_ID = IBY_PAYMENTS_ALL.PAYMENT_ID. Key col: PAYMENT_METHOD_CODE
  - AP_PAYMENT_SCHEDULES_ALL (APS): Invoice payment schedules / due dates. Join: AIA.INVOICE_ID = APS.INVOICE_ID. Key cols: INVOICE_ID, PAYMENT_NUM, DUE_DATE, GROSS_AMOUNT, AMOUNT_REMAINING, PAYMENT_STATUS_FLAG, DISCOUNT_DATE, SECOND_DISCOUNT_DATE, THIRD_DISCOUNT_DATE, DISCOUNT_AMOUNT_AVAILABLE, HOLD_FLAG. Use this table for AP invoice due dates — AP_INVOICES_ALL does NOT have DUE_DATE or TERM_DUE_DATE.
  - AP_INVOICE_DISTRIBUTIONS_ALL: Invoice distributions. Key cols: INVOICE_ID, INVOICE_LINE_NUMBER, DISTRIBUTION_LINE_NUMBER, AMOUNT, RCV_TRANSACTION_ID, ACCOUNTING_DATE, QUANTITY_INVOICED
  - RCV_TRANSACTIONS (RT): Receiving transactions. Key cols: TRANSACTION_ID, TRANSACTION_TYPE ('RECEIVE','DELIVER','RETURN'), TRANSACTION_DATE, QUANTITY, UOM_CODE, PO_UNIT_PRICE, PO_HEADER_ID, PO_LINE_ID, PO_LINE_LOCATION_ID, SHIPMENT_HEADER_ID, SHIPMENT_LINE_ID, ORGANIZATION_ID, DESTINATION_TYPE_CODE, SUBINVENTORY, LOCATOR_ID. DOES NOT HAVE: ITEM_ID (use PLA.ITEM_ID or RSL.ITEM_ID instead), UNIT_OF_MEASURE (use UOM_CODE), TRANSACTION_QUANTITY or PRIMARY_QUANTITY (use QUANTITY). For item info, join through PO_LINES_ALL (PLA.ITEM_ID) or RCV_SHIPMENT_LINES (RSL.ITEM_ID).
  - RCV_SHIPMENT_HEADERS (RSH): Receipt headers. Join: RSH.SHIPMENT_HEADER_ID = RT.SHIPMENT_HEADER_ID. Key cols: RECEIPT_NUM
  - RCV_SHIPMENT_LINES (RSL): Receipt lines. Join: RSL.SHIPMENT_LINE_ID = RT.SHIPMENT_LINE_ID. Key cols: SHIPMENT_LINE_ID, SHIPMENT_HEADER_ID, LINE_NUM, PO_HEADER_ID, PO_LINE_ID, PO_LINE_LOCATION_ID, QUANTITY_SHIPPED, QUANTITY_RECEIVED, QUANTITY_DELIVERED, QUANTITY_RETURNED, QUANTITY_ACCEPTED, QUANTITY_REJECTED, SHIPMENT_LINE_STATUS_CODE, ITEM_ID, ITEM_DESCRIPTION, CATEGORY_ID, TO_ORGANIZATION_ID, TO_SUBINVENTORY, DESTINATION_TYPE_CODE, UOM_CODE, PRIMARY_UOM_CODE, SHIPMENT_UNIT_PRICE, AMOUNT, AMOUNT_RECEIVED. WARNING: This is Fusion Cloud — the column is UOM_CODE (VARCHAR2(3) code like 'EA'), NOT UNIT_OF_MEASURE (the EBS spelled-out name). NEVER use RSL.UNIT_OF_MEASURE — it does NOT exist in Fusion Cloud. Use RSL.UOM_CODE instead.
  - RCV_SUPPLIER_RETURN_HEADERS: Supplier returns. Key cols: SUPPLIER_RETURN_HEADER_ID, SUPPLIER_RETURN_NUMBER, VENDOR_ID, RETURN_STATUS
  - RCV_SUPPLIER_RETURN_LINES: Return lines. Key cols: SUPPLIER_RETURN_HEADER_ID, ITEM_ID, ITEM_DESCRIPTION, PRIMARY_QUANTITY, RMA_REFERENCE
  - POZ_SUPPLIERS_V / POZ_SUPPLIERS_INT: Supplier views (include VENDOR_NAME column, unlike base POZ_SUPPLIERS table)
  - POZ_SUPPLIER_SITES_V: Supplier sites view. Key col: PAY_GROUP_LOOKUP_CODE
  - DOO_FULFILL_LINES_ALL (DFLA): OM fulfillment lines. Key cols: FULFILL_LINE_ID, HEADER_ID, LINE_ID, SOURCE_LINE_NUMBER, SOURCE_ORDER_NUMBER, FULFILL_LINE_NUMBER, ORDERED_QTY, ORDERED_UOM, UNIT_SELLING_PRICE, INVENTORY_ITEM_ID, STATUS_CODE, SHIPPING_INSTRUCTIONS. Join: DFLA.SOURCE_ORDER_NUMBER = DHA.SOURCE_ORDER_NUMBER or DFLA.HEADER_ID = DHA.HEADER_ID
  - DOO_HEADERS_EFF_B (DHEB): OM header extensible flexfields. Join: DHA.HEADER_ID = DHEB.HEADER_ID AND DHEB.CONTEXT_CODE = '<context>'. Key cols: ATTRIBUTE_CHAR1-20
  - DOO_ORDER_ADDRESSES (DOA): OM order addresses. Join: DHA.HEADER_ID = DOA.HEADER_ID. Key cols: ADDRESS_USE_TYPE ('BILL_TO','SHIP_TO'), CUST_ACCT_ID, CUST_ACCT_SITE_USE_ID, PARTY_SITE_ID
  - DOO_SALES_CREDITS (DSC): Sales credits. Join: DHA.HEADER_ID = DSC.HEADER_ID. Key col: SALESPERSON_ID
  - FUN_ALL_BUSINESS_UNITS_V (FABU): BU names. Join: DHA.ORG_ID = FABU.BU_ID. Key cols: BU_ID, BU_NAME
  - FND_VS_VALUES_VL: Flexfield value set values. Used with GL_CODE_COMBINATIONS to get segment descriptions: WHERE ATTRIBUTE_CATEGORY = '<value_set_name>' AND VALUE = GCC.SEGMENTn
  - EGP_ITEM_CAT_ASSIGNMENTS: Item category assignments. Join: ORGANIZATION_ID + INVENTORY_ITEM_ID. Key col: CATEGORY_SET_ID, CATEGORY_ID
  - EGP_CATEGORY_SETS_TL: Category set names. Join: CATEGORY_SET_ID. Key col: CATEGORY_SET_NAME
  - EGP_CATEGORIES_TL: Category names. Join: CATEGORY_ID. Key col: CATEGORY_NAME
  - EGP_CATEGORIES_B: Category codes. Join: CATEGORY_ID. Key col: CATEGORY_CODE
  - PO_AGENT_ASSIGNMENTS: Buyer/agent assignments. Join: EGP_SYSTEM_ITEMS_B.BUYER_ID = PO_AGENT_ASSIGNMENTS.ASSIGNMENT_ID. Key col: AGENT_ID
  - HZ_CUST_ACCOUNTS (HZA): Customer accounts. Key cols: CUST_ACCOUNT_ID, PARTY_ID, ACCOUNT_NUMBER
  - HZ_CUST_ACCT_SITES_ALL (HZCASA): Customer account sites. Key cols: CUST_ACCT_SITE_ID, PARTY_SITE_ID, CUST_ACCOUNT_ID
  - HZ_CUST_SITE_USES_ALL (HZCSUA): Customer site uses. Key cols: SITE_USE_ID, CUST_ACCT_SITE_ID, SITE_USE_CODE
  - HZ_PARTY_SITES (HZPS): Party sites. Key cols: PARTY_SITE_ID, PARTY_ID, LOCATION_ID
  - HZ_LOCATIONS (HZL): Locations (non-HR). Key cols: LOCATION_ID, ADDRESS1-4, CITY, STATE, COUNTRY, POSTAL_CODE, BUILDING, FLOOR_NUMBER
  - HZ_CUST_ACCOUNT_ROLES (HCAR): Customer contact roles. Join via RELATIONSHIP_ID
  - HZ_RELATIONSHIPS (HZR): Party relationships. For contacts: RELATIONSHIP_CODE='CONTACT', OBJECT_TYPE='PERSON'
  - INV_ORGANIZATION_DEFINITIONS_V (IODV): Inventory org definitions. Key cols: ORGANIZATION_ID, ORGANIZATION_CODE, ORGANIZATION_NAME
  - MSC_INSTANCE_ORGS: Planning org codes. Key col: ORGANIZATION_CODE
  - MSC_PAYMENT_TERMS_TL (MPT): Payment terms for OM. Join: DHA.PAYMENT_TERM_ID = MPT.TERM_ID. Key col: NAME
  - JTF_RS_SALESREPS (JRS): Sales resources. Join: SALESPERSON_ID = JRS.RESOURCE_ID
  - FND_ATTACHED_DOCUMENTS (FAD): Attachments. Key cols: PK1_VALUE (header ID), ENTITY_NAME, DOCUMENT_ID
  - FND_DOCUMENTS_TL (FDT): Document translations. Join: FAD.DOCUMENT_ID = FDT.DOCUMENT_ID. Key cols: FILE_NAME, DM_VERSION_NUMBER
21. For Received-Not-Invoiced (RNI) reports, use CTE pattern: join RCV_TRANSACTIONS (transaction_type='DELIVER') with AP_INVOICE_DISTRIBUTIONS_ALL (via RCV_TRANSACTION_ID) to compare qty received vs qty invoiced.
22. For Uninvoiced Imports, join RCV_SHIPMENT_LINES to AP_INVOICE_LINES_ALL via PO_HEADER_ID + PO_LINE_ID + PO_LINE_LOCATION_ID and compare quantities.
23. For OM customer addresses, use chain: DOO_ORDER_ADDRESSES.ADDRESS_USE_TYPE = 'SHIP_TO' or 'BILL_TO' -> HZ_CUST_SITE_USES_ALL -> HZ_CUST_ACCT_SITES_ALL -> HZ_PARTY_SITES -> HZ_LOCATIONS for the full address.
24. DOO_HEADERS_ALL status codes: 'OPEN', 'CLOSED', 'PARTIAL_CLOSE', 'DOO_DRAFT', 'DOO_REFERENCE'. Filter drafts with: DHA.STATUS_CODE NOT IN ('DOO_DRAFT', 'DOO_REFERENCE'). Order types: 'Standard', 'Quote', 'Proposal', 'Prebill'.
25. DOO_FULFILL_LINES_ALL status codes: 'CANCELED', 'CLOSED', 'CANCEL_PENDING', 'AWAITING_SHIPPING', 'SHIPPED', etc. Filter active: DFLA.STATUS_CODE NOT IN ('CANCELED', 'CLOSED', 'CANCEL_PENDING').
26. WSH_NEW_DELIVERIES does NOT have TRACKING_NUMBER. Tracking number is on WSH_DELIVERY_DETAILS (WDD.TRACKING_NUMBER). WSH_NEW_DELIVERIES has WAYBILL for shipment-level tracking. Use WDD.TRACKING_NUMBER for line-level tracking, WND.WAYBILL for shipment-level.
27. NEVER reference a column on a table unless that column is explicitly listed in the schema above. For tables listed only in the "ADDITIONAL TABLES" section (rule 19), ONLY use the key columns listed there. Do NOT guess or assume additional columns exist. If a column you need is not listed, note it as unavailable and suggest alternatives or omit it.
28. BLANKET PURCHASE AGREEMENT (BPA) RELEASES: PO_HEADERS_ALL does NOT have BLANKET_PO_HEADER_ID — that is an EBS-only column. In Fusion Cloud, the link from a release/standard PO back to a BPA is through PO_LINES_ALL.FROM_HEADER_ID (FK to PO_HEADERS_ALL.PO_HEADER_ID of the BPA). Also use PO_LINES_ALL.CONTRACT_ID for Contract PA references. To find releases against a BPA: JOIN PO_LINES_ALL REL_PLA ON BPA.PO_HEADER_ID = REL_PLA.FROM_HEADER_ID, then JOIN PO_HEADERS_ALL REL_PHA ON REL_PLA.PO_HEADER_ID = REL_PHA.PO_HEADER_ID. PHA.AMOUNT_RELEASED tracks the total released amount on the BPA header.
29. AP_INVOICES_ALL does NOT have TERM_DUE_DATE or DUE_DATE — that column is on RA_CUSTOMER_TRX_ALL (AR) not AP. For AP invoice due dates, use AP_PAYMENT_SCHEDULES_ALL (APS): JOIN AP_PAYMENT_SCHEDULES_ALL APS ON AIA.INVOICE_ID = APS.INVOICE_ID. Key cols: DUE_DATE, PAYMENT_NUM, GROSS_AMOUNT, AMOUNT_REMAINING, PAYMENT_STATUS_FLAG. To find overdue AP invoices: APS.DUE_DATE < TRUNC(SYSDATE) AND APS.PAYMENT_STATUS_FLAG IN ('N', 'P').
30. DATE FORMATTING: NEVER use month abbreviations like 'JAN', 'FEB', 'MAR' in TO_DATE or TO_CHAR — these are NLS-dependent and cause ORA-01843 errors. ALWAYS use numeric date formats. For TO_DATE: TO_DATE('2026-01-01', 'YYYY-MM-DD'). For TO_CHAR display: TO_CHAR(date_col, 'YYYY-MM-DD') or TO_CHAR(date_col, 'MM/DD/YYYY'). For relative date filters, prefer TRUNC(SYSDATE) - 90 instead of hardcoded dates. For BI Publisher parameters use :P_DATE_FROM and :P_DATE_TO which are already DATE type — do NOT wrap them in TO_DATE.
31. TIMESTAMP ARITHMETIC: Most Fusion Cloud date columns (CREATION_DATE, LAST_UPDATE_DATE, TRANSACTION_DATE) are TIMESTAMP, not DATE. Subtracting two TIMESTAMPs returns INTERVAL DAY TO SECOND, not a NUMBER — this causes ORA-00932 if used with AVG(), SUM(), or numeric comparisons. ALWAYS cast to DATE first: TRUNC(CAST(timestamp_col AS DATE)) or use EXTRACT(DAY FROM (ts1 - ts2)) to get numeric days. Example: AVG(CAST(RT.TRANSACTION_DATE AS DATE) - CAST(PHA.CREATION_DATE AS DATE)) AS AVG_DAYS.
32. For procurement receiving + inventory queries: receipt quantities come from RCV_TRANSACTIONS.QUANTITY and RCV_SHIPMENT_LINES.QUANTITY_RECEIVED. Item details come from EGP_SYSTEM_ITEMS_B/VL (joined via ITEM_ID or INVENTORY_ITEM_ID + ORGANIZATION_ID). Inventory org names come from INV_ORGANIZATION_DEFINITIONS_V. For UOM on receipts use RSL.UOM_CODE, PLA.UOM_CODE, PLLA.UOM_CODE, or ESI.PRIMARY_UOM_CODE. CRITICAL: In Fusion Cloud, UNIT_OF_MEASURE and UNIT_MEAS_LOOKUP_CODE do NOT exist on any PO or RCV table — those are EBS-only column names. The Fusion Cloud column is always UOM_CODE (VARCHAR2(3)). NEVER write UNIT_OF_MEASURE or UNIT_MEAS_LOOKUP_CODE on any table — these will cause ORA-00904 errors.

## COMMON TABLE ALIASES (from Oracle's own data models):
- PHA / Header = PO_HEADERS_ALL (or PO_HEADERS_DRAFT_ALL for drafts, PO_HEADERS_ARCHIVE_ALL for versioned)
- PLA / Line = PO_LINES_ALL (or PO_LINES_DRAFT_ALL, PO_LINES_ARCHIVE_ALL)
- PLLA / LineLocation = PO_LINE_LOCATIONS_ALL (or PO_LINE_LOCATIONS_DRAFT_ALL, PO_LINE_LOCATIONS_ARCHIVE_ALL)
- PDA / Distribution = PO_DISTRIBUTIONS_ALL (or PO_DISTRIBUTIONS_DRAFT_ALL, PO_DISTRIBUTIONS_ARCHIVE_ALL)
- PAH = PO_ACTION_HISTORY
- PS / Supplier = POZ_SUPPLIERS
- HP / SupplierPartyName = HZ_PARTIES (for supplier name via PS.PARTY_ID = HP.PARTY_ID)
- ESI / Item = EGP_SYSTEM_ITEMS_VL or EGP_SYSTEM_ITEMS_B (item master; use INVENTORY_ITEM_ID to join)
- GCC = GL_CODE_COMBINATIONS
- RT = RCV_TRANSACTIONS

## ADDITIONAL REFERENCE TABLES (from Oracle's production data models):
- POZ_SUPPLIER_SITES_ALL_M (PozSupplierSite): Supplier sites. Join: Header.VENDOR_SITE_ID = PozSupplierSite.VENDOR_SITE_ID
- POZ_SUPPLIER_CONTACTS (SupplierContact): Supplier contacts. Join: Header.VENDOR_CONTACT_ID = SupplierContact.VENDOR_CONTACT_ID, SupplierContact.PER_PARTY_ID = HZ_PARTIES.PARTY_ID for contact name
- POZ_SUPPLIER_ADDRESS_V: Supplier address view. Join via PARTY_ID to HZ_PARTIES
- HR_LOCATIONS_ALL_F_VL: Locations (ship-to, bill-to, deliver-to). Date-effective: TRUNC(SYSDATE) BETWEEN EFFECTIVE_START_DATE AND EFFECTIVE_END_DATE. Key cols: LOCATION_ID, LOCATION_NAME, ADDRESS_LINE_1 thru 4, TOWN_OR_CITY, REGION_1, REGION_2, COUNTRY, POSTAL_CODE, BUILDING, FLOOR_NUMBER
- HR_ORGANIZATION_V: Business Units / Orgs. Date-effective. Key cols: ORGANIZATION_ID, CLASSIFICATION_CODE = 'FUN_BUSINESS_UNIT'. TRUNC(SYSDATE) BETWEEN EFFECTIVE_START_DATE AND EFFECTIVE_END_DATE
- HR_ORGANIZATION_UNITS_F_TL: Org translations for BU names
- AP_TERMS_VL (PaymentTerms): Payment terms. Join: Header.TERMS_ID = PaymentTerms.TERM_ID. Key col: NAME
- FND_LOOKUPS: General lookup values. Join: lookup_code column = FND_LOOKUPS.LOOKUP_CODE AND FND_LOOKUPS.LOOKUP_TYPE = '<type>'. Key col: MEANING (display value)
- FND_CURRENCIES_VL (Currency): Currency info. Join: Header.CURRENCY_CODE = Currency.CURRENCY_CODE
- WSH_CARRIERS (Carrier): Carriers. Join: Header.CARRIER_ID = Carrier.CARRIER_ID, then Carrier.CARRIER_ID = HZ_PARTIES.PARTY_ID for carrier name
- INV_UNITS_OF_MEASURE_VL: UOM display. Join: UOM_CODE. Key col: UNIT_OF_MEASURE (display name)
- PO_LINE_TYPES_VL (LineType): Line types. Join: Line.LINE_TYPE_ID = LineType.LINE_TYPE_ID. Key col: LINE_TYPE
- PO_DOC_STYLE_LINES_VL (DocStyle): Document styles. Join: Header.STYLE_ID = DocStyle.STYLE_ID AND Header.TYPE_LOOKUP_CODE = DocStyle.DOCUMENT_SUBTYPE. Key col: DISPLAY_NAME
- PO_VERSIONS (Version): PO version tracking. Join: Header.PO_HEADER_ID = Version.PO_HEADER_ID. Key cols: REVISION_NUM, CO_SEQUENCE, CO_NUM, CHANGE_ORDER_DESC, CHANGE_ORDER_TYPE
- EGP_CATEGORIES_VL (Category): Item categories. Join: Line.CATEGORY_ID = Category.CATEGORY_ID
- PO_HAZARD_CLASSES_VL: Hazard classes. Join: Line.HAZARD_CLASS_ID = HazardClass.HAZARD_CLASS_ID
- PO_UN_NUMBERS_VL: UN numbers. Join: Line.UN_NUMBER_ID = UnNumber.UN_NUMBER_ID
- XLE_ENTITY_PROFILES (SoldToLe): Legal entities. Join: Header.SOLDTO_LE_ID = SoldToLe.LEGAL_ENTITY_ID. Key col: NAME
- XLE_REGISTRATIONS: LE tax registrations. Join: SoldToLe.LEGAL_ENTITY_ID = XLE_REGISTRATIONS.SOURCE_ID AND SOURCE_TABLE = 'XLE_ENTITY_PROFILES' AND IDENTIFYING_FLAG = 'Y'
- PER_PERSON_NAMES_F_V (PersonName): Person/employee names. Join via PERSON_ID. Date-effective. Key col: DISPLAY_NAME
- PER_EMAIL_ADDRESSES: Person email. Join: PERSON_ID + PRIMARY_EMAIL_ID = EMAIL_ADDRESS_ID. Key col: EMAIL_ADDRESS
- PER_DISPLAY_PHONES_V: Person phone. Join: PERSON_ID + PRIMARY_PHONE_ID = PHONE_ID. Key col: DISPLAY_PHONE_NUMBER
- PO_SYSTEM_PARAMETERS_ALL: System params per BU. Join: Header.PRC_BU_ID = PO_SYSTEM_PARAMETERS_ALL.PRC_BU_ID. Key col: INVENTORY_ORGANIZATION_ID
- PO_BIP_HELPER: Oracle PL/SQL package with helper functions for BI Publisher (get_doc_revision_number, format_price, get_supplier_contact_info, get_requester_name, etc.)
- GMS_AWARD_HEADERS_INFO_V: Grants/awards. Join: contract_id = Distribution.PJC_CONTRACT_ID

## COMMON JOINS (from Oracle's actual production data models):
- PO to Supplier: POZ_SUPPLIERS Supplier -> Supplier.VENDOR_ID = Header.VENDOR_ID(+), then Supplier.PARTY_ID = SupplierPartyName.PARTY_ID(+)
- Supplier to Name: HZ_PARTIES SupplierPartyName -> Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (SupplierPartyName.PARTY_NAME = supplier name)
- Supplier Site: POZ_SUPPLIER_SITES_ALL_M PozSupplierSite -> Header.VENDOR_SITE_ID = PozSupplierSite.VENDOR_SITE_ID(+)
- Supplier Contact: POZ_SUPPLIER_CONTACTS SupplierContact -> Header.VENDOR_CONTACT_ID = SupplierContact.VENDOR_CONTACT_ID(+), then SupplierContact.PER_PARTY_ID = HZ_PARTIES.PARTY_ID(+) for contact name
- PO to Lines: Header.PO_HEADER_ID = Line.PO_HEADER_ID
- Lines to Schedules: Line.PO_LINE_ID = LineLocation.PO_LINE_ID
- Schedules to Distributions: LineLocation.LINE_LOCATION_ID = Distribution.LINE_LOCATION_ID
- Line to Item: Line.ITEM_ID = Item.INVENTORY_ITEM_ID(+) (NOTE: For org-specific item, also need NVL(Item.ORGANIZATION_ID, PO_SYSTEM_PARAMETERS_ALL.INVENTORY_ORGANIZATION_ID))
- Line to Category: Line.CATEGORY_ID = CategoryPEO.CATEGORY_ID(+)
- Distribution to GL Account: Distribution.CODE_COMBINATION_ID = GCC.CODE_COMBINATION_ID
- PO to Approval History: Header.PO_HEADER_ID = PAH.OBJECT_ID (with PAH.OBJECT_TYPE_CODE = 'PO')
- Buyer/Agent Name: Header.AGENT_ID = PersonName.PERSON_ID(+) AND TRUNC(SYSDATE) BETWEEN PersonName.EFFECTIVE_START_DATE(+) AND PersonName.EFFECTIVE_END_DATE(+)
- Ship-to Location: Header/LineLocation.SHIP_TO_LOCATION_ID = ShipToLoc.LOCATION_ID(+) AND TRUNC(SYSDATE) BETWEEN ShipToLoc.EFFECTIVE_START_DATE(+) AND ShipToLoc.EFFECTIVE_END_DATE(+)
- Bill-to Location: Header.BILL_TO_LOCATION_ID = BillToLoc.LOCATION_ID(+) AND TRUNC(SYSDATE) BETWEEN BillToLoc.EFFECTIVE_START_DATE(+) AND BillToLoc.EFFECTIVE_END_DATE(+)
- Payment Terms: Header.TERMS_ID = PaymentTerms.TERM_ID(+)
- Carrier: Header.CARRIER_ID = Carrier.CARRIER_ID(+), then Carrier.CARRIER_ID = CarrierPartyName.PARTY_ID(+)
- Business Unit: Header.PRC_BU_ID = ProcurementBu.ORGANIZATION_ID(+) AND TRUNC(SYSDATE) BETWEEN ProcurementBu.EFFECTIVE_START_DATE(+) AND ProcurementBu.EFFECTIVE_END_DATE(+) AND ProcurementBu.CLASSIFICATION_CODE(+) = 'FUN_BUSINESS_UNIT'
- Legal Entity: Header.SOLDTO_LE_ID = SoldToLe.LEGAL_ENTITY_ID
- Line Type: Line.LINE_TYPE_ID = LineType.LINE_TYPE_ID
- UOM Display: Line.UOM_CODE = INV_UNITS_OF_MEASURE_VL.UOM_CODE(+) -> INV_UNITS_OF_MEASURE_VL.UNIT_OF_MEASURE for display name (NOTE: UNIT_OF_MEASURE only exists on INV_UNITS_OF_MEASURE_VL lookup table, NOT on PO/RCV tables)
- Deliver-to Person: Distribution.DELIVER_TO_PERSON_ID = Requester.PERSON_ID(+) AND TRUNC(SYSDATE) BETWEEN Requester.EFFECTIVE_START_DATE(+) AND Requester.EFFECTIVE_END_DATE(+)
- Deliver-to Location: Distribution.DELIVER_TO_LOCATION_ID = DeliverToLocation.LOCATION_ID(+) AND TRUNC(SYSDATE) BETWEEN DeliverToLocation.EFFECTIVE_START_DATE(+) AND DeliverToLocation.EFFECTIVE_END_DATE(+)
- FND Lookup Display: column_value = FND_LOOKUPS.LOOKUP_CODE(+) AND FND_LOOKUPS.LOOKUP_TYPE(+) = 'LOOKUP_TYPE_NAME' -> FND_LOOKUPS.MEANING for display

## IMPORTANT DATE-EFFECTIVE TABLES:
These tables require date-effective filters: TRUNC(SYSDATE) BETWEEN table.EFFECTIVE_START_DATE(+) AND table.EFFECTIVE_END_DATE(+)
- HR_LOCATIONS_ALL_F_VL
- HR_ORGANIZATION_V
- PER_PERSON_NAMES_F_V
- PER_ALL_PEOPLE_F
- PER_ALL_ASSIGNMENTS_M

## ORDER MANAGEMENT (DOO) JOINS:
- Order to Lines: DOO_HEADERS_ALL.HEADER_ID = DOO_LINES_ALL.HEADER_ID
- Order to Customer Name: DOO_HEADERS_ALL.SOLD_TO_PARTY_ID = HZ_PARTIES.PARTY_ID
- Order Line to Item: DOO_LINES_ALL.INVENTORY_ITEM_ID = EGP_SYSTEM_ITEMS_VL.INVENTORY_ITEM_ID(+)
- Common aliases: OH = DOO_HEADERS_ALL, OL = DOO_LINES_ALL

## SHIPPING (WSH) JOINS:
- Delivery to Lines: WSH_DELIVERY_DETAILS.DELIVERY_DETAIL_ID = WSH_DELIVERY_ASSIGNMENTS.DELIVERY_DETAIL_ID, WSH_NEW_DELIVERIES.DELIVERY_ID = WSH_DELIVERY_ASSIGNMENTS.DELIVERY_ID
- OM Order to Shipment Lines: DOO_HEADERS_ALL.HEADER_ID = WSH_DELIVERY_DETAILS.SOURCE_HEADER_ID, DOO_LINES_ALL.LINE_ID = WSH_DELIVERY_DETAILS.SOURCE_LINE_ID
- WSH_DELIVERY_DETAILS has SOURCE_HEADER_NUMBER and SOURCE_LINE_NUMBER for user-visible order/line numbers
- Carrier Name: WSH_NEW_DELIVERIES.CARRIER_ID = HZ_PARTIES.PARTY_ID(+)
- Common aliases: WND = WSH_NEW_DELIVERIES, WDD = WSH_DELIVERY_DETAILS, WDA = WSH_DELIVERY_ASSIGNMENTS

## ACCOUNTS PAYABLE (AP) JOINS:
- Invoice to Lines: AP_INVOICES_ALL.INVOICE_ID = AP_INVOICE_LINES_ALL.INVOICE_ID
- Invoice to Supplier: AP_INVOICES_ALL.VENDOR_ID = POZ_SUPPLIERS.VENDOR_ID, POZ_SUPPLIERS.PARTY_ID = HZ_PARTIES.PARTY_ID
- Invoice Line to PO: AP_INVOICE_LINES_ALL.PO_HEADER_ID = PO_HEADERS_ALL.PO_HEADER_ID(+), .PO_LINE_ID = PO_LINES_ALL.PO_LINE_ID(+), .PO_LINE_LOCATION_ID = PO_LINE_LOCATIONS_ALL.LINE_LOCATION_ID(+), .PO_DISTRIBUTION_ID = PO_DISTRIBUTIONS_ALL.PO_DISTRIBUTION_ID(+)
- Invoice to Payment Terms: AP_INVOICES_ALL.TERMS_ID = AP_TERMS_VL.TERM_ID(+)
- Common aliases: AI = AP_INVOICES_ALL, AIL = AP_INVOICE_LINES_ALL

## ACCOUNTS RECEIVABLE (AR) JOINS:
- Transaction to Lines: RA_CUSTOMER_TRX_ALL.CUSTOMER_TRX_ID = RA_CUSTOMER_TRX_LINES_ALL.CUSTOMER_TRX_ID
- Customer Name: RA_CUSTOMER_TRX_ALL.BILL_TO_CUSTOMER_ID = HZ_CUST_ACCOUNTS.CUST_ACCOUNT_ID, HZ_CUST_ACCOUNTS.PARTY_ID = HZ_PARTIES.PARTY_ID
- Credit memo to source: RA_CUSTOMER_TRX_LINES_ALL.PREVIOUS_CUSTOMER_TRX_ID = RA_CUSTOMER_TRX_ALL.CUSTOMER_TRX_ID
- Common aliases: RCT = RA_CUSTOMER_TRX_ALL, RCTL = RA_CUSTOMER_TRX_LINES_ALL

## CROSS-MODULE JOINS (OM -> Shipping -> Financials):
- Sales Order -> Shipment: DOO_LINES_ALL.LINE_ID = WSH_DELIVERY_DETAILS.SOURCE_LINE_ID
- PO -> AP Invoice: PO_HEADERS_ALL.PO_HEADER_ID = AP_INVOICE_LINES_ALL.PO_HEADER_ID
- AR Invoice -> Customer PO: RA_CUSTOMER_TRX_ALL.PURCHASE_ORDER contains the customer PO number (text field, not FK)

## SHIPPER / BILL OF LADING DATA MODEL (from LSB production customizations):
### Background
When creating a custom Shipper data model in BI Catalog, copy the seeded data model from the Supply Chain folder into the Custom folder. The seeded model provides ~95% of fields from a master table. Additional fields (DFFs, EFFs, line-level notes, content server notes, VMR info, route code, drop ship address) require custom joins.

### G_9 - Mini Master Table for Shipper
A secondary lookup table built from OM/Shipping tables to provide join keys for additional modules (work orders, transfer orders, content server notes, etc.).
Key tables and joins:
- DOO_HEADERS_ALL (DHA) -> DOO_LINES_ALL (DLA): DHA.HEADER_ID = DLA.HEADER_ID
- DOO_LINES_ALL (DLA) -> DOO_FULFILL_LINES_ALL (DFLA): DLA.LINE_ID = DFLA.LINE_ID
- DOO_FULFILL_LINES_ALL (DFLA) -> WSH_DELIVERY_DETAILS (WDD): WDD.SALES_ORDER_NUMBER = DHA.ORDER_NUMBER AND DFLA.FULFILL_LINE_ID = WDD.SOURCE_SHIPMENT_ID
- WSH_DELIVERY_DETAILS (WDD) -> WSH_DELIVERY_ASSIGNMENTS (WDA): WDA.DELIVERY_DETAIL_ID = WDD.DELIVERY_DETAIL_ID
- WSH_DELIVERY_DETAILS (WDD) -> INV_LICENSE_PLATE_NUMBERS (ILPN): WDD.PARENT_LPN_ID = ILPN.LPN_ID (for License Plate Numbers / carton labels)
Key fields from G_9: ORDER_NUMBER, HEADER_ID, LINE_ID, LINE_NUMBER, FULFILL_LINE_NUMBER, FULFILL_LINE_ID, INVENTORY_ITEM_ID, DELIVERY_DETAIL_ID, ORDER_TYPE_CODE, STATUS_CODE, LICENSE_PLATE_NUMBER, TRACKING_NUMBER, DELIVERY_ID, SHIP_METHOD_CODE
Filter: DHA.STATUS_CODE NOT IN ('DOO_DRAFT', 'DOO_REFERENCE', 'DOO_CREDIT_REVIEW_PENDING')

### Work Order Join (from Shipper)
Links sales order lines to manufacturing work orders via the supply chain module.
Join chain: DOO_HEADERS_ALL -> DOO_LINES_ALL -> DOO_FULFILL_LINES_ALL -> DOS_SUPPLY_HEADERS (DSH.SUPPLY_ORDER_REFERENCE_ID = DFLA.HEADER_ID AND DSH.INTERFACE_SOURCE_CODE = 'DOO') -> DOS_SUPPLY_LINES (DSL.HEADER_ID = DSH.HEADER_ID AND DSL.SUPPLY_ORDER_REFERENCE_LINE_ID = DFLA.FULFILL_LINE_ID) -> DOS_SUPPLY_TRACKING_LINES (DSTL.LINE_ID = DSL.LINE_ID AND DSTL.HEADER_ID = DSL.HEADER_ID) -> DOS_SUPPLY_MAKE_ORDER_DTLS (DSBOD.TRACKING_LINE_ID = DSTL.TRACKING_LINE_ID)
Key field: DSBOD.WORK_ORDER_NUMBER (alias WO_LINE)
Tables:
- DOS_SUPPLY_HEADERS (DSH): Supply order headers. Join: DSH.SUPPLY_ORDER_REFERENCE_ID = DFLA.HEADER_ID AND DSH.INTERFACE_SOURCE_CODE = 'DOO'. Key cols: HEADER_ID, SUPPLY_ORDER_REFERENCE_ID, INTERFACE_SOURCE_CODE
- DOS_SUPPLY_LINES (DSL): Supply order lines. Join: DSL.HEADER_ID = DSH.HEADER_ID AND DSL.SUPPLY_ORDER_REFERENCE_LINE_ID = DFLA.FULFILL_LINE_ID. Key cols: LINE_ID, HEADER_ID, SUPPLY_ORDER_REFERENCE_LINE_ID
- DOS_SUPPLY_TRACKING_LINES (DSTL): Supply tracking. Join: DSTL.LINE_ID = DSL.LINE_ID AND DSTL.HEADER_ID = DSL.HEADER_ID. Key col: TRACKING_LINE_ID
- DOS_SUPPLY_MAKE_ORDER_DTLS (DSBOD): Work order details. Join: DSBOD.TRACKING_LINE_ID = DSTL.TRACKING_LINE_ID. Key col: WORK_ORDER_NUMBER

### Transfer Order Tables (for Shipper)
Transfer orders are in the SCM module (not OM). Used when LSB requires TO data on the Shipper document.
Key tables:
- INV_TRANSFER_ORDER_HEADERS (TOH): Transfer order headers. Key cols: HEADER_ID, HEADER_NUMBER
- INV_TRANSFER_ORDER_LINES (TOL): Transfer order lines. Key cols: HEADER_ID, LINE_NUMBER, QTY_UOM_CODE, REQUESTED_QTY, DESTINATION_ORGANIZATION_ID, ORIGINAL_REQUEST_LINE_ID
Join chain: WSH_DELIVERY_DETAILS (WDD) -> INV_TRANSFER_ORDER_HEADERS (TOH.HEADER_NUMBER = WDD.SALES_ORDER_NUMBER) -> INV_TRANSFER_ORDER_LINES (TOL.HEADER_ID = TOH.HEADER_ID)
- TOL -> DOO_FULFILL_LINES_ALL: TOL.ORIGINAL_REQUEST_LINE_ID = DFLA.FULFILL_LINE_ID (for source order number)
- TOL -> EGO_ITEM_EFF_B: A.INVENTORY_ITEM_ID = WDD.INVENTORY_ITEM_ID (for extensible flexfields like custom attributes)
- EGO_ITEM_EFF_B -> FND_VS_VALUES_VL: A.ATTRIBUTE_CHAR10 = B.VALUE (for attribute descriptions)
- TOL -> HR_ALL_ORGANIZATION_UNITS_TL (HAOT): HAOT.ORGANIZATION_ID = TOL.DESTINATION_ORGANIZATION_ID (for destination org name)
Use CASE WHEN WDD.SOURCE_LINE_TYPE = 'TRANSFER_ORDER' THEN 'TO' ELSE WDD.SOURCE_LINE_TYPE END to identify transfer order lines.

### Content Server Notes Connection (for Shipper)
Brings in line-level notes stored in Oracle Content Server via the attachments framework.
Join chain: G_9.FULFILL_LINE_ID -> FND_ATTACHED_DOCUMENTS.PK1_VALUE (where ENTITY_NAME = 'DOO_FULFILL_LINES_ALL') -> FND_DOCUMENTS_TL (FAD.DOCUMENT_ID = FDT.DOCUMENT_ID)
Key fields: FAD.PK1_VALUE (maps to FULFILL_LINE_ID), FDT.DM_VERSION_NUMBER
For header-level notes, the process is similar but uses the header-level entity name.
In the BI Catalog data model editor, after setting up the bridge query (G_10), use the "+" button and choose "Content Server" to connect the document content.

### Additional Shipper Tables:
- INV_LICENSE_PLATE_NUMBERS (ILPN): License plate / carton numbers. Join: WDD.PARENT_LPN_ID = ILPN.LPN_ID. Key col: LICENSE_PLATE_NUMBER
- EGO_ITEM_EFF_B: Item extensible flexfields. Join: INVENTORY_ITEM_ID. Key cols: CONTEXT_CODE, ATTRIBUTE_CHAR1-20. Filter by CONTEXT_CODE for specific EFF contexts (e.g., 'LaSalleBristolAttributes')
- HR_ALL_ORGANIZATION_UNITS_TL (HAOT): Organization names (translatable). Join: ORGANIZATION_ID. Key col: NAME

## TABLE SCHEMAS:
"""

    # Add detailed schemas for ALL modules
    for table_name, table_def in COMBINED_TABLES.items():
        desc = table_def.get("description", "")
        if isinstance(desc, tuple):
            desc = " ".join(desc)
        pk = table_def.get("primary_key", "N/A")
        if isinstance(pk, list):
            pk = ", ".join(pk)
        cols = table_def.get("columns") or table_def.get("key_columns") or {}
        schema_text += f"\n### {table_name}\n{desc}\nPK: {pk}\nKey columns:\n"
        for col_name, col_info in cols.items():
            # Only include non-DFF columns in prompt to save tokens
            if not col_name.startswith(("ATTRIBUTE", "GLOBAL_ATTRIBUTE", "SH_ATTRIBUTE")):
                schema_text += f"  - {col_name} ({col_info['type']}): {col_info.get('desc', '')}\n"

    schema_text += "\n## LOOKUP VALUES:\n"
    for lookup_name, values in COMBINED_LOOKUPS.items():
        schema_text += f"\n{lookup_name}:\n"
        for val in values:
            schema_text += f"  - {val}\n"

    schema_text += """
## OUTPUT FORMAT:
- Return ONLY the SQL query inside a sql code block
- Add brief inline comments for non-obvious joins or filters
- After the SQL, add a short "Tables Used" summary
- If the user's request is ambiguous, state your assumptions
- If BI Publisher parameters would be useful, include them with :P_ prefix and note them
"""
    return schema_text


# ---------------------------------------------------------------------------
# Excel / CSV file parsing helper
# ---------------------------------------------------------------------------
def parse_uploaded_file(uploaded_file):
    """Parse an uploaded Excel or CSV file and return a summary for Claude."""
    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    try:
        if ext == ".csv":
            df = pd.read_csv(uploaded_file)
        else:
            # Try reading all sheets
            xls = pd.ExcelFile(uploaded_file)
            sheets_info = []
            for sheet_name in xls.sheet_names:
                sheet_df = pd.read_excel(xls, sheet_name=sheet_name)
                if sheet_df.empty:
                    continue
                sheets_info.append((sheet_name, sheet_df))
            if not sheets_info:
                return None, "The uploaded file has no data."
            # Use first non-empty sheet as primary, but describe all
            df = sheets_info[0][1]
            if len(sheets_info) > 1:
                multi_sheet_note = f"\n\nFile has {len(sheets_info)} sheets: {', '.join(s[0] for s in sheets_info)}. Primary sheet: '{sheets_info[0][0]}'"
            else:
                multi_sheet_note = ""
    except Exception as e:
        return None, f"Could not read file: {e}"

    # Build column summary
    col_details = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        total = len(df)
        sample_vals = df[col].dropna().head(5).tolist()
        sample_str = ", ".join(str(v) for v in sample_vals)
        col_details.append(
            f"  - {col} (dtype: {dtype}, {non_null}/{total} non-null) — samples: [{sample_str}]"
        )

    summary = (
        f"## Attached Report: {file_name}\n"
        f"Rows: {len(df)} | Columns: {len(df.columns)}\n\n"
        f"### Columns:\n" + "\n".join(col_details)
    )
    if ext != ".csv" and 'multi_sheet_note' in dir() and multi_sheet_note:
        summary += multi_sheet_note

    return df, summary


# ---------------------------------------------------------------------------
# Claude API call
# ---------------------------------------------------------------------------
def generate_sql(user_prompt, api_key_val):
    """Call Claude API to generate SQL from natural language."""
    client = anthropic.Anthropic(api_key=api_key_val)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# ofjdbc - Live Fusion query execution
# ---------------------------------------------------------------------------
def get_jdbc_jar_path():
    """Return the path to the ofjdbc JAR file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "orfujdbc-1.0-SNAPSHOT.jar")


def run_fusion_query(sql, host, username, password, report_path, max_rows=100):
    """Execute a SQL query against Oracle Fusion via ofjdbc JDBC driver.
    Returns a pandas DataFrame with results."""
    jar_path = get_jdbc_jar_path()
    if not os.path.exists(jar_path):
        raise FileNotFoundError(f"ofjdbc JAR not found at: {jar_path}")

    driver_class = "my.jdbc.wsdl_driver.WsdlDriver"
    jdbc_url = f"jdbc:wsdl://{host}/xmlpserver/services/ExternalReportWSSService?WSDL:{report_path}"

    # Start JVM if not already running (requires Java 9+)
    java_home = os.getenv("JAVA_HOME", r"C:\Program Files\Eclipse Adoptium\jdk-21.0.10.7-hotspot")
    jvm_path = os.path.join(java_home, "bin", "server", "jvm.dll")
    if not os.path.exists(jvm_path):
        jvm_path = jpype.getDefaultJVMPath()

    if not jpype.isJVMStarted():
        jpype.startJVM(
            jvm_path,
            f"-Djava.class.path={jar_path}",
            "-ea",
        )

    connection = None
    cursor = None
    try:
        connection = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [username, password],
            jar_path,
        )
        cursor = connection.cursor()

        # Add row limit if not already present
        sql_trimmed = sql.strip().rstrip(";")
        if "FETCH" not in sql_trimmed.upper():
            sql_trimmed += f" FETCH FIRST {max_rows} ROWS ONLY"

        cursor.execute(sql_trimmed)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
# Schema provenance — bump these when the table definitions are re-verified
# against a newer Oracle Fusion "Tables and Views" release.
SCHEMA_ORACLE_RELEASE = "26B"
SCHEMA_LAST_UPDATED = "2026-06-01"

# Header with logo
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    st.image("terillium_logo.png", width=100)
with header_col2:
    st.title("BI Publisher SQL Query Builder")
    st.caption("Oracle Fusion Cloud - Procurement | Suppliers | Items | Order Management | Shipping | Financials (AP/AR)")
    st.caption(
        f"📅 Data tables verified against Oracle Fusion **{SCHEMA_ORACLE_RELEASE}** "
        f"· last updated {SCHEMA_LAST_UPDATED}"
    )

# ---------------------------------------------------------------------------
# BI Publisher Data Source Configuration
# ---------------------------------------------------------------------------
with st.container(border=True):
    ds_col1, ds_col2, ds_col3 = st.columns([2, 2, 3])
    with ds_col1:
        st.markdown("**\\* Data Source**")
        st.code("ApplicationDB_FSCM", language=None)
    with ds_col2:
        st.markdown("**\\* Type of SQL**")
        st.code("Standard SQL", language=None)
    with ds_col3:
        st.markdown("**Modules Covered**")
        st.markdown("Procurement | Suppliers | Items | Requisitions | AP | AR | OM | Shipping | Payments | Cash")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Query Generator", "📝 Example Queries", "📖 Quick Reference", "📚 Catalog Library", "🗂️ Schema Explorer"])

# ---- TAB 1: AI Generator ----
with tab1:
    st.subheader("Describe the report you need")

    # Quick prompt templates
    quick_prompts = {
        "-- Select a template --": "",
        "PO listing with supplier": "List all approved purchase orders with PO number, supplier name, creation date, and total amount",
        "PO lines with items": "Show PO number, line number, item number, item description, quantity, unit price, and line amount for all standard POs",
        "Open POs pending receipt": "Find all approved PO lines where the quantity received is less than the quantity ordered, show PO number, line, item, ordered qty, received qty, and need-by date",
        "PO approval history": "Show the full approval history for purchase orders including approver name, action taken, action date, and any notes",
        "PO distributions with GL": "List PO distributions with the charge account (GL code combination segments), ordered/delivered/billed quantities",
        "Blanket agreement utilization": "Show blanket purchase agreements with their agreed amount, amount released, remaining balance, and expiration date",
        "POs by date range (parameterized)": "Create a parameterized report showing POs created between two dates with supplier name, PO amount, and status. Use BI Publisher parameters for the date range and business unit.",
        "PO shipments with receiving": "Show PO shipments with scheduled delivery dates, actual receipt dates, and quantities for on-time delivery analysis",
        "--- Order Management ---": "",
        "Sales orders with customer": "List all open sales orders with order number, customer name, ordered date, currency, and status",
        "Sales order lines with items": "Show sales order lines with item number, description, ordered quantity, unit price, extended amount, and scheduled ship date",
        "--- Shipping ---": "",
        "Shipments with tracking": "Show all shipments with delivery name, tracking/waybill number, carrier, ship date, delivery date, and weight",
        "OM orders to shipment lines": "Join sales order headers and lines to shipping delivery details showing order number, line, item, ordered qty vs shipped qty, and tracking number",
        "--- Financials ---": "",
        "AP invoices by supplier": "List all AP invoices with invoice number, date, supplier name, amount, currency, payment status, and PO number if matched",
        "AP invoice lines matched to PO": "Show AP invoice lines that are matched to purchase orders with the PO number, PO line, quantity invoiced, unit price, and amount",
        "AR invoices by customer": "List AR transactions with transaction number, date, customer name, amount, currency, and status",
    }

    selected_template = st.selectbox("Quick templates", options=list(quick_prompts.keys()))

    user_input = st.text_area(
        "Describe your report in plain English:",
        value=quick_prompts.get(selected_template, ""),
        height=120,
        placeholder="e.g., Show me all approved POs from last month with supplier name, item details, and total line amounts...",
    )

    # File upload for existing client reports
    st.markdown("---")
    st.markdown("**Attach a client report to reverse-engineer the SQL**")
    uploaded_file = st.file_uploader(
        "Upload an Excel or CSV file",
        type=["xlsx", "xls", "csv"],
        help="Upload a client's existing report (Excel/CSV). The app will analyze the columns and sample data to generate matching SQL from Oracle Fusion tables.",
    )

    file_summary = None
    if uploaded_file is not None:
        df_preview, file_summary = parse_uploaded_file(uploaded_file)
        if df_preview is not None:
            with st.expander(f"Preview: {uploaded_file.name} ({len(df_preview)} rows, {len(df_preview.columns)} cols)", expanded=True):
                st.dataframe(df_preview.head(20), width="stretch")
        else:
            st.error(file_summary)
            file_summary = None

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("🚀 Generate SQL", type="primary", width="stretch")

    if generate_btn:
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
        elif not user_input.strip() and not file_summary:
            st.warning("Please describe the report you need or attach a file.")
        else:
            # Build the full prompt
            full_prompt = ""
            if use_catalog_rag and catalogs:
                full_prompt += build_catalog_context(catalogs) + "\n\n"
            if file_summary:
                full_prompt += (
                    "The user has attached an existing client report (Excel/CSV). "
                    "Analyze the column names, data types, and sample values below to determine "
                    "which Oracle Fusion Cloud tables and columns can produce this report. "
                    "Generate a BI Publisher SQL query that recreates this report from the Fusion schema. "
                    "Map each spreadsheet column to the appropriate Fusion table.column, and note any columns "
                    "that cannot be mapped.\n\n"
                    f"{file_summary}\n\n"
                )
            if user_input.strip():
                full_prompt += f"Additional instructions: {user_input.strip()}\n"
            elif file_summary:
                full_prompt += "Generate the SQL to recreate this report from Oracle Fusion Cloud tables.\n"

            with st.spinner("Claude is writing your SQL query..."):
                try:
                    result = generate_sql(full_prompt, api_key)
                    st.session_state["last_result"] = result
                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Display result
    if "last_result" in st.session_state:
        st.divider()
        st.subheader("Generated SQL")
        st.markdown(st.session_state["last_result"])

        # Extract just the SQL for copy
        result_text = st.session_state["last_result"]
        sql_start = result_text.find("```sql")
        sql_end = result_text.find("```", sql_start + 6) if sql_start != -1 else -1
        if sql_start != -1 and sql_end != -1:
            clean_sql = result_text[sql_start + 6:sql_end].strip()

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                st.download_button(
                    "💾 Download SQL",
                    data=clean_sql,
                    file_name="bi_publisher_query.sql",
                    mime="text/plain",
                )
            with btn_col2:
                if st.session_state.get("fusion_connected"):
                    test_btn = st.button("⚡ Test on Fusion", type="secondary", width="stretch")
                else:
                    test_btn = st.button("⚡ Test on Fusion", type="secondary", width="stretch", disabled=True,
                                         help="Enter Fusion credentials in the sidebar to enable.")

            if st.session_state.get("fusion_connected") and test_btn:
                max_rows = st.session_state.get("fusion_max_rows", 100)
                with st.spinner(f"Running query on Fusion (max {max_rows} rows)..."):
                    try:
                        df_result = run_fusion_query(
                            clean_sql,
                            st.session_state["fusion_host"],
                            st.session_state["fusion_user"],
                            st.session_state["fusion_pass"],
                            st.session_state["fusion_report_path"],
                            max_rows=max_rows,
                        )
                        st.session_state["fusion_result"] = df_result
                    except Exception as e:
                        st.error(f"Fusion query error: {e}")

            # Show live results if available
            if "fusion_result" in st.session_state:
                st.divider()
                st.subheader("Live Fusion Results")
                df_result = st.session_state["fusion_result"]
                st.caption(f"{len(df_result)} rows returned")
                st.dataframe(df_result, width="stretch")

                # Download results as CSV
                csv_data = df_result.to_csv(index=False)
                st.download_button(
                    "💾 Download Results (CSV)",
                    data=csv_data,
                    file_name="fusion_query_results.csv",
                    mime="text/csv",
                    key="dl_fusion_csv",
                )


# ---- TAB 2: Examples ----
with tab2:
    st.subheader("Example BI Publisher SQL Queries")
    st.caption("Tested patterns for Oracle Fusion Cloud Procurement")

    for i, example in enumerate(EXAMPLES):
        with st.expander(f"**{example['name']}** - {example['description']}"):
            st.code(example["sql"], language="sql")
            st.download_button(
                f"💾 Download",
                data=example["sql"],
                file_name=f"{example['name'].lower().replace(' ', '_')}.sql",
                mime="text/plain",
                key=f"dl_{i}",
            )


# ---- TAB 3: Quick Reference ----
with tab3:
    st.subheader("Quick Reference")

    ref1, ref2 = st.columns(2)

    with ref1:
        st.markdown("### Core Table Hierarchy")
        st.code("""
PO_HEADERS_ALL (PHA)          -- One row per PO
  └─ PO_LINES_ALL (PLA)       -- One row per PO line
      └─ PO_LINE_LOCATIONS_ALL (PLLA)  -- Shipment schedules
          └─ PO_DISTRIBUTIONS_ALL (PDA) -- Accounting distributions
        """, language="text")

        st.markdown("### Standard Join Pattern")
        st.code("""
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    PO_DISTRIBUTIONS_ALL PDA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PLLA.LINE_LOCATION_ID = PDA.LINE_LOCATION_ID
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
        """, language="sql")

        st.markdown("### BI Publisher Parameters")
        st.code("""
-- Use :P_ prefix for runtime parameters
AND PHA.SEGMENT1 = :P_PO_NUMBER
AND PHA.PRC_BU_ID = :P_BUSINESS_UNIT
AND PHA.CREATION_DATE BETWEEN :P_DATE_FROM AND :P_DATE_TO
AND PHA.DOCUMENT_STATUS = :P_STATUS
AND PHA.TYPE_LOOKUP_CODE = :P_DOC_TYPE
        """, language="sql")

    with ref2:
        st.markdown("### Key Column Reference")
        st.markdown("""
| What you need | Table.Column |
|---|---|
| PO Number | `PHA.SEGMENT1` |
| PO Status | `PHA.DOCUMENT_STATUS` |
| PO Type | `PHA.TYPE_LOOKUP_CODE` |
| Buyer ID | `PHA.AGENT_ID` |
| Supplier ID | `PHA.VENDOR_ID` |
| Supplier Name | `HP.PARTY_NAME` |
| Item Number | `ESI.ITEM_NUMBER` |
| Item Description | `PLA.ITEM_DESCRIPTION` |
| Line Number | `PLA.LINE_NUM` |
| Quantity Ordered | `PLA.QUANTITY` or `PLLA.QUANTITY` |
| Unit Price | `PLA.UNIT_PRICE` |
| Need-by Date | `PLLA.NEED_BY_DATE` |
| Promised Date | `PLLA.PROMISED_DATE` |
| Qty Received | `PLLA.QUANTITY_RECEIVED` |
| Qty Billed | `PLLA.QUANTITY_BILLED` |
| Ship-to Location | `PLLA.SHIP_TO_LOCATION_ID` |
| GL Account | `PDA.CODE_COMBINATION_ID` |
| Destination | `PDA.DESTINATION_TYPE_CODE` |
| Project ID | `PDA.PJC_PROJECT_ID` |
| Approval Action | `PAH.ACTION_CODE` |
| Approver | `PAH.PERFORMER_ID` |
""")

        st.markdown("### Useful Filters")
        st.code("""
-- Only approved POs
AND PHA.DOCUMENT_STATUS = 'APPROVED'

-- Exclude cancelled
AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
AND NVL(PLA.CANCEL_FLAG, 'N') = 'N'

-- Standard POs only
AND PHA.TYPE_LOOKUP_CODE = 'STANDARD'

-- Blanket agreements only
AND PHA.TYPE_LOOKUP_CODE = 'BLANKET'

-- POs created in last 30 days
AND PHA.CREATION_DATE >= SYSDATE - 30

-- Pending receipt (open items)
AND PLLA.QUANTITY > NVL(PLLA.QUANTITY_RECEIVED, 0)

-- Specific business unit
AND PHA.PRC_BU_ID = :P_BU_ID
        """, language="sql")

        st.markdown("### Document Types")
        st.markdown("""
| TYPE_LOOKUP_CODE | Description |
|---|---|
| `STANDARD` | Standard Purchase Order |
| `BLANKET` | Blanket Purchase Agreement |
| `CONTRACT` | Contract Purchase Agreement |
| `PLANNED` | Planned Purchase Order |
""")

    st.divider()
    st.markdown("### 🔔 Pending-Approval / Next-Approver patterns")
    st.caption("PO_ACTION_HISTORY only carries COMPLETED approval actions. To find who a PO is currently sitting with, "
               "join to the BPM workflow tables. Access to WFTASK / HWF_TASKS_B may require extra grants on the BI Publisher data source.")
    for name, sql in WORKFLOW_SQL_PATTERNS.items():
        with st.expander(f"`{name}`"):
            st.code(sql, language="sql")
            st.download_button(
                "💾 Download",
                data=sql,
                file_name=f"{name}.sql",
                mime="text/plain",
                key=f"dl_wf_{name}",
            )


# ---- TAB 4: Catalog Library ----
with tab4:
    st.subheader("📚 BIP Catalog Library")
    st.caption("Existing BI Publisher data models loaded from .xdm.catalog files in the app directory. "
               "Enable the sidebar toggle to inject these as RAG context for Claude.")

    if not catalogs:
        st.info("No .xdm.catalog files found in the app directory.")
    else:
        cat_search = st.text_input("Search catalogs (name or SQL)", key="cat_search")
        for cat in catalogs:
            name = cat["name"]
            desc = cat.get("description", "") or ""
            if cat_search:
                needle = cat_search.lower()
                in_meta = needle in name.lower() or needle in desc.lower()
                in_sql = any(needle in ds["sql"].lower() for ds in cat.get("sql_datasets", []))
                if not (in_meta or in_sql):
                    continue

            n_sql = len(cat.get("sql_datasets", []))
            n_params = len(cat.get("parameters", []))
            label = f"**{name}** — {n_sql} SQL dataset(s), {n_params} parameter(s)"
            if desc:
                label += f"  \n_{desc[:140]}_"

            with st.expander(label):
                if cat.get("error"):
                    st.error(f"Parse error: {cat['error']}")
                    continue
                if cat.get("parameters"):
                    st.markdown("**Parameters:**")
                    for p in cat["parameters"]:
                        default = f" — default: `{p['default']}`" if p.get("default") else ""
                        st.markdown(f"- `:{p['name']}` ({p.get('type','?')}){default}")
                if cat.get("sql_datasets"):
                    for ds in cat["sql_datasets"]:
                        st.markdown(f"**DataSet: `{ds['name']}`**")
                        st.code(ds["sql"], language="sql")
                        st.download_button(
                            "💾 Download SQL",
                            data=ds["sql"],
                            file_name=f"{name.replace('.xdm.catalog','')}_{ds['name']}.sql",
                            mime="text/plain",
                            key=f"dl_cat_{name}_{ds['name']}",
                        )
                else:
                    st.caption("No SQL datasets extracted.")


# ---- TAB 5: Schema Explorer ----
with tab5:
    st.subheader("🗂️ Schema Explorer")
    st.caption(
        "Browse the full data dictionary. Pick a **module**, then a **table or view**, "
        "to see every documented column with its type, nullability, and description — "
        "plus the primary key, indexes, and join relationships."
    )

    # Step 1 & 2 — module then table
    pick_col1, pick_col2 = st.columns([1, 2])
    with pick_col1:
        se_module = st.selectbox(
            "1️⃣ Module",
            options=list(MODULE_PREFIX_MAP.keys()),
            key="se_module",
        )
    se_tables = filter_tables_by_module(se_module)
    with pick_col2:
        if se_tables:
            se_table = st.selectbox(
                f"2️⃣ Table / View — {len(se_tables)} in this module",
                options=sorted(se_tables.keys()),
                key="se_table",
            )
        else:
            se_table = None
            st.info("No tables documented for this module yet.")

    if se_table:
        tbl = COMBINED_TABLES[se_table]
        desc = tbl["description"] if isinstance(tbl.get("description"), str) else " ".join(tbl.get("description", ""))
        cols_dict = tbl.get("columns") or tbl.get("key_columns") or {}

        st.markdown(f"### `{se_table}`")
        st.write(desc)

        # Metadata strip
        pk = tbl.get("primary_key", "—")
        if isinstance(pk, list):
            pk = ", ".join(pk) if pk else "—"
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Columns", len(cols_dict))
        m2.metric("Object", tbl.get("object_type", "TABLE"))
        m3.metric("Schema", tbl.get("schema", "—"))
        m4.metric("Owner", tbl.get("owner", "—"))
        st.markdown(f"**Primary Key:** `{pk}`")

        # Step 3 — columns as a data table
        st.markdown("#### 3️⃣ Columns")
        if cols_dict:
            se_col_search = st.text_input("Filter columns (name or description)", key="se_col_search")
            rows = []
            for cname, cinfo in cols_dict.items():
                if se_col_search:
                    needle = se_col_search.lower()
                    if needle not in cname.lower() and needle not in cinfo.get("desc", "").lower():
                        continue
                nullable_val = cinfo.get("nullable")
                nullable = "NOT NULL" if nullable_val is False else ("NULL" if nullable_val is True else "—")
                rows.append({
                    "Column": cname,
                    "Type": cinfo.get("type", "—"),
                    "Nullable": nullable,
                    "Description": cinfo.get("desc", ""),
                })

            df_cols = pd.DataFrame(rows, columns=["Column", "Type", "Nullable", "Description"])
            st.caption(f"Showing {len(df_cols)} of {len(cols_dict)} columns")
            st.dataframe(
                df_cols,
                width="stretch",
                hide_index=True,
                column_config={
                    "Column": st.column_config.TextColumn("Column", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Nullable": st.column_config.TextColumn("Nullable", width="small"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                },
            )
            st.download_button(
                "💾 Download columns (CSV)",
                data=df_cols.to_csv(index=False),
                file_name=f"{se_table}_columns.csv",
                mime="text/csv",
                key="se_dl_cols",
            )
        else:
            st.info(
                "No column-level detail is documented for this object — it is typically a "
                "view; query the underlying base tables for full column detail."
            )

        # Indexes & relationships
        extra_col1, extra_col2 = st.columns(2)
        with extra_col1:
            if tbl.get("indexes"):
                with st.expander(f"🔑 Indexes ({len(tbl['indexes'])})", expanded=False):
                    for iname, icols in tbl["indexes"].items():
                        st.markdown(f"- **`{iname}`** → `{icols}`")
        with extra_col2:
            if tbl.get("foreign_keys"):
                with st.expander(f"🔗 Foreign keys / joins ({len(tbl['foreign_keys'])})", expanded=False):
                    for fk, fkcols in tbl["foreign_keys"].items():
                        st.markdown(f"- `{fk}` on `{fkcols}`")

        # Related join keys from the relationships map
        related = {k: v for k, v in COMBINED_RELATIONSHIPS.items() if se_table in k}
        if related:
            with st.expander(f"🧭 Documented join keys involving this table ({len(related)})", expanded=False):
                for rel, join in related.items():
                    st.markdown(f"- **{rel}**  \n  `{join}`")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
footer_col1, footer_col2 = st.columns([1, 5])
with footer_col1:
    st.image("terillium_logo.png", width=60)
with footer_col2:
    st.caption(
        f"Terillium - Oracle Fusion Cloud {SCHEMA_ORACLE_RELEASE} | "
        f"{len(COMBINED_TABLES)} tables | 30 example queries | 25 validation rules | "
        f"last updated {SCHEMA_LAST_UPDATED} | Powered by Claude API + ofjdbc"
    )

