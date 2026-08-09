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
