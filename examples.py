"""
Example SQL queries for BI Publisher Oracle Procurement reports.
Based on real working queries from SQL_PO_PRACTICE.sql and
Oracle's production PurchaseOrderDm.xdm.catalog data models.
"""

EXAMPLES = [
    {
        "name": "PO Header with Supplier Name",
        "description": "Basic query to list Purchase Orders with supplier names from TCA",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL"""
    },
    {
        "name": "PO Lines with Item Details",
        "description": "PO headers joined to lines with item master and supplier info",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PLA.ITEM_DESCRIPTION,
    PLA.ORDER_TYPE_LOOKUP_CODE,
    PLA.LINE_NUM,
    PLA.QUANTITY,
    HP.PARTY_NAME AS SUPPLIER_NAME,
    ESI.ITEM_NUMBER
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP,
    EGP_SYSTEM_ITEMS_B ESI
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID (+)
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PLA.ITEM_ID = ESI.INVENTORY_ITEM_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
ORDER BY
    PO_NUMBER ASC,
    PLA.LINE_NUM ASC"""
    },
    {
        "name": "PO with Shipment Schedules",
        "description": "Full PO with line locations showing delivery dates and quantities received",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.DOCUMENT_STATUS AS PO_STATUS,
    PHA.CURRENCY_CODE,
    PLA.LINE_NUM,
    PLA.ITEM_DESCRIPTION,
    PLA.QUANTITY AS ORDERED_QTY,
    PLA.UNIT_PRICE,
    PLLA.SHIPMENT_NUM,
    PLLA.NEED_BY_DATE,
    PLLA.PROMISED_DATE,
    PLLA.QUANTITY_RECEIVED,
    PLLA.QUANTITY_BILLED,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
    AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
ORDER BY
    PHA.SEGMENT1,
    PLA.LINE_NUM,
    PLLA.SHIPMENT_NUM"""
    },
    {
        "name": "PO Distributions with GL Accounts",
        "description": "Full PO drill-down to distribution level with charge account",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.TYPE_LOOKUP_CODE AS DOCUMENT_TYPE,
    PLA.LINE_NUM,
    PLA.ITEM_DESCRIPTION,
    PDA.DISTRIBUTION_NUM,
    PDA.QUANTITY_ORDERED,
    PDA.QUANTITY_DELIVERED,
    PDA.QUANTITY_BILLED,
    PDA.DESTINATION_TYPE_CODE,
    GCC.SEGMENT1 || '.' || GCC.SEGMENT2 || '.' || GCC.SEGMENT3 || '.' ||
    GCC.SEGMENT4 || '.' || GCC.SEGMENT5 AS CHARGE_ACCOUNT,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    PO_DISTRIBUTIONS_ALL PDA,
    GL_CODE_COMBINATIONS GCC,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PLLA.LINE_LOCATION_ID = PDA.LINE_LOCATION_ID
    AND PDA.CODE_COMBINATION_ID = GCC.CODE_COMBINATION_ID (+)
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
ORDER BY
    PHA.SEGMENT1,
    PLA.LINE_NUM,
    PDA.DISTRIBUTION_NUM"""
    },
    {
        "name": "PO Approval History",
        "description": "Track approval actions on purchase orders",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.TYPE_LOOKUP_CODE AS DOCUMENT_TYPE,
    PAH.SEQUENCE_NUM,
    PAH.ACTION_CODE,
    PAH.ACTION_DATE,
    PAH.ROLE_CODE,
    PAH.NOTE AS APPROVER_NOTE,
    HP_SUPPLIER.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    PO_ACTION_HISTORY PAH,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP_SUPPLIER
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PAH.OBJECT_ID
    AND PAH.OBJECT_TYPE_CODE = 'PO'
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP_SUPPLIER.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
ORDER BY
    PHA.SEGMENT1,
    PAH.SEQUENCE_NUM"""
    },
    {
        "name": "Blanket Agreement Summary",
        "description": "Blanket purchase agreements with amount released vs agreed",
        "sql": """SELECT
    PHA.SEGMENT1 AS AGREEMENT_NUMBER,
    PHA.START_DATE AS EFFECTIVE_DATE,
    PHA.END_DATE AS EXPIRATION_DATE,
    PHA.BLANKET_TOTAL_AMOUNT AS AGREED_AMOUNT,
    PHA.AMOUNT_RELEASED,
    (PHA.BLANKET_TOTAL_AMOUNT - NVL(PHA.AMOUNT_RELEASED, 0)) AS REMAINING_AMOUNT,
    PHA.CURRENCY_CODE,
    PHA.DOCUMENT_STATUS,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.TYPE_LOOKUP_CODE = 'BLANKET'
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
ORDER BY
    PHA.SEGMENT1"""
    },
    {
        "name": "Receiving Transactions by PO",
        "description": "Receipt details joined to PO information",
        "sql": """SELECT
    RT.TRANSACTION_DATE,
    RT.TRANSACTION_TYPE,
    RT.QUANTITY AS RECEIPT_QUANTITY,
    RT.UOM_CODE AS RECEIPT_UOM,
    RSH.RECEIPT_NUM,
    PHA.SEGMENT1 AS PO_NUMBER,
    PLA.LINE_NUM AS PO_LINE_NUMBER,
    PLA.ITEM_DESCRIPTION,
    ESI.ITEM_NUMBER
FROM
    RCV_TRANSACTIONS RT,
    RCV_SHIPMENT_HEADERS RSH,
    RCV_SHIPMENT_LINES RSL,
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    EGP_SYSTEM_ITEMS_VL ESI
WHERE 1 = 1
    AND RT.SHIPMENT_HEADER_ID = RSH.SHIPMENT_HEADER_ID
    AND RT.SHIPMENT_LINE_ID = RSL.SHIPMENT_LINE_ID
    AND RT.PO_HEADER_ID = PHA.PO_HEADER_ID
    AND RT.PO_LINE_ID = PLA.PO_LINE_ID
    AND PLA.ITEM_ID = ESI.INVENTORY_ITEM_ID (+)
    AND RT.ORGANIZATION_ID = ESI.ORGANIZATION_ID (+)
    AND RT.TRANSACTION_TYPE = 'RECEIVE'
ORDER BY
    RT.TRANSACTION_DATE DESC"""
    },
    {
        "name": "Open POs Pending Receipt",
        "description": "PO lines where quantity ordered exceeds quantity received",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.DOCUMENT_STATUS,
    PLA.LINE_NUM,
    PLA.ITEM_DESCRIPTION,
    PLLA.QUANTITY AS ORDERED_QTY,
    NVL(PLLA.QUANTITY_RECEIVED, 0) AS RECEIVED_QTY,
    (PLLA.QUANTITY - NVL(PLLA.QUANTITY_RECEIVED, 0)) AS PENDING_QTY,
    PLLA.NEED_BY_DATE,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.DOCUMENT_STATUS = 'APPROVED'
    AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
    AND NVL(PLA.CANCEL_FLAG, 'N') = 'N'
    AND PLLA.QUANTITY > NVL(PLLA.QUANTITY_RECEIVED, 0)
ORDER BY
    PLLA.NEED_BY_DATE ASC"""
    },
    {
        "name": "PO with BI Publisher Parameters",
        "description": "Example showing BI Publisher parameter placeholders for runtime filtering",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.DOCUMENT_STATUS,
    PHA.CREATION_DATE,
    PHA.APPROVED_DATE,
    PLA.LINE_NUM,
    PLA.ITEM_DESCRIPTION,
    PLA.QUANTITY,
    PLA.UNIT_PRICE,
    (PLA.QUANTITY * PLA.UNIT_PRICE) AS LINE_AMOUNT,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    POZ_SUPPLIERS PS,
    HZ_PARTIES HP
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PS.VENDOR_ID = PHA.VENDOR_ID (+)
    AND PS.PARTY_ID = HP.PARTY_ID (+)
    AND PHA.SEGMENT1 IS NOT NULL
    AND PHA.SEGMENT1 = :P_PO_NUMBER           /* BI Publisher Parameter */
    AND PHA.PRC_BU_ID = :P_BUSINESS_UNIT      /* BI Publisher Parameter */
ORDER BY
    PLA.LINE_NUM ASC"""
    },

    # ===================================================================
    # EXAMPLES FROM ORACLE'S PRODUCTION DATA MODELS (xdm.catalog files)
    # ===================================================================
    {
        "name": "PO Header with Buyer, Locations & Payment Terms",
        "description": "Full PO header report with buyer name, ship-to/bill-to addresses, supplier site, payment terms, and legal entity (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Header.TYPE_LOOKUP_CODE AS DOCUMENT_TYPE,
    Header.DOCUMENT_STATUS,
    Header.CURRENCY_CODE,
    Header.REVISION_NUM,
    Header.VENDOR_ORDER_NUM,
    Header.ACCEPTANCE_REQUIRED_FLAG,
    Header.ACCEPTANCE_DUE_DATE,
    Header.NOTE_TO_VENDOR,
    DocStyle.DISPLAY_NAME AS DOCUMENT_STYLE,
    /* Buyer info (date-effective) */
    PersonName.DISPLAY_NAME AS BUYER_NAME,
    PersonEmail.EMAIL_ADDRESS AS BUYER_EMAIL,
    PersonPhone.DISPLAY_PHONE_NUMBER AS BUYER_PHONE,
    /* Supplier info */
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER,
    PozSupplierSite.VENDOR_SITE_CODE AS SUPPLIER_SITE,
    /* Payment & freight */
    PaymentTerms.NAME AS PAYMENT_TERMS,
    FobLookup.MEANING AS FOB_TERMS,
    FreightLookup.MEANING AS FREIGHT_TERMS,
    /* Ship-to location */
    ShipToLoc.LOCATION_NAME AS SHIP_TO_LOCATION,
    ShipToLoc.ADDRESS_LINE_1 AS SHIP_TO_ADDRESS1,
    ShipToLoc.TOWN_OR_CITY AS SHIP_TO_CITY,
    ShipToLoc.REGION_2 AS SHIP_TO_STATE,
    ShipToLoc.POSTAL_CODE AS SHIP_TO_ZIP,
    ShipToLoc.COUNTRY AS SHIP_TO_COUNTRY,
    /* Bill-to location */
    BillToLoc.LOCATION_NAME AS BILL_TO_LOCATION,
    BillToLoc.ADDRESS_LINE_1 AS BILL_TO_ADDRESS1,
    BillToLoc.TOWN_OR_CITY AS BILL_TO_CITY,
    /* Legal entity */
    SoldToLe.NAME AS LEGAL_ENTITY_NAME
FROM
    PO_HEADERS_ALL Header,
    PO_DOC_STYLE_LINES_VL DocStyle,
    POZ_SUPPLIERS Supplier,
    POZ_SUPPLIER_SITES_ALL_M PozSupplierSite,
    HZ_PARTIES SupplierPartyName,
    HR_LOCATIONS_ALL_F_VL ShipToLoc,
    HR_LOCATIONS_ALL_F_VL BillToLoc,
    AP_TERMS_VL PaymentTerms,
    FND_LOOKUPS FobLookup,
    FND_LOOKUPS FreightLookup,
    PER_PERSON_NAMES_F_V PersonName,
    PER_EMAIL_ADDRESSES PersonEmail,
    PER_DISPLAY_PHONES_V PersonPhone,
    XLE_ENTITY_PROFILES SoldToLe
WHERE 1 = 1
    AND Header.STYLE_ID = DocStyle.STYLE_ID
    AND Header.TYPE_LOOKUP_CODE = DocStyle.DOCUMENT_SUBTYPE
    /* Supplier joins */
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.VENDOR_SITE_ID = PozSupplierSite.VENDOR_SITE_ID (+)
    /* Location joins (date-effective) */
    AND Header.SHIP_TO_LOCATION_ID = ShipToLoc.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN ShipToLoc.EFFECTIVE_START_DATE (+) AND ShipToLoc.EFFECTIVE_END_DATE (+)
    AND Header.BILL_TO_LOCATION_ID = BillToLoc.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN BillToLoc.EFFECTIVE_START_DATE (+) AND BillToLoc.EFFECTIVE_END_DATE (+)
    /* Payment terms */
    AND Header.TERMS_ID = PaymentTerms.TERM_ID (+)
    /* Lookup display values */
    AND Header.FOB_LOOKUP_CODE = FobLookup.LOOKUP_CODE (+)
    AND FobLookup.LOOKUP_TYPE (+) = 'FOB'
    AND Header.FREIGHT_TERMS_LOOKUP_CODE = FreightLookup.LOOKUP_CODE (+)
    AND FreightLookup.LOOKUP_TYPE (+) = 'FREIGHT TERMS'
    /* Buyer (date-effective) */
    AND Header.AGENT_ID = PersonName.PERSON_ID (+)
    AND TRUNC(SYSDATE) BETWEEN PersonName.EFFECTIVE_START_DATE (+) AND PersonName.EFFECTIVE_END_DATE (+)
    AND Header.AGENT_ID = PersonEmail.PERSON_ID (+)
    AND Header.AGENT_ID = PersonPhone.PERSON_ID (+)
    /* Legal entity */
    AND Header.SOLDTO_LE_ID = SoldToLe.LEGAL_ENTITY_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1"""
    },
    {
        "name": "PO Lines with Line Type, Category & UOM",
        "description": "PO lines with line type name, item category, UOM display name, and source agreement reference (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Line.LINE_NUM,
    Line.ITEM_DESCRIPTION,
    Item.ITEM_NUMBER,
    Item.DESCRIPTION AS ITEM_ORIGINAL_DESCRIPTION,
    Line.VENDOR_PRODUCT_NUM AS SUPPLIER_ITEM_NUMBER,
    LineType.LINE_TYPE AS LINE_TYPE_NAME,
    CategoryPEO.CATEGORY_NAME,
    Line.QUANTITY,
    Line.UNIT_PRICE,
    Line.PURCHASE_BASIS,
    Line.ORDER_TYPE_LOOKUP_CODE AS VALUE_BASIS,
    SHIPPING_UOM.UNIT_OF_MEASURE AS UOM_DISPLAY,
    PRICING_UOM.UNIT_OF_MEASURE AS PRICING_UOM_DISPLAY,
    Line.CANCEL_FLAG,
    Line.CANCEL_DATE,
    Line.CANCEL_REASON,
    /* Source agreement reference */
    BlanketHdr.SEGMENT1 AS SOURCE_AGREEMENT_NUM,
    ContractHdr.SEGMENT1 AS CONTRACT_NUM
FROM
    PO_HEADERS_ALL Header,
    PO_LINES_ALL Line,
    PO_LINE_TYPES_VL LineType,
    EGP_SYSTEM_ITEMS_VL Item,
    EGP_CATEGORIES_VL CategoryPEO,
    INV_UNITS_OF_MEASURE_VL SHIPPING_UOM,
    INV_UNITS_OF_MEASURE_VL PRICING_UOM,
    PO_HEADERS_ALL BlanketHdr,
    PO_HEADERS_ALL ContractHdr
WHERE 1 = 1
    AND Header.PO_HEADER_ID = Line.PO_HEADER_ID
    AND Line.LINE_TYPE_ID = LineType.LINE_TYPE_ID
    AND Line.ITEM_ID = Item.INVENTORY_ITEM_ID (+)
    AND Line.CATEGORY_ID = CategoryPEO.CATEGORY_ID (+)
    AND Line.SHIPPING_UOM_CODE = SHIPPING_UOM.UOM_CODE (+)
    AND Line.UOM_CODE = PRICING_UOM.UOM_CODE (+)
    AND Line.FROM_HEADER_ID = BlanketHdr.PO_HEADER_ID (+)
    AND Line.CONTRACT_ID = ContractHdr.PO_HEADER_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1,
    Line.LINE_NUM"""
    },
    {
        "name": "Shipment Schedules with Ship-To Address",
        "description": "PO shipment schedules with full ship-to address, carrier, transport mode, and receiving tolerances (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Line.LINE_NUM,
    Line.ITEM_DESCRIPTION,
    LineLocation.SHIPMENT_NUM,
    LineLocation.QUANTITY AS SCHEDULE_QTY,
    SHIPPING_UOM.UNIT_OF_MEASURE AS UOM_DISPLAY,
    LineLocation.PRICE_OVERRIDE AS SHIPMENT_PRICE,
    TO_CHAR(LineLocation.NEED_BY_DATE, 'YYYY-MM-DD') AS NEED_BY_DATE,
    LineLocation.PROMISED_DATE,
    LineLocation.QUANTITY_RECEIVED,
    LineLocation.QUANTITY_BILLED,
    LineLocation.QUANTITY_CANCELLED,
    LineLocation.CANCEL_FLAG,
    LineLocation.TAXABLE_FLAG,
    LineLocation.COUNTRY_OF_ORIGIN_CODE,
    LineLocation.NOTE_TO_RECEIVER,
    /* Ship-to address (date-effective) */
    ShipToLoc.LOCATION_NAME AS SHIP_TO_LOCATION,
    ShipToLoc.ADDRESS_LINE_1 AS SHIP_TO_ADDRESS1,
    ShipToLoc.ADDRESS_LINE_2 AS SHIP_TO_ADDRESS2,
    ShipToLoc.TOWN_OR_CITY AS SHIP_TO_CITY,
    ShipToLoc.REGION_2 AS SHIP_TO_STATE,
    ShipToLoc.COUNTRY AS SHIP_TO_COUNTRY,
    ShipToLoc.POSTAL_CODE AS SHIP_TO_ZIP,
    /* Transport */
    CarrierParty.PARTY_NAME AS CARRIER_NAME,
    ModeOfTransport.MEANING AS MODE_OF_TRANSPORT,
    ServiceLevel.MEANING AS SERVICE_LEVEL,
    /* Receiving controls */
    LineLocation.DAYS_EARLY_RECEIPT_ALLOWED,
    LineLocation.DAYS_LATE_RECEIPT_ALLOWED
FROM
    PO_HEADERS_ALL Header,
    PO_LINES_ALL Line,
    PO_LINE_LOCATIONS_ALL LineLocation,
    INV_UNITS_OF_MEASURE_VL SHIPPING_UOM,
    HR_LOCATIONS_ALL_F_VL ShipToLoc,
    HZ_PARTIES CarrierParty,
    FND_LOOKUPS ModeOfTransport,
    FND_LOOKUPS ServiceLevel
WHERE 1 = 1
    AND Header.PO_HEADER_ID = Line.PO_HEADER_ID
    AND Line.PO_LINE_ID = LineLocation.PO_LINE_ID
    AND LineLocation.SHIPPING_UOM_CODE = SHIPPING_UOM.UOM_CODE (+)
    AND LineLocation.SHIP_TO_LOCATION_ID = ShipToLoc.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN ShipToLoc.EFFECTIVE_START_DATE (+) AND ShipToLoc.EFFECTIVE_END_DATE (+)
    AND LineLocation.CARRIER_ID = CarrierParty.PARTY_ID (+)
    AND LineLocation.MODE_OF_TRANSPORT = ModeOfTransport.LOOKUP_CODE (+)
    AND ModeOfTransport.LOOKUP_TYPE (+) = 'WSH_MODE_OF_TRANSPORT'
    AND LineLocation.SERVICE_LEVEL = ServiceLevel.LOOKUP_CODE (+)
    AND ServiceLevel.LOOKUP_TYPE (+) = 'WSH_SERVICE_LEVELS'
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1,
    Line.LINE_NUM,
    LineLocation.SHIPMENT_NUM"""
    },
    {
        "name": "Distributions with Requester & Deliver-To",
        "description": "PO distributions with requester name/email/phone, deliver-to location, destination type, and GL account (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Line.LINE_NUM,
    Line.ITEM_DESCRIPTION,
    Distribution.DISTRIBUTION_NUM,
    Distribution.QUANTITY_ORDERED,
    Distribution.QUANTITY_DELIVERED,
    Distribution.QUANTITY_BILLED,
    UOM.UNIT_OF_MEASURE AS UOM_DISPLAY,
    DestTypeLookup.MEANING AS DESTINATION_TYPE,
    /* Deliver-to details (date-effective) */
    DeliverToLocation.LOCATION_NAME AS DELIVER_TO_LOCATION,
    DeliverToLocation.ADDRESS_LINE_1 AS DELIVER_TO_ADDRESS,
    DeliverToLocation.TOWN_OR_CITY AS DELIVER_TO_CITY,
    /* Requester info (date-effective) */
    Requester.DISPLAY_NAME AS REQUESTER_NAME,
    RequesterEmail.EMAIL_ADDRESS AS REQUESTER_EMAIL,
    RequesterPhone.DISPLAY_PHONE_NUMBER AS REQUESTER_PHONE,
    /* Project info */
    Distribution.PJC_PROJECT_ID,
    Distribution.PJC_TASK_ID,
    Distribution.PJC_EXPENDITURE_ITEM_DATE
FROM
    PO_HEADERS_ALL Header,
    PO_LINES_ALL Line,
    PO_DISTRIBUTIONS_ALL Distribution,
    PO_LOOKUP_CODES DestTypeLookup,
    HR_LOCATIONS_ALL_F_VL DeliverToLocation,
    PER_PERSON_NAMES_F_V Requester,
    PER_EMAIL_ADDRESSES RequesterEmail,
    PER_DISPLAY_PHONES_V RequesterPhone,
    PER_ALL_PEOPLE_F PersonDPEO,
    INV_UNITS_OF_MEASURE_VL UOM
WHERE 1 = 1
    AND Distribution.PO_HEADER_ID = Header.PO_HEADER_ID
    AND Distribution.PO_LINE_ID = Line.PO_LINE_ID
    AND Line.SHIPPING_UOM_CODE = UOM.UOM_CODE (+)
    /* Destination type lookup */
    AND Distribution.DESTINATION_TYPE_CODE = DestTypeLookup.LOOKUP_CODE (+)
    AND DestTypeLookup.LOOKUP_TYPE (+) = 'DESTINATION TYPE'
    /* Deliver-to location (date-effective) */
    AND Distribution.DELIVER_TO_LOCATION_ID = DeliverToLocation.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN DeliverToLocation.EFFECTIVE_START_DATE (+) AND DeliverToLocation.EFFECTIVE_END_DATE (+)
    /* Requester name (date-effective) */
    AND Distribution.DELIVER_TO_PERSON_ID = Requester.PERSON_ID (+)
    AND TRUNC(SYSDATE) BETWEEN Requester.EFFECTIVE_START_DATE (+) AND Requester.EFFECTIVE_END_DATE (+)
    /* Requester email & phone via PER_ALL_PEOPLE_F */
    AND Distribution.DELIVER_TO_PERSON_ID = PersonDPEO.PERSON_ID (+)
    AND TRUNC(SYSDATE) BETWEEN PersonDPEO.EFFECTIVE_START_DATE (+) AND PersonDPEO.EFFECTIVE_END_DATE (+)
    AND PersonDPEO.PERSON_ID = RequesterEmail.PERSON_ID (+)
    AND PersonDPEO.PRIMARY_EMAIL_ID = RequesterEmail.EMAIL_ADDRESS_ID (+)
    AND PersonDPEO.PERSON_ID = RequesterPhone.PERSON_ID (+)
    AND PersonDPEO.PRIMARY_PHONE_ID = RequesterPhone.PHONE_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1,
    Line.LINE_NUM,
    Distribution.DISTRIBUTION_NUM"""
    },
    {
        "name": "Supplier Address & Contact Info",
        "description": "Supplier address from POZ_SUPPLIER_ADDRESS_V with party name from HZ_PARTIES (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    SupAddr.ADDRESS1,
    SupAddr.ADDRESS2,
    SupAddr.ADDRESS3,
    SupAddr.ADDRESS4,
    SupAddr.CITY,
    SupAddr.STATE,
    SupAddr.COUNTRY,
    SupAddr.POSTAL_CODE,
    HP.PARTY_NAME AS SUPPLIER_NAME
FROM
    POZ_SUPPLIER_ADDRESS_V SupAddr,
    HZ_PARTIES HP
WHERE 1 = 1
    AND SupAddr.PARTY_ID = HP.PARTY_ID"""
    },
    {
        "name": "PO with Business Unit & Legal Entity",
        "description": "PO report showing procurement BU name and sold-to legal entity with tax registration (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Header.DOCUMENT_STATUS,
    Header.CREATION_DATE,
    /* Business Unit (date-effective with classification filter) */
    ProcurementBu.NAME AS PROCUREMENT_BU_NAME,
    /* Legal Entity */
    SoldToLe.NAME AS LEGAL_ENTITY_NAME,
    SoldToLeReg.REGISTRATION_NUMBER AS TAX_REGISTRATION_NUMBER,
    /* LE Address */
    SoldToLeLocation.ADDRESS1 AS LE_ADDRESS1,
    SoldToLeLocation.CITY AS LE_CITY,
    SoldToLeLocation.STATE AS LE_STATE,
    SoldToLeLocation.COUNTRY AS LE_COUNTRY,
    SoldToLeLocation.POSTAL_CODE AS LE_POSTAL_CODE,
    /* Supplier */
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL Header,
    HR_ORGANIZATION_V ProcurementBu,
    XLE_ENTITY_PROFILES SoldToLe,
    XLE_REGISTRATIONS SoldToLeReg,
    HZ_LOCATIONS SoldToLeLocation,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES SupplierPartyName
WHERE 1 = 1
    /* BU join (date-effective + classification) */
    AND Header.PRC_BU_ID = ProcurementBu.ORGANIZATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN ProcurementBu.EFFECTIVE_START_DATE (+) AND ProcurementBu.EFFECTIVE_END_DATE (+)
    AND ProcurementBu.CLASSIFICATION_CODE (+) = 'FUN_BUSINESS_UNIT'
    /* Legal entity chain */
    AND Header.SOLDTO_LE_ID = SoldToLe.LEGAL_ENTITY_ID (+)
    AND SoldToLe.LEGAL_ENTITY_ID = SoldToLeReg.SOURCE_ID (+)
    AND SoldToLeReg.SOURCE_TABLE (+) = 'XLE_ENTITY_PROFILES'
    AND SoldToLeReg.IDENTIFYING_FLAG (+) = 'Y'
    AND SoldToLeReg.LOCATION_ID = SoldToLeLocation.LOCATION_ID (+)
    /* Supplier */
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1"""
    },
    {
        "name": "PO Version / Change Order History",
        "description": "Track PO revisions and change orders with version details (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Header.TYPE_LOOKUP_CODE AS DOCUMENT_TYPE,
    Version.REVISION_NUM,
    Version.CO_NUM AS CHANGE_ORDER_NUM,
    Version.CO_SEQUENCE,
    Version.CHANGE_ORDER_TYPE,
    Version.CHANGE_ORDER_DESC,
    Version.CHANGE_ORDER_STATUS,
    PO_BIP_HELPER.get_doc_revision_number(
        Version.CHANGE_ORDER_TYPE,
        Version.CO_SEQUENCE,
        Header.PO_HEADER_ID,
        Version.REVISION_NUM
    ) AS DISPLAY_REVISION_NUM,
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL Header,
    PO_VERSIONS Version,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES SupplierPartyName
WHERE 1 = 1
    AND Header.PO_HEADER_ID = Version.PO_HEADER_ID
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1,
    Version.CO_SEQUENCE"""
    },
    {
        "name": "Drop Ship PO Schedules",
        "description": "PO line locations flagged as drop ship with customer ship-to details (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Line.LINE_NUM,
    Line.ITEM_DESCRIPTION,
    LineLocation.SHIPMENT_NUM,
    LineLocation.QUANTITY,
    LineLocation.NEED_BY_DATE,
    LineLocation.DROP_SHIP_FLAG,
    LineLocation.SALES_ORDER_NUMBER,
    LineLocation.SALES_ORDER_LINE_NUMBER,
    LineLocation.CUSTOMER_PO_NUMBER,
    LineLocation.CUSTOMER_ITEM,
    LineLocation.CUSTOMER_ITEM_DESC,
    /* Customer ship-to from HZ_LOCATIONS */
    CustLocation.ADDRESS1 AS CUST_SHIP_TO_ADDRESS,
    CustLocation.CITY AS CUST_SHIP_TO_CITY,
    CustLocation.STATE AS CUST_SHIP_TO_STATE,
    CustLocation.COUNTRY AS CUST_SHIP_TO_COUNTRY,
    CustLocation.POSTAL_CODE AS CUST_SHIP_TO_ZIP,
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL Header,
    PO_LINES_ALL Line,
    PO_LINE_LOCATIONS_ALL LineLocation,
    HZ_LOCATIONS CustLocation,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES SupplierPartyName
WHERE 1 = 1
    AND Header.PO_HEADER_ID = Line.PO_HEADER_ID
    AND Line.PO_LINE_ID = LineLocation.PO_LINE_ID
    AND LineLocation.DESTINATION_TYPE_CODE = 'DROP SHIP'
    AND LineLocation.SHIP_TO_CUST_LOCATION_ID = CustLocation.LOCATION_ID (+)
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
ORDER BY
    Header.SEGMENT1,
    Line.LINE_NUM,
    LineLocation.SHIPMENT_NUM"""
    },
    {
        "name": "PO with Hazard Class & UN Numbers",
        "description": "PO lines with hazardous material classification details (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.SEGMENT1 AS PO_NUMBER,
    Line.LINE_NUM,
    Line.ITEM_DESCRIPTION,
    Item.ITEM_NUMBER,
    Line.QUANTITY,
    Line.UNIT_PRICE,
    UnNumber.UN_NUMBER AS UN_NUMBER,
    UnNumber.DESCRIPTION AS UN_NUMBER_DESCRIPTION,
    HazardClass.HAZARD_CLASS AS HAZARD_CLASS,
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME
FROM
    PO_HEADERS_ALL Header,
    PO_LINES_ALL Line,
    EGP_SYSTEM_ITEMS_VL Item,
    PO_HAZARD_CLASSES_VL HazardClass,
    PO_UN_NUMBERS_VL UnNumber,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES SupplierPartyName
WHERE 1 = 1
    AND Header.PO_HEADER_ID = Line.PO_HEADER_ID
    AND Line.ITEM_ID = Item.INVENTORY_ITEM_ID (+)
    AND Line.HAZARD_CLASS_ID = HazardClass.HAZARD_CLASS_ID (+)
    AND Line.UN_NUMBER_ID = UnNumber.UN_NUMBER_ID (+)
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
    AND (Line.HAZARD_CLASS_ID IS NOT NULL OR Line.UN_NUMBER_ID IS NOT NULL)
ORDER BY
    Header.SEGMENT1,
    Line.LINE_NUM"""
    },
    {
        "name": "Full PO Print Report (Header-Level)",
        "description": "Comprehensive PO print report matching Oracle's standard PO output layout - header section with all key fields (from Oracle PurchaseOrderDm)",
        "sql": """SELECT
    Header.PO_HEADER_ID,
    Header.SEGMENT1 AS PO_NUMBER,
    Header.REVISION_NUM,
    Header.SIGNATURE_REQUIRED_FLAG,
    Header.VENDOR_ORDER_NUM,
    Header.ACCEPTANCE_REQUIRED_FLAG,
    Header.ACCEPTANCE_DUE_DATE,
    Header.PAY_ON_CODE,
    Header.CURRENCY_CODE,
    Currency.NAME AS CURRENCY_NAME,
    /* Document style */
    DocStyle.DISPLAY_NAME AS DOCUMENT_STYLE,
    /* Version / Change Order */
    PO_BIP_HELPER.get_doc_revision_number(
        Version.CHANGE_ORDER_TYPE, Version.CO_SEQUENCE,
        Header.PO_HEADER_ID, Version.REVISION_NUM
    ) AS DISPLAY_REVISION,
    NVL(Version.CO_NUM, 0) AS CHANGE_ORDER_NUM,
    Version.CHANGE_ORDER_DESC,
    /* Buyer */
    PersonName.DISPLAY_NAME AS BUYER_NAME,
    PersonEmail.EMAIL_ADDRESS AS BUYER_EMAIL,
    PersonPhone.DISPLAY_PHONE_NUMBER AS BUYER_PHONE,
    PersonFax.DISPLAY_PHONE_NUMBER AS BUYER_FAX,
    /* Supplier */
    SupplierPartyName.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER,
    PozSupplierSite.CUSTOMER_NUM AS CUSTOMER_ACCOUNT_NUM,
    /* Terms */
    PaymentTerms.NAME AS PAYMENT_TERMS,
    FobLookup.MEANING AS FOB,
    FreightLookup.MEANING AS FREIGHT_TERMS,
    CarrierPartyName.PARTY_NAME AS CARRIER,
    /* Ship-to */
    ShipToLoc.LOCATION_NAME AS SHIP_TO_LOCATION,
    ShipToLoc.ADDRESS_LINE_1 AS SHIP_TO_ADDR1,
    ShipToLoc.ADDRESS_LINE_2 AS SHIP_TO_ADDR2,
    ShipToLoc.TOWN_OR_CITY AS SHIP_TO_CITY,
    ShipToLoc.REGION_2 AS SHIP_TO_STATE,
    ShipToLoc.POSTAL_CODE AS SHIP_TO_ZIP,
    ShipToLoc.COUNTRY AS SHIP_TO_COUNTRY,
    /* Bill-to */
    BillToLoc.LOCATION_NAME AS BILL_TO_LOCATION,
    BillToLoc.ADDRESS_LINE_1 AS BILL_TO_ADDR1,
    BillToLoc.TOWN_OR_CITY AS BILL_TO_CITY,
    BillToLoc.REGION_2 AS BILL_TO_STATE,
    BillToLoc.POSTAL_CODE AS BILL_TO_ZIP,
    BillToLoc.COUNTRY AS BILL_TO_COUNTRY,
    /* Legal entity */
    SoldToLe.NAME AS LEGAL_ENTITY,
    SoldToLeReg.REGISTRATION_NUMBER AS TAX_REG_NUM,
    /* Negotiation terms */
    NegotiationTerms.BODY AS TERMS_AND_CONDITIONS,
    NegotiationTerms.ENABLED_FLAG AS TC_ENABLED_FLAG
FROM
    PO_HEADERS_ALL Header,
    PO_DOC_STYLE_LINES_VL DocStyle,
    PO_VERSIONS Version,
    PON_BIDDING_TERMS_VL NegotiationTerms,
    POZ_SUPPLIERS Supplier,
    POZ_SUPPLIER_SITES_ALL_M PozSupplierSite,
    HZ_PARTIES SupplierPartyName,
    WSH_CARRIERS Carrier,
    HZ_PARTIES CarrierPartyName,
    HR_LOCATIONS_ALL_F_VL ShipToLoc,
    HR_LOCATIONS_ALL_F_VL BillToLoc,
    AP_TERMS_VL PaymentTerms,
    FND_LOOKUPS FobLookup,
    FND_LOOKUPS FreightLookup,
    PER_PERSON_NAMES_F_V PersonName,
    PER_EMAIL_ADDRESSES PersonEmail,
    PER_DISPLAY_PHONES_V PersonPhone,
    PER_DISPLAY_PHONES_V PersonFax,
    FND_CURRENCIES_VL Currency,
    XLE_ENTITY_PROFILES SoldToLe,
    XLE_REGISTRATIONS SoldToLeReg,
    HZ_LOCATIONS SoldToLeLocation
WHERE 1 = 1
    /* Style */
    AND Header.STYLE_ID = DocStyle.STYLE_ID
    AND Header.TYPE_LOOKUP_CODE = DocStyle.DOCUMENT_SUBTYPE
    /* Version */
    AND Header.PO_HEADER_ID = Version.PO_HEADER_ID
    /* Supplier */
    AND Header.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = SupplierPartyName.PARTY_ID (+)
    AND Header.VENDOR_SITE_ID = PozSupplierSite.VENDOR_SITE_ID (+)
    /* Terms */
    AND Header.TERMS_ID = PaymentTerms.TERM_ID (+)
    AND Header.FOB_LOOKUP_CODE = FobLookup.LOOKUP_CODE (+)
    AND FobLookup.LOOKUP_TYPE (+) = 'FOB'
    AND Header.FREIGHT_TERMS_LOOKUP_CODE = FreightLookup.LOOKUP_CODE (+)
    AND FreightLookup.LOOKUP_TYPE (+) = 'FREIGHT TERMS'
    /* Carrier */
    AND Header.CARRIER_ID = Carrier.CARRIER_ID (+)
    AND Carrier.CARRIER_ID = CarrierPartyName.PARTY_ID (+)
    /* Locations (date-effective) */
    AND Header.SHIP_TO_LOCATION_ID = ShipToLoc.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN ShipToLoc.EFFECTIVE_START_DATE (+) AND ShipToLoc.EFFECTIVE_END_DATE (+)
    AND Header.BILL_TO_LOCATION_ID = BillToLoc.LOCATION_ID (+)
    AND TRUNC(SYSDATE) BETWEEN BillToLoc.EFFECTIVE_START_DATE (+) AND BillToLoc.EFFECTIVE_END_DATE (+)
    /* Buyer (date-effective) */
    AND Header.AGENT_ID = PersonName.PERSON_ID (+)
    AND TRUNC(SYSDATE) BETWEEN PersonName.EFFECTIVE_START_DATE (+) AND PersonName.EFFECTIVE_END_DATE (+)
    AND Header.AGENT_ID = PersonEmail.PERSON_ID (+)
    AND Header.AGENT_ID = PersonPhone.PERSON_ID (+)
    AND Header.AGENT_ID = PersonFax.PERSON_ID (+)
    /* Currency */
    AND Header.CURRENCY_CODE = Currency.CURRENCY_CODE (+)
    /* Legal entity */
    AND Header.SOLDTO_LE_ID = SoldToLe.LEGAL_ENTITY_ID (+)
    AND SoldToLe.LEGAL_ENTITY_ID = SoldToLeReg.SOURCE_ID (+)
    AND SoldToLeReg.SOURCE_TABLE (+) = 'XLE_ENTITY_PROFILES'
    AND SoldToLeReg.IDENTIFYING_FLAG (+) = 'Y'
    AND SoldToLeReg.LOCATION_ID = SoldToLeLocation.LOCATION_ID (+)
    /* Negotiation terms */
    AND Header.PO_HEADER_ID = NegotiationTerms.PO_HEADER_ID (+)
    AND Header.SEGMENT1 IS NOT NULL
    AND Header.SEGMENT1 = :P_PO_NUMBER               /* BI Publisher Parameter */
ORDER BY
    Header.SEGMENT1"""
    },

    # ===================================================================
    # PROCUREMENT + AP FOCUSED REPORTS
    # ===================================================================
    {
        "name": "PO-to-Invoice Matching Report",
        "description": "3-way match: PO line vs Receipt vs AP Invoice - shows ordered, received, and invoiced quantities with variances",
        "sql": """SELECT
    PHA.SEGMENT1 AS PO_NUMBER,
    PLA.LINE_NUM AS PO_LINE,
    PLA.ITEM_DESCRIPTION,
    ESI.ITEM_NUMBER,
    PLA.UNIT_PRICE AS PO_UNIT_PRICE,
    PLLA.QUANTITY AS PO_QTY_ORDERED,
    NVL(PLLA.QUANTITY_RECEIVED, 0) AS QTY_RECEIVED,
    NVL(PLLA.QUANTITY_BILLED, 0) AS QTY_INVOICED,
    (PLLA.QUANTITY - NVL(PLLA.QUANTITY_RECEIVED, 0)) AS QTY_PENDING_RECEIPT,
    (NVL(PLLA.QUANTITY_RECEIVED, 0) - NVL(PLLA.QUANTITY_BILLED, 0)) AS QTY_RECEIVED_NOT_INVOICED,
    /* AP Invoice details */
    AIA.INVOICE_NUM,
    AIA.INVOICE_DATE,
    AIL.LINE_NUMBER AS INVOICE_LINE,
    AIL.AMOUNT AS INVOICE_LINE_AMOUNT,
    AIL.QUANTITY_INVOICED AS INV_QTY,
    AIL.UNIT_PRICE AS INV_UNIT_PRICE,
    AIL.MATCH_TYPE,
    /* Supplier */
    HP.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES HP,
    EGP_SYSTEM_ITEMS_VL ESI,
    AP_INVOICE_LINES_ALL AIL,
    AP_INVOICES_ALL AIA
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PHA.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = HP.PARTY_ID (+)
    AND PLA.ITEM_ID = ESI.INVENTORY_ITEM_ID (+)
    /* AP Invoice matched to PO */
    AND AIL.PO_HEADER_ID (+) = PHA.PO_HEADER_ID
    AND AIL.PO_LINE_ID (+) = PLA.PO_LINE_ID
    AND AIL.PO_LINE_LOCATION_ID (+) = PLLA.LINE_LOCATION_ID
    AND AIL.INVOICE_ID = AIA.INVOICE_ID (+)
    /* Filters */
    AND PHA.TYPE_LOOKUP_CODE = 'STANDARD'
    AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
    AND NVL(PLA.CANCEL_FLAG, 'N') = 'N'
    AND PHA.SEGMENT1 IS NOT NULL
ORDER BY
    PHA.SEGMENT1,
    PLA.LINE_NUM"""
    },
    {
        "name": "AP Aging / Outstanding Invoices",
        "description": "AP aging report showing unpaid invoices with aging buckets (current, 1-30, 31-60, 61-90, 90+ days)",
        "sql": """SELECT
    HP.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER,
    AIA.INVOICE_NUM,
    AIA.INVOICE_DATE,
    AIA.INVOICE_TYPE_LOOKUP_CODE AS INVOICE_TYPE,
    AIA.INVOICE_AMOUNT,
    AIA.INVOICE_CURRENCY_CODE AS CURRENCY,
    AIA.AMOUNT_PAID,
    (AIA.INVOICE_AMOUNT - NVL(AIA.AMOUNT_PAID, 0)) AS AMOUNT_REMAINING,
    AIA.PAYMENT_STATUS_FLAG,
    AIA.GL_DATE,
    AIA.DESCRIPTION AS INVOICE_DESCRIPTION,
    PayTerms.NAME AS PAYMENT_TERMS,
    /* Aging buckets based on invoice date */
    CASE
        WHEN (TRUNC(SYSDATE) - AIA.INVOICE_DATE) <= 0 THEN 'NOT YET DUE'
        WHEN (TRUNC(SYSDATE) - AIA.INVOICE_DATE) BETWEEN 1 AND 30 THEN '1-30 DAYS'
        WHEN (TRUNC(SYSDATE) - AIA.INVOICE_DATE) BETWEEN 31 AND 60 THEN '31-60 DAYS'
        WHEN (TRUNC(SYSDATE) - AIA.INVOICE_DATE) BETWEEN 61 AND 90 THEN '61-90 DAYS'
        ELSE '90+ DAYS'
    END AS AGING_BUCKET,
    (TRUNC(SYSDATE) - AIA.INVOICE_DATE) AS DAYS_OUTSTANDING,
    /* Business Unit */
    HAOU.NAME AS BUSINESS_UNIT
FROM
    AP_INVOICES_ALL AIA,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES HP,
    AP_TERMS_VL PayTerms,
    HR_ALL_ORGANIZATION_UNITS HAOU
WHERE 1 = 1
    AND AIA.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = HP.PARTY_ID (+)
    AND AIA.TERMS_ID = PayTerms.TERM_ID (+)
    AND AIA.ORG_ID = HAOU.ORGANIZATION_ID (+)
    /* Only unpaid or partially paid */
    AND AIA.PAYMENT_STATUS_FLAG IN ('N', 'P')
    /* Exclude cancelled */
    AND AIA.CANCELLED_DATE IS NULL
    AND AIA.INVOICE_AMOUNT != 0
ORDER BY
    HP.PARTY_NAME,
    AIA.INVOICE_DATE"""
    },
    {
        "name": "Spend Analysis by Supplier & Category",
        "description": "PO spend analysis showing total spend by supplier and item category with line counts",
        "sql": """SELECT
    HP.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER,
    Cat.CATEGORY_NAME,
    PHA.CURRENCY_CODE,
    COUNT(DISTINCT PHA.PO_HEADER_ID) AS PO_COUNT,
    COUNT(PLA.PO_LINE_ID) AS LINE_COUNT,
    SUM(CASE
        WHEN PLA.ORDER_TYPE_LOOKUP_CODE = 'QUANTITY'
        THEN NVL(PLA.QUANTITY, 0) * NVL(PLA.UNIT_PRICE, 0)
        ELSE NVL(PLA.AMOUNT, 0)
    END) AS TOTAL_ORDERED_AMOUNT,
    SUM(CASE
        WHEN PLA.ORDER_TYPE_LOOKUP_CODE = 'QUANTITY'
        THEN NVL(PLLA.QUANTITY_BILLED, 0) * NVL(PLA.UNIT_PRICE, 0)
        ELSE NVL(PLLA.AMOUNT_BILLED, 0)
    END) AS TOTAL_INVOICED_AMOUNT,
    MIN(PHA.CREATION_DATE) AS FIRST_PO_DATE,
    MAX(PHA.CREATION_DATE) AS LAST_PO_DATE
FROM
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES HP,
    EGP_CATEGORIES_VL Cat
WHERE 1 = 1
    AND PHA.PO_HEADER_ID = PLA.PO_HEADER_ID
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID
    AND PHA.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = HP.PARTY_ID (+)
    AND PLA.CATEGORY_ID = Cat.CATEGORY_ID (+)
    AND PHA.TYPE_LOOKUP_CODE = 'STANDARD'
    AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
    AND NVL(PLA.CANCEL_FLAG, 'N') = 'N'
    AND PHA.DOCUMENT_STATUS = 'APPROVED'
    AND PHA.CREATION_DATE >= ADD_MONTHS(SYSDATE, -12)  /* Last 12 months */
GROUP BY
    HP.PARTY_NAME,
    Supplier.SEGMENT1,
    Cat.CATEGORY_NAME,
    PHA.CURRENCY_CODE
ORDER BY
    TOTAL_ORDERED_AMOUNT DESC"""
    },
    {
        "name": "Requisition-to-PO-to-Receipt-to-Invoice Lifecycle",
        "description": "Full procure-to-pay lifecycle tracking from requisition through PO, receipt, and invoice",
        "sql": """SELECT
    /* Requisition */
    PRH.REQUISITION_NUMBER,
    PRH.DOCUMENT_STATUS AS REQ_STATUS,
    PRL.LINE_NUMBER AS REQ_LINE,
    PRL.ITEM_DESCRIPTION,
    PRL.QUANTITY AS REQ_QTY,
    PRL.UNIT_PRICE AS REQ_UNIT_PRICE,
    RequesterName.DISPLAY_NAME AS REQUESTER,
    /* Purchase Order */
    PHA.SEGMENT1 AS PO_NUMBER,
    PHA.DOCUMENT_STATUS AS PO_STATUS,
    PLA.LINE_NUM AS PO_LINE,
    PLA.QUANTITY AS PO_QTY,
    PLA.UNIT_PRICE AS PO_UNIT_PRICE,
    /* Receipt */
    NVL(PLLA.QUANTITY_RECEIVED, 0) AS QTY_RECEIVED,
    /* Invoice */
    NVL(PLLA.QUANTITY_BILLED, 0) AS QTY_INVOICED,
    AIA.INVOICE_NUM,
    AIA.INVOICE_DATE,
    AIA.INVOICE_AMOUNT,
    AIA.PAYMENT_STATUS_FLAG,
    /* Supplier */
    HP.PARTY_NAME AS SUPPLIER_NAME,
    /* Dates for lifecycle tracking */
    PRH.CREATION_DATE AS REQ_DATE,
    PHA.CREATION_DATE AS PO_DATE,
    PHA.APPROVED_DATE AS PO_APPROVED_DATE
FROM
    POR_REQUISITION_HEADERS_ALL PRH,
    POR_REQUISITION_LINES_ALL PRL,
    PO_HEADERS_ALL PHA,
    PO_LINES_ALL PLA,
    PO_LINE_LOCATIONS_ALL PLLA,
    PO_DISTRIBUTIONS_ALL PDA,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES HP,
    AP_INVOICE_LINES_ALL AIL,
    AP_INVOICES_ALL AIA,
    PER_PERSON_NAMES_F_V RequesterName
WHERE 1 = 1
    /* Req to PO link (through distributions) */
    AND PRH.REQUISITION_HEADER_ID = PRL.REQUISITION_HEADER_ID
    AND PRL.PO_HEADER_ID = PHA.PO_HEADER_ID (+)
    AND PRL.PO_LINE_ID = PLA.PO_LINE_ID (+)
    AND PLA.PO_LINE_ID = PLLA.PO_LINE_ID (+)
    AND PLLA.LINE_LOCATION_ID = PDA.LINE_LOCATION_ID (+)
    /* PO to Invoice */
    AND AIL.PO_HEADER_ID (+) = PHA.PO_HEADER_ID
    AND AIL.PO_LINE_ID (+) = PLA.PO_LINE_ID
    AND AIL.INVOICE_ID = AIA.INVOICE_ID (+)
    /* Supplier */
    AND PHA.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = HP.PARTY_ID (+)
    /* Requester (on req line, date-effective) */
    AND PRL.REQUESTER_ID = RequesterName.PERSON_ID (+)
    AND TRUNC(SYSDATE) BETWEEN RequesterName.EFFECTIVE_START_DATE (+) AND RequesterName.EFFECTIVE_END_DATE (+)
    /* Filters */
    AND NVL(PRL.CANCEL_FLAG, 'N') = 'N'
ORDER BY
    PRH.REQUISITION_NUMBER,
    PRL.LINE_NUMBER"""
    },
    {
        "name": "AP Payment History",
        "description": "Payment details showing checks/disbursements matched to invoices with bank info and void status",
        "sql": """SELECT
    HAOU.NAME AS BUSINESS_UNIT,
    HP.PARTY_NAME AS SUPPLIER_NAME,
    Supplier.SEGMENT1 AS SUPPLIER_NUMBER,
    /* Check/Payment details */
    AC.CHECK_NUMBER AS PAYMENT_NUMBER,
    AC.CHECK_DATE AS PAYMENT_DATE,
    AC.AMOUNT AS CHECK_AMOUNT,
    AC.CHECKRUN_NAME AS PAYMENT_BATCH,
    AC.BANK_ACCOUNT_NAME,
    AC.VOID_DATE,
    AC.CLEARED_AMOUNT,
    AC.CLEARED_DATE,
    PayType.PAYMENT_METHOD_CODE AS PAYMENT_METHOD,
    /* Invoice details */
    AIA.INVOICE_NUM,
    AIA.INVOICE_DATE,
    AIA.INVOICE_AMOUNT,
    AIA.INVOICE_TYPE_LOOKUP_CODE AS INVOICE_TYPE,
    AIA.DESCRIPTION AS INVOICE_DESCRIPTION,
    /* Payment allocation */
    AIP.AMOUNT AS PAYMENT_AMOUNT,
    AIP.ACCOUNTING_DATE,
    AIP.PERIOD_NAME,
    AIP.DISCOUNT_TAKEN,
    AIP.DISCOUNT_LOST,
    AIP.REVERSAL_FLAG,
    /* Currency */
    AIA.INVOICE_CURRENCY_CODE AS INVOICE_CURRENCY,
    AIA.PAYMENT_CURRENCY_CODE AS PAYMENT_CURRENCY
FROM
    AP_INVOICE_PAYMENTS_ALL AIP,
    AP_CHECKS_ALL AC,
    AP_INVOICES_ALL AIA,
    POZ_SUPPLIERS Supplier,
    HZ_PARTIES HP,
    HR_ALL_ORGANIZATION_UNITS HAOU,
    IBY_PAYMENTS_ALL PayType
WHERE 1 = 1
    AND AIP.CHECK_ID = AC.CHECK_ID (+)
    AND AIP.INVOICE_ID = AIA.INVOICE_ID (+)
    AND AC.VENDOR_ID = Supplier.VENDOR_ID (+)
    AND Supplier.PARTY_ID = HP.PARTY_ID (+)
    AND AIA.ORG_ID = HAOU.ORGANIZATION_ID (+)
    AND AC.PAYMENT_ID = PayType.PAYMENT_ID (+)
ORDER BY
    AC.CHECK_DATE DESC,
    AC.CHECK_NUMBER,
    AIA.INVOICE_NUM"""
    },
    {
        "name": "Received Not Invoiced (RNI)",
        "description": "Items received on POs but not yet invoiced - uses CTE pattern from production data model (Megan's RNI)",
        "sql": """WITH inv_rec AS (
    SELECT
        AIDA.RCV_TRANSACTION_ID,
        AIDA.ACCOUNTING_DATE,
        CASE
            WHEN AIDA.ACCOUNTING_DATE > TO_DATE(:P_AS_OF_DATE, 'MM-DD-YYYY')
            THEN 0
            ELSE AIDA.QUANTITY_INVOICED
        END AS QTY_INV
    FROM AP_INVOICE_DISTRIBUTIONS_ALL AIDA
    WHERE AIDA.RCV_TRANSACTION_ID IS NOT NULL
)
SELECT
    HOU.NAME AS BRANCH,
    HP.PARTY_NAME AS SUPPLIER_NAME,
    RSH.RECEIPT_NUM,
    RSL.LINE_NUM AS RECEIPT_LINE,
    PHA.SEGMENT1 AS PO_NUMBER,
    PLA.LINE_NUM AS PO_LINE,
    ESI.ITEM_NUMBER,
    RT.TRANSACTION_DATE AS RECEIPT_DATE,
    RT.QUANTITY AS QTY_RECEIVED,
    SUM(NVL(inv_rec.QTY_INV, 0)) AS QTY_INVOICED,
    RT.QUANTITY - SUM(NVL(inv_rec.QTY_INV, 0)) AS QTY_OPEN,
    RT.PO_UNIT_PRICE AS UNIT_COST,
    (RT.QUANTITY - SUM(NVL(inv_rec.QTY_INV, 0))) * RT.PO_UNIT_PRICE AS AMOUNT_OPEN
FROM
    RCV_TRANSACTIONS RT
    JOIN RCV_SHIPMENT_HEADERS RSH
        ON RSH.SHIPMENT_HEADER_ID = RT.SHIPMENT_HEADER_ID
    JOIN RCV_SHIPMENT_LINES RSL
        ON RSL.SHIPMENT_LINE_ID = RT.SHIPMENT_LINE_ID
    JOIN PO_HEADERS_ALL PHA
        ON PHA.PO_HEADER_ID = RT.PO_HEADER_ID
    JOIN PO_LINES_ALL PLA
        ON PLA.PO_LINE_ID = RT.PO_LINE_ID
    LEFT JOIN EGP_SYSTEM_ITEMS_B ESI
        ON ESI.INVENTORY_ITEM_ID = PLA.ITEM_ID
        AND ESI.ORGANIZATION_ID = RT.ORGANIZATION_ID
    LEFT JOIN inv_rec
        ON inv_rec.RCV_TRANSACTION_ID = RT.TRANSACTION_ID
    LEFT JOIN POZ_SUPPLIERS Supplier
        ON Supplier.VENDOR_ID = PHA.VENDOR_ID
    LEFT JOIN HZ_PARTIES HP
        ON Supplier.PARTY_ID = HP.PARTY_ID
    LEFT JOIN HR_ORGANIZATION_UNITS_F_TL HOU
        ON HOU.ORGANIZATION_ID = RT.ORGANIZATION_ID
        AND HOU.LANGUAGE = USERENV('LANG')
        AND TRUNC(SYSDATE) BETWEEN HOU.EFFECTIVE_START_DATE AND HOU.EFFECTIVE_END_DATE
WHERE
    RT.TRANSACTION_TYPE = 'DELIVER'
    AND RT.TRANSACTION_DATE <= TO_DATE(:P_AS_OF_DATE, 'MM-DD-YYYY')
GROUP BY
    HOU.NAME, HP.PARTY_NAME, RSH.RECEIPT_NUM, RSL.LINE_NUM,
    PHA.SEGMENT1, PLA.LINE_NUM, ESI.ITEM_NUMBER,
    RT.TRANSACTION_DATE, RT.QUANTITY, RT.PO_UNIT_PRICE
HAVING
    RT.QUANTITY - SUM(NVL(inv_rec.QTY_INV, 0)) > 0  /* Only show open items */
ORDER BY
    RSH.RECEIPT_NUM, RSL.LINE_NUM"""
    },
    {
        "name": "Uninvoiced Foreign Imports",
        "description": "Received PO items from foreign suppliers not yet invoiced - uses CTE pattern from production data model",
        "sql": """WITH rct_base AS (
    SELECT
        SL.PO_HEADER_ID,
        SL.PO_LINE_ID,
        SL.PO_LINE_LOCATION_ID,
        SUM(SL.QUANTITY_RECEIVED) AS QUANTITY,
        T.PO_UNIT_PRICE
    FROM RCV_SHIPMENT_LINES SL
    JOIN RCV_TRANSACTIONS T
        ON SL.SHIPMENT_LINE_ID = T.SHIPMENT_LINE_ID
    WHERE T.TRANSACTION_TYPE = 'DELIVER'
        AND SL.SHIPMENT_LINE_STATUS_CODE = 'FULLY RECEIVED'
    GROUP BY SL.PO_HEADER_ID, SL.PO_LINE_ID, SL.PO_LINE_LOCATION_ID, T.PO_UNIT_PRICE
),
inv AS (
    SELECT
        PO_HEADER_ID,
        PO_LINE_ID,
        PO_LINE_LOCATION_ID,
        SUM(QUANTITY_INVOICED) AS QTY_INVOICED
    FROM AP_INVOICE_LINES_ALL
    GROUP BY PO_HEADER_ID, PO_LINE_ID, PO_LINE_LOCATION_ID
)
SELECT DISTINCT
    PSV.VENDOR_NAME AS SUPPLIER,
    PHA.SEGMENT1 AS PO_NUMBER,
    PLA.LINE_NUM AS PO_LINE,
    Items.ITEM_NUMBER,
    RCT.QUANTITY AS QTY_RECEIVED,
    (RCT.QUANTITY - NVL(INV.QTY_INVOICED, 0)) AS UNINVOICED_QTY,
    PLA.UNIT_PRICE AS PO_UNIT_COST,
    (RCT.QUANTITY - NVL(INV.QTY_INVOICED, 0)) * PLA.UNIT_PRICE AS UNINVOICED_AMOUNT
FROM rct_base RCT
JOIN PO_HEADERS_ALL PHA ON RCT.PO_HEADER_ID = PHA.PO_HEADER_ID
JOIN PO_LINES_ALL PLA ON PLA.PO_LINE_ID = RCT.PO_LINE_ID
    AND RCT.PO_HEADER_ID = PLA.PO_HEADER_ID
JOIN POZ_SUPPLIERS_V PSV ON PSV.VENDOR_ID = PHA.VENDOR_ID
JOIN POZ_SUPPLIER_SITES_V PSSV ON PSSV.VENDOR_SITE_ID = PHA.VENDOR_SITE_ID
LEFT JOIN inv ON INV.PO_HEADER_ID = RCT.PO_HEADER_ID
    AND INV.PO_LINE_ID = RCT.PO_LINE_ID
JOIN EGP_SYSTEM_ITEMS_B Items ON PLA.ITEM_ID = Items.INVENTORY_ITEM_ID
WHERE
    PSSV.PAY_GROUP_LOOKUP_CODE = 'FOREIGN'
    AND (RCT.QUANTITY - NVL(INV.QTY_INVOICED, 0)) > 0
    AND PLA.LINE_STATUS != 'CANCELLED'
ORDER BY
    PSV.VENDOR_NAME, PHA.SEGMENT1, PLA.LINE_NUM"""
    },

    # ===================================================================
    # SHIPPER / BILL OF LADING EXAMPLES (from LSB production data model)
    # ===================================================================
    {
        "name": "Shipper G_9 - Mini Master (OM + Shipping Bridge)",
        "description": "Bridge table linking OM orders to shipping details with LPN, tracking, and delivery info - used as the base for Shipper document joins",
        "sql": """SELECT DISTINCT
    DHA.ORDER_NUMBER,
    DHA.HEADER_ID,
    DLA.LINE_ID,
    DLA.LINE_NUMBER,
    DFLA.FULFILL_LINE_NUMBER,
    DFLA.FULFILL_LINE_ID,
    DFLA.INVENTORY_ITEM_ID,
    WDD.SALES_ORDER_NUMBER,
    WDD.SALES_ORDER_LINE_NUMBER,
    WDD.SOURCE_LINE_NUMBER,
    WDD.DELIVERY_DETAIL_ID,
    DHA.ORDER_TYPE_CODE,
    DHA.STATUS_CODE,
    ILPN.LICENSE_PLATE_NUMBER,
    WDD.TRACKING_NUMBER,
    WDA.DELIVERY_ID,
    WDD.SHIP_METHOD_CODE
FROM
    DOO_HEADERS_ALL DHA
JOIN DOO_LINES_ALL DLA
    ON DHA.HEADER_ID = DLA.HEADER_ID
JOIN DOO_FULFILL_LINES_ALL DFLA
    ON DLA.LINE_ID = DFLA.LINE_ID
JOIN WSH_DELIVERY_DETAILS WDD
    ON WDD.SALES_ORDER_NUMBER = DHA.ORDER_NUMBER
    AND DFLA.FULFILL_LINE_ID = WDD.SOURCE_SHIPMENT_ID
JOIN WSH_DELIVERY_ASSIGNMENTS WDA
    ON WDA.DELIVERY_DETAIL_ID = WDD.DELIVERY_DETAIL_ID
LEFT JOIN INV_LICENSE_PLATE_NUMBERS ILPN
    ON WDD.PARENT_LPN_ID = ILPN.LPN_ID
WHERE 1 = 1
    AND DHA.STATUS_CODE NOT IN ('DOO_DRAFT', 'DOO_REFERENCE', 'DOO_CREDIT_REVIEW_PENDING')
ORDER BY
    DLA.LINE_NUMBER ASC"""
    },
    {
        "name": "Shipper - Work Order by Sales Order Line",
        "description": "Links each sales order line to its manufacturing work order via the supply chain module (DOS tables)",
        "sql": """SELECT DISTINCT
    DSBOD.WORK_ORDER_NUMBER        AS WO_LINE,
    DHA.ORDER_NUMBER,
    DHA.HEADER_ID,
    DLA.LINE_NUMBER,
    DFLA.FULFILL_LINE_NUMBER,
    DSL.LINE_ID                    AS SUPPLY_LINE_ID,
    DSH.HEADER_ID                  AS SUPPLY_HEADER_ID
FROM
    DOO_HEADERS_ALL            DHA
JOIN DOO_LINES_ALL              DLA
    ON DLA.HEADER_ID = DHA.HEADER_ID
JOIN DOO_FULFILL_LINES_ALL      DFLA
    ON DFLA.LINE_ID = DLA.LINE_ID
JOIN DOS_SUPPLY_HEADERS         DSH
    ON DSH.SUPPLY_ORDER_REFERENCE_ID = DFLA.HEADER_ID
    AND DSH.INTERFACE_SOURCE_CODE     = 'DOO'
JOIN DOS_SUPPLY_LINES           DSL
    ON DSL.HEADER_ID = DSH.HEADER_ID
    AND DSL.SUPPLY_ORDER_REFERENCE_LINE_ID = DFLA.FULFILL_LINE_ID
JOIN DOS_SUPPLY_TRACKING_LINES  DSTL
    ON DSTL.LINE_ID   = DSL.LINE_ID
    AND DSTL.HEADER_ID = DSL.HEADER_ID
JOIN DOS_SUPPLY_MAKE_ORDER_DTLS DSBOD
    ON DSBOD.TRACKING_LINE_ID = DSTL.TRACKING_LINE_ID
WHERE 1 = 1"""
    },
    {
        "name": "Shipper - Transfer Order Details",
        "description": "Transfer order lines on the Shipper document with shipped/delivered quantities, destination org, and order type flag (SCM module)",
        "sql": """SELECT DISTINCT
    TOH.HEADER_NUMBER,
    TOL.LINE_NUMBER,
    TOL.QTY_UOM_CODE               AS UOM,
    TOL.REQUESTED_QTY              AS TO_ORDER_QTY,
    WDD.SHIPPED_QUANTITY           AS SHIPPED_QTY,
    WDD.DELIVERED_QUANTITY         AS DELIVERED_QTY,
    DFLA.SOURCE_ORDER_NUMBER,
    WDD.DELIVERY_DETAIL_ID,
    WDD.INVENTORY_ITEM_ID,
    A.CONTEXT_CODE,
    B.DESCRIPTION                  AS TRANS_DESCRIPTION,
    HAOT.NAME,
    WDA.DELIVERY_ID,
    CASE
        WHEN WDD.SOURCE_LINE_TYPE = 'TRANSFER_ORDER' THEN 'TO'
        ELSE WDD.SOURCE_LINE_TYPE
    END AS TO_ORDER_TYPE_CODE
FROM WSH_DELIVERY_DETAILS WDD
JOIN INV_TRANSFER_ORDER_HEADERS TOH
    ON TOH.HEADER_NUMBER = WDD.SALES_ORDER_NUMBER
JOIN INV_TRANSFER_ORDER_LINES TOL
    ON TOH.HEADER_ID = TOL.HEADER_ID
LEFT JOIN DOO_FULFILL_LINES_ALL DFLA
    ON TOL.ORIGINAL_REQUEST_LINE_ID = DFLA.FULFILL_LINE_ID
LEFT JOIN EGO_ITEM_EFF_B A
    ON A.INVENTORY_ITEM_ID = WDD.INVENTORY_ITEM_ID
LEFT JOIN FND_VS_VALUES_VL B
    ON A.ATTRIBUTE_CHAR10 = B.VALUE
JOIN HR_ALL_ORGANIZATION_UNITS_TL HAOT
    ON HAOT.ORGANIZATION_ID = TOL.DESTINATION_ORGANIZATION_ID
JOIN WSH_DELIVERY_ASSIGNMENTS WDA
    ON WDA.DELIVERY_DETAIL_ID = WDD.DELIVERY_DETAIL_ID
WHERE A.CONTEXT_CODE = 'LaSalleBristolAttributes'"""
    },
    {
        "name": "Shipper - Content Server Notes Bridge (G_10)",
        "description": "Bridge query linking fulfillment lines to Content Server documents for line-level notes on the Shipper (uses FND_ATTACHED_DOCUMENTS + FND_DOCUMENTS_TL)",
        "sql": """SELECT
    FAD.PK1_VALUE,
    FDT.DM_VERSION_NUMBER
FROM
    FND_ATTACHED_DOCUMENTS FAD,
    FND_DOCUMENTS_TL       FDT
WHERE 1 = 1
    AND FAD.DOCUMENT_ID = FDT.DOCUMENT_ID
    AND FAD.ENTITY_NAME = 'DOO_FULFILL_LINES_ALL'"""
    },
]
