import streamlit as st
import os
from datetime import datetime
from services.host_management import HostManagement
from services.handling_log import *
from services.log_cleanup import get_cleanup_warning
from components.log_viewer import create_log_viewer

st.set_page_config(layout="wide")

# Centered single column form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("Box Configuration"):
        st.subheader("Host Configuration")
        
        boxname = st.text_input("Box Name", help="Enter the name of the box/host")
        
        # Reboot options in a compact row
        st.write("**Reboot Options:**")
        reboot_col1, reboot_col2 = st.columns(2)
        with reboot_col1:
            esx_reboot = st.radio("ESX", ["Yes", "No"], index=1, key="esx_reboot")
        with reboot_col2:
            vm_reboot = st.radio("VM", ["Yes", "No"], index=1, key="vm_reboot")
        
        hostname = st.text_input("ACLX Hostname (SOS VTOC)", help="Hostname containing ACLX DB script")
        script_name = st.text_input("Script Path (SOS VTOC)", help="Full path to script (e.g., /root/setup.sh)")
        
        # ADIOS configuration
        st.write("**ADIOS Configuration:**")
        adios_version = st.text_input("ADIOS Version", help="e.g., Redwood, Roble")
        
        adios_col1, adios_col2 = st.columns(2)
        with adios_col1:
            updateadios = st.radio("Update", ["Yes", "No"], index=1, key="updateadios")
        with adios_col2:
            ready_host = st.radio("Ready", ["Yes", "No"], index=0, key="ready_host")
        
        # Submit button with better styling
        submit = st.form_submit_button("🚀 Start Host Management", use_container_width=True)

log_placeholder = st.empty()

if submit:
    host_management_dict = {}
    if not boxname:
        st.error("⚠️ Please enter the box name")
    else:
        host_management_dict['system'] = boxname
        host_management_dict['esx_reboot'] = esx_reboot 
        host_management_dict['vm_reboot'] = vm_reboot
        if hostname and script_name:
            host_management_dict['hostname'] = hostname
            host_management_dict['script_name'] = script_name
        if updateadios == "Yes":
            host_management_dict['updateadios'] = updateadios
        if adios_version:
            host_management_dict['adios_versions'] = adios_version
        host_management_dict['ready_host'] = "Yes"
        
        # Show configuration summary
        with st.expander("📋 Configuration Summary", expanded=True):
            st.json(host_management_dict)
        
        # Execute host management
        with st.spinner("🔄 Executing host management..."):
            hm = HostManagement()
            hm.main(host_management_dict)
        
        st.success("✅ Host management operation completed!")

        # Display cleanup warning after operations
        warning_message, cleanup_stats = get_cleanup_warning()
        if warning_message and not st.session_state.get('cleanup_snoozed', False):
            st.warning(warning_message)
            
            # Add cleanup action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clean Up Old Logs", key="cleanup_host", help="Delete logs older than 24 hours"):
                    from services.log_cleanup import LogCleanup
                    with st.spinner("🧹 Cleaning up old logs..."):
                        cleanup = LogCleanup()
                        results = cleanup.schedule_cleanup()
                    
                    if results['deleted_count'] > 0:
                        st.success(f"✅ Deleted {results['deleted_count']} old log files, freed {results['total_freed_mb']:.2f} MB")
                    else:
                        st.info("ℹ️ No old logs to delete")
                    
                    st.rerun()
            
            with col2:
                if st.button("⏰ Snooze Warning", key="snooze_host", help="Dismiss warning for this session"):
                    st.session_state['cleanup_snoozed'] = True
                    st.rerun()

# Compact Log Viewer Section
st.divider()
st.subheader("📋 Live Logs")

# Use expander for log viewer to save space
with st.expander(" Live Log Viewer", expanded=boxname is not None):
    # Get the latest log file for the current box if available
    latest_log = get_latest_log()
    if latest_log and boxname:
        # Try to find log file for the specific box
        log_dir = "Logs"
        box_logs = []
        for f in os.listdir(log_dir):
            if f.endswith(".log") and boxname in f:
                box_logs.append(os.path.join(log_dir, f))
        
        if box_logs:
            box_log_path = max(box_logs, key=os.path.getmtime)
            st.info(f"📡 Live logs for **{boxname}**")
            create_log_viewer(box_log_path, key="host_live")
        else:
            st.info(f"No logs found for {boxname}. Showing latest available log.")
            create_log_viewer(latest_log, key="general_live")
    else:
        st.info("🔍 Start a host management operation to see live logs:")
        if latest_log:
            create_log_viewer(latest_log, key="latest_live")
        else:
            st.warning("No log files found. Logs will appear here after you run host operations.")

# Collapsible log history
with st.expander("� Log History"):
    # Show log history and statistics
    log_dir = "Logs"
    if os.path.exists(log_dir):
        log_files = []
        for f in os.listdir(log_dir):
            if f.endswith(".log"):
                file_path = os.path.join(log_dir, f)
                try:
                    stat = os.stat(file_path)
                    log_files.append({
                        'name': f,
                        'path': file_path,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    continue
        
        if log_files:
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            
            # Compact display of log files
            for i, log_file in enumerate(log_files[:5]):  # Show top 5
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.text(f"📄 {log_file['name'][:30]}..." if len(log_file['name']) > 30 else f"📄 {log_file['name']}")
                
                with col2:
                    st.text(f"📅 {log_file['modified_str']}")
                
                with col3:
                    size_mb = log_file['size'] / (1024 * 1024)
                    st.text(f"💾 {size_mb:.1f}MB")
                
                with col4:
                    if st.button("👁️", key=f"view_log_{i}", help="View log"):
                        st.session_state['selected_log'] = log_file['path']
            
            # Show selected log if any
            if 'selected_log' in st.session_state:
                st.divider()
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.subheader(f"📋 {os.path.basename(st.session_state['selected_log'])}")
                    create_log_viewer(st.session_state['selected_log'], key="selected_log_viewer")
                with col2:
                    st.write("")
                    if st.button("❌ Close", key="close_selected_log"):
                        del st.session_state['selected_log']
                        st.rerun()
        else:
            st.info("No log files found in the Logs directory.")
    else:
        st.warning("Logs directory not found.")