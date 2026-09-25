// ========================================
// CAMPUSINTEL MAIN JAVASCRIPT
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("CampusIntel JavaScript Loaded");


    // ========================================
    // PASSWORD SHOW / HIDE
    // ========================================

    const passwordInputs =
        document.querySelectorAll(
            'input[type="password"]'
        );

    passwordInputs.forEach(function (input) {

        const button =
            document.createElement("button");

        button.type = "button";

        button.innerText = "👁️";

        button.className =
            "password-toggle";

        input.parentNode.appendChild(button);


        button.addEventListener(
            "click",
            function () {

                if (
                    input.type === "password"
                ) {

                    input.type = "text";

                    button.innerText =
                        "🙈";

                } else {

                    input.type = "password";

                    button.innerText =
                        "👁️";
                }

            }
        );

    });


    // ========================================
    // REPORT FORM VALIDATION
    // ========================================

    const reportForm =
        document.querySelector(
            "#reportForm"
        );


    if (reportForm) {

        reportForm.addEventListener(
            "submit",
            function (event) {

                const description =
                    document.querySelector(
                        "#description"
                    );

                if (
                    description &&
                    description.value.trim()
                        .length < 10
                ) {

                    event.preventDefault();

                    alert(
                        "Please enter at least 10 characters."
                    );

                    description.focus();

                    return;
                }

            }
        );

    }


    // ========================================
    // DELETE CONFIRMATION
    // ========================================

    const deleteButtons =
        document.querySelectorAll(
            ".delete-button"
        );


    deleteButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const confirmed =
                    confirm(
                        "Are you sure you want to delete this item?"
                    );

                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    });


    // ========================================
    // AUTO HIDE FLASH MESSAGES
    // ========================================

    const flashMessages =
        document.querySelectorAll(
            ".flash-message"
        );


    flashMessages.forEach(function (message) {

        setTimeout(
            function () {

                message.style.opacity = "0";

                setTimeout(
                    function () {

                        message.remove();

                    },
                    500
                );

            },
            5000
        );

    });


    // ========================================
    // LOADING BUTTON
    // ========================================

    const forms =
        document.querySelectorAll(
            "form"
        );


    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const submitButton =
                    form.querySelector(
                        'button[type="submit"]'
                    );


                if (submitButton) {

                    submitButton.disabled =
                        true;

                    submitButton.innerText =
                        "Processing...";

                }

            }
        );

    });


    // ========================================
    // MOBILE MENU
    // ========================================

    const menuButton =
        document.querySelector(
            "#menuButton"
        );

    const sidebar =
        document.querySelector(
            "#sidebar"
        );


    if (
        menuButton &&
        sidebar
    ) {

        menuButton.addEventListener(
            "click",
            function () {

                sidebar.classList.toggle(
                    "active"
                );

            }
        );

    }


    // ========================================
    // CHARACTER COUNTER
    // ========================================

    const description =
        document.querySelector(
            "#description"
        );

    const counter =
        document.querySelector(
            "#characterCount"
        );


    if (
        description &&
        counter
    ) {

        description.addEventListener(
            "input",
            function () {

                counter.innerText =
                    description.value.length;

            }
        );

    }


    // ========================================
    // SEARCH FILTER
    // ========================================

    const searchInput =
        document.querySelector(
            "#searchInput"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const searchValue =
                    searchInput.value
                    .toLowerCase();


                const rows =
                    document.querySelectorAll(
                        ".searchable"
                    );


                rows.forEach(function (row) {

                    const text =
                        row.innerText
                        .toLowerCase();


                    if (
                        text.includes(
                            searchValue
                        )
                    ) {

                        row.style.display =
                            "";

                    } else {

                        row.style.display =
                            "none";

                    }

                });

            }
        );

    }

});