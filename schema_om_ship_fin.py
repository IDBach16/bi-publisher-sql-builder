"""
Oracle Fusion Cloud - Order Management, Shipping & Financials Schema Reference
Sources:
  - OM: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/oedsc/ (DOO tables)
  - Shipping: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/oedsc/ (WSH tables)
  - Financials: https://docs.oracle.com/en/cloud/saas/financials/26a/oedmf/ (AP/AR tables)
"""

# ============================================================================
# TABLE RELATIONSHIPS (JOIN KEYS)
# ============================================================================
OM_SHIP_FIN_RELATIONSHIPS = {
    # OM internal
    "DOO_HEADERS_ALL -> DOO_LINES_ALL": "DOO_HEADERS_ALL.HEADER_ID = DOO_LINES_ALL.HEADER_ID",
    "DOO_LINES_ALL -> DOO_FULFILL_LINES_ALL": "DOO_LINES_ALL.LINE_ID = DOO_FULFILL_LINES_ALL.LINE_ID",
    # OM to Shipping
    "DOO_HEADERS_ALL -> WSH_DELIVERY_DETAILS": "DOO_HEADERS_ALL.HEADER_ID = WSH_DELIVERY_DETAILS.SOURCE_HEADER_ID",
    "DOO_LINES_ALL -> WSH_DELIVERY_DETAILS": "DOO_LINES_ALL.LINE_ID = WSH_DELIVERY_DETAILS.SOURCE_LINE_ID",
    # Shipping internal
    "WSH_DELIVERY_DETAILS -> WSH_DELIVERY_ASSIGNMENTS": "WSH_DELIVERY_DETAILS.DELIVERY_DETAIL_ID = WSH_DELIVERY_ASSIGNMENTS.DELIVERY_DETAIL_ID",
    "WSH_NEW_DELIVERIES -> WSH_DELIVERY_ASSIGNMENTS": "WSH_NEW_DELIVERIES.DELIVERY_ID = WSH_DELIVERY_ASSIGNMENTS.DELIVERY_ID",
    # AP internal
    "AP_INVOICES_ALL -> AP_INVOICE_LINES_ALL": "AP_INVOICES_ALL.INVOICE_ID = AP_INVOICE_LINES_ALL.INVOICE_ID",
    "AP_INVOICE_LINES_ALL -> AP_INVOICE_DISTRIBUTIONS_ALL": "AP_INVOICE_LINES_ALL.INVOICE_ID = AP_INVOICE_DISTRIBUTIONS_ALL.INVOICE_ID AND AP_INVOICE_LINES_ALL.LINE_NUMBER = AP_INVOICE_DISTRIBUTIONS_ALL.INVOICE_LINE_NUMBER",
    "AP_INVOICES_ALL -> AP_INVOICE_PAYMENTS_ALL": "AP_INVOICES_ALL.INVOICE_ID = AP_INVOICE_PAYMENTS_ALL.INVOICE_ID",
    "AP_INVOICE_PAYMENTS_ALL -> AP_CHECKS_ALL": "AP_INVOICE_PAYMENTS_ALL.CHECK_ID = AP_CHECKS_ALL.CHECK_ID",
    "AP_INVOICES_ALL -> AP_HOLDS_ALL": "AP_INVOICES_ALL.INVOICE_ID = AP_HOLDS_ALL.INVOICE_ID",
    "AP_INVOICES_ALL -> AP_PAYMENT_SCHEDULES_ALL": "AP_INVOICES_ALL.INVOICE_ID = AP_PAYMENT_SCHEDULES_ALL.INVOICE_ID",
    "AP_INVOICES_ALL -> AP_TERMS_B": "AP_INVOICES_ALL.TERMS_ID = AP_TERMS_B.TERM_ID",
    "AP_TERMS_B -> AP_TERMS_TL": "AP_TERMS_B.TERM_ID = AP_TERMS_TL.TERM_ID",
    "AP_TERMS_B -> AP_TERMS_LINES": "AP_TERMS_B.TERM_ID = AP_TERMS_LINES.TERM_ID",
    "AP_CHECKS_ALL -> IBY_PAYMENTS_ALL": "AP_CHECKS_ALL.PAYMENT_ID = IBY_PAYMENTS_ALL.PAYMENT_ID",
    "IBY_PAYMENTS_ALL -> IBY_PAY_INSTRUCTIONS_ALL": "IBY_PAYMENTS_ALL.PAYMENT_INSTRUCTION_ID = IBY_PAY_INSTRUCTIONS_ALL.PAYMENT_INSTRUCTION_ID",
    "AP_INVOICES_ALL -> AP_PREPAY_HISTORY_ALL": "AP_INVOICES_ALL.INVOICE_ID = AP_PREPAY_HISTORY_ALL.INVOICE_ID",
    "AP_CHECKS_ALL -> AP_PAYMENT_HISTORY_ALL": "AP_CHECKS_ALL.CHECK_ID = AP_PAYMENT_HISTORY_ALL.CHECK_ID",
    "AP_CHECKS_ALL -> CE_BANK_ACCOUNTS": "AP_CHECKS_ALL.CE_BANK_ACCT_USE_ID = CE_BANK_ACCOUNTS.BANK_ACCOUNT_ID",
    # AP to PO
    "AP_INVOICE_LINES_ALL -> PO_HEADERS_ALL": "AP_INVOICE_LINES_ALL.PO_HEADER_ID = PO_HEADERS_ALL.PO_HEADER_ID",
    "AP_INVOICE_LINES_ALL -> PO_LINES_ALL": "AP_INVOICE_LINES_ALL.PO_LINE_ID = PO_LINES_ALL.PO_LINE_ID",
    "AP_INVOICE_LINES_ALL -> PO_LINE_LOCATIONS_ALL": "AP_INVOICE_LINES_ALL.PO_LINE_LOCATION_ID = PO_LINE_LOCATIONS_ALL.LINE_LOCATION_ID",
    "AP_INVOICE_LINES_ALL -> PO_DISTRIBUTIONS_ALL": "AP_INVOICE_LINES_ALL.PO_DISTRIBUTION_ID = PO_DISTRIBUTIONS_ALL.PO_DISTRIBUTION_ID",
    # AP to Supplier
    "AP_INVOICES_ALL -> POZ_SUPPLIERS": "AP_INVOICES_ALL.VENDOR_ID = POZ_SUPPLIERS.VENDOR_ID",
    "AP_CHECKS_ALL -> POZ_SUPPLIERS": "AP_CHECKS_ALL.VENDOR_ID = POZ_SUPPLIERS.VENDOR_ID",
    # AR internal
    "RA_CUSTOMER_TRX_ALL -> RA_CUSTOMER_TRX_LINES_ALL": "RA_CUSTOMER_TRX_ALL.CUSTOMER_TRX_ID = RA_CUSTOMER_TRX_LINES_ALL.CUSTOMER_TRX_ID",
}

# ============================================================================
# ORDER MANAGEMENT - DOO TABLES
# ============================================================================

