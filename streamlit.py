import streamlit as st
import pandas as pd

st.title('🛫 Simulador Interactivo de Horas de Vuelo')

# Definición de restricciones
MESES_ALTO_USO = ['Enero', 'Julio', 'Agosto', 'Diciembre']
HORAS_MAX_MES = 90
HORAS_MIN_MES = 52
HORAS_MAX_ANUAL = 1000

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Inicializar DataFrame
datos = pd.DataFrame({
    'Mes': meses,
    'Mínimo': [HORAS_MIN_MES]*12,
    'Máximo': [HORAS_MAX_MES]*12,
    'Asignadas': [HORAS_MAX_MES if mes in MESES_ALTO_USO else HORAS_MIN_MES for mes in meses]
})

st.subheader("🔧 Ajuste manual de horas por mes")
total_asignado = 0

# Crear sliders interactivos por mes
for idx, mes in enumerate(datos['Mes']):
    asignado = st.slider(
        f"Horas asignadas - {mes}",
        min_value=int(datos.loc[idx, 'Mínimo']),
        max_value=int(datos.loc[idx, 'Máximo']),
        value=int(datos.loc[idx, 'Asignadas'])
    )
    datos.at[idx, 'Asignadas'] = asignado

# Calcular promedio semanal
datos['Promedio semanal'] = datos['Asignadas'] / 4

# Verificar restricciones anuales
total_asignado = datos['Asignadas'].sum()

st.markdown("---")
st.subheader("📈 Resumen de horas asignadas")
st.dataframe(datos.set_index('Mes'))

# Gráfica visual de horas asignadas
st.bar_chart(datos.set_index('Mes')['Asignadas'])

# Validaciones
if total_asignado > HORAS_MAX_ANUAL:
    st.error(f"❌ Se excedieron las horas anuales ({total_asignado} hrs). Máximo permitido: {HORAS_MAX_ANUAL} hrs.")
elif total_asignado < HORAS_MAX_ANUAL:
    restante = HORAS_MAX_ANUAL - total_asignado
    st.warning(f"⚠️ Quedan {restante} horas disponibles del límite anual ({HORAS_MAX_ANUAL} hrs).")
else:
    st.success("✅ ¡Has asignado exactamente el límite anual de 1000 horas!")

# Control estricto promedio semanal
if any(datos['Promedio semanal'] > 30):
    meses_conflicto = datos.loc[datos['Promedio semanal'] > 30, 'Mes'].tolist()
    st.warning(f"⚠️ Meses que superan el promedio semanal recomendado (30 hrs/sem): {', '.join(meses_conflicto)}. Revisa la asignación.")

# Nota adicional sobre restricción semanal (informativa)
st.info("💡 Recuerda que semanalmente no debes superar las 30 horas por piloto. Considera esta restricción al planificar vuelos específicos.")
