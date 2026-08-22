# ============================================================
# SYSTEM STATUS DEFINITIONS
# ============================================================

JOB_STATUSES = {
    "pending_review",
    "agent_review",
    "admin_review",
    "approved",
    "rejected",
    "open",
    "in_progress",
    "completed",
    "cancelled",
    "deleted",
}


APPLICATION_STATUSES = {
    "pending",
    "customer_approved",
    "customer_rejected",
    "agent_review",
    "admin_review",
    "approved",
    "rejected",
    "hired",
    "cancelled",
    "deleted",
}


# ============================================================
# VALID JOB TRANSITIONS
# ============================================================

JOB_TRANSITIONS = {

    "pending_review": {
        "agent_review",
        "admin_review",
        "rejected",
    },

    "agent_review": {
        "admin_review",
        "rejected",
    },

    "admin_review": {
        "approved",
        "rejected",
    },

    "approved": {
        "open",
        "cancelled",
    },

    "open": {
        "in_progress",
        "cancelled",
    },

    "in_progress": {
        "completed",
        "cancelled",
    },

    "completed": set(),

    "rejected": set(),

    "cancelled": set(),

    "deleted": set(),
}


# ============================================================
# VALID APPLICATION TRANSITIONS
# ============================================================

APPLICATION_TRANSITIONS = {

    "pending": {
        "customer_approved",
        "customer_rejected",
        "cancelled",
    },

    "customer_approved": {
        "agent_review",
        "admin_review",
        "customer_rejected",
    },

    "agent_review": {
        "admin_review",
        "rejected",
    },

    "admin_review": {
        "approved",
        "rejected",
    },

    "approved": {
        "hired",
        "cancelled",
    },

    "hired": set(),

    "customer_rejected": set(),

    "rejected": set(),

    "cancelled": set(),

    "deleted": set(),
}


def can_transition(
    transition_map,
    current_status,
    new_status
):
    """
    Central status-transition validation.
    """

    if current_status == new_status:
        return True

    allowed = transition_map.get(
        current_status,
        set()
    )

    return new_status in allowed
