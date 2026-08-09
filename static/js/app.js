document.addEventListener(
    "DOMContentLoaded",
    () => {

        const button =
            document.getElementById(
                "mobileMenuBtn"
            );

        const nav =
            document.querySelector(
                ".desktop-nav"
            );

        if (!button || !nav) {
            return;
        }

        button.addEventListener(
            "click",
            () => {

                nav.classList.toggle(
                    "mobile-open"
                );

            }
        );

    }
);
function showLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.classList.add(
            "active"
        );

    }
}


function hideLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.classList.remove(
            "active"
        );

    }
}