DOO_HEADERS_ALL = {
    "description": "Sales order headers (Order Management). One row per sales order.",
    "primary_key": "HEADER_ID",
    "columns": {
        "HEADER_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique identifier of the sales order"},
        "ORDER_NUMBER": {"type": "VARCHAR2(50)", "nullable": False, "desc": "Sales order number (user-visible)"},
        "STATUS_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Order status"},
        "ORDERED_DATE": {"type": "DATE", "nullable": False, "desc": "Date when items were ordered"},
        "SOLD_TO_CUSTOMER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to customer ID"},
        "SOLD_TO_CONTACT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to contact ID"},
        "SOLD_TO_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to party ID (FK to HZ_PARTIES)"},
        "TRANSACTIONAL_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Currency code on order header"},
        "APPLIED_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Currency code applied by Pricing"},
        "ORDER_TYPE_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Type of order placed"},
        "CUSTOMER_PO_NUMBER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Customer purchase order number"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Business unit ID"},
        "OPEN_FLAG": {"type": "VARCHAR2(1)", "nullable": False, "desc": "Y if order is not closed or cancelled"},
        "CANCELED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if order is cancelled"},
        "SUBMITTED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "N=not submitted, Y=validated and submitted"},
        "SUBMITTED_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "Date/time of order submission"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking version"},
    }
}

DOO_LINES_ALL = {
    "description": "Sales order lines (Order Management). One row per order line.",
    "primary_key": "LINE_ID",
    "columns": {
        "LINE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique identifier of the order line"},
        "HEADER_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Order header ID (FK to DOO_HEADERS_ALL)"},
        "LINE_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Line number"},
        "DISPLAY_LINE_NUMBER": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Line number for display"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Inventory item ID (FK to EGP_SYSTEM_ITEMS)"},
        "ITEM_TYPE_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Item type grouping"},
        "ITEM_SUB_TYPE_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Item sub-type (Model/Service/One-Time)"},
        "ORDERED_QTY": {"type": "NUMBER", "nullable": True, "desc": "Quantity ordered"},
        "CANCELED_QTY": {"type": "NUMBER", "nullable": True, "desc": "Cancelled quantity"},
        "FULFILLED_QTY": {"type": "NUMBER", "nullable": True, "desc": "Fulfilled quantity"},
        "SHIPPED_QTY": {"type": "NUMBER", "nullable": True, "desc": "Shipped quantity"},
        "RMA_DELIVERED_QTY": {"type": "NUMBER", "nullable": True, "desc": "RMA delivered quantity"},
        "ORDERED_UOM": {"type": "VARCHAR2(3)", "nullable": False, "desc": "Unit of measure for ordered quantity"},
        "UNIT_LIST_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Base selling price before discounts"},
        "UNIT_SELLING_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Price per unit buyer paid"},
        "EXTENDED_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Line amount (qty * price)"},
        "STATUS_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Order line status"},
        "OPEN_FLAG": {"type": "VARCHAR2(1)", "nullable": False, "desc": "Y if line not closed/cancelled"},
        "CANCELED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if line cancelled"},
        "ON_HOLD": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if line on hold"},
        "SCHEDULE_SHIP_DATE": {"type": "DATE", "nullable": True, "desc": "Expected ship date"},
        "ACTUAL_SHIP_DATE": {"type": "DATE", "nullable": True, "desc": "Actual ship date"},
        "FULFILLMENT_DATE": {"type": "DATE", "nullable": True, "desc": "Date line was fulfilled"},
        "SOURCE_LINE_ID": {"type": "VARCHAR2(50)", "nullable": False, "desc": "Source order line ID"},
        "SOURCE_LINE_NUMBER": {"type": "VARCHAR2(100)", "nullable": False, "desc": "Source line number"},
        "SOURCE_ORDER_ID": {"type": "VARCHAR2(50)", "nullable": False, "desc": "Source order ID in order capture"},
        "SOURCE_ORDER_NUMBER": {"type": "VARCHAR2(50)", "nullable": False, "desc": "Source order number"},
        "SOURCE_ORDER_SYSTEM": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Source order capture system"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Business unit ID"},
        "INVENTORY_ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Inventory organization ID"},
        "QUANTITY_PER_MODEL": {"type": "NUMBER", "nullable": True, "desc": "Component qty per model"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking version"},
    }
}

# ============================================================================
# SHIPPING - WSH TABLES
# ============================================================================

WSH_NEW_DELIVERIES = {
    "description": "Shipment/delivery headers. One row per shipment.",
    "primary_key": "DELIVERY_ID",
    "columns": {
        "DELIVERY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique delivery identifier"},
        "DELIVERY_NAME": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Shipment name"},
        "DELIVERY_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "STANDARD or CONSOLIDATED"},
        "STATUS_CODE": {"type": "VARCHAR2(2)", "nullable": True, "desc": "Delivery status (OP=Open, CL=Closed, etc.)"},
        "PLANNED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "N=unplanned, Y=planned"},
        "INITIAL_PICKUP_DATE": {"type": "DATE", "nullable": True, "desc": "First pickup date"},
        "ULTIMATE_DROPOFF_DATE": {"type": "DATE", "nullable": True, "desc": "Final dropoff date"},
        "ACTUAL_SHIP_DATE": {"type": "DATE", "nullable": True, "desc": "Actual ship date"},
        "DELIVERED_DATE": {"type": "DATE", "nullable": True, "desc": "Date delivered to customer"},
        "ACTUAL_DELIVERY_DATE": {"type": "DATE", "nullable": True, "desc": "Actual delivery date"},
        "CONFIRM_DATE": {"type": "DATE", "nullable": True, "desc": "Ship confirm date"},
        "SHIP_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Shipping method code"},
        "CARRIER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Freight carrier ID"},
        "WAYBILL": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Tracking/waybill number"},
        "SERVICE_LEVEL": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Service level"},
        "MODE_OF_TRANSPORT": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Mode of transport"},
        "INITIAL_PICKUP_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Pickup location ID"},
        "ULTIMATE_DROPOFF_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Dropoff location ID"},
        "SHIP_TO_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ship-to party ID"},
        "SOLD_TO_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to party ID"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Inventory organization ID"},
        "SOURCE_HEADER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source order header ID"},
        "FREIGHT_TERMS_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Freight terms code"},
        "FOB_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "FOB code"},
        "CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Currency code for freight costs"},
        "BILL_OF_LADING_NUMBER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Bill of lading number"},
        "PACKING_SLIP_NUMBER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Packing slip number"},
        "COMMERCIAL_INVOICE_NUMBER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Commercial invoice number"},
        "BOOKING_NUMBER": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Carrier booking number"},
        "COD_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Cash on delivery amount"},
        "COD_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "COD currency code"},
        "GROSS_WEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Gross weight"},
        "NET_WEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Net weight"},
        "WEIGHT_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Weight UOM"},
        "VOLUME": {"type": "NUMBER", "nullable": True, "desc": "Volume"},
        "VOLUME_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Volume UOM"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking version"},
    }
}

