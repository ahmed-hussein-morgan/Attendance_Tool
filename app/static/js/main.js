document.addEventListener('DOMContentLoaded', function () {
    // Set active nav link based on current path
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Add current year to footer
    document.querySelector('.footer .text-muted').innerHTML =
        document.querySelector('.footer .text-muted').innerHTML.replace(
            '{{ now.year }}',
            new Date().getFullYear()
        );

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle Test Connection Button
    $(document).on('click', '.test-connection', function () {
        const machineId = $(this).data('id');
        $.ajax({
            url: `/machines/test/${machineId}`,
            method: 'POST',
            success: function (response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                } else {
                    showNotification(response.message, 'error');
                }
            },
            error: function (xhr, status, error) {
                showNotification('Failed to test machine connection: ' + error, 'error');
            }
        });
    });

    // Handle Toggle Status Button
    $(document).on('click', '.toggle-status', function () {
        const machineId = $(this).data('id');
        $.ajax({
            url: `/machines/toggle_status/${machineId}`,
            method: 'POST',
            success: function (response) {
                if (response.status === 'success') {
                    showNotification(response.message, 'success');
                    location.reload();
                } else {
                    showNotification(response.message, 'error');
                }
            },
            error: function (xhr, status, error) {
                showNotification('Failed to toggle machine status: ' + error, 'error');
            }
        });
    });

    // Handle Edit Employee Button
    $(document).on('click', '.edit-btn', function () {
        const employeeId = $(this).data('id');
        window.location.href = `/employees/edit/${employeeId}`;
    });

    // Handle Delete Employee Button
    $(document).on('click', '.delete-btn', function () {
        const employeeId = $(this).data('id');
        if (confirm('Are you sure you want to delete this employee?')) {
            $.ajax({
                url: `/employees/delete/${employeeId}`,
                method: 'POST',
                success: function (response) {
                    if (response.status === 'success') {
                        showNotification(response.message, 'success');
                        location.reload();
                    } else {
                        showNotification(response.message, 'error');
                    }
                },
                error: function (xhr, status, error) {
                    showNotification('Failed to delete employee: ' + error, 'error');
                }
            });
        }
    });

    // Handle Import Employees Button
    $(document).ready(function() {
        // Handle Import Employees Button
        $('#importBtn').on('click', function() {
            const fileInput = $('#importFile')[0];
            if (!fileInput.files.length) {
                showNotification('Please select a file to import.', 'error');
                return;
            }
    
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
    
            $.ajax({
                url: '/api/import_employees',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.status === 'success') {
                        showNotification(response.message, 'success');
                        // Reload the page to reflect the updated employee list
                        location.reload();
                    } else {
                        showNotification(response.message, 'error');
                    }
                },
                error: function(xhr, status, error) {
                    showNotification('Failed to import employees: ' + error, 'error');
                }
            });
        });
    });
    // Handle Export Attendance Button
    $('#exportAttendanceBtn').on('click', function () {
        window.location.href = '/api/export_attendance';
    });

    // Handle Export Employees Button
    $('#exportEmployeesBtn').on('click', function () {
        window.location.href = '/api/export_employees';
    });

    // Handle Export Calculated Attendance Button
    $('#exportCalculatedBtn').on('click', function () {
        window.location.href = '/api/export_calculated_attendance';
    });

    // Handle Calculate Attendance Button
    $('#calculateForm').on('submit', function (e) {
        e.preventDefault();
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();
        const employeeId = $('#employeeId').val();

        if (!startDate || !endDate) {
            showNotification('Both start and end dates are required.', 'error');
            return;
        }

        $.ajax({
            url: '/api/calculate_attendance',
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
                employee_id: employeeId
            }),
            success: function (response) {
                if (response.status === 'success') {
                    const table = $('#calculatedTable').DataTable();
                    table.clear().rows.add(response.data).draw();
                } else {
                    showNotification(response.message, 'error');
                }
            },
            error: function (xhr, status, error) {
                showNotification('Failed to calculate attendance: ' + error, 'error');
            }
        });
    });
});

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '300px';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(notification);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(notification);
        bsAlert.close();
    }, 5000);
}

function formatDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    return date.toLocaleString('en-US', { timeZone: 'Africa/Cairo' });
}
