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
    "POZ_SUPPLIERS -> POZ_PRODUCTS_AND_SERVICES":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_PRODUCTS_AND_SERVICES.VENDOR_ID",
    "POZ_PRODUCTS_AND_SERVICES -> POZ_SUPP_PROD_SERV_CAT":
        "POZ_PRODUCTS_AND_SERVICES.CATEGORY_ID = POZ_SUPP_PROD_SERV_CAT.CATEGORY_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_TAX_PROFILES":
        "POZ_SUPPLIERS.PARTY_ID = POZ_SUPPLIER_TAX_PROFILES.PARTY_ID",
    "POZ_SUPPLIERS -> POZ_SUPPLIER_NOTES":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUPPLIER_NOTES.VENDOR_ID",
    "POZ_SUPPLIERS -> POZ_SUP_THIRD_PARTY_REL":
        "POZ_SUPPLIERS.VENDOR_ID = POZ_SUP_THIRD_PARTY_REL.VENDOR_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIERS":
        "PO_HEADERS_ALL.VENDOR_ID = POZ_SUPPLIERS.VENDOR_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIER_SITES_ALL_M":
        "PO_HEADERS_ALL.VENDOR_SITE_ID = POZ_SUPPLIER_SITES_ALL_M.VENDOR_SITE_ID",
    "PO_HEADERS_ALL -> POZ_SUPPLIER_CONTACTS":
        "PO_HEADERS_ALL.VENDOR_CONTACT_ID = POZ_SUPPLIER_CONTACTS.VENDOR_CONTACT_ID",
}


POZ_SUPPLIERS = {
    "description": "Supplier master. One row per supplier. NOTE: no name column here — supplier name lives on HZ_PARTIES.PARTY_NAME via PARTY_ID.",
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
        "TERMS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default payment terms (FK to AP_TERMS_TL)"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Default payment currency"},
        "INVOICE_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Default invoice currency"},
        "TAX_REPORTING_NAME": {"type": "VARCHAR2(80)", "nullable": True, "desc": "1099 reporting name"},
        "TAXPAYER_ID": {"type": "VARCHAR2(20)", "nullable": True, "desc": "Tax ID / TIN"},
        "FEDERAL_REPORTABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - 1099 reportable"},
        "STATE_REPORTABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - state reportable"},
        "TYPE_1099": {"type": "VARCHAR2(10)", "nullable": True, "desc": "1099 type"},
        "STANDARD_INDUSTRY_CLASS": {"type": "VARCHAR2(25)", "nullable": True, "desc": "SIC / NAICS classification code"},
        "SUPPLIER_NOTIF_METHOD": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Notification method (EMAIL, FAX, PRINT)"},
        "EMAIL_ADDRESS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Primary email"},
        "STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Registration status (NEW, APPROVED, REJECTED, etc.)"},
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
        "STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Import status (NEW, PROCESSED, REJECTED)"},
        "REJECT_REASON": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Rejection reason if import failed"},
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
        "PRC_BU_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Procurement BU owning this site row"},
        "PROCUREMENT_BU_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Same as PRC_BU_ID — alternate column name"},
        "SUPPLIER_ADDRESS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to POZ_SUPPLIER_ADDRESSES"},
        "PURCHASING_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - usable for POs"},
        "PAY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - usable for AP payments"},
        "RFQ_ONLY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - RFQ only"},
        "PRIMARY_PAY_SITE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - primary pay site"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Site inactive date (NULL = active)"},
        "TERMS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment terms (FK to AP_TERMS_TL)"},
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Default payment method"},
        "PAY_GROUP_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Pay group"},
        "INVOICE_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Invoice currency"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency"},
        "SHIP_TO_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default ship-to (FK to HR_LOCATIONS_ALL)"},
        "BILL_TO_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default bill-to"},
        "FOB_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Free-on-board terms"},
        "FREIGHT_TERMS_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Freight terms"},
        "INVOICE_AMOUNT_LIMIT": {"type": "NUMBER", "nullable": True, "desc": "Max invoice amount"},
        "HOLD_ALL_PAYMENTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - hold all payments"},
        "HOLD_UNMATCHED_INVOICES_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - hold unmatched"},
        "TOLERANCE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receiving tolerance ID"},
        "INVOICE_MATCH_OPTION": {"type": "VARCHAR2(25)", "nullable": True, "desc": "PO/RECEIPT match option"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF context (site-level DFFs)"},
    },
}


POZ_SUPPLIER_ADDRESSES = {
    "description": "Supplier addresses. Shared across sites — one address may serve multiple POZ_SUPPLIER_SITES_ALL_M rows.",
    "primary_key": "SUPPLIER_ADDRESS_ID",
    "key_columns": {
        "SUPPLIER_ADDRESS_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Address unique identifier"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "PARTY_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "TCA party site FK"},
        "LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to HZ_LOCATIONS (the actual address lines)"},
        "ADDRESS_NAME": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Address label"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Address inactive date"},
        "ADDRESS_PURPOSE_BILLING_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - billing address"},
        "ADDRESS_PURPOSE_ORDERING_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - ordering address"},
        "ADDRESS_PURPOSE_RFQ_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - RFQ address"},
        "ADDRESS_PURPOSE_PAY_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - remittance address"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
    },
}


