"""
Oracle Fusion Cloud Procurement 26B - Supplier Model schema (POZ_*)
Source: Oracle EDM Procurement 26B - Supplier Model section.
Tables: suppliers, sites, addresses, contacts, classifications,
products & services, tax profiles, third-party relationships, notes,
attachments, qualification record ownership.
"""

SUPPLIER_RELATIONSHIPS = {
    "POZ_SUPPLIERS -> HZ_PARTIES (supplier name)":
        "POZ_SUPPLIERS.PARTY_ID = HZ_PARTIES.PARTY_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_SITES_ALL_M":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUPPLIER_SITES_ALL_M.VENDOR_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_CONTACTS":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUPPLIER_CONTACTS.VENDOR_ID",
    "POZ_SUPPLIER_SITES_ALL_M -> POZ_SUPPLIER_ADDRESSES":
        "POZ_SUPPLIER_SITES_ALL_M.SUPPLIER_ADDRESS_ID = POZ_SUPPLIER_ADDRESSES.SUPPLIER_ADDRESS_ID",
    "POZ_SUPPLIER_ADDRESSES -> HZ_LOCATIONS":
        "POZ_SUPPLIER_ADDRESSES.LOCATION_ID = HZ_LOCATIONS.LOCATION_ID",
    "POZ_SUPPLIER_CONTACTS -> HZ_PARTIES (contact name)":
        "POZ_SUPPLIER_CONTACTS.PER_PARTY_ID = HZ_PARTIES.PARTY_ID",
    "POZ_SUPPLIERS -> POZ_BUSINESS_CLASSIFICATIONS":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_BUSINESS_CLASSIFICATIONS.VENDOR_ID",
    "POZ_SUPPLIERS -> POZ_SUP_PRODUCTS_SERVICES":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUP_PRODUCTS_SERVICES.VENDOR_ID",
    "POZ_SUP_PRODUCTS_SERVICES -> POZ_PROD_SERV_CATEGORY_V":
        "POZ_SUP_PRODUCTS_SERVICES.CATEGORY_ID = POZ_PROD_SERV_CATEGORY_V.CATEGORY_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_TAX_PROFILES":
        "POZ_SUPPLIERS.PARTY_ID = POZ_SUPPLIER_TAX_PROFILES.PARTY_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_NOTES":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUPPLIER_NOTES.VENDOR_ID",
    "POZ_SUPPLIER_SITES_ALL_M -> POZ_SUP_THIRDPARTY_PAYMENT_REL":
        "POZ_SUPPLIER_SITES_ALL_M.VENDOR_SITE_ID = POZ_SUP_THIRDPARTY_PAYMENT_REL.VENDOR_SITE_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIERS":
        "PO_HEADERS_ALL.VENDOR_ID = POZ_SUPPLIERS.VENDOR_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIER_SITES_ALL_M":
        "PO_HEADERS_ALL.VENDOR_SITE_ID = POZ_SUPPLIER_SITES_ALL_M.VENDOR_SITE_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIER_CONTACTS":
        "PO_HEADERS_ALL.VENDOR_CONTACT_ID = POZ_SUPPLIER_CONTACTS.VENDOR_CONTACT_ID",
}


