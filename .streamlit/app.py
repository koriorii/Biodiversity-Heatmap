import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Visualizador de Biodiversidad",
    page_icon="🌍",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Cabecera ───────────────────────────────────────────────────────────────────
st.title("🌍 Visualizador de Avistamientos de Biodiversidad")
st.markdown("Sube un CSV con coordenadas geográficas y explora la densidad de avistamientos en el globo.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controles")
    uploaded_file = st.file_uploader("📂 Cargar CSV", type=["csv", "txt"])
    st.divider()
    st.markdown("**Columnas esperadas**")
    st.code("decimalLatitude\ndecimalLongitude\nspecies (opcional)")
    st.caption("Funciona con cualquier CSV que tenga coordenadas.")

# ── Carga y limpieza de datos ──────────────────────────────────────────────────
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_csv(
        archivo,
        sep=None,
        engine="python",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )
    df.columns = df.columns.str.strip()

    col_lat = "decimalLatitude"  if "decimalLatitude"  in df.columns else df.columns[0]
    col_lon = "decimalLongitude" if "decimalLongitude" in df.columns else df.columns[1]
    col_sp  = "species" if "species" in df.columns else None

    df[col_lat] = pd.to_numeric(df[col_lat], errors="coerce")
    df[col_lon] = pd.to_numeric(df[col_lon], errors="coerce")
    df = df.dropna(subset=[col_lat, col_lon]).copy()

    if col_sp:
        df[col_sp] = df[col_sp].astype(str).replace("nan", "No identificado")

    return df, col_lat, col_lon, col_sp