WSH_DELIVERY_DETAILS = {
    "description": "Shipment line details. One row per item/line on a shipment.",
    "primary_key": "DELIVERY_DETAIL_ID",
    "columns": {
        "DELIVERY_DETAIL_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique shipment line identifier"},
        "SOURCE_HEADER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source order header ID (e.g., DOO_HEADERS_ALL.HEADER_ID)"},
        "SOURCE_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source order line ID (e.g., DOO_LINES_ALL.LINE_ID)"},
        "SOURCE_HEADER_NUMBER": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Source order number (user-visible)"},
        "SOURCE_LINE_NUMBER": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Source line number (user-visible)"},
        "SOURCE_SHIPMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source shipment ID"},
        "SOURCE_SHIPMENT_NUMBER": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Source shipment number"},
        "SOURCE_LINE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Type of source line"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Item ID (FK to EGP_SYSTEM_ITEMS)"},
        "ITEM_DESCRIPTION": {"type": "VARCHAR2(250)", "nullable": True, "desc": "Item description"},
        "SRC_REQUESTED_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Original quantity ordered from source"},
        "SRC_REQUESTED_QUANTITY_UOM": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Source ordered quantity UOM"},
        "REQUESTED_QUANTITY": {"type": "NUMBER", "nullable": False, "desc": "Shipping quantity for customer"},
        "REQUESTED_QUANTITY_UOM": {"type": "VARCHAR2(3)", "nullable": False, "desc": "Requested quantity UOM"},
        "SHIPPED_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Shipped quantity"},
        "DELIVERED_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Delivered quantity"},
        "CANCELLED_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Cancelled quantity"},
        "PICKED_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Picked quantity"},
        "RELEASED_STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Lifecycle status (ready to release, released, staged, shipped, backordered)"},
        "TRACKING_NUMBER": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Tracking number"},
        "LOT_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Lot number"},
        "SERIAL_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Serial number"},
        "REVISION": {"type": "VARCHAR2(18)", "nullable": True, "desc": "Item revision"},
        "SUBINVENTORY": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Subinventory"},
        "LOCATOR_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Locator ID"},
        "NET_WEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Net weight"},
        "GROSS_WEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Gross weight"},
        "WEIGHT_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Weight UOM"},
        "VOLUME": {"type": "NUMBER", "nullable": True, "desc": "Volume"},
        "VOLUME_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Volume UOM"},
        "TP_STATUS_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Transportation planning status"},
        "SHIPMENT_ADVICE_STATUS": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Whether shipment advice sent to source"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking version"},
    }
}

WSH_DELIVERY_ASSIGNMENTS = {
    "description": "Links shipment lines (WSH_DELIVERY_DETAILS) to shipments (WSH_NEW_DELIVERIES).",
    "primary_key": "DELIVERY_ASSIGNMENT_ID",
    "columns": {
        "DELIVERY_ASSIGNMENT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique assignment identifier"},
        "DELIVERY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Delivery ID (FK to WSH_NEW_DELIVERIES)"},
        "DELIVERY_DETAIL_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Delivery detail ID (FK to WSH_DELIVERY_DETAILS)"},
        "PARENT_DELIVERY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent delivery ID for consolidated shipments"},
        "PARENT_DELIVERY_DETAIL_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent detail ID (container)"},
        "ACTIVE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Whether assignment is active"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking version"},
    }
}

# ============================================================================
# FINANCIALS - AP (Accounts Payable) TABLES
# ============================================================================

AP_INVOICES_ALL = {
    "description": "AP invoice headers. One row per supplier invoice/credit memo/prepayment.",
    "primary_key": "INVOICE_ID",
    "columns": {
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique invoice identifier"},
        "INVOICE_NUM": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Invoice number"},
        "INVOICE_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Type: STANDARD, CREDIT, PREPAYMENT"},
        "INVOICE_DATE": {"type": "DATE", "nullable": True, "desc": "Invoice date"},
        "GL_DATE": {"type": "DATE", "nullable": True, "desc": "Accounting date"},
        "INVOICE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Invoice amount in transaction currency"},
        "INVOICE_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Invoice currency code"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency code"},
        "EXCHANGE_RATE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Currency conversion type"},
        "EXCHANGE_RATE": {"type": "NUMBER", "nullable": True, "desc": "Currency conversion rate"},
        "EXCHANGE_DATE": {"type": "DATE", "nullable": True, "desc": "Currency conversion date"},
        "BASE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Amount in functional currency"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier ID (FK to POZ_SUPPLIERS)"},
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier site ID"},
        "PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Party ID (FK to HZ_PARTIES)"},
        "PARTY_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Party site ID"},
        "PO_HEADER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "PO header matched to (FK to PO_HEADERS_ALL)"},
        "PO_MATCHED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if invoice is PO matched"},
        "PAYMENT_STATUS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y=paid, N=unpaid, P=partial"},
        "AMOUNT_PAID": {"type": "NUMBER", "nullable": True, "desc": "Amount paid"},
        "PAYMENT_AMOUNT_TOTAL": {"type": "NUMBER", "nullable": True, "desc": "Total amount paid"},
        "DISCOUNT_AMOUNT_TAKEN": {"type": "NUMBER", "nullable": True, "desc": "Discount taken"},
        "AMOUNT_APPLICABLE_TO_DISCOUNT": {"type": "NUMBER", "nullable": True, "desc": "Amount applicable to discount"},
        "APPROVED_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Approved amount"},
        "PAY_GROUP_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Pay group for payment runs"},
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Payment method (check, cash, credit)"},
        "TERMS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment terms ID (FK to AP_TERMS_B)"},
        "TERMS_DATE": {"type": "DATE", "nullable": True, "desc": "Date for payment term calculation"},
        "GOODS_RECEIVED_DATE": {"type": "DATE", "nullable": True, "desc": "Date goods received"},
        "INVOICE_RECEIVED_DATE": {"type": "DATE", "nullable": True, "desc": "Date invoice received"},
        "APPROVAL_STATUS": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Manual approval status"},
        "WFAPPROVAL_STATUS": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Workflow approval status"},
        "POSTING_STATUS": {"type": "VARCHAR2(15)", "nullable": True, "desc": "GL posting status"},
        "CANCELLED_DATE": {"type": "DATE", "nullable": True, "desc": "Cancellation date"},
        "SOURCE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Feeder system source"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Invoice description"},
        "VOUCHER_NUM": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Voucher number"},
        "TOTAL_TAX_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Total tax charged"},
        "FREIGHT_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Total freight amount"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ledger ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "LEGAL_ENTITY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Legal entity ID"},
        "ACCTS_PAY_CODE_COMBINATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "AP liability GL account ID"},
        "PROJECT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Project ID"},
        "TASK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Project task ID"},
        "EXPENDITURE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Project expenditure type"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": True, "desc": "Optimistic locking version"},
    }
}

