/**
 * utils.js
 * Small shared helpers used across pages: toast notifications,
 * clipboard copy, and a fetch wrapper that sends/reads JSON.
 */

function showToast(message) {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('is-visible'), 1800);
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    }
    // Fallback for non-secure contexts (older browsers / plain http on LAN)
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return Promise.resolve();
}

/**
 * Thin wrapper around fetch() for our JSON API endpoints.
 * Returns the parsed body and throws with `.errors` attached on failure.
 */
async function apiRequest(url, { method = 'GET', body } = {}) {
    const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
    });

    let data = {};
    try {
        data = await response.json();
    } catch (e) {
        // no JSON body
    }

    if (!response.ok) {
        const err = new Error('Request failed');
        err.errors = data.errors || ['Something went wrong. Please try again.'];
        throw err;
    }
    return data;
}
