import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit Dashboard
st.set_page_config(page_title="Accounting Dashboard", layout="wide")

st.title('Accounting Analytics Dashboard')
st.sidebar.title('Data Upload and Selection')

# File upload
uploaded_file = st.sidebar.file_uploader("Upload your Excel or CSV file", type=['csv', 'xls', 'xlsx'])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Clean column names: Strip whitespace and replace NaN with placeholders
    df.columns = df.columns.str.strip()
    df.columns = ['Column_' + str(i) if pd.isna(col) else col for i, col in enumerate(df.columns)]

    # Display the entire table for user reference
    st.write("### Full Table View")
    st.write(df)

    # Create a multiselect box for row selection
    row_selection = st.multiselect(
        "Select rows to include in the analysis (by index):",
        options=df.index.tolist(),
        default=[],
        help="Hold down the shift or ctrl key to select multiple rows"
    )

    # Button to submit the selection and create charts
    submit_button = st.button("Submit", key='submit_button')

    # Check if the button is clicked and if the number of selected rows is >= 2
    if submit_button:
        if len(row_selection) >= 2:
            # Filter the DataFrame to only include selected rows
            selected_df = df.loc[row_selection]

            # Check if the selected DataFrame has the necessary columns for analysis
            if len(selected_df.columns) < 3:
                st.error("The selected data does not have enough columns to perform analysis.")
            else:
                # Assume the first column is 'Particulars' and the rest are numerical data
                particulars_col = selected_df.columns[0]
                data_cols = selected_df.columns[2:]  # Columns representing months or numerical data
                
                # Display the selected rows
                st.write("### Selected Rows for Analysis")
                st.write(selected_df)

                # Bar Chart - Sum of the numerical data columns
                with st.container():
                    st.write("### Bar Chart: Sum of Selected Rows")
                    sum_data = selected_df[data_cols].sum(axis=0)
                    fig_bar = px.bar(
                        x=sum_data.index,
                        y=sum_data.values,
                        title='Bar Chart for Selected Data',
                        text=sum_data.values,
                        labels={'x': 'Categories', 'y': 'Values'}
                    )
                    fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                    fig_bar.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_bar, use_container_width=True)

                # Pie Chart - Distribution of the first selected numerical column
                with st.container():
                    st.write("### Pie Chart: Distribution of First Numerical Column")
                    first_data_col = data_cols[0]
                    fig_pie = px.pie(
                        selected_df,
                        names=particulars_col,
                        values=first_data_col,
                        title=f'Distribution of {first_data_col}',
                        hole=0.3
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)

                # Line Chart - Trend over the numerical columns
                with st.container():
                    st.write("### Line Chart: Trend Over Time")
                    fig_line = px.line(
                        selected_df,
                        x=particulars_col,
                        y=data_cols,
                        title='Line Chart for Selected Data Over Time'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)

                # Treemap - Breakdown of the first numerical column by "Particulars"
                with st.container():
                    st.write("### Treemap: Breakdown by Particulars")
                    fig_treemap = px.treemap(
                        selected_df,
                        path=[particulars_col],
                        values=first_data_col,
                        title='Treemap of Selected Data'
                    )
                    st.plotly_chart(fig_treemap, use_container_width=True)

                # Scatter Plot - Correlation between the first two numerical columns
                if len(data_cols) >= 2:
                    with st.container():
                        st.write("### Scatter Plot: Correlation Between Two Numerical Columns")
                        fig_scatter = px.scatter(
                            selected_df,
                            x=data_cols[0],
                            y=data_cols[1],
                            title=f'Scatter Plot: {data_cols[0]} vs {data_cols[1]}',
                            labels={'x': data_cols[0], 'y': data_cols[1]}
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("Please select at least 2 rows to generate the charts.")
