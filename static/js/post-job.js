/* ============================================================
   S. F WORKS — POST JOB
   Professional Job Posting Controller
   ============================================================ */

"use strict";


/* ============================================================
   CONFIGURATION
============================================================ */

const POST_JOB_CONFIG = {

    API_BASE: "/api/jobs",

    CREATE_ENDPOINT: "/api/jobs/create",

    CATEGORIES_ENDPOINT: "/api/jobs/categories",

    REDIRECT_AFTER_SUCCESS: "/jobs",

    MAX_TITLE_LENGTH: 200,

    MAX_DESCRIPTION_LENGTH: 5000

};


/* ============================================================
   DOM READY
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initPostJobPage();

    }
);


/* ============================================================
   INITIALIZE
============================================================ */

async function initPostJobPage() {

    const form = document.getElementById(
        "postJobForm"
    );

    if (!form) {

        console.warn(
            "S. F Works: Post job form not found."
        );

        return;
    }


    setupFormValidation(
        form
    );


    setupNumberValidation();


    await loadCategories();


    form.addEventListener(
        "submit",
        handleJobSubmit
    );

}


/* ============================================================
   LOAD CATEGORIES
============================================================ */

async function loadCategories() {

    const categorySelect =
        document.getElementById(
            "jobCategory"
        );


    if (!categorySelect) {

        return;
    }


    try {

        setCategoryLoading(
            categorySelect,
            true
        );


        const response =
            await fetch(
                POST_JOB_CONFIG
                    .CATEGORIES_ENDPOINT,
                {
                    method: "GET",

                    headers: {
                        "Accept":
                            "application/json"
                    },

                    credentials: "same-origin"
                }
            );


        const result =
            await parseJSONResponse(
                response
            );


        if (!response.ok) {

            throw new Error(
                result.message ||
                "Unable to load categories."
            );
        }


        const categories =
            Array.isArray(
                result.categories
            )
                ? result.categories
                : [];


        populateCategories(
            categorySelect,
            categories
        );


    } catch (error) {

        console.error(
            "Category loading error:",
            error
        );


        showToast(
            "Unable to load job categories.",
            "error"
        );


    } finally {

        setCategoryLoading(
            categorySelect,
            false
        );

    }

}


/* ============================================================
   POPULATE CATEGORY SELECT
============================================================ */

function populateCategories(
    select,
    categories
) {

    select.innerHTML = "";


    const defaultOption =
        document.createElement(
            "option"
        );


    defaultOption.value = "";

    defaultOption.textContent =
        "Select category";

    defaultOption.disabled = true;

    defaultOption.selected = true;


    select.appendChild(
        defaultOption
    );


    categories.forEach(
        category => {

            if (
                !category ||
                !category.id
            ) {

                return;
            }


            const option =
                document.createElement(
                    "option"
                );


            option.value =
                String(
                    category.id
                );


            option.textContent =
                category.name ||
                "Unnamed category";


            select.appendChild(
                option
            );

        }
    );

}


/* ============================================================
   CATEGORY LOADING STATE
============================================================ */

function setCategoryLoading(
    select,
    loading
) {

    if (!select) {

        return;
    }


    if (loading) {

        select.disabled = true;

        select.innerHTML = "";

        const option =
            document.createElement(
                "option"
            );

        option.textContent =
            "Loading categories...";

        option.selected = true;

        select.appendChild(
            option
        );

    } else {

        select.disabled = false;

    }

}


/* ============================================================
   FORM VALIDATION
============================================================ */

function setupFormValidation(
    form
) {

    const title =
        document.getElementById(
            "jobTitle"
        );

    const description =
        document.getElementById(
            "jobDescription"
        );

    const location =
        document.getElementById(
            "jobLocation"
        );


    if (title) {

        title.addEventListener(
            "input",
            () => {

                clearFieldError(
                    title
                );

                enforceMaxLength(
                    title,
                    POST_JOB_CONFIG
                        .MAX_TITLE_LENGTH
                );

            }
        );

    }


    if (description) {

        description.addEventListener(
            "input",
            () => {

                clearFieldError(
                    description
                );

                enforceMaxLength(
                    description,
                    POST_JOB_CONFIG
                        .MAX_DESCRIPTION_LENGTH
                );

            }
        );

    }


    if (location) {

        location.addEventListener(
            "input",
            () => {

                clearFieldError(
                    location
                );

            }
        );

    }

}


