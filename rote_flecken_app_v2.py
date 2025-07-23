import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageSequence

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

    for uploaded_file in uploaded_files:
        st.header(f"🖼️ Datei: `{uploaded_file.name}`")

        # 🧪 Versuch: Bild laden als Sequenz
        try:
            image_pil = Image.open(uploaded_file)
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]
        except:
            try:
                image_single = Image.open(uploaded_file).convert("RGB")
                frames = [image_single]
            except:
                frames = []

        # ❌ Kein gültiges Bild gefunden
        if not frames:
            st.error("❌ Bild konnte nicht verarbeitet werden.")
            continue

        # 🔄 Bildanalyse pro Frame
        for i, frame in enumerate(frames):
            if len(frames) > 1:
                st.subheader(f"📄 Seite {i+1}")

            image_np = np.array(frame)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

            # 🎨 Farbdefinition: Rot + Braun
            # 🔧 Dynamischer HSV-Farbbereich
            lower_dynamic = np.array([h_min, s_min, v_min])
            upper_dynamic = np.array([h_max, 255, 255])
            mask = cv2.inRange(hsv, lower_dynamic, upper_dynamic)

        # 🎨 Farbkonvertierung zu HSV
hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

# 🎚️ Dynamischer HSV-Bereich aus Slidern
lower_dynamic = np.array([h_min, s_min, v_min])
upper_dynamic = np.array([h_max, 255, 255])

# 🧪 Maske auf Basis des gewählten Farbbereichs
mask = cv2.inRange(hsv, lower_dynamic, upper_dynamic)

# 🧹 Maske säubern
kernel = np.ones((5, 5), np.uint8)
mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# 🔍 Konturen finden & filtern
contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
min_area = 50
filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

# 📐 Fleckenberechnung
fleckenzahl = len(filtered)
fläche_pixel = sum(cv2.contourArea(cnt) for cnt in filtered)
fläche_mm2 = fläche_pixel / (pixels_per_mm ** 2)

# 📢 Ergebnisse anzeigen
st.success(f"🔴 Flecken gefunden: {fleckenzahl}")
st.info(f"📐 Fläche: {fläche_pixel:.2f} Pixel² ({fläche_mm2:.2f} mm²)")
