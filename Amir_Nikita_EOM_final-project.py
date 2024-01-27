import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

st.write("# Welcome to the Salaries dashboard")

# Read the CSV dataset
df = pd.read_csv('../data/ds_salaries.csv', converters={'work_year': pd.to_datetime},
                 dtype={'employment_type': 'category'},
                 na_values=[''])

# Convert the 'work_year' column to a string with the desired format
df['work_year'] = pd.to_datetime(df['work_year'], format='%Y')

# Replace employment type abbreviations with full names
df['employment_type'] = df['employment_type'].cat.rename_categories({'FT': 'Full-Time', 'CT': 'Contractual', 'PT': 'Part-Time', 'FL': 'Freelancer', 'SE' : 'Self-Employed'})


# Display the dataframe
st.write("## Here's our dataset 📈")
st.write("#### Data Science Salaries 2023 💸")
st.write("##### Salaries of different Data Science fields in the DS domain. "
         "Below we let you get familiar with the data table. "
         "Click on each column name to sort high/low:")
st.write(df)

# Line chart: Salary over work years
st.write("## Next is a line chart")
st.write("This line chart illustrates the average salary trends of Data Science professionals over the years. The x-axis represents the work years, and the y-axis displays the average salary amount. The chart provides insights into how salaries have evolved from 2020 to now, offering a glimpse of potential salary growth or fluctuations over time. The 'bi-annual' aspect indicates that the data is presented on a twice a year pulse, allowing viewers to observe salary changes over six-month intervals. By analyzing this chart, users can discern patterns in salary progression and make informed decisions related to career development and work experience.")
avg_salary_by_work_year = df.groupby('work_year')['salary'].mean().reset_index()
line_fig = px.line(avg_salary_by_work_year, x='work_year', y='salary', title='Salary Over Work Time (bi-annual)')
line_fig.update_yaxes(range=[0, 600000])
line_chart = st.plotly_chart(line_fig)

# Group by FT/PT employee and calculate average salary
avg_salary_by_dept = df.groupby('employment_type')['salary'].mean().reset_index()

# Sort by average salary in descending order
avg_salary_by_dept = avg_salary_by_dept.sort_values(by='salary', ascending=False)

# Bar chart: Average salary by employment type
st.write("## Here is a bar chart")
st.write("Bars indicate the average salary of Data Science professionals grouped by their employment type. It provides an overview of salary differences between different types of employment, such as Full-Time, Part-Time, Contractual, and Freelancer roles.")
bar_fig = px.bar(avg_salary_by_dept, x='employment_type', y='salary', title='Average Salary by employment type')
bar_chart = st.plotly_chart(bar_fig)


# Interactive update on a line chart click
st.write("## Time for interactive participation")
st.write("This allows you to choose a specific year for the bar chart below, and the code calculates the average salary for FT and PT employee groups.")

selected_year = st.selectbox('Select a year:', avg_salary_by_work_year['work_year'].dt.year.unique())
filtered_avg_salary_by_dept = avg_salary_by_dept[avg_salary_by_dept['employment_type'].isin(['Full-Time', 'Part-Time'])]
filtered_avg_salary_by_dept['salary'] = filtered_avg_salary_by_dept['salary'] * selected_year
bar_fig.data[0].x = filtered_avg_salary_by_dept['employment_type']
bar_fig.data[0].y = filtered_avg_salary_by_dept['salary']
bar_chart = st.plotly_chart(bar_fig)


# Calculate average salary by job title
avg_salary_by_job_title = df.groupby('job_title')['salary'].mean().reset_index()

# Create a dot plot: Average salary distribution by job title
st.write("## Interactive Dot Plot")
st.write("The result will be a job title plot that visually represents the distribution of average salaries for different job titles. Each bubble represents the salary distribution for a specific job title and allows for a quick visual comparison of salary distributions across different job titles.")

fig = go.Figure()
for job_title in avg_salary_by_job_title['job_title']:
    fig.add_trace(go.Box(
        y=df[df['job_title'] == job_title]['salary'],
        name=job_title
    ))

fig.update_layout(
    title='Average Salary Distribution by Job Title',
    xaxis_title='Job Title',
    yaxis_title='Salary'
)

# Display the plot using Streamlit
st.plotly_chart(fig)

# Count job title frequency
st.write("## Specialization frequency (size of the bubble matters)")
st.write("The chart below displays the frequency of each job title in the dataset. Data engineer being the most sought after. It provides a visual representation of the number of occurrences of each job title")
job_title_counts = df['job_title'].value_counts().reset_index()

job_title_counts = df['job_title'].value_counts().reset_index()
job_title_counts.columns = ['job_title', 'frequency']

