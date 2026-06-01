"""
Oracle Fusion Cloud SCM - Item Master & Inventory Tables/Views Schema Reference
For BI Publisher SQL Data Models
Source: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/oedsc/
Release: 26A
"""

# ============================================================================
# TABLE RELATIONSHIPS (JOIN KEYS)
# ============================================================================
ITEM_RELATIONSHIPS = {
    # Item Master core joins
    "EGP_SYSTEM_ITEMS_B -> EGP_SYSTEM_ITEMS_TL": "B.INVENTORY_ITEM_ID = TL.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = TL.ORGANIZATION_ID AND TL.LANGUAGE = USERENV('LANG')",
    "EGP_SYSTEM_ITEMS_B -> EGP_ITEM_REVISIONS_B": "B.INVENTORY_ITEM_ID = R.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = R.ORGANIZATION_ID",
    "EGP_SYSTEM_ITEMS_B -> EGP_ITEM_CAT_ASSIGNMENTS": "B.INVENTORY_ITEM_ID = ICA.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = ICA.ORGANIZATION_ID",
    "EGP_SYSTEM_ITEMS_B -> EGO_ITEM_EFF_B": "B.INVENTORY_ITEM_ID = EFF.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = EFF.ORGANIZATION_ID",
    "EGP_SYSTEM_ITEMS_B -> EGP_ITEM_RELATIONSHIPS_B": "B.INVENTORY_ITEM_ID = REL.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = REL.ORGANIZATION_ID",

    # Category joins
    "EGP_ITEM_CAT_ASSIGNMENTS -> EGP_CATEGORIES_B": "ICA.CATEGORY_ID = CAT.CATEGORY_ID",
    "EGP_ITEM_CAT_ASSIGNMENTS -> EGP_CATEGORIES_TL": "ICA.CATEGORY_ID = CTL.CATEGORY_ID AND CTL.LANGUAGE = USERENV('LANG')",
    "EGP_ITEM_CAT_ASSIGNMENTS -> EGP_CATEGORY_SETS_B": "ICA.CATEGORY_SET_ID = CS.CATEGORY_SET_ID",
    "EGP_ITEM_CAT_ASSIGNMENTS -> EGP_CATEGORY_SETS_TL": "ICA.CATEGORY_SET_ID = CST.CATEGORY_SET_ID AND CST.LANGUAGE = USERENV('LANG')",
    "EGP_CATEGORY_SETS_B -> EGP_CATEGORY_SET_VALID_CATS": "CS.CATEGORY_SET_ID = VC.CATEGORY_SET_ID",
    "EGP_CATEGORY_SET_VALID_CATS -> EGP_CATEGORIES_B": "VC.CATEGORY_ID = CAT.CATEGORY_ID",

    # Organization joins
    "EGP_SYSTEM_ITEMS_B -> INV_ORG_PARAMETERS_V": "B.ORGANIZATION_ID = IOP.ORGANIZATION_ID",
    "EGP_SYSTEM_ITEMS_B -> INV_ORGANIZATION_DEFINITIONS_V": "B.ORGANIZATION_ID = IOD.ORGANIZATION_ID",

    # Item class joins
    "EGP_SYSTEM_ITEMS_B -> EGP_ITEM_CLASSES_B": "B.ITEM_CATALOG_GROUP_ID = IC.ITEM_CATALOG_GROUP_ID",

    # Revision EFF joins
    "EGP_ITEM_REVISIONS_B -> EGO_ITEM_REVISION_EFF_B": "R.REVISION_ID = REFF.REVISION_ID",

    # MFG Part Numbers
    "EGP_SYSTEM_ITEMS_B -> EGP_MFG_PART_NUMBERS_B": "B.INVENTORY_ITEM_ID = MPN.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = MPN.ORGANIZATION_ID",

    # Item-Org Associations
    "EGP_SYSTEM_ITEMS_B -> EGP_ITEM_ORG_ASSOCIATIONS": "B.INVENTORY_ITEM_ID = IOA.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = IOA.ORGANIZATION_ID",

    # Item Supplier Associations
    "EGP_SYSTEM_ITEMS_B -> EGO_ITEM_ASSOCIATIONS": "B.INVENTORY_ITEM_ID = IA.INVENTORY_ITEM_ID AND B.ORGANIZATION_ID = IA.ORGANIZATION_ID",

    # Convenient VL views (pre-joined B + TL)
    "EGP_SYSTEM_ITEMS_VL (= B + TL joined)": "SELECT * FROM EGP_SYSTEM_ITEMS_VL -- pre-joined base + translation",
    "EGP_CATEGORIES_VL (= B + TL joined)": "SELECT * FROM EGP_CATEGORIES_VL -- pre-joined base + translation",
    "EGP_CATEGORY_SETS_VL (= B + TL joined)": "SELECT * FROM EGP_CATEGORY_SETS_VL -- pre-joined base + translation",
}


# ============================================================================
# COMMONLY USED VIEWS (recommended for BI Publisher queries)
# ============================================================================

EGP_SYSTEM_ITEMS = {
    "description": (
        "Read-only view on EGP_SYSTEM_ITEMS_VL. "
        "Contains ~467 columns covering all item master attributes: "
        "identification, inventory control, lot/serial, planning, purchasing, "
        "pricing, physical attributes, order mgmt, receiving, service, etc. "
        "This is the recommended view for item queries in BI Publisher."
    ),
    "source": "EGP_SYSTEM_ITEMS_VL (which joins EGP_SYSTEM_ITEMS_B + EGP_SYSTEM_ITEMS_TL)",
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item unique identifier (PK part 1)"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization unique identifier (PK part 2)"},
        "ITEM_NUMBER": {"type": "VARCHAR2(300)", "desc": "User-visible item number / part number"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "desc": "Translated item description (from TL)"},
        "LONG_DESCRIPTION": {"type": "VARCHAR2(4000)", "desc": "Long description (from TL)"},
        "ITEM_TYPE": {"type": "VARCHAR2(30)", "desc": "Classification: finished, purchased, etc."},
        "INVENTORY_ITEM_STATUS_CODE": {"type": "VARCHAR2(10)", "desc": "Controls transaction activity"},
        "PRIMARY_UOM_CODE": {"type": "VARCHAR2(3)", "desc": "Primary unit of measure"},
        "SECONDARY_UOM_CODE": {"type": "VARCHAR2(3)", "desc": "Secondary UOM (dual UOM items)"},
        "INVENTORY_ITEM_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Can be stocked and transacted"},
        "PURCHASING_ITEM_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Can appear on purchase orders"},
        "PURCHASING_ENABLED_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Currently purchasable"},
        "CUSTOMER_ORDER_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Can be ordered by customers"},
        "SHIPPABLE_ITEM_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Can be shipped"},
        "BOM_ITEM_TYPE": {"type": "NUMBER", "desc": "1=Model, 2=Option Class, 4=Standard, 5=Planning"},
        "PLANNING_MAKE_BUY_CODE": {"type": "NUMBER", "desc": "1=Make, 2=Buy"},
        "LIST_PRICE_PER_UNIT": {"type": "NUMBER", "desc": "Default list price"},
        "BUYER_ID": {"type": "NUMBER(18)", "desc": "Default buyer FK"},
        "PLANNER_CODE": {"type": "VARCHAR2(10)", "desc": "Material planner assignment"},
        "LOT_CONTROL_CODE": {"type": "NUMBER", "desc": "1=No control, 2=Full lot control"},
        "SERIAL_NUMBER_CONTROL_CODE": {"type": "NUMBER", "desc": "1=No, 2=Predefined, 5=At receipt, 6=At SO issue"},
        "ENABLED_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - Item enabled"},
        "APPROVAL_STATUS": {"type": "VARCHAR2(30)", "desc": "Item approval status"},
        "ITEM_CATALOG_GROUP_ID": {"type": "NUMBER(18)", "desc": "Item class FK -> EGP_ITEM_CLASSES_B"},
        "UNIT_WEIGHT": {"type": "NUMBER", "desc": "Weight per unit"},
        "WEIGHT_UOM_CODE": {"type": "VARCHAR2(3)", "desc": "Weight UOM"},
        "UNIT_VOLUME": {"type": "NUMBER", "desc": "Volume per unit"},
        "VOLUME_UOM_CODE": {"type": "VARCHAR2(3)", "desc": "Volume UOM"},
        "STYLE_ITEM_FLAG": {"type": "VARCHAR2(1)", "desc": "Y = Style (parent), N = SKU"},
        "STYLE_ITEM_ID": {"type": "NUMBER(18)", "desc": "Parent style item FK"},
    },
}

EGP_SYSTEM_ITEMS_TL_ALL_V = {
    "description": (
        "View exposing all translation rows for items across all languages. "
        "Useful when you need multi-language item descriptions."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item unique identifier"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization unique identifier"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "desc": "Language code"},
        "SOURCE_LANG": {"type": "VARCHAR2(4)", "desc": "Source language code"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "desc": "Translated item description"},
        "LONG_DESCRIPTION": {"type": "VARCHAR2(4000)", "desc": "Translated long description"},
    },
}