# ── Densidad por celdas ────────────────────────────────────────────────────────
@st.cache_data
def calcular_densidad(lats, lons, resolucion=3.0):
    df = pd.DataFrame({"lat": lats, "lon": lons})
    df["_lat_bin"] = (df["lat"] // resolucion) * resolucion + resolucion / 2
    df["_lon_bin"] = (df["lon"] // resolucion) * resolucion + resolucion / 2
    conteo = df.groupby(["_lat_bin", "_lon_bin"]).size().reset_index(name="count")
    conteo["densidad"] = conteo["count"] / conteo["count"].max()
    return conteo

# ── Construir figura Plotly ────────────────────────────────────────────────────
def construir_figura(df, col_lat, col_lon, col_sp, especie):
    if especie != "Todas" and col_sp:
        df_vis = df[df[col_sp] == especie].copy()
    else:
        df_vis = df.copy()

    densidad = calcular_densidad(
        tuple(df_vis[col_lat].tolist()),
        tuple(df_vis[col_lon].tolist())
    )

    df_puntos = df_vis.sample(n=min(5_000, len(df_vis)), random_state=42)
    hover_text = df_puntos[col_sp].tolist() if col_sp else ["Avistamiento"] * len(df_puntos)

    fig = go.Figure()

    # Capa 1 — burbujas de densidad
    fig.add_trace(go.Scattergeo(
        lat=densidad["_lat_bin"],
        lon=densidad["_lon_bin"],
        mode="markers",
        marker=dict(
            size=densidad["densidad"] * 30 + 3,
            color=densidad["densidad"],
            colorscale="YlOrRd",
            cmin=0, cmax=1,
            opacity=0.65,
            colorbar=dict(
                title="Densidad<br>relativa",
                tickfont=dict(color="white"),
                x=1.02,
                thickness=14,
            ),
            line=dict(width=0),
        ),
        hovertemplate="Lat: %{lat:.1f}° Lon: %{lon:.1f}°<br>Registros: %{customdata}<extra></extra>",
        customdata=densidad["count"],
        name="Densidad",
        showlegend=False,
    ))

    # Capa 2 — puntos individuales finos
    fig.add_trace(go.Scattergeo(
        lat=df_puntos[col_lat],
        lon=df_puntos[col_lon],
        mode="markers",
        marker=dict(size=2, color="#ff4b4b", opacity=0.25, line=dict(width=0)),
        hovertext=hover_text,
        hovertemplate="<b>%{hovertext}</b><br>%{lat:.3f}°, %{lon:.3f}°<extra></extra>",
        name="Avistamientos",
        showlegend=False,
    ))

    fig.update_layout(
        height=680,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="#0d1117",
        title=dict(
            text=f"🌍 Densidad de avistamientos — {especie}  ({len(df_vis):,} registros)",
            font=dict(color="white", size=17),
            x=0.5, xanchor="center", y=0.98,
        ),
        geo=dict(
            projection_type="orthographic",
            showland=True,      landcolor="#1c2b1e",
            showocean=True,     oceancolor="#000814",
            showlakes=True,     lakecolor="#000814",
            showcountries=True, countrycolor="#3a4a3a",
            showsubunits=True,  subunitcolor="#3a4a3a",
            bgcolor="#0d1117",
            resolution=110,
            lataxis=dict(showgrid=True, gridcolor="#2a3a2a", gridwidth=0.5),
            lonaxis=dict(showgrid=True, gridcolor="#2a3a2a", gridwidth=0.5),
        ),
        
        dragmode="pan",
        
        uirevision="globo-fijo",
    )

    return fig, df_vis

# ── JavaScript: botón de tema flotante, sin recargar Streamlit ────────────────
# Usa Plotly.relayout() en el cliente para cambiar colores directamente
# en el canvas ya renderizado — sin tocar Python.
TEMA_JS = """
<script>
(function() {
    const TEMAS = {
        dark: {
            paper:  "#0d1117",
            tierra: "#1c2b1e",
            oceano: "#000814",
            paises: "#3a4a3a",
            grid:   "#2a3a2a",
            txt:    "white",
            btnTxt: "☀️ Modo claro"
        },
        light: {
            paper:  "#f0f4f8",
            tierra: "#c8ddb0",
            oceano: "#a8d0e6",
            paises: "#888888",
            grid:   "#aaaaaa",
            txt:    "#111111",
            btnTxt: "🌙 Modo oscuro"
        }
    };

    let temaActual = "dark";

    function aplicarTema(tema) {
        const t = TEMAS[tema];

        // Buscar todos los divs de Plotly en la página (puede haber uno en iframe)
        const raiz = window.parent.document;
        const divs = raiz.querySelectorAll(".js-plotly-plot");

        divs.forEach(div => {
            window.parent.Plotly.relayout(div, {
                paper_bgcolor:            t.paper,
                "title.font.color":       t.txt,
                "geo.landcolor":          t.tierra,
                "geo.oceancolor":         t.oceano,
                "geo.lakecolor":          t.oceano,
                "geo.bgcolor":            t.paper,
                "geo.countrycolor":       t.paises,
                "geo.subunitcolor":       t.paises,
                "geo.lataxis.gridcolor":  t.grid,
                "geo.lonaxis.gridcolor":  t.grid,
            });
        });

        const btn = document.getElementById("btn-tema");
        if (btn) btn.textContent = t.btnTxt;
        temaActual = tema;
    }

    function crearBoton() {
        // El botón vive en el documento padre (fuera del iframe de Streamlit)
        const doc = window.parent.document;
        if (doc.getElementById("btn-tema")) return;

        const btn = doc.createElement("button");
        btn.id = "btn-tema";
        btn.textContent = "☀️ Modo claro";
        btn.style.cssText = `
            position: fixed;
            top: 68px;
            right: 22px;
            z-index: 99999;
            padding: 8px 18px;
            border-radius: 20px;
            border: none;
            background: #2E86C1;
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
            transition: background 0.15s;
        `;
        btn.onmouseenter = () => { btn.style.background = "#1A5276"; };
        btn.onmouseleave = () => { btn.style.background = "#2E86C1"; };
        btn.onclick = () => {
            const nuevo = temaActual === "dark" ? "light" : "dark";
            aplicarTema(nuevo);
        };
        doc.body.appendChild(btn);
    }

    // Esperar a que Plotly esté cargado y el gráfico renderizado
    function init() {
        crearBoton();
    }

    // Pequeño delay para asegurar que el DOM del padre está listo
    setTimeout(init, 800);
})();
</script>
"""

# ── Lógica principal ───────────────────────────────────────────────────────────
if uploaded_file is not None:
    try:
        df, col_lat, col_lon, col_sp = cargar_datos(uploaded_file)

        with st.sidebar:
            st.divider()
            st.markdown("**🔍 Filtrar**")
            if col_sp:
                especies = ["Todas"] + sorted(df[col_sp].dropna().unique().tolist())
                especie_sel = st.selectbox("Especie", especies)
            else:
                especie_sel = "Todas"

        # Métricas
        col1, col2, col3 = st.columns(3)
        col1.metric("📍 Registros totales", f"{len(df):,}")
        col2.metric(
            "🦅 Especies únicas",
            f"{df[col_sp].nunique():,}" if col_sp else "—"
        )
        col3.metric(
            "🗺️ Rango de latitud",
            f"{df[col_lat].min():.1f}° a {df[col_lat].max():.1f}°"
        )

        # Figura
        fig, df_filtrado = construir_figura(df, col_lat, col_lon, col_sp, especie_sel)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": True,
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "responsive": True,
            }
        )

        # Inyectar JS del botón flotante de tema
        st.components.v1.html(TEMA_JS, height=0)

        with st.expander("🔎 Vista previa de datos filtrados"):
            st.dataframe(df_filtrado.head(200), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
        st.info("Verifica que el CSV tenga columnas de latitud y longitud válidas.")

else:
    st.info("👈 Carga un archivo CSV desde el panel lateral para comenzar.")
    st.markdown("[📄 Acá tienes un ejemplo de CSV sobre las aves Mimidae para probar el mapa](https://github.com/koriorii/Biodiversity-Heatmap/blob/24f431f68c4e5979f9c74936919923d014af3f7c/CSV_for_Testing.zip)")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### ¿Qué puede hacer esta app?")
        st.markdown("""
- 🔥 Mapa de calor de densidad sobre globo terráqueo
- 🌍 Globo interactivo — **arrastra para rotar**
- 🦅 Filtrar por especie
- ☀️🌙 Tema claro/oscuro **sin recargar el mapa**
- 📊 Métricas y vista previa de datos
        """)
    with col_b:
        st.markdown("#### Formato del CSV")
        ejemplo = pd.DataFrame({
            "decimalLatitude":  [4.711, 6.244, -0.229],
            "decimalLongitude": [-74.072, -75.591, -78.526],
            "species":          ["Mimus gilvus", "Mimus gilvus", "Mimus longicaudatus"]
        })
        st.dataframe(ejemplo, use_container_width=True)
