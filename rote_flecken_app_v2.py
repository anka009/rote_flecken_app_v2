import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageSequence
from streamlit_drawable_canvas import st_canvas

# 📥 Upload-Abschnitt
uploaded_files = st.file_uploader(
    "📁 Lade mehrere Bilder hoch",
    type=["jpg", "jpeg", "png", "tif", "tiff"],
    accept_multiple_files=True
)

# 📏 DPI und Umrechnung
dpi = 300  # Beispielwert
pixels_per_mm = dpi / 25.4

# 🎛️ Farbsensitivität per Slider
st.sidebar.header("🎨 Farbempfindlichkeit einstellen")
h_min = st.sidebar.slider("Hue min", 0, 180, 0)
h_max = st.sidebar.slider("Hue max", 0, 180, 30)
s_min = st.sidebar.slider("Sättigung min", 0, 255, 70)
v_min = st.sidebar.slider("Helligkeit min", 0, 255, 50)

if uploaded_files:
    total_flecken = 0
    total_pixel_area = 0

# 🔄 Bildanalyse pro Datei
for uploaded_file in uploaded_files:
    st.header(f"🖼️ Datei: `{uploaded_file.name}`")

    # 📥 Versuch: Bild laden als Sequenz
    try:
        image_pil = Image.open(uploaded_file)
        frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]
    except:
        try:
            image_single = Image.open(uploaded_file).convert("RGB")
            frames = [image_single]
        except:
            frames = []

    # ❌ Ungültige Datei überspringen
    if not frames:
        st.error("❌ Dieses Bild konnte nicht verarbeitet werden.")
        continue

    # 🧮 Initialisiere Summen
    total_flecken = 0
    total_pixel_area = 0

    # 🔄 Analyse pro Frame
    for i, frame in enumerate(frames):
        if len(frames) > 1:
            st.subheader(f"📄 Seite {i+1}")

        # 🖼️ Frame konvertieren
        image_np = np.array(frame)
        hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

        # 🎚️ Farbgrenzen aus Slider
        lower_dynamic = np.array([h_min, s_min, v_min])
        upper_dynamic = np.array([h_max, 255, 255])
        mask = cv2.inRange(hsv, lower_dynamic, upper_dynamic)

        # 🧹 Maske bereinigen
        kernel = np.ones((5, 5), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 🔍 Konturen erkennen
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 50
        filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        # 📊 Analyse-Ergebnisse
        fleckenzahl = len(filtered)
        fläche_pixel = sum(cv2.contourArea(cnt) for cnt in filtered)
        fläche_mm2 = fläche_pixel / (pixels_per_mm ** 2)

        st.success(f"🔴 Flecken gefunden: {fleckenzahl}")
        st.info(f"📐 Fläche: {fläche_pixel:.2f} Pixel² ({fläche_mm2:.2f} mm²)")

        # 📷 Bild mit Konturen anzeigen
        output = image_np.copy()
        cv2.drawContours(output, filtered, -1, (0, 255, 0), 2)
        st.image(output, caption="Markierte Flecken", channels="RGB")

        # 🖍️ Canvas zur manuellen Markierung
        st.subheader("🖍️ Manuelle Fleckenmarkierung")

from PIL import Image

# 🔁 Schleife über alle hochgeladenen Dateien
for i, uploaded_file in enumerate(uploaded_files):
    st.header(f"🖼️ Datei: `{uploaded_file.name}`")

    try:
        image_pil = Image.open(uploaded_file)
        frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]
        image_np = np.array(frames[0])
        pil_image = Image.fromarray(image_np)

        # 🖌️ Zeichenbereich
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=2,
            background_image=pil_image,
            update_streamlit=True,
            height=pil_image.height,
            width=pil_image.width,
            drawing_mode="rect",
            key=f"canvas_{i}"
        )

        # 🧮 Beispielhafte Auswertung (optional)
        if canvas_result.json_data is not None:
            st.write("📌 Anzahl Zeichnungen:", len(canvas_result.json_data["objects"]))

    except Exception as e:
        st.error(f"❌ Fehler beim Verarbeiten der Datei `{uploaded_file.name}`: {e}")


if canvas_result.json_data and "objects" in canvas_result.
            st.markdown("🎯 Manuell markierte Flecken:")
            for obj in canvas_result.json_data["objects"]:
                x = obj["left"]
                y = obj["top"]
                w = obj["width"]
                h = obj["height"]
                st.write(f"🟥 Rechteck: x={x}, y={y}, Breite={w}, Höhe={h}")

        # 📦 Summen aktualisieren
        total_flecken += fleckenzahl
        total_pixel_area += fläche_pixel

