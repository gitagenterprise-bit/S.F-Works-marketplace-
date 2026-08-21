document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        // =====================================================
        // PAGE
        // =====================================================

        const page =
            document.getElementById(
                "jobsPage"
            );

        if (!page) {
            return;
        }


        // =====================================================
        // ELEMENTS
        // =====================================================

        const apiUrl =
            page.dataset.apiUrl ||
            "/api/jobs";

        const searchInput =
            document.getElementById(
                "jobSearch"
            );

        const cityInput =
            document.getElementById(
                "jobCity"
            );

        const categoryInput =
            document.getElementById(
                "jobCategory"
            );

        const sortInput =
            document.getElementById(
                "jobSort"
            );

        const searchButton =
            document.getElementById(
                "searchJobsBtn"
            );

        const clearSearchButton =
            document.getElementById(
                "clearSearchBtn"
            );

        const resetButton =
            document.getElementById(
                "resetJobsBtn"
            );

        const retryButton =
            document.getElementById(
                "retryJobsBtn"
            );

        const grid =
            document.getElementById(
                "jobsGrid"
            );

        const loading =
            document.getElementById(
                "jobsLoading"
            );

        const empty =
            document.getElementById(
                "jobsEmpty"
            );

        const errorBox =
            document.getElementById(
                "jobsError"
            );

        const errorMessage =
            document.getElementById(
                "jobsErrorMessage"
            );

        const resultText =
            document.getElementById(
                "jobsResultText"
            );

        const heroCount =
            document.getElementById(
                "heroJobCount"
            );

        const activeFilters =
            document.getElementById(
                "activeFilters"
            );


        // =====================================================
        // STATE
        // =====================================================

        let allJobs = [];

        let currentJobs = [];

        let currentPage = 1;

        const pageSize = 9;


        // =====================================================
        // HELPERS
        // =====================================================

        function escapeHtml(value) {

            const element =
                document.createElement(
                    "div"
                );

            element.textContent =
                value == null
                    ? ""
                    : String(value);

            return element.innerHTML;

        }


        function formatMoney(value) {

            if (
                value === null ||
                value === undefined ||
                value === ""
            ) {
                return null;
            }


            const number =
                Number(value);


            if (
                !Number.isFinite(number)
            ) {
                return null;
            }


            return new Intl.NumberFormat(
                "en-IN",
                {
                    maximumFractionDigits: 0
                }
            ).format(number);

        }


        function formatBudget(job) {

            const budget =
                job?.budget || {};


            const min =
                formatMoney(
                    budget.min
                );


            const max =
                formatMoney(
                    budget.max
                );


            if (
                min !== null &&
                max !== null
            ) {

                return `₹${min} – ₹${max}`;

            }


            if (min !== null) {

                return `From ₹${min}`;

            }


            if (max !== null) {

                return `Up to ₹${max}`;

            }


            if (
                job?.budget_min != null ||
                job?.budget_max != null
            ) {

                const legacyMin =
                    formatMoney(
                        job.budget_min
                    );

                const legacyMax =
                    formatMoney(
                        job.budget_max
                    );


                if (
                    legacyMin &&
                    legacyMax
                ) {

                    return `₹${legacyMin} – ₹${legacyMax}`;

                }


                if (legacyMin) {

                    return `From ₹${legacyMin}`;

                }


                if (legacyMax) {

                    return `Up to ₹${legacyMax}`;

                }

            }


            return "Budget not specified";

        }


        function formatDate(value) {

            if (!value) {
                return "Recently";
            }


            const date =
                new Date(value);


            if (
                Number.isNaN(
                    date.getTime()
                )
            ) {

                return "Recently";

            }


            return date.toLocaleDateString(
                "en-IN",
                {
                    day: "numeric",
                    month: "short",
                    year: "numeric"
                }
            );

        }


        function getCategory(job) {

            if (
                job?.category &&
                typeof job.category === "object"
            ) {

                return {
                    name:
                        job.category.name ||
                        "Other",

                    slug:
                        job.category.slug ||
                        job.category.name ||
                        "other",

                    icon:
                        job.category.icon ||
                        "✦"
                };

            }


            return {
                name:
                    job?.category_name ||
                    "Other",

                slug:
                    job?.category_slug ||
                    "other",

                icon:
                    job?.category_icon ||
                    "✦"
            };

        }


        function getLocation(job) {

            const parts = [

                job?.city,

                job?.state,

                job?.pincode

            ].filter(
                value =>
                    value !== null &&
                    value !== undefined &&
                    String(value).trim()
            );


            if (parts.length) {

                return parts.join(", ");

            }


            return (
                job?.location ||
                "Location not specified"
            );

        }


        // =====================================================
        // NORMALIZE API RESPONSE
        // =====================================================

        function normalizeResponse(data) {

            if (Array.isArray(data)) {

                return data;

            }


            if (
                Array.isArray(
                    data?.jobs
                )
            ) {

                return data.jobs;

            }


            if (
                Array.isArray(
                    data?.data
                )
            ) {

                return data.data;

            }


            if (
                Array.isArray(
                    data?.results
                )
            ) {

                return data.results;

            }


            if (
                Array.isArray(
                    data?.data?.jobs
                )
            ) {

                return data.data.jobs;

            }


            return [];

        }


        // =====================================================
        // RENDER CARD
        // =====================================================

        function createJobCard(job) {

            const category =
                getCategory(job);


            const status =
                String(
                    job?.status ||
                    "open"
                ).toLowerCase();


            const priority =
                String(
                    job?.priority ||
                    "normal"
                );


            const title =
                job?.title ||
                "Untitled Job";


            const description =
                job?.description ||
                "No description provided.";


            const views =
                Number(
                    job?.views || 0
                );


            const id =
                job?.id;


            const article =
                document.createElement(
                    "article"
                );


            article.className =
                "job-card";


            article.innerHTML = `

                <div class="job-card-top">

                    <div class="job-category-icon">
                        ${escapeHtml(
                            category.icon
                        )}
                    </div>

                    <div class="job-card-badges">

                        <span class="job-badge job-badge-category">
                            ${escapeHtml(
                                category.name
                            )}
                        </span>

                        <span class="job-badge job-badge-status ${status !== "open" ? "closed" : ""}">
                            ${escapeHtml(
                                job?.status ||
                                "Open"
                            )}
                        </span>

                    </div>

                </div>


                <h3>
                    ${escapeHtml(title)}
                </h3>


                <p class="job-description-preview">
                    ${escapeHtml(description)}
                </p>


                <div class="job-location">

                    <span class="job-location-icon">
                        📍
                    </span>

                    <span>
                        ${escapeHtml(
                            getLocation(job)
                        )}
                    </span>

                </div>


                <div class="job-card-bottom">

                    <div>

                        <span class="job-budget-label">
                            Estimated Budget
                        </span>

                        <strong class="job-budget">
                            ${escapeHtml(
                                formatBudget(job)
                            )}
                        </strong>

                        <div class="job-meta">

                            <span>
                                ${views} views
                            </span>

                            <span>
                                •
                            </span>

                            <span>
                                ${escapeHtml(
                                    formatDate(
                                        job?.created_at
                                    )
                                )}
                            </span>

                            <span>
                                •
                            </span>

                            <span>
                                ${escapeHtml(
                                    priority
                                )}
                            </span>

                        </div>

                    </div>


                    ${
                        id
                            ? `
                            <a
                                href="/jobs/${encodeURIComponent(id)}"
                                class="job-view-button"
                            >
                                View Job →
                            </a>
                            `
                            : ""
                    }

                </div>

            `;


            return article;

        }


        // =====================================================
        // RENDER JOBS
        // =====================================================

        function renderJobs(jobs) {

            currentJobs =
                Array.isArray(jobs)
                    ? jobs
                    : [];


            if (!grid) {
                return;
            }


            grid.innerHTML = "";


            if (
                currentJobs.length === 0
            ) {

                grid.hidden =
                    true;

                empty.hidden =
                    false;

                updateResultText(
                    0
                );

                return;

            }


            empty.hidden =
                true;

            grid.hidden =
                false;


            const start =
                (currentPage - 1) *
                pageSize;


            const end =
                start + pageSize;


            const visibleJobs =
                currentJobs.slice(
                    start,
                    end
                );


            visibleJobs.forEach(
                job => {

                    grid.appendChild(
                        createJobCard(
                            job
                        )
                    );

                }
            );


            updateResultText(
                currentJobs.length
            );


            updatePagination();

        }


        // =====================================================
        // SORT
        // =====================================================

        function sortJobs(jobs) {

            const sorted =
                [...jobs];


            const sort =
                sortInput?.value ||
                "newest";


            if (
                sort === "budget_high"
            ) {

                sorted.sort(
                    (a, b) => {

                        const aValue =
                            Number(
                                a?.budget?.max ??
                                a?.budget_max ??
                                0
                            );

                        const bValue =
                            Number(
                                b?.budget?.max ??
                                b?.budget_max ??
                                0
                            );

                        return bValue - aValue;

                    }
                );

            }


            else if (
                sort === "budget_low"
            ) {

                sorted.sort(
                    (a, b) => {

                        const aValue =
                            Number(
                                a?.budget?.min ??
                                a?.budget_min ??
                                0
                            );

                        const bValue =
                            Number(
                                b?.budget?.min ??
                                b?.budget_min ??
                                0
                            );

                        return aValue - bValue;

                    }
                );

            }


            else {

                sorted.sort(
                    (a, b) => {

                        const aDate =
                            new Date(
                                a?.created_at ||
                                0
                            ).getTime();

                        const bDate =
                            new Date(
                                b?.created_at ||
                                0
                            ).getTime();

                        return bDate - aDate;

                    }
                );

            }


            return sorted;

        }


        // =====================================================
        // FILTER
        // =====================================================

        function filterJobs() {

            const search =
                (
                    searchInput?.value ||
                    ""
                )
                .trim()
                .toLowerCase();


            const city =
                (
                    cityInput?.value ||
                    ""
                )
                .trim()
                .toLowerCase();


            const category =
                (
                    categoryInput?.value ||
                    ""
                )
                .trim()
                .toLowerCase();


            let filtered =
                allJobs.filter(
                    job => {

                        const jobCategory =
                            getCategory(job);


                        const searchable =
                            [
                                job?.title,
                                job?.description,
                                jobCategory.name,
                                jobCategory.slug,
                                job?.location,
                                job?.city,
                                job?.state
                            ]
                            .filter(Boolean)
                            .join(" ")
                            .toLowerCase();


                        const jobCity =
                            String(
                                job?.city ||
                                job?.location ||
                                ""
                            ).toLowerCase();


                        const matchesSearch =
                            !search ||
                            searchable.includes(
                                search
                            );


                        const matchesCity =
                            !city ||
                            jobCity.includes(
                                city
                            );


                        const matchesCategory =
                            !category ||
                            jobCategory.slug
                                .toLowerCase()
                                .includes(
                                    category
                                ) ||
                            jobCategory.name
                                .toLowerCase()
                                .includes(
                                    category
                                );


                        return (
                            matchesSearch &&
                            matchesCity &&
                            matchesCategory
                        );

                    }
                );


            filtered =
                sortJobs(
                    filtered
                );


            currentPage =
                1;


            renderJobs(
                filtered
            );


            renderActiveFilters();

        }


        // =====================================================
        // FILTER UI
        // =====================================================

        function renderActiveFilters() {

            if (!activeFilters) {
                return;
            }


            activeFilters.innerHTML =
                "";


            const filters = [];


            if (
                searchInput?.value.trim()
            ) {

                filters.push({
                    label:
                        `Search: ${searchInput.value.trim()}`,
                    type:
                        "search"
                });

            }


            if (
                cityInput?.value.trim()
            ) {

                filters.push({
                    label:
                        `City: ${cityInput.value.trim()}`,
                    type:
                        "city"
                });

            }


            if (
                categoryInput?.value
            ) {

                const option =
                    categoryInput.options[
                        categoryInput.selectedIndex
                    ];


                filters.push({
                    label:
                        `Category: ${option.textContent}`,
                    type:
                        "category"
                });

            }


            if (!filters.length) {

                activeFilters.hidden =
                    true;

                return;

            }


            activeFilters.hidden =
                false;


            filters.forEach(
                filter => {

                    const item =
                        document.createElement(
                            "div"
                        );

                    item.className =
                        "active-filter";


                    item.innerHTML = `

                        <span>
                            ${escapeHtml(
                                filter.label
                            )}
                        </span>

                        <button
                            type="button"
                            data-filter="${filter.type}"
                            aria-label="Remove filter"
                        >
                            ×
                        </button>

                    `;


                    activeFilters.appendChild(
                        item
                    );

                }
            );

        }


        // =====================================================
        // RESULT TEXT
        // =====================================================

        function updateResultText(
            count
        ) {

            if (!resultText) {
                return;
            }


            if (count === 0) {

                resultText.textContent =
                    "No matching jobs found.";

                return;

            }


            resultText.textContent =
                `${count} ${
                    count === 1
                        ? "opportunity"
                        : "opportunities"
                } available`;

        }


        // =====================================================
        // PAGINATION
        // =====================================================

        function updatePagination() {

            const pagination =
                document.getElementById(
                    "jobsPagination"
                );

            const previous =
                document.getElementById(
                    "jobsPrevBtn"
                );

            const next =
                document.getElementById(
                    "jobsNextBtn"
                );

            const info =
                document.getElementById(
                    "jobsPageInfo"
                );


            const totalPages =
                Math.max(
                    1,
                    Math.ceil(
                        currentJobs.length /
                        pageSize
                    )
                );


            if (
                currentJobs.length <=
                pageSize
            ) {

                pagination.hidden =
                    true;

                return;

            }


            pagination.hidden =
                false;


            previous.disabled =
                currentPage <= 1;


            next.disabled =
                currentPage >= totalPages;


            info.textContent =
                `Page ${currentPage} of ${totalPages}`;

        }


        // =====================================================
        // LOADING
        // =====================================================

        function showLoading() {

            loading.hidden =
                false;

            grid.hidden =
                true;

            empty.hidden =
                true;

            errorBox.hidden =
                true;

        }


        // =====================================================
        // ERROR
        // =====================================================

        function showError(
            message
        ) {

            loading.hidden =
                true;

            grid.hidden =
                true;

            empty.hidden =
                true;

            errorBox.hidden =
                false;


            if (errorMessage) {

                errorMessage.textContent =
                    message ||
                    "Unable to load jobs.";

            }

        }


        // =====================================================
        // LOAD JOBS
        // =====================================================

        async function loadJobs() {

            showLoading();


            try {

                const response =
                    await fetch(
                        apiUrl,
                        {
                            method:
                                "GET",

                            credentials:
                                "include",

                            headers: {
                                "Accept":
                                    "application/json"
                            },

                            cache:
                                "no-store"
                        }
                    );


                let data = null;


                try {

                    data =
                        await response.json();

                } catch {

                    data =
                        null;

                }


                if (!response.ok) {

                    throw new Error(
                        data?.message ||
                        `Unable to load jobs (${response.status}).`
                    );

                }


                if (
                    data &&
                    data.status &&
                    data.status !== "success"
                ) {

                    throw new Error(
                        data.message ||
                        "Invalid jobs response."
                    );

                }


                allJobs =
                    normalizeResponse(
                        data
                    );


                if (heroCount) {

                    heroCount.textContent =
                        allJobs.length;

                }


                filterJobs();

                loading.hidden =
                    true;


            } catch (error) {

                console.error(
                    "Jobs loading error:",
                    error
                );


                showError(
                    error.message
                );

            }

        }


        // =====================================================
        // RESET
        // =====================================================

        function resetFilters() {

            if (searchInput) {
                searchInput.value = "";
            }


            if (cityInput) {
                cityInput.value = "";
            }


            if (categoryInput) {
                categoryInput.value = "";
            }


            if (clearSearchButton) {

                clearSearchButton.hidden =
                    true;

            }


            document
                .querySelectorAll(
                    ".quick-filter"
                )
                .forEach(
                    button =>
                        button.classList.remove(
                            "active"
                        )
                );


            filterJobs();

        }


        // =====================================================
        // EVENTS
        // =====================================================

        searchButton?.addEventListener(
            "click",
            filterJobs
        );


        searchInput?.addEventListener(
            "input",
            () => {

                if (clearSearchButton) {

                    clearSearchButton.hidden =
                        !searchInput.value;

                }

            }
        );


        searchInput?.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    filterJobs();

                }

            }
        );


        cityInput?.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    filterJobs();

                }

            }
        );


        categoryInput?.addEventListener(
            "change",
            filterJobs
        );


        sortInput?.addEventListener(
            "change",
            filterJobs
        );


        clearSearchButton?.addEventListener(
            "click",
            () => {

                searchInput.value = "";

                clearSearchButton.hidden =
                    true;

                filterJobs();

            }
        );


        resetButton?.addEventListener(
            "click",
            resetFilters
        );


        retryButton?.addEventListener(
            "click",
            loadJobs
        );


        activeFilters?.addEventListener(
            "click",
            event => {

                const button =
                    event.target.closest(
                        "button[data-filter]"
                    );


                if (!button) {
                    return;
                }


                const type =
                    button.dataset.filter;


                if (
                    type === "search"
                ) {

                    searchInput.value = "";

                }


                if (
                    type === "city"
                ) {

                    cityInput.value = "";

                }


                if (
                    type === "category"
                ) {

                    categoryInput.value = "";

                }


                filterJobs();

            }
        );


        document
            .querySelectorAll(
                ".quick-filter"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const category =
                                button.dataset.category;


                            categoryInput.value =
                                category;


                            document
                                .querySelectorAll(
                                    ".quick-filter"
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


                            filterJobs();

                        }
                    );

                }
            );


        document
            .getElementById(
                "jobsPrevBtn"
            )
            ?.addEventListener(
                "click",
                () => {

                    if (
                        currentPage <= 1
                    ) {
                        return;
                    }


                    currentPage--;

                    renderJobs(
                        currentJobs
                    );

                    window.scrollTo({
                        top:
                            document
                                .querySelector(
                                    ".jobs-results-header"
                                )
                                ?.offsetTop ||
                            0,

                        behavior:
                            "smooth"
                    });

                }
            );


        document
            .getElementById(
                "jobsNextBtn"
            )
            ?.addEventListener(
                "click",
                () => {

                    const totalPages =
                        Math.ceil(
                            currentJobs.length /
                            pageSize
                        );


                    if (
                        currentPage >=
                        totalPages
                    ) {
                        return;
                    }


                    currentPage++;

                    renderJobs(
                        currentJobs
                    );

                    window.scrollTo({
                        top:
                            document
                                .querySelector(
                                    ".jobs-results-header"
                                )
                                ?.offsetTop ||
                            0,

                        behavior:
                            "smooth"
                    });

                }
            );


        // =====================================================
        // URL CATEGORY
        // =====================================================

        const params =
            new URLSearchParams(
                window.location.search
            );


        const urlCategory =
            params.get(
                "category"
            );


        if (
            urlCategory &&
            categoryInput
        ) {

            categoryInput.value =
                urlCategory;

        }


        // =====================================================
        // START
        // =====================================================

        loadJobs();

    }
);
