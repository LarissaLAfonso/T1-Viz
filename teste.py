import numpy as np
import pandas as pd
import altair as alt

# Remove Altair row limit
alt.data_transformers.disable_max_rows()

file_path = "homicidios.csv"
df = pd.read_csv(file_path)

# Fill missing values
df["Regiao"] = df["Regiao"].fillna("Desconhecido").astype(str)
df["Mes"] = df["Mes"].fillna("Desconhecido").astype(str)

# Compute homicide rate per 1000 inhabitants
df["taxa_homicidios_1000"] = (df["Total Crimes"] / df["populacao"]) * 1000
df["taxa_homicidios_1000"] = pd.to_numeric(df["taxa_homicidios_1000"], errors="coerce").fillna(0)

# Log transformation for better visualization
df["log_taxa_homicidios"] = np.log1p(df["taxa_homicidios_1000"])  
df["Ano Agrupado"] = (df["Ano"] // 2) * 2

# Filter only even years
df_even_years = df[df["Ano"] % 2 == 0]
even_years = sorted(df_even_years["Ano"].unique())

# Create heatmaps for each even year
heatmaps = []
for i, year in enumerate(even_years):
    chart = alt.Chart(df[df["Ano Agrupado"] == year]).mark_rect().encode(
        x=alt.X("Mes:N", title=None, sort=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
                axis=alt.Axis(labelFont="Arial", labelFontSize=15)),  # X-axis labels size 15
        y=alt.Y("Regiao:N", title="Região" if i == 0 else None, 
                axis=alt.Axis(labels=(i == 0), ticks=False, labelFont="Arial", labelFontSize=18, 
                              titleFont="Arial", titleFontSize=18, labelAngle=-30, labelLimit=0)),  # Rotate Y labels & prevent truncation
        color=alt.Color("log_taxa_homicidios:Q", 
                        scale=alt.Scale(scheme="turbo"), 
                        title="Log Homicídios\npor 1.000 hab.",  # Manually breaking title into multiple lines
                        legend=alt.Legend(labelFont="Arial", labelFontSize=18, titleFont="Arial", titleFontSize=18, 
                                          titleLimit=500, labelLimit=500, direction="vertical", orient="right")),  # Fix truncation
        tooltip=[
            alt.Tooltip("Regiao:N", title="Região"),
            alt.Tooltip("Mes:N", title="Mês"),
            alt.Tooltip("taxa_homicidios_1000:Q", title="Homicídios por 1k hab.", format=".2f"),  # Ensure format is set
            alt.Tooltip("log_taxa_homicidios:Q", title="Log(Homicídios)", format=".2f")  # Fixed missing format issue
        ]
    ).properties(
        width=160,  # Increased width to prevent Y-label truncation
        height=800,
        title=alt.TitleParams(f"{year}-{year+1}", font="Arial", fontSize=14, anchor="middle")
    )
    
    heatmaps.append(chart)

# Concatenate heatmaps and share color scale
final_chart = alt.hconcat(*heatmaps).resolve_scale(color="shared").properties(
    title=alt.TitleParams(
        "Série Histórica dos Homicídios no Estado de São Paulo", 
        font="Arial", fontSize=18, anchor="middle", dy=-30  # Increase space between title & heatmaps
    )
)

# Save HTML
final_chart.save("heatmap_teste.html")
