-- ============================================================
-- PO Pending Approval Report — "Who is the Next Approver?"  (V3)
-- BI Publisher / Oracle Fusion Cloud
--
-- PARAMETERS:
--   :P_PO_NUMBER  VARCHAR2 — specific PO number          (NULL/'' = all)
--   :P_BU_ID      NUMBER   — Procurement BU id            (NULL/'' = all)
--   :P_DAYS_MIN   NUMBER   — only POs pending >= N days   (NULL/'' = all)
--
-- FIXES IN THIS VERSION:
--   * ORA-00904 "PHA"."PO_HEADER_": invalid identifier — was a truncated
--     column reference in the FirstRequester join; corrected to
--     PHA.PO_HEADER_ID (the PK of PO_HEADERS_ALL).
--   * Completed every join the SELECT references that was missing from the
--     cut-off draft: requester + manager, buyer + manager, GL combination,
--     PO line totals, and supplier/party.
--   * No PHA.BLANKET_TOTAL_AMOUNT — that column is EBS-only and does NOT
--     exist on PO_HEADERS_ALL in Fusion Cloud. PO total is summed from
--     PO_LINES_ALL instead.
--
-- VERIFY ON YOUR POD (these are the usual ORA-00904/00942 suspects):
--   * PO_ACTION_HISTORY.PERFORMER_ID — present on most pods; if it 00904s,
--     it is EMPLOYEE_ID on some versions.
--   * PER_ASSIGNMENT_SUPERVISORS_F — correct Fusion manager-hierarchy table;
--     if ORA-00942, swap PersonManager to PER_ALL_ASSIGNMENTS_M.
--   * PO_DISTRIBUTIONS_ALL.CODE_COMBINATION_ID — present in Fusion; only
--     needed for the GL_ACCOUNT / COST_CENTER columns.
-- ============================================================

WITH
-- Last SUBMIT/FORWARD per PO: when it entered its current pending state, and who submitted it.
LastSubmitOrForward AS (
    SELECT
        AH.OBJECT_ID,
        AH.PERFORMER_ID,
        AH.ACTION_DATE,
        AH.ACTION_CODE,
        ROW_NUMBER() OVER (PARTITION BY AH.OBJECT_ID ORDER BY AH.SEQUENCE_NUM DESC) AS RN
    FROM PO_ACTION_HISTORY AH
    WHERE AH.OBJECT_TYPE_CODE IN ('PO', 'PA')
      AND AH.ACTION_CODE      IN ('SUBMIT', 'FORWARD')
),

-- Last actionable row per PO: drives the "current approver" proxy from history.
LastApprovalAction AS (
    SELECT
        AH.OBJECT_ID,
        AH.PERFORMER_ID AS LAST_ACTOR_PERSON_ID,
        AH.ACTION_CODE  AS LAST_ACTION_CODE,
        ROW_NUMBER() OVER (PARTITION BY AH.OBJECT_ID ORDER BY AH.SEQUENCE_NUM DESC) AS RN
    FROM PO_ACTION_HISTORY AH
    WHERE AH.OBJECT_TYPE_CODE IN ('PO', 'PA')
      AND AH.ACTION_CODE      IN ('APPROVE', 'REJECT', 'FORWARD', 'SUBMIT')
),

-- First distribution per PO: requester + GL code-combination from the lowest DISTRIBUTION_NUM.
FirstRequester AS (
    SELECT
        PDA.PO_HEADER_ID,
        MIN(PDA.DELIVER_TO_PERSON_ID)
            KEEP (DENSE_RANK FIRST ORDER BY PDA.DISTRIBUTION_NUM) AS REQUESTER_PERSON_ID,
        MIN(PDA.CODE_COMBINATION_ID)
            KEEP (DENSE_RANK FIRST ORDER BY PDA.DISTRIBUTION_NUM) AS CCID
    FROM PO_DISTRIBUTIONS_ALL PDA
    WHERE PDA.DELIVER_TO_PERSON_ID IS NOT NULL
    GROUP BY PDA.PO_HEADER_ID
),

-- One-level manager links (person -> line manager), effective-dated.
PersonManager AS (
    SELECT
        PAS.PERSON_ID,
        PAS.MANAGER_ID AS MANAGER_PERSON_ID
    FROM PER_ASSIGNMENT_SUPERVISORS_F PAS
    WHERE PAS.MANAGER_TYPE = 'LINE_MANAGER'
      AND TRUNC(SYSDATE) BETWEEN PAS.EFFECTIVE_START_DATE AND PAS.EFFECTIVE_END_DATE
),

