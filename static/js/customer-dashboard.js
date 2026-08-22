/* ============================================================
   CUSTOMER DASHBOARD
   S.F WORKS MARKETPLACE
============================================================ */

(function () {

    "use strict";


    /* ========================================================
       CONFIG
    ======================================================== */

    const API_BASE = "/api/customer";


    /* ========================================================
       DOM
    ======================================================== */

    const jobsList =
        document.getElementById("jobsList");

    const jobsLoading =
        document.getElementById("jobsLoading");

    const jobsEmpty =
        document.getElementById("jobsEmpty");

    const totalJobs =
        document.getElementById("totalJobs");

    const activeJobs =
        document.getElementById("activeJobs");

    const totalApplications =
        document.getElementById("totalApplications");

    const completedJobs =
        document.getElementById("completedJobs");

    const logoutBtn =
        document.getElementById("customerLogoutBtn");

    const menuBtn =
        document.getElementById("customerMenuBtn");

    const sidebar =
        document.getElementById("customerSidebar");

    const overlay =
        document.getElementById(
            "customerSidebarOverlay"
        );


    /* ========================================================
       HELPERS
    ======================================================== */

    function escapeHtml(value) {

        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function formatMoney(value) {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return "Budget not specified";
        }

        const number =
            Number(value);

        if (Number.isNaN(number)) {
            return "Budget not specified";
        }

        return new Intl.NumberFormat(
            "en-IN",
            {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 0
            }
        ).format(number);
    }


    function formatBudget(job) {

        const min =
            job.budget_min;

        const max =
            job.budget_max;


        if (
            min !== null &&
            min !== undefined &&
            max !== null &&
            max !== undefined
        ) {

            return `${formatMoney(min)} – ${formatMoney(max)}`;

        }


        if (
            min !== null &&
            min !== undefined
        ) {

            return `From ${formatMoney(min)}`;

        }


        if (
            max !== null &&
            max !== undefined
        ) {

            return `Up to ${formatMoney(max)}`;

        }


        return "Budget not specified";
    }


    function formatDate(value) {

        if (!value) {
            return "";
        }

        const date =
            new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        return date.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );
    }


    /* ========================================================
       API REQUEST
    ======================================================== */

    async function apiRequest(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                {
                    credentials: "include",
                    ...options,
                    headers: {
                        "Accept":
                            "application/json",

                        ...(options.headers || {})
                    }
                }
            );


        let data = null;

        try {

            data =
                await response.json();

        } catch (error) {

            data = null;

        }


        if (
            response.status === 401 ||
            response.status === 403
        ) {

            window.location.href =
                "/login";

            return null;
        }


        if (!response.ok) {

            const message =
                data?.message ||
                "Something went wrong.";

            throw new Error(message);
        }


        return data;
    }


    /* ========================================================
       LOAD JOBS
    ======================================================== */

    async function loadJobs() {

        if (!jobsList) {
            return;
        }


        jobsLoading.hidden = false;

        jobsEmpty.hidden = true;

        jobsList.innerHTML = "";


        try {

            const data =
                await apiRequest(
                    `${API_BASE}/jobs?page=1&per_page=10`
                );


            if (!data) {
                return;
            }


            const jobs =
                Array.isArray(data.jobs)
                    ? data.jobs
                    : [];


            const pagination =
                data.pagination || {};


            /* -----------------------------------------------
               Total jobs
            ------------------------------------------------ */

            totalJobs.textContent =
                pagination.total ??
                jobs.length;


            /* -----------------------------------------------
               Active jobs
            ------------------------------------------------ */

            const activeCount =
                jobs.filter(
                    job =>
                        String(
                            job.status || ""
                        ).toLowerCase() === "active"
                ).length;


            activeJobs.textContent =
                activeCount;


            /* -----------------------------------------------
               Completed jobs
            ------------------------------------------------ */

            const completedCount =
                jobs.filter(
                    job =>
                        String(
                            job.status || ""
                        ).toLowerCase() === "completed"
                ).length;


            completedJobs.textContent =
                completedCount;


            /* -----------------------------------------------
               Applications
               
               Current jobs API does not return application
               count, therefore keep it as —.
            ------------------------------------------------ */

            totalApplications.textContent =
                "—";


            jobsLoading.hidden = true;


            if (!jobs.length) {

                jobsEmpty.hidden = false;

                return;
            }


            renderJobs(jobs);


        } catch (error) {

            jobsLoading.hidden = true;

            jobsList.innerHTML = `
                <div class="applications-placeholder">

                    <div class="placeholder-icon">
                        !
                    </div>

                    <h3>
                        Unable to load jobs
                    </h3>

                    <p>
                        ${escapeHtml(
                            error.message ||
                            "Please try again."
                        )}
                    </p>

                    <button
                        type="button"
                        class="primary-action"
                        id="retryJobsBtn"
                    >
                        Try Again
                    </button>

                </div>
            `;


            const retry =
                document.getElementById(
                    "retryJobsBtn"
                );


            if (retry) {

                retry.addEventListener(
                    "click",
                    loadJobs
                );

            }

        }

    }


    /* ========================================================
       RENDER JOBS
    ======================================================== */

    function renderJobs(jobs) {

        jobsList.innerHTML =
            jobs.map(
                job => {

                    const location =
                        [
                            job.city,
                            job.state
                        ]
                        .filter(Boolean)
                        .join(", ");


                    const category =
                        job.category ||
                        "General";


                    return `
                        <article class="job-card">

                            <div class="job-card-main">

                                <h3 class="job-card-title">
                                    ${escapeHtml(
                                        job.title ||
                                        "Untitled Job"
                                    )}
                                </h3>


                                <div class="job-card-meta">

                                    <span>
                                        ${escapeHtml(
                                            category
                                        )}
                                    </span>

                                    ${
                                        location
                                        ? `
                                            <span>
                                                📍
                                                ${escapeHtml(
                                                    location
                                                )}
                                            </span>
                                        `
                                        : ""
                                    }

                                    <span>
                                        👁
                                        ${Number(
                                            job.views || 0
                                        )} views
                                    </span>

                                    <span>
                                        ${escapeHtml(
                                            formatDate(
                                                job.created_at
                                            )
                                        )}
                                    </span>

                                </div>


                                ${
                                    job.description
                                    ? `
                                        <p class="job-card-description">
                                            ${escapeHtml(
                                                job.description
                                            )}
                                        </p>
                                    `
                                    : ""
                                }

                            </div>


                            <div class="job-card-side">

                                <div class="job-budget">
                                    ${escapeHtml(
                                        formatBudget(job)
                                    )}
                                </div>


                                <span class="job-status">
                                    ${escapeHtml(
                                        job.status ||
                                        "unknown"
                                    )}
                                </span>

                            </div>

                        </article>
                    `;
                }
            )
            .join("");
    }


    /* ========================================================
       MOBILE SIDEBAR
    ======================================================== */

    function openSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.add("open");

        if (overlay) {
            overlay.hidden = false;
        }
    }


    function closeSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.remove("open");

        if (overlay) {
            overlay.hidden = true;
        }
    }


    if (menuBtn) {

        menuBtn.addEventListener(
            "click",
            openSidebar
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    document
        .querySelectorAll(
            ".customer-nav-item"
        )
        .forEach(
            item => {

                item.addEventListener(
                    "click",
                    closeSidebar
                );

            }
        );


    /* ========================================================
       LOGOUT
    ======================================================== */

    if (logoutBtn) {

        logoutBtn.addEventListener(
            "click",
            async function () {

                const confirmed =
                    window.confirm(
                        "Are you sure you want to logout?"
                    );


                if (!confirmed) {
                    return;
                }


                try {

                    const response =
                        await fetch(
                            "/api/auth/logout",
                            {
                                method: "POST",
                                credentials: "include",
                                headers: {
                                    "Accept":
                                        "application/json"
                                }
                            }
                        );


                    if (
                        response.ok ||
                        response.status === 401
                    ) {

                        window.location.href =
                            "/login";

                        return;
                    }


                    window.location.href =
                        "/login";


                } catch (error) {

                    window.location.href =
                        "/login";

                }

            }
        );

    }


    /* ========================================================
       INITIALIZE
    ======================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            loadJobs();

        }
    );

})();
