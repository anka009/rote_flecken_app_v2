import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageSequence

# 🔄 Experiment zurücksetzen
if "total_flecken" not in st.session_state:
    st.session_state["total_flecken"] = 0
if "total_pixel_area" not in st.session_state:
    st.session_state["total_pixel_area"] = 0
if "analyse_ergebnisse" not in st.session_state:
    st.session_state["analyse_ergebnisse"] = []

# 🧹 Button zum Neustart
if st.sidebar.button("🧹 Neues Experiment starten"):
    st.session_state["total_flecken"] = 0
    st.session_state["total_pixel_area"] = 0
    st.session_state["analyse_ergebnisse"] = []
    st.experimental_rerun()

# 📂 Upload
uploaded_files = st.file_uploader("📂 Lade mehrere Bilder hoch", type=["jpg", "jpeg", "png", "tif", "tiff"], accept_multiple_files=True)

 # 🎨 Farbdefinition: Rot + Braun
lower_red1 = np.array([0, 70, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 70, 50])
upper_red2 = np.array([180, 255, 255])
lower_brown = np.array([10, 100, 20])
upper_brown = np.array([30, 255, 200])

for j, frame in enumerate(frames):
    image_np = np.array(frame)
    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
 
# 🧪 Masken kombinieren
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
mask3 = cv2.inRange(hsv, lower_brown, upper_brown)
mask = cv2.bitwise_or(cv2.bitwise_or(mask1, mask2), mask3)

# 🧹 Maske säubern
kernel = np.ones((5, 5), np.uint8)
mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# 🔎 Konturen + Berechnung
contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
min_area = 50
filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

fleckenzahl = len(filtered)
fläche_pixel = sum(cv2.contourArea(cnt) for cnt in filtered)
fläche_mm2 = fläche_pixel / (pixels_per_mm ** 2)

st.success(f"🔴 Flecken gefunden: {fleckenzahl}")
st.info(f"📐 Fläche: {fläche_pixel:.2f} Pixel² ({fläche_mm2:.2f} mm²)")

total_flecken += fleckenzahl
total_pixel_area += fläche_pixel

output = image_np.copy()
cv2.drawContours(output, filtered, -1, (0, 255, 0), 2)
st.image(output, caption="Markierte Flecken", channels="RGB")

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
            min_area = 50
            filtered = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
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

import pandas as pd
import io

# DataFrame aus deinen Ergebnissen
df = pd.DataFrame(st.session_state["analyse_ergebnisse"])

# CSV als Bytes vorbereiten
csv_data = df.to_csv(index=False).encode('utf-8')

# Download-Button für CSV
st.download_button(
    label="📄 Ergebnisse als CSV herunterladen",
    data=csv_data,
    file_name="flecken_analyse.csv",
    mime="text/csv"
)
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Analyse')

st.download_button(
    label="📥 Ergebnisse als Excel (.xlsx)",
    data=excel_buffer.getvalue(),
    file_name="flecken_analyse.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 📊 Gesamtübersicht
st.success(f"✅ Gesamte Fleckenanzahl: {total_flecken}")
st.info(f"📏 Gesamtfläche in Pixeln: {total_pixel_area:.2f}")
fläche_mm2 = total_pixel_area / ((300 / 25.4) ** 2)  # DPI-Umrechnung (300 dpi)
st.info(f"📐 Geschätzte Fläche in mm²: {fläche_mm2:.2f}")

    # 🧾 Export als CSV
    df = pd.DataFrame(analyse_ergebnisse)