/* ============================================================
   NUMBER VALIDATION
============================================================ */

function setupNumberValidation() {

    const minimum =
        document.getElementById(
            "budgetMin"
        );

    const maximum =
        document.getElementById(
            "budgetMax"
        );


    if (
        minimum &&
        maximum
    ) {

        const validateBudget =
            () => {

                const min =
                    parseFloat(
                        minimum.value
                    );

                const max =
                    parseFloat(
                        maximum.value
                    );


                if (
                    !Number.isNaN(min) &&
                    !Number.isNaN(max) &&
                    min > max
                ) {

                    setFieldError(
                        maximum,
                        "Maximum budget must be greater than or equal to minimum budget."
                    );

                } else {

                    clearFieldError(
                        maximum
                    );

                }

            };


        minimum.addEventListener(
            "input",
            validateBudget
        );


        maximum.addEventListener(
            "input",
            validateBudget
        );

    }

}


/* ============================================================
   SUBMIT JOB
============================================================ */

async function handleJobSubmit(
    event
) {

    event.preventDefault();


    const form =
        event.currentTarget;


    if (
        form.dataset.submitting ===
        "true"
    ) {

        return;
    }


    const validation =
        validateJobForm(
            form
        );


    if (!validation.valid) {

        showToast(
            validation.message,
            "error"
        );

        if (
            validation.field
        ) {

            validation.field.focus();

        }

        return;
    }


    const payload =
        collectJobData(
            form
        );


    setSubmittingState(
        form,
        true
    );


    try {

        const token =
            getAccessToken();


        if (!token) {

            showToast(
                "Please login as a customer before posting a job.",
                "error"
            );


            setSubmittingState(
                form,
                false
            );


            setTimeout(
                () => {

                    window.location.href =
                        "/login?next=/post-job";

                },
                1200
            );


            return;
        }


        const response =
            await fetch(
                POST_JOB_CONFIG
                    .CREATE_ENDPOINT,
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
            await parseJSONResponse(
                response
            );


        if (
            response.status === 401
        ) {

            handleUnauthorized();

            return;
        }


        if (
            response.status === 403
        ) {

            showToast(
                result.message ||
                "Only customer accounts can post jobs.",
                "error"
            );

            return;
        }


        if (!response.ok) {

            throw new Error(
                result.message ||
                "Unable to post your job."
            );
        }


        showToast(
            result.message ||
            "Job posted successfully!",
            "success"
        );


        form.reset();


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

        } else {

            setTimeout(
                () => {

                    window.location.href =
                        POST_JOB_CONFIG
                            .REDIRECT_AFTER_SUCCESS;

                },
                900
            );

        }


    } catch (error) {

        console.error(
            "Job submission error:",
            error
        );


        showToast(
            error.message ||
            "Something went wrong. Please try again.",
            "error"
        );


    } finally {

        setSubmittingState(
            form,
            false
        );

    }

}


/* ============================================================
   VALIDATE JOB FORM
============================================================ */

