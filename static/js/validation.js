/**
 * ApexMed: Client-Side Input Validations & Interactive Handlers
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Password Visibility Toggle
    const togglePasswordBtn = document.getElementById("togglePasswordBtn");
    const passwordInput = document.getElementById("password");

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            const icon = togglePasswordBtn.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-eye");
                icon.classList.toggle("fa-eye-slash");
            }
        });
    }

    // 2. Real-time Email Format Validation
    const emailInput = document.getElementById("email");
    const emailFeedback = document.getElementById("emailFeedback");
    const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;

    if (emailInput && emailFeedback) {
        emailInput.addEventListener("input", function () {
            const val = emailInput.value.trim();
            if (val.length === 0) {
                emailInput.classList.remove("is-valid", "is-invalid");
                emailFeedback.textContent = "";
            } else if (!emailRegex.test(val)) {
                emailInput.classList.add("is-invalid");
                emailInput.classList.remove("is-valid");
                emailFeedback.textContent = "Please enter a valid email format (e.g., name@domain.com)";
            } else {
                emailInput.classList.remove("is-invalid");
                emailInput.classList.add("is-valid");
                emailFeedback.textContent = "";
            }
        });
    }

    // 3. Password Length & Match Validation (for Registration)
    const regPassword = document.getElementById("reg_password");
    const regConfirmPassword = document.getElementById("reg_confirm_password");
    const confirmFeedback = document.getElementById("confirmFeedback");

    if (regPassword && regConfirmPassword && confirmFeedback) {
        function validatePasswordMatch() {
            if (regConfirmPassword.value.length === 0) {
                regConfirmPassword.classList.remove("is-valid", "is-invalid");
                confirmFeedback.textContent = "";
            } else if (regPassword.value !== regConfirmPassword.value) {
                regConfirmPassword.classList.add("is-invalid");
                regConfirmPassword.classList.remove("is-valid");
                confirmFeedback.textContent = "Passwords do not match.";
            } else {
                regConfirmPassword.classList.remove("is-invalid");
                regConfirmPassword.classList.add("is-valid");
                confirmFeedback.textContent = "";
            }
        }
        regPassword.addEventListener("input", validatePasswordMatch);
        regConfirmPassword.addEventListener("input", validatePasswordMatch);
    }

    // 4. Client-side Form Submit Interception for Login Form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            let valid = true;
            const email = document.getElementById("email");
            const password = document.getElementById("password");

            // Email check
            if (!email.value.trim()) {
                email.classList.add("is-invalid");
                if (emailFeedback) emailFeedback.textContent = "Email address cannot be empty.";
                valid = false;
            } else if (!emailRegex.test(email.value.trim())) {
                email.classList.add("is-invalid");
                if (emailFeedback) emailFeedback.textContent = "Please enter a valid email format.";
                valid = false;
            }

            // Password check
            const passFeedback = document.getElementById("passwordFeedback");
            if (!password.value.trim()) {
                password.classList.add("is-invalid");
                if (passFeedback) passFeedback.textContent = "Password cannot be empty.";
                valid = false;
            } else if (password.value.length < 6) {
                password.classList.add("is-invalid");
                if (passFeedback) passFeedback.textContent = "Password must be at least 6 characters.";
                valid = false;
            }

            if (!valid) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    }

    // 5. Quick-Fill Demo Credentials Helper (For instant testing/evaluator convenience)
    window.quickFill = function (role) {
        const emailField = document.getElementById("email");
        const passField = document.getElementById("password");
        if (!emailField || !passField) return;

        if (role === "admin") {
            emailField.value = "admin@apexmed.com";
            passField.value = "Admin@123";
        } else if (role === "doctor") {
            emailField.value = "dr.vance@apexmed.com";
            passField.value = "Admin@123";
        } else if (role === "patient") {
            emailField.value = "patient.alice@gmail.com";
            passField.value = "Admin@123";
        }

        emailField.classList.remove("is-invalid");
        emailField.classList.add("is-valid");
        passField.classList.remove("is-invalid");
        passField.classList.add("is-valid");
        if (emailFeedback) emailFeedback.textContent = "";
    };
});
