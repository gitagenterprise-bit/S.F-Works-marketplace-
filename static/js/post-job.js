document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    // =========================================================
    // ELEMENTS
    // =========================================================

    const page =
        document.getElementById("postJobPage");

    const form =
        document.getElementById("postJobForm");

    const categoryInput =
        document.getElementById("jobCategory");

    const categoryIdInput =
        document.getElementById("jobCategoryId");

    const categoryDropdown =
        document.getElementById("categoryDropdown");

    const categoryList =
        document.getElementById("categoryList");

    const categoryButton =
        document.getElementById("categoryDropdownButton");

    const categoryCount =
        document.getElementById("categoryCount");

    const categoryStatus =
        document.getElementById("categoryStatus");

    const otherButton =
        document.getElementById("otherCategoryButton");

    const description =
        document.getElementById("jobDescription");

    const descriptionCounter =
        document.getElementById("descriptionCounter");

    const formMessage =
        document.getElementById("formMessage");

    const submitButton =
        document.getElementById("postJobButton");


    // =========================================================
    // SAFETY CHECK
    // =========================================================

    if (!page || !form) {
        return;
    }


    // =========================================================
    // URLS
    // =========================================================

    const categoriesUrl =
        page.dataset.categoriesUrl;

    const createJobUrl =
        page.dataset.createJobUrl;


    let categories = [];

    let selectedCategory = null;


    // =========================================================
    // AUTHENTICATED REQUEST
    //
    // JWT IS STORED IN HTTPONLY COOKIE
    //
    // Access Cookie:
    //     15 minutes
    //
    // Refresh Cookie:
    //     30 days
    //
    // Flow:
    //
    // Request
    //   ↓
    // 401?
    //   ↓
    // /api/auth/refresh
    //   ↓
    // New Access Cookie
    //   ↓
    // Request again
    // =========================================================

    async function apiRequest(
        url,
        options = {},
        retryAfterRefresh = true
    ) {

        const requestOptions = {
            ...options,

            credentials: "include",

            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        };


        let response;


        try {

            response =
                await fetch(
                    url,
                    requestOptions
                );

        } catch (error) {

            console.error(
                "API request failed:",
                error
            );

            throw new Error(
                "Unable to connect to the server. Please check your internet connection."
            );

        }


        // =====================================================
        // ACCESS TOKEN EXPIRED / MISSING
        // =====================================================

        if (
            response.status === 401 &&
            retryAfterRefresh
        ) {

            let refreshResponse;


            try {

                refreshResponse =
                    await fetch(
                        "/api/auth/refresh",
                        {
                            method: "POST",

                            credentials: "include",

                            headers: {
                                "Accept":
                                    "application/json"
                            }
                        }
                    );

            } catch (error) {

                console.error(
                    "Refresh request failed:",
                    error
                );

                return response;

            }


            // =================================================
            // REFRESH SUCCESS
            // =================================================

            if (refreshResponse.ok) {

                /*
                 * Server has now issued a new
                 * Access JWT Cookie.
                 *
                 * Browser automatically stores
                 * the HttpOnly cookie.
                 *
                 * Retry original request once.
                 */

                try {

                    response =
                        await fetch(
                            url,
                            requestOptions
                        );

                } catch (error) {

                    console.error(
                        "Retry request failed:",
                        error
                    );

                    throw new Error(
                        "Unable to connect to the server."
                    );

                }

            }

        }


        return response;
    }


    // =========================================================
    // CATEGORY STATUS
    // =========================================================

    function setCategoryStatus(
        message = "",
        type = ""
    ) {

        if (!categoryStatus) {
            return;
        }


        categoryStatus.textContent =
            message;


        categoryStatus.className =
            "category-status";


        if (type) {

            categoryStatus.classList.add(
                `is-${type}`
            );

        }

    }


    // =========================================================
    // DROPDOWN
    // =========================================================

    function openCategoryDropdown() {

        categoryDropdown.classList.add(
            "is-open"
        );


        categoryDropdown.setAttribute(
            "aria-hidden",
            "false"
        );


        categoryInput.setAttribute(
            "aria-expanded",
            "true"
        );


        categoryButton.setAttribute(
            "aria-expanded",
            "true"
        );

    }


    function closeCategoryDropdown() {

        categoryDropdown.classList.remove(
            "is-open"
        );


        categoryDropdown.setAttribute(
            "aria-hidden",
            "true"
        );


        categoryInput.setAttribute(
            "aria-expanded",
            "false"
        );


        categoryButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }


    function toggleCategoryDropdown() {

        if (
            categoryDropdown.classList.contains(
                "is-open"
            )
        ) {

            closeCategoryDropdown();

        } else {

            openCategoryDropdown();

            renderCategories(
                categoryInput.value
            );

        }

    }


    // =========================================================
    // CATEGORY LOADING
    // =========================================================

    function showCategoryLoading() {

        categoryList.innerHTML = `

            <div class="category-loading">

                <span class="category-spinner"></span>

                <strong>
                    Loading categories...
                </strong>

                <small>
                    Please wait
                </small>

            </div>

        `;

    }


    // =========================================================
    // CATEGORY EMPTY
    // =========================================================

    function showCategoryEmpty() {

        categoryList.innerHTML = `

            <div class="category-empty">

                <div class="empty-icon">
                    ◌
                </div>

                <strong>
                    No category found
                </strong>

                <small>
                    Try another search or choose Other.
                </small>

            </div>

        `;

    }


    // =========================================================
    // CATEGORY ERROR
    // =========================================================

    function showCategoryError() {

        categoryList.innerHTML = `

            <div class="category-empty category-error">

                <div class="empty-icon">
                    !
                </div>

                <strong>
                    Unable to load categories
                </strong>

                <small>
                    Please refresh the page and try again.
                </small>

                <button
                    type="button"
                    id="retryCategories"
                    class="retry-category-button"
                >
                    Try Again
                </button>

            </div>

        `;


        const retry =
            document.getElementById(
                "retryCategories"
            );


        if (retry) {

            retry.addEventListener(
                "click",
                loadCategories
            );

        }

    }


    // =========================================================
    // CATEGORY ICON
    // =========================================================

    function safeIcon(icon) {

        if (!icon) {
            return "✦";
        }

        return icon;
    }


    // =========================================================
    // ESCAPE HTML
    // =========================================================

    function escapeHtml(value) {

        const div =
            document.createElement("div");


        div.textContent =
            value == null
                ? ""
                : String(value);


        return div.innerHTML;

    }


    // =========================================================
    // RENDER CATEGORIES
    // =========================================================

    function renderCategories(
        searchTerm = ""
    ) {

        const term =
            searchTerm
                .trim()
                .toLowerCase();


        const filtered =
            categories.filter(category => {

                if (!term) {
                    return true;
                }


                return (

                    category.name
                        .toLowerCase()
                        .includes(term)

                    ||

                    (category.description || "")
                        .toLowerCase()
                        .includes(term)

                );

            });


        categoryCount.textContent =
            filtered.length;


        if (!filtered.length) {

            showCategoryEmpty();

            return;

        }


        categoryList.innerHTML = "";


        filtered.forEach(category => {

            const item =
                document.createElement("button");


            item.type =
                "button";


            item.className =
                "category-option";


            item.setAttribute(
                "role",
                "option"
            );


            item.dataset.categoryId =
                category.id;


            if (
                selectedCategory &&
                Number(selectedCategory.id) ===
                Number(category.id)
            ) {

                item.classList.add(
                    "is-selected"
                );

            }


            item.innerHTML = `

                <span class="category-option-icon">
                    ${safeIcon(category.icon)}
                </span>

                <span class="category-option-content">

                    <strong>
                        ${escapeHtml(category.name)}
                    </strong>

                    <small>
                        ${escapeHtml(
                            category.description || ""
                        )}
                    </small>

                </span>

                <span class="category-option-check">
                    ✓
                </span>

            `;


            item.addEventListener(
                "click",
                () => {

                    selectCategory(
                        category
                    );

                }
            );


            categoryList.appendChild(
                item
            );

        });

    }


    // =========================================================
    // SELECT CATEGORY
    // =========================================================

    function selectCategory(category) {

        selectedCategory =
            category;


        categoryInput.value =
            category.name;


        categoryIdInput.value =
            category.id;


        setCategoryStatus(
            `Selected: ${category.name}`,
            "success"
        );


        categoryInput.classList.add(
            "has-selection"
        );


        closeCategoryDropdown();


        renderCategories();

    }


    // =========================================================
    // OTHER CATEGORY
    // =========================================================

    function selectOther() {

        const other =
            categories.find(
                category =>
                    category.slug === "other"
            );


        if (!other) {

            setCategoryStatus(
                "Other category is unavailable.",
                "error"
            );

            return;

        }


        selectCategory(
            other
        );

    }


    // =========================================================
    // LOAD CATEGORIES
    // =========================================================

    async function loadCategories() {

        showCategoryLoading();


        setCategoryStatus(
            "Loading categories..."
        );


        try {

            const response =
                await fetch(
                    categoriesUrl,
                    {
                        method: "GET",

                        credentials: "include",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        cache: "no-store"
                    }
                );


            let data = {};


            try {

                data =
                    await response.json();

            } catch (error) {

                throw new Error(
                    "Invalid server response."
                );

            }


            if (
                !response.ok ||
                data.status !== "success"
            ) {

                throw new Error(
                    data.message ||
                    "Failed to load categories."
                );

            }


            categories =
                Array.isArray(
                    data.categories
                )
                    ? data.categories
                    : [];


            // =================================================
            // OTHER MUST EXIST
            // =================================================

            if (
                !categories.some(
                    category =>
                        category.slug === "other"
                )
            ) {

                throw new Error(
                    "Other category is missing."
                );

            }


            renderCategories();


            setCategoryStatus(
                `${categories.length} categories available`,
                "success"
            );


        } catch (error) {

            console.error(
                "Category loading error:",
                error
            );


            categories = [];


            showCategoryError();


            setCategoryStatus(
                "Could not load categories.",
                "error"
            );

        }

    }


    // =========================================================
    // DESCRIPTION COUNTER
    // =========================================================

    function updateDescriptionCounter() {

        if (!description) {
            return;
        }


        const length =
            description.value.length;


        descriptionCounter.textContent =
            `${length} / 5000`;

    }


    // =========================================================
    // FORM MESSAGE
    // =========================================================

    function showMessage(
        message,
        type = "error"
    ) {

        formMessage.textContent =
            message;


        formMessage.className =
            `form-message is-${type}`;


        formMessage.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    }


    function clearMessage() {

        formMessage.textContent =
            "";


        formMessage.className =
            "form-message";

    }


    // =========================================================
    // VALIDATION
    // =========================================================

    function validateForm() {

        clearMessage();


        const title =
            document
                .getElementById("jobTitle")
                .value
                .trim();


        const descriptionValue =
            description.value.trim();


        const location =
            document
                .getElementById("jobLocation")
                .value
                .trim();


        const budgetMin =
            document
                .getElementById("budgetMin")
                .value;


        const budgetMax =
            document
                .getElementById("budgetMax")
                .value;


        // -----------------------------------------------------
        // TITLE
        // -----------------------------------------------------

        if (!title) {

            showMessage(
                "Please enter a job title."
            );

            return false;

        }


        if (title.length < 3) {

            showMessage(
                "Job title must contain at least 3 characters."
            );

            return false;

        }


        if (title.length > 200) {

            showMessage(
                "Job title cannot exceed 200 characters."
            );

            return false;

        }


        // -----------------------------------------------------
        // DESCRIPTION
        // -----------------------------------------------------

        if (!descriptionValue) {

            showMessage(
                "Please describe your job."
            );

            return false;

        }


        if (descriptionValue.length < 10) {

            showMessage(
                "Please provide a little more detail about the job."
            );

            return false;

        }


        if (descriptionValue.length > 5000) {

            showMessage(
                "Job description cannot exceed 5000 characters."
            );

            return false;

        }


        // -----------------------------------------------------
        // CATEGORY
        // -----------------------------------------------------

        if (
            !categoryIdInput.value ||
            !selectedCategory
        ) {

            showMessage(
                "Please select a category."
            );


            categoryInput.focus();


            return false;

        }


        // -----------------------------------------------------
        // LOCATION
        // -----------------------------------------------------

        if (!location) {

            showMessage(
                "Please enter the work location."
            );

            return false;

        }


        // -----------------------------------------------------
        // BUDGET
        // -----------------------------------------------------

        if (
            budgetMin !== "" &&
            Number(budgetMin) < 0
        ) {

            showMessage(
                "Minimum budget cannot be negative."
            );

            return false;

        }


        if (
            budgetMax !== "" &&
            Number(budgetMax) < 0
        ) {

            showMessage(
                "Maximum budget cannot be negative."
            );

            return false;

        }


        if (
            budgetMin !== "" &&
            budgetMax !== "" &&
            Number(budgetMin) >
            Number(budgetMax)
        ) {

            showMessage(
                "Minimum budget cannot exceed maximum budget."
            );

            return false;

        }


        return true;

    }


    // =========================================================
    // SUBMIT JOB
    // =========================================================

    async function submitJob(event) {

        event.preventDefault();


        // -----------------------------------------------------
        // CLIENT VALIDATION
        // -----------------------------------------------------

        if (!validateForm()) {
            return;
        }


        // -----------------------------------------------------
        // DISABLE BUTTON
        // -----------------------------------------------------

        submitButton.disabled =
            true;


        submitButton.classList.add(
            "is-loading"
        );


        const buttonText =
            submitButton.querySelector(
                ".button-text"
            );


        if (buttonText) {

            buttonText.textContent =
                "Posting...";

        }


        // -----------------------------------------------------
        // PAYLOAD
        // -----------------------------------------------------

        const payload = {

            title:
                document
                    .getElementById("jobTitle")
                    .value
                    .trim(),


            description:
                description
                    .value
                    .trim(),


            category_id:
                Number(
                    categoryIdInput.value
                ),


            budget_min:
                document
                    .getElementById("budgetMin")
                    .value !== ""
                    ? Number(
                        document
                            .getElementById("budgetMin")
                            .value
                    )
                    : null,


            budget_max:
                document
                    .getElementById("budgetMax")
                    .value !== ""
                    ? Number(
                        document
                            .getElementById("budgetMax")
                            .value
                    )
                    : null,


            location:
                document
                    .getElementById("jobLocation")
                    .value
                    .trim(),


            city:
                document
                    .getElementById("jobCity")
                    .value
                    .trim(),


            state:
                document
                    .getElementById("jobState")
                    .value
                    .trim(),


            pincode:
                document
                    .getElementById("jobPincode")
                    .value
                    .trim(),


            priority:
                document
                    .getElementById("jobPriority")
                    .value

        };


        // =====================================================
        // API REQUEST
        //
        // IMPORTANT:
        //
        // No Authorization header.
        //
        // JWT is HttpOnly Cookie.
        //
        // apiRequest() handles:
        //
        // Access valid
        //      ↓
        // Create Job
        //
        // Access expired
        //      ↓
        // 401
        //      ↓
        // Refresh
        //      ↓
        // New Access Cookie
        //      ↓
        // Create Job again
        // =====================================================

        try {

            const response =
                await apiRequest(
                    createJobUrl,
                    {
                        method: "POST",

                        body:
                            JSON.stringify(
                                payload
                            )
                    },
                    true
                );


            // -------------------------------------------------
            // READ RESPONSE SAFELY
            // -------------------------------------------------

            let data = {};


            try {

                data =
                    await response.json();

            } catch (error) {

                console.warn(
                    "Server returned non-JSON response."
                );

            }


            // =================================================
            // NOT AUTHENTICATED
            // =================================================

            if (
                response.status === 401
            ) {

                showMessage(
                    "Please sign up or login to create a job post.",
                    "error"
                );


                setTimeout(() => {

                    const goLogin =
                        confirm(
                            "You need to login or sign up before posting a job.\n\nOK = Login\nCancel = Stay here"
                        );


                    if (goLogin) {

                        window.location.href =
                            "/login";

                    }

                }, 100);


                return;

            }


            // =================================================
            // FORBIDDEN
            // =================================================

            if (
                response.status === 403
            ) {

                throw new Error(
                    data.message ||
                    "You do not have permission to post a job."
                );

            }


            // =================================================
            // OTHER HTTP ERRORS
            // =================================================

            if (!response.ok) {

                throw new Error(
                    data.message ||
                    "Unable to post job."
                );

            }


            // =================================================
            // SUCCESS
            // =================================================

            showMessage(
                data.message ||
                "Job posted successfully!",
                "success"
            );


            // -------------------------------------------------
            // RESET FORM
            // -------------------------------------------------

            form.reset();


            categoryIdInput.value =
                "";


            categoryInput.classList.remove(
                "has-selection"
            );


            selectedCategory =
                null;


            setCategoryStatus(
                "Job posted successfully.",
                "success"
            );


            updateDescriptionCounter();


            // =================================================
            // REDIRECT TO JOB
            // =================================================

            if (
                data.job &&
                data.job.id
            ) {

                setTimeout(() => {

                    window.location.href =
                        `/jobs/${encodeURIComponent(
                            data.job.id
                        )}`;

                }, 1200);

            }


        } catch (error) {

            console.error(
                "Job submission error:",
                error
            );


            showMessage(
                error.message ||
                "Something went wrong. Please try again.",
                "error"
            );


        } finally {

            submitButton.disabled =
                false;


            submitButton.classList.remove(
                "is-loading"
            );


            if (buttonText) {

                buttonText.textContent =
                    "Post Job";

            }

        }

    }


    // =========================================================
    // CATEGORY INPUT — FOCUS
    // =========================================================

    categoryInput.addEventListener(
        "focus",
        () => {

            openCategoryDropdown();


            renderCategories(
                categoryInput.value
            );

        }
    );


    // =========================================================
    // CATEGORY INPUT — SEARCH
    // =========================================================

    categoryInput.addEventListener(
        "input",
        () => {

            /*
             * If user changes the category text manually,
             * the previous category ID is no longer trusted.
             */

            if (
                selectedCategory &&
                categoryInput.value !==
                selectedCategory.name
            ) {

                selectedCategory =
                    null;


                categoryIdInput.value =
                    "";


                categoryInput.classList.remove(
                    "has-selection"
                );


                setCategoryStatus(
                    "Please select a category from the list."
                );

            }


            openCategoryDropdown();


            renderCategories(
                categoryInput.value
            );

        }
    );


    // =========================================================
    // CATEGORY BUTTON
    // =========================================================

    categoryButton.addEventListener(
        "click",
        toggleCategoryDropdown
    );


    // =========================================================
    // OTHER BUTTON
    // =========================================================

    otherButton.addEventListener(
        "click",
        selectOther
    );


    // =========================================================
    // CLOSE DROPDOWN OUTSIDE
    // =========================================================

    document.addEventListener(
        "click",
        event => {

            if (
                !event.target.closest(
                    "#categoryPicker"
                )
            ) {

                closeCategoryDropdown();

            }

        }
    );


    // =========================================================
    // ESC KEY
    // =========================================================

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                closeCategoryDropdown();

            }

        }
    );


    // =========================================================
    // DESCRIPTION COUNTER
    // =========================================================

    description.addEventListener(
        "input",
        updateDescriptionCounter
    );


    // =========================================================
    // FORM SUBMIT
    // =========================================================

    form.addEventListener(
        "submit",
        submitJob
    );


    // =========================================================
    // INITIALIZE
    // =========================================================

    updateDescriptionCounter();

    loadCategories();

});
