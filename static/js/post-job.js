document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    // =========================================================
    // ELEMENTS
    // =========================================================

    const form = document.getElementById("postJobForm");

    const categoryPicker =
        document.getElementById("categoryPicker");

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

    const customCategoryButton =
        document.getElementById("customCategoryButton");

    const formMessage =
        document.getElementById("formMessage");

    const postJobButton =
        document.getElementById("postJobButton");

    const description =
        document.getElementById("jobDescription");

    const descriptionCounter =
        document.getElementById("descriptionCounter");


    // =========================================================
    // STATE
    // =========================================================

    let categories = [];

    let selectedCategory = null;

    let categoriesLoaded = false;

    let isLoadingCategories = false;


    // =========================================================
    // CATEGORY STATUS
    // =========================================================

    function setCategoryStatus(message, type = "") {

        if (!categoryStatus) return;

        categoryStatus.textContent = message;

        categoryStatus.className =
            `category-status ${type}`.trim();
    }


    // =========================================================
    // OPEN DROPDOWN
    // =========================================================

    function openCategoryDropdown() {

        if (!categoryPicker || !categoryDropdown) {
            return;
        }

        categoryPicker.classList.add("is-open");

        categoryDropdown.setAttribute(
            "aria-hidden",
            "false"
        );

        if (categoryInput) {

            categoryInput.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        if (categoryButton) {

            categoryButton.setAttribute(
                "aria-expanded",
                "true"
            );
        }
    }


    // =========================================================
    // CLOSE DROPDOWN
    // =========================================================

    function closeCategoryDropdown() {

        if (!categoryPicker || !categoryDropdown) {
            return;
        }

        categoryPicker.classList.remove("is-open");

        categoryDropdown.setAttribute(
            "aria-hidden",
            "true"
        );

        if (categoryInput) {

            categoryInput.setAttribute(
                "aria-expanded",
                "false"
            );
        }

        if (categoryButton) {

            categoryButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    // =========================================================
    // TOGGLE DROPDOWN
    // =========================================================

    async function toggleCategoryDropdown() {

        if (!categoryPicker) return;

        const isOpen =
            categoryPicker.classList.contains(
                "is-open"
            );

        if (isOpen) {

            closeCategoryDropdown();

            return;
        }

        if (!categoriesLoaded) {

            await loadCategories();
        }

        renderCategories(
            categoryInput?.value || ""
        );

        openCategoryDropdown();
    }


    // =========================================================
    // ESCAPE HTML
    // =========================================================

    function escapeHtml(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =========================================================
    // LOAD CATEGORIES
    // =========================================================

    async function loadCategories() {

        if (!categoryList) return;

        if (isLoadingCategories) {
            return;
        }

        isLoadingCategories = true;

        categoryList.innerHTML = `
            <div class="category-loading">
                <span class="category-spinner"></span>
                <strong>Loading categories...</strong>
                <small>Please wait</small>
            </div>
        `;

        setCategoryStatus(
            "Loading categories...",
            "loading"
        );

        try {

            const response = await fetch(
                "/api/jobs/categories",
                {
                    method: "GET",

                    headers: {
                        "Accept": "application/json"
                    },

                    credentials: "same-origin",

                    cache: "no-store"
                }
            );


            if (!response.ok) {

                throw new Error(
                    `Category API returned ${response.status}`
                );
            }


            const result =
                await response.json();


            console.log(
                "Categories API response:",
                result
            );


            /*
             * Expected:
             *
             * {
             *     status: "success",
             *     categories: [...]
             * }
             */

            if (
                !result ||
                !Array.isArray(
                    result.categories
                )
            ) {

                throw new Error(
                    "Invalid category API response."
                );
            }


            categories =
                result.categories
                    .filter(category => {

                        return (
                            category &&
                            category.id !== undefined &&
                            category.name
                        );
                    })
                    .map(category => {

                        return {
                            id:
                                Number(
                                    category.id
                                ),

                            name:
                                String(
                                    category.name
                                ),

                            description:
                                String(
                                    category.description ||
                                    ""
                                ),

                            icon:
                                String(
                                    category.icon ||
                                    "✦"
                                ),

                            slug:
                                String(
                                    category.slug ||
                                    ""
                                )
                        };

                    });


            categoriesLoaded = true;


            if (categoryCount) {

                categoryCount.textContent =
                    categories.length;
            }


            renderCategories(
                categoryInput?.value || ""
            );


            if (categories.length) {

                setCategoryStatus(
                    `${categories.length} categories available`,
                    "success"
                );

            } else {

                setCategoryStatus(
                    "No categories are currently available.",
                    "warning"
                );
            }


        } catch (error) {

            console.error(
                "CATEGORY LOAD ERROR:",
                error
            );

            categories = [];

            categoriesLoaded = false;


            categoryList.innerHTML = `
                <div class="category-empty category-error">
                    <strong>
                        Unable to load categories
                    </strong>

                    <small>
                        Please refresh the page and try again.
                    </small>

                    <button
                        type="button"
                        class="category-retry"
                        id="categoryRetryButton"
                    >
                        Retry
                    </button>
                </div>
            `;


            setCategoryStatus(
                "Unable to load categories.",
                "error"
            );


            const retryButton =
                document.getElementById(
                    "categoryRetryButton"
                );


            if (retryButton) {

                retryButton.addEventListener(
                    "click",
                    async () => {

                        categoriesLoaded = false;

                        await loadCategories();

                    }
                );
            }


        } finally {

            isLoadingCategories = false;
        }
    }


    // =========================================================
    // RENDER CATEGORIES
    // =========================================================

    function renderCategories(
        searchText = ""
    ) {

        if (!categoryList) return;


        const search =
            String(searchText || "")
                .trim()
                .toLowerCase();


        const filtered =
            categories.filter(category => {

                const name =
                    String(
                        category.name || ""
                    ).toLowerCase();

                const description =
                    String(
                        category.description || ""
                    ).toLowerCase();

                const slug =
                    String(
                        category.slug || ""
                    ).toLowerCase();


                return (
                    !search ||
                    name.includes(search) ||
                    description.includes(search) ||
                    slug.includes(search)
                );
            });


        if (categoryCount) {

            categoryCount.textContent =
                filtered.length;
        }


        if (!filtered.length) {

            categoryList.innerHTML = `
                <div class="category-empty">

                    <strong>
                        No matching category
                    </strong>

                    <small>
                        Try another search term.
                    </small>

                </div>
            `;

            return;
        }


        categoryList.innerHTML =
            filtered.map(category => {

                const isSelected =
                    selectedCategory &&
                    Number(
                        selectedCategory.id
                    ) === Number(
                        category.id
                    );


                return `
                    <button
                        type="button"
                        class="category-option ${isSelected ? "active" : ""}"
                        data-category-id="${escapeHtml(category.id)}"
                    >

                        <span class="category-option-icon">
                            ${escapeHtml(category.icon)}
                        </span>


                        <span class="category-option-content">

                            <strong>
                                ${escapeHtml(category.name)}
                            </strong>

                            ${
                                category.description
                                    ? `
                                        <small>
                                            ${escapeHtml(
                                                category.description
                                            )}
                                        </small>
                                      `
                                    : ""
                            }

                        </span>


                        <span class="category-option-arrow">
                            →
                        </span>

                    </button>
                `;

            }).join("");
    }


    // =========================================================
    // SELECT CATEGORY
    // =========================================================

    function selectCategory(category) {

        if (!category) {
            return;
        }


        selectedCategory =
            category;


        /*
         * Visible field
         */

        if (categoryInput) {

            categoryInput.value =
                category.name;

            categoryInput.classList.add(
                "category-selected"
            );
        }


        /*
         * REAL DATABASE ID
         */

        if (categoryIdInput) {

            categoryIdInput.value =
                String(category.id);
        }


        setCategoryStatus(
            `Selected: ${category.name}`,
            "success"
        );


        renderCategories(
            categoryInput?.value || ""
        );


        closeCategoryDropdown();
    }


    // =========================================================
    // CATEGORY LIST CLICK
    // =========================================================

    if (categoryList) {

        categoryList.addEventListener(
            "click",
            event => {

                const retry =
                    event.target.closest(
                        "#categoryRetryButton"
                    );

                if (retry) {
                    return;
                }


                const option =
                    event.target.closest(
                        ".category-option"
                    );


                if (!option) {
                    return;
                }


                const categoryId =
                    Number(
                        option.dataset.categoryId
                    );


                const category =
                    categories.find(
                        item =>
                            Number(item.id) ===
                            categoryId
                    );


                if (!category) {

                    console.error(
                        "Category not found:",
                        categoryId
                    );

                    return;
                }


                selectCategory(
                    category
                );
            }
        );
    }


    // =========================================================
    // SEARCH INPUT
    // =========================================================

    if (categoryInput) {

        categoryInput.addEventListener(
            "input",
            () => {

                const value =
                    categoryInput.value.trim();


                /*
                 * If user changes selected category
                 * manually, remove old ID.
                 */

                if (
                    selectedCategory &&
                    value !==
                    selectedCategory.name
                ) {

                    selectedCategory =
                        null;

                    if (categoryIdInput) {

                        categoryIdInput.value =
                            "";
                    }


                    categoryInput.classList.remove(
                        "category-selected"
                    );


                    setCategoryStatus(
                        "Select a category from the list.",
                        "warning"
                    );
                }


                renderCategories(
                    value
                );


                openCategoryDropdown();
            }
        );


        categoryInput.addEventListener(
            "focus",
            async () => {

                if (!categoriesLoaded) {

                    await loadCategories();
                }


                renderCategories(
                    categoryInput.value
                );


                openCategoryDropdown();
            }
        );


        categoryInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Escape"
                ) {

                    closeCategoryDropdown();

                    return;
                }


                if (
                    event.key === "ArrowDown"
                ) {

                    event.preventDefault();

                    openCategoryDropdown();

                    return;
                }


                /*
                 * Do NOT allow Enter to submit
                 * the form while dropdown is open.
                 */

                if (
                    event.key === "Enter" &&
                    categoryPicker?.classList.contains(
                        "is-open"
                    )
                ) {

                    event.preventDefault();

                    const firstOption =
                        categoryList?.querySelector(
                            ".category-option"
                        );


                    if (firstOption) {

                        firstOption.click();
                    }
                }
            }
        );
    }


    // =========================================================
    // DROPDOWN BUTTON
    // =========================================================

    if (categoryButton) {

        categoryButton.addEventListener(
            "click",
            async event => {

                event.preventDefault();

                event.stopPropagation();

                await toggleCategoryDropdown();


                if (categoryInput) {

                    categoryInput.focus();
                }
            }
        );
    }


    // =========================================================
    // CUSTOM CATEGORY
    // =========================================================

    if (customCategoryButton) {

        customCategoryButton.addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();


                setCategoryStatus(
                    "Only admin-approved categories can be used for jobs.",
                    "warning"
                );


                if (categoryInput) {

                    categoryInput.focus();

                    categoryInput.select();
                }


                openCategoryDropdown();
            }
        );
    }


    // =========================================================
    // OUTSIDE CLICK
    // =========================================================

    document.addEventListener(
        "click",
        event => {

            if (
                categoryPicker &&
                !categoryPicker.contains(
                    event.target
                )
            ) {

                closeCategoryDropdown();
            }
        }
    );


    // =========================================================
    // DESCRIPTION COUNTER
    // =========================================================

    function updateDescriptionCounter() {

        if (
            !description ||
            !descriptionCounter
        ) {
            return;
        }


        descriptionCounter.textContent =
            `${description.value.length} / 5000`;
    }


    if (description) {

        description.addEventListener(
            "input",
            updateDescriptionCounter
        );

        updateDescriptionCounter();
    }


    // =========================================================
    // FORM MESSAGE
    // =========================================================

    function showMessage(
        message,
        type = "error"
    ) {

        if (!formMessage) {
            return;
        }


        formMessage.textContent =
            message;


        formMessage.className =
            `form-message ${type} show`;


        formMessage.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }


    function clearMessage() {

        if (!formMessage) {
            return;
        }


        formMessage.textContent = "";

        formMessage.className =
            "form-message";
    }


    // =========================================================
    // FORM SUBMIT
    // =========================================================

    if (form) {

        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();

                clearMessage();


                const title =
                    document
                        .getElementById(
                            "jobTitle"
                        )
                        ?.value
                        .trim();


                const jobDescription =
                    document
                        .getElementById(
                            "jobDescription"
                        )
                        ?.value
                        .trim();


                const location =
                    document
                        .getElementById(
                            "jobLocation"
                        )
                        ?.value
                        .trim();


                const city =
                    document
                        .getElementById(
                            "jobCity"
                        )
                        ?.value
                        .trim();


                const state =
                    document
                        .getElementById(
                            "jobState"
                        )
                        ?.value
                        .trim();


                const pincode =
                    document
                        .getElementById(
                            "jobPincode"
                        )
                        ?.value
                        .trim();


                const budgetMin =
                    document
                        .getElementById(
                            "budgetMin"
                        )
                        ?.value;


                const budgetMax =
                    document
                        .getElementById(
                            "budgetMax"
                        )
                        ?.value;


                const priority =
                    document
                        .getElementById(
                            "jobPriority"
                        )
                        ?.value ||
                    "normal";


                // =================================================
                // VALIDATION
                // =================================================

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


                const categoryId =
                    Number(
                        categoryIdInput?.value
                    );


                if (
                    !categoryId ||
                    !selectedCategory
                ) {

                    showMessage(
                        "Please select a valid category from the category list."
                    );


                    if (categoryInput) {

                        categoryInput.focus();
                    }


                    await loadCategories();

                    renderCategories(
                        categoryInput?.value || ""
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
                    budgetMin !== "" &&
                    budgetMax !== "" &&
                    Number(budgetMin) >
                    Number(budgetMax)
                ) {

                    showMessage(
                        "Minimum budget cannot exceed maximum budget."
                    );

                    return;
                }


                // =================================================
                // PAYLOAD
                // =================================================

                const payload = {

                    title,

                    description:
                        jobDescription,

                    category_id:
                        categoryId,

                    budget_min:
                        budgetMin !== ""
                            ? Number(budgetMin)
                            : null,

                    budget_max:
                        budgetMax !== ""
                            ? Number(budgetMax)
                            : null,

                    location,

                    city:
                        city || null,

                    state:
                        state || null,

                    pincode:
                        pincode || null,

                    priority
                };


                console.log(
                    "POST JOB PAYLOAD:",
                    payload
                );


                // =================================================
                // BUTTON LOADING
                // =================================================

                if (postJobButton) {

                    postJobButton.disabled =
                        true;


                    postJobButton.dataset.originalText =
                        postJobButton.querySelector(
                            ".button-text"
                        )?.textContent ||
                        "Post Job";


                    const buttonText =
                        postJobButton.querySelector(
                            ".button-text"
                        );


                    if (buttonText) {

                        buttonText.textContent =
                            "Posting...";
                    }
                }


                try {

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


                    let result = {};


                    try {

                        result =
                            await response.json();

                    } catch (_) {

                        result = {};
                    }


                    console.log(
                        "POST JOB RESPONSE:",
                        result
                    );


                    if (!response.ok) {

                        throw new Error(
                            result.message ||
                            `Unable to post job (${response.status})`
                        );
                    }


                    if (
                        result.status !==
                        "success"
                    ) {

                        throw new Error(
                            result.message ||
                            "Job could not be posted."
                        );
                    }


                    showMessage(
                        result.message ||
                        "Job posted successfully!",
                        "success"
                    );


                    // =================================================
                    // SUCCESS
                    // =================================================

                    form.reset();


                    if (categoryIdInput) {

                        categoryIdInput.value =
                            "";
                    }


                    selectedCategory =
                        null;


                    if (categoryInput) {

                        categoryInput.classList.remove(
                            "category-selected"
                        );
                    }


                    setCategoryStatus(
                        "Job posted successfully.",
                        "success"
                    );


                    updateDescriptionCounter();


                    if (
                        result.job &&
                        result.job.id
                    ) {

                        setTimeout(
                            () => {

                                window.location.href =
                                    `/jobs/${result.job.id}`;

                            },
                            1000
                        );
                    }


                } catch (error) {

                    console.error(
                        "POST JOB ERROR:",
                        error
                    );


                    showMessage(
                        error.message ||
                        "Something went wrong. Please try again."
                    );


                } finally {

                    if (postJobButton) {

                        postJobButton.disabled =
                            false;


                        const buttonText =
                            postJobButton.querySelector(
                                ".button-text"
                            );


                        if (buttonText) {

                            buttonText.textContent =
                                postJobButton.dataset.originalText ||
                                "Post Job";
                        }
                    }
                }
            }
        );
    }


    // =========================================================
    // INITIAL STATE
    // =========================================================

    if (categoryInput) {

        categoryInput.setAttribute(
            "role",
            "combobox"
        );

        categoryInput.setAttribute(
            "aria-expanded",
            "false"
        );

        categoryInput.setAttribute(
            "aria-autocomplete",
            "list"
        );
    }


    if (categoryDropdown) {

        categoryDropdown.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    if (categoryButton) {

        categoryButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    // =========================================================
    // INITIAL CATEGORY LOAD
    // =========================================================

    loadCategories();

});