EGP_ITEM_REVISIONS_V = {
    "description": (
        "View joining EGP_ITEM_REVISIONS_B + EGP_ITEM_REVISIONS_TL. "
        "Stores revision history for items. Each row = one revision of one item in one org."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "sql": (
        "SELECT B.*, T.DESCRIPTION "
        "FROM EGP_ITEM_REVISIONS_B B, EGP_ITEM_REVISIONS_TL T "
        "WHERE B.REVISION_ID = T.REVISION_ID AND T.LANGUAGE = USERENV('LANG')"
    ),
    "key_columns": {
        "REVISION_ID": {"type": "NUMBER(18)", "desc": "Revision unique identifier (PK)"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "REVISION": {"type": "VARCHAR2(18)", "desc": "Revision code (e.g. A, B, 01)"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "desc": "Translated revision description"},
        "EFFECTIVITY_DATE": {"type": "DATE", "desc": "Date revision becomes effective"},
        "END_EFFECTIVITY_DATE": {"type": "DATE", "desc": "Date revision stops being effective"},
        "IMPLEMENTATION_DATE": {"type": "DATE", "desc": "Date revision was implemented"},
        "ECN_INITIATION_DATE": {"type": "DATE", "desc": "Engineering Change Notice initiation date"},
        "CHANGE_LINE_ID": {"type": "NUMBER(18)", "desc": "Change order line FK"},
        "CURRENT_PHASE_ID": {"type": "NUMBER(18)", "desc": "Lifecycle phase FK"},
        "ALT_REVISION_CODE": {"type": "VARCHAR2(40)", "desc": "Alternate revision code"},
    },
}

EGP_SYSTEM_ITEMS_B_V = {
    "description": (
        "View on EGP_SYSTEM_ITEMS_B (base table only, no translations). "
        "Use when you do not need DESCRIPTION/LONG_DESCRIPTION."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "note": "Same columns as EGP_SYSTEM_ITEMS_B table. See EGP_SYSTEM_ITEMS for column list.",
}

EGP_ITEM_CAT_ASSIGNMENTS_PUB_V = {
    "description": (
        "Public view of item-to-category assignments. "
        "Convenient alternative to EGP_ITEM_CAT_ASSIGNMENTS table."
    ),
    "schema": "FUSION",
    "owner": "EGP",
}

EGP_ITEM_REVISIONS_B_V = {
    "description": (
        "View on EGP_ITEM_REVISIONS_B base table. "
        "Same columns as the base table without translations."
    ),
    "schema": "FUSION",
    "owner": "EGP",
}

EGP_MFG_PART_NUMBERS = {
    "description": (
        "View for manufacturer part numbers. Links items to manufacturer part numbers and manufacturer IDs. "
        "⚠️ Not re-verified in the 2026-05-29 audit (agent timeout). In 26B the backing object is "
        "EGP_MFG_PART_NUMBERS_B_V where the PK is ITEM_RELATIONSHIP_ID and date columns are START_DATE_ACTIVE/"
        "END_DATE_ACTIVE — confirm column names on-pod before relying on this view."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "MANUFACTURER_ID": {"type": "NUMBER(18)", "desc": "Manufacturer FK"},
        "MFG_PART_NUM": {"type": "VARCHAR2(150)", "desc": "Manufacturer part number"},
    },
}

EGP_FULL_CATEGORY_LIST = {
    "description": (
        "TABLE (not a view) — stores relationship between all catalogs and categories, "
        "including shared category hierarchies (up to 15 parent levels). "
        "Useful for navigating category trees across catalogs. "
        "A companion view EGP_FULL_CATEGORY_LIST_V also exists."
    ),
    "object_type": "TABLE",
    "primary_key": ["CATEGORY_SET_ID", "CATEGORY_ID", "LOAD_ID"],  # 26B-verified 2026-06-01 (LOAD_ID is part of the PK)
    "schema": "FUSION",
    "owner": "EGP",
}

EGP_FLATTENED_VALID_CATS_VL = {
    "description": (
        "Flattened view of valid categories per catalog with translations. "
        "Useful for reporting on full category hierarchies."
    ),
    "schema": "FUSION",
    "owner": "EGP",
}


# ============================================================================
# CORE TABLES - Detailed Column Definitions
# ============================================================================

# ---- ITEM MASTER ----

EGP_SYSTEM_ITEMS_B = {
    "description": (
        "Base item master table. Storage for Item Number (part number/part/item). "
        "Contains 600+ columns covering every item attribute domain. "
        "One row per item per organization."
    ),
    "primary_key": ["INVENTORY_ITEM_ID", "ORGANIZATION_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "TRANSACTION_TABLES",
    "columns": {
        # --- Identifiers ---
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item unique identifier"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization unique identifier"},
        "ITEM_NUMBER": {"type": "VARCHAR2(300)", "nullable": False, "desc": "User-visible part/material/product number"},
        "ITEM_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Classification: finished, purchased, etc."},
        "INVENTORY_ITEM_STATUS_CODE": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Controls transaction activity for the item"},
        "ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item enabled for use"},
        "APPROVAL_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Approval status of the item"},
        "ITEM_CATALOG_GROUP_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Item class FK -> EGP_ITEM_CLASSES_B"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking counter"},

        # --- UOM ---
        "PRIMARY_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Primary unit of measure"},
        "SECONDARY_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Secondary UOM for dual UOM items"},
        "UNIT_OF_ISSUE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "UOM for inventory issuance"},
        "ALLOWED_UNITS_LOOKUP_CODE": {"type": "NUMBER", "nullable": True, "desc": "Standard or item-specific UOM conversion"},
        "DUAL_UOM_CONTROL": {"type": "NUMBER", "nullable": True, "desc": "Dual UOM pricing control"},
        "DUAL_UOM_DEVIATION_HIGH": {"type": "NUMBER", "nullable": True, "desc": "High deviation tolerance for dual UOM"},
        "DUAL_UOM_DEVIATION_LOW": {"type": "NUMBER", "nullable": True, "desc": "Low deviation tolerance for dual UOM"},

        # --- Inventory Control ---
        "INVENTORY_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item can be stocked and transacted in inventory"},
        "STOCK_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item can be stocked"},
        "INVENTORY_ASSET_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Valued as asset in inventory"},
        "RESERVABLE_TYPE": {"type": "NUMBER", "nullable": True, "desc": "Material reservation enabled"},
        "CHECK_SHORTAGES_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Check for material shortages"},
        "REVISION_QTY_CONTROL_CODE": {"type": "NUMBER", "nullable": True, "desc": "Track inventory by revision"},
        "CYCLE_COUNT_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Auto cycle count scheduling"},
        "NEGATIVE_MEASUREMENT_ERROR": {"type": "NUMBER", "nullable": True, "desc": "Negative variance tolerance %"},
        "POSITIVE_MEASUREMENT_ERROR": {"type": "NUMBER", "nullable": True, "desc": "Positive variance tolerance %"},

        # --- Lot Control ---
        "LOT_CONTROL_CODE": {"type": "NUMBER", "nullable": True, "desc": "1=No control, 2=Full lot control"},
        "SHELF_LIFE_CODE": {"type": "NUMBER", "nullable": True, "desc": "How long lots remain available"},
        "SHELF_LIFE_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Active days per lot"},
        "AUTO_LOT_ALPHA_PREFIX": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Auto lot number prefix"},
        "START_AUTO_LOT_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Starting auto lot number"},
        "LOT_DIVISIBLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Lot can be split"},
        "LOT_MERGE_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Multiple lots can merge"},
        "LOT_SUBSTITUTION_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Lots can be substituted"},
        "LOT_STATUS_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Status control at lot level"},
        "DEFAULT_LOT_STATUS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default lot status"},
        "CHILD_LOT_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Subject to child lot control"},
        "CHILD_LOT_PREFIX": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Child lot alpha prefix"},
        "CHILD_LOT_STARTING_NUMBER": {"type": "NUMBER", "nullable": True, "desc": "Child lot starting number"},
        "CHILD_LOT_VALIDATION_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Validate child lot parameters"},
        "COPY_LOT_ATTRIBUTE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Child inherits parent lot attributes"},
        "PARENT_CHILD_GENERATION_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "How child lots are generated"},
        "GRADE_CONTROL_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Grade controlled with lots"},
        "DEFAULT_GRADE": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Default grade for item"},
        "MATURITY_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Days to lot maturity"},
        "HOLD_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Days before lot release"},
        "RETEST_INTERVAL": {"type": "NUMBER", "nullable": True, "desc": "Days before retest required"},
        "EXPIRATION_ACTION_CODE": {"type": "VARCHAR2(32)", "nullable": True, "desc": "Default expiration action"},
        "EXPIRATION_ACTION_INTERVAL": {"type": "NUMBER", "nullable": True, "desc": "Days before expiration action"},

        # --- Serial Control ---
        "SERIAL_NUMBER_CONTROL_CODE": {"type": "NUMBER", "nullable": True, "desc": "1=No, 2=Predefined, 5=At receipt, 6=At SO issue"},
        "AUTO_SERIAL_ALPHA_PREFIX": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Serial number alpha prefix"},
        "START_AUTO_SERIAL_NUMBER": {"type": "VARCHAR2(80)", "nullable": True, "desc": "Starting auto serial number"},
        "SERIAL_STATUS_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Status control at serial level"},
        "DEFAULT_SERIAL_STATUS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default serial status"},

        # --- Purchasing ---
        "PURCHASING_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item can appear on purchase orders"},
        "PURCHASING_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item currently purchasable"},
        "MUST_USE_APPROVED_VENDOR_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Only approved suppliers allowed"},
        "LIST_PRICE_PER_UNIT": {"type": "NUMBER", "nullable": True, "desc": "Default price for RFQ/PO"},
        "MARKET_PRICE": {"type": "NUMBER", "nullable": True, "desc": "Market price printed on PO"},
        "BUYER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default buyer FK"},
        "PRICE_TOLERANCE_PERCENT": {"type": "NUMBER", "nullable": True, "desc": "Max price variance acceptable"},
        "PURCHASING_TAX_CODE": {"type": "VARCHAR2(50)", "nullable": True, "desc": "Tax classification code"},
        "TAXABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Supplier charges tax"},
        "OUTSIDE_OPERATION_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Can be added to outside processing PO"},

        # --- Receiving ---
        "RECEIVING_ROUTING_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Receipt routing (direct, standard, inspection)"},
        "RECEIPT_REQUIRED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Supplier receipt required before payment"},
        "ALLOW_UNORDERED_RECEIPTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Receive without PO"},
        "ALLOW_SUBSTITUTE_RECEIPTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Receive substitutes"},
        "DAYS_EARLY_RECEIPT_ALLOWED": {"type": "NUMBER", "nullable": True, "desc": "Days before promise date"},
        "DAYS_LATE_RECEIPT_ALLOWED": {"type": "NUMBER", "nullable": True, "desc": "Days after promise date"},
        "RECEIPT_DAYS_EXCEPTION_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Action if outside receipt days range"},
        "QTY_RCV_TOLERANCE": {"type": "NUMBER", "nullable": True, "desc": "Over-receipt tolerance percent"},
        "QTY_RCV_EXCEPTION_CODE": {"type": "VARCHAR2(25)", "nullable": True, "desc": "Action if outside quantity tolerance"},
        "INVOICE_MATCH_OPTION": {"type": "NUMBER(1)", "nullable": True, "desc": "2=2-way, 3=3-way, 4=4-way matching"},
        "MATCH_APPROVAL_LEVEL": {"type": "NUMBER(1)", "nullable": True, "desc": "1=PO, 2=Receipt level matching"},
        "INVOICE_CLOSE_TOLERANCE": {"type": "NUMBER", "nullable": True, "desc": "Auto-close tolerance percent"},

        # --- Planning ---
        "INVENTORY_PLANNING_CODE": {"type": "NUMBER", "nullable": True, "desc": "Planning method for organization"},
        "MRP_PLANNING_CODE": {"type": "NUMBER", "nullable": True, "desc": "Min-Max, Not Planned, Reorder Point"},
        "PLANNER_CODE": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Material planner assignment"},
        "PLANNING_MAKE_BUY_CODE": {"type": "NUMBER", "nullable": True, "desc": "1=Make, 2=Buy"},
        "STD_LOT_SIZE": {"type": "NUMBER", "nullable": True, "desc": "Standard order quantity"},
        "FIXED_ORDER_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Fixed order quantity for planned orders"},
        "FIXED_DAYS_SUPPLY": {"type": "NUMBER", "nullable": True, "desc": "Days used to modify order timing"},
        "MINIMUM_ORDER_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Minimum order quantity"},
        "MAXIMUM_ORDER_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Maximum order quantity"},
        "MIN_MINMAX_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Minimum for Min-Max planning"},
        "MAX_MINMAX_QUANTITY": {"type": "NUMBER", "nullable": True, "desc": "Maximum for Min-Max planning"},
        "MRP_SAFETY_STOCK_CODE": {"type": "NUMBER", "nullable": True, "desc": "Fixed or dynamic safety stock"},
        "MRP_SAFETY_STOCK_PERCENT": {"type": "NUMBER", "nullable": True, "desc": "Safety stock percent"},
        "SAFETY_STOCK_BUCKET_DAYS": {"type": "NUMBER", "nullable": True, "desc": "Repetitive planning period workdays"},

        # --- Lead Times ---
        "FULL_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Total days to procure/manufacture"},
        "FIXED_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Days independent of order quantity"},
        "VARIABLE_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Additional time per unit"},
        "CUM_MANUFACTURING_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Assembly + largest component lead time"},
        "CUMULATIVE_TOTAL_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Total lead time for assembly + all components"},
        "PREPROCESSING_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Days to add to place order"},
        "POSTPROCESSING_LEAD_TIME": {"type": "NUMBER", "nullable": True, "desc": "Days to receive into inventory"},
        "LEAD_TIME_LOT_SIZE": {"type": "NUMBER", "nullable": True, "desc": "Lot size for lead time computation"},

        # --- Physical Attributes ---
        "UNIT_WEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Weight of one unit"},
        "WEIGHT_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Weight unit of measure"},
        "UNIT_VOLUME": {"type": "NUMBER", "nullable": True, "desc": "Volume of one unit"},
        "VOLUME_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Volume unit of measure"},
        "UNIT_LENGTH": {"type": "NUMBER", "nullable": True, "desc": "Item length"},
        "UNIT_WIDTH": {"type": "NUMBER", "nullable": True, "desc": "Item width"},
        "UNIT_HEIGHT": {"type": "NUMBER", "nullable": True, "desc": "Item height"},
        "DIMENSION_UOM_CODE": {"type": "VARCHAR2(3)", "nullable": True, "desc": "Dimension UOM"},
        "SHRINKAGE_RATE": {"type": "NUMBER", "nullable": True, "desc": "Material loss factor"},

        # --- BOM / Manufacturing ---
        "BOM_ITEM_TYPE": {"type": "NUMBER", "nullable": True, "desc": "1=Model, 2=Option Class, 4=Standard, 5=Planning"},
        "BUILD_IN_WIP_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Create jobs/assemblies in WIP"},
        "PICK_COMPONENTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "BOM with picked options"},
        "REPLENISH_TO_ORDER_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Built for sales order demand"},
        "BASE_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Model for ATO configuration"},
        "EFFECTIVITY_CONTROL": {"type": "NUMBER", "nullable": True, "desc": "Date/Model/Unit effectivity"},
        "WIP_SUPPLY_TYPE": {"type": "NUMBER(18)", "nullable": True, "desc": "Supply type for WIP components"},
        "WIP_SUPPLY_SUBINVENTORY": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Primary subinventory for WIP"},

        # --- Order Management ---
        "CUSTOMER_ORDER_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Allow external customer orders"},
        "CUSTOMER_ORDER_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item currently orderable"},
        "INTERNAL_ORDER_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Allow internal transfer orders"},
        "INTERNAL_ORDER_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Orderable on internal requisitions"},
        "SHIPPABLE_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Ship to customer allowed"},
        "RETURNABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Allow customer returns"},
        "BACK_ORDERABLE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item can be backordered"},
        "SO_TRANSACTIONS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "OM demand transactions allowed"},
        "DEFAULT_SO_SOURCE_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Internal/External (drop-ship indicator)"},

        # --- Sourcing ---
        "SOURCE_TYPE": {"type": "NUMBER", "nullable": True, "desc": "Fulfillment source (Inventory, Supplier, Subinventory)"},
        "SOURCE_ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Internal requisition source org"},
        "SOURCE_SUBINVENTORY": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Subinventory source"},
        "BACK_TO_BACK_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Back-to-back ordering enabled"},

        # --- Costing ---
        "COSTING_ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Report/value/account costs"},
        "DEFAULT_INCLUDE_IN_ROLLUP_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Include in cost rollup"},
        "CARRYING_COST": {"type": "NUMBER", "nullable": True, "desc": "% of unit cost to stock annually"},
        "ORDER_COST": {"type": "NUMBER", "nullable": True, "desc": "Fixed cost to place order"},

        # --- Service ---
        "SERVICEABLE_PRODUCT_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Eligible for service contract"},
        "SERVICE_DURATION": {"type": "NUMBER", "nullable": True, "desc": "Service duration"},
        "SERVICE_DURATION_PERIOD_CODE": {"type": "VARCHAR2(10)", "nullable": True, "desc": "Duration period type"},

        # --- Style / SKU ---
        "STYLE_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y=Style (parent), N=SKU"},
        "STYLE_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent style item FK"},

        # --- Hazardous / Compliance ---
        "HAZARDOUS_MATERIAL_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item is hazardous"},
        "HAZARD_CLASS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Hazard material category"},
        "CAS_NUMBER": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Chemical Abstracts Service number"},
        "UN_NUMBER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "UN identification for intl trade"},

        # --- Locator / Subinventory Control ---
        "RESTRICT_LOCATORS_CODE": {"type": "NUMBER", "nullable": True, "desc": "Restrict to specified locators"},
        "RESTRICT_SUBINVENTORIES_CODE": {"type": "NUMBER", "nullable": True, "desc": "Restrict to specified subinventories"},
        "LOCATION_CONTROL_CODE": {"type": "NUMBER", "nullable": True, "desc": "Physical storage area control"},

        # --- ATP ---
        "ATP_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Check ATP / capable to promise"},
        "ATP_RULE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "User-defined ATP rule"},
        "ATP_COMPONENTS_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Include components in ATP checking"},

        # --- EAM / Maintenance ---
        "EAM_ITEM_TYPE": {"type": "NUMBER", "nullable": True, "desc": "Asset Group, Activity, Rebuildable Item"},
        "EQUIPMENT_TYPE": {"type": "NUMBER", "nullable": True, "desc": "Item is equipment"},
        "ASSET_TRACKED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Tracked as asset in Installed Base"},

        # --- Web / E-commerce ---
        "WEB_STATUS": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Enabled, Published, Unpublished"},
        "ORDERABLE_ON_WEB_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Orderable from web"},

        # --- Versioning / Change Management ---
        "VERSION_ID": {"type": "NUMBER(20)", "nullable": True, "desc": "Version number identifier"},
        "ACD_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "ADD/UPDATE/DELETE/HISTORY"},
        "CHANGE_LINE_ID": {"type": "NUMBER(20)", "nullable": True, "desc": "Change order line FK"},
        "VERSION_START_DATE": {"type": "DATE", "nullable": True, "desc": "Version effective start date"},
        "VERSION_END_DATE": {"type": "DATE", "nullable": True, "desc": "Version effective end date"},
        "IMPLEMENTATION_DATE": {"type": "DATE", "nullable": True, "desc": "Implementation date"},
        "CURRENT_PHASE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Item lifecycle phase FK"},
        "CURRENT_PHASE_CODE": {"type": "VARCHAR2(120)", "nullable": True, "desc": "Item lifecycle phase code"},

        # --- Organization ---
        "MASTER_ORG_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Master organization ID"},
        "INVENTORY_ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Org tracking inventory"},

        # --- DFF (Descriptive Flexfields) ---
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF structure definition"},
        "ATTRIBUTE1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "DFF segment 1 (through ATTRIBUTE30)"},
        "ATTRIBUTE_NUMBER1": {"type": "NUMBER", "nullable": True, "desc": "Numeric DFF segment 1 (through 10)"},
        "ATTRIBUTE_DATE1": {"type": "DATE", "nullable": True, "desc": "Date DFF segment 1 (through 5)"},
        "ATTRIBUTE_TIMESTAMP1": {"type": "TIMESTAMP", "nullable": True, "desc": "Timestamp DFF segment 1 (through 5)"},
        "GLOBAL_ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Global DFF structure definition"},
        "GLOBAL_ATTRIBUTE1": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Global DFF segment 1 (through 20)"},
        "GLOBAL_ATTRIBUTE_NUMBER1": {"type": "NUMBER", "nullable": True, "desc": "Global numeric DFF 1 (through 5)"},
        "GLOBAL_ATTRIBUTE_DATE1": {"type": "DATE", "nullable": True, "desc": "Global date DFF 1 (through 5)"},

        # --- Audit ---
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who created the row"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "User who last updated the row"},
        "LAST_UPDATE_LOGIN": {"type": "VARCHAR2(32)", "nullable": True, "desc": "Session login of last updater"},
        "REQUEST_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "ESS job request ID"},

        # --- Trading Partner: CONFIRMED present on EGP_SYSTEM_ITEMS_B in 26B
        #     (members of unique index EGP_SYSTEM_ITEMS_B_U3). Verified 2026-06-01 against
        #     26b/oedsc/egpsystemitemsb-4735.html. EGP_TRADING_PARTNER_ITEMS also exists separately. ---
        "TRADING_PARTNER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Trading partner (supplier/customer/etc.) FK; part of index U3"},
        "TP_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Trading partner type: CUSTOMER, MANUFACTURER, COMPETITOR, SUPPLIER"},
        "TP_ITEM_NUMBER": {"type": "VARCHAR2(300)", "nullable": True, "desc": "Trading partner's item number; part of index U3"},

        # --- Misc ---
        "COMPLETENESS_SCORE": {"type": "NUMBER(3)", "nullable": True, "desc": "Item data completeness percentage"},
        "PRELIMINARY_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Item in preliminary state"},
        "ITEM_CLASS_CODE": {"type": "VARCHAR2(800)", "nullable": True, "desc": "UNSPSC category association"},
        "PRIMARY_IMAGE_URL": {"type": "VARCHAR2(4000)", "nullable": True, "desc": "Primary image attachment URL"},
        "ENGINEERED_ITEM_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Engineered using PDL"},
        "CONTRACT_MANUFACTURING": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Contract manufacturing item"},
    },
    "indexes": {
        "EGP_SYSTEM_ITEMS_B_U1 (Unique)": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "EGP_SYSTEM_ITEMS_B_U3 (Unique)": "ORGANIZATION_ID, ITEM_NUMBER, TRADING_PARTNER_ID, TP_TYPE, TP_ITEM_NUMBER",
        "EGP_SYSTEM_ITEMS_B_N1": "ITEM_NUMBER",
        "EGP_SYSTEM_ITEMS_B_N16": "UPPER(ITEM_NUMBER), ORGANIZATION_ID",
        "EGP_SYSTEM_ITEMS_B_N32": "ORGANIZATION_ID, UPPER(ITEM_NUMBER), ACD_TYPE",
    },
    "foreign_keys": {
        "-> EGP_SYSTEM_ITEMS_TL": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGP_ITEM_CAT_ASSIGNMENTS": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGO_ITEM_EFF_B": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGP_ITEM_RELATIONSHIPS_B": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGP_ITEM_REVISIONS_B": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGP_ITEM_TEXT_TL": "ITEM_ID, ORG_ID",
        "-> EGO_ITEM_ASSOCIATIONS": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGP_SYSTEM_ITEMS_INTERFACE": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
    },
}

