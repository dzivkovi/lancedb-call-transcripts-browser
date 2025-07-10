#!/usr/bin/env python3
"""
Professional LanceDB Browser
Clean, Excel-style interface focused on readable data
"""

import streamlit as st
import lancedb
import duckdb
import pandas as pd
import argparse
import sys
from datetime import datetime

st.set_page_config(
    page_title="LanceDB Call Transcript Browser",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for professional styling
st.markdown(
    """
<style>
    .main-header {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .text-preview {
        max-height: 200px;
        overflow-y: auto;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    .nav-button {
        margin: 0.25rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def connect_db():
    """Connect to the LanceDB database"""
    return lancedb.connect(".")


@st.cache_data
def load_table_metadata():
    """Load table metadata for caching"""
    db = connect_db()
    table = db.open_table(st.session_state.table_name)

    try:
        total_rows = table.count_rows()
    except:
        total_rows = None

    # Get sample for analysis
    sample = table.to_pandas().head(100)

    # Define columns of interest (hide technical columns)
    display_columns = [
        "session_id",
        "timestamp",
        "text",
        "target",
        "session_type",
        "content_type",
    ]
    available_columns = [col for col in display_columns if col in sample.columns]

    return {
        "total_rows": total_rows,
        "all_columns": list(sample.columns),
        "display_columns": available_columns,
        "sample": sample,
        "unique_sessions": sample["session_id"].nunique()
        if "session_id" in sample.columns
        else 0,
    }


def get_table():
    """Get table object (not cached)"""
    db = connect_db()
    return db.open_table(st.session_state.table_name)


def convert_timestamp(timestamp):
    """Convert Unix timestamp to readable format"""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)


def get_data_page(table, page_num, page_size, columns=None):
    """Get a specific page of data"""
    offset = (page_num - 1) * page_size

    try:
        df = table.to_pandas()

        if columns:
            df = df[columns]

        # Convert timestamp if present
        if "timestamp" in df.columns:
            df["readable_time"] = df["timestamp"].apply(convert_timestamp)

        return df.iloc[offset : offset + page_size]
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def aggregate_sessions(table):
    """Get aggregated session texts"""
    try:
        lance_data = table.to_lance()

        sql = """
        SELECT 
            session_id,
            FIRST(timestamp) as first_timestamp,
            STRING_AGG(text, ' ') as full_text,
            COUNT(*) as chunk_count,
            FIRST(target) as participant,
            FIRST(session_type) as session_type
        FROM 
            (SELECT * FROM lance_data ORDER BY timestamp, chunk_id ASC) 
        GROUP BY 
            session_id
        ORDER BY first_timestamp DESC
        """

        result = duckdb.query(sql).to_df()

        # Convert timestamps
        if "first_timestamp" in result.columns:
            result["readable_time"] = result["first_timestamp"].apply(convert_timestamp)

        return result

    except Exception as e:
        st.error(f"Error aggregating sessions: {e}")
        return pd.DataFrame()


# Main Application
def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>Call Transcript Browser</h1>
        <p>Professional interface for browsing LanceDB call transcripts</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load metadata
    with st.spinner("Loading database..."):
        metadata = load_table_metadata()
        table = get_table()

    if metadata["total_rows"] == 0:
        st.error("No data found in the database")
        return

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", f"{metadata['total_rows']:,}")
    with col2:
        st.metric("Unique Sessions", metadata["unique_sessions"])
    with col3:
        st.metric("Data Columns", len(metadata["all_columns"]))
    with col4:
        if metadata["sample"]["text"].notna().any():
            avg_length = metadata["sample"]["text"].str.len().mean()
            st.metric("Avg Text Length", f"{avg_length:.0f} chars")

    st.markdown("---")

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(
        ["Raw Data Browser", "Session Transcripts", "Data Export"]
    )

    with tab1:
        st.subheader("Raw Data Browser")

        # Controls
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            page_size = st.selectbox("Records per page:", [10, 25, 50, 100], index=1)

        with col2:
            total_pages = (metadata["total_rows"] + page_size - 1) // page_size
            page_num = st.number_input(
                "Page:", min_value=1, max_value=total_pages, value=1
            )

        with col3:
            show_columns = st.multiselect(
                "Columns to display:",
                metadata["display_columns"],
                default=["session_id", "text", "target"],
            )

        with col4:
            st.write(f"Page {page_num:,} of {total_pages:,}")
            st.write(
                f"Records {(page_num - 1) * page_size + 1:,}-{min(page_num * page_size, metadata['total_rows']):,}"
            )

        # Navigation buttons
        nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

        with nav_col1:
            if st.button("First", disabled=(page_num == 1)):
                st.query_params["page"] = "1"
                st.rerun()

        with nav_col2:
            if st.button("Previous", disabled=(page_num == 1)):
                st.query_params["page"] = str(max(1, page_num - 1))
                st.rerun()

        with nav_col3:
            if st.button("Next", disabled=(page_num == total_pages)):
                st.query_params["page"] = str(min(total_pages, page_num + 1))
                st.rerun()

        with nav_col4:
            if st.button("Last", disabled=(page_num == total_pages)):
                st.query_params["page"] = str(total_pages)
                st.rerun()

        with nav_col5:
            if st.button("Refresh"):
                st.cache_data.clear()
                st.rerun()

        # Data display
        if show_columns:
            page_data = get_data_page(
                table,
                page_num,
                page_size,
                show_columns
                + (["readable_time"] if "timestamp" in show_columns else []),
            )

            if not page_data.empty:
                # Configure column display
                column_config = {}

                if "text" in page_data.columns:
                    column_config["text"] = st.column_config.TextColumn(
                        "Text Content", width="large", help="Call transcript content"
                    )

                if "session_id" in page_data.columns:
                    column_config["session_id"] = st.column_config.TextColumn(
                        "Session ID", width="medium"
                    )

                if "readable_time" in page_data.columns:
                    column_config["readable_time"] = st.column_config.TextColumn(
                        "Timestamp", width="medium"
                    )

                st.dataframe(
                    page_data,
                    use_container_width=True,
                    column_config=column_config,
                    hide_index=True,
                )

                # Quick text preview for selected row
                if "text" in page_data.columns and not page_data.empty:
                    st.subheader("Text Preview")
                    selected_idx = st.selectbox(
                        "Select row to preview:",
                        range(len(page_data)),
                        format_func=lambda x: f"Row {(page_num - 1) * page_size + x + 1}: {page_data.iloc[x]['session_id'] if 'session_id' in page_data.columns else 'Record'}",
                    )

                    if selected_idx is not None:
                        text_content = page_data.iloc[selected_idx]["text"]
                        st.text_area("Full Text:", text_content, height=200)
            else:
                st.warning("No data found for this page")
        else:
            st.warning("Please select at least one column to display")

    with tab2:
        st.subheader("Complete Session Transcripts")

        with st.spinner("Aggregating session transcripts..."):
            sessions_df = aggregate_sessions(table)

        if not sessions_df.empty:
            st.success(f"Found {len(sessions_df)} complete sessions")

            # Session selector
            col1, col2 = st.columns([3, 1])

            with col1:
                session_options = sessions_df.apply(
                    lambda row: f"{row['session_id']} - {row['participant']} ({row['readable_time']})",
                    axis=1,
                ).tolist()

                selected_session_idx = st.selectbox(
                    "Select session:",
                    range(len(sessions_df)),
                    format_func=lambda x: session_options[x],
                )

            with col2:
                st.metric("Total Sessions", len(sessions_df))

            # Display selected session
            if selected_session_idx is not None:
                session = sessions_df.iloc[selected_session_idx]

                # Session metadata
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Session ID", session["session_id"])
                with col2:
                    st.metric("Participant", session["participant"])
                with col3:
                    st.metric("Chunks", session["chunk_count"])
                with col4:
                    st.metric("Text Length", f"{len(session['full_text']):,} chars")

                # Full transcript
                st.subheader("Complete Transcript")
                st.text_area(
                    "Full conversation:",
                    session["full_text"],
                    height=400,
                    help="Complete aggregated transcript for this session",
                )

                # Download individual session
                st.download_button(
                    label="Download This Session",
                    data=session["full_text"],
                    file_name=f"session_{session['session_id']}.txt",
                    mime="text/plain",
                )

            # Download all sessions
            st.markdown("---")
            sessions_csv = sessions_df.to_csv(index=False)
            st.download_button(
                label="Download All Sessions as CSV",
                data=sessions_csv,
                file_name="all_sessions.csv",
                mime="text/csv",
            )
        else:
            st.error("Could not aggregate sessions")

    with tab3:
        st.subheader("Data Export Options")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.markdown("**Quick Exports**")

            # Export current page
            if st.button("Export Current Page"):
                current_data = get_data_page(
                    table, page_num, page_size, metadata["display_columns"]
                )
                csv_data = current_data.to_csv(index=False)
                st.download_button(
                    label="Download Current Page",
                    data=csv_data,
                    file_name=f"page_{page_num}_data.csv",
                    mime="text/csv",
                )

            # Export all readable data
            if st.button("Export All Readable Data"):
                all_data = table.to_pandas()[metadata["display_columns"]]
                if "timestamp" in all_data.columns:
                    all_data["readable_time"] = all_data["timestamp"].apply(
                        convert_timestamp
                    )
                csv_data = all_data.to_csv(index=False)
                st.download_button(
                    label="Download All Data",
                    data=csv_data,
                    file_name="all_transcript_data.csv",
                    mime="text/csv",
                )

        with export_col2:
            st.markdown("**Custom Export**")

            export_columns = st.multiselect(
                "Select columns for export:",
                metadata["all_columns"],
                default=metadata["display_columns"],
            )

            if export_columns:
                if st.button("Generate Custom Export"):
                    custom_data = table.to_pandas()[export_columns]
                    csv_data = custom_data.to_csv(index=False)
                    st.download_button(
                        label="Download Custom Export",
                        data=csv_data,
                        file_name="custom_export.csv",
                        mime="text/csv",
                    )


# Search functionality
with st.sidebar:
    st.header("Search & Filter")

    search_term = st.text_input("Search in transcripts:")

    if search_term:
        with st.spinner("Searching..."):
            table = get_table()
            all_data = table.to_pandas()

            if "text" in all_data.columns:
                matches = all_data[
                    all_data["text"].str.contains(search_term, case=False, na=False)
                ]

                if not matches.empty:
                    st.success(f"Found {len(matches)} matches")

                    # Show preview of matches
                    for idx, (_, row) in enumerate(matches.head(5).iterrows()):
                        with st.expander(
                            f"Match {idx + 1}: {row.get('session_id', 'Unknown')}"
                        ):
                            text = row["text"]
                            # Highlight search term
                            start = text.lower().find(search_term.lower())
                            if start != -1:
                                preview = text[
                                    max(0, start - 50) : start + len(search_term) + 50
                                ]
                                st.write(f"...{preview}...")

                    # Download search results
                    csv_results = matches.to_csv(index=False)
                    st.download_button(
                        label="Download Search Results",
                        data=csv_results,
                        file_name=f"search_results_{search_term}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No matches found")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Professional LanceDB Browser - Clean, Excel-style interface for data exploration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  streamlit run %(prog)s                           # Browse whiskey_jack table
  streamlit run %(prog)s -- --table evidence_calls # Browse custom table
  streamlit run %(prog)s -- --table phone_records  # Browse phone records table
        """,
    )
    
    parser.add_argument(
        "--table",
        default="whiskey_jack",
        help="LanceDB table name (default: whiskey_jack)",
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Initialize session state with table name
    if "table_name" not in st.session_state:
        args = parse_args()
        st.session_state.table_name = args.table
    
    main()
