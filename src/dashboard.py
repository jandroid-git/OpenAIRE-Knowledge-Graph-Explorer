import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Daten laden
projects = pd.read_csv('data/projects_data_csv/projects.csv')
project_funders = pd.read_csv('data/projects_data_csv/project_funder_rel.csv')
project_countries = pd.read_csv('data/projects_data_csv/project_country_rel.csv')

# Vorbereitung
projects['startDate'] = pd.to_datetime(projects['startDate'], errors='coerce')
projects['endDate'] = pd.to_datetime(projects['endDate'], errors='coerce')
projects['startYear'] = projects['startDate'].dt.year
projects['project_duration_days'] = (projects['endDate'] - projects['startDate']).dt.days

# Dashboard 
st.set_page_config(page_title="OpenAIRE Dashboard", layout="wide")
st.title("OpenAIRE Forschungsprojekt-Dashboard")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Projekte insgesamt", f"{len(projects):,}")
col2.metric("Frühestes Jahr", int(projects['startYear'].min()) if not projects.empty else "-")
col3.metric("Letztes Jahr", int(projects['startYear'].max()) if not projects.empty else "-")

st.markdown("---")

# 1. Anzahl Projekte pro Jahr
st.subheader("Anzahl der Projekte nach Startjahr")
projects_by_year = projects['startYear'].value_counts().sort_index()
fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.lineplot(x=projects_by_year.index, y=projects_by_year.values, marker='o', ax=ax1)
ax1.set_title('Projekte pro Jahr')
ax1.set_xlabel('Jahr')
ax1.set_ylabel('Anzahl')
st.pyplot(fig1)

# 2. Durchschnittlicher Förderbetrag pro Jahr
st.subheader("Durchschnittlicher Förderbetrag pro Jahr")
avg_funding_by_year = projects.groupby('startYear')['fundedAmount'].mean()
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.lineplot(x=avg_funding_by_year.index, y=avg_funding_by_year.values, marker='o', color='red', ax=ax2)
ax2.set_title('Durchschnittlicher Förderbetrag pro Jahr')
ax2.set_xlabel('Jahr')
ax2.set_ylabel('€')
st.pyplot(fig2)

# 3. Projekte nach Land
st.subheader("Projekte nach Land")
country_counts = project_countries['country'].value_counts().head(15)
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(x=country_counts.values, y=country_counts.index, color='skyblue', ax=ax3)
ax3.set_title('Projekte pro Land (Top 15)')
ax3.set_xlabel('Anzahl')
ax3.set_ylabel('Land')
st.pyplot(fig3)

# 4. Top 10 Förderer nach Anzahl Projekte
st.subheader("Top 10 Förderer nach Anzahl Projekte")
funder_counts = project_funders['funder_name'].value_counts().head(10)
fig4, ax4 = plt.subplots(figsize=(8, 5))
sns.barplot(x=funder_counts.values, y=funder_counts.index, color='lightgreen', ax=ax4)
ax4.set_title('Top Förderer nach Anzahl Projekte')
ax4.set_xlabel('Anzahl')
ax4.set_ylabel('Förderer')
st.pyplot(fig4)

# 5. Top 10 Förderer nach Fördersumme
st.subheader("Top 10 Förderer nach Fördersumme")
merged = pd.merge(project_funders, projects[['id', 'fundedAmount']], left_on='project_id', right_on='id', how='left')
sum_by_funder = merged.groupby('funder_name')['fundedAmount'].sum().sort_values(ascending=False).head(10)
fig5, ax5 = plt.subplots(figsize=(8, 5))
sns.barplot(x=sum_by_funder.values, y=sum_by_funder.index, color='teal', ax=ax5)
ax5.set_title('Förderer nach Fördersumme (Top 10)')
ax5.set_xlabel('Fördersumme (€)')
ax5.set_ylabel('Förderer')
st.pyplot(fig5)

# 6. Durchschnittlicher Förderbetrag pro Förderer
st.subheader("Durchschnittlicher Förderbetrag pro Förderer")
avg_by_funder = merged.groupby('funder_name')['fundedAmount'].mean().sort_values(ascending=False).head(10)
fig6, ax6 = plt.subplots(figsize=(8, 5))
sns.barplot(x=avg_by_funder.values, y=avg_by_funder.index, color='steelblue', ax=ax6)
ax6.set_title('Ø Förderbetrag pro Förderer (Top 10)')
ax6.set_xlabel('Durchschnitt (€)')
ax6.set_ylabel('Förderer')
st.pyplot(fig6)

# 7. Projektdauer vs. Förderbetrag 
st.subheader("Projektdauer vs. Förderbetrag")
valid_projects = projects[(projects['project_duration_days'] > 0) & (projects['fundedAmount'] > 0)]
fig7, ax7 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=valid_projects, x='project_duration_days', y='fundedAmount', alpha=0.5, ax=ax7)
ax7.set_title('Zusammenhang Projektdauer und Förderbetrag')
ax7.set_xlabel('Dauer (Tage)')
ax7.set_ylabel('Förderbetrag (€)')
st.pyplot(fig7)

st.markdown("---")
st.caption("Datenquelle: OpenAIRE. Erstellt in Python und Streamlit.")
