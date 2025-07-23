import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageSequence

# 📂 Upload
uploaded_files = st.file_uploader("📂 Lade mehrere Bilder hoch", type=["jpg", "jpeg", "png", "tif", "tiff"], accept_multiple_files=True)

# 🎛️ Farbfilter in Sidebar
st.sidebar.header("🎨 Farbempfindlichkeit einstellen")
h_min = st.sidebar.slider("Hue min", 0, 180, 0)
h_max = st.sidebar.slider("Hue max", 0, 180, 30)
s_min = st.sidebar.slider("Sättigung min", 0, 255, 70)
v_min = st.sidebar.slider("Helligkeit min", 0, 255, 50)

# 🧮 Initialisierung
total_flecken = 0
total_pixel_area = 0
analyse_ergebnisse = []

# 🔁 Analyse der Bilder
if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        st.header(f"🖼️ Datei: `{uploaded_file.name}`")
        try:
            image_pil = Image.open(uploaded_file)
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]
        except Exception as e:
            st.error(f"❌ Fehler beim Laden von `{uploaded_file.name}`: {e}")
            continue

        for j, frame in enumerate(frames):
            if len(frames) > 1:
                st.subheader(f"📄 Seite {j + 1}")

            image_np = np.array(frame)
            st.image(image_np, caption="Originalbild", use_container_width=True)

            # HSV-Farbmaske
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            result = cv2.bitwise_and(image_np, image_np, mask=mask)
            st.image(result, caption="🎯 Farbmaske (detektierte Bereiche)", use_container_width=True)

            # Konturen berechnen und einzeichnen
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            image_with_contours = image_np.copy()
            cv2.drawContours(image_with_contours, contours, -1, (255, 0, 0), thickness=2)
            st.image(image_with_contours, caption="🧭 Markierte Flecken", use_container_width=True)

            fleckenzahl = len(contours)
            fläche_pixel = sum(cv2.contourArea(c) for c in contours)

            total_flecken += fleckenzahl
            total_pixel_area += fläche_pixel

            st.write(f"🔴 Automatisch erkannte Flecken: **{fleckenzahl}**")
            st.write(f"📐 Fläche in Pixeln: **{fläche_pixel:.2f}**")

            analyse_ergebnisse.append({
                "Datei": uploaded_file.name,
                "Seite": j + 1,
                "Fleckenzahl": fleckenzahl,
                "Fleckfläche (Pixel)": fläche_pixel
            })

    # 📊 Gesamtübersicht
    st.success(f"✅ Gesamte Fleckenanzahl: {total_flecken}")
    st.info(f"📏 Gesamtfläche in Pixeln: {total_pixel_area:.2f}")
    fläche_mm2 = total_pixel_area / ((300 / 25.4) ** 2)  # DPI-Umrechnung (300 dpi)
    st.info(f"📐 Geschätzte Fläche in mm²: {fläche_mm2:.2f}")

    # 🧾 Export als CSV
    df = pd.DataFrame(analyse_ergebnisse)
