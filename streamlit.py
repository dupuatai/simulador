import streamlit as st
import pandas as pd
import altair as alt

# --------------------------- Configuración inicial ---------------------------
st.set_page_config(page_title="Planificador de Horas de Vuelo", layout="wide")

st.title("🛫 Planificador de Horas de Vuelo")

# --------------------------- Widgets de configuración ---------------------------
with st.expander("🔧 Configuración de restricciones", expanded=True):
    HORAS_MAX_MES = st.number_input("Máximo de horas por mes", min_value=1, max_value=200, value=90)
    HORAS_MIN_MES = st.number_input("Mínimo de horas por mes", min_value=1, max_value=200, value=52)
    HORAS_MAX_ANUAL = st.number_input("Máximo de horas anuales", min_value=1, max_value=2000, value=1000)

# --------------------------- Datos base ---------------------------
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
MESES_ALTA_DEMANDA = ['Enero', 'Julio', 'Agosto', 'Diciembre']

df = pd.DataFrame({
    'Mes': MESES,
    'Horas asignadas ✏️': [HORAS_MAX_MES if mes in MESES_ALTA_DEMANDA else HORAS_MIN_MES for mes in MESES],
    'Mes alta demanda': [mes in MESES_ALTA_DEMANDA for mes in MESES],
})

# --------------------------- Edición interactiva ---------------------------
st.subheader("✏️ Horas asignadas por mes")

editable_cols = ['Horas asignadas ✏️', 'Mes alta demanda']

edited = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    disabled=[col for col in df.columns if col not in editable_cols],
    column_config={
        "Horas asignadas ✏️": st.column_config.NumberColumn(
            "Horas asignadas ✏️",
            min_value=HORAS_MIN_MES,
            max_value=HORAS_MAX_MES,
            step=1,
            format="%d"
        ),
        "Mes alta demanda": st.column_config.CheckboxColumn("Mes alta demanda"),
    }
)

# 🔄 Calcular automáticamente el promedio semanal
edited['Promedio semanal'] = edited['Horas asignadas ✏️'] / 4

# --------------------------- Validaciones ---------------------------
warnings = []

if any((edited['Horas asignadas ✏️'] < HORAS_MIN_MES) | (edited['Horas asignadas ✏️'] > HORAS_MAX_MES)):
    warnings.append(f"❌ Las horas asignadas deben estar entre {HORAS_MIN_MES} y {HORAS_MAX_MES} por mes.")

total_anual = edited['Horas asignadas ✏️'].sum()
if total_anual > HORAS_MAX_ANUAL:
    warnings.append(f"❌ Se excedieron las horas anuales permitidas: {total_anual} hrs (Máximo: {HORAS_MAX_ANUAL})")
elif total_anual < HORAS_MAX_ANUAL:
    restante = HORAS_MAX_ANUAL - total_anual
    warnings.append(f"⚠️ Has asignado {total_anual} horas, te quedan {restante} horas por asignar del total anual permitido ({HORAS_MAX_ANUAL} hrs).")
else:
    warnings.append("✅ ¡Has asignado exactamente el total de horas permitidas!")

semanales_conflicto = edited.loc[edited['Promedio semanal'] > 30, 'Mes'].tolist()
if semanales_conflicto:
    warnings.append(f"⚠️ Los siguientes meses superan 30 hrs semanales: {', '.join(semanales_conflicto)}")

# --------------------------- Mostrar advertencias ---------------------------
for warn in warnings:
    st.warning(warn)

# --------------------------- Tabla resumen ---------------------------
st.subheader("📊 Resumen de horas asignadas")
edited['Total anual'] = total_anual
st.dataframe(edited.drop(columns='Total anual'), use_container_width=True, hide_index=True)

# --------------------------- Gráfica de barras ---------------------------
color_scale = alt.condition(
    alt.datum["Mes alta demanda"],
    alt.value("#FF7F50"),
    alt.value("#1f77b4")
)

chart = alt.Chart(edited).mark_bar().encode(
    x=alt.X("Mes", sort=MESES),
    y="Horas asignadas ✏️",
    color=color_scale
).properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)
