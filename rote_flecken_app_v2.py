import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageSequence

# 📁 Datei-Upload
uploaded_files = st.file_uploader("📂 Lade mehrere Bilder hoch", type=["jpg", "jpeg", "png", "tif", "tiff"], accept_multiple_files=True)

# 🎛️ Farb-Slider in der Seitenleiste
st.sidebar.header("🎨 Farbempfindlichkeit einstellen")
h_min = st.sidebar.slider("Hue min", 0, 180, 0)
h_max = st.sidebar.slider("Hue max", 0, 180, 30)
s_min = st.sidebar.slider("Sättigung min", 0, 255, 70)
v_min = st.sidebar.slider("Helligkeit min", 0, 255, 50)

# 🧾 Ergebnisliste für CSV
analyse_ergebnisse = []

# 🔁 Schleife über alle Bilder
if uploaded_files:
    total_flecken = 0
    total_pixel_area = 0

    for i, uploaded_file in enumerate(uploaded_files):
        st.header(f"🖼️ Datei: `{uploaded_file.name}`")
        try:
            image_pil = Image.open(uploaded_file)
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image_pil)]
        except Exception as e:
            st.error(f"❌ Fehler beim Laden von `{uploaded_file.name}`: {e}")
            continue

        if not frames:
            st.warning("⚠️ Keine verarbeitbaren Frames gefunden.")
            continue

        for j, frame in enumerate(frames):
            if len(frames) > 1:
                st.subheader(f"📄 Seite {j + 1}")

            image_np = np.array(frame)
            st.image(image_np, caption="Originalbild", use_column_width=True)

            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            lower_bound = np.array([h_min, s_min, v_min])
            upper_bound = np.array([h_max, 255, 255])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            result = cv2.bitwise_and(image_np, image_np, mask=mask)

            st.image(result, caption="🎯 Detektierte Flecken", use_column_width=True)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            fleckenzahl = len(contours)
            fläche_pixel = sum(cv2.contourArea(c) for c in contours)

            st.write(f"🔴 Automatisch erkannte Flecken: **{fleckenzahl}**")
            st.write(f"📐 Fläche (Pixel): **{fläche_pixel:.2f}**")

            analyse_ergebnisse.append({
                "Datei": uploaded_file.name,
                "Seite": j + 1,
                "Fleckenzahl": fleckenzahl,
                "Fleckfläche (Pixel)": fläche_pixel
            })

            total_flecken += fleckenzahl
            total_pixel_area += fläche_pixel

    # 📊 Gesamtergebnisse anzeigen
    st.success(f"✅ Gesamte Fleckenanzahl: {total_flecken}")
    st.info(f"📏 Gesamtfläche in Pixeln: {total_pixel_area:.2f}")
    fläche_mm2 = total_pixel_area / ((300 / 25.4) ** 2)  # Annahme: 300 DPI
    st.info(f"📐 Geschätzte Fläche in mm²: {fläche_mm2:.2f}")

    # 📋 Tabelle anzeigen & CSV-Download ermöglichen
    df = pd.DataFrame(analyse_ergebnisse)
    st.markdown("### 🧾 Tabellarische Ergebnisse")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ CSV herunterladen", data=csv, file_name="fleckenanalyse.csv", mime="text/csv")
