/* =========================================================
   S. F WORKS
   PREMIUM ADMIN DASHBOARD
========================================================= */

"use strict";


/* =========================================================
   CONFIG
========================================================= */

const ADMIN_API = "/api/admin";


const state = {

    currentSection:
        "dashboard",

    usersPage:
        1,

    jobsPage:
        1,

    auditPage:
        1,

    users:
        [],

    agents:
        [],

    categories:
        [],

    jobs:
        [],

    applications:
        [],

    admin:
        null
};


/* =========================================================
   DOM
========================================================= */

const $ = (
    selector
) => document.querySelector(
    selector
);


const $$ = (
    selector
) => document.querySelectorAll(
    selector
);


/* =========================================================
   API
========================================================= */

async function apiFetch(
    url,
    options = {}
) {

    const response = await fetch(
        url,
        {
            credentials:
                "include",

            headers: {
                "Content-Type":
                    "application/json",

                ...(options.headers || {})
            },

            ...options
        }
    );


    let data = null;

    try {

        data =
            await response.json();

    } catch {

        data = null;

    }


    if (
        response.status === 401
        ||
        response.status === 403
    ) {

        if (
            !url.endsWith(
                "/me"
            )
        ) {

            window.location.href =
                "/admin/login";

        }

    }


    if (!response.ok) {

        throw new Error(
            data?.message
            ||
            "Something went wrong."
        );

    }


    return data;
}


/* =========================================================
   TOAST
========================================================= */

function showToast(
    message,
    type = "success"
) {

    const container =
        $(
            "#toastContainer"
        );


    const toast =
        document.createElement(
            "div"
        );


    toast.className =
        `sf-toast ${type}`;


    toast.textContent =
        message;


    container.appendChild(
        toast
    );


    setTimeout(
        () => {

            toast.remove();

        },
        3500
    );
}


/* =========================================================
   HELPERS
========================================================= */

function escapeHtml(
    value
) {

    if (
        value === null
        ||
        value === undefined
    ) {

        return "";

    }


    return String(
        value
    )
    .replace(
        /&/g,
        "&amp;"
    )
    .replace(
        /</g,
        "&lt;"
    )
    .replace(
        />/g,
        "&gt;"
    )
    .replace(
        /"/g,
        "&quot;"
    )
    .replace(
        /'/g,
        "&#039;"
    );
}


function initials(
    name
) {

    if (!name) {

        return "U";

    }


    return name
        .split(
            " "
        )
        .filter(Boolean)
        .slice(
            0,
            2
        )
        .map(
            word =>
                word[0]
        )
        .join("")
        .toUpperCase();
}


function formatDate(
    value
) {

    if (!value) {

        return "—";

    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "—";

    }


    return date.toLocaleString(
        "en-IN",
        {
            day:
                "2-digit",

            month:
                "short",

            year:
                "numeric",

            hour:
                "2-digit",

            minute:
                "2-digit"
        }
    );
}


function statusBadge(
    status
) {

    const value =
        String(
            status || "unknown"
        )
        .toLowerCase();


    let label =
        value
            .replace(
                /_/g,
                " "
            );


    label =
        label.replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );


    let className =
        "pending";


    if (
        [
            "active",
            "approved",
            "hired",
            "true"
        ].includes(
            value
        )
    ) {

        className =
            "approved";

    }


    if (
        [
            "inactive",
            "rejected",
            "deleted",
            "false"
        ].includes(
            value
        )
    ) {

        className =
            "rejected";

    }


    return `
        <span class="sf-status ${className}">
            ${escapeHtml(label)}
        </span>
    `;
}


function roleBadge(
    role
) {

    return `
        <span class="sf-status ${escapeHtml(role || "")}">
            ${escapeHtml(
                role || "unknown"
            )}
        </span>
    `;
}


/* =========================================================
   ADMIN ME
========================================================= */

