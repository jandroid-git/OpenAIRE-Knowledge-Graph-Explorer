import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# === Load data ===
projects = pd.read_csv('data/projects_data_csv/projects.csv')
project_funders = pd.read_csv('data/projects_data_csv/project_funder_rel.csv')
project_countries = pd.read_csv('data/projects_data_csv/project_country_rel.csv')
project_publications = pd.read_csv('data/projects_data_csv/project_publications.csv')
publication_project_rel = pd.read_csv('data/projects_data_csv/publication_project_rel.csv')

# === Preprocessing ===
projects['startDate'] = pd.to_datetime(projects['startDate'], errors='coerce')
projects['endDate'] = pd.to_datetime(projects['endDate'], errors='coerce')
projects['startYear'] = projects['startDate'].dt.year
projects['project_duration_days'] = (projects['endDate'] - projects['startDate']).dt.days
project_title_map = projects.set_index('id')['title'].to_dict()
project_funding_map = projects.set_index('id')['fundedAmount'].to_dict()
project_publications['citation_count'] = pd.to_numeric(project_publications['citation_count'], errors='coerce').fillna(0)

# === Streamlit Layout ===
st.set_page_config(page_title="OpenAIRE Dashboard", layout="wide")
st.title("OpenAIRE Research Project Dashboard (with 10.000 Projects)")

# === KPIs ===
col1, col2, col3 = st.columns(3)
col1.metric("Total Projects (up to 10k)", f"{len(projects):,}")
col2.metric("Earliest Year", int(projects['startYear'].min()) if not projects.empty else "-")
col3.metric("Latest Year", int(projects['startYear'].max()) if not projects.empty else "-")

st.markdown("---")

# === 1. Projects per Year ===
st.subheader("Number of Projects per Start Year")
projects_by_year = projects['startYear'].value_counts().sort_index()
fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.lineplot(x=projects_by_year.index, y=projects_by_year.values, marker='o', ax=ax1)
ax1.set_title('Projects per Year')
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Projects')
st.pyplot(fig1)
st.write(" Shows trends in research funding activity over time.")

# === 2. Average Funding per Year ===
st.subheader("Average Funding Amount per Year")
avg_funding_by_year = projects.groupby('startYear')['fundedAmount'].mean()
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.lineplot(x=avg_funding_by_year.index, y=avg_funding_by_year.values, marker='o', color='red', ax=ax2)
ax2.set_title('Average Funding Amount per Year')
ax2.set_xlabel('Year')
ax2.set_ylabel('€')
st.pyplot(fig2)
st.write("Reveals whether funding per project is increasing or decreasing over time.")


# === 3. Projects by Country ===
st.subheader("Projects by Country")
country_counts = project_countries['country'].value_counts().head(15)
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(x=country_counts.values, y=country_counts.index, color='skyblue', ax=ax3)
ax3.set_title('Top 15 Countries by Number of Projects')
ax3.set_xlabel('Projects')
ax3.set_ylabel('Country')
st.pyplot(fig3)
st.write("Highlights geographical distribution of research activity.")


# === 4. Top 10 Funders by Number of Projects ===
st.subheader("Top 10 Funders by Project Count")
funder_counts = project_funders['funder_name'].value_counts().head(10)
fig4, ax4 = plt.subplots(figsize=(8, 5))
sns.barplot(x=funder_counts.values, y=funder_counts.index, color='lightgreen', ax=ax4)
ax4.set_title('Top Funders by Project Count')
ax4.set_xlabel('Projects')
ax4.set_ylabel('Funder')
st.pyplot(fig4)
st.write("Identifies major funders in terms of volume.")


# === 5. Top 10 Funders by Total Funding ===
st.subheader("Top 10 Funders by Total Funding Amount")
merged = pd.merge(project_funders, projects[['id', 'fundedAmount']], left_on='project_id', right_on='id', how='left')
sum_by_funder = merged.groupby('funder_name')['fundedAmount'].sum().sort_values(ascending=False).head(10)
fig5, ax5 = plt.subplots(figsize=(8, 5))
sns.barplot(x=sum_by_funder.values, y=sum_by_funder.index, color='teal', ax=ax5)
ax5.set_title('Top Funders by Total Funding (€)')
ax5.set_xlabel('Total (€)')
ax5.set_ylabel('Funder')
st.pyplot(fig5)
st.write("Shows which funders provide the most total money.")

