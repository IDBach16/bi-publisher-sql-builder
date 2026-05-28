"""
Oracle Fusion Cloud - BPM / SOA / AMX Workflow tables
Source: Oracle Fusion SOAINFRA + HWF schemas (human workflow).

These tables drive ACTIVE/PENDING approval routing. PO_ACTION_HISTORY only
records completed actions — to find the CURRENT next approver on a PO that
is sitting in DOCUMENT_STATUS = 'PENDING APPROVAL', you must join to
WFTASK + WFASSIGNEE (or the newer HWF_TASKS_B + HWF_TASK_ASSIGNMENTS_B).

ACCESS NOTE: These tables live in a separate Fusion schema (FUSION_SOAINFRA
or similar). The BI Publisher data source 'ApplicationDB_FSCM' may need
additional grants to read them. If a SELECT returns ORA-00942 (table or
view does not exist), file an SR to request SELECT privilege, or use the
seeded approval REST APIs instead.

IDENTIFICATIONKEY format (WFTASK / HWF_TASKS_B):
  For PO approval tasks this column carries the document identifier.
  Common formats seen in the wild:
    - "300000123456"                  (just the PO_HEADER_ID)
    - "204:300000123456"              (BU_ID:PO_HEADER_ID)
    - "ORA_PURCHASEORDER:300000..."   (entity:id)
  Strategy: TO_NUMBER(REGEXP_SUBSTR(IDENTIFICATIONKEY, '\\d+$'))
"""

WORKFLOW_RELATIONSHIPS = {
    "WFTASK -> WFASSIGNEE (current assignees)":
        "WFTASK.TASKID = WFASSIGNEE.TASKID",
    "WFTASK -> WFCOMMENTS":
        "WFTASK.TASKID = WFCOMMENTS.TASKID",
    "WFTASK -> WFATTACHMENT":
        "WFTASK.TASKID = WFATTACHMENT.TASKID",
    "WFTASK -> WFTASKHISTORY":
        "WFTASK.TASKID = WFTASKHISTORY.TASKID",
    "HWF_TASKS_B -> HWF_TASK_ASSIGNMENTS_B":
        "HWF_TASKS_B.TASK_ID = HWF_TASK_ASSIGNMENTS_B.TASK_ID",
    "HWF_TASKS_B -> HWF_TASK_HISTORY":
        "HWF_TASKS_B.TASK_ID = HWF_TASK_HISTORY.TASK_ID",
    "WFTASK <- PO_HEADERS_ALL (via IDENTIFICATIONKEY)":
        "PO_HEADERS_ALL.PO_HEADER_ID = TO_NUMBER(REGEXP_SUBSTR(WFTASK.IDENTIFICATIONKEY, '\\d+$'))",
    "WFASSIGNEE -> PER_PERSON_NAMES_F_V (resolve username to display name)":
        "WFASSIGNEE.ASSIGNEE = PER_USERS.USERNAME, PER_USERS.PERSON_ID = PER_PERSON_NAMES_F_V.PERSON_ID",
}