AP_INVOICE_LINES_ALL = {
    "description": "AP invoice lines. One row per invoice line (Item, Freight, Tax, Prepayment, etc.).",
    "primary_key": "INVOICE_ID + LINE_NUMBER",
    "columns": {
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID (FK to AP_INVOICES_ALL)"},
        "LINE_NUMBER": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice line number"},
        "LINE_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Line type: Item, Freight, Miscellaneous, Tax, Prepayment"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Line description"},
        "AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Line amount in invoice currency"},
        "BASE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Line amount in functional currency"},
        "QUANTITY_INVOICED": {"type": "NUMBER", "nullable": True, "desc": "Quantity invoiced"},
        "UNIT_MEAS_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Unit of measure"},
        "UNIT_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Price per unit"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Inventory item ID"},
        "ITEM_DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Item description"},
        "PURCHASING_CATEGORY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Item category ID"},
        "PO_HEADER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Matched PO header ID (FK to PO_HEADERS_ALL)"},
        "PO_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Matched PO line ID (FK to PO_LINES_ALL)"},
        "PO_LINE_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Matched PO schedule ID (FK to PO_LINE_LOCATIONS_ALL)"},
        "PO_DISTRIBUTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Matched PO distribution ID (FK to PO_DISTRIBUTIONS_ALL)"},
        "PO_RELEASE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "PO release number"},
        "MATCH_TYPE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Match type (PO, Receipt, etc.)"},
        "FINAL_MATCH_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if PO no longer available for matching"},
        "RCV_TRANSACTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receipt transaction ID"},
        "RCV_SHIPMENT_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receipt shipment line ID"},
        "ACCOUNTING_DATE": {"type": "DATE", "nullable": True, "desc": "Accounting date for the line"},
        "PERIOD_NAME": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Accounting period"},
        "WFAPPROVAL_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Approval status"},
        "DISCARDED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if line discarded"},
        "CANCELLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if line cancelled"},
        "FUNDS_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Funds status"},
        "DEFERRED_ACCTG_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if deferred expense"},
        "DEF_ACCTG_START_DATE": {"type": "DATE", "nullable": True, "desc": "Deferred expense start date"},
        "DEF_ACCTG_END_DATE": {"type": "DATE", "nullable": True, "desc": "Deferred expense end date"},
        "PROJECT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Project ID"},
        "TASK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Task ID"},
        "ASSETS_TRACKING_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if item is an asset"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ledger ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": True, "desc": "Optimistic locking version"},
    }
}

# ============================================================================
# FINANCIALS - AP DISTRIBUTIONS
# ============================================================================

AP_INVOICE_DISTRIBUTIONS_ALL = {
    "description": "AP invoice accounting distributions. One row per GL distribution per invoice line.",
    "primary_key": "INVOICE_DISTRIBUTION_ID",
    "columns": {
        "INVOICE_DISTRIBUTION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique distribution identifier"},
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID (FK to AP_INVOICES_ALL)"},
        "INVOICE_LINE_NUMBER": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice line number (FK to AP_INVOICE_LINES_ALL)"},
        "DISTRIBUTION_LINE_NUMBER": {"type": "NUMBER(18)", "nullable": False, "desc": "Distribution line number"},
        "LINE_TYPE_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Distribution type: ITEM, ACCRUAL, IPV, ERV, etc."},
        "AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Distribution amount in transaction currency"},
        "BASE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Distribution amount in functional currency"},
        "QUANTITY_INVOICED": {"type": "NUMBER", "nullable": True, "desc": "Quantity invoiced on this distribution"},
        "UNIT_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Unit price"},
        "DIST_CODE_COMBINATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "GL account code combination ID"},
        "ACCOUNTING_DATE": {"type": "DATE", "nullable": True, "desc": "GL accounting date"},
        "PERIOD_NAME": {"type": "VARCHAR2(15)", "nullable": True, "desc": "GL accounting period"},
        "POSTED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if posted to GL (ACCRUAL_POSTED_FLAG/CASH_POSTED_FLAG do NOT exist on this table — they are on payment-side tables)"},
        "MATCH_STATUS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Approval status: A=approved, T=tested, null=untested"},
        "ENCUMBERED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if encumbered (budgetary control)"},
        "REVERSAL_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if this is a reversal distribution"},
        "PARENT_REVERSAL_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Distribution ID of the reversed distribution"},
        "CANCELLATION_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if cancelled"},
        "PO_DISTRIBUTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "PO distribution ID (FK to PO_DISTRIBUTIONS_ALL)"},
        "RCV_TRANSACTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receipt transaction ID"},
        "ASSETS_TRACKING_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if asset tracked"},
        "ASSET_BOOK_TYPE_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Asset book type"},
        "PROJECT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Project ID"},
        "TASK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Task ID"},
        "EXPENDITURE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Project expenditure type"},
        "EXPENDITURE_ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Expenditure organization ID"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ledger ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - AP PAYMENTS / CHECKS
# ============================================================================

AP_CHECKS_ALL = {
    "description": "AP payments (checks/EFTs). One row per payment issued to a supplier.",
    "primary_key": "CHECK_ID",
    "columns": {
        "CHECK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique payment identifier"},
        "CHECK_NUMBER": {"type": "NUMBER(18)", "nullable": True, "desc": "Check/payment number"},
        "CHECK_DATE": {"type": "DATE", "nullable": True, "desc": "Payment date"},
        "AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Payment amount in payment currency"},
        "BASE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Payment amount in functional currency"},
        "CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency code"},
        "EXCHANGE_RATE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Currency conversion type"},
        "EXCHANGE_RATE": {"type": "NUMBER", "nullable": True, "desc": "Currency conversion rate"},
        "EXCHANGE_DATE": {"type": "DATE", "nullable": True, "desc": "Currency conversion date"},
        "VENDOR_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier ID (FK to POZ_SUPPLIERS)"},
        "VENDOR_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier site ID"},
        "PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Party ID (FK to HZ_PARTIES)"},
        "PARTY_SITE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Party site ID"},
        "ADDRESS_LINE1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Payee address line 1"},
        "CITY": {"type": "VARCHAR2(60)", "nullable": True, "desc": "Payee city"},
        "STATE": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Payee state"},
        "COUNTRY": {"type": "VARCHAR2(60)", "nullable": True, "desc": "Payee country"},
        "ZIP": {"type": "VARCHAR2(60)", "nullable": True, "desc": "Payee postal code"},
        "PAYMENT_TYPE_FLAG": {"type": "VARCHAR2(25)", "nullable": True, "desc": "A=automatic, M=manual, Q=quick, R=refund"},
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Payment method (CHECK, EFT, WIRE)"},
        "STATUS_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Payment status: NEGOTIABLE, VOIDED, CLEARED, etc."},
        "VOID_DATE": {"type": "DATE", "nullable": True, "desc": "Date payment was voided"},
        "CLEARED_DATE": {"type": "DATE", "nullable": True, "desc": "Date payment cleared the bank"},
        "CLEARED_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Cleared amount"},
        "STOPPED_DATE": {"type": "DATE", "nullable": True, "desc": "Date stop payment was issued"},
        "CE_BANK_ACCT_USE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Bank account use ID (FK to CE_BANK_ACCOUNTS)"},
        "PAYMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "IBY payment ID (FK to IBY_PAYMENTS_ALL)"},
        "PAYMENT_INSTRUCTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment instruction ID"},
        "PAYMENT_DOCUMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment document (check stock) ID"},
        "DOC_SEQUENCE_VALUE": {"type": "NUMBER", "nullable": True, "desc": "Document sequence (voucher) number"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID (SET_OF_BOOKS_ID does NOT exist in Fusion — use LEGAL_ENTITY_ID/ORG_ID)"},
        "LEGAL_ENTITY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Legal entity ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

AP_INVOICE_PAYMENTS_ALL = {
    "description": "Links AP invoices to payments. One row per invoice-payment application.",
    "primary_key": "INVOICE_PAYMENT_ID",
    "columns": {
        "INVOICE_PAYMENT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique invoice payment identifier"},
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID (FK to AP_INVOICES_ALL)"},
        "CHECK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Payment ID (FK to AP_CHECKS_ALL)"},
        "PAYMENT_NUM": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment schedule number"},
        "AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Amount applied from this payment to this invoice"},
        "DISCOUNT_TAKEN": {"type": "NUMBER", "nullable": True, "desc": "Discount amount taken"},
        "DISCOUNT_LOST": {"type": "NUMBER", "nullable": True, "desc": "Discount amount lost"},
        "EXCHANGE_RATE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Currency conversion type"},
        "EXCHANGE_RATE": {"type": "NUMBER", "nullable": True, "desc": "Currency conversion rate"},
        "EXCHANGE_DATE": {"type": "DATE", "nullable": True, "desc": "Currency conversion date"},
        "ACCOUNTING_DATE": {"type": "DATE", "nullable": True, "desc": "GL accounting date"},
        "PERIOD_NAME": {"type": "VARCHAR2(15)", "nullable": True, "desc": "GL period name"},
        "POSTED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if posted to GL (ACCRUAL_POSTED_FLAG/CASH_POSTED_FLAG are EBS-era and do NOT exist in Fusion)"},
        "REVERSAL_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if reversed"},
        "REVERSAL_INV_PMT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "ID of the reversed payment application"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ledger ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