# === 6. Average Funding per Funder ===
st.subheader("Average Funding Amount per Funder")
avg_by_funder = merged.groupby('funder_name')['fundedAmount'].mean().sort_values(ascending=False).head(10)
fig6, ax6 = plt.subplots(figsize=(8, 5))
sns.barplot(x=avg_by_funder.values, y=avg_by_funder.index, color='steelblue', ax=ax6)
ax6.set_title('Top Funders by Average Funding (€)')
ax6.set_xlabel('Average (€)')
ax6.set_ylabel('Funder')
st.pyplot(fig6)
st.write("Highlights funders that give higher amounts per project.")


# === 7. Project Duration vs. Funding ===
st.subheader("Project Duration vs. Funding Amount")
valid_projects = projects[(projects['project_duration_days'] > 0) & (projects['fundedAmount'] > 0)]
fig7, ax7 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=valid_projects, x='project_duration_days', y='fundedAmount', alpha=0.5, ax=ax7)
ax7.set_title('Project Duration vs. Funding Amount')
ax7.set_xlabel('Duration (days)')
ax7.set_ylabel('Funding (€)')
st.pyplot(fig7)
st.write("Explore correlation between duration and funding.")


# === 8. Top Projects by Number of Publications ===
st.subheader("Top Projects by Number of Publications")
pub_counts = publication_project_rel['project_id'].value_counts().head(10)
top_pub_projects = pub_counts.reset_index()
top_pub_projects.columns = ['project_id', 'pub_count']
top_pub_projects['title'] = top_pub_projects['project_id'].map(project_title_map).fillna(top_pub_projects['project_id'])
fig8, ax8 = plt.subplots(figsize=(10, 6))
sns.barplot(x='pub_count', y='title', data=top_pub_projects, color='seagreen', ax=ax8)
ax8.set_title('Top Projects by Number of Publications')
ax8.set_xlabel('Publications')
ax8.set_ylabel('Project Title')
st.pyplot(fig8)
st.write("Shows productivity in terms of outputs.")

# === 9. Top Publications by Citation Count ===
st.subheader("Top Publications by Citation Count")
top_cited_pubs = project_publications.sort_values(by='citation_count', ascending=False).head(10)
fig9, ax9 = plt.subplots(figsize=(10, 6))
sns.barplot(x='citation_count', y='title', data=top_cited_pubs, color='darkred', ax=ax9)
ax9.set_title('Most Cited Publications')
ax9.set_xlabel('Citations')
ax9.set_ylabel('Publication Title')
st.pyplot(fig9)
st.write("Identifies the most influential published work.")

# === 10. Top Journals by Number of Publications ===
st.subheader("Top Journals by Number of Publications")
journal_counts = project_publications['journal'].value_counts().dropna().head(10)
fig10, ax10 = plt.subplots(figsize=(10, 6))
sns.barplot(x=journal_counts.values, y=journal_counts.index, color='orchid', ax=ax10)
ax10.set_title('Top Journals by Publication Count')
ax10.set_xlabel('Publications')
ax10.set_ylabel('Journal')
st.pyplot(fig10)
st.write("Highlights publishing venues used most frequently.")

# === 11. Distribution of Citation Counts ===
st.subheader("Distribution of Citation Counts")
fig11, ax11 = plt.subplots(figsize=(10, 6))
sns.histplot(project_publications['citation_count'], bins=30, kde=True, color='brown', ax=ax11)
ax11.set_title('Distribution of Citation Counts')
ax11.set_xlabel('Citations')
ax11.set_ylabel('Frequency')
st.pyplot(fig11)
st.write("Provides insight into how citations are distributed across publications.")

# === 12. Average Citation per Project ===
st.subheader("Top Projects by Average Citation Count")
merged_cit = pd.merge(publication_project_rel, project_publications, on='doi', how='left')
citation_avg = merged_cit.groupby('project_id')['citation_count'].mean().sort_values(ascending=False).head(10).reset_index()
citation_avg['title'] = citation_avg['project_id'].map(project_title_map).fillna(citation_avg['project_id'])
fig12, ax12 = plt.subplots(figsize=(10, 6))
sns.barplot(x='citation_count', y='title', data=citation_avg, color='darkgreen', ax=ax12)
ax12.set_title('Top Projects by Average Citation Count')
ax12.set_xlabel('Average Citations')
ax12.set_ylabel('Project Title')
st.pyplot(fig12)
st.write("Measures projects’ overall impact per output.")

st.markdown("---")
st.caption("Source: OpenAIRE. Built with Python and Streamlit.")