async function loadAdmin() {

    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/me`
            );


        state.admin =
            data.user;


        const name =
            data.user?.full_name
            ||
            "Administrator";


        if (
            $("#adminName")
        ) {

            $("#adminName")
                .textContent =
                name;

        }


        if (
            $("#heroAdminName")
        ) {

            $("#heroAdminName")
                .textContent =
                name.split(
                    " "
                )[0];

        }


        if (
            $(".sf-avatar")
        ) {

            $(".sf-avatar")
                .textContent =
                initials(
                    name
                );

        }

    } catch (error) {

        console.error(
            error
        );

    }
}


/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/dashboard`
            );


        const stats =
            data.stats || {};


        const mapping = {

            statTotalUsers:
                "total_users",

            statWorkers:
                "total_workers",

            statAgents:
                "total_agents",

            statJobs:
                "total_jobs",

            statPendingJobs:
                "pending_jobs",

            statApplications:
                "total_applications",

            statPendingWorkers:
                "pending_workers",

            statActiveUsers:
                "active_users"

        };


        Object.entries(
            mapping
        ).forEach(
            ([id, key]) => {

                const element =
                    $(
                        `#${id}`
                    );


                if (element) {

                    element.textContent =
                        Number(
                            stats[key] || 0
                        ).toLocaleString(
                            "en-IN"
                        );

                }

            }
        );


        $("#attentionWorkers")
            .textContent =
            stats.pending_workers
            || 0;


        $("#attentionJobs")
            .textContent =
            stats.pending_jobs
            || 0;


        $("#attentionApplications")
            .textContent =
            stats.pending_applications
            || 0;


        updateChart(
            stats
        );

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   CHART
========================================================= */

function updateChart(
    stats
) {

    const values = [

        stats.total_jobs || 0,

        stats.total_applications || 0,

        stats.total_users || 0,

        stats.total_workers || 0,

        stats.total_agents || 0

    ];


    const max =
        Math.max(
            ...values,
            1
        );


    $$(".sf-bar")
        .forEach(
            (
                bar,
                index
            ) => {

                const value =
                    values[index]
                    || 0;


                const percentage =
                    Math.max(
                        8,
                        (
                            value / max
                        ) * 100
                    );


                bar.style
                    .setProperty(
                        "--value",
                        `${percentage}%`
                    );

            }
        );
}


/* =========================================================
   USERS
========================================================= */

