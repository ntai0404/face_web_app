/**
 * LOGS.JS - Simple iframe refresh for Google Sheets
 */

const refreshSheetBtn = document.getElementById('refresh-sheet');
const sheetIframe = document.getElementById('sheet-iframe');

if (refreshSheetBtn && sheetIframe) {
    refreshSheetBtn.addEventListener('click', () => {
        // Reload iframe content
        sheetIframe.src = sheetIframe.src;

        // Visual feedback
        refreshSheetBtn.disabled = true;
        refreshSheetBtn.textContent = '⏳ Đang tải...';

        setTimeout(() => {
            refreshSheetBtn.disabled = false;
            refreshSheetBtn.textContent = '🔄 Tải lại Sheet';
        }, 1000);
    });
}
