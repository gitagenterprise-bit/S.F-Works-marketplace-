document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("postJobForm");

    const categoryPicker =
        document.getElementById("categoryPicker");

    const categoryInput =
        document.getElementById("jobCategory");

    const categoryDropdown =
        document.getElementById("categoryDropdown");

    const categoryList =
        document.getElementById("categoryList");

    const categoryButton =
        document.getElementById("categoryDropdownButton");

    const customButton =
        document.getElementById("customCategoryButton");

    const categoryCount =
        document.getElementById("categoryCount");

    const categoryStatus =
        document.getElementById("categoryStatus");

    const description =
        document.getElementById("jobDescription");

    const descriptionCounter =
        document.getElementById("descriptionCounter");

    const formMessage =
        document.getElementById("formMessage");

    const submitButton =
        document.getElementById("postJobButton");


    let categories = [];


    /* =====================================================
       DESCRIPTION COUNTER
    ===================================================== */

    if (description && descriptionCounter) {

        function updateCounter() {

            descriptionCounter.textContent =
                `${description.value.length} / 5000`;

        }

        description.addEventListener(
            "input",
            updateCounter
        );

        updateCounter();
    }


    /* =====================================================
       CATEGORY DROPDOWN
    ===================================================== */

    function openCategory() {

        if (!categoryPicker) return;

        categoryPicker.classList.add("open");

        if (categoryButton) {
            categoryButton.setAttribute(
                "aria-expanded",
                "true"
            );
        }
    }


    function closeCategory() {

        if (!categoryPicker) return;

        categoryPicker.classList.remove("open");

        if (categoryButton) {
            categoryButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    /* =====================================================
       RENDER CATEGORY LIST
    ===================================================== */

    function renderCategories(searchText = "") {

        if (!categoryList) return;

        const search =
            searchText.trim().toLowerCase();


        const filtered =
            categories.filter(function (category) {

                const name =
                    String(
                        category.name ||
                        category.title ||
                        category.category_name ||
                        ""
                    );

                return name
                    .toLowerCase()
                    .includes(search);
            });


        categoryList.innerHTML = "";


        if (categoryCount) {
            categoryCount.textContent =
                filtered.length;
        }


        if (!filtered.length) {

            categoryList.innerHTML = `
                <div class="category-empty">

                    <strong>
                        No category found
                    </strong>

                    Type your own category below.

                </div>
            `;

            return;
        }


        filtered.forEach(function (category) {

            const name =
                category.name ||
                category.title ||
                category.category_name;


            if (!name) return;


            const button =
                document.createElement("button");


            button.type = "button";

            button.className =
                "category-option";


            button.innerHTML = `
                <span class="category-option-icon">
                    ◈
                </span>

                <span>
                    ${escapeHtml(name)}
                </span>
            `;


            button.addEventListener(
                "click",
                function () {

                    categoryInput.value =
                        name;

                    categoryInput.dataset.categoryId =
                        category.id || "";


                    if (categoryStatus) {

                        categoryStatus.textContent =
                            "Category selected";

                        categoryStatus.className =
                            "category-status success";
                    }


                    closeCategory();
                }
            );


            categoryList.appendChild(button);

        });
    }


    /* =====================================================
       ESCAPE HTML
    ===================================================== */

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent = value;

        return div.innerHTML;
    }


    /* =====================================================
       LOAD CATEGORIES
    ===================================================== */

    async function loadCategories() {

        /*
         * First show a few fallback categories.
         * Therefore input/dropdown works even if
         * API is unavailable.
         */

        categories = [
            {
                id: 1,
                name: "Electrical"
            },
            {
                id: 2,
                name: "Plumbing"
            },
            {
                id: 3,
                name: "Painting"
            },
            {
                id: 4,
                name: "Carpentry"
            },
            {
                id: 5,
                name: "Cleaning"
            },
            {
                id: 6,
                name: "Home Repair"
            },
            {
                id: 7,
                name: "AC & Refrigerator Repair"
            },
            {
                id: 8,
                name: "Computer & Laptop Repair"
            },
            {
                id: 9,
                name: "Mobile Repair"
            },
            {
                id: 10,
                name: "Gardening"
            }
        ];


        renderCategories();


        /*
         * Try loading real categories from backend.
         */

        try {

            const response =
                await fetch(
                    "/api/categories",
                    {
                        method: "GET",
                        headers: {
                            "Accept":
                                "application/json"
                        },
                        credentials:
                            "same-origin"
                    }
                );


            if (!response.ok) {
                return;
            }


            const data =
                await response.json();


            let serverCategories = [];


            if (Array.isArray(data)) {

                serverCategories = data;

            } else if (
                data &&
                Array.isArray(data.categories)
            ) {

                serverCategories =
                    data.categories;

            } else if (
                data &&
                Array.isArray(data.data)
            ) {

                serverCategories =
                    data.data;
            }


            if (serverCategories.length) {

                categories =
                    serverCategories;

                renderCategories();

            }


        } catch (error) {

            console.warn(
                "Category API unavailable. Using fallback categories."
            );

        }


        if (categoryStatus) {

            categoryStatus.textContent =
                "Select a category or type your own.";

            categoryStatus.className =
                "category-status";
        }
    }


    /* =====================================================
       INPUT EVENTS
    ===================================================== */

    if (categoryInput) {

        categoryInput.addEventListener(
            "focus",
            function () {

                openCategory();

                renderCategories(
                    categoryInput.value
                );
            }
        );


        categoryInput.addEventListener(
            "click",
            function () {

                openCategory();

                renderCategories(
                    categoryInput.value
                );
            }
        );


        categoryInput.addEventListener(
            "input",
            function () {

                /*
                 * User is typing manually,
                 * so selected category ID is removed.
                 */

                delete categoryInput.dataset.categoryId;


                openCategory();


                renderCategories(
                    categoryInput.value
                );


                if (categoryStatus) {

                    categoryStatus.textContent =
                        categoryInput.value.trim()
                            ? "Custom category"
                            : "Select a category or type your own.";

                    categoryStatus.className =
                        "category-status";
                }
            }
        );
    }


    /* =====================================================
       ARROW BUTTON
    ===================================================== */

    if (categoryButton) {

        categoryButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                if (
                    categoryPicker.classList.contains("open")
                ) {

                    closeCategory();

                } else {

                    openCategory();

                    renderCategories(
                        categoryInput
                            ? categoryInput.value
                            : ""
                    );
                }
            }
        );
    }


    /* =====================================================
       CUSTOM CATEGORY
    ===================================================== */

    if (customButton) {

        customButton.addEventListener(
            "click",
            function () {

                openCategory();


                if (categoryInput) {

                    categoryInput.focus();

                    categoryInput.select();

                    delete categoryInput.dataset.categoryId;
                }


                if (categoryStatus) {

                    categoryStatus.textContent =
                        "Type your custom category.";

                    categoryStatus.className =
                        "category-status success";
                }
            }
        );
    }


    /* =====================================================
       CLICK OUTSIDE
    ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                categoryPicker &&
                !categoryPicker.contains(
                    event.target
                )
            ) {

                closeCategory();
            }
        }
    );


    /* =====================================================
       FORM SUBMIT
    ===================================================== */

    if (form) {

        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                if (formMessage) {

                    formMessage.textContent = "";

                    formMessage.className =
                        "form-message";
                }


                const title =
                    document
                        .getElementById("jobTitle")
                        ?.value
                        .trim();


                const jobDescription =
                    description
                        ?.value
                        .trim();


                const categoryName =
                    categoryInput
                        ?.value
                        .trim();


                const location =
                    document
                        .getElementById("jobLocation")
                        ?.value
                        .trim();


                if (!title) {

                    showFormError(
                        "Please enter a job title."
                    );

                    return;
                }


                if (jobDescription.length < 20) {

                    showFormError(
                        "Please provide at least 20 characters in the description."
                    );

                    return;
                }


                if (!categoryName) {

                    showFormError(
                        "Please select or type a category."
                    );

                    categoryInput?.focus();

                    return;
                }


                if (!location) {

                    showFormError(
                        "Please enter the work location."
                    );

                    return;
                }


                /*
                 * IMPORTANT
                 *
                 * Existing category:
                 * category_id = selected ID
                 *
                 * Custom category:
                 * category_id = null
                 */

                const payload = {

                    title: title,

                    description:
                        jobDescription,

                    category_id:
                        categoryInput
                            ?.dataset
                            .categoryId || null,

                    category_name:
                        categoryName,

                    budget_min:
                        document
                            .getElementById("budgetMin")
                            ?.value || null,

                    budget_max:
                        document
                            .getElementById("budgetMax")
                            ?.value || null,

                    location:
                        location,

                    city:
                        document
                            .getElementById("jobCity")
                            ?.value
                            .trim() || "",

                    state:
                        document
                            .getElementById("jobState")
                            ?.value
                            .trim() || "",

                    pincode:
                        document
                            .getElementById("jobPincode")
                            ?.value
                            .trim() || "",

                    priority:
                        document
                            .getElementById("jobPriority")
                            ?.value || "normal"
                };


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.innerHTML = `
                        <span class="button-text">
                            Publishing...
                        </span>
                    `;
                }


                try {

                    const response =
                        await fetch(
                            "/api/jobs",
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
                            .catch(() => ({}));


                    if (!response.ok) {

                        throw new Error(
                            result.message ||
                            result.error ||
                            "Unable to post job."
                        );
                    }


                    if (formMessage) {

                        formMessage.textContent =
                            result.message ||
                            "Job posted successfully.";

                        formMessage.className =
                            "form-message show success";
                    }


                    form.reset();


                    if (categoryInput) {

                        delete categoryInput
                            .dataset
                            .categoryId;
                    }


                    if (descriptionCounter) {

                        descriptionCounter.textContent =
                            "0 / 5000";
                    }


                } catch (error) {

                    console.error(
                        "Post job error:",
                        error
                    );


                    showFormError(
                        error.message ||
                        "Something went wrong. Please try again."
                    );


                } finally {

                    if (submitButton) {

                        submitButton.disabled =
                            false;

                        submitButton.innerHTML = `
                            <span class="button-icon">
                                +
                            </span>

                            <span class="button-text">
                                Post Job
                            </span>

                            <span class="button-arrow">
                                →
                            </span>
                        `;
                    }
                }
            }
        );
    }


    /* =====================================================
       FORM ERROR
    ===================================================== */

    function showFormError(message) {

        if (!formMessage) return;

        formMessage.textContent =
            message;

        formMessage.className =
            "form-message show error";
    }


    /* =====================================================
       START
    ===================================================== */

    loadCategories();

});
