# CSS for modern premium UI styling (inspired by LocalSend's clean layout and Cinnamon GTK theme compatibility)
CSS_STYLE = """
window {
    font-family: 'Cantarell', 'Ubuntu', sans-serif;
}

headerbar {
    padding: 8px;
}

.title {
    font-weight: bold;
    font-size: 16px;
}

.dashboard-container {
    padding: 24px;
}

.reminder-banner {
    background-color: rgba(239, 68, 68, 0.06); /* Soft, light pastel red */
    border: 1px solid rgba(239, 68, 68, 0.25);  /* Clean crimson border */
    color: #b91c1c;                             /* High-contrast dark red text */
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.reminder-banner-info {
    background-color: rgba(245, 158, 11, 0.06); /* Soft, light pastel amber */
    border: 1px solid rgba(245, 158, 11, 0.25);  /* Clean orange/amber border */
    color: #b45309;                             /* High-contrast dark orange text */
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.banner-title {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 6px;
}

.reminder-banner .banner-title {
    color: #991b1b; /* Darker red for bold title */
}

.reminder-banner-info .banner-title {
    color: #92400e; /* Darker orange for bold title */
}

.log-banner {
    background-color: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.28);
    color: #92400e;
    padding: 4px 8px;
    border-radius: 8px;
}

.log-banner label {
    color: #92400e;
    font-size: 12px;
}

.log-banner button.btn-secondary {
    background-color: rgba(146, 64, 14, 0.06);
    color: #92400e;
    font-size: 12px;
    font-weight: 500;
    min-height: 24px;
    padding: 2px 9px;
    border-radius: 7px;
    border: 1px solid rgba(146, 64, 14, 0.16);
}

.log-banner button.btn-secondary:hover {
    background-color: rgba(146, 64, 14, 0.12);
}

.card {
    background-color: @theme_base_color;
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 20px; /* Highly rounded corners like LocalSend */
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.card-title {
    font-size: 16px;
    font-weight: bold;
    color: @theme_selected_bg_color; /* Dynamic system accent color */
}

.card-header {
    margin-bottom: 12px;
}

.modal-card-title {
    font-size: 18px;
    font-weight: 800;
    color: @theme_selected_bg_color;
    margin-bottom: 15px;
    border-bottom: 2px solid alpha(@theme_selected_bg_color, 0.15);
    padding-bottom: 6px;
}

.sub-card {
    background-color: rgba(128, 128, 128, 0.04);
    border: 1px solid rgba(128, 128, 128, 0.08);
    border-radius: 12px;
    padding: 14px;
    margin-top: 6px;
    margin-bottom: 6px;
}

.sub-card-title {
    font-size: 14px;
    font-weight: bold;
    color: @theme_fg_color;
}

.dashboard-section-title {
    font-size: 18px;
    font-weight: bold;
    color: @theme_selected_bg_color;
}

.status-badge-unpaid {
    background-color: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
}

.status-badge-paid {
    background-color: rgba(16, 185, 129, 0.12);
    color: #15803d;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
}

.status-badge-prepaid {
    background-color: alpha(@theme_selected_bg_color, 0.12);
    color: @theme_selected_bg_color;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
}

button.btn-primary, window.dialog button.btn-primary, window button.btn-primary, .btn-primary {
    background-color: @theme_selected_bg_color; /* Dynamic system accent color */
    background-image: none;                     /* Crucial to override Cinnamon system gradients */
    color: @theme_selected_fg_color;            /* High-contrast system selected text color */
    font-weight: bold;
    border-radius: 20px; /* Round pill buttons like LocalSend */
    padding: 8px 20px;
    border: none;
}

button.btn-primary:hover, window.dialog button.btn-primary:hover, window button.btn-primary:hover, .btn-primary:hover {
    background-color: alpha(@theme_selected_bg_color, 0.85);
    background-image: none;
    opacity: 0.9;
}

button.btn-secondary, window.dialog button.btn-secondary, window button.btn-secondary, .btn-secondary {
    background-color: rgba(128, 128, 128, 0.1);
    background-image: none;
    color: @theme_fg_color;
    font-weight: bold;
    border-radius: 20px;
    padding: 6px 14px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}

button.btn-secondary:hover, window.dialog button.btn-secondary:hover, window button.btn-secondary:hover, .btn-secondary:hover {
    background-color: rgba(128, 128, 128, 0.18);
}

button.btn-success, window.dialog button.btn-success, window button.btn-success, .btn-success {
    background-color: rgba(128, 128, 128, 0.1);
    background-image: none;
    color: @theme_fg_color;
    font-weight: bold;
    border-radius: 20px;
    padding: 6px 14px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}

button.btn-success:hover, window.dialog button.btn-success:hover, window button.btn-success:hover, .btn-success:hover {
    background-color: rgba(128, 128, 128, 0.18);
}

button.btn-warning, window.dialog button.btn-warning, window button.btn-warning, .btn-warning {
    background-color: rgba(128, 128, 128, 0.1);
    background-image: none;
    color: @theme_fg_color;
    font-weight: bold;
    border-radius: 20px;
    padding: 6px 14px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}

button.btn-warning:hover, window.dialog button.btn-warning:hover, window button.btn-warning:hover, .btn-warning:hover {
    background-color: rgba(128, 128, 128, 0.18);
}

button.btn-danger, window.dialog button.btn-danger, window button.btn-danger, .btn-danger {
    background-color: rgba(239, 68, 68, 0.08); /* Soft pastel red */
    background-image: none;
    color: #ef4444;                             /* Darker red */
    font-weight: bold;
    border-radius: 20px;
    padding: 6px 14px;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

button.btn-danger:hover, window.dialog button.btn-danger:hover, window button.btn-danger:hover, .btn-danger:hover {
    background-color: rgba(239, 68, 68, 0.15);
}




.sidebar {
    background-color: @theme_bg_color;
    border-right: 1px solid rgba(128, 128, 128, 0.15);
    padding: 12px;
}

.sidebar-button {
    padding: 12px 24px;
    color: @theme_fg_color;
    font-weight: 500;
    background: none;
    border: none;
    border-radius: 24px; /* LocalSend pill style */
    margin: 6px 0;
    opacity: 0.8;
}

.sidebar-button:hover {
    background-color: rgba(128, 128, 128, 0.1);
    opacity: 1.0;
}

.sidebar-button-active {
    background-color: alpha(@theme_selected_bg_color, 0.15); /* Dynamic system accent color with transparency */
    color: @theme_selected_bg_color;
    font-weight: bold;
    opacity: 1.0;
}

.value-label {
    font-size: 15px;
    opacity: 0.8;
}

.compact-dropdown popover listview row:selected {
    background-color: alpha(@theme_selected_bg_color, 0.16);
    color: @theme_selected_bg_color;
}

.compact-dropdown popover listview row:selected label {
    color: @theme_selected_bg_color;
    font-weight: bold;
}

.bold-value {
    font-weight: bold;
}

/* Excel-like details tables styles */
.details-header-box {
    margin-bottom: 10px;
}

.details-tab-title {
    font-size: 18px;
    font-weight: bold;
    color: @theme_selected_bg_color;
    margin-bottom: 14px;
}

.details-grid {
    background-color: @theme_base_color;
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 12px;
    padding: 8px;
}

.details-grid-header {
    font-weight: bold;
    background-color: alpha(@theme_selected_bg_color, 0.08);
    color: @theme_selected_bg_color;
    padding: 10px 14px;
    border-radius: 6px;
}

.details-grid-cell {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.08);
}

.details-grid-cell-bold {
    padding: 10px 14px;
    font-weight: bold;
    border-bottom: 1px solid rgba(128, 128, 128, 0.08);
}

.details-formula {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: alpha(@theme_fg_color, 0.85);
    background-color: rgba(128, 128, 128, 0.06);
    padding: 4px 8px;
    border-radius: 6px;
}
"""