WFTASK = {
    "description": "BPM workflow task — one row per ACTIVE approval task. State='ASSIGNED' means pending an approver right now. This is THE table for 'who is it sitting with?' queries.",
    "primary_key": "TASKID",
    "key_columns": {
        "TASKID": {"type": "VARCHAR2(64)", "nullable": False, "desc": "BPM task unique identifier (string GUID)"},
        "TASKNUMBER": {"type": "NUMBER", "nullable": True, "desc": "Sequential human-readable task number"},
        "TITLE": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Task title (e.g., 'Approve Purchase Order 12345')"},
        "IDENTIFICATIONKEY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Document identifier. For PO tasks contains PO_HEADER_ID (sometimes prefixed). Use REGEXP_SUBSTR(IDENTIFICATIONKEY, '\\d+$') to extract."},
        "COMPONENTNAME": {"type": "VARCHAR2(200)", "nullable": True, "desc": "Workflow component. Common values: 'PurchaseOrderApprovalHumanTask', 'PurchaseAgreementApprovalHumanTask', 'RequisitionApprovalHumanTask', 'InvoiceApprovalHumanTask'"},
        "COMPOSITENAME": {"type": "VARCHAR2(200)", "nullable": True, "desc": "SOA composite name (e.g., 'PurchaseOrderApproval')"},
        "COMPOSITEVERSION": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Composite version"},
        "STATE": {"type": "VARCHAR2(40)", "nullable": False, "desc": "ASSIGNED, COMPLETED, EXPIRED, WITHDRAWN, ERRORED, INFO_REQUESTED, SUSPENDED, OUTCOME_UPDATED"},
        "OUTCOME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "APPROVE, REJECT, REQUEST_INFO, etc. (NULL while pending)"},
        "PRIORITY": {"type": "NUMBER", "nullable": True, "desc": "1=highest"},
        "OWNERUSER": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Username who owns the task overall"},
        "OWNERGROUP": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Group that owns the task"},
        "CREATOR": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Username who submitted the document (i.e., the requester/buyer)"},
        "CREATEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When the task was created"},
        "ASSIGNEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When the task was assigned to current approver — use for 'days pending' calc"},
        "UPDATEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "Last update timestamp"},
        "ENDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When the task completed (NULL while ASSIGNED)"},
        "EXPIRATIONDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When the task will auto-escalate/expire"},
        "ROOTTASKID": {"type": "VARCHAR2(64)", "nullable": True, "desc": "Root task in chained approvals (multi-stage routing)"},
        "PARENTTASKID": {"type": "VARCHAR2(64)", "nullable": True, "desc": "Parent task in nested approvals"},
        "TASKDEFINITIONNAME": {"type": "VARCHAR2(200)", "nullable": True, "desc": "Logical task definition name"},
        "WORKFLOWPATTERN": {"type": "VARCHAR2(40)", "nullable": True, "desc": "SINGLE_APPROVER, PARALLEL, SERIAL, MGMT_CHAIN"},
        "PRODUCTNAME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Source product (PRC, AP, OM, etc.)"},
        "PRODUCTTYPE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Product sub-type"},
        "CATEGORY": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Task category"},
        "TASKDISPLAYURL": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Deep link to task in BPM Worklist"},
    },
}


WFASSIGNEE = {
    "description": "Current assignees on an active BPM task. ONE WFTASK can have multiple WFASSIGNEE rows (parallel approvers, group assignment). This is where the actual NEXT APPROVER name comes from.",
    "primary_key": ["TASKID", "ASSIGNEE"],
    "key_columns": {
        "TASKID": {"type": "VARCHAR2(64)", "nullable": False, "desc": "FK to WFTASK.TASKID"},
        "ASSIGNEE": {"type": "VARCHAR2(256)", "nullable": False, "desc": "Username, group name, or role name of the assignee"},
        "ASSIGNEETYPE": {"type": "VARCHAR2(20)", "nullable": False, "desc": "'user', 'group', 'role' — filter to 'user' for individual approvers"},
        "DISPLAYNAME": {"type": "VARCHAR2(400)", "nullable": True, "desc": "Friendly name (already resolved). Use NVL(DISPLAYNAME, ASSIGNEE) for output."},
        "ROLENAME": {"type": "VARCHAR2(256)", "nullable": True, "desc": "If assigned via a role, the role name"},
        "ISGROUP": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - is this a group assignment"},
        "STATE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Assignee-level state (some installs use this for delegate/acquire tracking)"},
        "ACQUIREDBY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Username who 'acquired' a group task"},
        "ISADHOC": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - ad-hoc routing"},
    },
}


WFTASKHISTORY = {
    "description": "Historical/versioned snapshot of WFTASK rows. Multiple versions per TASKID as state changes. Useful for full approval timeline beyond PO_ACTION_HISTORY.",
    "primary_key": ["TASKID", "VERSION"],
    "key_columns": {
        "TASKID": {"type": "VARCHAR2(64)", "nullable": False, "desc": "FK to WFTASK.TASKID"},
        "VERSION": {"type": "NUMBER", "nullable": False, "desc": "Version number (incremented on every state change)"},
        "STATE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "State at this version"},
        "OUTCOME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Outcome chosen at this version"},
        "UPDATEDBY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Username who triggered this state change"},
        "UPDATEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When this version was written"},
        "ASSIGNEDUSERS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Comma-delimited list of users assigned at this version"},
        "ASSIGNEDGROUPS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Comma-delimited list of groups assigned at this version"},
        "COMMENTS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Action comments"},
    },
}


WFCOMMENTS = {
    "description": "Comments on a BPM task (approver notes beyond what's in PO_ACTION_HISTORY.NOTE).",
    "primary_key": "COMMENTID",
    "key_columns": {
        "COMMENTID": {"type": "NUMBER", "nullable": False, "desc": "Comment ID"},
        "TASKID": {"type": "VARCHAR2(64)", "nullable": False, "desc": "FK to WFTASK.TASKID"},
        "CREATEDBY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Username who added the comment"},
        "CREATEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When the comment was added"},
        "TASKCOMMENT": {"type": "CLOB", "nullable": True, "desc": "Comment body"},
        "UPDATEDBY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Last updated by"},
    },
}


