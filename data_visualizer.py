import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Streamlit Dashboard
st.set_page_config(page_title="Accounting Dashboard", layout="wide")
st.markdown(
    """
    <style>
    /* Style the sidebar */
    .css-18e3th9 {
        background-color: #2E2E2E;
        color: white;
    }
    
    /* Style for headers */
    h1 {
        color: #ff6347;
        text-align: center;
    }
    
    /* Fancy filter style */
    .stSelectbox, .stMultiselect {
        background-color: #323232;
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Add transition effect */
    .stContainer {
        transition: transform 0.2s ease;
    }

    .stContainer:hover {
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Accounting Analytics Dashboard')
st.sidebar.title('Data Upload and Filters')

# File upload
uploaded_file = st.sidebar.file_uploader("Upload your Excel or CSV file", type=['csv', 'xls', 'xlsx'])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Drop "Sl No" or other indexing columns if present
    indexing_columns = [col for col in df.columns if 'sl no' in col.lower() or 'index' in col.lower()]
    df.drop(columns=indexing_columns, errors='ignore', inplace=True)
    
    # Convert columns to datetime if possible, and handle month-only data
    for col in df.columns:
        if 'date' in col.lower() or 'month' in col.lower():
            try:
                # Handle full date format (DD/MM/YYYY)
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                df['Month'] = df[col].dt.to_period('M')
            except:
                # If parsing fails, handle month names directly (e.g., "Jan", "Feb")
                if df[col].dtype == 'object':
                    df['Month'] = df[col].str.capitalize()  # Capitalize to ensure uniform month names

    # Show data preview
    st.write("### Data Preview:")
    st.write(df.head())

    # Filtering options based on column names
    st.sidebar.title('Filters')

    # Filter by name (assuming 'Name' column or similar exists)
    name_column = [col for col in df.columns if 'name' in col.lower() or 'client' in col.lower() or 'employee' in col.lower()]
    if name_column:
        name_column = name_column[0]
        name_options = df[name_column].dropna().unique()
        selected_name = st.sidebar.selectbox(f'Select {name_column}', ['All'] + list(name_options))
    else:
        selected_name = 'All'

    # Filter by month (either extracted from date or month names directly)
    selected_month = 'All'
    if 'Month' in df.columns:
        month_options = df['Month'].dropna().unique()
        selected_month = st.sidebar.selectbox('Select Month', ['All'] + list(month_options))

    # Filter by project
    project_column = [col for col in df.columns if 'project' in col.lower()]
    if project_column:
        project_column = project_column[0]
        project_options = df[project_column].dropna().unique()
        selected_project = st.sidebar.selectbox(f'Select {project_column}', ['All'] + list(project_options))
    else:
        selected_project = 'All'

    # Apply filters
    filtered_df = df.copy()
    if selected_name != 'All':
        filtered_df = filtered_df[filtered_df[name_column] == selected_name]

    if selected_month != 'All' and 'Month' in df.columns:
        filtered_df = filtered_df[filtered_df['Month'] == selected_month]

    if selected_project != 'All':
        filtered_df = filtered_df[filtered_df[project_column] == selected_project]

    # Find "amount" related columns
    amount_columns = [col for col in filtered_df.columns if 'amount' in col.lower()]
    if not amount_columns:
        st.warning("No 'Amount' columns found in the dataset.")
    else:
        primary_amount_column = amount_columns[0]  # Use the first "amount" column found for the charts

    # Display summary
    st.write(f"### Summary for Selected Filters")
    st.write(f"Total Records: {len(filtered_df)}")
    
    if primary_amount_column:
        st.write(f"Total {primary_amount_column}: {filtered_df[primary_amount_column].sum():,.2f}")

    # Create accounting-related charts
    st.write("## Data Visualizations")
    
    # Bar Chart - Group by name and sum the amounts
    if primary_amount_column:
        with st.container():
            st.write("### Bar Chart: Total Amounts by Company")
            grouped_df = filtered_df.groupby(name_column)[primary_amount_column].sum().reset_index()
            fig_bar = px.bar(
                grouped_df, 
                x=name_column, 
                y=primary_amount_column, 
                title=f'Bar Chart for Total {primary_amount_column} by {name_column}',
                text=primary_amount_column,
                hover_data={name_column: True, primary_amount_column: True}
            )
            # Remove y-axis labels and tick marks
            fig_bar.update_yaxes(visible=False, showticklabels=False)
            # Remove column name below the x-axis
            fig_bar.update_xaxes(title_text='')
            fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_bar.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

    # Replace line chart with a Treemap for hierarchical data visualization
    if project_column and primary_amount_column and name_column:
        with st.container():
            st.write("### Treemap: Breakdown by Project and Company")
            fig_treemap = px.treemap(
                filtered_df,
                path=[project_column, name_column],
                values=primary_amount_column,
                title='Treemap of Revenue by Project and Company',
                hover_data={primary_amount_column: True}
            )
            st.plotly_chart(fig_treemap, use_container_width=True)

    # Pie Chart - Distribution of amounts (by name or project)
    if len(name_column) > 0 and primary_amount_column:
        with st.container():
            st.write("### Pie Chart: Distribution")
            fig_pie = px.pie(
                filtered_df, 
                names=name_column, 
                values=primary_amount_column, 
                title=f'Distribution of {primary_amount_column} by {name_column}', 
                hole=0.3,
                hover_data={primary_amount_column: True}
            )
            # Display name, amount, and percentage in the labels
            fig_pie.update_traces(
                texttemplate='%{label}<br>Amount: %{value:,.2f}<br>%{percent}', 
                textposition='inside', 
                textinfo='label+value+percent',
                hovertemplate='<b>%{label}</b><br>Amount: %{value:,.2f}<br>Percentage: %{percent}'
            )
            fig_pie.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Sunburst Chart - Hierarchical visualization (e.g., Project -> Name -> Amount)
    if project_column and primary_amount_column and name_column:
        with st.container():
            st.write("### Sunburst Chart: Hierarchical View")
            fig_sunburst = px.sunburst(
                filtered_df, 
                path=[project_column, name_column], 
                values=primary_amount_column, 
                title='Sunburst Chart for Hierarchical Data',
                hover_data={primary_amount_column: True}
            )
            # Display amount with the name in the labels
            fig_sunburst.update_traces(texttemplate='%{label}<br>Amount: %{value:,.2f}', textinfo='label+value')
            fig_sunburst.update_layout(height=500)
            st.plotly_chart(fig_sunburst, use_container_width=True)
