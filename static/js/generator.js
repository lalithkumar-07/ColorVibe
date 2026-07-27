/**
 * generator.js
 * Drives the home page palette generator: shuffling (via the server-side
 * harmony API), locking individual swatches, copying hex values, and
 * saving the current palette.
 */

document.addEventListener('DOMContentLoaded', () => {
    const strip = document.getElementById('swatchStrip');
    if (!strip) return; // not on the generator page

    const swatches = Array.from(strip.querySelectorAll('.swatch'));
    const harmonyChips = document.querySelectorAll('.harmony-chip');
    const shuffleBtn = document.getElementById('shuffleBtn');
    const saveBtn = document.getElementById('saveBtn');
    const saveModal = document.getElementById('saveModal');
    const saveForm = document.getElementById('saveForm');
    const cancelSaveBtn = document.getElementById('cancelSaveBtn');
    const paletteNameInput = document.getElementById('paletteName');
    const paletteNameError = document.getElementById('paletteNameError');

    let currentHarmony = 'random';

    function getLockedMap() {
        const locked = {};
        swatches.forEach((swatch) => {
            const lockBtn = swatch.querySelector('.swatch-lock');
            if (lockBtn.getAttribute('aria-pressed') === 'true') {
                locked[swatch.dataset.index] = swatch.querySelector('.swatch-hex').dataset.hex;
            }
        });
        return locked;
    }

    function applyColors(colors) {
        colors.forEach((hex, i) => {
            const swatch = swatches[i];
            if (!swatch) return;
            swatch.style.backgroundColor = hex;
            const hexBtn = swatch.querySelector('.swatch-hex');
            hexBtn.dataset.hex = hex;
            hexBtn.querySelector('.hex-value').textContent = hex;
        });
    }

    async function shuffle() {
        shuffleBtn.disabled = true;
        try {
            const data = await apiRequest('/api/generate', {
                method: 'POST',
                body: {
                    count: swatches.length,
                    harmony: currentHarmony,
                    locked: getLockedMap(),
                },
            });
            applyColors(data.colors);
        } catch (err) {
            showToast('Could not generate a palette right now.');
        } finally {
            shuffleBtn.disabled = false;
        }
    }

    // ---- Harmony selection ------------------------------------------------
    harmonyChips.forEach((chip) => {
        chip.addEventListener('click', () => {
            harmonyChips.forEach((c) => c.classList.remove('is-active'));
            chip.classList.add('is-active');
            currentHarmony = chip.dataset.harmony;
            shuffle();
        });
    });

    // ---- Lock toggles ------------------------------------------------
    swatches.forEach((swatch) => {
        const lockBtn = swatch.querySelector('.swatch-lock');
        lockBtn.addEventListener('click', () => {
            const isLocked = lockBtn.getAttribute('aria-pressed') === 'true';
            lockBtn.setAttribute('aria-pressed', String(!isLocked));
            lockBtn.setAttribute('aria-label', isLocked ? 'Lock this color' : 'Unlock this color');
        });
    });

    // ---- Copy hex on click ------------------------------------------------
    strip.addEventListener('click', (e) => {
        const hexBtn = e.target.closest('.swatch-hex');
        if (!hexBtn) return;
        copyToClipboard(hexBtn.dataset.hex).then(() => showToast(`${hexBtn.dataset.hex} copied`));
    });

    // ---- Shuffle button + spacebar ------------------------------------------------
    shuffleBtn.addEventListener('click', shuffle);

    document.addEventListener('keydown', (e) => {
        const target = e.target;
        const typing = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';
        const modalOpen = !saveModal.hidden;
        if (e.code === 'Space' && !typing && !modalOpen) {
            e.preventDefault();
            shuffle();
        }
    });

    // ---- Save palette ------------------------------------------------
    function openSaveModal() {
        if (!window.COLORVIBE.isLoggedIn) {
            window.location.href = window.COLORVIBE.loginUrl;
            return;
        }
        paletteNameError.hidden = true;
        paletteNameInput.value = '';
        saveModal.hidden = false;
        paletteNameInput.focus();
    }

    function closeSaveModal() {
        saveModal.hidden = true;
    }

    saveBtn.addEventListener('click', openSaveModal);
    cancelSaveBtn.addEventListener('click', closeSaveModal);
    saveModal.addEventListener('click', (e) => {
        if (e.target === saveModal) closeSaveModal();
    });

    saveForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = paletteNameInput.value.trim();

        if (!name) {
            paletteNameError.textContent = 'Palette name is required.';
            paletteNameError.hidden = false;
            return;
        }

        const colors = swatches.map((s) => s.querySelector('.swatch-hex').dataset.hex);

        try {
            await apiRequest(window.COLORVIBE.saveUrl, {
                method: 'POST',
                body: { name, colors, harmony: currentHarmony },
            });
            closeSaveModal();
            showToast('Palette saved');
        } catch (err) {
            paletteNameError.textContent = (err.errors && err.errors[0]) || 'Could not save palette.';
            paletteNameError.hidden = false;
        }
    });
});