POZ_SUPPLIERS = {
    "description": ("Supplier master. One row per supplier. NOTE: no name column here — supplier name lives on "
                    "HZ_PARTIES.PARTY_NAME via PARTY_ID. Verified vs Oracle 26B: these attributes are NOT on this "
                    "header table — TERMS_ID, PAYMENT_CURRENCY_CODE, INVOICE_CURRENCY_CODE live at site level "
                    "(POZ_SUPPLIER_SITES_ALL_M); EMAIL_ADDRESS lives in TCA (HZ_PARTIES/HZ_CONTACT_POINTS via PARTY_ID); "
                    "STATUS (registration) lives in POZ_SUPPLIER_REGISTRATIONS; TAXPAYER_ID is replaced by "
                    "VAT_REGISTRATION_NUM + TAXPAYER_COUNTRY."),
    "primary_key": "VENDOR_ID",
    "key_columns": {
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier unique identifier"},
        "PARTY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "TCA party FK (join to HZ_PARTIES.PARTY_ID for supplier name)"},
        "SEGMENT1": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Supplier number (human-readable; alias as SUPPLIER_NUMBER)"},
        "VENDOR_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Supplier type (STANDARD, EMPLOYEE, CONTRACTOR, etc.)"},
        "ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - supplier enabled"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective start date"},
        "END_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective end date (NULL = active)"},
        "EMPLOYEE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "If employee supplier, FK to HR person"},
        "PARENT_VENDOR_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent supplier (self-FK)"},
        "ONE_TIME_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - one-time supplier"},
        "MIN_ORDER_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Minimum order amount"},
        "TAX_REPORTING_NAME": {"type": "VARCHAR2(80)", "nullable": True, "desc": "1099 reporting name"},
        "TAXPAYER_COUNTRY": {"type": "VARCHAR2(2)", "nullable": True, "desc": "Country for tax identity (26B; replaces TAXPAYER_ID use)"},
        "VAT_REGISTRATION_NUM": {"type": "VARCHAR2(20)", "nullable": True, "desc": "VAT registration number (26B; replaces TAXPAYER_ID use)"},
        "FEDERAL_REPORTABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - 1099 reportable"},
        "STATE_REPORTABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - state reportable"},
        "TYPE_1099": {"type": "VARCHAR2(10)", "nullable": True, "desc": "1099 type"},
        "STANDARD_INDUSTRY_CLASS": {"type": "VARCHAR2(25)", "nullable": True, "desc": "SIC / NAICS classification code"},
        "BUSINESS_RELATIONSHIP": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Supplier relationship classification (26B)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF context"},
    },
}


POZ_SUPPLIERS_INT = {
    "description": "Supplier interface (import staging). Used by Import Suppliers ESS job.",
    "primary_key": "VENDOR_INTERFACE_ID",
    "key_columns": {
        "VENDOR_INTERFACE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Interface row ID"},
        "VENDOR_NAME": {"type": "VARCHAR2(360)", "nullable": True, "desc": "Supplier name (only on interface — base POZ_SUPPLIERS has no name)"},
        "SEGMENT1": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Proposed supplier number"},
        "VENDOR_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Supplier type"},
        "STATUS": {"type": "VARCHAR2(20)", "nullable": True, "desc": "Import status (NEW, PROCESSED, REJECTED)"},
        "IMPORT_ACTION": {"type": "VARCHAR2(10)", "nullable": True, "desc": "CREATE or UPDATE action flag (26B)"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "VENDOR_ID assigned on successful import"},
        "LOAD_REQUEST_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "ESS request that loaded the row"},
    },
}


POZ_SUPPLIER_SITES_ALL_M = {
    "description": "Supplier sites (one row per supplier site per business unit). The 'M' suffix indicates multi-BU. Carries pay/purchasing/RFQ flags.",
    "primary_key": "VENDOR_SITE_ID",
    "key_columns": {
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Site unique identifier"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "VENDOR_SITE_CODE": {"type": "VARCHAR2(15)", "nullable": False, "desc": "Site code (human-readable)"},
        "VENDOR_SITE_CODE_ALT": {"type": "VARCHAR2(320)", "nullable": True, "desc": "Alternate site code"},
        "PRC_BU_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Procurement BU owning this site row (PROCUREMENT_BU_ID alias does NOT exist per docs)"},
        "SUPPLIER_ADDRESS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to POZ_SUPPLIER_ADDRESSES. ⚠️ docs show address FK as PARTY_SITE_ID — verify on-pod"},
        "PURCHASING_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - usable for POs"},
        "PAY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - usable for AP payments"},
        "RFQ_ONLY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - RFQ only"},
        "PRIMARY_PAY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - primary pay site"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Site inactive date (NULL = active)"},
        "TERMS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment terms (FK to AP_TERMS_TL)"},
        "PAYMENT_METHOD_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Default payment method (renamed from PAYMENT_METHOD_CODE per docs)"},
        "PAY_GROUP_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Pay group"},
        "INVOICE_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Invoice currency"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency"},
        "SHIP_TO_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default ship-to (FK to HR_LOCATIONS_ALL). ⚠️ not confirmed in 26B docs — verify on-pod"},
        "BILL_TO_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default bill-to. ⚠️ not confirmed in 26B docs — verify on-pod"},
        "FOB_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Free-on-board terms"},
        "FREIGHT_TERMS_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Freight terms"},
        "INVOICE_AMOUNT_LIMIT": {"type": "NUMBER", "nullable": True, "desc": "Max invoice amount"},
        "HOLD_ALL_PAYMENTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - hold all payments"},
        "HOLD_UNMATCHED_INVOICES_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - hold unmatched"},
        "TOLERANCE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receiving tolerance ID"},
        "MATCH_OPTION": {"type": "VARCHAR2(25)", "nullable": True, "desc": "PO/RECEIPT match option (renamed from INVOICE_MATCH_OPTION per docs)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF context (site-level DFFs)"},
    },
}