async function loadUsers(
    page = 1
) {

    const body =
        $("#usersTableBody");


    body.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="sf-loading">
                    Loading users...
                </div>
            </td>
        </tr>
    `;


    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/users?page=${page}&per_page=25`
            );


        state.users =
            data.users || [];


        state.usersPage =
            page;


        renderUsers();


        renderPagination(
            "usersPagination",
            data.pagination,
            loadUsers
        );

    } catch (error) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                </td>
            </tr>
        `;

    }
}


function renderUsers() {

    const body =
        $("#usersTableBody");


    const search =
        (
            $("#userSearch")
                ?.value
            || ""
        )
        .toLowerCase();


    const role =
        $(
            "#userRoleFilter"
        )?.value
        || "";


    const filtered =
        state.users.filter(
            user => {

                const matchesSearch =
                    !search
                    ||
                    String(
                        user.full_name
                        || ""
                    )
                    .toLowerCase()
                    .includes(
                        search
                    )
                    ||
                    String(
                        user.email
                        || ""
                    )
                    .toLowerCase()
                    .includes(
                        search
                    )
                    ||
                    String(
                        user.phone
                        || ""
                    )
                    .includes(
                        search
                    );


                const matchesRole =
                    !role
                    ||
                    user.role === role;


                return (
                    matchesSearch
                    &&
                    matchesRole
                );

            }
        );


    if (!filtered.length) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        No users found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML =
        filtered
        .map(
            user => `

            <tr>

                <td>

                    <div class="sf-user-cell">

                        <div class="sf-mini-avatar">
                            ${initials(
                                user.full_name
                            )}
                        </div>

                        <div>

                            <strong>
                                ${escapeHtml(
                                    user.full_name
                                )}
                            </strong>

                            <span>
                                ID #${user.id}
                            </span>

                        </div>

                    </div>

                </td>


                <td>

                    <div>
                        ${escapeHtml(
                            user.email || "—"
                        )}
                    </div>

                    <div style="color:#909aaa;margin-top:3px;">
                        ${escapeHtml(
                            user.phone || "—"
                        )}
                    </div>

                </td>


                <td>
                    ${roleBadge(
                        user.role
                    )}
                </td>


                <td>
                    ${
                        user.is_verified
                        ? statusBadge(
                            "approved"
                        )
                        : statusBadge(
                            "pending"
                        )
                    }
                </td>


                <td>
                    ${statusBadge(
                        user.is_active
                        ? "active"
                        : "inactive"
                    )}
                </td>


                <td>

                    <button
                        class="sf-table-action"
                        data-user-toggle="${user.id}"
                        data-next-active="${!user.is_active}"
                    >
                        ${
                            user.is_active
                            ? "Suspend"
                            : "Activate"
                        }
                    </button>

                </td>

            </tr>
        `
        )
        .join("");


    $$(
        "[data-user-toggle]"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    toggleUser(
                        Number(
                            button.dataset
                                .userToggle
                        ),
                        button.dataset
                            .nextActive
                            === "true"
                    );

                }
            );

        }
    );
}


/* =========================================================
   USER STATUS
========================================================= */

async function toggleUser(
    userId,
    isActive
) {

    try {

        await apiFetch(
            `${ADMIN_API}/users/${userId}/status`,
            {
                method:
                    "PATCH",

                body:
                    JSON.stringify({
                        is_active:
                            isActive
                    })
            }
        );


        showToast(
            "User status updated successfully."
        );


        await loadUsers(
            state.usersPage
        );


        await loadDashboard();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   AGENTS
========================================================= */

async function loadAgents() {

    const grid =
        $("#agentsGrid");


    grid.innerHTML = `
        <div class="sf-loading-card">
            Loading agents...
        </div>
    `;


    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/agents`
            );


        state.agents =
            data.agents || [];


        renderAgents();

    } catch (error) {

        grid.innerHTML = `
            <div class="sf-loading-card">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

    }
}


function renderAgents() {

    const grid =
        $("#agentsGrid");


    if (!state.agents.length) {

        grid.innerHTML = `
            <div class="sf-loading-card">
                No agents found.
            </div>
        `;

        return;
    }


    grid.innerHTML =
        state.agents
        .map(
            agent => {

                const areas =
                    agent.areas || [];


                return `

                <article class="sf-agent-card">

                    <div class="sf-agent-header">

                        <div class="sf-agent-identity">

                            <div class="sf-agent-avatar">
                                ${initials(
                                    agent.user?.full_name
                                )}
                            </div>

                            <div>

                                <strong>
                                    ${escapeHtml(
                                        agent.user?.full_name
                                        || "Agent"
                                    )}
                                </strong>

                                <span>
                                    ${escapeHtml(
                                        agent.designation
                                        || "Area Agent"
                                    )}
                                </span>

                            </div>

                        </div>

                        <span class="sf-agent-code">
                            ${escapeHtml(
                                agent.agent_code
                            )}
                        </span>

                    </div>


                    <div>
                        ${statusBadge(
                            agent.is_active
                            ? "active"
                            : "inactive"
                        )}
                    </div>


                    <div class="sf-agent-meta">

                        <div class="sf-agent-meta-item">

                            <span>
                                SERVICE AREAS
                            </span>

                            <strong>
                                ${areas.length}
                            </strong>

                        </div>


                        <div class="sf-agent-meta-item">

                            <span>
                                PERMISSIONS
                            </span>

                            <strong>
                                ${
                                    (
                                        agent.permissions
                                        || []
                                    ).filter(
                                        p =>
                                            p.is_allowed
                                    ).length
                                }
                            </strong>

                        </div>

                    </div>


                    <div class="sf-agent-areas">

                        <div class="sf-agent-areas-title">

                            <span>
                                Assigned Areas
                            </span>

                            <button
                                class="sf-table-action"
                                data-agent-toggle="${agent.id}"
                                data-next-active="${!agent.is_active}"
                            >
                                ${
                                    agent.is_active
                                    ? "Suspend"
                                    : "Activate"
                                }
                            </button>

                        </div>


                        ${
                            areas.length
                            ?
                            areas
                                .filter(
                                    area =>
                                        area.is_active
                                )
                                .slice(
                                    0,
                                    8
                                )
                                .map(
                                    area => `
                                        <span class="sf-area-tag">
                                            ${escapeHtml(
                                                area.district
                                            )}
                                            ${
                                                area.area
                                                ? " · " +
                                                  escapeHtml(
                                                      area.area
                                                  )
                                                : ""
                                            }
                                        </span>
                                    `
                                )
                                .join("")
                            :
                            `<span class="sf-area-tag">
                                No active areas
                            </span>`
                        }

                    </div>

                </article>
            `;

            }
        )
        .join("");


    $$(
        "[data-agent-toggle]"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    toggleAgent(
                        Number(
                            button.dataset
                                .agentToggle
                        ),
                        button.dataset
                            .nextActive
                            === "true"
                    );

                }
            );

        }
    );
}


/* =========================================================
   AGENT STATUS
========================================================= */

async function toggleAgent(
    agentId,
    isActive
) {

    try {

        await apiFetch(
            `${ADMIN_API}/agents/${agentId}/status`,
            {
                method:
                    "PATCH",

                body:
                    JSON.stringify({
                        is_active:
                            isActive
                    })
            }
        );


        showToast(
            "Agent status updated."
        );


        await loadAgents();

        await loadDashboard();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   CREATE AGENT MODAL
========================================================= */

function openAgentModal() {

    const modal =
        $("#createAgentModal");


    modal.classList.add(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "false"
    );
}


function closeAgentModal() {

    const modal =
        $("#createAgentModal");


    modal.classList.remove(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "true"
    );
}


function addAreaRow() {

    const container =
        $("#agentAreasContainer");


    const row =
        document.createElement(
            "div"
        );


    row.className =
        "sf-area-row";


    row.innerHTML = `

        <input
            name="district"
            placeholder="District"
            required
        >

        <input
            name="police_station"
            placeholder="Police Station"
        >

        <input
            name="area"
            placeholder="Area"
        >

        <input
            name="pincode"
            placeholder="Pincode"
            maxlength="6"
        >

    `;


    container.appendChild(
        row
    );
}


async function createAgent(
    event
) {

    event.preventDefault();


    const form =
        $("#createAgentForm");


    const formData =
        new FormData(
            form
        );


    const areas =
        [];


    $$(
        "#agentAreasContainer .sf-area-row"
    ).forEach(
        row => {

            areas.push({

                district:
                    row.querySelector(
                        '[name="district"]'
                    )?.value
                    .trim(),

                police_station:
                    row.querySelector(
                        '[name="police_station"]'
                    )?.value
                    .trim(),

                area:
                    row.querySelector(
                        '[name="area"]'
                    )?.value
                    .trim(),

                pincode:
                    row.querySelector(
                        '[name="pincode"]'
                    )?.value
                    .trim()

            });

        }
    );


    const payload = {

        full_name:
            formData.get(
                "full_name"
            ),

        designation:
            formData.get(
                "designation"
            ),

        email:
            formData.get(
                "email"
            ),

        phone:
            formData.get(
                "phone"
            ),

        password:
            formData.get(
                "password"
            ),

        areas:
            areas

    };


    try {

        await apiFetch(
            `${ADMIN_API}/agents`,
            {
                method:
                    "POST",

                body:
                    JSON.stringify(
                        payload
                    )
            }
        );


        showToast(
            "Agent created successfully."
        );


        form.reset();


        $("#agentAreasContainer")
            .innerHTML = `

            <div class="sf-area-row">

                <input
                    name="district"
                    placeholder="District"
                    required
                >

                <input
                    name="police_station"
                    placeholder="Police Station"
                >

                <input
                    name="area"
                    placeholder="Area"
                >

                <input
                    name="pincode"
                    placeholder="Pincode"
                    maxlength="6"
                >

            </div>

        `;


        closeAgentModal();


        await loadAgents();

        await loadDashboard();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   JOBS
========================================================= */

async function loadJobs(
    page = 1
) {

    const status =
        $("#jobStatusFilter")
            ?.value
        || "";


    const body =
        $("#jobsTableBody");


    body.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="sf-loading">
                    Loading jobs...
                </div>
            </td>
        </tr>
    `;


    try {

        const query =
            new URLSearchParams({

                page:
                    page,

                per_page:
                    25

            });


        if (status) {

            query.set(
                "status",
                status
            );

        }


        const data =
            await apiFetch(
                `${ADMIN_API}/jobs?${query}`
            );


        state.jobs =
            data.jobs || [];


        state.jobsPage =
            page;


        renderJobs();


        renderPagination(
            "jobsPagination",
            data.pagination,
            loadJobs
        );

    } catch (error) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                </td>
            </tr>
        `;

    }
}


function renderJobs() {

    const body =
        $("#jobsTableBody");


    if (!state.jobs.length) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        No jobs found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML =
        state.jobs
        .map(
            job => `

            <tr>

                <td>

                    <div class="sf-user-cell">

                        <div class="sf-mini-avatar">
                            ▣
                        </div>

                        <div>

                            <strong>
                                ${escapeHtml(
                                    job.title
                                )}
                            </strong>

                            <span>
                                Job #${job.id}
                            </span>

                        </div>

                    </div>

                </td>


                <td>

                    <strong>
                        ${escapeHtml(
                            job.customer?.name
                            || "Unknown"
                        )}
                    </strong>

                    <div style="color:#909aaa;margin-top:3px;">
                        ${escapeHtml(
                            job.customer?.email
                            || ""
                        )}
                    </div>

                </td>


                <td>

                    ₹${Number(
                        job.budget?.min
                        || 0
                    ).toLocaleString(
                        "en-IN"
                    )}

                    -

                    ₹${Number(
                        job.budget?.max
                        || 0
                    ).toLocaleString(
                        "en-IN"
                    )}

                </td>


                <td>

                    ${escapeHtml(
                        job.city
                        || job.location
                        || "—"
                    )}

                    ${
                        job.pincode
                        ? `
                            <div style="color:#909aaa;margin-top:3px;">
                                ${escapeHtml(
                                    job.pincode
                                )}
                            </div>
                        `
                        : ""
                    }

                </td>


                <td>
                    ${statusBadge(
                        job.status
                    )}
                </td>


                <td>

                    ${
                        [
                            "pending_review",
                            "agent_review",
                            "admin_review"
                        ].includes(
                            job.status
                        )
                        ?
                        `
                        <button
                            class="sf-table-action"
                            data-job-approve="${job.id}"
                        >
                            Review
                        </button>
                        `
                        :
                        "—"
                    }

                </td>

            </tr>

        `
        )
        .join("");


    $$(
        "[data-job-approve]"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    approveJob(
                        Number(
                            button.dataset
                                .jobApprove
                        )
                    );

                }
            );

        }
    );
}


/* =========================================================
   JOB APPROVAL
========================================================= */

async function approveJob(
    jobId
) {

    const approved =
        window.confirm(
            "Approve this job?"
        );


    const action =
        approved
        ? "approve"
        : "reject";


    const remarks =
        window.prompt(
            "Optional remarks:"
        );


    try {

        await apiFetch(
            `${ADMIN_API}/jobs/${jobId}/approval`,
            {
                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        action:
                            action,

                        remarks:
                            remarks
                            || null

                    })
            }
        );


        showToast(
            approved
            ? "Job approved."
            : "Job rejected."
        );


        await loadJobs(
            state.jobsPage
        );


        await loadDashboard();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   APPLICATIONS
========================================================= */

async function loadApplications() {

    const body =
        $("#applicationsTableBody");


    body.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="sf-loading">
                    Loading applications...
                </div>
            </td>
        </tr>
    `;


    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/applications?per_page=50`
            );


        state.applications =
            data.applications || [];


        renderApplications();

    } catch (error) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                </td>
            </tr>
        `;

    }
}


