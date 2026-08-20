/* ============================================================
   S. F WORKS
   PREMIUM POST JOB
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    const form = document.getElementById("postJobForm");

    if (!form) {
        return;
    }

    /* ========================================================
       ELEMENTS
    ======================================================== */

    const categoryInput =
        document.getElementById("jobCategory");

    const categoryPicker =
        document.getElementById("categoryPicker");

    const categoryDropdown =
        document.getElementById("categoryDropdown");

    const categoryDropdownButton =
        document.getElementById("categoryDropdownButton");

    const categoryList =
        document.getElementById("categoryList");

    const categoryCount =
        document.getElementById("categoryCount");

    const categoryStatus =
        document.getElementById("categoryStatus");

    const customCategoryButton =
        document.getElementById("customCategoryButton");

    const description =
        document.getElementById("jobDescription");

    const descriptionCounter =
        document.getElementById("descriptionCounter");

    const formMessage =
        document.getElementById("formMessage");

    const submitButton =
        document.getElementById("postJobButton");


    /* ========================================================
       STATE
    ======================================================== */

    let categories = [];

    let selectedCategoryId = null;

    let selectedCategoryName = "";

    let isCustomCategory = false;


    /* ========================================================
       HELPERS
    ======================================================== */

    function showMessage(message, type = "error") {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = message;

        formMessage.className =
            `form-message ${type}`;

    }


    function clearMessage() {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = "";

        formMessage.className =
            "form-message";

    }


    function showCategoryStatus(
        message,
        type = ""
    ) {

        if (!categoryStatus) {
            return;
        }

        categoryStatus.textContent =
            message;

        categoryStatus.className =
            `category-status ${type}`;

    }


    function openCategoryDropdown() {

        if (!categoryDropdown) {
            return;
        }

        categoryDropdown.classList.add(
            "is-open"
        );

    }


    function closeCategoryDropdown() {

        if (!categoryDropdown) {
            return;
        }

        categoryDropdown.classList.remove(
            "is-open"
        );

    }


    function clearCategorySelection() {

        selectedCategoryId = null;

        selectedCategoryName = "";

        isCustomCategory = false;

    }


    /* ========================================================
       LOAD CATEGORIES
       ======================================================== */

    async function loadCategories() {

        if (!categoryList) {
            return;
        }

        categoryList.innerHTML = `
            <div class="category-loading">
                <span class="loading-spinner"></span>
                Loading categories...
            </div>
        `;

        showCategoryStatus(
            "Loading categories..."
        );

        try {

            /*
             * IMPORTANT:
             *
             * Your Flask blueprint should be:
             *
             * /api/jobs/categories
             */

            const response = await fetch(
                "/api/jobs/categories",
                {
                    method: "GET",
                    headers: {
                        "Accept":
                            "application/json"
                    },
                    credentials: "same-origin"
                }
            );


            if (!response.ok) {

                throw new Error(
                    `Category API returned ${response.status}`
                );

            }


            const result =
                await response.json();


            if (
                result.status !== "success"
                ||
                !Array.isArray(
                    result.categories
                )
            ) {

                throw new Error(
                    "Invalid category response"
                );

            }


            categories =
                result.categories;


            categoryCount.textContent =
                categories.length;


            renderCategories(
                categories
            );


            showCategoryStatus(
                `${categories.length} categories available`,
                "success"
            );

        }

        catch (error) {

            console.error(
                "Category loading error:",
                error
            );


            categoryList.innerHTML = `
                <div class="category-empty">
                    <strong>
                        Unable to load categories
                    </strong>

                    <span>
                        Please refresh the page and try again.
                    </span>
                </div>
            `;


            categoryCount.textContent =
                "0";


            showCategoryStatus(
                "Could not load categories.",
                "error"
            );

        }

    }


    /* ========================================================
       RENDER CATEGORIES
       ======================================================== */

    function renderCategories(
        list
    ) {

        if (!categoryList) {
            return;
        }


        categoryList.innerHTML = "";


        if (!list.length) {

            categoryList.innerHTML = `
                <div class="category-empty">
                    <strong>
                        No categories found
                    </strong>

                    <span>
                        Try another search.
                    </span>
                </div>
            `;

            return;
        }


        list.forEach(category => {

            const button =
                document.createElement(
                    "button"
                );


            button.type = "button";

            button.className =
                "category-option";


            button.dataset.id =
                category.id;


            button.dataset.name =
                category.name;


            const icon =
                category.icon || "◈";


            button.innerHTML = `

                <span class="category-option-icon">
                    ${escapeHtml(icon)}
                </span>

                <span class="category-option-content">

                    <strong>
                        ${escapeHtml(category.name)}
                    </strong>

                    ${
                        category.description
                        ?
                        `<small>
                            ${escapeHtml(
                                category.description
                            )}
                        </small>`
                        :
                        ""
                    }

                </span>

                <span class="category-option-check">
                    ✓
                </span>

            `;


            button.addEventListener(
                "click",
                () => {

                    selectCategory(
                        category
                    );

                }
            );


            categoryList.appendChild(
                button
            );

        });

    }


    /* ========================================================
       SELECT CATEGORY
       ======================================================== */

    function selectCategory(
        category
    ) {

        selectedCategoryId =
            Number(category.id);

        selectedCategoryName =
            category.name;

        isCustomCategory =
            false;


        categoryInput.value =
            category.name;


        categoryInput.dataset.categoryId =
            category.id;


        categoryInput.dataset.categoryName =
            category.name;


        closeCategoryDropdown();


        showCategoryStatus(
            `Selected: ${category.name}`,
            "success"
        );

    }


    /* ========================================================
       SEARCH CATEGORY
       ======================================================== */

    function filterCategories(
        search
    ) {

        const query =
            search
                .trim()
                .toLowerCase();


        if (!query) {

            renderCategories(
                categories
            );

            return;

        }


        const filtered =
            categories.filter(
                category =>
                    category.name
                        .toLowerCase()
                        .includes(query)
                    ||
                    (
                        category.description
                        &&
                        category.description
                            .toLowerCase()
                            .includes(query)
                    )
            );


        renderCategories(
            filtered
        );


        categoryCount.textContent =
            filtered.length;

    }


    /* ========================================================
       CATEGORY INPUT
       ======================================================== */

    if (categoryInput) {

        categoryInput.addEventListener(
            "focus",
            () => {

                openCategoryDropdown();

            }
        );


        categoryInput.addEventListener(
            "input",
            () => {

                /*
                 * User is typing.
                 * Remove previous selected category.
                 */

                clearCategorySelection();


                categoryInput.removeAttribute(
                    "data-category-id"
                );


                categoryInput.removeAttribute(
                    "data-category-name"
                );


                const value =
                    categoryInput.value.trim();


                if (value) {

                    isCustomCategory =
                        true;

                    showCategoryStatus(
                        "Custom category entered. Please select an existing category.",
                        "warning"
                    );

                }
                else {

                    isCustomCategory =
                        false;

                    showCategoryStatus(
                        ""
                    );

                }


                openCategoryDropdown();


                filterCategories(
                    value
                );

            }
        );

    }


    /* ========================================================
       DROPDOWN BUTTON
       ======================================================== */

    if (categoryDropdownButton) {

        categoryDropdownButton.addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();


                if (
                    categoryDropdown
                    &&
                    categoryDropdown.classList.contains(
                        "is-open"
                    )
                ) {

                    closeCategoryDropdown();

                }
                else {

                    openCategoryDropdown();

                    if (categoryInput) {

                        categoryInput.focus();

                    }

                }

            }
        );

    }


    /* ========================================================
       CUSTOM CATEGORY
       ======================================================== */

    if (customCategoryButton) {

        customCategoryButton.addEventListener(
            "click",
            event => {

                event.preventDefault();

                closeCategoryDropdown();


                clearCategorySelection();


                isCustomCategory =
                    true;


                categoryInput.value = "";


                categoryInput.removeAttribute(
                    "data-category-id"
                );


                categoryInput.removeAttribute(
                    "data-category-name"
                );


                categoryInput.focus();


                showCategoryStatus(
                    "You can type a category, but an existing marketplace category must be selected to post this job.",
                    "warning"
                );

            }
        );

    }


    /* ========================================================
       CLOSE DROPDOWN OUTSIDE
       ======================================================== */

    document.addEventListener(
        "click",
        event => {

            if (
                categoryPicker
                &&
                !categoryPicker.contains(
                    event.target
                )
            ) {

                closeCategoryDropdown();

            }

        }
    );


    /* ========================================================
       DESCRIPTION COUNTER
       ======================================================== */

    if (
        description
        &&
        descriptionCounter
    ) {

        function updateCounter() {

            const length =
                description.value.length;


            descriptionCounter.textContent =
                `${length} / 5000`;

        }


        description.addEventListener(
            "input",
            updateCounter
        );


        updateCounter();

    }


    /* ========================================================
       FORM SUBMIT
       ======================================================== */

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            clearMessage();


            const title =
                document
                    .getElementById("jobTitle")
                    ?.value
                    .trim();


            const jobDescription =
                description
                    ?.value
                    .trim();


            const location =
                document
                    .getElementById("jobLocation")
                    ?.value
                    .trim();


            const city =
                document
                    .getElementById("jobCity")
                    ?.value
                    .trim();


            const state =
                document
                    .getElementById("jobState")
                    ?.value
                    .trim();


            const pincode =
                document
                    .getElementById("jobPincode")
                    ?.value
                    .trim();


            const budgetMin =
                document
                    .getElementById("budgetMin")
                    ?.value;


            const budgetMax =
                document
                    .getElementById("budgetMax")
                    ?.value;


            const priority =
                document
                    .getElementById("jobPriority")
                    ?.value
                || "normal";


            /* ---------------------------------------------
               VALIDATION
            --------------------------------------------- */

            if (!title) {

                showMessage(
                    "Please enter a job title."
                );

                return;

            }


            if (!jobDescription) {

                showMessage(
                    "Please describe the job."
                );

                return;

            }


            if (!selectedCategoryId) {

                showMessage(
                    "Please select a category from the category list."
                );

                openCategoryDropdown();

                return;

            }


            if (!location) {

                showMessage(
                    "Please enter the work location."
                );

                return;

            }


            if (
                budgetMin
                &&
                budgetMax
                &&
                Number(budgetMin)
                    >
                Number(budgetMax)
            ) {

                showMessage(
                    "Minimum budget cannot exceed maximum budget."
                );

                return;

            }


            /* ---------------------------------------------
               PAYLOAD
            --------------------------------------------- */

            const payload = {

                title,

                description:
                    jobDescription,

                category_id:
                    selectedCategoryId,

                budget_min:
                    budgetMin
                    ?
                    Number(budgetMin)
                    :
                    null,

                budget_max:
                    budgetMax
                    ?
                    Number(budgetMax)
                    :
                    null,

                location,

                city:
                    city || null,

                state:
                    state || null,

                pincode:
                    pincode || null,

                priority

            };


            /* ---------------------------------------------
               BUTTON LOADING
            --------------------------------------------- */

            const originalText =
                submitButton
                    ?.querySelector(
                        ".button-text"
                    )
                    ?.textContent;


            if (submitButton) {

                submitButton.disabled =
                    true;


                const buttonText =
                    submitButton.querySelector(
                        ".button-text"
                    );


                if (buttonText) {

                    buttonText.textContent =
                        "Posting...";

                }

            }


            try {

                /*
                 * IMPORTANT:
                 *
                 * Backend route:
                 * POST /api/jobs/create
                 */

                const response =
                    await fetch(
                        "/api/jobs/create",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );


                const result =
                    await response.json()
                        .catch(
                            () => ({})
                        );


                if (!response.ok) {

                    throw new Error(
                        result.message
                        ||
                        `Unable to post job (${response.status})`
                    );

                }


                showMessage(
                    result.message
                    ||
                    "Job posted successfully!",
                    "success"
                );


                /*
                 * Redirect after successful creation
                 */

                if (
                    result.job
                    &&
                    result.job.id
                ) {

                    setTimeout(
                        () => {

                            window.location.href =
                                `/jobs/${result.job.id}`;

                        },
                        900
                    );

                }


            }

            catch (error) {

                console.error(
                    "Post job error:",
                    error
                );


                showMessage(
                    error.message
                    ||
                    "Something went wrong. Please try again."
                );

            }

            finally {

                if (submitButton) {

                    submitButton.disabled =
                        false;


                    const buttonText =
                        submitButton.querySelector(
                            ".button-text"
                        );


                    if (buttonText) {

                        buttonText.textContent =
                            originalText
                            ||
                            "Post Job";

                    }

                }

            }

        }
    );


    /* ========================================================
       HTML ESCAPE
       ======================================================== */

    function escapeHtml(
        value
    ) {

        return String(value)
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


    /* ========================================================
       START
       ======================================================== */

    loadCategories();

});
