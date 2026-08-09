document.addEventListener(
    "DOMContentLoaded",
    loadAdminDashboard
);


async function loadAdminDashboard() {

    try {

        const response = await fetch(
            "/admin/dashboard"
        );


        if (!response.ok) {

            throw new Error(
                "Unable to load dashboard"
            );

        }


        const result =
            await response.json();


        if (
            result.status !== "success"
        ) {

            throw new Error(
                "Dashboard API error"
            );

        }


        const dashboard =
            result.dashboard;


        /* Users */

        setValue(
            "total-users",
            dashboard.users.total
        );

        setValue(
            "total-customers",
            dashboard.users.customers
        );

        setValue(
            "total-workers",
            dashboard.users.workers
        );

        setValue(
            "total-admins",
            dashboard.users.admins
        );


        /* Jobs */

        setValue(
            "total-jobs",
            dashboard.jobs.total
        );

        setValue(
            "open-jobs",
            dashboard.jobs.open
        );

        setValue(
            "assigned-jobs",
            dashboard.jobs.assigned
        );

        setValue(
            "completed-jobs",
            dashboard.jobs.completed
        );


        /* Applications */

        setValue(
            "total-applications",
            dashboard.applications.total
        );

        setValue(
            "pending-applications",
            dashboard.applications.pending
        );

        setValue(
            "accepted-applications",
            dashboard.applications.accepted
        );

        setValue(
            "rejected-applications",
            dashboard.applications.rejected
        );


        /* Workers */

        setValue(
            "verified-workers",
            dashboard.workers.verified
        );

        setValue(
            "pending-verification",
            dashboard.workers.pending_verification
        );


    } catch (error) {

        console.error(
            "Admin dashboard error:",
            error
        );

    }

}


function setValue(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.textContent =
        value ?? 0;
          }