POZ_SUPPLIER_CONTACTS = {
    "description": "Supplier contacts. Contact name comes from HZ_PARTIES via PER_PARTY_ID, NOT from this table.",
    "primary_key": "VENDOR_CONTACT_ID",
    "key_columns": {
        "VENDOR_CONTACT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Contact unique identifier"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "PER_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to HZ_PARTIES for contact name (PARTY_TYPE='PERSON')"},
        "REL_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Relationship party ID"},
        "RELATIONSHIP_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "HZ_RELATIONSHIPS FK"},
        "FIRST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Denormalized first name"},
        "LAST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Denormalized last name"},
        "JOB_TITLE": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Title"},
        "EMAIL_ADDRESS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Contact email"},
        "PHONE_AREA_CODE": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Phone area code"},
        "PHONE_NUMBER": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Phone number"},
        "PHONE_EXTENSION": {"type": "VARCHAR2(20)", "nullable": True, "desc": "Phone extension"},
        "FAX_AREA_CODE": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Fax area code"},
        "FAX_NUMBER": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Fax number"},
        "MOBILE_NUMBER": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Mobile number"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Contact inactive date"},
        "CONTACT_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Contact role/type"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
    },
}


POZ_SUP_THIRD_PARTY_REL = {
    "description": "Third-party payment relationships (e.g., pay supplier A via third party B).",
    "primary_key": "THIRD_PARTY_REL_ID",
    "key_columns": {
        "THIRD_PARTY_REL_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Relationship unique identifier"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Primary supplier"},
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Primary supplier site"},
        "THIRD_PARTY_VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Third-party (payee) supplier"},
        "THIRD_PARTY_VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Third-party site"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Relationship start"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Relationship end (NULL = active)"},
        "RELATIONSHIP_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Type of relationship"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_BUSINESS_CLASSIFICATIONS = {
    "description": "Diversity / business classifications assigned to a supplier (small business, minority-owned, women-owned, etc.).",
    "primary_key": "BUS_CLASSIFICATION_ID",
    "key_columns": {
        "BUS_CLASSIFICATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Classification record unique ID"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "CLASSIFICATION_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Lookup code (e.g., MINORITY_OWNED, WOMEN_OWNED, SMALL_BUSINESS)"},
        "CLASSIFICATION_NAME": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Display name"},
        "SUB_CLASSIFICATION_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Sub-classification lookup code"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective start"},
        "EXPIRATION_DATE": {"type": "DATE", "nullable": True, "desc": "Certification expiration"},
        "CERTIFICATE_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Certificate number"},
        "CERTIFYING_AGENCY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to POZ_BUS_CLASS_REFERENCES"},
        "MINORITY_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Minority type (if MINORITY_OWNED)"},
        "NOTES": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Notes"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_BUS_CLASS_REFERENCES = {
    "description": "Certifying agencies that issue business classification certificates.",
    "primary_key": "BUS_CLASS_REFERENCE_ID",
    "key_columns": {
        "BUS_CLASS_REFERENCE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Agency record ID"},
        "AGENCY_NAME": {"type": "VARCHAR2(240)", "nullable": False, "desc": "Certifying agency name"},
        "AGENCY_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Agency type (FEDERAL, STATE, LOCAL, PRIVATE)"},
        "CONTACT_NAME": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Agency contact"},
        "PHONE_NUMBER": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Phone"},
        "WEB_ADDRESS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Website"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
    },
}


POZ_PRODUCTS_AND_SERVICES = {
    "description": "Products and services a supplier provides (mapped to procurement categories).",
    "primary_key": "PROD_SERV_ID",
    "key_columns": {
        "PROD_SERV_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Product/service record ID"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Supplier FK"},
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "FK to POZ_SUPP_PROD_SERV_CAT / EGP_CATEGORIES_B"},
        "CATEGORY_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "PURCHASING / BROWSING"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective start"},
        "END_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective end"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_SUPP_PROD_SERV_CAT = {
    "description": "Reference list of procurement categories available for supplier products/services.",
    "primary_key": "CATEGORY_ID",
    "key_columns": {
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category ID"},
        "CATEGORY_NAME": {"type": "VARCHAR2(240)", "nullable": False, "desc": "Category display name"},
        "CATEGORY_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Category code"},
        "PARENT_CATEGORY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent in hierarchy"},
        "DESCRIPTION": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Description"},
        "STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "A=Active, I=Inactive"},
    },
}


POZ_QUAL_REC_OWNERSHIPS = {
    "description": "Qualification record ownership — who owns/maintains a supplier qualification.",
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
    "description": "Supplier tax profile (one row per supplier party). Tax registrations live in ZX tables.",
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
        "REPORTING_AUTHORITY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Reporting authority"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
    },
}


POZ_SUPPLIER_NOTES = {
    "description": "Notes attached to a supplier (free-text annotations from buyers).",
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
    "description": "Pointer table to attachments on a supplier record. Actual file metadata is in FND_ATTACHED_DOCUMENTS / FND_DOCUMENTS_TL.",
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
    "POZ_SUP_THIRD_PARTY_REL": POZ_SUP_THIRD_PARTY_REL,
    "POZ_BUSINESS_CLASSIFICATIONS": POZ_BUSINESS_CLASSIFICATIONS,
    "POZ_BUS_CLASS_REFERENCES": POZ_BUS_CLASS_REFERENCES,
    "POZ_PRODUCTS_AND_SERVICES": POZ_PRODUCTS_AND_SERVICES,
    "POZ_SUPP_PROD_SERV_CAT": POZ_SUPP_PROD_SERV_CAT,
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
    "CLASSIFICATION_CODE (POZ_BUSINESS_CLASSIFICATIONS)": [
        "MINORITY_OWNED",
        "WOMEN_OWNED",
        "SMALL_BUSINESS",
        "VETERAN_OWNED",
        "SERVICE_DISABLED_VETERAN_OWNED",
        "HUB_ZONE",
        "DISADVANTAGED_BUSINESS",
        "LGBT_OWNED",
    ],
    "INVOICE_MATCH_OPTION (POZ_SUPPLIER_SITES_ALL_M)": [
        "PO - 2-way / 3-way / 4-way match to PO",
        "RECEIPT - Match against receipts",
    ],
}
