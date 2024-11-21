""" Name: Chiara Bellini
CS230: 5-6
Data: Fortune 500 Corporate Headquarters
URL: Link to your web application on Streamlit Cloud (if posted)

Description:  This program provides insights into the Fortune 500 dataset by allowing users to upload a CSV file containing information about top fortune 500 companies of a determine fiscal year.
Users can explore key data points such as revenues, profits, and employee counts across various states and counties.
The program offers a range of interactive queries, including selecting the top companies by revenue, analyzing profit margins by state, and comparing revenue growth across states.
Visualizations include bar charts, scatter plots, and tables, which help users understand the distribution of companies by revenue, profit margins, and employee counts, as well as explore county-based statistics like the number of companies and total employee counts. """
import streamlit as st
import pandas as pd
import plotly.express as px

# [ST4] Set up the page configuration
st.set_page_config(page_title="Fortune 500 Insights", layout="wide")

# Add a title for the insights
st.title("Fortune 500 Companies Insights")

# [DA1] Load and clean data
@st.cache_data
def load_data(uploaded_file):
    # [PY3] Error checking with try/except - Try reading the data from the uploaded CSV file
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    # Debugging: print out column names to help identify issues
    st.write("### Columns in the uploaded dataset:")
    st.write(df.columns)

    #  Check if necessary columns exist
    required_columns = ['REVENUES', 'PROFIT', 'EMPLOYEES', 'NAME', 'STATE', 'COUNTY']
    #[PY4] A list comprehension:
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns in the uploaded data: {', '.join(missing_columns)}")
        return df

    # Clean the data by dropping rows with missing values in key columns
    df = df.dropna(subset=['REVENUES', 'PROFIT', 'EMPLOYEES'])

    # [DA1] Lambda function to clean columns by removing dollar signs and commas, and convert to appropriate types
    df['REVENUES'] = df['REVENUES'].apply(lambda x: float(str(x).replace('$', '').replace(',', '')) if isinstance(x, str) else x)
    df['PROFIT'] = df['PROFIT'].apply(lambda x: float(str(x).replace('$', '').replace(',', '')) if isinstance(x, str) else x)
    df['EMPLOYEES'] = df['EMPLOYEES'].apply(lambda x: int(str(x).replace(',', '')) if isinstance(x, str) else x)

    return df

# [ST1] File uploader widget for CSV
uploaded_file = st.file_uploader("Upload your Fortune 500 dataset", type="csv")

