/**
 * auth.js
 * Client-side validation for the login and register forms. This mirrors
 * (but does not replace) the server-side checks in utils/validators.py —
 * the server always re-validates before touching the database.
 */

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const USERNAME_RE = /^[A-Za-z0-9_]{3,50}$/;

function setFieldError(form, field, message) {
    const input = form.querySelector(`#${field}`);
    const errorEl = form.querySelector(`[data-error-for="${field}"]`);
    if (message) {
        input.classList.add('is-invalid');
        if (errorEl) { errorEl.textContent = message; errorEl.hidden = false; }
    } else {
        input.classList.remove('is-invalid');
        if (errorEl) { errorEl.hidden = true; }
    }
    return !message;
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const email = loginForm.email.value.trim();
            const password = loginForm.password.value;

            let ok = true;
            ok = setFieldError(loginForm, 'email', EMAIL_RE.test(email) ? '' : 'Enter a valid email address.') && ok;
            ok = setFieldError(loginForm, 'password', password ? '' : 'Password is required.') && ok;

            if (!ok) e.preventDefault();
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const username = registerForm.username.value.trim();
            const email = registerForm.email.value.trim();
            const password = registerForm.password.value;
            const confirm = registerForm.confirm_password.value;

            let ok = true;
            ok = setFieldError(registerForm, 'username', USERNAME_RE.test(username)
                ? '' : '3-50 characters: letters, numbers, or underscore.') && ok;
            ok = setFieldError(registerForm, 'email', EMAIL_RE.test(email) ? '' : 'Enter a valid email address.') && ok;

            let passwordError = '';
            if (password.length < 8) passwordError = 'At least 8 characters.';
            else if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) passwordError = 'Include a letter and a number.';
            ok = setFieldError(registerForm, 'password', passwordError) && ok;

            ok = setFieldError(registerForm, 'confirm_password', password === confirm ? '' : 'Passwords do not match.') && ok;

            if (!ok) e.preventDefault();
        });
    }
});
