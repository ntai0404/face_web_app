/**
 * LOGS.JS - Professional Attendance Dashboard & Real-time Table
 */

const logsTbody = document.getElementById('logs-tbody');
const refreshLogsBtn = document.getElementById('refresh-logs');
const logSearchInput = document.getElementById('log-search');
const exportExcelBtn = document.getElementById('export-excel');

// Stat elements (Cards)
const statTotal = document.getElementById('stat-total');
const statCheckin = document.getElementById('stat-checkin');
const statCheckout = document.getElementById('stat-checkout');
const statWorking = document.getElementById('stat-working');

// Stat elements (Text spans)
const totalLogsSpan = document.getElementById('total-logs');
const todayLogsSpan = document.getElementById('today-logs');

let allAttendanceRecords = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();

    // Auto refresh every 2 seconds for near real-time updates
    setInterval(fetchDashboardData, 2000);
});

// Refresh button listener
if (refreshLogsBtn) {
    refreshLogsBtn.addEventListener('click', () => {
        refreshLogsBtn.disabled = true;
        refreshLogsBtn.innerHTML = '⏳ Đang tải...';
        fetchDashboardData();

        setTimeout(() => {
            refreshLogsBtn.disabled = false;
            refreshLogsBtn.innerHTML = '🔄 Tải lại dữ liệu';
        }, 2000);
    });
}

// Export Excel (CSV) logic
if (exportExcelBtn) {
    exportExcelBtn.addEventListener('click', () => {
        if (allAttendanceRecords.length === 0) {
            alert('Không có dữ liệu để xuất!');
            return;
        }

        const headers = ["STT", "Mã NV", "Họ Tên", "Ngày", "Vào", "Ra", "Tổng (h)", "Trạng thái"];
        const rows = allAttendanceRecords.map((r, index) => [
            index + 1,
            r.employee_code,
            r.full_name,
            new Date().toLocaleDateString(),
            r.check_in_time || '',
            r.check_out_time || '',
            r.duration || '0',
            r.status === 'working' ? 'Đang làm việc' : 'Đã về'
        ]);

        let csvContent = "\uFEFF"; // UTF-8 BOM for Excel
        csvContent += headers.join(",") + "\n";
        rows.forEach(row => {
            csvContent += row.map(field => `"${field}"`).join(",") + "\n";
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `diem_danh_${new Date().toLocaleDateString().replace(/\//g, '-')}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

// Search functionality
if (logSearchInput) {
    logSearchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = allAttendanceRecords.filter(record =>
            record.full_name.toLowerCase().includes(searchTerm) ||
            record.employee_code.toLowerCase().includes(searchTerm)
        );
        renderTable(filtered);
    });
}

async function fetchDashboardData() {
    try {
        // Fetch Stats
        const statsResp = await fetch('/api/attendance/stats');
        const stats = await statsResp.json();
        updateStatsCards(stats);

        // Fetch Records
        const recordsResp = await fetch('/api/attendance/today');
        const data = await recordsResp.json();
        allAttendanceRecords = data.records || [];
        renderTable(allAttendanceRecords);

    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

function updateStatsCards(stats) {
    if (!stats) return;
    statTotal.textContent = stats.total_employees || 0;
    statCheckin.textContent = stats.checked_in || 0;
    statCheckout.textContent = stats.checked_out || 0;
    statWorking.textContent = stats.currently_working || 0;

    // Update text spans too
    if (totalLogsSpan) totalLogsSpan.textContent = stats.checked_in || 0;
    if (todayLogsSpan) todayLogsSpan.textContent = stats.checked_in || 0;
}

function renderTable(records) {
    if (!logsTbody) return;

    if (records.length === 0) {
        logsTbody.innerHTML = `
            <tr>
                <td colspan="7" class="no-data" style="text-align:center; padding:30px; color:#666;">
                    <p style="font-size:1.2em; margin:0;">📭 Chưa có dữ liệu điểm danh hôm nay</p>
                </td>
            </tr>
        `;
        return;
    }

    logsTbody.innerHTML = records.map((record, index) => `
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding:12px; text-align:center;">${index + 1}</td>
            <td style="padding:12px;">${record.check_in_time || '--:--:--'}</td>
            <td style="padding:12px; font-weight:bold;">${record.employee_code}</td>
            <td style="padding:12px;">${record.full_name}</td>
            <td style="padding:12px; text-align:center;">${record.confidence ? (record.confidence * 100).toFixed(1) + '%' : '--'}</td>
            <td style="padding:12px; text-align:center;">${record.liveness_score ? record.liveness_score.toFixed(2) : '--'}</td>
            <td style="padding:12px; text-align:center;">
                <span style="padding:5px 10px; border-radius:20px; font-size:0.85em; font-weight:bold; background:${getStatusBg(record.status)}; color:${getStatusColor(record.status)};">
                    ${record.status_icon} ${getStatusText(record.status)}
                </span>
            </td>
        </tr>
    `).join('');
}

function getStatusText(status) {
    switch (status) {
        case 'working': return 'Đang làm việc';
        case 'left': return 'Đã về';
        default: return 'Chưa đến';
    }
}

function getStatusBg(status) {
    switch (status) {
        case 'working': return 'rgba(76,175,80,0.1)';
        case 'left': return 'rgba(244,67,54,0.1)';
        default: return 'rgba(158,158,158,0.1)';
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'working': return '#2e7d32';
        case 'left': return '#c62828';
        default: return '#616161';
    }
}