function renderApplications() {

    const body =
        $("#applicationsTableBody");


    if (!state.applications.length) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        No applications found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML =
        state.applications
        .map(
            app => `

            <tr>

                <td>

                    <strong>
                        ${escapeHtml(
                            app.job_title
                            || "Job"
                        )}
                    </strong>

                    <div style="color:#909aaa;margin-top:3px;">
                        #${app.job_id}
                    </div>

                </td>


                <td>

                    <strong>
                        ${escapeHtml(
                            app.worker_name
                            || "Worker"
                        )}
                    </strong>

                    <div style="color:#909aaa;margin-top:3px;">
                        #${app.worker_id}
                    </div>

                </td>


                <td>

                    ₹${Number(
                        app.proposed_amount
                        || 0
                    ).toLocaleString(
                        "en-IN"
                    )}

                </td>


                <td>
                    ${escapeHtml(
                        app.availability
                        || "—"
                    )}
                </td>


                <td>
                    ${statusBadge(
                        app.status
                    )}
                </td>


                <td>

                    ${
                        [
                            "pending",
                            "customer_approved",
                            "agent_review",
                            "admin_review"
                        ].includes(
                            app.status
                        )
                        ?
                        `
                        <button
                            class="sf-table-action"
                            data-app-review="${app.id}"
                        >
                            Review
                        </button>
                        `
                        :
                        "—"
                    }

                </td>

            </tr>

        `
        )
        .join("");


    $$(
        "[data-app-review]"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    approveApplication(
                        Number(
                            button.dataset
                                .appReview
                        )
                    );

                }
            );

        }
    );
}