EGP_SYSTEM_ITEMS_TL = {
    "description": (
        "Translation table for item descriptions. "
        "One row per item per org per language. "
        "Join to EGP_SYSTEM_ITEMS_B on INVENTORY_ITEM_ID + ORGANIZATION_ID."
    ),
    "primary_key": ["INVENTORY_ITEM_ID", "ORGANIZATION_ID", "LANGUAGE"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_SEED",
    "columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization FK"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Language code (e.g. US, FR)"},
        "SOURCE_LANG": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Source language"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Translated item description"},
        "LONG_DESCRIPTION": {"type": "VARCHAR2(4000)", "nullable": True, "desc": "Translated long description"},
        "HTML_LONG_DESCRIPTION": {"type": "CLOB", "nullable": True, "desc": "HTML-formatted long description"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}


# ---- CATEGORIES ----

EGP_CATEGORIES_B = {
    "description": (
        "Base table for item categories. "
        "A category is a grouping mechanism used within a catalog (category set). "
        "One row per category."
    ),
    "primary_key": ["CATEGORY_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_TX_DATA",
    "columns": {
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category unique identifier (PK)"},
        "CATEGORY_CODE": {"type": "VARCHAR2(820)", "nullable": True, "desc": "Unique user-readable category code"},
        "SEGMENT1": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Key flexfield segment 1"},
        "SEGMENT2": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Key flexfield segment 2"},
        "SEGMENT3": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Key flexfield segment 3 (up to segment 20)"},
        "ENABLED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Category enabled"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Start date"},
        "END_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "End date"},
        "SUMMARY_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Summary flag"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "DFF segment 1 (through 15)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}

EGP_CATEGORIES_TL = {
    "description": (
        "Translation table for categories. "
        "One row per category per language. "
        "Provides translatable CATEGORY_NAME and DESCRIPTION."
    ),
    "primary_key": ["CATEGORY_ID", "LANGUAGE"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_TX_DATA",
    "columns": {
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category FK"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Language code"},
        "SOURCE_LANG": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Source language"},
        "CATEGORY_NAME": {"type": "VARCHAR2(250)", "nullable": False, "desc": "Translatable category name"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Translatable category description"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}

# EGP_CATEGORIES_VL = B + TL joined on CATEGORY_ID WHERE LANGUAGE = USERENV('LANG')


# ---- CATEGORY SETS (CATALOGS) ----

EGP_CATEGORY_SETS_B = {
    "description": (
        "Base table for item catalogs (category sets). "
        "Each catalog groups items into categories for a functional purpose "
        "(e.g. Purchasing, Inventory, Planning). One row per catalog."
    ),
    "primary_key": ["CATEGORY_SET_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_SEED",
    "columns": {
        "CATEGORY_SET_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Catalog unique identifier (PK)"},
        "CATALOG_CODE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Unique user-readable catalog code"},
        "CONTROL_LEVEL": {"type": "NUMBER(9)", "nullable": False, "desc": "1=Auto assign to child orgs, 2=Current org only"},
        "MULT_ITEM_CAT_ASSIGN_FLAG": {"type": "VARCHAR2(1)", "nullable": False, "desc": "Allow multiple categories per item in this catalog"},
        "HIERARCHY_ENABLED": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Catalog supports category hierarchy"},
        "DEFAULT_CATEGORY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Default category for new items"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Date catalog becomes active"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Date catalog becomes inactive"},
        "SEQUENCE_NUMBER": {"type": "NUMBER(9)", "nullable": True, "desc": "Display order"},
        "CATALOG_CONTENT_CODE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Items assigned only at leaf categories"},
        "PUBLIC_CATALOG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Public catalog access flag"},
        "FUNCTIONAL_AREA_CATALOG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Functional area association flag"},
        "RAISE_ITEM_CAT_ASSIGN_EVENT": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Trigger change event for item assignments"},
        "RAISE_ALT_CAT_HIER_CHG_EVENT": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Trigger change event for category hierarchy"},
        "VALIDATE_FLAG": {"type": "VARCHAR2(1)", "nullable": False, "desc": "Deprecated"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(150)", "nullable": True, "desc": "DFF segment 1 (through 15)"},
        "ATTRIBUTE_NUMBER1": {"type": "NUMBER", "nullable": True, "desc": "Numeric DFF 1 (through 10)"},
        "ATTRIBUTE_DATE1": {"type": "DATE", "nullable": True, "desc": "Date DFF 1 (through 5)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
    "foreign_keys": {
        "-> EGP_CATEGORY_SETS_TL": "CATEGORY_SET_ID",
        "-> EGP_DEFAULT_CATEGORY_SETS": "CATEGORY_SET_ID",
        "-> EGP_CATEGORY_SET_VALID_CATS": "CATEGORY_SET_ID",
        "-> EGP_CATG_MAP_HDRS_B": "SOURCE_CATG_SET_ID / TARGET_CATG_SET_ID",
    },
    "indexes": {
        "EGP_CATEGORY_SETS_B_PK (Unique)": "CATEGORY_SET_ID",
        "EGP_CATEGORY_SETS_B_N1": "STATUS_FLAG",
        "EGP_CATEGORY_SETS_B_N2": "LAST_UPDATE_DATE",
    },
}

# EGP_CATEGORY_SETS_TL: Translation table for catalogs (CATEGORY_SET_NAME, DESCRIPTION)
# EGP_CATEGORY_SETS_VL = B + TL joined on CATEGORY_SET_ID WHERE LANGUAGE = USERENV('LANG')


# ---- ITEM-CATEGORY ASSIGNMENTS ----

EGP_ITEM_CAT_ASSIGNMENTS = {
    "description": (
        "Items assigned to a catalog (category set) and its category. "
        "One row per item + org + catalog + category combination."
    ),
    "primary_key": ["INVENTORY_ITEM_ID", "ORGANIZATION_ID", "CATEGORY_SET_ID", "CATEGORY_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_TX_DATA",
    "columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item FK -> EGP_SYSTEM_ITEMS_B"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization FK"},
        "CATEGORY_SET_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Catalog FK -> EGP_CATEGORY_SETS_B"},
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category FK -> EGP_CATEGORIES_B"},
        "ITEM_CATEGORY_ASSIGNMENT_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Surrogate PK (unique)"},
        "SEQUENCE_NUMBER": {"type": "NUMBER(9)", "nullable": True, "desc": "Display order of categories"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "Effective start date"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "Effective end date"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
    "indexes": {
        "EGP_ITEM_CAT_ASSIGNMENTS_PK (Unique)": "INVENTORY_ITEM_ID, ORGANIZATION_ID, CATEGORY_SET_ID, CATEGORY_ID",
        "EGP_ITEM_CAT_ASSIGNMENTS_U2 (Unique)": "ITEM_CATEGORY_ASSIGNMENT_ID",
        "EGP_ITEM_CAT_ASSIGNMENTS_N1": "CATEGORY_SET_ID, CATEGORY_ID, ORGANIZATION_ID",
        "EGP_ITEM_CAT_ASSIGNMENTS_N2": "LAST_UPDATE_DATE, INVENTORY_ITEM_ID, ORGANIZATION_ID",
    },
}

# EGP_ITEM_CATEGORIES: View joining assignments with category/catalog details

EGP_CATEGORY_SET_VALID_CATS = {
    "description": (
        "Valid categories per catalog. "
        "Controls which categories are allowed in each category set."
    ),
    "primary_key": ["CATEGORY_SET_ID", "CATEGORY_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "columns": {
        "CATEGORY_SET_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Catalog FK"},
        "CATEGORY_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Category FK"},
        "PARENT_CATEGORY_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent category (hierarchy)"},
    },
}

EGP_DEFAULT_CATEGORY_SETS = {
    "description": (
        "Default category set per functional area. "
        "Maps functional areas (Purchasing, Inventory, Planning, etc.) "
        "to their default catalog."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "columns": {
        "FUNCTIONAL_AREA_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Functional area identifier"},
        "CATEGORY_SET_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Default catalog FK"},
    },
}


# ---- EXTENSIBLE FLEXFIELDS (EFF) ----

EGO_ITEM_EFF_B = {
    "description": (
        "Extensible Flexfield (EFF) table for item-level custom attributes. "
        "Stores version-controlled attribute data with change tracking. "
        "Each row = one EFF context instance for one item. "
        "Supports up to 40 character, 20 number, 10 date, and 10 timestamp attributes."
    ),
    "primary_key": ["EFF_LINE_ID"],
    "schema": "FUSION",
    "owner": "EGO",
    "tablespace": "TRANSACTION_TABLES",
    "columns": {
        "EFF_LINE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Row unique identifier (PK)"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item FK -> EGP_SYSTEM_ITEMS_B"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization FK"},
        "CATEGORY_CODE": {"type": "VARCHAR2(800)", "nullable": False, "desc": "Item Class code associated with the item"},
        "CONTEXT_CODE": {"type": "VARCHAR2(80)", "nullable": False, "desc": "Internal name of the attribute group"},
        "VERSION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Version FK -> EGO_VERSIONS_B"},
        "VERSION_START_DATE": {"type": "DATE", "nullable": False, "desc": "Version effective start date"},
        "VERSION_END_DATE": {"type": "DATE", "nullable": True, "desc": "Version effective end date"},
        "CHANGE_LINE_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Change order line FK"},
        "ACD_TYPE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "ADD/UPDATE/DELETE modification type"},
        "CHANGE_BIT_MAP": {"type": "VARCHAR2(200)", "nullable": False, "desc": "Bitmap indicating changed attributes"},
        "IMPLEMENTATION_DATE": {"type": "DATE", "nullable": True, "desc": "Implementation date"},
        "ATTRIBUTE_CHAR1": {"type": "VARCHAR2(4000)", "nullable": True, "desc": "Character attribute 1 (through ATTRIBUTE_CHAR40)"},
        "ATTRIBUTE_NUMBER1": {"type": "NUMBER", "nullable": True, "desc": "Number attribute 1 (through ATTRIBUTE_NUMBER20)"},
        "ATTRIBUTE_DATE1": {"type": "DATE", "nullable": True, "desc": "Date attribute 1 (through ATTRIBUTE_DATE10)"},
        "ATTRIBUTE_TIMESTAMP1": {"type": "TIMESTAMP", "nullable": True, "desc": "Timestamp attribute 1 (through ATTRIBUTE_TIMESTAMP10)"},
        "ATTRIBUTE_NUMBER1_UOM": {"type": "VARCHAR2(9)", "nullable": True, "desc": "UOM for number attr 1 (through 20)"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
    "indexes": {
        "EGO_ITEM_EFF_B_PK (Unique)": "EFF_LINE_ID",
        "EGO_ITEM_EFF_B_U1 (Unique)": "EFF_LINE_ID, VERSION_START_DATE, CHANGE_LINE_ID",
        "EGO_ITEM_EFF_B_U2 (Unique)": "EFF_LINE_ID, CHANGE_LINE_ID, VERSION_ID, ACD_TYPE",
        "EGO_ITEM_EFF_B_N1": "ORGANIZATION_ID, INVENTORY_ITEM_ID, CONTEXT_CODE",
        "EGO_ITEM_EFF_B_N4": "CONTEXT_CODE, CATEGORY_CODE",
        "EGO_ITEM_EFF_B_N5": "INVENTORY_ITEM_ID, CONTEXT_CODE, ORGANIZATION_ID",
    },
    "foreign_keys": {
        "-> EGP_SYSTEM_ITEMS_B": "INVENTORY_ITEM_ID, ORGANIZATION_ID",
        "-> EGO_VERSIONS_B": "VERSION_ID",
    },
}

