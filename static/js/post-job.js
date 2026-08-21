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


    if (!page || !form) {
        return;
    }


    const categoriesUrl =
        page.dataset.categoriesUrl;

    const createJobUrl =
        page.dataset.createJobUrl;


    let categories = [];

    let selectedCategory = null;


    // =========================================================
    // AUTH
    // =========================================================

    function getAccessToken() {

        const possibleKeys = [
            "access_token",
            "accessToken",
            "jwt_token",
            "token"
        ];

        for (const key of possibleKeys) {

            const value =
                localStorage.getItem(key);

            if (value) {
                return value;
            }
        }

        return null;
    }


    function buildHeaders() {

        const headers = {
            "Content-Type": "application/json"
        };

        const token =
            getAccessToken();

        if (token) {

            headers["Authorization"] =
                `Bearer ${token}`;

        }

        return headers;
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
    // LOADING
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
    // EMPTY
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
    // ERROR
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

            item.type = "button";

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

                    selectCategory(category);

                }
            );


            categoryList.appendChild(item);

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
    // OTHER
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


        selectCategory(other);

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


            const data =
                await response.json();


            if (
                !response.ok ||
                data.status !== "success"
            ) {

                throw new Error(
                    data.message ||
                    "Failed to load categories"
                );

            }


            categories =
                Array.isArray(
                    data.categories
                )
                    ? data.categories
                    : [];


            // -------------------------------------------------
            // OTHER MUST EXIST
            // -------------------------------------------------

            if (
                !categories.some(
                    category =>
                        category.slug === "other"
                )
            ) {

                throw new Error(
                    "Other category is missing"
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

        formMessage.textContent = "";

        formMessage.className =
            "form-message";

    }


    // =========================================================
    // VALIDATION
    // =========================================================

    function validateForm() {

        clearMessage();


        const title =
            document.getElementById(
                "jobTitle"
            ).value.trim();


        const descriptionValue =
            description.value.trim();


        const location =
            document.getElementById(
                "jobLocation"
            ).value.trim();


        const budgetMin =
            document.getElementById(
                "budgetMin"
            ).value;


        const budgetMax =
            document.getElementById(
                "budgetMax"
            ).value;


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


        if (!descriptionValue) {

            showMessage(
                "Please describe your job."
            );

            return false;

        }


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


        if (!location) {

            showMessage(
                "Please enter the work location."
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
    // SUBMIT
    // =========================================================

    async function submitJob(event) {

        event.preventDefault();


        if (!validateForm()) {
            return;
        }


        submitButton.disabled =
            true;


        submitButton.classList.add(
            "is-loading"
        );


        submitButton.querySelector(
            ".button-text"
        ).textContent =
            "Posting...";


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


        try {

            const response =
                await fetch(
                    createJobUrl,
                    {
                        method: "POST",

                        credentials: "include",

                        headers:
                            buildHeaders(),

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.message ||
                    "Unable to post job."
                );

            }


            showMessage(
                data.message ||
                "Job posted successfully!",
                "success"
            );


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


            setTimeout(() => {

                if (
                    data.job &&
                    data.job.id
                ) {

                    window.location.href =
                        `/jobs/${data.job.id}`;

                }

            }, 1200);


        } catch (error) {

            console.error(
                "Job submission error:",
                error
            );


            showMessage(
                error.message ||
                "Something went wrong. Please try again."
            );


        } finally {

            submitButton.disabled =
                false;

            submitButton.classList.remove(
                "is-loading"
            );

            submitButton.querySelector(
                ".button-text"
            ).textContent =
                "Post Job";

        }

    }


    // =========================================================
    // EVENTS
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


    categoryInput.addEventListener(
        "input",
        () => {

            // typing means previous selection
            // is no longer guaranteed

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


    categoryButton.addEventListener(
        "click",
        toggleCategoryDropdown
    );


    otherButton.addEventListener(
        "click",
        selectOther
    );


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


    document.addEventListener(
        "keydown",
        event => {

            if (event.key === "Escape") {

                closeCategoryDropdown();

            }

        }
    );


    description.addEventListener(
        "input",
        updateDescriptionCounter
    );


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