/* =========================================================
   APPLICATION APPROVAL
========================================================= */

async function approveApplication(
    applicationId
) {

    const approved =
        window.confirm(
            "Approve this application and mark worker as hired?"
        );


    const action =
        approved
        ? "approve"
        : "reject";


    const remarks =
        window.prompt(
            "Optional remarks:"
        );


    try {

        await apiFetch(
            `${ADMIN_API}/applications/${applicationId}/approval`,
            {
                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        action:
                            action,

                        remarks:
                            remarks
                            || null

                    })
            }
        );


        showToast(
            approved
            ? "Application approved and hired."
            : "Application rejected."
        );


        await loadApplications();

        await loadDashboard();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );

    }
}


/* =========================================================
   CATEGORIES
========================================================= */

async function loadCategories() {

    const grid =
        $("#categoriesGrid");


    grid.innerHTML = `
        <div class="sf-loading-card">
            Loading categories...
        </div>
    `;


    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/categories`
            );


        state.categories =
            data.categories || [];


        renderCategories();

    } catch (error) {

        grid.innerHTML = `
            <div class="sf-loading-card">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

    }
}


function renderCategories() {

    const grid =
        $("#categoriesGrid");


    if (!state.categories.length) {

        grid.innerHTML = `
            <div class="sf-loading-card">
                No categories found.
            </div>
        `;

        return;
    }


    grid.innerHTML =
        state.categories
        .map(
            category => `

            <article class="sf-category-card">

                <div class="sf-category-icon">
                    ${
                        escapeHtml(
                            category.icon
                            || "▦"
                        )
                    }
                </div>

                <h3>
                    ${escapeHtml(
                        category.name
                    )}
                </h3>

                <p>
                    ${escapeHtml(
                        category.description
                        || "No description available."
                    )}
                </p>

                <div>
                    ${statusBadge(
                        category.is_active
                        ? "active"
                        : "inactive"
                    )}
                </div>

            </article>

        `
        )
        .join("");
}