# Bubble chart: Job title frequency
fig = px.scatter(job_title_counts, x='job_title', y='frequency', size='frequency',
                 size_max=50, title='Job Title Frequency (Bubble Chart)',
                 labels={'job_title': 'Job Title', 'frequency': 'Frequency'},
                 color_discrete_sequence=px.colors.qualitative.Pastel)

fig.update_xaxes(title='Job Title')
fig.update_yaxes(title='Frequency')

# Display the bubble chart using Streamlit
st.plotly_chart(fig)

st.write("## An example of great looking chart but useless as the proportions are unreadable")
# Create a hierarchical structure for the tree chart
unique_job_titles = job_title_counts['job_title'].unique()
root_node = {'name': 'Job Titles', 'children': []}

for job_title in unique_job_titles:
    job_node = {'name': job_title, 'value': job_title_counts[job_title_counts['job_title'] == job_title]['frequency'].values[0]}
    root_node['children'].append(job_node)

# Create the tree chart
fig = go.Figure(go.Sunburst(
    ids=[root_node['name']] + [f"{root_node['name']} - {child['name']}" for child in root_node['children']],
    labels=[root_node['name']] + [child['name'] for child in root_node['children']],
    parents=[''] + [root_node['name'] for child in root_node['children']],
    values=[sum(child['value'] for child in root_node['children'])] + [child['value'] for child in root_node['children']],
))

fig.update_layout(
    title='Job Title Frequency (Tree Chart)',
    margin=dict(l=0, r=0, b=0, t=40),
)

# Display the tree chart using Streamlit
st.plotly_chart(fig)

st.write("## Fixed with grouping to six categories")
# Define the grouping logic based on common keywords
group_mapping = {
    'Data Scientist': ['Data Scientist', 'DS', 'Data Science'],
    'Data Analyst': ['Data Analyst', 'DA'],
    'Machine Learning Engineer': ['Machine Learning Engineer', 'MLE', 'Machine Learning'],
    'Software Engineer': ['Software Engineer', 'SE', 'Software Developer'],
    'Researcher': ['Researcher', 'Research Scientist'],
    'Manager': ['Manager']
}

# Group the job titles into six categories
def group_job_titles(job_title):
    for category, keywords in group_mapping.items():
        for keyword in keywords:
            if keyword.lower() in job_title.lower():
                return category
    return 'Other'

job_title_counts['category'] = job_title_counts['job_title'].apply(group_job_titles)
category_counts = job_title_counts.groupby('category')['frequency'].sum().reset_index()

# Create the hierarchical structure for the tree chart
root_node = {'name': 'Job Categories', 'children': []}

for category in category_counts['category']:
    category_node = {'name': category, 'value': category_counts[category_counts['category'] == category]['frequency'].values[0]}
    root_node['children'].append(category_node)

# Create the tree chart
fig = go.Figure(go.Sunburst(
    ids=[root_node['name']] + [f"{root_node['name']} - {child['name']}" for child in root_node['children']],
    labels=[root_node['name']] + [child['name'] for child in root_node['children']],
    parents=[''] + [root_node['name'] for child in root_node['children']],
    values=[sum(child['value'] for child in root_node['children'])] + [child['value'] for child in root_node['children']],
))

fig.update_layout(
    title='Job Category Frequency (Tree Chart)',
    margin=dict(l=0, r=0, b=0, t=40),
)

# Display the tree chart using Streamlit
st.plotly_chart(fig)

# Create the treemap chart
st.write("### And Treemap is a winner")
fig = px.treemap(job_title_counts, path=['job_title'], values='frequency',
                 title='Job Title Frequency (Treemap Chart)',
                 color_discrete_sequence=px.colors.qualitative.Pastel)

# Display the treemap chart using Streamlit
st.plotly_chart(fig)

# Calculate the correlation matrix
st.write("### Now, what about the relationship between salary and remote-work?")
st.write("##### Surely, salary and remote-work have a positive correlation indicating a trend of DS professionals working from home.    ")
correlation_matrix = df[['salary_in_usd', 'salary', 'remote_ratio']].dropna().corr()

# Create the correlation heatmap
fig = px.imshow(correlation_matrix,
                labels=dict(x="Variable", y="Variable", color="Correlation"),
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                color_continuous_scale=px.colors.sequential.Viridis)

# Update layout for better readability
fig.update_layout(
    title='Correlation Heatmap',
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    width=600,
    height=600,
    margin=dict(t=50, r=50, b=50, l=50),
)

# Display the correlation heatmap using Streamlit
st.plotly_chart(fig)