EGO_ITEM_EFF_TL = {
    "description": (
        "Translation table for item EFF translatable attributes. "
        "Stores translated character attribute values."
    ),
    "primary_key": ["EFF_LINE_ID", "LANGUAGE"],
    "schema": "FUSION",
    "owner": "EGO",
}

EGO_ITEM_REVISION_EFF_B = {
    "description": (
        "Extensible Flexfield (EFF) table for revision-level custom attributes. "
        "Similar structure to EGO_ITEM_EFF_B but keyed by REVISION_ID."
    ),
    "schema": "FUSION",
    "owner": "EGO",
    "key_columns": {
        "EFF_LINE_ID": {"type": "NUMBER(18)", "desc": "Row PK"},
        "REVISION_ID": {"type": "NUMBER(18)", "desc": "Revision FK -> EGP_ITEM_REVISIONS_B"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "CONTEXT_CODE": {"type": "VARCHAR2(80)", "desc": "Attribute group internal name"},
    },
}


# ---- ITEM REVISIONS ----

EGP_ITEM_REVISIONS_B = {
    "description": (
        "Base table for item revisions. "
        "Stores revision history: each row = one revision of one item in one org."
    ),
    "primary_key": ["REVISION_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "TRANSACTION_TABLES",
    "columns": {
        "REVISION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Revision unique identifier (PK)"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item FK -> EGP_SYSTEM_ITEMS_B"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization FK"},
        "REVISION": {"type": "VARCHAR2(18)", "nullable": False, "desc": "Revision code (e.g. A, B, 01)"},
        "REVISION_REASON": {"type": "VARCHAR2(30)", "nullable": True, "desc": "Reason for creating revision"},
        "EFFECTIVITY_DATE": {"type": "DATE", "nullable": True, "desc": "Date revision becomes effective"},
        "END_EFFECTIVITY_DATE": {"type": "DATE", "nullable": True, "desc": "Date revision stops being effective"},
        "ECN_INITIATION_DATE": {"type": "DATE", "nullable": True, "desc": "Engineering Change Notice initiation date"},
        "IMPLEMENTATION_DATE": {"type": "DATE", "nullable": True, "desc": "Implementation date"},
        "CHANGE_LINE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Change order line FK"},
        "CURRENT_PHASE_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Lifecycle phase FK"},
        "ALT_REVISION_CODE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Alternate revision code"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "DFF segment 1 (through 15)"},
        "ATTRIBUTE_NUMBER1": {"type": "NUMBER", "nullable": True, "desc": "Numeric DFF 1 (through 10)"},
        "ATTRIBUTE_DATE1": {"type": "DATE", "nullable": True, "desc": "Date DFF 1 (through 5)"},
        "ATTRIBUTE_TIMESTAMP1": {"type": "TIMESTAMP", "nullable": True, "desc": "Timestamp DFF 1 (through 5)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}

EGP_ITEM_REVISIONS_TL = {
    "description": (
        "Translation table for item revisions. "
        "Provides translatable DESCRIPTION per revision per language."
    ),
    "primary_key": ["REVISION_ID", "LANGUAGE"],
    "schema": "FUSION",
    "owner": "EGP",
    "columns": {
        "REVISION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Revision FK"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Language code"},
        "SOURCE_LANG": {"type": "VARCHAR2(4)", "nullable": False, "desc": "Source language"},
        "DESCRIPTION": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Translated revision description"},
    },
}


# ---- ITEM RELATIONSHIPS ----

EGP_ITEM_RELATIONSHIPS_B = {
    "description": (
        "Stores item-to-item relationships: "
        "related items, substitutes, cross-references, superseded-by, etc."
    ),
    "primary_key": ["ITEM_RELATIONSHIP_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "FUSION_TS_TX_DATA",
    "columns": {
        "ITEM_RELATIONSHIP_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Relationship unique identifier (PK)"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Source item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Organization FK"},
        "RELATED_ITEM_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Target/related item FK"},
        "ITEM_RELATIONSHIP_TYPE": {"type": "VARCHAR2(30)", "nullable": False, "desc": "Relationship type code, e.g. SUBSTITUTE/ITEM_XREF (renamed from RELATIONSHIP_TYPE_ID; now a VARCHAR2 code)"},
        "RECIPROCAL_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Relationship is bidirectional"},
        "START_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective start date (renamed from START_DATE)"},
        "END_DATE_ACTIVE": {"type": "DATE", "nullable": True, "desc": "Effective end date (renamed from END_DATE)"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(150)", "nullable": True, "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(150)", "nullable": True, "desc": "DFF segment 1 (through 15)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}

EGP_ITEM_RELATIONSHIPS_TL = {
    "description": "Translation table for item relationships.",
    "schema": "FUSION",
    "owner": "EGP",
}


# ---- ITEM CLASSES ----

EGP_ITEM_CLASSES_B = {
    "description": (
        "Item classes (formerly item catalog groups). "
        "Defines the classification hierarchy for items. "
        "Each item class can have its own set of EFF attribute groups."
    ),
    "primary_key": ["ITEM_CLASS_ID"],
    "schema": "FUSION",
    "owner": "EGP",
    "tablespace": "REFERENCE",
    "columns": {
        "ITEM_CLASS_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Item class unique identifier, PK (renamed from ITEM_CATALOG_GROUP_ID)"},
        "ITEM_CLASS_CODE": {"type": "VARCHAR2(80)", "nullable": False, "desc": "Internal code for the item class (replaces INTERNAL_NAME)"},
        "PARENT_ITEM_CLASS_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent item class, hierarchy (renamed from PARENT_CATALOG_GROUP_ID)"},
        "ITEM_CREATION_ALLOWED_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Items can be created in this class"},
        "OBJECT_VERSION_NUMBER": {"type": "NUMBER(9)", "nullable": False, "desc": "Optimistic locking"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "nullable": True, "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(240)", "nullable": True, "desc": "DFF segment 1 (through 15)"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Row creation timestamp"},
        "CREATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Creator"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "LAST_UPDATED_BY": {"type": "VARCHAR2(64)", "nullable": False, "desc": "Last updater"},
    },
}

