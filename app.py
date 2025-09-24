import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

# ==============================
# Fungsi untuk prediksi EDD
# ==============================
def predict_edd(hpht_date):
    # Dummy data untuk melatih RandomForest
    X = np.array(range(1, 301)).reshape(-1, 1)  # usia kehamilan (hari)
    y = X.flatten() + 280  # prediksi hari persalinan

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # input hari kehamilan sejak HPHT
    input_days = np.array([[1]])
    predicted_days = model.predict(input_days)[0]

    edd_date = hpht_date + timedelta(days=int(predicted_days))
    return edd_date

# ==============================
# Fungsi untuk membuat jadwal check-up & USG
# ==============================
def generate_checkup_schedule(hpht_date, edd_date):
    schedule = []

    # Check-up tiap bulan
    current_date = hpht_date
    month = 1
    while current_date < edd_date:
        schedule.append({
            "Tanggal": current_date.strftime("%d-%m-%Y"),
            "Kegiatan": f"Check-up Bulan ke-{month}"
        })
        # tambah 1 bulan (asumsi 30 hari)
        current_date += timedelta(days=30)
        month += 1

    # Tambahkan USG di trimester 1 (minggu 12)
    usg_t1 = hpht_date + timedelta(weeks=12)
    if usg_t1 < edd_date:
        schedule.append({
            "Tanggal": usg_t1.strftime("%d-%m-%Y"),
            "Kegiatan": "USG Trimester 1"
        })

    # Tambahkan USG di trimester 3 (minggu 30)
    usg_t3 = hpht_date + timedelta(weeks=30)
    if usg_t3 < edd_date:
        schedule.append({
            "Tanggal": usg_t3.strftime("%d-%m-%Y"),
            "Kegiatan": "USG Trimester 3"
        })

    # Urutkan berdasarkan tanggal
    schedule = sorted(schedule, key=lambda x: datetime.strptime(x["Tanggal"], "%d-%m-%Y"))

    return pd.DataFrame(schedule)

# ==============================
# Streamlit UI
# ==============================
st.title("🍼 Prediksi Tanggal Kelahiran & Jadwal Check-up")

hpht_input = st.date_input("Masukkan Hari Pertama Haid Terakhir (HPHT):")

if st.button("Prediksi"):
    hpht_date = datetime.combine(hpht_input, datetime.min.time())

    # Prediksi EDD
    edd_pred = predict_edd(hpht_date)

    st.success(f"Perkiraan Tanggal Persalinan (EDD): **{edd_pred.strftime('%d-%m-%Y')}**")

    # Buat jadwal check-up
    schedule_df = generate_checkup_schedule(hpht_date, edd_pred)
    st.subheader("📅 Jadwal Check-up & USG")
    st.dataframe(schedule_df)