AP_PAYMENT_SCHEDULES_ALL = {
    "description": "AP payment schedules. One row per scheduled payment installment per invoice.",
    "primary_key": "INVOICE_ID + PAYMENT_NUM",
    "columns": {
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID (FK to AP_INVOICES_ALL)"},
        "PAYMENT_NUM": {"type": "NUMBER(18)", "nullable": False, "desc": "Payment schedule number"},
        "DUE_DATE": {"type": "DATE", "nullable": True, "desc": "Payment due date"},
        "DISCOUNT_DATE": {"type": "DATE", "nullable": True, "desc": "Discount date (last day to take discount)"},
        "SECOND_DISCOUNT_DATE": {"type": "DATE", "nullable": True, "desc": "Second discount date"},
        "THIRD_DISCOUNT_DATE": {"type": "DATE", "nullable": True, "desc": "Third discount date"},
        "GROSS_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Gross amount due"},
        "AMOUNT_REMAINING": {"type": "NUMBER", "nullable": True, "desc": "Amount still unpaid"},
        "DISCOUNT_AMOUNT_AVAILABLE": {"type": "NUMBER", "nullable": True, "desc": "Discount amount available"},
        "SECOND_DISC_AMT_AVAILABLE": {"type": "NUMBER", "nullable": True, "desc": "Second discount amount available"},
        "THIRD_DISC_AMT_AVAILABLE": {"type": "NUMBER", "nullable": True, "desc": "Third discount amount available"},
        "DISCOUNT_AMOUNT_REMAINING": {"type": "NUMBER", "nullable": True, "desc": "Discount amount remaining"},
        "PAYMENT_STATUS_FLAG": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Y=fully paid, N=unpaid, P=partially paid"},
        "PAYMENT_PRIORITY": {"type": "NUMBER(2)", "nullable": True, "desc": "Payment priority (1-99)"},
        "HOLD_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if payment is on hold"},
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Payment method code"},
        "EXTERNAL_BANK_ACCOUNT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier bank account ID"},
        "IBY_HOLD_REASON": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Reason for payment hold"},
        "PAYMENT_CROSS_RATE": {"type": "NUMBER", "nullable": True, "desc": "Cross-currency payment rate (FUTURE_PAY_DUE_DATE not documented in 25D — removed)"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

AP_PAYMENT_HISTORY_ALL = {
    "description": "AP payment lifecycle history. Tracks clearing, unclearing, maturity events for payments.",
    "primary_key": "PAYMENT_HISTORY_ID",
    "columns": {
        "PAYMENT_HISTORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique history record identifier"},
        "CHECK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Payment ID (FK to AP_CHECKS_ALL)"},
        "TRANSACTION_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Event type: PAYMENT CLEARING, PAYMENT UNCLEARING, PAYMENT MATURITY, etc."},
        "ACCOUNTING_DATE": {"type": "DATE", "nullable": True, "desc": "Accounting date of the event"},
        "TRX_BANK_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Bank amount"},
        "TRX_BASE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Functional currency amount"},
        "ERRORS_BANK_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Bank errors amount"},
        "CHARGES_BANK_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Bank charges amount"},
        "MATCHED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if matched to bank statement"},
        "POSTED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if posted to GL"},
        "REV_PMT_HIST_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Reversed payment history ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - AP HOLDS
# ============================================================================