EGP_ITEM_CLASSES_TL = {
    "description": "Translation table for item classes. Provides translatable CLASS_NAME and DESCRIPTION.",
    "primary_key": ["ITEM_CLASS_ID", "LANGUAGE"],
    "schema": "FUSION",
    "owner": "EGP",
}


# ---- ITEM ASSOCIATIONS ----

EGO_ITEM_ASSOCIATIONS = {
    "description": (
        "Item-supplier, item-customer, and item-manufacturer associations. "
        "Links items to trading partners with effectivity dating."
    ),
    "schema": "FUSION",
    "owner": "EGO",
    # 26B-verified (2026-06-01, 25c/oedsc/egoitemassociations-5190): PK is the 7-column composite below,
    # NOT ASSOCIATION_ID. ITEM_ASSOCIATION_ID does not exist; ASSOCIATION_ID is a non-key unique id.
    "primary_key": [
        "INVENTORY_ITEM_ID", "ORGANIZATION_ID", "ACD_TYPE",
        "CHANGE_LINE_ID", "VERSION_ID", "SUPPLIER_ID", "SUPPLIER_SITE_ID",
    ],
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK (PK member)"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK (PK member)"},
        "ACD_TYPE": {"type": "VARCHAR2(30)", "desc": "Add/Change/Delete change type (PK member)"},
        "CHANGE_LINE_ID": {"type": "NUMBER(18)", "desc": "Change order line FK (PK member)"},
        "VERSION_ID": {"type": "NUMBER(18)", "desc": "Version FK -> EGO_VERSIONS_B (PK member)"},
        "SUPPLIER_ID": {"type": "NUMBER(18)", "desc": "Supplier FK (PK member; replaces generic TRADING_PARTNER_ID)"},
        "SUPPLIER_SITE_ID": {"type": "NUMBER(18)", "desc": "Supplier site FK (PK member)"},
        "ASSOCIATION_ID": {"type": "NUMBER(18)", "desc": "Non-key surrogate unique id (NOT the PK; ITEM_ASSOCIATION_ID does not exist)"},
        "PRIMARY_FLAG": {"type": "VARCHAR2(1)", "desc": "Y/N - primary supplier association"},
        "VERSION_START_DATE": {"type": "DATE", "desc": "Effective start date (renamed from START_DATE)"},
        "VERSION_END_DATE": {"type": "DATE", "desc": "Effective end date (renamed from END_DATE)"},
    },
}