WFATTACHMENT = {
    "description": "Attachments tied to a BPM task.",
    "primary_key": "ATTACHMENTID",
    "key_columns": {
        "ATTACHMENTID": {"type": "NUMBER", "nullable": False, "desc": "Attachment ID"},
        "TASKID": {"type": "VARCHAR2(64)", "nullable": False, "desc": "FK to WFTASK.TASKID"},
        "NAME": {"type": "VARCHAR2(400)", "nullable": True, "desc": "File name"},
        "MIMETYPE": {"type": "VARCHAR2(200)", "nullable": True, "desc": "MIME type"},
        "URI": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Attachment URI"},
        "CREATEDBY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Who attached it"},
        "CREATEDDATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When attached"},
    },
}


HWF_TASKS_B = {
    "description": "Hosted Workflow Foundation — newer Fusion tables for human workflow tasks. Equivalent to WFTASK in some pods. Try this if WFTASK is not accessible.",
    "primary_key": "TASK_ID",
    "key_columns": {
        "TASK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Task unique identifier"},
        "TASK_NUMBER": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Sequential human-readable task number"},
        "TITLE": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Task title"},
        "TASK_TYPE": {"type": "VARCHAR2(100)", "nullable": True, "desc": "Task type (PurchaseOrderApprovalHumanTask, etc.)"},
        "IDENTIFICATION_KEY": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Document key (same parsing rules as WFTASK.IDENTIFICATIONKEY)"},
        "STATE": {"type": "VARCHAR2(40)", "nullable": False, "desc": "ASSIGNED, COMPLETED, EXPIRED, WITHDRAWN, etc."},
        "OUTCOME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "APPROVE, REJECT, etc."},
        "PRIORITY": {"type": "NUMBER", "nullable": True, "desc": "1=highest"},
        "CREATOR_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to PER_USERS — task creator"},
        "OWNER_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to PER_USERS — task owner"},
        "OWNER_ROLE": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Owner role name"},
        "CREATION_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "When created"},
        "ASSIGNED_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When assigned to current approver"},
        "LAST_UPDATE_DATE": {"type": "TIMESTAMP", "nullable": False, "desc": "Last update timestamp"},
        "END_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When completed"},
        "EXPIRATION_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "Auto-expire date"},
        "ROOT_TASK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Root task in chained approvals"},
        "PARENT_TASK_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Parent task"},
        "PRODUCT_CODE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Source product code"},
        "APPLICATION_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Source application ID"},
    },
}


HWF_TASK_ASSIGNMENTS_B = {
    "description": "Assignments for HWF_TASKS_B — who the task is currently assigned to. The next-approver lookup table in HWF-based deployments.",
    "primary_key": ["TASK_ID", "ASSIGNEE_USER_ID"],
    "key_columns": {
        "TASK_ASSIGNMENT_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Assignment unique ID"},
        "TASK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "FK to HWF_TASKS_B.TASK_ID"},
        "ASSIGNEE_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to PER_USERS — assigned user"},
        "ASSIGNEE_USERNAME": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Assignee username (denormalized)"},
        "ASSIGNEE_TYPE": {"type": "VARCHAR2(20)", "nullable": False, "desc": "'USER', 'GROUP', 'ROLE'"},
        "ASSIGNEE_ROLE": {"type": "VARCHAR2(256)", "nullable": True, "desc": "Role name when assigned by role"},
        "ASSIGNMENT_STATE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "ACTIVE, ACQUIRED, RELEASED"},
        "ACQUIRED_BY_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "User who claimed a group task"},
        "DISPLAY_NAME": {"type": "VARCHAR2(400)", "nullable": True, "desc": "Friendly display name"},
    },
}