AP_HOLDS_ALL = {
    "description": "AP invoice holds. One row per hold applied to an invoice.",
    "primary_key": "HOLD_ID",
    "columns": {
        "HOLD_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique hold identifier"},
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID (FK to AP_INVOICES_ALL)"},
        "LINE_LOCATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "PO shipment ID (for matching holds)"},
        "HOLD_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Hold name/type code (HOLD_TYPE column does NOT exist in Fusion)"},
        "HOLD_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "Date hold was placed"},
        "HOLD_REASON": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Reason hold was placed"},
        "RELEASE_LOOKUP_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Release name/code (null if still held)"},
        "RELEASE_REASON": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Reason hold was released"},
        "HELD_BY": {"type": "VARCHAR2(64)", "nullable": True, "desc": "Username who placed the hold (Fusion: VARCHAR2, not numeric ID; RELEASED_BY/RELEASED_DATE do not exist)"},
        "WF_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Workflow approval status"},
        "STATUS_FLAG": {"type": "VARCHAR2(25)", "nullable": True, "desc": "S=hold active, R=released"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - AP PAYMENT TERMS
# ============================================================================

AP_TERMS_B = {
    "description": "AP payment terms header (base). One row per payment term definition.",
    "primary_key": "TERM_ID",
    "columns": {
        "TERM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique payment term identifier"},
        "ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if term is active"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Active start date"},
        "END_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Active end date"},
        "TYPE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Term type"},
        "DUE_CUTOFF_DAY": {"type": "NUMBER(2)", "nullable": True, "desc": "Due cutoff day of month (DISCOUNT_CUTOFF_DAY does NOT exist on AP_TERMS_B)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

AP_TERMS_TL = {
    "description": "AP payment terms translations. One row per term per language.",
    "primary_key": "TERM_ID + LANGUAGE",
    "columns": {
        "TERM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Payment term ID (FK to AP_TERMS_B)"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Language code"},
        "SOURCE_LANG": {"type": "VARCHAR2(4)", "nullable": True, "desc": "Source language code"},
        "NAME": {"type": "VARCHAR2(50)", "nullable": False, "desc": "Payment term name (e.g., Net 30, 2/10 Net 30)"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Payment term description"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

AP_TERMS_LINES = {
    "description": "AP payment term lines. Defines installment percentages, due days, and discount rules.",
    "primary_key": "TERM_ID + SEQUENCE_NUM",
    "columns": {
        "TERM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Payment term ID (FK to AP_TERMS_B)"},
        "SEQUENCE_NUM": {"type": "NUMBER(18)", "nullable": False, "desc": "Sequence/installment number"},
        "DUE_PERCENT": {"type": "NUMBER", "nullable": True, "desc": "Percent of invoice amount due in this installment"},
        "DUE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Fixed amount due (if not percent-based)"},
        "DUE_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Number of days until due"},
        "DUE_DAY_OF_MONTH": {"type": "NUMBER(2)", "nullable": True, "desc": "Day of month payment is due"},
        "DUE_MONTHS_FORWARD": {"type": "NUMBER(2)", "nullable": True, "desc": "Months forward for due date"},
        "DISCOUNT_PERCENT": {"type": "NUMBER", "nullable": True, "desc": "Discount percentage if paid early"},
        "DISCOUNT_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Days within which discount applies"},
        "DISCOUNT_DAY_OF_MONTH": {"type": "NUMBER(2)", "nullable": True, "desc": "Day of month for discount cutoff"},
        "DISCOUNT_PERCENT_2": {"type": "NUMBER", "nullable": True, "desc": "Second discount percentage"},
        "DISCOUNT_DAYS_2": {"type": "NUMBER", "nullable": True, "desc": "Days for second discount"},
        "DISCOUNT_PERCENT_3": {"type": "NUMBER", "nullable": True, "desc": "Third discount percentage"},
        "DISCOUNT_DAYS_3": {"type": "NUMBER", "nullable": True, "desc": "Days for third discount"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - AP PREPAYMENTS
# ============================================================================

AP_PREPAY_HISTORY_ALL = {
    "description": "AP prepayment application/unapplication history. Tracks how prepayments are applied to invoices.",
    "primary_key": "PREPAY_HISTORY_ID",
    "columns": {
        "PREPAY_HISTORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique prepayment history identifier"},
        "INVOICE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Invoice ID the prepay is applied to (FK to AP_INVOICES_ALL)"},
        "INVOICE_LINE_NUMBER": {"type": "NUMBER(18)", "nullable": True, "desc": "Invoice line number"},
        "PREPAY_INVOICE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Prepayment invoice ID"},
        "PREPAY_LINE_NUM": {"type": "NUMBER(18)", "nullable": True, "desc": "Prepayment line number (real name; NOT PREPAY_LINE_NUMBER). Prepay amounts are on AP_INVOICE_LINES_ALL/AP_PREPAY_APP_DISTS, not here."},
        "TRANSACTION_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "APPLICATION or UNAPPLICATION"},
        "ACCOUNTING_DATE": {"type": "DATE", "nullable": True, "desc": "GL accounting date"},
        "POSTED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if posted to GL"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - IBY (Oracle Payments) TABLES
# ============================================================================

IBY_PAYMENTS_ALL = {
    "description": "Oracle Payments - payment records. One row per payment created by the payment engine.",
    "primary_key": "PAYMENT_ID",
    "columns": {
        "PAYMENT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique payment identifier"},
        "PAYMENT_INSTRUCTION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment instruction ID (FK to IBY_PAY_INSTRUCTIONS_ALL)"},
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Payment method (CHECK, EFT, WIRE)"},
        "PAYMENT_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Payment status: ISSUED, VOID, REMOVED, etc."},
        "PAYMENT_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Payment amount"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency"},
        "PAYMENT_DATE": {"type": "DATE", "nullable": True, "desc": "Payment date"},
        "PAPER_DOCUMENT_NUMBER": {"type": "NUMBER(18)", "nullable": True, "desc": "Paper document (check) number"},
        "PAYEE_PARTY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payee party ID (FK to HZ_PARTIES)"},
        "PAYEE_NAME": {"type": "VARCHAR2(360)", "nullable": True, "desc": "Payee name"},
        "INTERNAL_BANK_ACCOUNT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Internal bank account ID (FK to CE_BANK_ACCOUNTS)"},
        "EXTERNAL_BANK_ACCOUNT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Supplier/payee bank account ID"},
        "PAYMENT_PROFILE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment process profile ID (PAYMENT_DOCUMENT_ID is NOT on this table — it's on IBY_PAY_INSTRUCTIONS_ALL; use DOCUMENT_SEQUENCE_VALUE here)"},
        "PAYMENT_REASON_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Reason for payment"},
        "PAYMENT_REASON_COMMENTS": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Payment reason comments"},
        "COMPLETED_PMTS_GROUP_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Completed payments group ID"},
        "MATURITY_DATE": {"type": "DATE", "nullable": True, "desc": "Maturity date for future-dated payments"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

IBY_PAY_INSTRUCTIONS_ALL = {
    "description": "Oracle Payments - payment instructions sent to banks. One row per payment instruction batch.",
    "primary_key": "PAYMENT_INSTRUCTION_ID",
    "columns": {
        "PAYMENT_INSTRUCTION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique payment instruction identifier"},
        "PAYMENT_INSTRUCTION_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Status: CREATED, FORMATTED, TRANSMITTED, TERMINATED"},
        "PAYMENT_COUNT": {"type": "NUMBER", "nullable": True, "desc": "Number of payments in instruction (PAYMENT_AMOUNT/PAYMENT_METHOD_CODE are NOT on this table — they live at the payment level, IBY_PAYMENTS_ALL)"},
        "PAYMENT_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Payment currency"},
        "PAYMENT_PROFILE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment process profile ID"},
        "PAYMENT_DOCUMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment document (check stock) ID"},
        "INTERNAL_BANK_ACCOUNT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Internal bank account ID"},
        "PAYMENT_DATE": {"type": "DATE", "nullable": True, "desc": "Scheduled payment date"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

IBY_PAYMENT_METHODS_B = {
    "description": "Oracle Payments - payment method definitions. One row per payment method.",
    "primary_key": "PAYMENT_METHOD_CODE",
    "columns": {
        "PAYMENT_METHOD_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Payment method code (CHECK, EFT, WIRE, etc.)"},
        # PAYMENT_METHOD_NAME is on IBY_PAYMENT_METHODS_TL — join IBY_PAYMENT_METHODS_VL to get the name.
        # ENABLED_FLAG does not exist — use INACTIVE_DATE / START_DATE / END_DATE for enablement.
        "INACTIVE_DATE": {"type": "DATE", "nullable": True, "desc": "Inactive date — use instead of ENABLED_FLAG to determine if active"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Effective start date"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Effective end date"},
        "SUPPORT_BILLS_PAYABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y if supports future-dated payments"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - CE (Cash Management) TABLES
# ============================================================================

CE_BANK_ACCOUNTS = {
    "description": "Internal (company) bank accounts. One row per bank account.",
    "primary_key": "BANK_ACCOUNT_ID",
    "columns": {
        "BANK_ACCOUNT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Unique bank account identifier"},
        "BANK_ACCOUNT_NAME": {"type": "VARCHAR2(360)", "nullable": True, "desc": "Bank account name"},
        "BANK_ACCOUNT_NUM": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Bank account number"},
        "MASKED_ACCOUNT_NUM": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Masked bank account number"},
        "BANK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Bank party ID (BANK_NAME/BRANCH_NAME/COUNTRY_CODE are NOT on this table — they're on the related bank/branch party entities)"},
        "BANK_BRANCH_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Branch party FK (renamed from BRANCH_ID)"},
        "CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Account currency"},
        "BANK_ACCOUNT_TYPE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Account type, SAVINGS/CHECKING (renamed from ACCOUNT_TYPE)"},
        "CASH_CLEARING_CCID": {"type": "NUMBER(18)", "nullable": True, "desc": "Cash clearing GL account ID"},
        "ASSET_CODE_COMBINATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Cash asset GL account CCID (replaces CASH_ACCOUNT_CCID)"},
        "ACCOUNT_CLASSIFICATION": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Account classification (e.g. INTERNAL)"},
        "IBAN_NUMBER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "IBAN"},
        "AGENCY_LOCATION_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Agency location code"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Account end date (null if active)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# FINANCIALS - AR (Accounts Receivable) TABLES