POZ_SUPPLIER_ADDRESSES = {
    "description": ("Supplier addresses. The documented object is the view POZ_SUPPLIER_ADDRESS_V, keyed by PARTY_SITE_ID "
                    "(not SUPPLIER_ADDRESS_ID). Query the view for address detail. Purpose columns are named "
                    "ADDRESS_PURPOSE_ORDERING / ADDRESS_PURPOSE_REMIT_TO / ADDRESS_PURPOSE_RFQ_OR_BIDDING (no billing flag)."),
    "primary_key": "PARTY_SITE_ID",
    "key_columns": {
        "SUPPLIER_ADDRESS_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Address ID (base table). ⚠️ the view uses PARTY_SITE_ID — verify on-pod"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "PARTY_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "TCA party site FK (primary identifier on POZ_SUPPLIER_ADDRESS_V)"},
        "LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to HZ_LOCATIONS (the actual address lines)"},
        "PARTY_SITE_NAME": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Address label (renamed from ADDRESS_NAME per view)"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Address inactive date"},
        "ADDRESS_PURPOSE_ORDERING": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - ordering address (renamed from _ORDERING_FLAG)"},
        "ADDRESS_PURPOSE_RFQ_OR_BIDDING": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - RFQ/bidding address (renamed from _RFQ_FLAG)"},
        "ADDRESS_PURPOSE_REMIT_TO": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - remittance address (renamed from _PAY_FLAG)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
    },
}


POZ_SUPPLIER_CONTACTS = {
    "description": ("Supplier contacts. ⚠️ Verified vs Oracle 26B: the base table POZ_SUPPLIER_CONTACTS is a lean "
                    "association table — name/email/phone/title columns live on the VIEW POZ_SUPPLIER_CONTACTS_V "
                    "(denormalized from HZ_PARTIES/HZ_ORG_CONTACTS/HZ_CONTACT_POINTS). Query the _V view for contact "
                    "detail. Phone columns on the view are PHONE / FAX / MOBILE (not *_NUMBER). VENDOR_ID is on the "
                    "view; CONTACT_TYPE is not documented on either object."),
    "primary_key": "VENDOR_CONTACT_ID",
    "key_columns": {
        "VENDOR_CONTACT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Contact unique identifier"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK (present on POZ_SUPPLIER_CONTACTS_V, not the base table)"},
        "PER_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to HZ_PARTIES for contact name (PARTY_TYPE='PERSON')"},
        "RELATIONSHIP_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "HZ_RELATIONSHIPS FK"},
        "ORG_CONTACT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to HZ_ORG_CONTACTS (canonical join key for contact detail)"},
        "FIRST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "First name (on POZ_SUPPLIER_CONTACTS_V)"},
        "LAST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Last name (on POZ_SUPPLIER_CONTACTS_V)"},
        "JOB_TITLE": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Title (on POZ_SUPPLIER_CONTACTS_V)"},
        "EMAIL_ADDRESS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Contact email (on POZ_SUPPLIER_CONTACTS_V)"},
        "PHONE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Phone number (view column; renamed from PHONE_NUMBER)"},
        "PHONE_EXTENSION": {"type": "VARCHAR2(20)", "nullable": True, "desc": "Phone extension (on POZ_SUPPLIER_CONTACTS_V)"},
        "FAX": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Fax number (view column; renamed from FAX_NUMBER)"},
        "MOBILE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Mobile number (view column; renamed from MOBILE_NUMBER)"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive (on POZ_SUPPLIER_CONTACTS_V)"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Contact inactive date"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
    },
}


