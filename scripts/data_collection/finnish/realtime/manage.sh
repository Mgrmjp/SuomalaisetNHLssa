#!/bin/bash
#
# Real-Time NHL Monitor Management Script
#
# Usage:
#   ./manage.sh start    - Start the daemon
#   ./manage.sh stop     - Stop the daemon
#   ./manage.sh restart  - Restart the daemon
#   ./manage.sh status   - Check daemon status
#   ./manage.sh logs     - View daemon logs
#   ./manage.sh test     - Run integration tests
#

set -e

SERVICE_NAME="nhl-realtime"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="${SCRIPT_DIR}/realtime_monitor.py"
LOG_FILE="${SCRIPT_DIR}/logs/realtime_monitor.log"

cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script requires root privileges (use sudo)"
        exit 1
    fi
}

install_service() {
    log_info "Installing systemd service..."
    check_root

    cp "${SCRIPT_DIR}/${SERVICE_NAME}.service" "${SERVICE_FILE}"
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}"

    log_info "Service installed and enabled"
    log_info "To start: sudo systemctl start ${SERVICE_NAME}"
}

start_daemon() {
    log_info "Starting ${SERVICE_NAME} service..."
    check_root
    systemctl start "${SERVICE_NAME}"
    sleep 2
    status
}

stop_daemon() {
    log_info "Stopping ${SERVICE_NAME} service..."
    check_root
    systemctl stop "${SERVICE_NAME}"
    log_info "Service stopped"
}

restart_daemon() {
    log_info "Restarting ${SERVICE_NAME} service..."
    check_root
    systemctl restart "${SERVICE_NAME}"
    sleep 2
    status
}

status() {
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        log_info "Service is running"
        systemctl status "${SERVICE_NAME}" --no-pager -l
    else
        log_warn "Service is not running"
        systemctl status "${SERVICE_NAME}" --no-pager -l || true
    fi
}

view_logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "Showing last 50 lines of log (Ctrl+C to exit)..."
        tail -f -n 50 "$LOG_FILE"
    else
        log_warn "Log file not found: $LOG_FILE"
        log_info "Checking systemd journal..."
        sudo journalctl -u "${SERVICE_NAME}" -f -n 50
    fi
}

run_tests() {
    log_info "Running integration tests..."
    python3 "${SCRIPT_DIR}/test_integration.py"
}

run_manual() {
    log_info "Running monitor manually (foreground mode)..."
    log_info "Press Ctrl+C to stop"
    python3 "$MONITOR_SCRIPT"
}

show_help() {
    cat << EOF
Real-Time NHL Monitor Management Script

Usage: $0 <command>

Commands:
    install    Install systemd service
    start      Start the daemon service
    stop       Stop the daemon service
    restart    Restart the daemon service
    status     Check daemon status
    logs       View daemon logs (tail -f)
    test       Run integration tests
    manual     Run in manual/foreground mode
    help       Show this help message

Examples:
    # Install and start
    sudo $0 install
    sudo $0 start

    # Check status
    sudo $0 status

    # View logs
    sudo $0 logs

    # Run tests
    $0 test

    # Run manually (for testing)
    $0 manual

EOF
}

case "$1" in
    install)
        install_service
        ;;
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        restart_daemon
        ;;
    status)
        status
        ;;
    logs)
        view_logs
        ;;
    test)
        run_tests
        ;;
    manual)
        run_manual
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        log_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
