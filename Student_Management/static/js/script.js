/**
 * Student Management System - Client-side Logic
 * Vanilla JavaScript: Search & Filter, Modals, Dynamic Grade Calculators, Chart.js Visualizations
 */

document.addEventListener("DOMContentLoaded", () => {
    initSidebarToggle();
    initFlashMessages();
    initLiveSearchAndFilter();
    initMarkCalculators();
});

/* ==========================================================================
   Sidebar & Navigation
   ========================================================================== */
function initSidebarToggle() {
    const toggleBtn = document.getElementById("menuToggleBtn");
    const sidebar = document.getElementById("appSidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("mobile-open");
        });

        // Close when clicking outside on mobile
        document.addEventListener("click", (e) => {
            if (window.innerWidth <= 860 && 
                sidebar.classList.contains("mobile-open") && 
                !sidebar.contains(e.target) && 
                !toggleBtn.contains(e.target)) {
                sidebar.classList.remove("mobile-open");
            }
        });
    }
}

/* ==========================================================================
   Flash Notification Dismissal
   ========================================================================== */
function initFlashMessages() {
    document.querySelectorAll(".alert-close").forEach(btn => {
        btn.addEventListener("click", function () {
            const alertBox = this.closest(".alert-message");
            if (alertBox) {
                alertBox.style.opacity = "0";
                setTimeout(() => alertBox.remove(), 250);
            }
        });
    });
}

/* ==========================================================================
   Modals Control
   ========================================================================== */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
    }
}

// Close modal on background click
window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
        e.target.classList.remove("active");
    }
});

/* ==========================================================================
   Delete Confirmation Helper
   ========================================================================== */
function confirmDelete(studentName, deleteUrl) {
    if (confirm(`Are you sure you want to delete student: "${studentName}"?\nThis action cannot be undone.`)) {
        window.location.href = deleteUrl;
    }
}

function confirmAction(message, actionUrl) {
    if (confirm(message)) {
        window.location.href = actionUrl;
    }
}

/* ==========================================================================
   Attendance Modal Handler
   ========================================================================== */
function openAttendanceModal(studentId, studentName, totalClasses, presentClasses) {
    const form = document.getElementById("attendanceForm");
    if (!form) return;
    
    form.action = `/attendance/update/${studentId}`;
    document.getElementById("attStudentName").innerText = studentName;
    document.getElementById("attTotalClasses").value = totalClasses;
    document.getElementById("attPresentClasses").value = presentClasses;

    calcAttendancePreview();
    openModal("attendanceModal");
}

function calcAttendancePreview() {
    const totalInput = document.getElementById("attTotalClasses");
    const presentInput = document.getElementById("attPresentClasses");
    const preview = document.getElementById("attPercentagePreview");
    
    if (totalInput && presentInput && preview) {
        const tot = parseInt(totalInput.value) || 0;
        const pres = parseInt(presentInput.value) || 0;
        if (tot > 0) {
            const pct = Math.min(100, Math.round((pres / tot) * 100));
            preview.innerText = `${pct}% (${tot - pres} absent)`;
            preview.className = pct >= 75 ? "badge badge-success" : (pct >= 60 ? "badge badge-warning" : "badge badge-danger");
        } else {
            preview.innerText = "0%";
            preview.className = "badge badge-secondary";
        }
    }
}

/* ==========================================================================
   Marks Modal Handler & Dynamic Grade Calculation
   ========================================================================== */
function openMarksModal(studentId = null, studentName = "", subject = "", internal = 0, external = 0) {
    const select = document.getElementById("markStudentSelect");
    const nameDisplay = document.getElementById("markStudentNameDisplay");
    
    if (select && studentId) {
        select.value = studentId;
    }
    if (nameDisplay && studentName) {
        nameDisplay.innerText = studentName;
    }

    const subInput = document.getElementById("markSubject");
    if (subInput && subject) {
        subInput.value = subject;
    }

    const intInput = document.getElementById("markInternal");
    const extInput = document.getElementById("markExternal");
    if (intInput) intInput.value = internal;
    if (extInput) extInput.value = external;

    calculateMarkPreview();
    openModal("marksModal");
}

function calculateMarkPreview() {
    const intInput = document.getElementById("markInternal");
    const extInput = document.getElementById("markExternal");
    const totDisplay = document.getElementById("markTotalDisplay");
    const gradeDisplay = document.getElementById("markGradeDisplay");

    if (!intInput || !extInput || !totDisplay || !gradeDisplay) return;

    const internal = parseFloat(intInput.value) || 0;
    const external = parseFloat(extInput.value) || 0;
    const total = internal + external;

    totDisplay.innerText = total.toFixed(1);

    let grade = "F";
    let badgeClass = "badge-danger";

    if (total >= 90) {
        grade = "A+";
        badgeClass = "badge-success";
    } else if (total >= 80) {
        grade = "A";
        badgeClass = "badge-success";
    } else if (total >= 70) {
        grade = "B+";
        badgeClass = "badge-info";
    } else if (total >= 60) {
        grade = "B";
        badgeClass = "badge-info";
    } else if (total >= 50) {
        grade = "C";
        badgeClass = "badge-warning";
    } else {
        grade = "F";
        badgeClass = "badge-danger";
    }

    gradeDisplay.innerText = grade;
    gradeDisplay.className = `badge ${badgeClass}`;
}

function initMarkCalculators() {
    const intInput = document.getElementById("markInternal");
    const extInput = document.getElementById("markExternal");
    if (intInput && extInput) {
        intInput.addEventListener("input", calculateMarkPreview);
        extInput.addEventListener("input", calculateMarkPreview);
    }
}