/* =========================================================
   AUDIT LOGS
========================================================= */

async function loadAuditLogs(
    page = 1
) {

    const body =
        $("#auditTableBody");


    body.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="sf-loading">
                    Loading audit logs...
                </div>
            </td>
        </tr>
    `;


    try {

        const data =
            await apiFetch(
                `${ADMIN_API}/audit-logs?page=${page}&per_page=50`
            );


        renderAuditLogs(
            data.logs || []
        );


        renderPagination(
            "auditPagination",
            data.pagination,
            loadAuditLogs
        );

    } catch (error) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                </td>
            </tr>
        `;

    }
}


function renderAuditLogs(
    logs
) {

    const body =
        $("#auditTableBody");


    if (!logs.length) {

        body.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="sf-loading">
                        No audit logs found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML =
        logs
        .map(
            log => `

            <tr>

                <td>
                    ${formatDate(
                        log.created_at
                    )}
                </td>


                <td>

                    <strong>
                        ${escapeHtml(
                            log.action
                        )}
                    </strong>

                </td>


                <td>

                    ${escapeHtml(
                        log.resource_type
                        || "—"
                    )}

                    ${
                        log.resource_id
                        ? `
                            #${log.resource_id}
                        `
                        : ""
                    }

                </td>


                <td>

                    ${
                        log.new_status
                        ?
                        statusBadge(
                            log.new_status
                        )
                        :
                        "—"
                    }

                </td>


                <td>
                    ${escapeHtml(
                        log.ip_address
                        || "—"
                    )}
                </td>


                <td>

                    <small>
                        ${escapeHtml(
                            JSON.stringify(
                                log.details
                                || {}
                            )
                        )}
                    </small>

                </td>

            </tr>

        `
        )
        .join("");
}


/* =========================================================
   PAGINATION
========================================================= */

function renderPagination(
    containerId,
    pagination,
    callback
) {

    const container =
        $(
            `#${containerId}`
        );


    if (
        !container
        ||
        !pagination
        ||
        pagination.pages <= 1
    ) {

        if (container) {

            container.innerHTML =
                "";

        }

        return;
    }


    const current =
        pagination.page;


    const total =
        pagination.pages;


    let html = "";


    if (
        pagination.has_prev
    ) {

        html += `
            <button
                data-page="${current - 1}"
            >
                ‹
            </button>
        `;

    }


    const start =
        Math.max(
            1,
            current - 2
        );


    const end =
        Math.min(
            total,
            current + 2
        );


    for (
        let i = start;
        i <= end;
        i++
    ) {

        html += `
            <button
                class="${i === current ? "active" : ""}"
                data-page="${i}"
            >
                ${i}
            </button>
        `;

    }


    if (
        pagination.has_next
    ) {

        html += `
            <button
                data-page="${current + 1}"
            >
                ›
            </button>
        `;

    }


    container.innerHTML =
        html;


    container
        .querySelectorAll(
            "button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        callback(
                            Number(
                                button.dataset
                                    .page
                            )
                        );

                    }
                );

            }
        );
}


/* =========================================================
   NAVIGATION
========================================================= */

function navigateTo(
    section
) {

    state.currentSection =
        section;


    $$(".sf-nav-item")
        .forEach(
            item => {

                item.classList.toggle(
                    "active",
                    item.dataset.section
                    === section
                );

            }
        );


    $$(".sf-page-section")
        .forEach(
            item => {

                item.classList.toggle(
                    "active",
                    item.id
                    ===
                    `section-${section}`
                );

            }
        );


    const titles = {

        dashboard:
            "Command Center",

        users:
            "Users",

        agents:
            "Agents",

        workers:
            "Worker Verification",

        jobs:
            "Jobs",

        applications:
            "Applications",

        categories:
            "Categories",

        audit:
            "Audit Logs"

    };


    $("#pageTitle")
        .textContent =
        titles[section]
        || "Dashboard";


    $("#pageBreadcrumb")
        .textContent =
        titles[section]
        || "Dashboard";


    closeSidebar();


    loadSection(
        section
    );
}


/* =========================================================
   SECTION LOADER
========================================================= */

async function loadSection(
    section
) {

    switch (
        section
    ) {

        case "dashboard":

            await loadDashboard();

            break;


        case "users":

            await loadUsers(
                state.usersPage
            );

            break;


        case "agents":

            await loadAgents();

            break;


        case "jobs":

            await loadJobs(
                state.jobsPage
            );

            break;


        case "applications":

            await loadApplications();

            break;


        case "categories":

            await loadCategories();

            break;


        case "audit":

            await loadAuditLogs(
                state.auditPage
            );

            break;

    }
}