EGP_ITEM_ORG_ASSOCIATIONS = {
    "description": (
        "Item-to-organization associations. "
        "Tracks which items are assigned to which organizations."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "INVENTORY_ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Inventory organization FK (MASTER_ORGANIZATION_ID is not documented on this table)"},
        "ITEM_DEFINITION_ORG_ID": {"type": "NUMBER(18)", "desc": "Item-defining (master) organization FK — use for master-org lookups"},
    },
}

EGP_MFG_PART_NUMBERS_B = {
    "description": (
        "Manufacturer part numbers. "
        "Links items to specific part numbers from manufacturers."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    # In 26B exposed as the view EGP_MFG_PART_NUMBERS_B_V (built on EGP_ITEM_RELATIONSHIPS_B + EGP_TRADING_PARTNER_ITEMS).
    "key_columns": {
        "ITEM_RELATIONSHIP_ID": {"type": "NUMBER(18)", "desc": "Row PK (renamed from MFG_PART_NUM_ID)"},
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "MANUFACTURER_ID": {"type": "NUMBER(18)", "desc": "Manufacturer FK"},
        "MFG_PART_NUM": {"type": "VARCHAR2(150)", "desc": "Manufacturer part number"},
        "START_DATE_ACTIVE": {"type": "DATE", "desc": "Effective start date (renamed from START_DATE)"},
        "END_DATE_ACTIVE": {"type": "DATE", "desc": "Effective end date (renamed from END_DATE)"},
    },
}


# ---- BOM / ITEM STRUCTURES ----

EGP_STRUCTURES_B = {
    "description": (
        "Bill of Material (BOM) structures. "
        "Each row = a unique manufacturing or engineering bill. "
        "Identified by BILL_SEQUENCE_ID."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "BILL_SEQUENCE_ID": {"type": "NUMBER(18)", "desc": "BOM unique identifier (PK)"},
        "COMMON_ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK (docs use COMMON_ORGANIZATION_ID, not ORGANIZATION_ID; assembly item via PK1_VALUE/PK2_VALUE)"},
        "COMMON_ASSEMBLY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Assembly (parent) item FK (docs use COMMON_ASSEMBLY_ITEM_ID, not ASSEMBLY_ITEM_ID)"},
        "STRUCTURE_TYPE_ID": {"type": "NUMBER(18)", "desc": "Structure type FK"},
        "ALTERNATE_BOM_DESIGNATOR": {"type": "VARCHAR2(80)", "desc": "Alternate BOM name (NULL = primary)"},
        "EFFECTIVITY_CONTROL": {"type": "NUMBER", "desc": "Date/Model/Unit effectivity"},
    },
}