# ============================================================================

RA_CUSTOMER_TRX_ALL = {
    "description": "AR transaction headers (invoices, debit memos, credit memos, bills receivable).",
    "primary_key": "CUSTOMER_TRX_ID",
    "columns": {
        "CUSTOMER_TRX_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Transaction unique identifier"},
        "TRX_NUMBER": {"type": "VARCHAR2(20)", "nullable": False, "desc": "Transaction/invoice number"},
        "TRX_DATE": {"type": "DATE", "nullable": False, "desc": "Transaction date"},
        "CUST_TRX_TYPE_SEQ_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Transaction type sequence ID"},
        "STATUS_TRX": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Transaction status"},
        "COMPLETE_FLAG": {"type": "VARCHAR2(1)", "nullable": False, "desc": "Y if transaction is complete"},
        "DOCUMENT_STATUS_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Document status (e.g., Approved)"},
        "SOLD_TO_CUSTOMER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to customer ID"},
        "SOLD_TO_CONTACT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to contact ID"},
        "SOLD_TO_SITE_USE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Sold-to site use ID"},
        "BILL_TO_CUSTOMER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Bill-to customer ID"},
        "BILL_TO_CONTACT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Bill-to contact ID"},
        "BILL_TO_SITE_USE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Bill-to site use ID"},
        "SHIP_TO_CUSTOMER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ship-to customer ID"},
        "SHIP_TO_CONTACT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ship-to contact ID"},
        "SHIP_TO_SITE_USE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Ship-to site use ID"},
        "PAYING_CUSTOMER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Paying customer ID"},
        "INVOICE_CURRENCY_CODE": {"type": "VARCHAR2(15)", "nullable": True, "desc": "Invoice currency code"},
        "EXCHANGE_RATE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Currency conversion type"},
        "EXCHANGE_DATE": {"type": "DATE", "nullable": True, "desc": "Currency conversion date"},
        "EXCHANGE_RATE": {"type": "NUMBER", "nullable": True, "desc": "Currency conversion rate"},
        "TERM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Payment terms ID"},
        "TERM_DUE_DATE": {"type": "DATE", "nullable": True, "desc": "Payment due date"},
        "RECEIPT_METHOD_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receipt method ID"},
        "BR_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Bill receivable amount"},
        "PURCHASE_ORDER": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Customer purchase order number"},
        "PURCHASE_ORDER_REVISION": {"type": "VARCHAR2(50)", "nullable": True, "desc": "PO revision"},
        "PURCHASE_ORDER_DATE": {"type": "DATE", "nullable": True, "desc": "PO date"},
        "CUSTOMER_REFERENCE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Customer reference"},
        "CUSTOMER_REFERENCE_DATE": {"type": "DATE", "nullable": True, "desc": "Customer reference date"},
        "PREVIOUS_CUSTOMER_TRX_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Previous/source transaction ID (for credit memos)"},
        "BATCH_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Transaction batch ID"},
        "BATCH_SOURCE_SEQ_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Batch source sequence ID"},
        "POSTING_CONTROL_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "GL posting status ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Business unit ID"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Ledger ID"},
        "LEGAL_ENTITY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Legal entity ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

RA_CUSTOMER_TRX_LINES_ALL = {
    "description": "AR transaction lines. LINE types: LINE (item), TAX, FREIGHT, CB (chargeback).",
    "primary_key": "CUSTOMER_TRX_LINE_ID",
    "columns": {
        "CUSTOMER_TRX_LINE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Transaction line unique identifier"},
        "CUSTOMER_TRX_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Transaction header ID (FK to RA_CUSTOMER_TRX_ALL)"},
        "LINE_NUMBER": {"type": "NUMBER", "nullable": False, "desc": "Transaction line number"},
        "LINE_TYPE": {"type": "VARCHAR2(20)", "nullable": False, "desc": "Line type: LINE, TAX, FREIGHT, CB"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Line description"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Inventory item ID"},
        "QUANTITY_ORDERED": {"type": "NUMBER", "nullable": True, "desc": "Quantity ordered"},
        "QUANTITY_INVOICED": {"type": "NUMBER", "nullable": True, "desc": "Quantity invoiced"},
        "QUANTITY_CREDITED": {"type": "NUMBER", "nullable": True, "desc": "Quantity credited (credit memos)"},
        "UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Unit of measure code"},
        "UNIT_STANDARD_PRICE": {"type": "NUMBER", "nullable": True, "desc": "List price per unit"},
        "UNIT_SELLING_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Selling price per unit"},
        "EXTENDED_AMOUNT": {"type": "NUMBER", "nullable": False, "desc": "Transaction line amount"},
        "REVENUE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Revenue amount"},
        "GROSS_UNIT_SELLING_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Unit price inclusive of tax"},
        "GROSS_EXTENDED_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Amount inclusive of tax"},
        "TAXABLE_AMOUNT": {"type": "NUMBER", "nullable": True, "desc": "Taxable amount"},
        "AMOUNT_DUE_REMAINING": {"type": "NUMBER", "nullable": True, "desc": "Remaining balance"},
        "AMOUNT_DUE_ORIGINAL": {"type": "NUMBER", "nullable": True, "desc": "Original balance"},
        "REASON_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Reason code"},
        "ACCOUNTING_RULE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Accounting rule for revenue recognition"},
        "RULE_START_DATE": {"type": "DATE", "nullable": True, "desc": "Revenue recognition start date"},
        "RULE_END_DATE": {"type": "DATE", "nullable": True, "desc": "Revenue recognition end date"},
        "PREVIOUS_CUSTOMER_TRX_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source invoice ID (credit memos)"},
        "PREVIOUS_CUSTOMER_TRX_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source invoice line ID (credit memos)"},
        "LINK_TO_CUST_TRX_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent line for TAX/FREIGHT lines"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Ledger ID"},
        "ORG_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Business unit ID"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation date"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update date"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated"},
    }
}

