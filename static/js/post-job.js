/* =========================================================
   S. F WORKS — POST JOB
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("postJobForm");

    if (!form) {
        return;
    }


    /* =====================================================
       ELEMENTS
    ====================================================== */

    const categorySelect =
        document.getElementById("jobCategory");

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


    /* =====================================================
       HELPERS
    ====================================================== */

    function showMessage(message, type = "error") {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = message;
        formMessage.className =
            `form-message show ${type}`;

    }


    function clearMessage() {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = "";
        formMessage.className = "form-message";

    }


    function setCategoryStatus(
        message,
        type = ""
    ) {

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


    /* =====================================================
       DESCRIPTION COUNTER
    ====================================================== */

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


    /* =====================================================
       CATEGORY LOADER
    ====================================================== */

    async function loadCategories() {

        if (!categorySelect) {
            return;
        }

        categorySelect.innerHTML = `
            <option value="">
                Loading categories...
            </option>
        `;

        categorySelect.disabled = true;

        setCategoryStatus(
            "Loading available categories...",
            "loading"
        );


        /*
         * IMPORTANT:
         * Your backend should expose:
         *
         * GET /api/categories
         *
         */

        try {

            const response = await fetch(
                "/api/categories",
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
                    `Category API returned ${response.status}`
                );

            }


            const data =
                await response.json();


            /*
             * Supports both:
             *
             * [
             *   {"id":1,"name":"Electrical"}
             * ]
             *
             * and:
             *
             * {
             *   "categories": [...]
             * }
             */

            let categories = [];

            if (Array.isArray(data)) {

                categories = data;

            } else if (
                data &&
                Array.isArray(data.categories)
            ) {

                categories = data.categories;

            } else if (
                data &&
                Array.isArray(data.data)
            ) {

                categories = data.data;

            }


            if (!categories.length) {

                categorySelect.innerHTML = `
                    <option value="">
                        No categories available
                    </option>
                `;

                categorySelect.disabled = true;

                setCategoryStatus(
                    "No active categories were found.",
                    "error"
                );

                return;

            }


            categorySelect.innerHTML = `
                <option value="">
                    Select a category
                </option>
            `;


            categories.forEach(category => {

                if (
                    category.id === undefined ||
                    category.id === null
                ) {
                    return;
                }


                const option =
                    document.createElement("option");


                option.value =
                    category.id;


                option.textContent =
                    category.name ||
                    category.title ||
                    category.category_name ||
                    "Unnamed Category";


                categorySelect.appendChild(option);

            });


            categorySelect.disabled = false;


            setCategoryStatus(
                `${categories.length} categories available`,
                "success"
            );

        } catch (error) {

            console.error(
                "Category loading error:",
                error
            );


            categorySelect.innerHTML = `
                <option value="">
                    Unable to load categories
                </option>
            `;

            categorySelect.disabled = true;


            setCategoryStatus(
                "Unable to load categories. Please refresh the page.",
                "error"
            );

        }

    }


    loadCategories();


    /* =====================================================
       FORM VALIDATION
    ====================================================== */

    function validateForm() {

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


        const category =
            categorySelect
                ?.value;


        const location =
            document
                .getElementById("jobLocation")
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


        if (!title) {

            showMessage(
                "Please enter a job title."
            );

            document
                .getElementById("jobTitle")
                ?.focus();

            return false;

        }


        if (title.length < 5) {

            showMessage(
                "Job title should contain at least 5 characters."
            );

            document
                .getElementById("jobTitle")
                ?.focus();

            return false;

        }


        if (!jobDescription) {

            showMessage(
                "Please describe the work you need."
            );

            description?.focus();

            return false;

        }


        if (jobDescription.length < 20) {

            showMessage(
                "Please provide a little more detail about the job."
            );

            description?.focus();

            return false;

        }


        if (!category) {

            showMessage(
                "Please select a job category."
            );

            categorySelect?.focus();

            return false;

        }


        if (!location) {

            showMessage(
                "Please enter the work location."
            );

            document
                .getElementById("jobLocation")
                ?.focus();

            return false;

        }


        if (
            budgetMin !== "" &&
            budgetMax !== "" &&
            Number(budgetMin) > Number(budgetMax)
        ) {

            showMessage(
                "Minimum budget cannot be greater than maximum budget."
            );

            document
                .getElementById("budgetMin")
                ?.focus();

            return false;

        }


        return true;

    }


    /* =====================================================
       FORM SUBMIT
    ====================================================== */

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            if (!validateForm()) {
                return;
            }


            submitButton.disabled = true;


            const originalButtonHTML =
                submitButton.innerHTML;


            submitButton.innerHTML = `
                <span class="button-text">
                    Publishing...
                </span>
            `;


            try {

                const formData =
                    new FormData(form);


                const payload = {

                    title:
                        formData.get("title"),

                    description:
                        formData.get("description"),

                    category_id:
                        formData.get("category_id"),

                    budget_min:
                        formData.get("budget_min")
                        || null,

                    budget_max:
                        formData.get("budget_max")
                        || null,

                    location:
                        formData.get("location"),

                    city:
                        formData.get("city"),

                    state:
                        formData.get("state"),

                    pincode:
                        formData.get("pincode"),

                    priority:
                        formData.get("priority")

                };


                /*
                 * Change this URL ONLY if your backend
                 * uses a different endpoint.
                 */

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
                                JSON.stringify(payload)
                        }
                    );


                let result = {};

                try {

                    result =
                        await response.json();

                } catch {
                    result = {};
                }


                if (!response.ok) {

                    throw new Error(
                        result.message ||
                        result.error ||
                        "Unable to post your job."
                    );

                }


                showMessage(
                    result.message ||
                    "Your job has been posted successfully.",
                    "success"
                );


                form.reset();

                updateDescriptionCounter();


                /*
                 * Reload categories after reset so
                 * select remains usable.
                 */

                await loadCategories();


            } catch (error) {

                console.error(
                    "Post job error:",
                    error
                );


                showMessage(
                    error.message ||
                    "Something went wrong. Please try again.",
                    "error"
                );


            } finally {

                submitButton.disabled = false;

                submitButton.innerHTML =
                    originalButtonHTML;

            }

        }
    );

});