# Define a dictionary to map country codes to their full names
country_code_to_name = {
    "AE": "United Arab Emirates",
    "AR": "Argentina",
    "CA": "Canada",
    "DE": "Germany",
    "GB": "Great Britain",
    "NG": "Nigeria",
    "IN": "India",
    "HK": "Hong Kong",
    "PT": "Portugal",
    "NL": "Netherlands",
    "CH": "Switzerland",
    "CF": "Central African Republic",
    "FR": "France",
    "AU": "Australia",
    "FI": "Finland",
    "UA": "Ukraine",
    "IE": "Ireland",
    "IL": "Israel",
    "GH": "Ghana",
    "AT": "Austria",
    "CO": "Colombia",
    "SG": "Singapore",
    "SE": "Sweden",
    "SI": "Slovenia",
    "MX": "Mexico",
    "UZ": "Uzbekistan",
    "BR": "Brazil",
    "TH": "Thailand",
    "HR": "Croatia",
    "PL": "Poland",
    "KW": "Kuwait",
    "VN": "Vietnam",
    "CY": "Cyprus",
    "AR": "Argentina",
    "AM": "Armenia",
    "BA": "Bosnia and Herzegovina",
    "KE": "Kenya",
    "GR": "Greece",
    "MK": "North Macedonia",
    "LV": "Latvia",
    "RO": "Romania",
    "PK": "Pakistan",
    "IT": "Italy",
    "MA": "Morocco",
    "LT": "Lithuania",
    "BE": "Belgium",
    "AS": "American Samoa",
    "IR": "Iran",
    "HU": "Hungary",
    "SK": "Slovakia",
    "CN": "China",
    "CZ": "Czech Republic",
    "CR": "Costa Rica",
    "TR": "Turkey",
    "CL": "Chile",
    "PR": "Puerto Rico",
    "DK": "Denmark",
    "BO": "Bolivia",
    "PH": "Philippines",
    "DO": "Dominican Republic",
    "EG": "Egypt",
    "ID": "Indonesia",
    "AE": "United Arab Emirates",
    "MY": "Malaysia",
    "JP": "Japan",
    "EE": "Estonia",
    "HN": "Honduras",
    "TN": "Tunisia",
    "RU": "Russia",
    "DZ": "Algeria",
    "IQ": "Iraq",
    "BG": "Bulgaria",
    "JE": "Jersey",
    "RS": "Serbia",
    "NZ": "New Zealand",
    "MD": "Moldova",
    "LU": "Luxembourg",
    "MT": "Malta"
}

st.write("### Worldmap of salaries around the world")
st.write("##### A country-level geomap with data points representing employee residence locations, where the color of each country represents the average salary in USD for employees from that country. The hover tooltip will show additional information such as the job title for each data point.")
# Map the country codes in the DataFrame to their full names
df['employee_residence'] = df['employee_residence'].map(country_code_to_name)
df['company_location'] = df['company_location'].map(country_code_to_name)

# Create the geomap using Plotly Express
fig = px.choropleth(df,
                    locations='employee_residence',   # Use the column containing the employee residence country names
                    locationmode='country names',    # Specify that the locations are country names
                    color='salary_in_usd',           # Replace 'salary_in_usd' with the column you want to use for color-coding data points
                    hover_name='job_title',          # Replace 'job_title' with the column you want to show on hover for each data point
                    title='Employee Residence and Company Locations Geomap',
                    projection='natural earth')      # You can change the 'projection' parameter to choose a different map projection

# Update layout for better readability
fig.update_layout(
    width=800,
    height=600,
)

# Display the geomap using Streamlit
st.plotly_chart(fig)

# Conclusion line
st.write("# Thank you for your interest in our DS Salaries Web App. We hope you enjoyed it!")
st.write("### In conclusion, we enjoyed visualizing data using an assortment of charts, finding interesting insights about job titles, salaries, demand and frequeny, and correlation between salary and remote work ratio.")

st.write("##### We'll leave you here to explore the rest of the dataset to follow your interests in case we missed something. Select a column from the dataset to visualize its distribution or explore the salary trend over the years.")

# Add an interactive element (dropdown) to select a column for visualization
selected_column = st.selectbox("Select a column for visualization:", df.columns)

# Create a plot based on the selected column
if selected_column != 'work_year':
    fig = px.histogram(df, x=selected_column, color='employment_type', title=f'{selected_column} Distribution by Employment Type')
else:
    # Extract the year from the 'work_year' column using the dt accessor
    df['year'] = df['work_year'].dt.year
    fig = px.line(df, x='year', y='salary', color='employment_type', title='Salary Trend by Year')

# Display the plot
st.plotly_chart(fig)