HWF_TASK_HISTORY = {
    "description": "Version history of HWF_TASKS_B rows — full timeline of state changes for an approval task.",
    "primary_key": ["TASK_ID", "VERSION"],
    "key_columns": {
        "TASK_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "FK to HWF_TASKS_B.TASK_ID"},
        "VERSION": {"type": "NUMBER", "nullable": False, "desc": "Version number"},
        "STATE": {"type": "VARCHAR2(40)", "nullable": True, "desc": "State at this version"},
        "OUTCOME": {"type": "VARCHAR2(40)", "nullable": True, "desc": "Outcome at this version"},
        "UPDATED_BY_USER_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "Who triggered this version"},
        "UPDATE_DATE": {"type": "TIMESTAMP", "nullable": True, "desc": "When this version was written"},
        "ASSIGNED_USERS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Assigned users at this version"},
        "ASSIGNED_GROUPS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Assigned groups at this version"},
        "COMMENTS": {"type": "VARCHAR2(2000)", "nullable": True, "desc": "Action comments"},
    },
}


PER_USERS = {
    "description": "HR/Security users — bridge from BPM usernames (WFASSIGNEE.ASSIGNEE) to PERSON_ID for joining to PER_PERSON_NAMES_F_V.",
    "primary_key": "USER_ID",
    "key_columns": {
        "USER_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "User unique identifier"},
        "USERNAME": {"type": "VARCHAR2(256)", "nullable": False, "desc": "Login username — joins to WFASSIGNEE.ASSIGNEE"},
        "PERSON_ID": {"type": "NUMBER(18)", "nullable": True, "desc": "FK to PER_ALL_PEOPLE_F / PER_PERSON_NAMES_F_V for display name"},
        "ACTIVE_FLAG": {"type": "VARCHAR2(1)", "nullable": True, "desc": "Y/N - user is active"},
        "START_DATE": {"type": "DATE", "nullable": True, "desc": "User effective start"},
        "END_DATE": {"type": "DATE", "nullable": True, "desc": "User effective end (NULL = active)"},
        "EMAIL_ADDRESS": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Email"},
    },
}


PER_PERSON_NAMES_F_V = {
    "description": "Date-effective view of person display names. Always filter with TRUNC(SYSDATE) BETWEEN EFFECTIVE_START_DATE AND EFFECTIVE_END_DATE.",
    "primary_key": ["PERSON_ID", "EFFECTIVE_START_DATE"],
    "key_columns": {
        "PERSON_ID": {"type": "NUMBER(18)", "nullable": False, "desc": "Person ID — joins to PER_USERS.PERSON_ID or PO_ACTION_HISTORY.PERFORMER_ID"},
        "DISPLAY_NAME": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Formatted display name (Last, First)"},
        "FIRST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "First name"},
        "LAST_NAME": {"type": "VARCHAR2(150)", "nullable": True, "desc": "Last name"},
        "FULL_NAME": {"type": "VARCHAR2(240)", "nullable": True, "desc": "Full name"},
        "EFFECTIVE_START_DATE": {"type": "DATE", "nullable": False, "desc": "Row effective start"},
        "EFFECTIVE_END_DATE": {"type": "DATE", "nullable": False, "desc": "Row effective end (4712-12-31 = unbounded)"},
        "NAME_TYPE": {"type": "VARCHAR2(30)", "nullable": True, "desc": "GLOBAL is the standard one to use"},
    },
}


ALL_WORKFLOW_TABLES = {
    "WFTASK": WFTASK,
    "WFASSIGNEE": WFASSIGNEE,
    "WFTASKHISTORY": WFTASKHISTORY,
    "WFCOMMENTS": WFCOMMENTS,
    "WFATTACHMENT": WFATTACHMENT,
    "HWF_TASKS_B": HWF_TASKS_B,
    "HWF_TASK_ASSIGNMENTS_B": HWF_TASK_ASSIGNMENTS_B,
    "HWF_TASK_HISTORY": HWF_TASK_HISTORY,
    "PER_USERS": PER_USERS,
    "PER_PERSON_NAMES_F_V": PER_PERSON_NAMES_F_V,
}