EGP_COMPONENTS_B = {
    "description": (
        "BOM components (child items within a bill of material). "
        "Each row = one component line on a BOM."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "key_columns": {
        "COMPONENT_SEQUENCE_ID": {"type": "NUMBER(18)", "desc": "Component unique identifier (PK)"},
        "BILL_SEQUENCE_ID": {"type": "NUMBER(18)", "desc": "Parent BOM FK -> EGP_STRUCTURES_B"},
        "PK1_VALUE": {"type": "VARCHAR2(240)", "desc": "Child item INVENTORY_ITEM_ID as string (replaces COMPONENT_ITEM_ID); TO_NUMBER(PK1_VALUE) to join EGP_SYSTEM_ITEMS_B"},
        "COMPONENT_QUANTITY": {"type": "NUMBER", "desc": "Required quantity per assembly"},
        "EFFECTIVITY_DATE": {"type": "DATE", "desc": "Component effective from date"},
        "DISABLE_DATE": {"type": "DATE", "desc": "Component effective to date"},
        "ITEM_NUM": {"type": "NUMBER", "desc": "Component sequence/sort order on BOM"},
        "WIP_SUPPLY_TYPE": {"type": "NUMBER", "desc": "Supply type (push, pull, operation pull, etc.)"},
        "SUPPLY_SUBINVENTORY": {"type": "VARCHAR2(10)", "desc": "Supply subinventory"},
        "SUPPLY_LOCATOR_ID": {"type": "NUMBER(18)", "desc": "Supply locator FK"},
        "OPTIONAL": {"type": "NUMBER", "desc": "1=Optional, 2=Required"},
    },
}


# ---- INVENTORY ORGANIZATION ----

INV_ORG_PARAMETERS_V = {
    "description": (
        "Inventory organization parameters view. "
        "Exposes configuration settings for inventory-enabled organizations. "
        "Filtered: INV_ORG_PARAMETERS WHERE INVENTORY_FLAG = 'Y'."
    ),
    "schema": "FUSION",
    "owner": "INV",
    "source": "INV_ORG_PARAMETERS WHERE INVENTORY_FLAG = 'Y'",
    "key_columns": {
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization unique identifier"},
        "ORGANIZATION_CODE": {"type": "VARCHAR2(18)", "desc": "Organization short code"},
        "MASTER_ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Master organization FK"},
        "BUSINESS_UNIT_ID": {"type": "NUMBER(18)", "desc": "Business unit FK"},
        "LEGAL_ENTITY_ID": {"type": "NUMBER(18)", "desc": "Legal entity FK"},
        "SERIAL_NUMBER_TYPE": {"type": "NUMBER", "desc": "Serial number type (AUTO/MANUAL)"},
        "SERIAL_NUMBER_GENERATION": {"type": "NUMBER", "desc": "Serial generation method"},
        "LOT_NUMBER_UNIQUENESS": {"type": "NUMBER", "desc": "Lot uniqueness scope"},
        "LOT_NUMBER_GENERATION": {"type": "NUMBER", "desc": "Lot generation method"},
        "NEGATIVE_INV_RECEIPT_CODE": {"type": "NUMBER", "desc": "Negative inventory receipt handling"},
        "STOCK_LOCATOR_CONTROL_CODE": {"type": "NUMBER", "desc": "Locator control level"},
        "WMS_ENABLED_FLAG": {"type": "VARCHAR2(1)", "desc": "WMS enabled"},
        "MFG_PLANT_FLAG": {"type": "VARCHAR2(1)", "desc": "Manufacturing plant"},
        "EAM_ENABLED_FLAG": {"type": "VARCHAR2(1)", "desc": "Enterprise Asset Mgmt enabled"},
        "SOURCE_ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Default source org"},
        "SOURCE_SUBINVENTORY": {"type": "VARCHAR2(10)", "desc": "Default source subinventory"},
        "SOURCE_TYPE": {"type": "NUMBER", "desc": "Source type (org/supplier)"},
        "FA_BOOK_TYPE_CODE": {"type": "VARCHAR2(30)", "desc": "Fixed assets book type"},
        "STARTING_REVISION": {"type": "VARCHAR2(3)", "desc": "Starting revision code"},
        "TIMEZONE_CODE": {"type": "VARCHAR2(50)", "desc": "Timezone code"},
        "SUPPLIER_ID": {"type": "NUMBER(18)", "desc": "Associated supplier FK"},
        "SUPPLIER_SITE_ID": {"type": "NUMBER(18)", "desc": "Supplier site FK"},
        "ATTRIBUTE_CATEGORY": {"type": "VARCHAR2(30)", "desc": "DFF structure"},
        "ATTRIBUTE1": {"type": "VARCHAR2(150)", "desc": "DFF segment 1 (through 15)"},
    },
}

INV_ORGANIZATION_DEFINITIONS_V = {
    "description": (
        "Inventory organization definitions view. "
        "Provides organization name, code, and classification details. "
        "Commonly used to get ORGANIZATION_NAME for display in reports."
    ),
    "schema": "FUSION",
    "owner": "INV",
    "key_columns": {
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization unique identifier"},
        "ORGANIZATION_CODE": {"type": "VARCHAR2(18)", "desc": "Organization short code"},
        "ORGANIZATION_NAME": {"type": "VARCHAR2(240)", "desc": "Organization display name"},
        "BUSINESS_GROUP_ID": {"type": "NUMBER(18)", "desc": "Business group FK"},
        "BUSINESS_UNIT_ID": {"type": "NUMBER(18)", "desc": "Business unit FK (Fusion replaced EBS OPERATING_UNIT with BUSINESS_UNIT_ID/BUSINESS_UNIT_NAME)"},
        "BUSINESS_UNIT_NAME": {"type": "VARCHAR2(240)", "desc": "Business unit name"},
        "LEGAL_ENTITY": {"type": "NUMBER(18)", "desc": "Legal entity FK"},
        "SET_OF_BOOKS_ID": {"type": "NUMBER(18)", "desc": "Ledger FK"},
    },
}


# ============================================================================
# SAMPLE BI PUBLISHER SQL QUERIES
# ============================================================================

SAMPLE_QUERIES = {
    "item_master_basic": """
-- Basic item master query with description
SELECT
    esi.ITEM_NUMBER,
    esi.DESCRIPTION,
    esi.ITEM_TYPE,
    esi.PRIMARY_UOM_CODE,
    esi.INVENTORY_ITEM_STATUS_CODE,
    esi.PLANNING_MAKE_BUY_CODE,
    esi.LIST_PRICE_PER_UNIT,
    iod.ORGANIZATION_CODE,
    iod.ORGANIZATION_NAME
FROM EGP_SYSTEM_ITEMS esi
JOIN INV_ORGANIZATION_DEFINITIONS_V iod
    ON esi.ORGANIZATION_ID = iod.ORGANIZATION_ID
WHERE esi.ENABLED_FLAG = 'Y'
ORDER BY esi.ITEM_NUMBER
""",

    "item_with_categories": """
-- Item with purchasing category
SELECT
    esi.ITEM_NUMBER,
    esi.DESCRIPTION,
    cvl.CATEGORY_NAME AS PURCHASING_CATEGORY,
    csvl.CATEGORY_SET_NAME AS CATALOG_NAME
FROM EGP_SYSTEM_ITEMS esi
JOIN EGP_ITEM_CAT_ASSIGNMENTS ica
    ON esi.INVENTORY_ITEM_ID = ica.INVENTORY_ITEM_ID
    AND esi.ORGANIZATION_ID = ica.ORGANIZATION_ID
JOIN EGP_CATEGORIES_VL cvl
    ON ica.CATEGORY_ID = cvl.CATEGORY_ID
JOIN EGP_CATEGORY_SETS_VL csvl
    ON ica.CATEGORY_SET_ID = csvl.CATEGORY_SET_ID
WHERE esi.ENABLED_FLAG = 'Y'
""",

    "item_with_eff_attributes": """
-- Item with extensible flexfield attributes
SELECT
    esi.ITEM_NUMBER,
    esi.DESCRIPTION,
    eff.CONTEXT_CODE AS ATTRIBUTE_GROUP,
    eff.ATTRIBUTE_CHAR1,
    eff.ATTRIBUTE_CHAR2,
    eff.ATTRIBUTE_NUMBER1,
    eff.ATTRIBUTE_DATE1
FROM EGP_SYSTEM_ITEMS esi
JOIN EGO_ITEM_EFF_B eff
    ON esi.INVENTORY_ITEM_ID = eff.INVENTORY_ITEM_ID
    AND esi.ORGANIZATION_ID = eff.ORGANIZATION_ID
WHERE eff.ACD_TYPE != 'HISTORY'
    AND (eff.VERSION_END_DATE IS NULL OR eff.VERSION_END_DATE > SYSDATE)
""",

    "item_revisions": """
-- Item revision history
SELECT
    esi.ITEM_NUMBER,
    rev.REVISION,
    rev.DESCRIPTION AS REVISION_DESCRIPTION,
    rev.EFFECTIVITY_DATE,
    rev.END_EFFECTIVITY_DATE,
    rev.IMPLEMENTATION_DATE
FROM EGP_SYSTEM_ITEMS esi
JOIN EGP_ITEM_REVISIONS_V rev
    ON esi.INVENTORY_ITEM_ID = rev.INVENTORY_ITEM_ID
    AND esi.ORGANIZATION_ID = rev.ORGANIZATION_ID
ORDER BY esi.ITEM_NUMBER, rev.EFFECTIVITY_DATE
""",

    "item_relationships": """
-- Item cross-references and related items
SELECT
    esi.ITEM_NUMBER AS SOURCE_ITEM,
    rel_item.ITEM_NUMBER AS RELATED_ITEM,
    rel.RELATIONSHIP_TYPE_ID,
    rel.START_DATE,
    rel.END_DATE
FROM EGP_SYSTEM_ITEMS_B esi
JOIN EGP_ITEM_RELATIONSHIPS_B rel
    ON esi.INVENTORY_ITEM_ID = rel.INVENTORY_ITEM_ID
    AND esi.ORGANIZATION_ID = rel.ORGANIZATION_ID
JOIN EGP_SYSTEM_ITEMS_B rel_item
    ON rel.RELATED_ITEM_ID = rel_item.INVENTORY_ITEM_ID
    AND rel.ORGANIZATION_ID = rel_item.ORGANIZATION_ID
""",
}


