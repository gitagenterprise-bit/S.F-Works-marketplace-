function openModal(
    content
) {

    const overlay =
        document.getElementById(
            "modalOverlay"
        );

    const modalContent =
        document.getElementById(
            "modalContent"
        );

    if (!overlay || !modalContent) {
        return;
    }

    modalContent.innerHTML =
        content;

    overlay.classList.add(
        "active"
    );
}


function closeModal() {

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
}