-- PO total from non-cancelled lines (replaces the non-existent header total column).
POLineTotals AS (
    SELECT
        PLA.PO_HEADER_ID,
        SUM(NVL(PLA.AMOUNT, NVL(PLA.QUANTITY, 0) * NVL(PLA.UNIT_PRICE, 0))) AS TOTAL_AMOUNT
    FROM PO_LINES_ALL PLA
    WHERE NVL(PLA.CANCEL_FLAG, 'N') = 'N'
    GROUP BY PLA.PO_HEADER_ID
)

SELECT
    -- Document
    PHA.SEGMENT1                                AS PO_NUMBER,
    PHA.TYPE_LOOKUP_CODE                        AS PO_TYPE,
    PHA.DOCUMENT_STATUS                         AS STATUS,

    -- Timing
    LSF.ACTION_CODE                             AS LAST_WORKFLOW_ACTION,
    TRUNC(LSF.ACTION_DATE)                      AS PENDING_SINCE,
    TRUNC(SYSDATE) - TRUNC(LSF.ACTION_DATE)     AS DAYS_PENDING,

    -- Current / next approver (derived from PO_ACTION_HISTORY)
    CASE
        WHEN LAA.LAST_ACTION_CODE IN ('APPROVE', 'REJECT')
            THEN 'LAST ACTOR (already approved/rejected this level)'
        WHEN LAA.LAST_ACTION_CODE = 'FORWARD'
            THEN 'FORWARDED TO — see SUBMITTER column'
        ELSE 'PENDING — next approver not yet in history'
    END                                         AS APPROVER_STATUS_NOTE,
    NVL(
        CASE WHEN LAA.LAST_ACTION_CODE = 'FORWARD' THEN LastActorN.DISPLAY_NAME END,
        SubMgrN.DISPLAY_NAME            -- submitter's manager = most likely next approver
    )                                           AS MOST_LIKELY_NEXT_APPROVER,

    -- People
    SubmitterN.DISPLAY_NAME                     AS SUBMITTER,
    SubMgrN.DISPLAY_NAME                        AS CAND1_SUBMITTER_MANAGER,
    SubMgr2N.DISPLAY_NAME                       AS CAND2_SUBMITTER_SKIP_LEVEL,
    ReqN.DISPLAY_NAME                           AS REQUESTER,
    ReqMgrN.DISPLAY_NAME                        AS CAND3_REQUESTER_MANAGER,
    BuyerN.DISPLAY_NAME                         AS BUYER,
    BuyerMgrN.DISPLAY_NAME                      AS CAND4_BUYER_MANAGER,

    -- GL account (manual segment concat — GL_CODE_COMBINATIONS_KFV does not exist in Fusion)
    GCC.SEGMENT1 || '.' || GCC.SEGMENT2 || '.' || GCC.SEGMENT3 || '.' ||
    GCC.SEGMENT4 || '.' || NVL(GCC.SEGMENT5, '')                  AS GL_ACCOUNT,
    GCC.SEGMENT2                                AS COST_CENTER,   -- adjust segment# to your COA

    -- Amount / context
    PLT.TOTAL_AMOUNT                            AS PO_TOTAL_AMOUNT,
    PHA.CURRENCY_CODE                           AS CURRENCY,
    PHA.PRC_BU_ID                               AS PROC_BU_ID,
    HP.PARTY_NAME                               AS SUPPLIER_NAME,
    PS.SEGMENT1                                 AS SUPPLIER_NUMBER

FROM PO_HEADERS_ALL PHA

-- Supplier (name lives on HZ_PARTIES, never POZ_SUPPLIERS.VENDOR_NAME)
LEFT JOIN POZ_SUPPLIERS PS ON PS.VENDOR_ID = PHA.VENDOR_ID
LEFT JOIN HZ_PARTIES    HP ON HP.PARTY_ID   = PS.PARTY_ID

-- Workflow history rows
LEFT JOIN LastSubmitOrForward LSF ON LSF.OBJECT_ID = PHA.PO_HEADER_ID AND LSF.RN = 1
LEFT JOIN LastApprovalAction  LAA ON LAA.OBJECT_ID = PHA.PO_HEADER_ID AND LAA.RN = 1

-- Last actor name (used when last action was FORWARD)
LEFT JOIN PER_PERSON_NAMES_F_V LastActorN
    ON  LastActorN.PERSON_ID = LAA.LAST_ACTOR_PERSON_ID
    AND LastActorN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN LastActorN.EFFECTIVE_START_DATE AND LastActorN.EFFECTIVE_END_DATE

