import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")

st.title("📝 Feedback & Issue Tracker")
st.markdown("---")

# Initialize database
def init_db():
    """Initialize the SQLite database for feedback."""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            issue TEXT NOT NULL,
            status TEXT DEFAULT 'Ongoing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_feedback(name, issue):
    """Add new feedback to the database."""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (name, issue, status)
        VALUES (?, ?, 'Ongoing')
    ''', (name, issue))
    
    conn.commit()
    conn.close()

def get_all_feedback():
    """Get all feedback from the database."""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, issue, status, created_at, updated_at
        FROM feedback
        ORDER BY created_at DESC
    ''')
    
    feedback_list = cursor.fetchall()
    conn.close()
    
    return feedback_list

def update_feedback_status(feedback_id, status):
    """Update feedback status."""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE feedback
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, feedback_id))
    
    conn.commit()
    conn.close()

def delete_feedback(feedback_id):
    """Delete feedback from the database."""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Create two columns for form and feedback list
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Submit Feedback")
    
    with st.form("feedback_form"):
        # Name field
        name = st.text_input(
            "Name *",
            placeholder="Enter your name",
            help="Please provide your name for reference"
        )
        
        # Issue description
        issue = st.text_area(
            "Issue Description *",
            placeholder="Describe your issue or feedback in detail...",
            height=150,
            help="Please provide as much detail as possible about your issue"
        )
        
        # Submit button
        submitted = st.form_submit_button("📤 Submit Feedback", use_container_width=True)
        
        if submitted:
            if not name.strip():
                st.error("⚠️ Please enter your name")
            elif not issue.strip():
                st.error("⚠️ Please describe your issue")
            else:
                try:
                    add_feedback(name.strip(), issue.strip())
                    st.success("✅ Feedback submitted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error submitting feedback: {str(e)}")

with col2:
    st.subheader("📊 Feedback List")
    
    # Get all feedback
    feedback_list = get_all_feedback()
    
    if not feedback_list:
        st.info("📭 No feedback submitted yet. Be the first to share your thoughts!")
    else:
        # Status filter
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Ongoing", "Resolved"],
            index=0,
            key="status_filter"
        )
        
        # Filter feedback based on status
        if status_filter == "All":
            filtered_feedback = feedback_list
        else:
            filtered_feedback = [f for f in feedback_list if f[3] == status_filter]
        
        # Display feedback
        for i, feedback in enumerate(filtered_feedback):
            feedback_id, name, issue, status, created_at, updated_at = feedback
            
            # Convert timestamp to readable format
            created_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            updated_dt = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
            
            # Create expandable section for each feedback
            with st.expander(f"#{feedback_id} - {name} - {status}", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write("**Issue Description:**")
                    st.write(issue)
                    
                    st.write("**Submitted:**")
                    st.caption(f"📅 {created_dt.strftime('%Y-%m-%d %H:%M')}")
                    
                    if updated_dt != created_dt:
                        st.write("**Last Updated:**")
                        st.caption(f"🔄 {updated_dt.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    # Status toggle
                    new_status = "Resolved" if status == "Ongoing" else "Ongoing"
                    if st.button(f"🔄 Mark as {new_status}", key=f"status_{feedback_id}"):
                        update_feedback_status(feedback_id, new_status)
                        st.rerun()
                
                with col3:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{feedback_id}"):
                        delete_feedback(feedback_id)
                        st.rerun()
            
            st.divider()

# Statistics section
st.markdown("---")
st.subheader("📈 Feedback Statistics")

if feedback_list:
    # Calculate statistics
    total_feedback = len(feedback_list)
    ongoing_count = len([f for f in feedback_list if f[3] == "Ongoing"])
    resolved_count = len([f for f in feedback_list if f[3] == "Resolved"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Feedback", total_feedback)
    
    with col2:
        st.metric("🔄 Ongoing", ongoing_count)
    
    with col3:
        st.metric("✅ Resolved", resolved_count)
    
    with col4:
        if total_feedback > 0:
            resolution_rate = (resolved_count / total_feedback) * 100
            st.metric("📈 Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.metric("📈 Resolution Rate", "0%")
else:
    st.info("📊 No feedback data available yet")

# Export functionality
if feedback_list:
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    if st.button("📊 Export to CSV", key="export_csv"):
        # Create DataFrame
        df = pd.DataFrame(feedback_list, columns=[
            'ID', 'Name', 'Issue', 'Status', 'Created At', 'Updated At'
        ])
        
        # Convert to CSV
        csv = df.to_csv(index=False)
        
        # Download button
        st.download_button(
            label="💾 Download Feedback Data",
            data=csv,
            file_name=f"feedback_export_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )