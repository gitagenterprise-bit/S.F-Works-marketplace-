/* =========================================================
   S.F WORKS — ENTERPRISE ADMIN DASHBOARD
   ========================================================= */

(() => {

    "use strict";


    /* =====================================================
       CONFIG
    ====================================================== */

    const app = document.getElementById("adminApp");

    const API = app?.dataset.apiPrefix || "/api/admin";


    const state = {

        currentSection: "dashboard",

        usersPage: 1,
        jobsPage: 1,
        applicationsPage: 1,
        auditPage: 1,

        jobsStatus: "",

        userSearch: "",

        pendingConfirm: null,

        agentAreas: 1

    };


    /* =====================================================
       DOM HELPERS
    ====================================================== */

    const $ = selector =>
        document.querySelector(selector);

    const $$ = selector =>
        [...document.querySelectorAll(selector)];


    /* =====================================================
       API CLIENT
    ====================================================== */

    async function api(
        endpoint,
        options = {}
    ) {

        const config = {

            credentials: "same-origin",

            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            },

            ...options

        };

        let response;

        try {

            response = await fetch(
                `${API}${endpoint}`,
                config
            );

        } catch (error) {

            throw new Error(
                "Unable to connect to server."
            );
        }


        let payload = {};

        try {

            payload = await response.json();

        } catch (_) {

            payload = {};
        }


        if (!response.ok) {

            throw new Error(
                payload.message ||
                `Request failed (${response.status})`
            );
        }


        return payload;
    }


    /* =====================================================
       TOAST
    ====================================================== */

    function toast(
        message,
        type = "success"
    ) {

        const container =
            $("#toastContainer");

        if (!container) return;

        const item =
            document.createElement("div");

        item.className =
            `toast ${type}`;

        const icon =
            type === "success"
                ? "✓"
                : type === "error"
                    ? "!"
                    : "•";

        item.innerHTML = `
            <strong>${icon}</strong>
            <span>${escapeHtml(message)}</span>
        `;

        container.appendChild(item);

        setTimeout(() => {

            item.style.opacity = "0";
            item.style.transform =
                "translateY(8px)";

            setTimeout(
                () => item.remove(),
                200
            );

        }, 3500);
    }


    /* =====================================================
       ESCAPE
    ====================================================== */

    function escapeHtml(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }

        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    /* =====================================================
       FORMATTERS
    ====================================================== */

    function formatDate(value) {

        if (!value) return "—";

        const date =
            new Date(value);

        if (Number.isNaN(
            date.getTime()
        )) {
            return "—";
        }

        return date.toLocaleString(
            undefined,
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );
    }


    function formatMoney(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "—";
        }

        return new Intl.NumberFormat(
            "en-IN",
            {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 0
            }
        ).format(value);
    }


    function initials(name) {

        return String(name || "A")
            .trim()
            .split(/\s+/)
            .slice(0, 2)
            .map(
                part =>
                    part.charAt(0).toUpperCase()
            )
            .join("");
    }


    function statusBadge(status) {

        const value =
            String(status || "unknown")
                .toLowerCase();

        const label =
            value
                .replaceAll("_", " ")
                .replace(
                    /\b\w/g,
                    char =>
                        char.toUpperCase()
                );

        let type = value;

        if (
            ![
                "active",
                "approved",
                "hired",
                "pending",
                "agent_review",
                "admin_review",
                "customer_approved",
                "rejected",
                "deleted",
                "inactive"
            ].includes(value)
        ) {
            type = "default";
        }

        return `
            <span class="status-badge ${type}">
                ${escapeHtml(label)}
            </span>
        `;
    }


    /* =====================================================
       NAVIGATION
    ====================================================== */

    function openSection(
        section
    ) {

        state.currentSection =
            section;

        $$(".admin-section")
            .forEach(element => {

                element.classList.toggle(
                    "active",
                    element.id ===
                    `section-${section}`
                );

            });


        $$(".admin-nav-item")
            .forEach(item => {

                item.classList.toggle(
                    "active",
                    item.dataset.section ===
                    section
                );

            });


        const titles = {

            dashboard:
                "Dashboard",

            users:
                "Users",

            workers:
                "Worker Verification",

            agents:
                "Agents",

            jobs:
                "Jobs",

            applications:
                "Applications",

            categories:
                "Categories",

            audit:
                "Audit Logs"

        };


        const title =
            titles[section] ||
            "Dashboard";


        $("#pageTitle").textContent =
            title;

        $("#breadcrumb").textContent =
            `Admin / ${title}`;


        closeMobileSidebar();


        loadSection(section);
    }


    async function loadSection(
        section
    ) {

        try {

            switch (section) {

                case "dashboard":
                    await loadDashboard();
                    break;

                case "users":
                    await loadUsers();
                    break;

                case "agents":
                    await loadAgents();
                    break;

                case "jobs":
                    await loadJobs();
                    break;

                case "applications":
                    await loadApplications();
                    break;

                case "categories":
                    await loadCategories();
                    break;

                case "audit":
                    await loadAuditLogs();
                    break;

            }

        } catch (error) {

            toast(
                error.message,
                "error"
            );
        }
    }


    /* =====================================================
       MOBILE SIDEBAR
    ====================================================== */

    function openMobileSidebar() {

        $("#adminSidebar")
            ?.classList.add("open");

        $("#sidebarOverlay")
            ?.classList.add("open");
    }


    function closeMobileSidebar() {

        $("#adminSidebar")
            ?.classList.remove("open");

        $("#sidebarOverlay")
            ?.classList.remove("open");
    }


    /* =====================================================
       CURRENT ADMIN
    ====================================================== */

    async function loadAdmin() {

        const result =
            await api("/me");

        const user =
            result.user;

        if (!user) return;

        const name =
            user.full_name ||
            "Administrator";

        $("#adminName").textContent =
            name;

        $("#dropdownAdminName").textContent =
            name;

        $("#welcomeName").textContent =
            name.split(" ")[0];

        $("#adminEmail").textContent =
            user.email || "Administrator";

        $("#adminAvatar").textContent =
            initials(name);
    }


    /* =====================================================
       DASHBOARD
    ====================================================== */

    async function loadDashboard() {

        const result =
            await api("/dashboard");

        const stats =
            result.stats || {};

        setText(
            "statTotalUsers",
            stats.total_users
        );

        setText(
            "statActiveUsers",
            stats.active_users
        );

        setText(
            "statTotalWorkers",
            stats.total_workers
        );

        setText(
            "statPendingWorkers",
            stats.pending_workers
        );

        setText(
            "statTotalAgents",
            stats.total_agents
        );

        setText(
            "statTotalJobs",
            stats.total_jobs
        );

        setText(
            "statPendingJobs",
            stats.pending_jobs
        );

        setText(
            "statApplications",
            stats.total_applications
        );

        setText(
            "statCategories",
            stats.total_categories
        );

        setText(
            "queueWorkers",
            stats.pending_workers
        );

        setText(
            "queueJobs",
            stats.pending_jobs
        );

        setText(
            "queueApplications",
            stats.pending_applications
        );

        setText(
            "navUsersCount",
            stats.total_users
        );

        setText(
            "navAgentsCount",
            stats.total_agents
        );

        setText(
            "navJobsCount",
            stats.total_jobs
        );
    }


    function setText(
        id,
        value
    ) {

        const element =
            document.getElementById(id);

        if (element) {

            element.textContent =
                Number.isFinite(
                    Number(value)
                )
                    ? Number(value).toLocaleString("en-IN")
                    : (value ?? "0");
        }
    }


    /* =====================================================
       USERS
    ====================================================== */

    async function loadUsers(
        page = state.usersPage
    ) {

        state.usersPage = page;

        const result =
            await api(
                `/users?page=${page}&per_page=25`
            );

        let users =
            result.users || [];

        if (state.userSearch) {

            const term =
                state.userSearch
                    .toLowerCase();

            users =
                users.filter(
                    user =>
                        String(
                            user.full_name || ""
                        )
                            .toLowerCase()
                            .includes(term)
                        ||
                        String(
                            user.email || ""
                        )
                            .toLowerCase()
                            .includes(term)
                        ||
                        String(
                            user.phone || ""
                        )
                            .toLowerCase()
                            .includes(term)
                );
        }


        const body =
            $("#usersTableBody");

        if (!users.length) {

            body.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="table-loading">
                            No users found.
                        </div>
                    </td>
                </tr>
            `;

        } else {

            body.innerHTML =
                users.map(
                    renderUserRow
                ).join("");
        }


        renderPagination(
            $("#usersPagination"),
            result.pagination,
            loadUsers
        );
    }


    function renderUserRow(
        user
    ) {

        const active =
            Boolean(user.is_active);

        return `
            <tr>

                <td>

                    <div class="table-user">

                        <div class="table-avatar">
                            ${escapeHtml(
                                initials(
                                    user.full_name
                                )
                            )}
                        </div>

                        <div class="table-user-info">

                            <strong>
                                ${escapeHtml(
                                    user.full_name ||
                                    "Unknown"
                                )}
                            </strong>

                            <span>
                                #${user.id}
                            </span>

                        </div>

                    </div>

                </td>


                <td>

                    <div class="table-user-info">

                        <span>
                            ${escapeHtml(
                                user.email || "—"
                            )}
                        </span>

                        <span>
                            ${escapeHtml(
                                user.phone || "—"
                            )}
                        </span>

                    </div>

                </td>


                <td>
                    ${statusBadge(
                        user.role
                    )}
                </td>


                <td>
                    ${statusBadge(
                        active
                            ? "active"
                            : "inactive"
                    )}
                </td>


                <td>
                    ${user.is_verified
                        ? `
                            <span class="status-badge approved">
                                Verified
                            </span>
                        `
                        : `
                            <span class="status-badge pending">
                                Unverified
                            </span>
                        `
                    }
                </td>


                <td>
                    ${formatDate(
                        user.created_at
                    )}
                </td>


                <td>

                    <div class="table-actions">

                        <button
                            class="table-action ${
                                active
                                    ? "danger"
                                    : "success"
                            }"
                            data-user-status="${user.id}"
                            data-active="${active}"
                        >
                            ${
                                active
                                    ? "Suspend"
                                    : "Activate"
                            }
                        </button>


                        ${
                            !user.is_verified
                                ? `
                                    <button
                                        class="table-action success"
                                        data-user-verify="${user.id}"
                                    >
                                        Verify
                                    </button>
                                `
                                : ""
                        }

                    </div>

                </td>

            </tr>
        `;
    }


    /* =====================================================
       USER ACTIONS
    ====================================================== */

    async function updateUserStatus(
        userId,
        active
    ) {

        await api(
            `/users/${userId}/status`,
            {
                method: "PATCH",

                body: JSON.stringify({
                    is_active: !active
                })
            }
        );

        toast(
            `User ${
                active
                    ? "suspended"
                    : "activated"
            } successfully.`
        );

        await Promise.all([
            loadUsers(),
            loadDashboard()
        ]);
    }


    async function verifyUser(
        userId
    ) {

        await api(
            `/users/${userId}/verify`,
            {
                method: "PATCH"
            }
        );

        toast(
            "User verified successfully."
        );

        await Promise.all([
            loadUsers(),
            loadDashboard()
        ]);
    }


    /* =====================================================
       AGENTS
    ====================================================== */

    async function loadAgents() {

        const result =
            await api("/agents");

        const agents =
            result.agents || [];

        const grid =
            $("#agentGrid");

        if (!agents.length) {

            grid.innerHTML = `
                <div class="panel">
                    <div class="empty-state">
                        <div class="empty-icon">◆</div>
                        <h3>No agents yet</h3>
                        <p>
                            Create your first operational agent.
                        </p>
                        <button
                            class="btn btn-primary"
                            id="emptyCreateAgent"
                        >
                            Create Agent
                        </button>
                    </div>
                </div>
            `;

            $("#emptyCreateAgent")
                ?.addEventListener(
                    "click",
                    openAgentModal
                );

            return;
        }


        grid.innerHTML =
            agents
                .map(renderAgentCard)
                .join("");
    }


    function renderAgentCard(
        agent
    ) {

        const user =
            agent.user || {};

        const active =
            Boolean(user.is_active);

        const areas =
            agent.areas || [];

        const permissions =
            agent.permissions || [];


        const areaTags =
            areas.length
                ? areas
                    .slice(0, 5)
                    .map(
                        area => `
                            <span class="area-tag">
                                ${escapeHtml(
                                    area.name
                                )}
                            </span>
                        `
                    )
                    .join("")
                : `
                    <span class="area-tag">
                        No areas assigned
                    </span>
                `;


        return `
            <article
                class="agent-card"
                data-agent-card="${agent.id}"
            >

                <div class="agent-card-header">

                    <div class="agent-identity">

                        <div class="agent-avatar">
                            ${escapeHtml(
                                initials(
                                    user.full_name
                                )
                            )}
                        </div>

                        <div class="agent-name">

                            <strong>
                                ${escapeHtml(
                                    user.full_name ||
                                    "Agent"
                                )}
                            </strong>

                            <span>
                                ${escapeHtml(
                                    agent.designation ||
                                    "Area Agent"
                                )}
                            </span>

                            <span class="employee-code">
                                ${escapeHtml(
                                    agent.employee_code
                                )}
                            </span>

                        </div>

                    </div>

                    ${statusBadge(
                        active
                            ? "active"
                            : "inactive"
                    )}

                </div>


                <div class="agent-details">

                    <div class="agent-detail">

                        <span>
                            Email
                        </span>

                        <strong>
                            ${escapeHtml(
                                user.email || "—"
                            )}
                        </strong>

                    </div>


                    <div class="agent-detail">

                        <span>
                            Phone
                        </span>

                        <strong>
                            ${escapeHtml(
                                user.phone || "—"
                            )}
                        </strong>

                    </div>


                    <div class="agent-detail">

                        <span>
                            Areas
                        </span>

                        <strong>
                            ${areas.length}
                        </strong>

                    </div>


                    <div class="agent-detail">

                        <span>
                            Permissions
                        </span>

                        <strong>
                            ${permissions.filter(
                                p => p.is_allowed
                            ).length}
                        </strong>

                    </div>

                </div>


                <div class="agent-areas">

                    <div class="agent-areas-title">

                        <span>
                            Service Areas
                        </span>

                        <span>
                            ${areas.length}
                        </span>

                    </div>

                    <div class="area-tags">
                        ${areaTags}
                    </div>

                </div>


                <div class="agent-card-footer">

                    <button
                        class="table-action"
                        data-agent-toggle="${agent.id}"
                        data-active="${active}"
                    >
                        ${
                            active
                                ? "Suspend Agent"
                                : "Activate Agent"
                        }
                    </button>

                    <button
                        class="table-action"
                        data-agent-areas="${agent.id}"
                    >
                        Manage Areas
                    </button>

                </div>

            </article>
        `;
    }


    /* =====================================================
       CREATE AGENT MODAL
    ====================================================== */

    function openAgentModal() {

        const modal =
            $("#agentModal");

        modal.classList.add("open");

        modal.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.style.overflow =
            "hidden";

        setTimeout(
            () =>
                modal
                    .querySelector(
                        'input[name="full_name"]'
                    )
                    ?.focus(),
            100
        );
    }


    function closeModal(
        id
    ) {

        const modal =
            document.getElementById(id);

        if (!modal) return;

        modal.classList.remove("open");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );

        if (
            !document.querySelector(
                ".modal-backdrop.open"
            )
        ) {
            document.body.style.overflow =
                "";
        }
    }


    function addAreaForm() {

        const container =
            $("#agentAreaContainer");

        const card =
            document.createElement("div");

        card.className =
            "area-form-card";

        card.innerHTML = `

            <button
                type="button"
                class="area-remove"
                title="Remove area"
            >
                ×
            </button>

            <div class="area-form-grid">

                <div class="form-group">

                    <label>
                        Area Name *
                    </label>

                    <input
                        data-area-field="name"
                        required
                        placeholder="Area name"
                    >

                </div>

                <div class="form-group">

                    <label>
                        Area Type
                    </label>

                    <select
                        data-area-field="area_type"
                    >
                        <option value="locality">
                            Locality
                        </option>
                        <option value="police_station">
                            Police Station
                        </option>
                        <option value="district">
                            District
                        </option>
                        <option value="pincode">
                            Pincode
                        </option>
                    </select>

                </div>

                <div class="form-group">

                    <label>
                        District
                    </label>

                    <input
                        data-area-field="district"
                        placeholder="District"
                    >

                </div>

                <div class="form-group">

                    <label>
                        Police Station
                    </label>

                    <input
                        data-area-field="police_station"
                        placeholder="Police Station"
                    >

                </div>

                <div class="form-group">

                    <label>
                        Locality
                    </label>

                    <input
                        data-area-field="locality"
                        placeholder="Locality"
                    >

                </div>

                <div class="form-group">

                    <label>
                        Pincode
                    </label>

                    <input
                        data-area-field="pincode"
                        maxlength="6"
                        inputmode="numeric"
                        placeholder="Pincode"
                    >

                </div>

                <div class="form-group">

                    <label>
                        State
                    </label>

                    <input
                        data-area-field="state"
                        placeholder="State"
                    >

                </div>

            </div>
        `;

        container.appendChild(card);
    }


    function collectAgentAreas() {

        return [
            ...document.querySelectorAll(
                ".area-form-card"
            )
        ].map(card => {

            const get =
                field =>
                    card
                        .querySelector(
                            `[data-area-field="${field}"]`
                        )
                        ?.value
                        ?.trim() || "";

            return {

                name:
                    get("name"),

                area_type:
                    get("area_type")
                    || "locality",

                district:
                    get("district"),

                police_station:
                    get("police_station"),

                locality:
                    get("locality"),

                pincode:
                    get("pincode"),

                state:
                    get("state")
            };
        });
    }


    async function createAgent(
        event
    ) {

        event.preventDefault();

        const form =
            event.currentTarget;

        const button =
            $("#createAgentButton");

        const formData =
            new FormData(form);

        const areas =
            collectAgentAreas();


        const payload = {

            full_name:
                formData.get(
                    "full_name"
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

            designation:
                formData.get(
                    "designation"
                ),

            areas:
                areas

        };


        if (
            areas.some(
                area => !area.name
            )
        ) {

            toast(
                "Every service area must have a name.",
                "error"
            );

            return;
        }


        button.disabled =
            true;

        button.textContent =
            "Creating...";


        try {

            const result =
                await api(
                    "/agents",
                    {
                        method: "POST",
                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            closeModal(
                "agentModal"
            );

            form.reset();

            resetAreaForms();


            await Promise.all([
                loadAgents(),
                loadDashboard()
            ]);


            const agent =
                result.agent;

            toast(
                `Agent ${agent?.employee_code || ""} created successfully.`
            );


        } catch (error) {

            toast(
                error.message,
                "error"
            );

        } finally {

            button.disabled =
                false;

            button.textContent =
                "Create Agent";
        }
    }


    function resetAreaForms() {

        const container =
            $("#agentAreaContainer");

        container.innerHTML = "";

        const template =
            document.createElement(
                "div"
            );

        template.className =
            "area-form-card";

        template.innerHTML = `

            <div class="area-form-grid">

                <div class="form-group">
                    <label>Area Name *</label>
                    <input
                        data-area-field="name"
                        required
                        placeholder="e.g. Bangaon"
                    >
                </div>

                <div class="form-group">
                    <label>Area Type</label>
                    <select
                        data-area-field="area_type"
                    >
                        <option value="locality">
                            Locality
                        </option>
                        <option value="police_station">
                            Police Station
                        </option>
                        <option value="district">
                            District
                        </option>
                        <option value="pincode">
                            Pincode
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label>District</label>
                    <input
                        data-area-field="district"
                        placeholder="District"
                    >
                </div>

                <div class="form-group">
                    <label>Police Station</label>
                    <input
                        data-area-field="police_station"
                        placeholder="Police Station"
                    >
                </div>

                <div class="form-group">
                    <label>Locality</label>
                    <input
                        data-area-field="locality"
                        placeholder="Locality"
                    >
                </div>

                <div class="form-group">
                    <label>Pincode</label>
                    <input
                        data-area-field="pincode"
                        maxlength="6"
                        inputmode="numeric"
                        placeholder="6 digit pincode"
                    >
                </div>

                <div class="form-group">
                    <label>State</label>
                    <input
                        data-area-field="state"
                        placeholder="West Bengal"
                    >
                </div>

            </div>
        `;

        container.appendChild(
            template
        );
    }


    /* =====================================================
       AGENT STATUS
    ====================================================== */

    async function toggleAgent(
        agentId,
        active
    ) {

        await api(
            `/agents/${agentId}/status`,
            {
                method: "PATCH",

                body:
                    JSON.stringify({
                        is_active:
                            !active
                    })
            }
        );

        toast(
            `Agent ${
                active
                    ? "suspended"
                    : "activated"
            } successfully.`
        );

        await Promise.all([
            loadAgents(),
            loadDashboard()
        ]);
    }


    /* =====================================================
       JOBS
    ====================================================== */

    async function loadJobs(
        page = state.jobsPage
    ) {

        state.jobsPage =
            page;

        const query =
            new URLSearchParams({
                page,
                per_page: 25
            });

        if (state.jobsStatus) {

            query.set(
                "status",
                state.jobsStatus
            );
        }


        const result =
            await api(
                `/jobs?${query.toString()}`
            );

        const jobs =
            result.jobs || [];

        const body =
            $("#jobsTableBody");


        if (!jobs.length) {

            body.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="table-loading">
                            No jobs found.
                        </div>
                    </td>
                </tr>
            `;

        } else {

            body.innerHTML =
                jobs
                    .map(renderJobRow)
                    .join("");
        }


        renderPagination(
            $("#jobsPagination"),
            result.pagination,
            loadJobs
        );
    }


    function renderJobRow(
        job
    ) {

        const budget =
            job.budget?.min !== null &&
            job.budget?.max !== null
                ? `${formatMoney(
                    job.budget.min
                )} – ${formatMoney(
                    job.budget.max
                )}`
                : "Negotiable";


        const canReview =
            ![
                "deleted",
                "approved",
                "rejected"
            ].includes(
                job.status
            );


        return `
            <tr>

                <td>

                    <div class="table-user">

                        <div class="table-avatar">
                            ▤
                        </div>

                        <div class="table-user-info">

                            <strong>
                                ${escapeHtml(
                                    job.title
                                )}
                            </strong>

                            <span>
                                #${job.id}
                            </span>

                        </div>

                    </div>

                </td>


                <td>
                    ${escapeHtml(
                        job.customer?.name ||
                        "—"
                    )}
                </td>


                <td>
                    ${escapeHtml(
                        job.category?.name ||
                        "—"
                    )}
                </td>


                <td>
                    ${budget}
                </td>


                <td>
                    ${statusBadge(
                        job.status
                    )}
                </td>


                <td>
                    ${formatDate(
                        job.created_at
                    )}
                </td>


                <td>

                    <div class="table-actions">

                        ${
                            canReview
                                ? `
                                    <button
                                        class="table-action success"
                                        data-job-approval="${job.id}"
                                        data-action="approve"
                                    >
                                        Approve
                                    </button>

                                    <button
                                        class="table-action danger"
                                        data-job-approval="${job.id}"
                                        data-action="reject"
                                    >
                                        Reject
                                    </button>
                                `
                                : ""
                        }


                        ${
                            job.status !== "deleted"
                                ? `
                                    <button
                                        class="table-action danger"
                                        data-job-delete="${job.id}"
                                    >
                                        Delete
                                    </button>
                                `
                                : ""
                        }

                    </div>

                </td>

            </tr>
        `;
    }


    /* =====================================================
       JOB APPROVAL
    ====================================================== */

    async function updateJobApproval(
        jobId,
        action
    ) {

        const remarks =
            window.prompt(
                `${
                    action === "approve"
                        ? "Approval"
                        : "Rejection"
                } remarks (optional):`,
                ""
            );


        await api(
            `/jobs/${jobId}/approval`,
            {
                method: "PATCH",

                body:
                    JSON.stringify({
                        action,
                        remarks:
                            remarks ||
                            null
                    })
            }
        );


        toast(
            `Job ${
                action === "approve"
                    ? "approved"
                    : "rejected"
            } successfully.`
        );


        await Promise.all([
            loadJobs(),
            loadDashboard()
        ]);
    }


    /* =====================================================
       JOB DELETE
    ====================================================== */

    async function deleteJob(
        jobId
    ) {

        await api(
            `/jobs/${jobId}`,
            {
                method: "DELETE"
            }
        );

        toast(
            "Job removed successfully."
        );

        await Promise.all([
            loadJobs(),
            loadDashboard()
        ]);
    }


    /* =====================================================
       APPLICATIONS
    ====================================================== */

    async function loadApplications(
        page = state.applicationsPage
    ) {

        state.applicationsPage =
            page;

        const status =
            $("#applicationStatusFilter")
                ?.value || "";


        const query =
            new URLSearchParams({
                page,
                per_page: 25
            });

        if (status) {

            query.set(
                "status",
                status
            );
        }


        const result =
            await api(
                `/applications?${query.toString()}`
            );

        const applications =
            result.applications || [];


        const body =
            $("#applicationsTableBody");


        if (!applications.length) {

            body.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="table-loading">
                            No applications found.
                        </div>
                    </td>
                </tr>
            `;

        } else {

            body.innerHTML =
                applications
                    .map(
                        renderApplicationRow
                    )
                    .join("");
        }


        renderPagination(
            $("#applicationsPagination"),
            result.pagination,
            loadApplications
        );
    }


    function renderApplicationRow(
        application
    ) {

        const canReview =
            ![
                "hired",
                "rejected"
            ].includes(
                application.status
            );


        return `
            <tr>

                <td>
                    #${application.id}
                </td>

                <td>
                    ${escapeHtml(
                        application.worker_name ||
                        "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        application.job_title ||
                        "—"
                    )}
                </td>

                <td>
                    ${formatMoney(
                        application.proposed_amount
                    )}
                </td>

                <td>
                    ${statusBadge(
                        application.status
                    )}
                </td>

                <td>
                    ${formatDate(
                        application.created_at
                    )}
                </td>

                <td>

                    <div class="table-actions">

                        ${
                            canReview
                                ? `
                                    <button
                                        class="table-action success"
                                        data-application-approval="${application.id}"
                                        data-action="approve"
                                    >
                                        Hire
                                    </button>

                                    <button
                                        class="table-action danger"
                                        data-application-approval="${application.id}"
                                        data-action="reject"
                                    >
                                        Reject
                                    </button>
                                `
                                : ""
                        }

                    </div>

                </td>

            </tr>
        `;
    }


    async function updateApplicationApproval(
        applicationId,
        action
    ) {

        const remarks =
            window.prompt(
                "Remarks (optional):",
                ""
            );


        await api(
            `/applications/${applicationId}/approval`,
            {
                method: "PATCH",

                body:
                    JSON.stringify({
                        action,
                        remarks:
                            remarks ||
                            null
                    })
            }
        );


        toast(
            action === "approve"
                ? "Application hired successfully."
                : "Application rejected successfully."
        );


        await Promise.all([
            loadApplications(),
            loadDashboard()
        ]);
    }


    /* =====================================================
       CATEGORIES
    ====================================================== */

    async function loadCategories() {

        const result =
            await api("/categories");

        const categories =
            result.categories || [];

        const grid =
            $("#categoryGrid");


        if (!categories.length) {

            grid.innerHTML = `
                <div class="panel">
                    <div class="empty-state">
                        <div class="empty-icon">
                            ▦
                        </div>
                        <h3>
                            No categories
                        </h3>
                    </div>
                </div>
            `;

            return;
        }


        grid.innerHTML =
            categories
                .map(
                    category => `
                        <article
                            class="agent-card"
                        >

                            <div
                                class="agent-card-header"
                            >

                                <div
                                    class="agent-identity"
                                >

                                    <div
                                        class="agent-avatar"
                                    >
                                        ${
                                            escapeHtml(
                                                category.icon ||
                                                "▦"
                                            )
                                        }
                                    </div>

                                    <div
                                        class="agent-name"
                                    >

                                        <strong>
                                            ${escapeHtml(
                                                category.name
                                            )}
                                        </strong>

                                        <span>
                                            ${escapeHtml(
                                                category.slug ||
                                                ""
                                            )}
                                        </span>

                                    </div>

                                </div>

                                ${statusBadge(
                                    category.is_active
                                        ? "active"
                                        : "inactive"
                                )}

                            </div>

                            <div
                                class="agent-details"
                            >

                                <div
                                    class="agent-detail"
                                >

                                    <span>
                                        ID
                                    </span>

                                    <strong>
                                        #${category.id}
                                    </strong>

                                </div>

                                <div
                                    class="agent-detail"
                                >

                                    <span>
                                        Status
                                    </span>

                                    <strong>
                                        ${
                                            category.is_active
                                                ? "Active"
                                                : "Inactive"
                                        }
                                    </strong>

                                </div>

                            </div>

                            <p
                                style="
                                    margin:14px 0 0;
                                    color:#667085;
                                    font-size:10px;
                                    line-height:1.6;
                                "
                            >
                                ${escapeHtml(
                                    category.description ||
                                    "No description available."
                                )}
                            </p>

                        </article>
                    `
                )
                .join("");
    }


    /* =====================================================
       AUDIT LOGS
    ====================================================== */

    async function loadAuditLogs(
        page = state.auditPage
    ) {

        state.auditPage =
            page;

        const result =
            await api(
                `/audit-logs?page=${page}&per_page=50`
            );

        const logs =
            result.logs || [];

        const body =
            $("#auditTableBody");


        if (!logs.length) {

            body.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="table-loading">
                            No audit logs found.
                        </div>
                    </td>
                </tr>
            `;

        } else {

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
                                    )}
                                    #${escapeHtml(
                                        log.resource_id
                                    )}
                                </td>

                                <td>

                                    ${
                                        log.new_status
                                            ? statusBadge(
                                                log.new_status
                                            )
                                            : "—"
                                    }

                                </td>

                                <td>
                                    #${escapeHtml(
                                        log.actor_id
                                    )}
                                </td>

                                <td>
                                    ${escapeHtml(
                                        log.ip_address ||
                                        "—"
                                    )}
                                </td>

                                <td>
                                    <code>
                                        ${escapeHtml(
                                            JSON.stringify(
                                                log.details || {}
                                            )
                                        )}
                                    </code>
                                </td>

                            </tr>
                        `
                    )
                    .join("");
        }


        renderPagination(
            $("#auditPagination"),
            result.pagination,
            loadAuditLogs
        );
    }


    /* =====================================================
       PAGINATION
    ====================================================== */

    function renderPagination(
        container,
        pagination,
        callback
    ) {

        if (!container || !pagination) {
            return;
        }

        const totalPages =
            pagination.pages || 1;

        const current =
            pagination.page || 1;


        if (totalPages <= 1) {

            container.innerHTML =
                "";

            return;
        }


        const buttons = [];


        if (pagination.has_prev) {

            buttons.push(`
                <button
                    class="page-button"
                    data-page="${current - 1}"
                >
                    ‹
                </button>
            `);
        }


        const start =
            Math.max(
                1,
                current - 2
            );

        const end =
            Math.min(
                totalPages,
                current + 2
            );


        for (
            let page = start;
            page <= end;
            page++
        ) {

            buttons.push(`
                <button
                    class="page-button ${
                        page === current
                            ? "active"
                            : ""
                    }"
                    data-page="${page}"
                >
                    ${page}
                </button>
            `);
        }


        if (pagination.has_next) {

            buttons.push(`
                <button
                    class="page-button"
                    data-page="${current + 1}"
                >
                    ›
                </button>
            `);
        }


        container.innerHTML =
            buttons.join("");


        container
            .querySelectorAll(
                "[data-page]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        callback(
                            Number(
                                button.dataset.page
                            )
                        );

                    }
                );

            });
    }


    /* =====================================================
       CONFIRMATION
    ====================================================== */

    function confirmAction({
        title,
        message,
        confirmText = "Confirm",
        type = "danger",
        callback
    }) {

        state.pendingConfirm =
            callback;

        $("#confirmTitle")
            .textContent = title;

        $("#confirmMessage")
            .textContent = message;

        const button =
            $("#confirmActionButton");

        button.textContent =
            confirmText;

        button.className =
            `btn ${
                type === "success"
                    ? "btn-success"
                    : "btn-danger"
            }`;

        $("#confirmModal")
            .classList.add("open");
    }


    /* =====================================================
       LOGOUT
    ====================================================== */

    async function logout() {

        try {

            await api(
                "/logout",
                {
                    method: "POST"
                }
            );

        } catch (_) {
            // Logout should continue
            // even if API response fails.
        }

        window.location.href =
            "/admin/login";
    }


    /* =====================================================
       EVENT DELEGATION
    ====================================================== */

    document.addEventListener(
        "click",
        async event => {

            const nav =
                event.target.closest(
                    "[data-section]"
                );

            if (
                nav &&
                nav.dataset.section
            ) {

                openSection(
                    nav.dataset.section
                );

                return;
            }


            const userStatus =
                event.target.closest(
                    "[data-user-status]"
                );

            if (userStatus) {

                const id =
                    Number(
                        userStatus.dataset.userStatus
                    );

                const active =
                    userStatus.dataset.active ===
                    "true";


                confirmAction({

                    title:
                        active
                            ? "Suspend user?"
                            : "Activate user?",

                    message:
                        active
                            ? "This account will no longer be able to use the platform."
                            : "This account will be restored and can use the platform again.",

                    confirmText:
                        active
                            ? "Suspend"
                            : "Activate",

                    type:
                        active
                            ? "danger"
                            : "success",

                    callback:
                        () =>
                            updateUserStatus(
                                id,
                                active
                            )

                });

                return;
            }


            const verify =
                event.target.closest(
                    "[data-user-verify]"
                );

            if (verify) {

                const id =
                    Number(
                        verify.dataset.userVerify
                    );

                confirmAction({

                    title:
                        "Verify user?",

                    message:
                        "The user will be marked as verified.",

                    confirmText:
                        "Verify",

                    type:
                        "success",

                    callback:
                        () =>
                            verifyUser(id)

                });

                return;
            }


            const agentToggle =
                event.target.closest(
                    "[data-agent-toggle]"
                );

            if (agentToggle) {

                const id =
                    Number(
                        agentToggle.dataset.agentToggle
                    );

                const active =
                    agentToggle.dataset.active ===
                    "true";

                confirmAction({

                    title:
                        active
                            ? "Suspend agent?"
                            : "Activate agent?",

                    message:
                        active
                            ? "The agent will lose access to the platform."
                            : "The agent will regain platform access.",

                    confirmText:
                        active
                            ? "Suspend"
                            : "Activate",

                    type:
                        active
                            ? "danger"
                            : "success",

                    callback:
                        () =>
                            toggleAgent(
                                id,
                                active
                            )

                });

                return;
            }


            const jobApproval =
                event.target.closest(
                    "[data-job-approval]"
                );

            if (jobApproval) {

                const id =
                    Number(
                        jobApproval.dataset.jobApproval
                    );

                const action =
                    jobApproval.dataset.action;

                confirmAction({

                    title:
                        action === "approve"
                            ? "Approve job?"
                            : "Reject job?",

                    message:
                        action === "approve"
                            ? "This job will be published as approved."
                            : "This job will be marked as rejected.",

                    confirmText:
                        action === "approve"
                            ? "Approve"
                            : "Reject",

                    type:
                        action === "approve"
                            ? "success"
                            : "danger",

                    callback:
                        () =>
                            updateJobApproval(
                                id,
                                action
                            )

                });

                return;
            }


            const jobDelete =
                event.target.closest(
                    "[data-job-delete]"
                );

            if (jobDelete) {

                const id =
                    Number(
                        jobDelete.dataset.jobDelete
                    );

                confirmAction({

                    title:
                        "Delete job?",

                    message:
                        "The job will be soft-deleted and removed from normal marketplace operations.",

                    confirmText:
                        "Delete Job",

                    type:
                        "danger",

                    callback:
                        () =>
                            deleteJob(id)

                });

                return;
            }


            const applicationApproval =
                event.target.closest(
                    "[data-application-approval]"
                );

            if (applicationApproval) {

                const id =
                    Number(
                        applicationApproval
                            .dataset
                            .applicationApproval
                    );

                const action =
                    applicationApproval
                        .dataset
                        .action;

                confirmAction({

                    title:
                        action === "approve"
                            ? "Hire applicant?"
                            : "Reject application?",

                    message:
                        action === "approve"
                            ? "The application will be marked as hired."
                            : "The application will be permanently moved to rejected status.",

                    confirmText:
                        action === "approve"
                            ? "Hire"
                            : "Reject",

                    type:
                        action === "approve"
                            ? "success"
                            : "danger",

                    callback:
                        () =>
                            updateApplicationApproval(
                                id,
                                action
                            )

                });

                return;
            }


            const close =
                event.target.closest(
                    "[data-close-modal]"
                );

            if (close) {

                closeModal(
                    close.dataset.closeModal
                );

                return;
            }


            const removeArea =
                event.target.closest(
                    ".area-remove"
                );

            if (removeArea) {

                removeArea
                    .closest(
                        ".area-form-card"
                    )
                    ?.remove();

                return;
            }

        }
    );


    /* =====================================================
       INITIALIZATION
    ====================================================== */

    function bindEvents() {

        /* Navigation */

        $$(".admin-nav-item")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () =>
                        openSection(
                            button.dataset.section
                        )
                );

            });


        /* Mobile */

        $("#mobileMenu")
            ?.addEventListener(
                "click",
                openMobileSidebar
            );

        $("#sidebarClose")
            ?.addEventListener(
                "click",
                closeMobileSidebar
            );

        $("#sidebarOverlay")
            ?.addEventListener(
                "click",
                closeMobileSidebar
            );


        /* Profile */

        $("#profileMenuButton")
            ?.addEventListener(
                "click",
                () =>
                    $("#profileDropdown")
                        .classList.toggle(
                            "open"
                        )
            );


        /* Logout */

        $("#logoutButton")
            ?.addEventListener(
                "click",
                () => {

                    confirmAction({

                        title:
                            "Sign out?",

                        message:
                            "Your administrator session will be closed.",

                        confirmText:
                            "Sign out",

                        type:
                            "danger",

                        callback:
                            logout

                    });

                }
            );


        /* Refresh */

        $("#refreshButton")
            ?.addEventListener(
                "click",
                () =>
                    loadSection(
                        state.currentSection
                    )
            );

        $("#dashboardRefresh")
            ?.addEventListener(
                "click",
                loadDashboard
            );


        /* Create Agent */

        $("#openCreateAgent")
            ?.addEventListener(
                "click",
                openAgentModal
            );

        $("#createAgentForm")
            ?.addEventListener(
                "submit",
                createAgent
            );

        $("#addAgentArea")
            ?.addEventListener(
                "click",
                addAreaForm
            );


        /* User search */

        $("#userSearch")
            ?.addEventListener(
                "input",
                event => {

                    state.userSearch =
                        event.target.value
                            .trim();

                    loadUsers(1);

                }
            );


        $("#reloadUsers")
            ?.addEventListener(
                "click",
                () => loadUsers(
                    state.usersPage
                )
            );


        /* Jobs */

        $("#reloadJobs")
            ?.addEventListener(
                "click",
                () =>
                    loadJobs(
                        state.jobsPage
                    )
            );


        $$("[data-job-status]")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        $$(
                            "[data-job-status]"
                        )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "active"
                                    )
                            );

                        button.classList.add(
                            "active"
                        );

                        state.jobsStatus =
                            button.dataset.jobStatus;

                        loadJobs(1);

                    }
                );

            });


        /* Applications */

        $("#applicationStatusFilter")
            ?.addEventListener(
                "change",
                () =>
                    loadApplications(1)
            );


        $("#reloadApplications")
            ?.addEventListener(
                "click",
                () =>
                    loadApplications(
                        state.applicationsPage
                    )
            );


        /* Confirm */

        $("#confirmActionButton")
            ?.addEventListener(
                "click",
                async () => {

                    const callback =
                        state.pendingConfirm;

                    state.pendingConfirm =
                        null;

                    closeModal(
                        "confirmModal"
                    );

                    if (!callback) {
                        return;
                    }

                    try {

                        await callback();

                    } catch (error) {

                        toast(
                            error.message,
                            "error"
                        );

                    }

                }
            );


        /* Escape */

        document.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Escape"
                ) {

                    $$(".modal-backdrop.open")
                        .forEach(
                            modal =>
                                closeModal(
                                    modal.id
                                )
                        );

                    closeMobileSidebar();
                }

            }
        );


        /* Close profile */

        document.addEventListener(
            "click",
            event => {

                const profile =
                    $(".admin-profile");

                if (
                    profile &&
                    !profile.contains(
                        event.target
                    )
                ) {

                    $("#profileDropdown")
                        ?.classList.remove(
                            "open"
                        );
                }

            }
        );

    }


    async function boot() {

        bindEvents();

        resetAreaForms();

        try {

            await loadAdmin();

            await loadDashboard();

        } catch (error) {

            toast(
                error.message,
                "error"
            );

            if (
                /401|administrator|unauthorized/i
                    .test(
                        error.message
                    )
            ) {

                window.location.href =
                    "/admin/login";
            }

        }

    }


    boot();

})();
