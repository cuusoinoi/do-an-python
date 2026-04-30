// Sidebar Elements
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");
const toggleBtn = document.getElementById("toggleSidebar");

const isMobileTablet = () => window.innerWidth <= 1023;

// Close all submenus
function closeAllSubmenus(except = null) {
    document.querySelectorAll(".sidebar__item--open").forEach((el) => {
        if (el !== except) el.classList.remove("sidebar__item--open");
    });
    document.querySelectorAll(".sidebar__submenu-popup").forEach((p) => (p.style.display = "none"));
}

// Toggle Sidebar
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        if (isMobileTablet()) {
            sidebar.classList.toggle("sidebar--open");
            overlay.classList.toggle("overlay--active");
        } else {
            sidebar.classList.toggle("sidebar--collapsed");
        }
    });
}

// Overlay click to close sidebar on mobile
if (overlay) {
    overlay.addEventListener("click", () => {
        sidebar.classList.remove("sidebar--open");
        overlay.classList.remove("overlay--active");
    });
}

// Submenu toggle
document.querySelectorAll(".sidebar__item--has-submenu").forEach((item) => {
    const link = item.querySelector(".sidebar__link");
    const submenu = item.querySelector(".sidebar__submenu");
    const popup = item.querySelector(".sidebar__submenu-popup");

    // Click handler for accordion (expanded mode & mobile)
    if (link) {
        link.addEventListener("click", (e) => {
            e.stopPropagation();
            const collapsed = sidebar.classList.contains("sidebar--collapsed");

            if (isMobileTablet()) {
                // Accordion behavior on mobile
                if (item.classList.contains("sidebar__item--open")) {
                    item.classList.remove("sidebar__item--open");
                } else {
                    closeAllSubmenus(item);
                    item.classList.add("sidebar__item--open");
                }
            } else if (!collapsed) {
                // Normal accordion desktop (only when expanded)
                if (item.classList.contains("sidebar__item--open")) {
                    item.classList.remove("sidebar__item--open");
                } else {
                    closeAllSubmenus(item);
                    item.classList.add("sidebar__item--open");
                }
            }
            // When collapsed, hover handles the popup - click does nothing
        });
    }

    // Hover handler for popup submenu (collapsed mode only)
    item.addEventListener("mouseenter", () => {
        const collapsed = sidebar.classList.contains("sidebar--collapsed");
        if (collapsed && popup && !isMobileTablet()) {
            closeAllSubmenus(item);
            const rect = item.getBoundingClientRect();
            popup.innerHTML = submenu.innerHTML;
            popup.style.top = `${rect.top}px`;
            popup.style.display = "flex";
        }
    });

    item.addEventListener("mouseleave", (e) => {
        const collapsed = sidebar.classList.contains("sidebar--collapsed");
        if (collapsed && popup && !isMobileTablet()) {
            // Check if mouse moved to popup
            const relatedTarget = e.relatedTarget;
            if (!popup.contains(relatedTarget)) {
                popup.style.display = "none";
            }
        }
    });

    // Keep popup open when hovering over it
    if (popup) {
        popup.addEventListener("mouseenter", () => {
            popup.style.display = "flex";
        });

        popup.addEventListener("mouseleave", () => {
            popup.style.display = "none";
        });
    }
});

// Close submenus when clicking outside
document.addEventListener("click", (e) => {
    if (!e.target.closest('.sidebar__item--has-submenu')) {
        closeAllSubmenus();
    }
});

// Theme Toggle
document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');
    const icon = themeToggle?.querySelector('i');
    const themeText = document.getElementById('themeToggleText');
    const savedTheme = localStorage.getItem('theme');

    // Function to update theme text and icon
    function updateThemeDisplay(isDark) {
        if (icon) {
            icon.classList.replace(isDark ? 'fa-moon' : 'fa-sun', isDark ? 'fa-sun' : 'fa-moon');
        }
        if (themeText) {
            themeText.textContent = isDark ? 'Giao diện sáng' : 'Giao diện tối';
        }
    }

    // Load saved theme
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        updateThemeDisplay(true);
    } else {
        updateThemeDisplay(false);
    }

    // Update chart theme on load
    window.addEventListener('load', () => {
        if (typeof updateChartTheme === 'function') updateChartTheme();
    });

    // Theme toggle click
    themeToggle?.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        updateThemeDisplay(isDark);

        if (typeof updateChartTheme === 'function') {
            updateChartTheme();
        }
    });
});