/* =========================================================
   SIDEBAR
========================================================= */

function openSidebar() {

    $("#adminSidebar")
        .classList.add(
            "open"
        );

    $("#sidebarOverlay")
        .classList.add(
            "open"
        );
}


function closeSidebar() {

    $("#adminSidebar")
        .classList.remove(
            "open"
        );

    $("#sidebarOverlay")
        .classList.remove(
            "open"
        );
}


/* =========================================================
   LOGOUT
========================================================= */

async function logout() {

    try {

        await apiFetch(
            `${ADMIN_API}/logout`,
            {
                method:
                    "POST"
            }
        );

    } catch (
        error
    ) {

        console.error(
            error
        );

    } finally {

        window.location.href =
            "/admin/login";

    }
}


/* =========================================================
   EVENTS
========================================================= */

function bindEvents() {


    /* NAV */

    $$(".sf-nav-item")
        .forEach(
            item => {

                item.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        navigateTo(
                            item.dataset
                                .section
                        );

                    }
                );

            }
        );


    /* QUICK ACTIONS */

    $$(
        "[data-section]"
    ).forEach(
        item => {

            if (
                item.classList.contains(
                    "sf-nav-item"
                )
            ) {

                return;

            }


            item.addEventListener(
                "click",
                () => {

                    if (
                        item.dataset.section
                    ) {

                        navigateTo(
                            item.dataset
                                .section
                        );

                    }

                }
            );

        }
    );


    /* MOBILE */

    $("#mobileMenu")
        ?.addEventListener(
            "click",
            openSidebar
        );


    $("#sidebarOverlay")
        ?.addEventListener(
            "click",
            closeSidebar
        );


    /* REFRESH */

    $("#refreshDashboard")
        ?.addEventListener(
            "click",
            async () => {

                await loadDashboard();

                showToast(
                    "Dashboard refreshed."
                );

            }
        );


    $("#refreshUsers")
        ?.addEventListener(
            () =>
                loadUsers(
                    state.usersPage
                )
        );


    $("#refreshJobs")
        ?.addEventListener(
            () =>
                loadJobs(
                    1
                )
        );


    $("#refreshAudit")
        ?.addEventListener(
            () =>
                loadAuditLogs(
                    1
                )
        );


    /* USER FILTER */

    $("#userSearch")
        ?.addEventListener(
            "input",
            renderUsers
        );


    $("#userRoleFilter")
        ?.addEventListener(
            "change",
            renderUsers
        );


    /* JOB FILTER */

    $("#jobStatusFilter")
        ?.addEventListener(
            "change",
            () =>
                loadJobs(
                    1
                )
        );


    /* CREATE AGENT */

    $("#openCreateAgent")
        ?.addEventListener(
            "click",
            openAgentModal
        );


    $("#closeCreateAgent")
        ?.addEventListener(
            "click",
            closeAgentModal
        );


    $("#cancelCreateAgent")
        ?.addEventListener(
            "click",
            closeAgentModal
        );


    $("#addAreaButton")
        ?.addEventListener(
            "click",
            addAreaRow
        );


    $("#createAgentForm")
        ?.addEventListener(
            "submit",
            createAgent
        );


    $("#logoutButton")
        ?.addEventListener(
            "click",
            logout
        );

}


/* =========================================================
   INIT
========================================================= */

async function initDashboard() {

    bindEvents();


    await loadAdmin();


    await loadDashboard();


    /*
     * Preload the first useful data.
     */

    await Promise.allSettled([

        loadAgents(),

        loadCategories()

    ]);

}


document.addEventListener(
    "DOMContentLoaded",
    initDashboard
);