# Renamed in current Oracle docs: POZ_SUP_THIRD_PARTY_REL -> POZ_SUP_THIRDPARTY_PAYMENT_REL,
# with PK and third-party/date columns renamed (see desc). Old name/columns will fail on current pods.
POZ_SUP_THIRDPARTY_PAYMENT_REL = {
    "description": ("Third-party payment relationships (e.g., pay supplier A via third party B). Renamed from "
                    "POZ_SUP_THIRD_PARTY_REL in current Oracle docs. VENDOR_ID and RELATIONSHIP_TYPE removed; "
                    "supplier linkage is via VENDOR_SITE_ID."),
    "primary_key": "TPP_RELATIONSHIP_ID",
    "key_columns": {
        "TPP_RELATIONSHIP_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Relationship unique identifier (renamed from THIRD_PARTY_REL_ID)"},
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Primary supplier site (supplier linkage)"},
        "REMIT_TO_SUPPLIER_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Third-party (payee) supplier (renamed from THIRD_PARTY_VENDOR_ID)"},
        "REMIT_TO_ADDRESS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Third-party address (renamed from THIRD_PARTY_VENDOR_SITE_ID)"},
        "FROM_DATE": {"type": "DATE", "nullable": True, "desc": "Relationship start (renamed from START_DATE)"},
        "TO_DATE": {"type": "DATE", "nullable": True, "desc": "Relationship end, NULL = active (renamed from END_DATE)"},
        "DEFAULT_RELATIONSHIP_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - default third-party relationship"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_BUSINESS_CLASSIFICATIONS = {
    "description": ("Diversity / business classifications assigned to a supplier. Verified vs Oracle 25D: PK is "
                    "CLASSIFICATION_ID (not BUS_CLASSIFICATION_ID); the classification type column is LOOKUP_CODE "
                    "(not CLASSIFICATION_CODE). STATUS and START_DATE_ACTIVE are OBSOLETE — use CLASS_STATUS and START_DATE."),
    "primary_key": "CLASSIFICATION_ID",
    "key_columns": {
        "CLASSIFICATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Classification record unique ID (renamed from BUS_CLASSIFICATION_ID)"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "TCA party identifier (modern join key alongside VENDOR_ID)"},
        "LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Classification lookup code, e.g. MINORITY_OWNED, WOMEN_OWNED (renamed from CLASSIFICATION_CODE)"},
        "CLASS_STATUS": {"type": "VARCHAR2(255)", "nullable": True, "desc": "Approval workflow status: PENDING/APPROVED/REJECTED (replaces obsolete STATUS)"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Certificate start date (replaces obsolete START_DATE_ACTIVE)"},
        "EXPIRATION_DATE": {"type": "DATE", "nullable": True, "desc": "Certification expiration"},
        "CERTIFICATE_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Certificate number"},
        "CERTIFYING_AGENCY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to POZ_CERTIFYING_AGENCIES"},
        "EXT_ATTR_1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Minority type info (replaces MINORITY_TYPE_LOOKUP_CODE)"},
        "NOTES": {"type": "VARCHAR2(1000)", "nullable": True, "desc": "Notes"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


# Renamed in current Oracle docs: POZ_BUS_CLASS_REFERENCES -> POZ_CERTIFYING_AGENCIES (different column set).
POZ_CERTIFYING_AGENCIES = {
    "description": ("Certifying agencies that issue business classification certificates. Renamed from "
                    "POZ_BUS_CLASS_REFERENCES; PK is AGENCY_ID. AGENCY_TYPE/CONTACT_NAME/PHONE_NUMBER/WEB_ADDRESS are "
                    "not documented; active/inactive is controlled by END_DATE (no STATUS flag)."),
    "primary_key": "AGENCY_ID",
    "key_columns": {
        "AGENCY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Agency record ID (renamed from BUS_CLASS_REFERENCE_ID)"},
        "NAME": {"type": "VARCHAR2(255)", "nullable": False, "desc": "Certifying agency name (renamed from AGENCY_NAME)"},
        "DESCRIPTION": {"type": "VARCHAR2(1000)", "nullable": True, "desc": "Agency description"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Inactive date, NULL = active (replaces STATUS flag)"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": True, "desc": "Optimistic locking version"},
    },
}


# Renamed in current Oracle docs: POZ_PRODUCTS_AND_SERVICES -> POZ_SUP_PRODUCTS_SERVICES; PK CLASSIFICATION_ID.
POZ_SUP_PRODUCTS_SERVICES = {
    "description": ("Products and services a supplier provides (mapped to procurement categories). Renamed from "
                    "POZ_PRODUCTS_AND_SERVICES; PK is CLASSIFICATION_ID. CATEGORY_TYPE/START_DATE_ACTIVE/END_DATE_ACTIVE "
                    "are not documented on this table (CATEGORY_TYPE exists only on the import table POZ_SUP_PROD_SERV_INT)."),
    "primary_key": "CLASSIFICATION_ID",
    "key_columns": {
        "CLASSIFICATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Product/service record ID (renamed from PROD_SERV_ID)"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "FK to POZ_PROD_SERV_CATEGORY_V / EGP_CATEGORIES_B"},
        "PURCHASING_CAT_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - purchasing category assignment"},
        "STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Status (widened to 30 per docs)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


