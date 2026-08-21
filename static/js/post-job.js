document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    /* =========================================================
       ELEMENTS
    ========================================================== */

    const form = document.getElementById("postJobForm");

    if (!form) {
        return;
    }


    const categoryInput =
        document.getElementById("jobCategory");

    const categoryIdInput =
        document.getElementById("jobCategoryId");

    const categoryPicker =
        document.getElementById("categoryPicker");

    const categoryDropdown =
        document.getElementById("categoryDropdown");

    const categoryList =
        document.getElementById("categoryList");

    const categoryCount =
        document.getElementById("categoryCount");

    const categoryButton =
        document.getElementById("categoryDropdownButton");

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


    const categoryUrl =
        form.dataset.categoryUrl;

    const createUrl =
        form.dataset.createUrl;


    let categories = [];


    /* =========================================================
       CATEGORY DROPDOWN
    ========================================================== */

    function openCategoryDropdown() {

        categoryDropdown.classList.add("is-open");

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

        categoryDropdown.classList.remove("is-open");

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


    categoryButton.addEventListener(
        "click",
        () => {

            if (
                categoryDropdown.classList.contains(
                    "is-open"
                )
            ) {

                closeCategoryDropdown();

            } else {

                openCategoryDropdown();

                categoryInput.focus();

                renderCategories(
                    categoryInput.value.trim()
                );
            }
        }
    );


    categoryInput.addEventListener(
        "focus",
        () => {

            openCategoryDropdown();

            renderCategories(
                categoryInput.value.trim()
            );
        }
    );


    /* =========================================================
       LOAD CATEGORIES
    ========================================================== */

    async function loadCategories() {

        categoryList.innerHTML = `
            <div class="category-loading">
                <span class="category-spinner"></span>
                <strong>Loading categories...</strong>
                <small>Please wait</small>
            </div>
        `;


        try {

            if (!categoryUrl) {
                throw new Error(
                    "Category API URL is missing."
                );
            }


            const response = await fetch(
                categoryUrl,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );


            const contentType =
                response.headers.get(
                    "content-type"
                ) || "";


            if (!contentType.includes(
                "application/json"
            )) {

                throw new Error(
                    `Category API returned ${response.status} instead of JSON.`
                );
            }


            const result =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    result.message ||
                    "Failed to load categories."
                );
            }


            if (
                result.status !== "success" ||
                !Array.isArray(result.categories)
            ) {

                throw new Error(
                    "Invalid category response."
                );
            }


            categories =
                result.categories;


            categoryCount.textContent =
                categories.length;


            renderCategories("");


            if (categories.length === 0) {

                setCategoryStatus(
                    "No active categories are available.",
                    "error"
                );

            } else {

                setCategoryStatus(
                    `${categories.length} categories available.`,
                    "success"
                );
            }


        } catch (error) {

            console.error(
                "CATEGORY LOAD ERROR:",
                error
            );


            categories = [];

            categoryCount.textContent = "0";


            categoryList.innerHTML = `
                <div class="category-error">

                    <div class="category-error-icon">
                        !
                    </div>

                    <strong>
                        Unable to load categories
                    </strong>

                    <small>
                        ${escapeHtml(error.message)}
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


            const retryButton =
                document.getElementById(
                    "retryCategories"
                );


            if (retryButton) {

                retryButton.addEventListener(
                    "click",
                    loadCategories
                );
            }


            setCategoryStatus(
                "Category loading failed.",
                "error"
            );
        }
    }


    /* =========================================================
       RENDER CATEGORIES
    ========================================================== */

    function renderCategories(searchTerm = "") {

        const term =
            searchTerm.toLowerCase().trim();


        const filtered =
            categories.filter(category => {

                const name =
                    String(
                        category.name || ""
                    ).toLowerCase();

                const slug =
                    String(
                        category.slug || ""
                    ).toLowerCase();

                const description =
                    String(
                        category.description || ""
                    ).toLowerCase();


                return (
                    !term ||
                    name.includes(term) ||
                    slug.includes(term) ||
                    description.includes(term)
                );
            });


        categoryCount.textContent =
            filtered.length;


        if (filtered.length === 0) {

            categoryList.innerHTML = `
                <div class="category-empty">

                    <div class="empty-icon">
                        ◈
                    </div>

                    <strong>
                        No category found
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

                const icon =
                    category.icon || "✦";


                const description =
                    category.description ||
                    "Professional service";


                return `

                    <button
                        type="button"
                        class="category-option"
                        data-category-id="${escapeHtml(
                            category.id
                        )}"
                        data-category-name="${escapeHtml(
                            category.name
                        )}"
                    >

                        <span class="category-option-icon">
                            ${escapeHtml(icon)}
                        </span>


                        <span class="category-option-content">

                            <strong>
                                ${escapeHtml(
                                    category.name
                                )}
                            </strong>

                            <small>
                                ${escapeHtml(
                                    description
                                )}
                            </small>

                        </span>


                        <span class="category-option-arrow">
                            →
                        </span>

                    </button>
                `;
            }).join("");


        categoryList
            .querySelectorAll(
                ".category-option"
            )
            .forEach(option => {

                option.addEventListener(
                    "click",
                    () => {

                        const id =
                            option.dataset.categoryId;

                        const name =
                            option.dataset.categoryName;


                        selectCategory(
                            id,
                            name
                        );
                    }
                );
            });
    }


    /* =========================================================
       SELECT CATEGORY
    ========================================================== */

    function selectCategory(
        id,
        name
    ) {

        categoryIdInput.value = id;

        categoryInput.value = name;

        categoryInput.classList.add(
            "category-selected"
        );

        setCategoryStatus(
            `Selected: ${name}`,
            "success"
        );

        closeCategoryDropdown();
    }


    /* =========================================================
       SEARCH
    ========================================================== */

    categoryInput.addEventListener(
        "input",
        () => {

            /*
             * User changed the category text.
             * Therefore old ID is no longer trusted.
             */

            categoryIdInput.value = "";

            categoryInput.classList.remove(
                "category-selected"
            );


            renderCategories(
                categoryInput.value
            );


            openCategoryDropdown();
        }
    );


    /* =========================================================
       CUSTOM CATEGORY
    ========================================================== */

    customCategoryButton.addEventListener(
        "click",
        () => {

            const value =
                categoryInput.value.trim();


            if (!value) {

                setCategoryStatus(
                    "Type a category name first.",
                    "error"
                );

                categoryInput.focus();

                return;
            }


            setCategoryStatus(
                `"${value}" is not an approved category. Please contact admin to add it.`,
                "error"
            );
        }
    );


    /* =========================================================
       DESCRIPTION COUNTER
    ========================================================== */

    if (description) {

        function updateDescriptionCounter() {

            descriptionCounter.textContent =
                `${description.value.length} / 5000`;
        }


        description.addEventListener(
            "input",
            updateDescriptionCounter
        );


        updateDescriptionCounter();
    }


    /* =========================================================
       FORM SUBMIT
    ========================================================== */

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            clearFormMessage();


            const title =
                document
                    .getElementById("jobTitle")
                    .value.trim();


            const descriptionValue =
                description.value.trim();


            const categoryId =
                categoryIdInput.value;


            const location =
                document
                    .getElementById("jobLocation")
                    .value.trim();


            const budgetMinValue =
                document
                    .getElementById("budgetMin")
                    .value;


            const budgetMaxValue =
                document
                    .getElementById("budgetMax")
                    .value;


            const city =
                document
                    .getElementById("jobCity")
                    .value.trim();


            const state =
                document
                    .getElementById("jobState")
                    .value.trim();


            const pincode =
                document
                    .getElementById("jobPincode")
                    .value.trim();


            const priority =
                document
                    .getElementById("jobPriority")
                    .value;


            /* ---------------------------------------------
               VALIDATION
            ---------------------------------------------- */

            if (!title) {

                showFormMessage(
                    "Please enter a job title.",
                    "error"
                );

                return;
            }


            if (!descriptionValue) {

                showFormMessage(
                    "Please describe the job.",
                    "error"
                );

                return;
            }


            if (!categoryId) {

                showFormMessage(
                    "Please select a category from the list.",
                    "error"
                );

                openCategoryDropdown();

                return;
            }


            if (!location) {

                showFormMessage(
                    "Please enter the work location.",
                    "error"
                );

                return;
            }


            const budgetMin =
                budgetMinValue === ""
                    ? null
                    : Number(budgetMinValue);


            const budgetMax =
                budgetMaxValue === ""
                    ? null
                    : Number(budgetMaxValue);


            if (
                budgetMin !== null &&
                budgetMax !== null &&
                budgetMin > budgetMax
            ) {

                showFormMessage(
                    "Minimum budget cannot exceed maximum budget.",
                    "error"
                );

                return;
            }


            /* ---------------------------------------------
               AUTH TOKEN
            ---------------------------------------------- */

            const token =
                localStorage.getItem(
                    "access_token"
                ) ||
                localStorage.getItem(
                    "accessToken"
                ) ||
                localStorage.getItem(
                    "token"
                ) ||
                sessionStorage.getItem(
                    "access_token"
                );


            if (!token) {

                showFormMessage(
                    "Please login as a customer before posting a job.",
                    "error"
                );

                return;
            }


            /* ---------------------------------------------
               PAYLOAD
            ---------------------------------------------- */

            const payload = {

                title: title,

                description: descriptionValue,

                category_id: Number(
                    categoryId
                ),

                budget_min: budgetMin,

                budget_max: budgetMax,

                location: location,

                city: city || null,

                state: state || null,

                pincode: pincode || null,

                priority: priority

            };


            /* ---------------------------------------------
               BUTTON LOADING
            ---------------------------------------------- */

            submitButton.disabled = true;

            submitButton.classList.add(
                "is-loading"
            );


            const originalButtonText =
                submitButton.querySelector(
                    ".button-text"
                );


            const oldText =
                originalButtonText.textContent;


            originalButtonText.textContent =
                "Posting Job...";


            try {

                const response =
                    await fetch(
                        createUrl,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${token}`
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
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.message ||
                        "Unable to post job."
                    );
                }


                showFormMessage(
                    result.message ||
                    "Job posted successfully!",
                    "success"
                );


                form.reset();

                categoryIdInput.value = "";

                categoryInput.classList.remove(
                    "category-selected"
                );


                if (descriptionCounter) {

                    descriptionCounter.textContent =
                        "0 / 5000";
                }


                /*
                 * Redirect after successful creation.
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
                        900
                    );
                }


            } catch (error) {

                console.error(
                    "POST JOB ERROR:",
                    error
                );


                showFormMessage(
                    error.message ||
                    "Something went wrong.",
                    "error"
                );


            } finally {

                submitButton.disabled = false;

                submitButton.classList.remove(
                    "is-loading"
                );

                originalButtonText.textContent =
                    oldText;
            }

        }
    );


    /* =========================================================
       OUTSIDE CLICK
    ========================================================== */

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


    /* =========================================================
       ESC KEY
    ========================================================== */

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


    /* =========================================================
       STATUS
    ========================================================== */

    function setCategoryStatus(
        message,
        type
    ) {

        categoryStatus.textContent =
            message;

        categoryStatus.className =
            "category-status";

        if (type) {

            categoryStatus.classList.add(
                type
            );
        }
    }


    function showFormMessage(
        message,
        type
    ) {

        formMessage.textContent =
            message;

        formMessage.className =
            "form-message";

        formMessage.classList.add(
            type
        );

        formMessage.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }


    function clearFormMessage() {

        formMessage.textContent = "";

        formMessage.className =
            "form-message";
    }


    /* =========================================================
       ESCAPE HTML
    ========================================================== */

    function escapeHtml(value) {

        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    /* =========================================================
       INITIAL LOAD
    ========================================================== */

    loadCategories();

});