# ============================================================================
# ADDED 2026-06-01 — objects confirmed present in Oracle Fusion SCM 26B docs
# (previously only referenced in join keys; existence verified, PKs noted where
#  the per-table 26B/oedsc page could be read — see SCHEMA_AUDIT_ITEMS_26B_2026-06-01.md)
# ============================================================================

EGP_TRADING_PARTNER_ITEMS = {
    "description": (
        "Trading-partner item cross-references (customer / competitor / supplier / "
        "manufacturer item numbers) linked to internal items. Note: TRADING_PARTNER_ID / "
        "TP_TYPE / TP_ITEM_NUMBER ALSO exist directly on EGP_SYSTEM_ITEMS_B (index U3)."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    # Exact 26B PK not machine-readable (deep-link redirected); columns below are the reliable join keys.
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Internal item FK -> EGP_SYSTEM_ITEMS_B"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "TRADING_PARTNER_ID": {"type": "NUMBER(18)", "desc": "Trading partner FK"},
        "TP_TYPE": {"type": "VARCHAR2(30)", "desc": "CUSTOMER / MANUFACTURER / COMPETITOR / SUPPLIER"},
        "TP_ITEM_NUMBER": {"type": "VARCHAR2(300)", "desc": "Trading partner's item number"},
    },
}

EGP_SYSTEM_ITEMS_VL = {
    "description": (
        "Pre-joined item master VIEW (base EGP_SYSTEM_ITEMS_B + translation EGP_SYSTEM_ITEMS_TL "
        "+ EGP_ITEM_ORG_ASSOCIATIONS), filtered to the session language. "
        "Recommended target for BI Publisher item queries over the raw _B/_TL tables."
    ),
    "object_type": "VIEW",
    "schema": "FUSION",
    "owner": "EGP",
}

EGP_SYSTEM_ITEMS_INTERFACE = {
    "description": (
        "Item import staging/interface table (Item Import / Product Hub batch loads). "
        "Rows are processed into EGP_SYSTEM_ITEMS_B; not for transactional reporting."
    ),
    "schema": "FUSION",
    "owner": "EGP",
}

EGP_ITEM_TEXT_TL = {
    "description": (
        "Item long-text / keyword index translation table (Oracle Text). "
        "Join to item master on ITEM_ID + ORG_ID."
    ),
    "schema": "FUSION",
    "owner": "EGP",
    "primary_key": ["ITEM_ID", "ORG_ID", "LANGUAGE"],  # 26B-verified 2026-06-01
    "key_columns": {
        "ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK (= INVENTORY_ITEM_ID)"},
        "ORG_ID": {"type": "NUMBER(18)", "desc": "Organization FK (= ORGANIZATION_ID)"},
        "LANGUAGE": {"type": "VARCHAR2(4)", "desc": "Row language"},
    },
}

EGO_VERSIONS_B = {
    "description": (
        "Generic object-version store used for item version control "
        "(referenced by EGO_ITEM_ASSOCIATIONS.VERSION_ID and change management)."
    ),
    "schema": "FUSION",
    "owner": "EGO",
    "primary_key": ["VERSION_ID"],  # 26B-verified 2026-06-01
    "key_columns": {
        "VERSION_ID": {"type": "NUMBER(18)", "desc": "Version unique identifier (PK)"},
    },
}

EGP_ITEM_CATEGORIES = {
    "description": (
        "VIEW (not a table) joining item-category assignments with category-set and "
        "category detail (EGP_ITEM_CAT_ASSIGNMENTS + EGP_CATEGORY_SETS_B + "
        "EGP_ITEM_ORG_ASSOCIATIONS + INV_ORG_PARAMETERS). No primary key."
    ),
    "object_type": "VIEW",
    "schema": "FUSION",
    "owner": "EGP",
    # Logical uniqueness (not a declared PK):
    "key_columns": {
        "INVENTORY_ITEM_ID": {"type": "NUMBER(18)", "desc": "Item FK"},
        "ORGANIZATION_ID": {"type": "NUMBER(18)", "desc": "Organization FK"},
        "CATEGORY_SET_ID": {"type": "NUMBER(18)", "desc": "Category set / catalog FK"},
        "CATEGORY_ID": {"type": "NUMBER(18)", "desc": "Category FK"},
    },
}

EGP_CATG_MAP_HDRS_VL = {
    "description": (
        "Category-mapping header VIEW. Oracle publishes this as the _VL view; "
        "the underlying EGP_CATG_MAP_HDRS_B base table has no standalone documented page."
    ),
    "object_type": "VIEW",
    "schema": "FUSION",
    "owner": "EGP",
}


# ============================================================================
# ALL TABLES (for lookup by app.py) — includes tables with full "columns" defs
# ============================================================================
ALL_ITEM_TABLES = {
    "EGP_SYSTEM_ITEMS_B": EGP_SYSTEM_ITEMS_B,
    "EGP_SYSTEM_ITEMS_TL": EGP_SYSTEM_ITEMS_TL,
    "EGP_CATEGORIES_B": EGP_CATEGORIES_B,
    "EGP_CATEGORIES_TL": EGP_CATEGORIES_TL,
    "EGP_CATEGORY_SETS_B": EGP_CATEGORY_SETS_B,
    "EGP_ITEM_CAT_ASSIGNMENTS": EGP_ITEM_CAT_ASSIGNMENTS,
    "EGP_CATEGORY_SET_VALID_CATS": EGP_CATEGORY_SET_VALID_CATS,
    "EGP_DEFAULT_CATEGORY_SETS": EGP_DEFAULT_CATEGORY_SETS,
    "EGO_ITEM_EFF_B": EGO_ITEM_EFF_B,
    "EGP_ITEM_REVISIONS_B": EGP_ITEM_REVISIONS_B,
    "EGP_ITEM_REVISIONS_TL": EGP_ITEM_REVISIONS_TL,
    "EGP_ITEM_RELATIONSHIPS_B": EGP_ITEM_RELATIONSHIPS_B,
    "EGP_ITEM_CLASSES_B": EGP_ITEM_CLASSES_B,
    # Added 2026-06-01 — confirmed present in 26B
    "EGO_ITEM_ASSOCIATIONS": EGO_ITEM_ASSOCIATIONS,
    "EGP_TRADING_PARTNER_ITEMS": EGP_TRADING_PARTNER_ITEMS,
    "EGP_SYSTEM_ITEMS_VL": EGP_SYSTEM_ITEMS_VL,
    "EGP_SYSTEM_ITEMS_INTERFACE": EGP_SYSTEM_ITEMS_INTERFACE,
    "EGP_ITEM_TEXT_TL": EGP_ITEM_TEXT_TL,
    "EGO_VERSIONS_B": EGO_VERSIONS_B,
    "EGP_ITEM_CATEGORIES": EGP_ITEM_CATEGORIES,
    "EGP_CATG_MAP_HDRS_VL": EGP_CATG_MAP_HDRS_VL,
    "EGP_FULL_CATEGORY_LIST": EGP_FULL_CATEGORY_LIST,
}

# ============================================================================
# LOOKUP VALUES
# ============================================================================
ITEM_LOOKUP_VALUES = {
    "ITEM_TYPE (EGP_SYSTEM_ITEMS_B)": [
        "FINISHED GOOD - Finished goods",
        "PURCHASED - Purchased items",
        "RAW MATERIAL - Raw materials",
        "SUBASSEMBLY - Subassemblies",
        "SUPPLY ITEM - Supply items",
        "EXPENSE ITEM - Expense items",
    ],
    "BOM_ITEM_TYPE (EGP_SYSTEM_ITEMS_B)": [
        "1 - Model",
        "2 - Option Class",
        "4 - Standard",
        "5 - Planning",
    ],
    "PLANNING_MAKE_BUY_CODE (EGP_SYSTEM_ITEMS_B)": [
        "1 - Make",
        "2 - Buy",
    ],
    "LOT_CONTROL_CODE (EGP_SYSTEM_ITEMS_B)": [
        "1 - No lot control",
        "2 - Full lot control",
    ],
    "SERIAL_NUMBER_CONTROL_CODE (EGP_SYSTEM_ITEMS_B)": [
        "1 - No serial control",
        "2 - Predefined serial numbers",
        "5 - At receipt",
        "6 - At sales order issue",
    ],
    "ACD_TYPE (EGO_ITEM_EFF_B)": [
        "ADD - New record",
        "UPDATE - Changed record",
        "DELETE - Deleted record",
        "HISTORY - Historical version",
    ],
    "TP_TYPE (EGO_ITEM_ASSOCIATIONS)": [
        "CUSTOMER - Customer association",
        "MANUFACTURER - Manufacturer association",
        "SUPPLIER - Supplier association",
        "COMPETITOR - Competitor association",
    ],
}