WORKFLOW_LOOKUP_VALUES = {
    "STATE (WFTASK / HWF_TASKS_B)": [
        "ASSIGNED - Task is pending action by current assignee(s)",
        "COMPLETED - Task done (approved or rejected)",
        "EXPIRED - Auto-expired past EXPIRATIONDATE",
        "WITHDRAWN - Withdrawn by submitter",
        "ERRORED - Workflow errored out",
        "INFO_REQUESTED - Approver requested more info",
        "SUSPENDED - Suspended by admin",
        "OUTCOME_UPDATED - Outcome set but next step pending",
    ],
    "OUTCOME (WFTASK / HWF_TASKS_B)": [
        "APPROVE",
        "REJECT",
        "REQUEST_INFO",
        "FORWARD",
        "DELEGATE",
        "REASSIGN",
        "WITHDRAW",
    ],
    "COMPONENTNAME (WFTASK) — Procurement-relevant": [
        "PurchaseOrderApprovalHumanTask - PO approval",
        "PurchaseAgreementApprovalHumanTask - BPA / Contract PA approval",
        "PurchaseOrderChangeOrderApprovalHumanTask - Change order approval",
        "RequisitionApprovalHumanTask - Requisition approval",
        "NegotiationApprovalHumanTask - Sourcing negotiation approval",
        "InvoiceApprovalHumanTask - AP invoice approval",
        "SupplierRegistrationApprovalHumanTask - New supplier registration",
    ],
    "ASSIGNEETYPE (WFASSIGNEE)": [
        "user - Named individual approver",
        "group - Approval group (may be acquired by a member)",
        "role - Role-based assignment",
    ],
    "WORKFLOWPATTERN (WFTASK)": [
        "SINGLE_APPROVER - One person must approve",
        "PARALLEL - Multiple approvers, all required",
        "SERIAL - Multiple approvers, one at a time",
        "MGMT_CHAIN - Up the supervisor chain until limit met",
        "FYI - Notification only, no action required",
    ],
}


# ---------------------------------------------------------------------------
# Reference SQL fragments — drop into BI Publisher reports for next-approver
# ---------------------------------------------------------------------------
WORKFLOW_SQL_PATTERNS = {
    "PendingApprovers_via_WFTASK": """
-- CTE to pull the CURRENT next approver(s) for every PO in PENDING APPROVAL.
-- Use this to replace 'Pending Assignment' placeholder in your Pending Approval report.
PendingApprovers AS (
    SELECT
        TO_NUMBER(REGEXP_SUBSTR(T.IDENTIFICATIONKEY, '\\d+$'))      AS PO_HEADER_ID,
        LISTAGG(NVL(A.DISPLAYNAME, A.ASSIGNEE), ', ')
            WITHIN GROUP (ORDER BY A.DISPLAYNAME)                  AS NEXT_APPROVER,
        MIN(T.ASSIGNEDDATE)                                         AS PENDING_SINCE,
        MIN(T.EXPIRATIONDATE)                                       AS APPROVAL_EXPIRES,
        MIN(T.TASKID)                                               AS TASK_ID
    FROM WFTASK T
    JOIN WFASSIGNEE A
        ON T.TASKID = A.TASKID
       AND A.ASSIGNEETYPE IN ('user', 'group')
    WHERE T.STATE IN ('ASSIGNED', 'INFO_REQUESTED')
      AND T.COMPONENTNAME IN (
          'PurchaseOrderApprovalHumanTask',
          'PurchaseAgreementApprovalHumanTask',
          'PurchaseOrderChangeOrderApprovalHumanTask'
      )
      AND REGEXP_LIKE(T.IDENTIFICATIONKEY, '\\d+$')
    GROUP BY T.IDENTIFICATIONKEY
)
""".strip(),

    "PendingApprovers_via_HWF_TASKS_B": """
-- Alternative using the newer HWF tables. Try this if WFTASK is not accessible.
PendingApprovers AS (
    SELECT
        TO_NUMBER(REGEXP_SUBSTR(T.IDENTIFICATION_KEY, '\\d+$'))   AS PO_HEADER_ID,
        LISTAGG(NVL(A.DISPLAY_NAME, A.ASSIGNEE_USERNAME), ', ')
            WITHIN GROUP (ORDER BY A.DISPLAY_NAME)                AS NEXT_APPROVER,
        MIN(T.ASSIGNED_DATE)                                       AS PENDING_SINCE,
        MIN(T.EXPIRATION_DATE)                                     AS APPROVAL_EXPIRES
    FROM HWF_TASKS_B T
    JOIN HWF_TASK_ASSIGNMENTS_B A
        ON T.TASK_ID = A.TASK_ID
       AND A.ASSIGNMENT_STATE = 'ACTIVE'
       AND A.ASSIGNEE_TYPE IN ('USER', 'GROUP')
    WHERE T.STATE IN ('ASSIGNED', 'INFO_REQUESTED')
      AND T.TASK_TYPE IN (
          'PurchaseOrderApprovalHumanTask',
          'PurchaseAgreementApprovalHumanTask'
      )
      AND REGEXP_LIKE(T.IDENTIFICATION_KEY, '\\d+$')
    GROUP BY T.IDENTIFICATION_KEY
)
""".strip(),
}
