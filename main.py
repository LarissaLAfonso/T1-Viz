import altair as alt
import pandas as pd
import numpy as np

# Carregar o arquivo homicidios.csv
file_path = "homicidios.csv"
df = pd.read_csv(file_path)

# Ensure the dataset is correctly formatted
df["taxa_homicidios_1000"] = (df["Total Crimes"] / df["populacao"]) * 1000
df["taxa_homicidios_1000"] = pd.to_numeric(df["taxa_homicidios_1000"], errors="coerce").fillna(0)

# Apply log transformation to the homicide rate to enhance color differentiation
df["log_taxa_homicidios"] = np.log1p(df["taxa_homicidios_1000"])  # log(1 + x) to avoid log(0)
df["Ano Agrupado"] = (df["Ano"] // 2) * 2

df_even_years = df[df["Ano"] % 2 == 0]

heatmaps = []
even_years = sorted(df_even_years["Ano"].unique())

for i, year in enumerate(even_years):
    chart = alt.Chart(df[df["Ano"] == year]).mark_rect().encode(
        x=alt.X("Mes:N", title=None, sort=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]),  # No "Mês" label
        y=alt.Y("Regiao:N", title="Região" if i == 0 else None, axis=alt.Axis(labels=(i == 0))),  # Only first chart has "Região" label and tick labels
        color=alt.Color("taxa_homicidios_1000:Q", scale=alt.Scale(scheme="turbo"), title="Logaritmo de\nhomicídios a cada\n1000 habitantes"),
        tooltip=["Regiao", "Mes", "taxa_homicidios_1000"]
    ).properties(
        width=150,
        height=400,
        title=f"{year}"
    )
    
    heatmaps.append(chart)

# Concatenate heatmaps horizontally
final_chart = alt.hconcat(*heatmaps).resolve_scale(color="shared").properties(
    title="Série Histórica dos Homicídios no Estado de São Paulo"  
)

# Exibir o gráfico
final_chart.save("heatmap_homicidios.html")
