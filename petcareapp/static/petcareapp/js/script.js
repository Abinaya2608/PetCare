/* ==============================
   PETCARE - JAVASCRIPT
   ============================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ---------- Mobile Navbar ---------- */

    const navbar = document.querySelector(".navbar");
    const navLinks = document.querySelector(".nav-links");

    if (navbar && navLinks) {

        const toggleButton = document.createElement("button");

        toggleButton.className = "nav-toggle";
        toggleButton.type = "button";
        toggleButton.setAttribute(
            "aria-label",
            "Toggle navigation"
        );

        toggleButton.innerHTML = "☰";

        navbar.insertBefore(toggleButton, navLinks);

        toggleButton.addEventListener("click", function () {

            navLinks.classList.toggle("open");

            if (navLinks.classList.contains("open")) {
                toggleButton.innerHTML = "✕";
            } else {
                toggleButton.innerHTML = "☰";
            }

        });
    }


    /* ---------- Django Messages ---------- */

    const messages = document.querySelectorAll(".message");

    messages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transition =
                "opacity 0.4s ease";

            setTimeout(function () {
                message.remove();
            }, 400);

        }, 3500);

    });


    /* ---------- Confirm Actions ---------- */

    const confirmElements =
        document.querySelectorAll("[data-confirm]");

    confirmElements.forEach(function (element) {

        element.addEventListener("click", function (event) {

            const message =
                element.getAttribute("data-confirm") ||
                "Are you sure?";

            if (!confirm(message)) {
                event.preventDefault();
            }

        });

    });


    /* ---------- Quantity Validation ---------- */

    const quantityInputs =
        document.querySelectorAll(".quantity-input");

    quantityInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            let value = parseInt(input.value);

            const min =
                parseInt(input.min || "1");

            const max =
                parseInt(input.max || "999");

            if (isNaN(value)) {
                value = min;
            }

            if (value < min) {
                value = min;
            }

            if (value > max) {
                value = max;
            }

            input.value = value;

        });

    });


    /* ---------- Auto Calculate Quantity ---------- */

    const quantityButtons =
        document.querySelectorAll("[data-quantity]");

    quantityButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const action =
                button.getAttribute("data-quantity");

            const target =
                button.parentElement.querySelector(
                    ".quantity-input"
                );

            if (!target) {
                return;
            }

            let value =
                parseInt(target.value || "1");

            if (action === "increase") {
                value++;
            }

            if (action === "decrease" && value > 1) {
                value--;
            }

            const max =
                parseInt(target.max || "999");

            if (value > max) {
                value = max;
            }

            target.value = value;

        });

    });


    /* ---------- Search Form ---------- */

    const searchInput =
        document.querySelector(
            ".search-form input"
        );

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {
                    return;
                }

            }
        );

    }


    /* ---------- Prevent Double Submit ---------- */

    const forms =
        document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector(
                    'button[type="submit"]'
                );

            if (submitButton) {

                submitButton.disabled = true;

                setTimeout(function () {
                    submitButton.disabled = false;
                }, 3000);
            }

        });

    });

});