# If the user uploads a file
if uploaded_file is not None:
    # Load the data
    df = load_data(uploaded_file)

    # Check if the data loaded correctly
    if df.empty:
        st.error("No data to display due to missing columns or other issues.")
    else:
        # [PY5] Create a dictionary mapping state to total revenue
        state_revenue_dict = dict(df.groupby('STATE')['REVENUES'].sum())

        # Convert the dictionary into a DataFrame for better visualization
        state_revenue_df = pd.DataFrame(list(state_revenue_dict.items()), columns=['STATE', 'TOTAL_REVENUE'])

        # Display the total revenue by state as a table
        st.write("### Total Revenue by State:")
        st.write(state_revenue_df)

        # [DA2] & [ST2] What is the total revenue of the top X companies?
        top_x = st.slider("Select top X companies", min_value=1, max_value=50, step=1, value=10)

        top_companies = df[['NAME', 'REVENUES']].sort_values(by='REVENUES', ascending=False).head(top_x)
        total_revenue = top_companies['REVENUES'].sum()

        st.write(f"### Total Revenue of the Top {top_x} Companies: ${total_revenue:,.2f}")

        #[VIZ1] Bar chart displaying the revenues
        fig = px.bar(top_companies, x='NAME', y='REVENUES', title=f"Top {top_x} Companies by Revenue",
                     labels={'REVENUES': 'Revenue ($)', 'NAME': 'Company'})
        st.plotly_chart(fig)

        # [DA6] & [VIZ2] Create a pivot table for average revenue by state
        pivot_table = df.pivot_table(values='REVENUES', index='STATE', aggfunc='mean').reset_index()
        st.write("### Average Revenue by State")
        st.write(pivot_table)

        #[ST3]select box: What is the average profit margin of companies in <state>?
        state = st.selectbox("Select a state for Profit Margin", df['STATE'].unique())

        # Filter data for the selected state
        state_data = df[df['STATE'] == state]

        # Calculate the profit margin using a lambda function
        state_data['PROFIT_MARGIN'] = state_data.apply(
            lambda row: row['PROFIT'] / row['REVENUES'] * 100 if row['REVENUES'] != 0 else 0,
            axis=1
        )
        avg_profit_margin = state_data['PROFIT_MARGIN'].mean()

        # Display the average profit margin
        st.write(f"### Average Profit Margin for Companies in {state}: {avg_profit_margin:.2f}%")

        #[VIZ2] Create a scatter plot to show the profit margin for each company
        fig2 = px.scatter(
            state_data,
            x='NAME',  # Company names on the x-axis
            y='PROFIT_MARGIN',  # Profit margins on the y-axis
            title=f"Profit Margins for Companies in {state}",
            labels={'NAME': 'Company Name', 'PROFIT_MARGIN': 'Profit Margin (%)'},
            hover_data=['REVENUES', 'PROFIT'],  # Additional data to display on hover
        )

        # Improve layout for readability
        fig2.update_layout(
            xaxis_tickangle=45,  # Rotate x-axis labels for better readability
            margin=dict(l=40, r=40, t=50, b=100),  # Adjust margins
        )

        # Display the scatter plot
        st.plotly_chart(fig2)

        #  What is the average number of employees for companies in <state>?
        avg_employees = state_data['EMPLOYEES'].mean()
        st.write(f"### Average Number of Employees for Companies in {state}: {avg_employees:,.0f}")

        # How does the revenue growth in <state> compare to the national average?
        state_revenue_growth = state_data['REVENUES'].pct_change() * 100  # Percentage change in revenues
        national_avg_growth = df['REVENUES'].pct_change().mean() * 100

        state_avg_growth = state_revenue_growth.mean()

        st.write(f"### Revenue Growth in {state} compared to the National Average")
        st.write(f"State Average Revenue Growth: {state_avg_growth:.2f}%")
        st.write(f"National Average Revenue Growth: {national_avg_growth:.2f}%")


        # [MAP] Display a map showing locations of Fortune 500 companies
        st.write("### Map of Fortune 500 Companies by Location")
        company_locations = df[['NAME', 'LATITUDE', 'LONGITUDE']]
        st.map(company_locations)

        # [DA3]&[PY2] Which county has the most Fortune 500 companies?
        county_company_count = df['COUNTY'].value_counts().reset_index()
        county_company_count.columns = ['COUNTY', 'NUM_COMPANIES']
        top_county_by_companies = county_company_count.sort_values(by='NUM_COMPANIES', ascending=False).head(1)

        st.write(
            f"### County with the Most Fortune 500 Companies: {top_county_by_companies['COUNTY'].iloc[0]} (Companies: {top_county_by_companies['NUM_COMPANIES'].iloc[0]})"
        )

        # vertical bar chart showing top counties by number of companies
        fig4a = px.bar(
            county_company_count,
            x='COUNTY',
            y='NUM_COMPANIES',
            orientation='v',  # vertical bar chart
            title="Top Counties by Number of Companies",
            labels={'NUM_COMPANIES': 'Number of Companies', 'COUNTY': 'County'},
        )

        # Sort the bars by the number of companies in descending order
        fig4a.update_layout(yaxis=dict(categoryorder='total ascending'))

        st.plotly_chart(fig4a)


        # [DA4] Which county has the highest total employee count across all Fortune 500 companies?
        county_data = df[['COUNTY', 'EMPLOYEES']].groupby('COUNTY').sum().reset_index()
        top_county_by_employees = county_data.sort_values(by='EMPLOYEES', ascending=False).head(1)

        st.write(
            f"### County with the Highest Total Employee Count Across All Fortune 500 Companies: {top_county_by_employees['COUNTY'].iloc[0]} (Employees: {top_county_by_employees['EMPLOYEES'].iloc[0]:,})"
        )

        # Horizontal bar chart showing top counties by total employee count
        fig4b = px.bar(county_data, x='EMPLOYEES', y='COUNTY', orientation='h',
                       title="Top Counties by Total Employee Count",
                       labels={'EMPLOYEES': 'Total Employees', 'COUNTY': 'County'})

        # Sort the bars by total employees in descending order
        fig4b.update_layout(xaxis=dict(categoryorder='total descending'))

        st.plotly_chart(fig4b)