/* ==========================================================================
   Live Filter & Search in Table
   ========================================================================== */
function initLiveSearchAndFilter() {
    const searchInput = document.getElementById("studentTableSearch");
    const deptFilter = document.getElementById("filterDept");
    const yearFilter = document.getElementById("filterYear");
    const statusFilter = document.getElementById("filterStatus");
    const tableBody = document.getElementById("studentsTableBody");

    if (!tableBody) return;

    const rows = tableBody.querySelectorAll("tr.student-row");

    function applyFilter() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
        const selDept = deptFilter ? deptFilter.value : "all";
        const selYear = yearFilter ? yearFilter.value : "all";
        const selStatus = statusFilter ? statusFilter.value : "all";

        let visibleCount = 0;

        rows.forEach(row => {
            const name = (row.dataset.name || "").toLowerCase();
            const reg = (row.dataset.reg || "").toLowerCase();
            const dept = row.dataset.dept || "";
            const year = row.dataset.year || "";
            const status = row.dataset.status || "";

            const matchesQuery = !query || name.includes(query) || reg.includes(query) || dept.toLowerCase().includes(query);
            const matchesDept = (selDept === "all" || dept === selDept);
            const matchesYear = (selYear === "all" || year === selYear);
            const matchesStatus = (selStatus === "all" || status === selStatus);

            if (matchesQuery && matchesDept && matchesYear && matchesStatus) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        const noMatchRow = document.getElementById("noRecordsRow");
        if (noMatchRow) {
            noMatchRow.style.display = (visibleCount === 0) ? "" : "none";
        }
    }

    if (searchInput) searchInput.addEventListener("input", applyFilter);
    if (deptFilter) deptFilter.addEventListener("change", applyFilter);
    if (yearFilter) yearFilter.addEventListener("change", applyFilter);
    if (statusFilter) statusFilter.addEventListener("change", applyFilter);
}

/* ==========================================================================
   Chart.js Renderers
   ========================================================================== */

/**
 * Render Dashboard charts: Department Distribution & Attendance Status
 */
function renderDashboardCharts(deptData, attendanceData) {
    // 1. Department Distribution Chart (Doughnut)
    const deptCanvas = document.getElementById("deptChart");
    if (deptCanvas && deptData) {
        const labels = deptData.map(d => d.label);
        const counts = deptData.map(d => d.count);
        
        new Chart(deptCanvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        "#2563eb", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#64748b"
                    ],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dept = deptData[context.dataIndex];
                                return ` ${dept.name}: ${context.raw} students`;
                            }
                        }
                    }
                },
                cutout: "68%"
            }
        });
    }

    // 2. Attendance Breakdown Chart (Pie)
    const attCanvas = document.getElementById("attSummaryChart");
    if (attCanvas && attendanceData) {
        new Chart(attCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Good (≥75%)", "Warning (60–74%)", "Low (<60%)"],
                datasets: [{
                    data: [attendanceData.good, attendanceData.warning, attendanceData.low],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } }
                }
            }
        });
    }
}

/**
 * Render Academic Performance charts:
 * 1. Subject-wise Average Marks (Bar)
 * 2. Department-wise Student Count (Doughnut)
 * 3. Attendance Distribution (Pie)
 * 4. Grade Distribution (Bar)
 */
function renderPerformanceCharts(data) {
    // 1. Subject-wise Marks Bar Chart
    const subCanvas = document.getElementById("subjectMarksChart");
    if (subCanvas && data.subject_analysis) {
        new Chart(subCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: data.subject_analysis.map(s => s.subject),
                datasets: [
                    {
                        label: "Average Score",
                        data: data.subject_analysis.map(s => s.avg_score),
                        backgroundColor: "#2563eb",
                        borderRadius: 6
                    },
                    {
                        label: "Highest Score",
                        data: data.subject_analysis.map(s => s.max_score),
                        backgroundColor: "#10b981",
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: "#f1f5f9" }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { position: "top", labels: { boxWidth: 12, font: { family: "Inter" } } }
                }
            }
        });
    }

    // 2. Department-wise Count
    const deptCanvas = document.getElementById("deptPerfChart");
    if (deptCanvas && data.department_distribution) {
        new Chart(deptCanvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: data.department_distribution.map(d => d.label),
                datasets: [{
                    data: data.department_distribution.map(d => d.count),
                    backgroundColor: ["#2563eb", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#64748b"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } }
                }
            }
        });
    }

    // 3. Attendance Distribution
    const attCanvas = document.getElementById("attPerfChart");
    if (attCanvas && data.attendance_distribution) {
        new Chart(attCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Good (≥75%)", "Warning (60–74%)", "Low (<60%)"],
                datasets: [{
                    data: [
                        data.attendance_distribution.good,
                        data.attendance_distribution.warning,
                        data.attendance_distribution.low
                    ],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } }
                }
            }
        });
    }

    // 4. Grade Distribution Bar Chart
    const gradeCanvas = document.getElementById("gradeDistributionChart");
    if (gradeCanvas && data.grade_distribution) {
        const grades = ["A+", "A", "B+", "B", "C", "F"];
        const counts = grades.map(g => data.grade_distribution[g] || 0);
        const colors = ["#10b981", "#06b6d4", "#2563eb", "#3b82f6", "#f59e0b", "#ef4444"];

        new Chart(gradeCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: grades,
                datasets: [{
                    label: "Student Count",
                    data: counts,
                    backgroundColor: colors,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: "#f1f5f9" }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
