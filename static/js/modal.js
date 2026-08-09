/* =========================================================
   S. F WORKS — PREMIUM MODAL SYSTEM
========================================================= */

(function () {

    "use strict";


    /* =====================================================
       GET ELEMENTS
    ====================================================== */

    function getModalElements() {

        return {

            overlay:
                document.getElementById(
                    "modalOverlay"
                ),

            modal:
                document.getElementById(
                    "modalBox"
                ),

            content:
                document.getElementById(
                    "modalContent"
                )

        };

    }


    /* =====================================================
       OPEN MODAL
    ====================================================== */

    window.openModal = function (content) {

        const {
            overlay,
            modal,
            modalContent
        } = {

            overlay:
                document.getElementById(
                    "modalOverlay"
                ),

            modal:
                document.getElementById(
                    "modalBox"
                ),

            modalContent:
                document.getElementById(
                    "modalContent"
                )

        };


        /* ---------------------------------------------
           Safety check
        ---------------------------------------------- */

        if (
            !overlay ||
            !modalContent
        ) {

            return;

        }


        /* ---------------------------------------------
           Insert dynamic content
        ---------------------------------------------- */

        modalContent.innerHTML =
            content;


        /* ---------------------------------------------
           Save current scroll position
        ---------------------------------------------- */

        document.body.dataset.modalScrollY =
            String(
                window.scrollY
            );


        /* ---------------------------------------------
           Lock page scroll
        ---------------------------------------------- */

        document.body.style.overflow =
            "hidden";


        /* ---------------------------------------------
           Show modal
        ---------------------------------------------- */

        overlay.classList.add(
            "active"
        );


        overlay.setAttribute(
            "aria-hidden",
            "false"
        );


        /* ---------------------------------------------
           Focus modal
        ---------------------------------------------- */

        requestAnimationFrame(
            function () {

                if (modal) {

                    modal.focus();

                }

            }
        );

    };


    /* =====================================================
       CLOSE MODAL
    ====================================================== */

    window.closeModal = function () {

        const overlay =
            document.getElementById(
                "modalOverlay"
            );


        if (!overlay) {

            return;

        }


        /* ---------------------------------------------
           Hide modal
        ---------------------------------------------- */

        overlay.classList.remove(
            "active"
        );


        overlay.setAttribute(
            "aria-hidden",
            "true"
        );


        /* ---------------------------------------------
           Restore page scroll
        ---------------------------------------------- */

        const savedScrollY =
            parseInt(
                document.body.dataset.modalScrollY ||
                "0",
                10
            );


        document.body.style.overflow =
            "";


        /* ---------------------------------------------
           Restore scroll position
        ---------------------------------------------- */

        window.scrollTo(
            0,
            savedScrollY
        );


        /* ---------------------------------------------
           Remove content after animation
        ---------------------------------------------- */

        const modalContent =
            document.getElementById(
                "modalContent"
            );


        if (modalContent) {

            setTimeout(
                function () {

                    /*
                     * Only clear content if
                     * modal is still closed.
                     */

                    if (
                        !overlay.classList.contains(
                            "active"
                        )
                    ) {

                        modalContent.innerHTML =
                            "";

                    }

                },
                300
            );

        }

    };


    /* =====================================================
       ESCAPE KEY
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !== "Escape"
            ) {

                return;

            }


            const overlay =
                document.getElementById(
                    "modalOverlay"
                );


            if (
                overlay &&
                overlay.classList.contains(
                    "active"
                )
            ) {

                closeModal();

            }

        }
    );


    /* =====================================================
       BACKDROP CLICK
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const overlay =
                document.getElementById(
                    "modalOverlay"
                );


            if (
                !overlay ||
                !overlay.classList.contains(
                    "active"
                )
            ) {

                return;

            }


            /*
             * Close only when clicking
             * directly on the backdrop.
             */

            if (
                event.target === overlay ||
                event.target.classList.contains(
                    "modal-backdrop"
                )
            ) {

                closeModal();

            }

        }
    );


    /* =====================================================
       PREVENT MODAL CONTENT CLICK FROM CLOSING
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            const modal =
                document.getElementById(
                    "modalBox"
                );


            if (
                !modal
            ) {

                return;

            }


            /*
             * Stop clicks inside modal from
             * bubbling to overlay handlers.
             */

            if (
                modal.contains(
                    event.target
                )
            ) {

                event.stopPropagation();

            }

        },
        true
    );


    /* =====================================================
       INITIAL STATE
    ====================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            const overlay =
                document.getElementById(
                    "modalOverlay"
                );


            if (!overlay) {

                return;

            }


            overlay.classList.remove(
                "active"
            );


            overlay.setAttribute(
                "aria-hidden",
                "true"
            );

        }
    );


    /* =====================================================
       CLEANUP ON PAGE EXIT
    ====================================================== */

    window.addEventListener(
        "pagehide",
        function () {

            document.body.style.overflow =
                "";

        }
    );


})();
