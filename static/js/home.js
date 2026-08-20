/* =========================================================
   S. F WORKS
   PREMIUM HOME PAGE
   Horizontal Marketplace Scroller
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       HORIZONTAL SCROLL
    ====================================================== */

    const wrappers = document.querySelectorAll(
        ".horizontal-scroll-wrapper"
    );


    wrappers.forEach((wrapper) => {

        const scroller = wrapper.querySelector(
            "[data-scroll-container]"
        );

        if (!scroller) {
            return;
        }


        const prevButton = wrapper.querySelector(
            ".scroll-prev"
        );

        const nextButton = wrapper.querySelector(
            ".scroll-next"
        );


        /* =================================================
           ARROW NAVIGATION
        ================================================= */

        const getScrollAmount = () => {

            const firstCard =
                scroller.firstElementChild;

            if (!firstCard) {
                return 320;
            }

            const gap = parseFloat(
                getComputedStyle(scroller).columnGap
            ) || 18;

            return firstCard.offsetWidth + gap;
        };


        if (prevButton) {

            prevButton.addEventListener(
                "click",
                () => {

                    scroller.scrollBy({
                        left: -getScrollAmount(),
                        behavior: "smooth"
                    });

                }
            );

        }


        if (nextButton) {

            nextButton.addEventListener(
                "click",
                () => {

                    scroller.scrollBy({
                        left: getScrollAmount(),
                        behavior: "smooth"
                    });

                }
            );

        }


        /* =================================================
           MOUSE DRAG SCROLL
        ================================================= */

        let isDown = false;
        let startX = 0;
        let scrollStart = 0;


        scroller.addEventListener(
            "pointerdown",
            (event) => {

                if (event.pointerType === "touch") {
                    return;
                }

                isDown = true;

                startX = event.clientX;

                scrollStart =
                    scroller.scrollLeft;

                scroller.classList.add(
                    "is-dragging"
                );

                scroller.setPointerCapture(
                    event.pointerId
                );

            }
        );


        scroller.addEventListener(
            "pointermove",
            (event) => {

                if (!isDown) {
                    return;
                }

                const distance =
                    event.clientX - startX;

                scroller.scrollLeft =
                    scrollStart - distance;

            }
        );


        const stopDragging = (event) => {

            if (!isDown) {
                return;
            }

            isDown = false;

            scroller.classList.remove(
                "is-dragging"
            );

            try {
                scroller.releasePointerCapture(
                    event.pointerId
                );
            } catch (error) {
                /* pointer already released */
            }

        };


        scroller.addEventListener(
            "pointerup",
            stopDragging
        );

        scroller.addEventListener(
            "pointercancel",
            stopDragging
        );

        scroller.addEventListener(
            "pointerleave",
            stopDragging
        );


        /* =================================================
           PREVENT CLICK AFTER DRAG
        ================================================= */

        let moved = false;


        scroller.addEventListener(
            "pointerdown",
            () => {
                moved = false;
            }
        );


        scroller.addEventListener(
            "pointermove",
            (event) => {

                if (
                    Math.abs(
                        event.movementX
                    ) > 3
                ) {
                    moved = true;
                }

            }
        );


        scroller.addEventListener(
            "click",
            (event) => {

                if (moved) {

                    event.preventDefault();
                    event.stopPropagation();

                }

            },
            true
        );


        /* =================================================
           UPDATE ARROW STATE
        ================================================= */

        const updateButtons = () => {

            if (!prevButton && !nextButton) {
                return;
            }

            const maxScroll =
                scroller.scrollWidth -
                scroller.clientWidth;


            if (prevButton) {

                prevButton.disabled =
                    scroller.scrollLeft <= 5;

            }


            if (nextButton) {

                nextButton.disabled =
                    scroller.scrollLeft >=
                    maxScroll - 5;

            }

        };


        scroller.addEventListener(
            "scroll",
            updateButtons,
            {
                passive: true
            }
        );


        window.addEventListener(
            "resize",
            updateButtons
        );


        updateButtons();

    });


    /* =====================================================
       PREMIUM CARD TILT
    ====================================================== */

    const heroCard =
        document.querySelector(
            ".premium-job-card"
        );


    if (
        heroCard &&
        window.matchMedia(
            "(pointer: fine)"
        ).matches
    ) {

        heroCard.addEventListener(
            "mousemove",
            (event) => {

                const rect =
                    heroCard.getBoundingClientRect();

                const x =
                    event.clientX - rect.left;

                const y =
                    event.clientY - rect.top;

                const rotateY =
                    ((x / rect.width) - 0.5) * 5;

                const rotateX =
                    ((y / rect.height) - 0.5) * -5;


                heroCard.style.transform =
                    `perspective(900px)
                     rotateX(${rotateX}deg)
                     rotateY(${rotateY}deg)
                     translateY(-5px)`;

            }
        );


        heroCard.addEventListener(
            "mouseleave",
            () => {

                heroCard.style.transform =
                    "";

            }
        );

    }


    /* =====================================================
       HORIZONTAL SCROLL WITH MOUSE WHEEL
    ====================================================== */

    document
        .querySelectorAll(
            ".horizontal-scroll"
        )
        .forEach((scroller) => {

            scroller.addEventListener(
                "wheel",
                (event) => {

                    if (
                        Math.abs(
                            event.deltaY
                        ) <= Math.abs(
                            event.deltaX
                        )
                    ) {
                        return;
                    }


                    const canScroll =
                        scroller.scrollWidth >
                        scroller.clientWidth;


                    if (!canScroll) {
                        return;
                    }


                    event.preventDefault();


                    scroller.scrollLeft +=
                        event.deltaY;

                },
                {
                    passive: false
                }
            );

        });


});
