document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    // =========================================================
    // ELEMENTS
    // =========================================================

    const form = document.getElementById("postJobForm");

    const categoryInput =
        document.getElementById("jobCategory");

    const categoryPicker =
        document.getElementById("categoryPicker");

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
    // HIDDEN CATEGORY ID
    // =========================================================

    let categoryIdInput =
        document.getElementById("jobCategoryId");

    if (!categoryIdInput) {

        categoryIdInput =
            document.createElement("input");

        categoryIdInput.type = "hidden";
        categoryIdInput.id = "jobCategoryId";
        categoryIdInput.name = "category_id";

        form.appendChild(categoryIdInput);
    }


    // =========================================================
    // STATE
    // =========================================================

    let categories = [];

    let selectedCategory = null;


    // =========================================================
    // CATEGORY DROPDOWN
    // =========================================================

    function openCategoryDropdown() {

        if (!categoryDropdown) return;

        categoryDropdown.classList.add("is-open");

        if (categoryInput) {
            categoryInput.setAttribute(
                "aria-expanded",
                "true"
            );
        }
    }


    function closeCategoryDropdown() {

        if (!categoryDropdown) return;

        categoryDropdown.classList.remove("is-open");

        if (categoryInput) {
            categoryInput.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    function toggleCategoryDropdown() {

        if (!categoryDropdown) return;

        if (
            categoryDropdown.classList.contains(
                "is-open"
            )
        ) {

            closeCategoryDropdown();

        } else {

            renderCategories(
                categoryInput
                    ? categoryInput.value
                    : ""
            );

            openCategoryDropdown();
        }
    }


    // =========================================================
    // LOAD CATEGORIES
    // =========================================================

    async function loadCategories() {

        if (!categoryList) return;

        categoryList.innerHTML = `
            <div class="category-loading">
                <span class="category-spinner"></span>
                Loading categories...
            </div>
        `;

        try {

            const response = await fetch(
                "/api/jobs/categories",
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            if (!response.ok) {

                throw new Error(
                    `Category request failed: ${response.status}`
                );
            }

            const result =
                await response.json();

            if (
                result.status !== "success" ||
                !Array.isArray(result.categories)
            ) {

                throw new Error(
                    "Invalid category response"
                );
            }

            categories =
                result.categories;

            if (categoryCount) {

                categoryCount.textContent =
                    categories.length;
            }

            renderCategories("");

            if (categoryStatus) {

                categoryStatus.textContent =
                    categories.length
                        ? `${categories.length} categories available`
                        : "No categories available";

                categoryStatus.className =
                    categories.length
                        ? "category-status success"
                        : "category-status warning";
            }

        } catch (error) {

            console.error(
                "Category loading error:",
                error
            );

            categories = [];

            if (categoryList) {

                categoryList.innerHTML = `
                    <div class="category-empty">
                        <strong>Unable to load categories</strong>
                        <small>Please refresh the page and try again.</small>
                    </div>
                `;
            }

            if (categoryStatus) {

                categoryStatus.textContent =
                    "Unable to load categories.";

                categoryStatus.className =
                    "category-status error";
            }
        }
    }


    // =========================================================
    // RENDER CATEGORIES
    // =========================================================

    function renderCategories(searchText = "") {

        if (!categoryList) return;

        const search =
            searchText
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

                return (
                    !search ||
                    name.includes(search) ||
                    description.includes(search)
                );
            });


        if (categoryCount) {

            categoryCount.textContent =
                filtered.length;
        }


        if (!filtered.length) {

            categoryList.innerHTML = `
                <div class="category-empty">
                    <strong>No matching category</strong>
                    <small>
                        Try another search term.
                    </small>
                </div>
            `;

            return;
        }


        categoryList.innerHTML =
            filtered.map(category => {

                const icon =
                    category.icon ||
                    "✦";

                const description =
                    category.description ||
                    "Professional service category";

                return `
                    <button
                        type="button"
                        class="category-option"
                        data-category-id="${category.id}"
                        data-category-name="${escapeHtml(category.name)}"
                    >

                        <span class="category-option-icon">
                            ${escapeHtml(icon)}
                        </span>

                        <span class="category-option-content">

                            <strong>
                                ${escapeHtml(category.name)}
                            </strong>

                            <small>
                                ${escapeHtml(description)}
                            </small>

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

        if (!category) return;

        selectedCategory =
            category;

        if (categoryInput) {

            categoryInput.value =
                category.name;
        }

        if (categoryIdInput) {

            categoryIdInput.value =
                category.id;
        }

        if (categoryStatus) {

            categoryStatus.textContent =
                `Selected: ${category.name}`;

            categoryStatus.className =
                "category-status success";
        }

        closeCategoryDropdown();
    }


    // =========================================================
    // CATEGORY CLICK
    // =========================================================

    if (categoryList) {

        categoryList.addEventListener(
            "click",
            event => {

                const option =
                    event.target.closest(
                        ".category-option"
                    );

                if (!option) return;

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

                if (category) {

                    selectCategory(category);
                }
            }
        );
    }


    // =========================================================
    // SEARCH CATEGORY
    // =========================================================

    if (categoryInput) {

        categoryInput.addEventListener(
            "input",
            () => {

                const typedValue =
                    categoryInput.value.trim();

                /*
                 * User changed the selected category.
                 * Clear the old category ID.
                 */

                if (
                    selectedCategory &&
                    typedValue !==
                    selectedCategory.name
                ) {

                    selectedCategory = null;

                    categoryIdInput.value = "";

                    if (categoryStatus) {

                        categoryStatus.textContent =
                            "Please select a category from the list.";

                        categoryStatus.className =
                            "category-status warning";
                    }
                }

                renderCategories(
                    typedValue
                );

                openCategoryDropdown();
            }
        );


        categoryInput.addEventListener(
            "focus",
            () => {

                renderCategories(
                    categoryInput.value
                );

                openCategoryDropdown();
            }
        );


        categoryInput.addEventListener(
            "keydown",
            event => {

                if (event.key === "Escape") {

                    closeCategoryDropdown();
                }

                if (
                    event.key === "ArrowDown"
                ) {

                    event.preventDefault();

                    openCategoryDropdown();
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
            event => {

                event.preventDefault();

                toggleCategoryDropdown();

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
            () => {

                /*
                 * IMPORTANT:
                 * Your database Job.category_id is a
                 * foreign key and cannot accept arbitrary text.
                 *
                 * Therefore custom categories cannot be posted
                 * directly unless the backend first creates a
                 * Category record.
                 */

                if (categoryStatus) {

                    categoryStatus.textContent =
                        "Please choose an existing category. Custom categories require admin approval.";

                    categoryStatus.className =
                        "category-status warning";
                }

                if (categoryInput) {

                    categoryInput.focus();

                    categoryInput.select();
                }

                openCategoryDropdown();
            }
        );
    }


    // =========================================================
    // CLOSE DROPDOWN OUTSIDE
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

        if (!descriptionCounter || !description) {
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

        if (!formMessage) return;

        formMessage.textContent =
            message;

        formMessage.className =
            `form-message ${type}`;

        formMessage.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }


    function clearMessage() {

        if (!formMessage) return;

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


                // ---------------------------------------------
                // Basic validation
                // ---------------------------------------------

                const title =
                    document
                        .getElementById("jobTitle")
                        ?.value.trim();

                const jobDescription =
                    document
                        .getElementById("jobDescription")
                        ?.value.trim();

                const location =
                    document
                        .getElementById("jobLocation")
                        ?.value.trim();

                const city =
                    document
                        .getElementById("jobCity")
                        ?.value.trim();

                const state =
                    document
                        .getElementById("jobState")
                        ?.value.trim();

                const pincode =
                    document
                        .getElementById("jobPincode")
                        ?.value.trim();

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
                        ?.value ||
                    "normal";


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


                if (
                    !categoryIdInput ||
                    !categoryIdInput.value
                ) {

                    showMessage(
                        "Please select a category from the category list."
                    );

                    if (categoryInput) {
                        categoryInput.focus();
                    }

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


                // ---------------------------------------------
                // Request body
                // ---------------------------------------------

                const payload = {

                    title: title,

                    description:
                        jobDescription,

                    category_id:
                        Number(
                            categoryIdInput.value
                        ),

                    budget_min:
                        budgetMin !== ""
                            ? Number(budgetMin)
                            : null,

                    budget_max:
                        budgetMax !== ""
                            ? Number(budgetMax)
                            : null,

                    location: location,

                    city:
                        city || null,

                    state:
                        state || null,

                    pincode:
                        pincode || null,

                    priority:
                        priority
                };


                // ---------------------------------------------
                // Button loading state
                // ---------------------------------------------

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

                    /*
                     * IMPORTANT:
                     *
                     * Backend route:
                     *
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


                    let result = {};

                    try {

                        result =
                            await response.json();

                    } catch (_) {

                        result = {};
                    }


                    if (!response.ok) {

                        throw new Error(
                            result.message ||
                            `Unable to post job (${response.status})`
                        );
                    }


                    showMessage(
                        result.message ||
                        "Job posted successfully!",
                        "success"
                    );


                    // -----------------------------------------
                    // Success
                    // -----------------------------------------

                    if (
                        result.status ===
                        "success"
                    ) {

                        form.reset();

                        categoryIdInput.value =
                            "";

                        selectedCategory =
                            null;

                        if (categoryStatus) {

                            categoryStatus.textContent =
                                "Job posted successfully.";

                            categoryStatus.className =
                                "category-status success";
                        }

                        updateDescriptionCounter();


                        /*
                         * Redirect to job details if
                         * backend returned job ID.
                         */

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
                    }


                } catch (error) {

                    console.error(
                        "Post job error:",
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
    // HTML ESCAPE
    // =========================================================

    function escapeHtml(value) {

        return String(value ?? "")
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


    // =========================================================
    // INITIALIZE
    // =========================================================

    if (categoryInput) {

        categoryInput.setAttribute(
            "aria-expanded",
            "false"
        );

        categoryInput.setAttribute(
            "role",
            "combobox"
        );
    }


    loadCategories();

});