function validateJobForm(
    form
) {

    const title =
        document.getElementById(
            "jobTitle"
        );

    const description =
        document.getElementById(
            "jobDescription"
        );

    const category =
        document.getElementById(
            "jobCategory"
        );

    const location =
        document.getElementById(
            "jobLocation"
        );

    const budgetMin =
        document.getElementById(
            "budgetMin"
        );

    const budgetMax =
        document.getElementById(
            "budgetMax"
        );


    clearAllFieldErrors(
        form
    );


    if (
        !title ||
        !title.value.trim()
    ) {

        return validationError(
            title,
            "Job title is required."
        );

    }


    if (
        title.value.trim().length < 3
    ) {

        return validationError(
            title,
            "Job title must contain at least 3 characters."
        );

    }


    if (
        title.value.trim().length >
        POST_JOB_CONFIG
            .MAX_TITLE_LENGTH
    ) {

        return validationError(
            title,
            "Job title is too long."
        );

    }


    if (
        !description ||
        !description.value.trim()
    ) {

        return validationError(
            description,
            "Job description is required."
        );

    }


    if (
        description.value.trim().length < 10
    ) {

        return validationError(
            description,
            "Please provide a little more detail about the work."
        );

    }


    if (
        !category ||
        !category.value
    ) {

        return validationError(
            category,
            "Please select a job category."
        );

    }


    if (
        !location ||
        !location.value.trim()
    ) {

        return validationError(
            location,
            "Work location is required."
        );

    }


    const min =
        budgetMin &&
        budgetMin.value !== ""
            ? parseFloat(
                budgetMin.value
            )
            : null;


    const max =
        budgetMax &&
        budgetMax.value !== ""
            ? parseFloat(
                budgetMax.value
            )
            : null;


    if (
        min !== null &&
        (
            Number.isNaN(min) ||
            min < 0
        )
    ) {

        return validationError(
            budgetMin,
            "Please enter a valid minimum budget."
        );

    }


    if (
        max !== null &&
        (
            Number.isNaN(max) ||
            max < 0
        )
    ) {

        return validationError(
            budgetMax,
            "Please enter a valid maximum budget."
        );

    }


    if (
        min !== null &&
        max !== null &&
        min > max
    ) {

        return validationError(
            budgetMax,
            "Maximum budget cannot be lower than minimum budget."
        );

    }


    return {
        valid: true
    };

}


/* ============================================================
   COLLECT FORM DATA
============================================================ */

function collectJobData(
    form
) {

    const getValue =
        id => {

            const element =
                document.getElementById(
                    id
                );

            return element
                ? element.value.trim()
                : "";

        };


    const getNumber =
        id => {

            const value =
                getValue(id);


            if (!value) {

                return null;

            }


            const number =
                Number(value);


            return Number.isFinite(
                number
            )
                ? number
                : null;

        };


    return {

        title:
            getValue(
                "jobTitle"
            ),

        description:
            getValue(
                "jobDescription"
            ),

        category_id:
            Number(
                getValue(
                    "jobCategory"
                )
            ),

        budget_min:
            getNumber(
                "budgetMin"
            ),

        budget_max:
            getNumber(
                "budgetMax"
            ),

        location:
            getValue(
                "jobLocation"
            ),

        city:
            getValue(
                "jobCity"
            ) || null,

        state:
            getValue(
                "jobState"
            ) || null,

        pincode:
            getValue(
                "jobPincode"
            ) || null,

        priority:
            getValue(
                "jobPriority"
            ) || "normal"

    };

}


/* ============================================================
   ACCESS TOKEN
============================================================ */

function getAccessToken() {

    const possibleKeys = [

        "access_token",

        "accessToken",

        "jwt_token",

        "jwtToken",

        "token",

        "authToken"

    ];


    for (
        const key of possibleKeys
    ) {

        const token =
            localStorage.getItem(
                key
            );


        if (
            token &&
            token.trim()
        ) {

            return token.trim();

        }

    }


    /*
     * Support sessionStorage too.
     */

    for (
        const key of possibleKeys
    ) {

        const token =
            sessionStorage.getItem(
                key
            );


        if (
            token &&
            token.trim()
        ) {

            return token.trim();

        }

    }


    return null;

}


/* ============================================================
   UNAUTHORIZED
============================================================ */

function handleUnauthorized() {

    clearPossibleTokens();


    showToast(
        "Your session has expired. Please login again.",
        "error"
    );


    setTimeout(
        () => {

            window.location.href =
                "/login?next=/post-job";

        },
        1000
    );

}


/* ============================================================
   CLEAR TOKENS
============================================================ */

function clearPossibleTokens() {

    const keys = [

        "access_token",
        "accessToken",
        "jwt_token",
        "jwtToken",
        "token",
        "authToken"

    ];


    keys.forEach(
        key => {

            localStorage.removeItem(
                key
            );

            sessionStorage.removeItem(
                key
            );

        }
    );

}


/* ============================================================
   SUBMITTING STATE
============================================================ */