# Not found in current Oracle docs as POZ_SUPP_PROD_SERV_CAT. Documented object is the view POZ_PROD_SERV_CATEGORY_V.
POZ_PROD_SERV_CATEGORY_V = {
    "description": ("Reference list of procurement categories for supplier products/services. ⚠️ POZ_SUPP_PROD_SERV_CAT "
                    "is not in current Oracle docs — the documented object is the view POZ_PROD_SERV_CATEGORY_V "
                    "(CATEGORY_ID, CATEGORY_NAME, PURCHASING_CAT_FLAG only). CATEGORY_CODE/PARENT_CATEGORY_ID/DESCRIPTION/STATUS "
                    "are not documented; for category hierarchy/detail join EGP_CATEGORIES_B."),
    "primary_key": "CATEGORY_ID",
    "key_columns": {
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category ID"},
        "CATEGORY_NAME": {"type": "VARCHAR2(240)", "nullable": False, "desc": "Category display name"},
        "PURCHASING_CAT_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - purchasing category"},
    },
}


POZ_QUAL_REC_OWNERSHIPS = {
    "description": ("⚠️ UNVERIFIED: not found in Oracle 25D/26A Procurement docs. The POZ supplier model has no POZ_QUAL* "
                    "tables; qualification data is documented under the POQ_ prefix (POQ_QUALIFICATIONS, "
                    "POQ_EVALUATION_TEAM). May be a custom/internal table — confirm on-pod before use. "
                    "Qualification record ownership — who owns/maintains a supplier qualification."),
    "primary_key": "QUAL_REC_OWNERSHIP_ID",
    "key_columns": {
        "QUAL_REC_OWNERSHIP_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Ownership record ID"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "QUALIFICATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Qualification FK (FOQ_QUALIFICATIONS)"},
        "OWNER_PERSON_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Owner HR person ID"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Ownership start"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Ownership end"},
        "STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Status"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_SUPPLIER_TAX_PROFILES = {
    "description": ("Supplier tax profile (one row per supplier party). ⚠️ The authoritative documented table is "
                    "ZX_PARTY_TAX_PROFILE (owner ZX, Financials/Tax) — query that name. All columns below match it "
                    "except REPORTING_AUTHORITY_ID, which does not exist (use REPORTING_AUTHORITY_FLAG Y/N)."),
    "primary_key": "PARTY_TAX_PROFILE_ID",
    "key_columns": {
        "PARTY_TAX_PROFILE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Tax profile unique ID"},
        "PARTY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "FK to HZ_PARTIES (supplier party)"},
        "PARTY_TYPE_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Party type (THIRD_PARTY)"},
        "REGISTRATION_TYPE_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Default tax registration type"},
        "ROUNDING_LEVEL_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "HEADER / LINE rounding"},
        "ROUNDING_RULE_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "UP / DOWN / NEAREST"},
        "WITHHOLDING_START_DATE": {"type": "DATE", "nullable": True, "desc": "Withholding effective start"},
        "ALLOW_OFFSET_TAX_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - allow offset tax"},
        "SELF_ASSESS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - self-assess"},
        "TAX_CLASSIFICATION_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Default tax classification"},
        "REPORTING_AUTHORITY_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - reporting authority (replaces non-existent REPORTING_AUTHORITY_ID)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_SUPPLIER_NOTES = {
    "description": ("⚠️ UNVERIFIED / likely non-standard: POZ_SUPPLIER_NOTES does not appear in Oracle's 25D Procurement "
                    "Tables and Views docs (every other POZ_SUPPLIER_* table is listed). Do not assume this exists on a "
                    "stock Fusion pod — confirm before use. Notes attached to a supplier (free-text annotations from buyers)."),
    "primary_key": "NOTE_ID",
    "key_columns": {
        "NOTE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Note unique ID"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Site FK (NULL for supplier-level notes)"},
        "NOTE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Note type/category"},
        "NOTE_TEXT": {"type": "CLOB", "nullable": True, "desc": "Note body"},
        "AUTHOR_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Author user ID"},
        "VISIBILITY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "INTERNAL / SUPPLIER_VISIBLE"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_SUPPLIER_ATTACHMENTS = {
    "description": ("⚠️ UNVERIFIED / likely non-standard: POZ_SUPPLIER_ATTACHMENTS is not in Oracle docs (25B–26B). The only "
                    "documented POZ attachment object is the import table POZ_SUP_ATTACHMENTS_INT, and operational supplier "
                    "attachments live in the generic FND_ATTACHED_DOCUMENTS / FND_DOCUMENTS framework. ATTACHMENT_PURPOSE "
                    "is undocumented (closest is ATTACHMENT_CATEGORY). Prefer FND_ATTACHED_DOCUMENTS joined via "
                    "ENTITY_NAME='POZ_SUPPLIERS' and PK1_VALUE."),
    "primary_key": "ATTACHMENT_ID",
    "key_columns": {
        "ATTACHMENT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Attachment link ID"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "ENTITY_NAME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "FND attachment entity name (POZ_SUPPLIERS)"},
        "PK1_VALUE": {"type": "VARCHAR2(255)", "nullable": True, "desc": "PK to join FND_ATTACHED_DOCUMENTS"},
        "DOCUMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to FND_DOCUMENTS_TL"},
        "ATTACHMENT_PURPOSE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Purpose (BACKGROUND_CHECK, INSURANCE, W9, etc.)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


