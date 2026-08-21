document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    /* =========================================================
       ELEMENTS
    ========================================================= */

    const form = document.getElementById("postJobForm");

    const categoryPicker =
        document.getElementById("categoryPicker");

    const categoryInput =
        document.getElementById("jobCategory");

    const categoryId =
        document.getElementById("jobCategoryId");

    const categoryDropdown =
        document.getElementById("categoryDropdown");

    const categoryButton =
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


    if (!form) {
        return;
    }


    /* =========================================================
       STATE
    ========================================================= */

    let categories = [];

    let activeIndex = -1;


    /* =========================================================
       CATEGORY API
       
       IMPORTANT:
       Backend should return:
       
       [
           {
               "id": 1,
               "name": "Electrician"
           }
       ]
       
       OR:
       
       {
           "categories": [...]
       }
    ========================================================= */

    const CATEGORY_API = "/api/categories";


    /* =========================================================
       HELPERS
    ========================================================= */

    function escapeHTML(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }


    function setCategoryStatus(message, type = "") {

        if (!categoryStatus) {
            return;
        }

        categoryStatus.textContent = message;

        categoryStatus.className =
            "category-status";

        if (type) {
            categoryStatus.classList.add(type);
        }

    }


    function openCategoryDropdown() {

        if (!categoryPicker) {
            return;
        }

        categoryPicker.classList.add("open");

        categoryInput.setAttribute(
            "aria-expanded",
            "true"
        );

        categoryButton.setAttribute(
            "aria-expanded",
            "true"
        );

        categoryDropdown.setAttribute(
            "aria-hidden",
            "false"
        );

    }


    function closeCategoryDropdown() {

        if (!categoryPicker) {
            return;
        }

        categoryPicker.classList.remove("open");

        categoryInput.setAttribute(
            "aria-expanded",
            "false"
        );

        categoryButton.setAttribute(
            "aria-expanded",
            "false"
        );

        categoryDropdown.setAttribute(
            "aria-hidden",
            "true"
        );

        activeIndex = -1;

    }


    /* =========================================================
       LOAD CATEGORIES
    ========================================================= */

    async function loadCategories() {

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

        try {

            const response =
                await fetch(CATEGORY_API, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                });


            if (!response.ok) {
                throw new Error(
                    `Category request failed: ${response.status}`
                );
            }


            const data =
                await response.json();


            if (Array.isArray(data)) {

                categories = data;

            } else if (
                data &&
                Array.isArray(data.categories)
            ) {

                categories = data.categories;

            } else {

                categories = [];

            }


            renderCategories(categories);

        } catch (error) {

            console.error(
                "Category loading error:",
                error
            );


            categoryList.innerHTML = `
                <div class="category-loading">

                    <strong>
                        Unable to load categories
                    </strong>

                    <small>
                        Please refresh the page and try again.
                    </small>

                </div>
            `;

            categoryCount.textContent = "0";

            setCategoryStatus(
                "Categories could not be loaded.",
                "error"
            );

        }

    }


    /* =========================================================
       RENDER CATEGORIES
    ========================================================= */

    function renderCategories(list) {

        categoryCount.textContent =
            String(list.length);


        if (!list.length) {

            categoryList.innerHTML = `
                <div class="category-loading">

                    <strong>
                        No categories found
                    </strong>

                    <small>
                        Try another search.
                    </small>

                </div>
            `;

            return;
        }


        categoryList.innerHTML =
            list.map((category, index) => {

                const id =
                    category.id ??
                    category.category_id;

                const name =
                    category.name ??
                    category.title ??
                    category.category_name ??
                    "Unnamed Category";

                const description =
                    category.description ??
                    "Approved marketplace category";


                return `
                    <button
                        type="button"
                        class="category-option"
                        data-category-id="${escapeHTML(id)}"
                        data-index="${index}"
                        role="option"
                    >

                        <span class="category-option-icon">
                            ✦
                        </span>

                        <span class="category-option-content">

                            <strong>
                                ${escapeHTML(name)}
                            </strong>

                            <small>
                                ${escapeHTML(description)}
                            </small>

                        </span>

                    </button>
                `;

            }).join("");


        categoryList
            .querySelectorAll(".category-option")
            .forEach(option => {

                option.addEventListener(
                    "click",
                    () => {

                        selectCategory(
                            option.dataset.categoryId,
                            option
                        );

                    }
                );

            });

    }


    /* =========================================================
       SELECT CATEGORY
    ========================================================= */

    function selectCategory(id, option) {

        const selected =
            categories.find(category =>
                String(
                    category.id ??
                    category.category_id
                ) === String(id)
            );


        if (!selected) {
            return;
        }


        const name =
            selected.name ??
            selected.title ??
            selected.category_name ??
            "";


        categoryInput.value = name;

        categoryId.value = id;

        setCategoryStatus(
            `Selected: ${name}`,
            "success"
        );


        categoryList
            .querySelectorAll(".category-option")
            .forEach(item => {

                item.classList.remove("active");

            });


        if (option) {
            option.classList.add("active");
        }


        closeCategoryDropdown();

    }


    /* =========================================================
       FILTER CATEGORIES
    ========================================================= */

    function filterCategories(search) {

        const query =
            search.trim().toLowerCase();


        if (!query) {

            renderCategories(categories);

            return;

        }


        const filtered =
            categories.filter(category => {

                const name =
                    String(
                        category.name ??
                        category.title ??
                        category.category_name ??
                        ""
                    ).toLowerCase();


                const description =
                    String(
                        category.description ?? ""
                    ).toLowerCase();


                return (
                    name.includes(query) ||
                    description.includes(query)
                );

            });


        renderCategories(filtered);

    }


    /* =========================================================
       OPEN BUTTON
    ========================================================= */

    categoryButton.addEventListener(
        "click",
        () => {

            if (
                categoryPicker.classList.contains("open")
            ) {

                closeCategoryDropdown();

            } else {

                openCategoryDropdown();

                if (!categories.length) {
                    loadCategories();
                }

            }

        }
    );


    /* =========================================================
       INPUT FOCUS
    ========================================================= */

    categoryInput.addEventListener(
        "focus",
        () => {

            openCategoryDropdown();

            if (!categories.length) {
                loadCategories();
            }

        }
    );


    /* =========================================================
       SEARCH
    ========================================================= */

    categoryInput.addEventListener(
        "input",
        () => {

            /*
             * User changed category manually.
             * Therefore old database ID is no longer valid.
             */

            categoryId.value = "";

            setCategoryStatus("");

            openCategoryDropdown();

            filterCategories(
                categoryInput.value
            );

        }
    );


    /* =========================================================
       KEYBOARD NAVIGATION
    ========================================================= */

    categoryInput.addEventListener(
        "keydown",
        event => {

            const options =
                Array.from(
                    categoryList.querySelectorAll(
                        ".category-option"
                    )
                );


            if (!options.length) {
                return;
            }


            if (event.key === "ArrowDown") {

                event.preventDefault();

                activeIndex =
                    Math.min(
                        activeIndex + 1,
                        options.length - 1
                    );

            }


            else if (event.key === "ArrowUp") {

                event.preventDefault();

                activeIndex =
                    Math.max(
                        activeIndex - 1,
                        0
                    );

            }


            else if (event.key === "Enter") {

                if (activeIndex >= 0) {

                    event.preventDefault();

                    options[activeIndex].click();

                }

                return;

            }


            else if (event.key === "Escape") {

                closeCategoryDropdown();

                return;

            }


            options.forEach(
                option =>
                    option.classList.remove("active")
            );


            if (options[activeIndex]) {

                options[activeIndex]
                    .classList.add("active");

                options[activeIndex]
                    .scrollIntoView({
                        block: "nearest"
                    });

            }

        }
    );


    /* =========================================================
       CUSTOM CATEGORY BUTTON
    ========================================================= */

    customCategoryButton.addEventListener(
        "click",
        () => {

            categoryInput.focus();

            categoryInput.select();

            setCategoryStatus(
                "Search from the approved categories above.",
                ""
            );

        }
    );


    /* =========================================================
       OUTSIDE CLICK
    ========================================================= */

    document.addEventListener(
        "click",
        event => {

            if (
                categoryPicker &&
                !categoryPicker.contains(event.target)
            ) {

                closeCategoryDropdown();

            }

        }
    );


    /* =========================================================
       DESCRIPTION COUNTER
    ========================================================= */

    function updateDescriptionCounter() {

        if (!description || !descriptionCounter) {
            return;
        }


        const length =
            description.value.length;


        descriptionCounter.textContent =
            `${length} / 5000`;

    }


    if (description) {

        description.addEventListener(
            "input",
            updateDescriptionCounter
        );

        updateDescriptionCounter();

    }


    /* =========================================================
       FIELD VALIDATION
    ========================================================= */

    function markInvalid(element) {

        if (!element) {
            return;
        }

        element.classList.add("invalid");

    }


    function clearInvalid(element) {

        if (!element) {
            return;
        }

        element.classList.remove("invalid");

    }


    function validateForm() {

        let valid = true;


        const requiredFields = [
            document.getElementById("jobTitle"),
            document.getElementById("jobDescription"),
            categoryInput,
            document.getElementById("jobLocation")
        ];


        requiredFields.forEach(field => {

            if (!field) {
                return;
            }


            if (!field.value.trim()) {

                markInvalid(field);

                valid = false;

            } else {

                clearInvalid(field);

            }

        });


        /*
         * Category must have a real database ID.
         */

        if (!categoryId.value) {

            markInvalid(categoryInput);

            setCategoryStatus(
                "Please select an approved category from the list.",
                "error"
            );

            valid = false;

        }


        const min =
            parseFloat(
                document.getElementById("budgetMin")?.value
            );


        const max =
            parseFloat(
                document.getElementById("budgetMax")?.value
            );


        if (
            Number.isFinite(min) &&
            Number.isFinite(max) &&
            max < min
        ) {

            formMessage.textContent =
                "Maximum budget cannot be lower than minimum budget.";

            formMessage.className =
                "form-message show error";

            valid = false;

        }


        return valid;

    }


    /* =========================================================
       REMOVE INVALID STATE
    ========================================================= */

    form.querySelectorAll(
        "input, textarea, select"
    ).forEach(field => {

        field.addEventListener(
            "input",
            () => clearInvalid(field)
        );

        field.addEventListener(
            "change",
            () => clearInvalid(field)
        );

    });


    /* =========================================================
       FORM SUBMIT
    ========================================================= */

    form.addEventListener(
        "submit",
        event => {

            formMessage.className =
                "form-message";

            formMessage.textContent = "";


            if (!validateForm()) {

                event.preventDefault();

                formMessage.textContent =
                    "Please check the highlighted fields and try again.";

                formMessage.className =
                    "form-message show error";

                window.scrollTo({
                    top:
                        form.getBoundingClientRect().top +
                        window.scrollY -
                        100,
                    behavior: "smooth"
                });

                return;

            }


            /*
             * Important:
             * Do NOT preventDefault here.
             *
             * Flask will receive the normal POST request.
             */

            submitButton.disabled = true;


            const buttonText =
                submitButton.querySelector(
                    ".button-text"
                );


            if (buttonText) {
                buttonText.textContent =
                    "Posting Job...";
            }

        }
    );


    /* =========================================================
       INITIAL LOAD
    ========================================================= */

    loadCategories();

});
