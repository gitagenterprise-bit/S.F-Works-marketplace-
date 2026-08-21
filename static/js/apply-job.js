/* ============================================================
   S.F WORKS — PREMIUM JOB APPLICATION
============================================================ */

(function () {

    "use strict";


    /* ========================================================
       CONFIG
    ======================================================== */

    const API_BASE = "/api/jobs";


    const jobId =
        window.JOB_ID ||
        getJobIdFromUrl();


    /* ========================================================
       DOM
    ======================================================== */

    const form =
        document.getElementById(
            "jobApplyForm"
        );


    const submitButton =
        document.getElementById(
            "submitApplication"
        );


    const submitText =
        document.getElementById(
            "submitText"
        );


    const formAlert =
        document.getElementById(
            "formAlert"
        );


    const successState =
        document.getElementById(
            "successState"
        );


    const message =
        document.getElementById(
            "message"
        );


    const messageCount =
        document.getElementById(
            "messageCount"
        );


    const mobile =
        document.getElementById(
            "mobile"
        );


    const proposedAmount =
        document.getElementById(
            "proposedAmount"
        );


    const availability =
        document.getElementById(
            "availability"
        );


    /* ========================================================
       INIT
    ======================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        init
    );


    async function init() {

        if (!jobId) {

            showAlert(
                "Unable to identify this job.",
                "error"
            );

            return;
        }


        setupMessageCounter();

        setupMobileValidation();

        setupFormValidation();


        await loadCurrentUser();

        await loadJob();


        checkExistingApplication();
    }


    /* ========================================================
       GET JOB ID
    ======================================================== */

    function getJobIdFromUrl() {

        const parts =
            window.location.pathname
                .split("/")
                .filter(Boolean);


        const last =
            parts[parts.length - 1];


        const id =
            Number(last);


        return Number.isInteger(id) &&
               id > 0
            ? id
            : null;
    }


    /* ========================================================
       API FETCH
    ======================================================== */

    async function apiFetch(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                {
                    credentials: "include",
                    ...options,
                    headers: {
                        "Content-Type":
                            "application/json",
                        ...(options.headers || {})
                    }
                }
            );


        let data = null;


        try {

            data =
                await response.json();

        } catch (error) {

            data = null;
        }


        if (!response.ok) {

            const message =
                data?.message ||
                "Something went wrong. Please try again.";


            const error =
                new Error(message);


            error.status =
                response.status;


            error.data =
                data;


            throw error;
        }


        return data;
    }


    /* ========================================================
       LOAD CURRENT USER
    ======================================================== */

    async function loadCurrentUser() {

        try {

            /*
             * Change this endpoint only if your project
             * uses a different current-user API.
             */

            const data =
                await apiFetch(
                    "/api/auth/me"
                );


            const user =
                data?.user;


            if (!user) {

                return;
            }


            const nameInput =
                document.getElementById(
                    "workerName"
                );


            if (nameInput) {

                nameInput.value =
                    user.full_name || "";
            }


            if (user.phone) {

                mobile.value =
                    normalizeMobile(
                        user.phone
                    );
            }


            /*
             * Only worker should apply.
             */

            if (
                user.role &&
                user.role !== "worker"
            ) {

                disableApplication(
                    "Only workers can apply for jobs."
                );

                return;
            }


            if (
                user.is_active === false
            ) {

                disableApplication(
                    "Your account is currently disabled."
                );
            }

        } catch (error) {

            /*
             * If /api/auth/me does not exist,
             * the submit API will still handle auth.
             */

            console.warn(
                "Could not load current user:",
                error
            );
        }
    }


    /* ========================================================
       LOAD JOB
    ======================================================== */

    async function loadJob() {

        try {

            const data =
                await apiFetch(
                    `${API_BASE}/${jobId}`
                );


            const job =
                data?.job;


            if (!job) {

                throw new Error(
                    "Job information could not be loaded."
                );
            }


            renderJob(job);


        } catch (error) {

            showAlert(
                error.message,
                "error"
            );


            disableApplication(
                "This job is unavailable."
            );
        }
    }


    /* ========================================================
       RENDER JOB
    ======================================================== */

    function renderJob(job) {

        setText(
            "jobTitle",
            job.title || "Job"
        );


        setText(
            "jobCategory",
            job.category?.name ||
            "General"
        );


        setText(
            "jobBudget",
            formatBudget(job)
        );


        setText(
            "jobLocation",
            formatLocation(job)
        );


        setText(
            "jobDescription",
            job.description ||
            "No description provided."
        );


        const status =
            document.getElementById(
                "jobStatus"
            );


        if (status) {

            status.textContent =
                formatStatus(
                    job.status
                );


            if (
                job.status !== "open"
            ) {

                status.classList.add(
                    "closed"
                );

                disableApplication(
                    "This job is no longer accepting applications."
                );
            }
        }
    }


    /* ========================================================
       FORMAT BUDGET
    ======================================================== */

    function formatBudget(job) {

        const min =
            job.budget?.min;

        const max =
            job.budget?.max;


        if (
            min !== null &&
            min !== undefined &&
            max !== null &&
            max !== undefined
        ) {

            return (
                `₹${formatNumber(min)} - ` +
                `₹${formatNumber(max)}`
            );
        }


        if (
            min !== null &&
            min !== undefined
        ) {

            return `₹${formatNumber(min)}`;
        }


        if (
            max !== null &&
            max !== undefined
        ) {

            return `₹${formatNumber(max)}`;
        }


        return "Budget not specified";
    }


    /* ========================================================
       FORMAT LOCATION
    ======================================================== */

    function formatLocation(job) {

        const parts = [
            job.location,
            job.city,
            job.state
        ].filter(
            value =>
                value &&
                String(value).trim()
        );


        if (!parts.length) {

            return "Location not specified";
        }


        return [
            ...new Set(parts)
        ].join(", ");
    }


    /* ========================================================
       NUMBER
    ======================================================== */

    function formatNumber(value) {

        const number =
            Number(value);


        if (
            !Number.isFinite(number)
        ) {

            return "0";
        }


        return number.toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 2
            }
        );
    }


    /* ========================================================
       STATUS
    ======================================================== */

    function formatStatus(status) {

        if (!status) {

            return "Open";
        }


        return String(status)
            .charAt(0)
            .toUpperCase()
            +
            String(status)
                .slice(1);
    }


    /* ========================================================
       TEXT HELPER
    ======================================================== */

    function setText(
        id,
        value
    ) {

        const element =
            document.getElementById(id);


        if (element) {

            element.textContent =
                value;
        }
    }


    /* ========================================================
       MOBILE
    ======================================================== */

    function setupMobileValidation() {

        if (!mobile) {

            return;
        }


        mobile.addEventListener(
            "input",
            function () {

                this.value =
                    this.value
                        .replace(/\D/g, "")
                        .slice(0, 10);

                clearFieldError(
                    "mobile"
                );
            }
        );


        mobile.addEventListener(
            "blur",
            function () {

                validateMobile();
            }
        );
    }


    function normalizeMobile(value) {

        if (!value) {

            return "";
        }


        return String(value)
            .replace(/\D/g, "")
            .slice(-10);
    }


    function validateMobile() {

        const value =
            mobile.value.trim();


        const error =
            document.getElementById(
                "mobileError"
            );


        if (!value) {

            showFieldError(
                mobile,
                error,
                "Mobile number is required."
            );

            return false;
        }


        if (!/^[6-9]\d{9}$/.test(value)) {

            showFieldError(
                mobile,
                error,
                "Enter a valid 10-digit Indian mobile number."
            );

            return false;
        }


        clearFieldError(
            "mobile"
        );


        return true;
    }


    /* ========================================================
       MESSAGE COUNTER
    ======================================================== */

    function setupMessageCounter() {

        if (!message) {

            return;
        }


        updateMessageCount();


        message.addEventListener(
            "input",
            updateMessageCount
        );
    }


    function updateMessageCount() {

        if (!message || !messageCount) {

            return;
        }


        messageCount.textContent =
            message.value.length;
    }


    /* ========================================================
       FORM VALIDATION
    ======================================================== */

    function setupFormValidation() {

        if (!form) {

            return;
        }


        form.addEventListener(
            "submit",
            handleSubmit
        );


        proposedAmount?.addEventListener(
            "input",
            function () {

                clearFieldError(
                    "proposedAmount"
                );
            }
        );


        availability?.addEventListener(
            "input",
            function () {

                clearFieldError(
                    "availability"
                );
            }
        );
    }


    function validateForm() {

        let valid = true;


        if (!validateMobile()) {

            valid = false;
        }


        const amount =
            Number(
                proposedAmount.value
            );


        const amountError =
            document.getElementById(
                "amountError"
            );


        if (
            !proposedAmount.value.trim()
        ) {

            showFieldError(
                proposedAmount,
                amountError,
                "Proposed amount is required."
            );

            valid = false;

        } else if (
            !Number.isFinite(amount) ||
            amount <= 0
        ) {

            showFieldError(
                proposedAmount,
                amountError,
                "Enter a valid proposed amount."
            );

            valid = false;

        } else {

            clearFieldError(
                "proposedAmount"
            );
        }


        const availabilityValue =
            availability.value.trim();


        const availabilityError =
            document.getElementById(
                "availabilityError"
            );


        if (!availabilityValue) {

            showFieldError(
                availability,
                availabilityError,
                "Please enter your availability."
            );

            valid = false;

        } else {

            clearFieldError(
                "availability"
            );
        }


        return valid;
    }


    /* ========================================================
       SUBMIT
    ======================================================== */

    async function handleSubmit(
        event
    ) {

        event.preventDefault();


        hideAlert();


        if (!validateForm()) {

            showAlert(
                "Please correct the highlighted fields.",
                "error"
            );

            return;
        }


        setLoading(
            true
        );


        const payload = {

            proposed_amount:
                Number(
                    proposedAmount.value
                ),

            message:
                message.value.trim()
                || null,

            availability:
                availability.value.trim()
                || null
        };


        try {

            const data =
                await apiFetch(
                    `${API_BASE}/${jobId}/apply`,
                    {
                        method: "POST",
                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            showSuccess(
                data?.message ||
                "Application submitted successfully."
            );


        } catch (error) {

            console.error(
                "Application submit error:",
                error
            );


            if (
                error.status === 401 ||
                error.status === 422
            ) {

                showAlert(
                    "Please login as a worker before applying.",
                    "error"
                );

            } else {

                showAlert(
                    error.message ||
                    "Unable to submit application.",
                    "error"
                );
            }


        } finally {

            setLoading(
                false
            );
        }
    }


    /* ========================================================
       EXISTING APPLICATION
    ======================================================== */

    function checkExistingApplication() {

        /*
         * The current backend already prevents duplicate
         * applications with:
         *
         * job_id + worker_id
         *
         * Therefore the definitive check happens server-side.
         *
         * We intentionally don't create an extra API request
         * here unless you add a dedicated endpoint later.
         */
    }


    /* ========================================================
       SUCCESS
    ======================================================== */

    function showSuccess(
        messageText
    ) {

        if (form) {

            form.style.display =
                "none";
        }


        const cardHeader =
            document.querySelector(
                ".application-card-header"
            );


        if (cardHeader) {

            cardHeader.style.display =
                "none";
        }


        if (formAlert) {

            formAlert.style.display =
                "none";
        }


        if (successState) {

            successState.classList.add(
                "show"
            );


            const paragraph =
                successState.querySelector(
                    "p"
                );


            if (paragraph) {

                paragraph.textContent =
                    messageText;
            }
        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }


    /* ========================================================
       ALERT
    ======================================================== */

    function showAlert(
        messageText,
        type = "error"
    ) {

        if (!formAlert) {

            return;
        }


        formAlert.textContent =
            messageText;


        formAlert.className =
            `form-alert show ${type}`;
    }


    function hideAlert() {

        if (!formAlert) {

            return;
        }


        formAlert.className =
            "form-alert";

        formAlert.textContent =
            "";
    }


    /* ========================================================
       FIELD ERRORS
    ======================================================== */

    function showFieldError(
        input,
        errorElement,
        messageText
    ) {

        if (input) {

            input.classList.add(
                "input-error"
            );
        }


        if (errorElement) {

            errorElement.textContent =
                messageText;

            errorElement.classList.add(
                "show"
            );
        }
    }


    function clearFieldError(
        inputId
    ) {

        const input =
            document.getElementById(
                inputId
            );


        if (input) {

            input.classList.remove(
                "input-error"
            );
        }


        const error =
            document.getElementById(
                `${inputId}Error`
            );


        if (error) {

            error.textContent =
                "";

            error.classList.remove(
                "show"
            );
        }
    }


    /* ========================================================
       LOADING
    ======================================================== */

    function setLoading(
        loading
    ) {

        if (!submitButton) {

            return;
        }


        submitButton.disabled =
            loading;


        if (loading) {

            submitButton.classList.add(
                "loading"
            );


            if (submitText) {

                submitText.textContent =
                    "Submitting...";
            }

        } else {

            submitButton.classList.remove(
                "loading"
            );


            if (submitText) {

                submitText.textContent =
                    "Submit Application";
            }
        }
    }


    /* ========================================================
       DISABLE
    ======================================================== */

    function disableApplication(
        reason
    ) {

        if (!submitButton) {

            return;
        }


        submitButton.disabled =
            true;


        if (submitText) {

            submitText.textContent =
                reason ||
                "Application unavailable";
        }


        submitButton.style.opacity =
            "0.55";
    }


})();
