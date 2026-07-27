/**
 * dashboard.js
 * Handles rename/delete for saved palettes on the dashboard grid, and the
 * CSS/JSON export tabs on the palette detail page.
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboardGrid();
    initExportPanel();
});

function initDashboardGrid() {
    const grid = document.getElementById('paletteGrid');
    if (!grid) return;

    grid.addEventListener('click', async (e) => {
        const card = e.target.closest('.palette-card');
        if (!card) return;
        const paletteId = card.dataset.id;

        if (e.target.closest('.palette-delete-btn')) {
            if (!confirm('Delete this palette? This cannot be undone.')) return;
            try {
                await apiRequest(`/palettes/${paletteId}`, { method: 'DELETE' });
                card.remove();
                showToast('Palette deleted');
            } catch (err) {
                showToast('Could not delete palette.');
            }
            return;
        }

        if (e.target.closest('.palette-rename-btn')) {
            const nameEl = card.querySelector('.palette-card-name');
            const newName = prompt('Rename palette', nameEl.textContent.trim());
            if (!newName || !newName.trim()) return;
            try {
                await apiRequest(`/palettes/${paletteId}`, { method: 'PUT', body: { name: newName.trim() } });
                nameEl.textContent = newName.trim();
                showToast('Palette renamed');
            } catch (err) {
                showToast((err.errors && err.errors[0]) || 'Could not rename palette.');
            }
        }
    });
}

function initExportPanel() {
    const exportCode = document.getElementById('exportCode');
    if (!exportCode || !window.PALETTE_COLORS) return;

    const tabs = document.querySelectorAll('.export-tab');
    const copyBtn = document.getElementById('copyExportBtn');
    const colors = window.PALETTE_COLORS;

    function buildCss() {
        const lines = colors.map((hex, i) => `  --color-${i + 1}: ${hex};`);
        return `:root {\n${lines.join('\n')}\n}`;
    }

    function buildJson() {
        return JSON.stringify(colors, null, 2);
    }

    function render(format) {
        exportCode.textContent = format === 'json' ? buildJson() : buildCss();
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            tabs.forEach((t) => t.classList.remove('is-active'));
            tab.classList.add('is-active');
            render(tab.dataset.format);
        });
    });

    copyBtn.addEventListener('click', () => {
        copyToClipboard(exportCode.textContent).then(() => showToast('Copied to clipboard'));
    });

    // Also allow clicking a static swatch hex to copy it directly.
    document.addEventListener('click', (e) => {
        const hexBtn = e.target.closest('.swatch-hex--static');
        if (!hexBtn) return;
        copyToClipboard(hexBtn.dataset.hex).then(() => showToast(`${hexBtn.dataset.hex} copied`));
    });

    render('css');
}