# ============================================================================
# ALL TABLES (for lookup by app.py)
# ============================================================================

ALL_OM_SHIP_FIN_TABLES = {
    "DOO_HEADERS_ALL": DOO_HEADERS_ALL,
    "DOO_LINES_ALL": DOO_LINES_ALL,
    "WSH_NEW_DELIVERIES": WSH_NEW_DELIVERIES,
    "WSH_DELIVERY_DETAILS": WSH_DELIVERY_DETAILS,
    "WSH_DELIVERY_ASSIGNMENTS": WSH_DELIVERY_ASSIGNMENTS,
    "AP_INVOICES_ALL": AP_INVOICES_ALL,
    "AP_INVOICE_LINES_ALL": AP_INVOICE_LINES_ALL,
    "AP_INVOICE_DISTRIBUTIONS_ALL": AP_INVOICE_DISTRIBUTIONS_ALL,
    "AP_CHECKS_ALL": AP_CHECKS_ALL,
    "AP_INVOICE_PAYMENTS_ALL": AP_INVOICE_PAYMENTS_ALL,
    "AP_PAYMENT_SCHEDULES_ALL": AP_PAYMENT_SCHEDULES_ALL,
    "AP_PAYMENT_HISTORY_ALL": AP_PAYMENT_HISTORY_ALL,
    "AP_HOLDS_ALL": AP_HOLDS_ALL,
    "AP_TERMS_B": AP_TERMS_B,
    "AP_TERMS_TL": AP_TERMS_TL,
    "AP_TERMS_LINES": AP_TERMS_LINES,
    "AP_PREPAY_HISTORY_ALL": AP_PREPAY_HISTORY_ALL,
    "IBY_PAYMENTS_ALL": IBY_PAYMENTS_ALL,
    "IBY_PAY_INSTRUCTIONS_ALL": IBY_PAY_INSTRUCTIONS_ALL,
    "IBY_PAYMENT_METHODS_B": IBY_PAYMENT_METHODS_B,
    "CE_BANK_ACCOUNTS": CE_BANK_ACCOUNTS,
    "RA_CUSTOMER_TRX_ALL": RA_CUSTOMER_TRX_ALL,
    "RA_CUSTOMER_TRX_LINES_ALL": RA_CUSTOMER_TRX_LINES_ALL,
}

OM_SHIP_FIN_LOOKUP_VALUES = {
    "INVOICE_TYPE_LOOKUP_CODE (AP_INVOICES_ALL)": [
        "STANDARD - Standard Invoice",
        "CREDIT - Credit Memo",
        "PREPAYMENT - Prepayment",
        "DEBIT - Debit Memo",
        "MIXED - Mixed Invoice",
    ],
    "LINE_TYPE_LOOKUP_CODE (AP_INVOICE_LINES_ALL)": [
        "ITEM - Item line",
        "FREIGHT - Freight line",
        "MISCELLANEOUS - Miscellaneous line",
        "TAX - Tax line",
        "PREPAY - Prepayment application",
        "AWT - Automatic Withholding Tax",
    ],
    "LINE_TYPE (RA_CUSTOMER_TRX_LINES_ALL)": [
        "LINE - Regular invoice line (items)",
        "TAX - Tax line",
        "FREIGHT - Freight line",
        "CB - Chargeback line",
    ],
    "STATUS_CODE (WSH_NEW_DELIVERIES)": [
        "OP - Open",
        "SA - Ship confirmed/Awaiting",
        "CL - Closed",
        "IT - In-Transit",
        "CO - Confirmed",
    ],
    "RELEASED_STATUS (WSH_DELIVERY_DETAILS)": [
        "R - Ready to release",
        "S - Released to warehouse",
        "Y - Staged/Pick confirmed",
        "C - Shipped",
        "B - Backordered",
        "D - Cancelled",
    ],
    "PAYMENT_STATUS_FLAG (AP_INVOICES_ALL)": [
        "Y - Fully Paid",
        "N - Unpaid",
        "P - Partially Paid",
    ],
    "LINE_TYPE_LOOKUP_CODE (AP_INVOICE_DISTRIBUTIONS_ALL)": [
        "ITEM - Item expense",
        "ACCRUAL - Accrual entry",
        "IPV - Invoice Price Variance",
        "ERV - Exchange Rate Variance",
        "TAX - Tax distribution",
        "FREIGHT - Freight distribution",
        "MISCELLANEOUS - Miscellaneous distribution",
        "PREPAY - Prepayment application",
        "AWT - Automatic Withholding Tax",
    ],
    "STATUS_LOOKUP_CODE (AP_CHECKS_ALL)": [
        "NEGOTIABLE - Issued/outstanding",
        "VOIDED - Voided",
        "CLEARED - Cleared at bank",
        "CLEARED BUT UNACCOUNTED - Cleared, not yet accounted",
        "RECONCILED - Reconciled with bank statement",
        "RECONCILED UNACCOUNTED - Reconciled, not yet accounted",
        "STOP INITIATED - Stop payment requested",
        "OVERFLOW - Overflow payment",
    ],
    "PAYMENT_TYPE_FLAG (AP_CHECKS_ALL)": [
        "A - Automatic (payment batch)",
        "M - Manual",
        "Q - Quick payment",
        "R - Refund",
    ],
    "HOLD_LOOKUP_CODE (AP_HOLDS_ALL)": [
        "PRICE - Price variance hold",
        "QTY REC - Quantity received hold",
        "QTY ORD - Quantity ordered hold",
        "AMOUNT - Amount hold",
        "VENDOR - Supplier hold",
        "PERIOD - Accounting period hold",
        "TAX VARIANCE - Tax variance hold",
        "DIST VARIANCE - Distribution variance hold",
        "FUNDS - Insufficient funds hold",
        "NATURAL ACCOUNT TAX - Tax account hold",
        "CANT FUNDS CHECK - Cannot funds check",
        "MATCH REQUIRED - PO match required hold",
    ],
    "TRANSACTION_TYPE (AP_PAYMENT_HISTORY_ALL)": [
        "PAYMENT CLEARING - Payment cleared at bank",
        "PAYMENT UNCLEARING - Payment clearing reversed",
        "PAYMENT MATURITY - Future-dated payment matured",
        "PAYMENT CREATED - Payment created",
    ],
    "PAYMENT_STATUS (IBY_PAYMENTS_ALL)": [
        "ISSUED - Payment issued",
        "VOID - Payment voided",
        "REMOVED - Payment removed",
        "SETUP - Payment in setup",
        "SUBMITTED_FOR_PRINTING - Sent for printing",
        "FORMATTED - Payment formatted",
    ],
    "PAYMENT_INSTRUCTION_STATUS (IBY_PAY_INSTRUCTIONS_ALL)": [
        "CREATED - Instruction created",
        "FORMATTED - Instruction formatted",
        "TRANSMITTED - Sent to bank",
        "TERMINATED - Instruction terminated",
    ],
}