-- Submitter + manager + skip-level manager
LEFT JOIN PER_PERSON_NAMES_F_V SubmitterN
    ON  SubmitterN.PERSON_ID = LSF.PERFORMER_ID
    AND SubmitterN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN SubmitterN.EFFECTIVE_START_DATE AND SubmitterN.EFFECTIVE_END_DATE
LEFT JOIN PersonManager SubMgr ON SubMgr.PERSON_ID = LSF.PERFORMER_ID
LEFT JOIN PER_PERSON_NAMES_F_V SubMgrN
    ON  SubMgrN.PERSON_ID = SubMgr.MANAGER_PERSON_ID
    AND SubMgrN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN SubMgrN.EFFECTIVE_START_DATE AND SubMgrN.EFFECTIVE_END_DATE
LEFT JOIN PersonManager SubMgr2 ON SubMgr2.PERSON_ID = SubMgr.MANAGER_PERSON_ID
LEFT JOIN PER_PERSON_NAMES_F_V SubMgr2N
    ON  SubMgr2N.PERSON_ID = SubMgr2.MANAGER_PERSON_ID
    AND SubMgr2N.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN SubMgr2N.EFFECTIVE_START_DATE AND SubMgr2N.EFFECTIVE_END_DATE

-- Requester (from first distribution) + manager
LEFT JOIN FirstRequester FR ON FR.PO_HEADER_ID = PHA.PO_HEADER_ID
LEFT JOIN PER_PERSON_NAMES_F_V ReqN
    ON  ReqN.PERSON_ID = FR.REQUESTER_PERSON_ID
    AND ReqN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN ReqN.EFFECTIVE_START_DATE AND ReqN.EFFECTIVE_END_DATE
LEFT JOIN PersonManager ReqMgr ON ReqMgr.PERSON_ID = FR.REQUESTER_PERSON_ID
LEFT JOIN PER_PERSON_NAMES_F_V ReqMgrN
    ON  ReqMgrN.PERSON_ID = ReqMgr.MANAGER_PERSON_ID
    AND ReqMgrN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN ReqMgrN.EFFECTIVE_START_DATE AND ReqMgrN.EFFECTIVE_END_DATE

-- Buyer (AGENT_ID) + manager
LEFT JOIN PER_PERSON_NAMES_F_V BuyerN
    ON  BuyerN.PERSON_ID = PHA.AGENT_ID
    AND BuyerN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN BuyerN.EFFECTIVE_START_DATE AND BuyerN.EFFECTIVE_END_DATE
LEFT JOIN PersonManager BuyerMgr ON BuyerMgr.PERSON_ID = PHA.AGENT_ID
LEFT JOIN PER_PERSON_NAMES_F_V BuyerMgrN
    ON  BuyerMgrN.PERSON_ID = BuyerMgr.MANAGER_PERSON_ID
    AND BuyerMgrN.NAME_TYPE = 'GLOBAL'
    AND TRUNC(SYSDATE) BETWEEN BuyerMgrN.EFFECTIVE_START_DATE AND BuyerMgrN.EFFECTIVE_END_DATE

-- GL combination + PO total
LEFT JOIN GL_CODE_COMBINATIONS GCC ON GCC.CODE_COMBINATION_ID = FR.CCID
LEFT JOIN POLineTotals         PLT ON PLT.PO_HEADER_ID        = PHA.PO_HEADER_ID

WHERE 1 = 1
    AND PHA.SEGMENT1 IS NOT NULL                 -- exclude incomplete drafts
    AND NVL(PHA.CANCEL_FLAG, 'N') = 'N'
    AND PHA.DOCUMENT_STATUS = 'PENDING APPROVAL'
    AND (:P_PO_NUMBER IS NULL OR :P_PO_NUMBER = '' OR PHA.SEGMENT1  = :P_PO_NUMBER)
    AND (:P_BU_ID     IS NULL OR :P_BU_ID     = '' OR PHA.PRC_BU_ID = TO_NUMBER(:P_BU_ID))
    AND (:P_DAYS_MIN  IS NULL OR :P_DAYS_MIN  = '' OR
         (LSF.ACTION_DATE IS NOT NULL
          AND TRUNC(SYSDATE) - TRUNC(LSF.ACTION_DATE) >= TO_NUMBER(:P_DAYS_MIN)))

ORDER BY
    CASE WHEN LSF.ACTION_DATE IS NOT NULL
         THEN TRUNC(SYSDATE) - TRUNC(LSF.ACTION_DATE)
         ELSE 9999
    END DESC,
    PLT.TOTAL_AMOUNT DESC
