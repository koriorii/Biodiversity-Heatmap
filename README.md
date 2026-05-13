# 🌍 Visualizador de Avistamientos de Biodiversidad

Una aplicación web interactiva que genera **mapas de calor** a partir de datos de avistamiento de especies con coordenadas geográficas.

Desarrollada con Python, Streamlit y Plotly. Diseñada para datos del [GBIF (Global Biodiversity Information Facility)](https://www.gbif.org/), pero funciona con cualquier CSV que tenga columnas de latitud y longitud.

---

## ✨ Funcionalidades

- 🔥 **Mapa de calor de densidad** — visualiza zonas de alta concentración de avistamientos
- 🌍 **Globo interactivo** — rota, acerca y aleja el mapa
- 🦅 **Filtro por especie** — selecciona una especie específica o visualiza todas
- ☀️🌙 **Modo claro / oscuro**
- 📊 **Métricas automáticas** — total de registros, especies únicas, rango de coordenadas
- 🔎 **Vista previa de datos** — inspecciona los registros filtrados directamente en la app

---

## 🚀 Demo

> *Próximamente: link a Streamlit Cloud*

---

## 📂 Estructura del repositorio

```
biodiversity-heatmap/
│
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── data/
│   └── mimidae.csv     # Dataset de ejemplo (familia Mimidae — sinsontes)
└── README.md
```

---

## 🛠️ Instalación local

### 1. Clona el repositorio
```bash
git clone https://github.com/tu-usuario/biodiversity-heatmap.git
cd biodiversity-heatmap
```

### 2. Crea un entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

### 3. Instala dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecuta la app
```bash
streamlit run app.py
```

La app abre automáticamente en `http://localhost:8501`

---

## 📋 Formato del CSV

El archivo debe tener al menos dos columnas de coordenadas. Los nombres estándar del GBIF son detectados automáticamente:

| Columna              | Descripción                    | Requerida |
|----------------------|-------------------------------|-----------|
| `decimalLatitude`    | Latitud decimal                | ✅ Sí     |
| `decimalLongitude`   | Longitud decimal               | ✅ Sí     |
| `species`            | Nombre de la especie           | ❌ Opcional |

Si tu CSV usa otros nombres de columna, la app intentará usar las dos primeras columnas numéricas.

### Ejemplo mínimo
```csv
decimalLatitude,decimalLongitude,species
4.711,-74.072,Mimus gilvus
6.244,-75.591,Mimus gilvus
-0.229,-78.526,Mimus longicaudatus
```

---

## 🧪 Dataset de ejemplo

El repositorio incluye un dataset de la familia **Mimidae** (sinsontes y cuclillos americanos) descargado de GBIF. Puedes usarlo directamente para probar la app.

Fuente: [GBIF.org](https://www.gbif.org) — licencia CC BY 4.0

Cita: GBIF.org (12 May 2026) GBIF Occurrence Download https://doi.org/10.15468/dl.26g7nh

---

## 🧰 Tecnologías

| Librería     | Uso                                      |
|--------------|------------------------------------------|
| `streamlit`  | Interfaz web interactiva                 |
| `plotly`     | Mapa de calor y globo interactivo        |
| `pandas`     | Carga y limpieza de datos                |

---

## 👩‍💻 Autora

**Juliana Cavicchioli Moyano**  
Ingeniería en Multimedia — Universidad Militar Nueva Granada  
[LinkedIn](https://www.linkedin.com/in/juliana-cavicchioli-moyano-a29558226) · [GitHub](https://github.com/juliana-cavicchioli)

---

## 📄 Licencia

MIT — libre de usar, modificar y distribuir con atribución.
