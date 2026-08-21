document.addEventListener(
    "DOMContentLoaded",
    () => {

        "use strict";


        // =====================================================
        // ELEMENTS
        // =====================================================

        const page =
            document.getElementById(
                "jobDetailsPage"
            );

        if (!page) {
            return;
        }


        const jobId =
            page.dataset.jobId;

        const apiUrl =
            page.dataset.apiUrl;


        const loading =
            document.getElementById(
                "jobLoading"
            );

        const errorBox =
            document.getElementById(
                "jobError"
            );

        const errorMessage =
            document.getElementById(
                "jobErrorMessage"
            );

        const content =
            document.getElementById(
                "jobContent"
            );


        // =====================================================
        // HELPERS
        // =====================================================

        function escapeHtml(value) {

            const div =
                document.createElement(
                    "div"
                );

            div.textContent =
                value == null
                    ? ""
                    : String(value);

            return div.innerHTML;
        }


        function formatDate(value) {

            if (!value) {
                return "Recently";
            }


            const date =
                new Date(value);


            if (
                Number.isNaN(
                    date.getTime()
                )
            ) {

                return "Recently";

            }


            return date.toLocaleDateString(
                "en-IN",
                {
                    day: "numeric",
                    month: "short",
                    year: "numeric"
                }
            );

        }


        function formatMoney(value) {

            if (
                value === null ||
                value === undefined ||
                value === ""
            ) {

                return null;

            }


            const number =
                Number(value);


            if (
                !Number.isFinite(number)
            ) {

                return null;

            }


            return new Intl.NumberFormat(
                "en-IN",
                {
                    maximumFractionDigits: 0
                }
            ).format(number);

        }


        function setText(
            id,
            value
        ) {

            const element =
                document.getElementById(
                    id
                );

            if (element) {

                element.textContent =
                    value ?? "";

            }

        }


        // =====================================================
        // ERROR STATE
        // =====================================================

        function showError(
            message
        ) {

            loading.hidden =
                true;

            content.hidden =
                true;

            errorBox.hidden =
                false;

            errorMessage.textContent =
                message ||
                "Unable to load this job.";

        }


        // =====================================================
        // BUDGET
        // =====================================================

        function renderBudget(
            budget
        ) {

            const element =
                document.getElementById(
                    "jobBudget"
                );


            if (!element) {
                return;
            }


            if (!budget) {

                element.textContent =
                    "Budget not specified";

                return;

            }


            const minimum =
                formatMoney(
                    budget.min
                );

            const maximum =
                formatMoney(
                    budget.max
                );


            if (
                minimum !== null &&
                maximum !== null
            ) {

                element.textContent =
                    `₹${minimum} – ₹${maximum}`;

                return;

            }


            if (minimum !== null) {

                element.textContent =
                    `From ₹${minimum}`;

                return;

            }


            if (maximum !== null) {

                element.textContent =
                    `Up to ₹${maximum}`;

                return;

            }


            element.textContent =
                "Budget not specified";

        }


        // =====================================================
        // LOCATION
        // =====================================================

        function renderLocation(
            job
        ) {

            const parts = [
                job.city,
                job.state,
                job.pincode
            ].filter(
                value =>
                    value !== null &&
                    value !== undefined &&
                    String(value).trim()
            );


            setText(
                "jobLocation",
                job.location || "Location not specified"
            );


            setText(
                "jobAddress",
                parts.join(", ")
            );


            if (
                job.latitude !== null &&
                job.latitude !== undefined &&
                job.longitude !== null &&
                job.longitude !== undefined
            ) {

                const map =
                    document.getElementById(
                        "jobMap"
                    );


                if (map) {

                    map.hidden =
                        false;

                }

            }

        }


        // =====================================================
        // IMAGES
        // =====================================================

        function renderImages(
            images
        ) {

            const card =
                document.getElementById(
                    "jobImagesCard"
                );

            const container =
                document.getElementById(
                    "jobImages"
                );


            if (
                !card ||
                !container
            ) {

                return;

            }


            if (
                !Array.isArray(images) ||
                images.length === 0
            ) {

                card.hidden =
                    true;

                return;

            }


            container.innerHTML =
                "";


            images.forEach(
                image => {

                    const imagePath =
                        image.image_path;


                    if (!imagePath) {
                        return;
                    }


                    const wrapper =
                        document.createElement(
                            "div"
                        );

                    wrapper.className =
                        "job-image-item";


                    const img =
                        document.createElement(
                            "img"
                        );


                    img.src =
                        imagePath;

                    img.alt =
                        "Job image";

                    img.loading =
                        "lazy";


                    img.addEventListener(
                        "error",
                        () => {

                            wrapper.remove();

                        }
                    );


                    wrapper.appendChild(
                        img
                    );

                    container.appendChild(
                        wrapper
                    );

                }
            );


            if (
                container.children.length
            ) {

                card.hidden =
                    false;

            }

        }


        // =====================================================
        // RENDER JOB
        // =====================================================

        function renderJob(
            job
        ) {

            if (!job) {

                showError(
                    "Job information is unavailable."
                );

                return;

            }


            setText(
                "jobTitle",
                job.title
            );


            setText(
                "jobCategory",
                job.category?.name ||
                "Other"
            );


            setText(
                "jobSummaryCategory",
                job.category?.name ||
                "Other"
            );


            setText(
                "jobCreatedAt",
                formatDate(
                    job.created_at
                )
            );


            setText(
                "jobViews",
                job.views || 0
            );


            setText(
                "jobId",
                `#${job.id}`
            );


            setText(
                "jobSummaryPriority",
                job.priority || "Normal"
            );


            setText(
                "jobPriority",
                job.priority || "Normal"
            );


            setText(
                "jobStatus",
                job.status || "Open"
            );


            // -------------------------------------------------
            // CATEGORY ICON
            // -------------------------------------------------

            setText(
                "jobCategoryIcon",
                job.category?.icon || "✦"
            );


            // -------------------------------------------------
            // DESCRIPTION
            // -------------------------------------------------

            const description =
                document.getElementById(
                    "jobDescription"
                );


            if (description) {

                description.innerHTML =
                    escapeHtml(
                        job.description || ""
                    ).replace(
                        /\n/g,
                        "<br>"
                    );

            }


            // -------------------------------------------------
            // BUDGET
            // -------------------------------------------------

            renderBudget(
                job.budget
            );


            // -------------------------------------------------
            // LOCATION
            // -------------------------------------------------

            renderLocation(
                job
            );


            // -------------------------------------------------
            // IMAGES
            // -------------------------------------------------

            renderImages(
                job.images
            );


            // -------------------------------------------------
            // PRIORITY CLASS
            // -------------------------------------------------

            const priority =
                String(
                    job.priority ||
                    "normal"
                ).toLowerCase();


            const priorityElement =
                document.getElementById(
                    "jobPriority"
                );


            if (priorityElement) {

                priorityElement.className =
                    "job-priority";

                priorityElement.classList.add(
                    `priority-${priority}`
                );

            }


            // -------------------------------------------------
            // STATUS CLASS
            // -------------------------------------------------

            const statusElement =
                document.getElementById(
                    "jobStatus"
                );


            if (statusElement) {

                statusElement.className =
                    "job-status-badge";

                statusElement.classList.add(
                    `status-${String(
                        job.status ||
                        "open"
                    ).toLowerCase()}`
                );

            }

        }


        // =====================================================
        // LOAD JOB
        // =====================================================

        async function loadJob() {

            try {

                const response =
                    await fetch(
                        apiUrl,
                        {
                            method: "GET",

                            credentials:
                                "include",

                            headers: {
                                "Accept":
                                    "application/json"
                            },

                            cache:
                                "no-store"
                        }
                    );


                let data = null;


                try {

                    data =
                        await response.json();

                } catch {

                    data = null;

                }


                if (!response.ok) {

                    throw new Error(
                        data?.message ||
                        "Unable to load this job."
                    );

                }


                if (
                    data?.status !==
                    "success"
                ) {

                    throw new Error(
                        data?.message ||
                        "Invalid job response."
                    );

                }


                const job =
                    data.job;


                renderJob(
                    job
                );


                loading.hidden =
                    true;

                errorBox.hidden =
                    true;

                content.hidden =
                    false;


            } catch (error) {

                console.error(
                    "Job details error:",
                    error
                );


                showError(
                    error.message
                );

            }

        }


        // =====================================================
        // START
        // =====================================================

        if (!jobId || !apiUrl) {

            showError(
                "Invalid job URL."
            );

            return;

        }


        loadJob();

    }
);