// Toast notifications from URL params
document.addEventListener('DOMContentLoaded', function() {
    const params = new URLSearchParams(window.location.search);
    const msg = params.get('msg');
    const success = params.get('success');
    const error = params.get('error');

    if (msg && (success || error)) {
        const toast = document.createElement('div');
        toast.className = 'toast ' + (success ? 'success' : 'error');
        toast.innerHTML = success ?
            `<i class="fas fa-check-circle"></i> ${msg}` :
            `<i class="fas fa-exclamation-circle"></i> ${msg}`;
        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Auto hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Custom Alert và Confirm - Thay thế alert() và confirm() mặc định
(function() {
    // Tạo modal container nếu chưa có
    if (!document.getElementById('custom-modal-container')) {
        const modalContainer = document.createElement('div');
        modalContainer.id = 'custom-modal-container';
        modalContainer.innerHTML = `
            <div class="custom-modal-overlay" id="custom-modal-overlay"></div>
            <div class="custom-modal" id="custom-modal">
                <div class="custom-modal-header">
                    <h3 class="custom-modal-title" id="custom-modal-title"></h3>
                    <button class="custom-modal-close" id="custom-modal-close">&times;</button>
                </div>
                <div class="custom-modal-body" id="custom-modal-body"></div>
                <div class="custom-modal-footer" id="custom-modal-footer"></div>
            </div>
        `;
        document.body.appendChild(modalContainer);
    }

    // Lưu trữ các handlers để có thể xóa
    let currentHandlers = [];

    // Xóa tất cả event listeners cũ
    function clearHandlers() {
        currentHandlers.forEach(handler => {
            if (handler.element && handler.event && handler.fn) {
                handler.element.removeEventListener(handler.event, handler.fn);
            }
        });
        currentHandlers = [];
    }

    // Hàm hiển thị Alert đẹp
    window.showAlert = function(message, title = 'Thông báo', type = 'info') {
        return new Promise((resolve) => {
            clearHandlers();
            
            const overlay = document.getElementById('custom-modal-overlay');
            const modal = document.getElementById('custom-modal');
            const modalTitle = document.getElementById('custom-modal-title');
            const modalBody = document.getElementById('custom-modal-body');
            const modalFooter = document.getElementById('custom-modal-footer');
            const closeBtn = document.getElementById('custom-modal-close');

            // Set icon và màu theo type
            const icons = {
                'info': '<i class="fas fa-info-circle"></i>',
                'success': '<i class="fas fa-check-circle"></i>',
                'warning': '<i class="fas fa-exclamation-triangle"></i>',
                'error': '<i class="fas fa-times-circle"></i>'
            };
            const colors = {
                'info': '#007bff',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545'
            };

            modalTitle.innerHTML = icons[type] + ' ' + title;
            modalTitle.style.color = colors[type];
            modalBody.innerHTML = '<p>' + message + '</p>';
            modalFooter.innerHTML = '<button class="custom-modal-btn custom-modal-btn-primary" id="custom-modal-ok">OK</button>';

            overlay.style.display = 'flex';
            modal.style.display = 'block';
            setTimeout(() => {
                overlay.classList.add('active');
                modal.classList.add('active');
            }, 10);

            const closeModal = () => {
                overlay.classList.remove('active');
                modal.classList.remove('active');
                setTimeout(() => {
                    overlay.style.display = 'none';
                    modal.style.display = 'none';
                }, 300);
                resolve(true);
            };

            const okBtn = document.getElementById('custom-modal-ok');
            const okHandler = () => closeModal();
            const closeHandler = () => closeModal();
            const overlayHandler = (e) => {
                if (e.target === overlay) closeModal();
            };

            okBtn.addEventListener('click', okHandler);
            closeBtn.addEventListener('click', closeHandler);
            overlay.addEventListener('click', overlayHandler);

            currentHandlers.push(
                { element: okBtn, event: 'click', fn: okHandler },
                { element: closeBtn, event: 'click', fn: closeHandler },
                { element: overlay, event: 'click', fn: overlayHandler }
            );
        });
    };

    // Hàm hiển thị Confirm đẹp
    window.showConfirm = function(message, title = 'Xác nhận') {
        return new Promise((resolve) => {
            clearHandlers();
            
            const overlay = document.getElementById('custom-modal-overlay');
            const modal = document.getElementById('custom-modal');
            const modalTitle = document.getElementById('custom-modal-title');
            const modalBody = document.getElementById('custom-modal-body');
            const modalFooter = document.getElementById('custom-modal-footer');
            const closeBtn = document.getElementById('custom-modal-close');

            modalTitle.innerHTML = '<i class="fas fa-question-circle"></i> ' + title;
            modalTitle.style.color = '#ffc107';
            modalBody.innerHTML = '<p>' + message + '</p>';
            modalFooter.innerHTML = `
                <button class="custom-modal-btn custom-modal-btn-secondary" id="custom-modal-cancel">Hủy</button>
                <button class="custom-modal-btn custom-modal-btn-primary" id="custom-modal-confirm">Xác nhận</button>
            `;

            overlay.style.display = 'flex';
            modal.style.display = 'block';
            setTimeout(() => {
                overlay.classList.add('active');
                modal.classList.add('active');
            }, 10);

            const closeModal = (result) => {
                overlay.classList.remove('active');
                modal.classList.remove('active');
                setTimeout(() => {
                    overlay.style.display = 'none';
                    modal.style.display = 'none';
                }, 300);
                resolve(result);
            };

            // Gắn event listeners mới
            const confirmBtn = document.getElementById('custom-modal-confirm');
            const cancelBtn = document.getElementById('custom-modal-cancel');
            
            const confirmHandler = () => closeModal(true);
            const cancelHandler = () => closeModal(false);
            const closeHandler = () => closeModal(false);
            const overlayHandler = (e) => {
                if (e.target === overlay) closeModal(false);
            };

            confirmBtn.addEventListener('click', confirmHandler);
            cancelBtn.addEventListener('click', cancelHandler);
            closeBtn.addEventListener('click', closeHandler);
            overlay.addEventListener('click', overlayHandler);

            currentHandlers.push(
                { element: confirmBtn, event: 'click', fn: confirmHandler },
                { element: cancelBtn, event: 'click', fn: cancelHandler },
                { element: closeBtn, event: 'click', fn: closeHandler },
                { element: overlay, event: 'click', fn: overlayHandler }
            );
        });
    };

    // Override alert() và confirm() mặc định
    window.alert = function(message) {
        return showAlert(message, 'Thông báo', 'info');
    };

    // Helper function để sử dụng confirm trong onclick
    // Sử dụng: onclick="return confirmDelete('Bạn có chắc muốn xóa?', this.href)"
    window.confirmDelete = function(message, url) {
        showConfirm(message || 'Bạn có chắc muốn xóa?', 'Xác nhận').then(result => {
            if (result && url) {
                window.location.href = url;
            }
        });
        return false;
    };

    // Override confirm() - trả về Promise
    window.confirm = function(message) {
        return showConfirm(message, 'Xác nhận');
    };
})();
