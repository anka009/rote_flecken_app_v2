import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageSequence
from streamlit_drawable_canvas import st_canvas

# 📁 Datei-Upload
uploaded_files = st.file_uploader("📂 Lade mehrere Bilder hoch", type=["jpg", "jpeg", "png", "tif", "tiff"], accept_multiple_files=True)

# 🎛️ Farb-Slider
st.sidebar.header("🎨 Farbempfindlichkeit einstellen")
h_min = st.sidebar.slider("Hue min", 0, 180, 0)
h_max = st.sidebar.slider("Hue max", 0, 180, 30)
s_min = st.sidebar.slider("Sättigung min", 0, 255, 70)
v_min = st.sidebar.slider("Helligkeit min", 0, 255, 50)

# 🔢 Initialisierung der Summen
total_flecken = 0
total_pixel_area = 0

# 🔁 Schleife über alle Dateien
if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        st.header(f"🖼️ Datei: `{uploaded_file.name}`")

        try:
            # 🎞️ Bild öffnen (Sequenz oder Einzelbild)
            image_pil = Image.open(uploaded_file)
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]

        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei `{uploaded_file.name}`: {e}")
            continue

        if not frames:
            st.error("⚠️ Keine verarbeitbaren Frames gefunden.")
            continue

        # 📊 Analyse pro Frame
        for j, frame in enumerate(frames):
            if len(frames) > 1:
                st.subheader(f"📄 Seite {j + 1}")

            image_np = np.array(frame)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

            # 🎯 Farbbereich filtern
            lower_bound = np.array([h_min, s_min, v_min])
            upper_bound = np.array([h_max, 255, 255])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # 🧱 Konturen extrahieren
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            fleckenzahl = len(contours)
            fläche_pixel = sum(cv2.contourArea(c) for c in contours)

            total_flecken += fleckenzahl
            total_pixel_area += fläche_pixel

            st.write(f"🔴 Automatisch erkannte Flecken: {fleckenzahl}")
            st.write(f"🧮 Fläche in Pixeln: {fläche_pixel:.2f}")

            # 🖌️ Canvas für manuelle Markierungen
            pil_image = Image.fromarray(image_np)
            canvas_result = st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=2,
                background_image=pil_image,
                update_streamlit=True,
                height=pil_image.height,
                width=pil_image.width,
                drawing_mode="rect",
                key=f"canvas_{i}_{j}"
            )

            if canvas_result and canvas_result.json_data and "objects" in canvas_result.json_data:
                st.markdown("🎯 Manuell markierte Flecken:")
                for obj in canvas_result.json_data["objects"]:
                    x = obj["left"]
                    y = obj["top"]
                    w = obj["width"]
                    h = obj["height"]
                    st.write(f"🟥 Rechteck: x={x}, y={y}, Breite={w}, Höhe={h}")

        st.markdown("---")

    # 🧾 Gesamtergebnisse
    st.success(f"✅ Gesamte Fleckenanzahl: {total_flecken}")
    st.info(f"📐 Gesamtfläche (Pixel): {total_pixel_area:.2f}")
    fläche_mm2 = total_pixel_area / ((300 / 25.4) ** 2)  # DPI als Umrechnungsbasis
    st.info(f"📏 Geschätzte Fläche in mm2: {fläche_mm2:.2f}")