function setSubmittingState(
    form,
    submitting
) {

    form.dataset.submitting =
        submitting
            ? "true"
            : "false";


    const button =
        form.querySelector(
            'button[type="submit"]'
        );


    if (!button) {

        return;
    }


    if (submitting) {

        button.disabled = true;

        button.dataset.originalText =
            button.textContent.trim();

        button.textContent =
            "Posting Job...";

        button.setAttribute(
            "aria-busy",
            "true"
        );

    } else {

        button.disabled = false;

        button.textContent =
            button.dataset.originalText ||
            "Post Job";

        button.removeAttribute(
            "aria-busy"
        );

    }

}


/* ============================================================
   FIELD ERROR
============================================================ */

function setFieldError(
    field,
    message
) {

    if (!field) {

        return;
    }


    field.classList.add(
        "is-invalid"
    );


    field.setAttribute(
        "aria-invalid",
        "true"
    );


    let errorElement =
        document.getElementById(
            `${field.id}Error`
        );


    if (!errorElement) {

        errorElement =
            document.createElement(
                "small"
            );

        errorElement.id =
            `${field.id}Error`;

        errorElement.className =
            "form-error";


        field.insertAdjacentElement(
            "afterend",
            errorElement
        );

    }


    errorElement.textContent =
        message;

}


/* ============================================================
   CLEAR FIELD ERROR
============================================================ */

function clearFieldError(
    field
) {

    if (!field) {

        return;
    }


    field.classList.remove(
        "is-invalid"
    );


    field.removeAttribute(
        "aria-invalid"
    );


    const errorElement =
        document.getElementById(
            `${field.id}Error`
        );


    if (errorElement) {

        errorElement.remove();

    }

}


/* ============================================================
   CLEAR ALL ERRORS
============================================================ */

function clearAllFieldErrors(
    form
) {

    const invalidFields =
        form.querySelectorAll(
            ".is-invalid"
        );


    invalidFields.forEach(
        field => {

            clearFieldError(
                field
            );

        }
    );


    const errors =
        form.querySelectorAll(
            ".form-error"
        );


    errors.forEach(
        error => {

            error.remove();

        }
    );

}


/* ============================================================
   VALIDATION ERROR HELPER
============================================================ */

function validationError(
    field,
    message
) {

    setFieldError(
        field,
        message
    );


    return {

        valid: false,

        field: field,

        message: message

    };

}


/* ============================================================
   MAX LENGTH
============================================================ */

function enforceMaxLength(
    field,
    maxLength
) {

    if (
        field.value.length >
        maxLength
    ) {

        field.value =
            field.value.substring(
                0,
                maxLength
            );

    }

}


/* ============================================================
   JSON RESPONSE PARSER
============================================================ */

async function parseJSONResponse(
    response
) {

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";


    if (
        contentType.includes(
            "application/json"
        )
    ) {

        return await response.json();

    }


    const text =
        await response.text();


    return {

        status:
            "error",

        message:
            text ||
            "Unexpected server response."

    };

}


/* ============================================================
   TOAST
============================================================ */

function showToast(
    message,
    type = "info"
) {

    /*
     * Use existing S. F Works toast.js
     * when available.
     */

    if (
        typeof window.showToast ===
        "function"
    ) {

        window.showToast(
            message,
            type
        );

        return;
    }


    /*
     * Fallback toast.
     */

    const toast =
        document.createElement(
            "div"
        );


    toast.className =
        `sf-js-toast sf-js-toast-${type}`;


    toast.textContent =
        message;


    Object.assign(
        toast.style,
        {

            position:
                "fixed",

            bottom:
                "24px",

            left:
                "50%",

            transform:
                "translateX(-50%)",

            zIndex:
                "99999",

            padding:
                "13px 18px",

            borderRadius:
                "10px",

            background:
                "#111827",

            color:
                "#ffffff",

            fontSize:
                "14px",

            fontWeight:
                "600",

            boxShadow:
                "0 10px 30px rgba(0,0,0,.18)",

            maxWidth:
                "calc(100% - 32px)",

            textAlign:
                "center"

        }

    );


    document.body.appendChild(
        toast
    );


    setTimeout(
        () => {

            toast.remove();

        },
        3500
    );

}