ALL_SUPPLIER_TABLES = {
    "POZ_SUPPLIERS": POZ_SUPPLIERS,
    "POZ_SUPPLIERS_INT": POZ_SUPPLIERS_INT,
    "POZ_SUPPLIER_SITES_ALL_M": POZ_SUPPLIER_SITES_ALL_M,
    "POZ_SUPPLIER_ADDRESSES": POZ_SUPPLIER_ADDRESSES,
    "POZ_SUPPLIER_CONTACTS": POZ_SUPPLIER_CONTACTS,
    "POZ_SUP_THIRDPARTY_PAYMENT_REL": POZ_SUP_THIRDPARTY_PAYMENT_REL,
    "POZ_BUSINESS_CLASSIFICATIONS": POZ_BUSINESS_CLASSIFICATIONS,
    "POZ_CERTIFYING_AGENCIES": POZ_CERTIFYING_AGENCIES,
    "POZ_SUP_PRODUCTS_SERVICES": POZ_SUP_PRODUCTS_SERVICES,
    "POZ_PROD_SERV_CATEGORY_V": POZ_PROD_SERV_CATEGORY_V,
    "POZ_QUAL_REC_OWNERSHIPS": POZ_QUAL_REC_OWNERSHIPS,
    "POZ_SUPPLIER_TAX_PROFILES": POZ_SUPPLIER_TAX_PROFILES,
    "POZ_SUPPLIER_NOTES": POZ_SUPPLIER_NOTES,
    "POZ_SUPPLIER_ATTACHMENTS": POZ_SUPPLIER_ATTACHMENTS,
}


SUPPLIER_LOOKUP_VALUES = {
    "VENDOR_TYPE_LOOKUP_CODE (POZ_SUPPLIERS)": [
        "STANDARD - Standard supplier",
        "EMPLOYEE - Employee supplier (T&E reimbursement)",
        "CONTRACTOR - Contingent worker supplier",
        "TAX AUTHORITY - Tax authority",
    ],
    "STATUS (POZ_SUPPLIERS registration)": [
        "NEW - Newly registered, pending review",
        "PENDING_APPROVAL - Submitted for approval",
        "APPROVED - Active supplier",
        "REJECTED - Rejected during onboarding",
        "INACTIVE - Disabled",
    ],
    "LOOKUP_CODE (POZ_BUSINESS_CLASSIFICATIONS)": [
        "MINORITY_OWNED",
        "WOMEN_OWNED",
        "SMALL_BUSINESS",
        "VETERAN_OWNED",
        "SERVICE_DISABLED_VETERAN_OWNED",
        "HUB_ZONE",
        "DISADVANTAGED_BUSINESS",
        "LGBT_OWNED",
    ],
    "MATCH_OPTION (POZ_SUPPLIER_SITES_ALL_M)": [
        "PO - 2-way / 3-way / 4-way match to PO",
        "RECEIPT - Match against receipts",
    ],
}
