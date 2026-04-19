import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import io

# --- 1. إعدادات الأمان وقاعدة بيانات المستخدمين ---
USERS = {
    "admin_nazih": {"password": "admin_password_2026", "role": "admin"},
    "user_team": {"password": "work_password_123", "role": "user"}
}

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Ajustement des alarmes ECO74", layout="wide")

# --- 3. تحسين المظهر باستخدام CSS (Professional Look) ---
st.markdown("""
    <style>
    /* تحسين الخطوط والخلفية */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* تنسيق حاوية تسجيل الدخول */
    .login-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e9ecef;
    }

    /* تنسيق العناوين */
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        letter-spacing: -1px;
    }

    /* زر التحميل والتفاعلات */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1E3A8A;
        color: white;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #3b82f6;
        border-color: #3b82f6;
    }

    /* إخفاء شريط Streamlit العلوي لزيادة الاحترافية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. منطق تسجيل الدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

def login():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h2 style='color: #1E3A8A;'>🔐 ACCÈS SÉCURISÉ</h2>
                <p style='color: #6c757d;'>Veuillez vous identifier pour accéder au système ECO74</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.role = USERS[username]["role"]
                    st.rerun()
                else:
                    st.error("Identifiants incorrects. Veuillez réessayer.")

# --- 5. تشغيل التطبيق بعد التحقق ---
if not st.session_state.authenticated:
    login()
else:
    # عرض الدور في الزاوية بخط احترافي
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: -50px;">
            <span style="background-color: #fee2e2; color: #dc2626; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #fecaca;">
                ● {st.session_state.role.upper()} SESSION
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # زر تسجيل الخروج بتصميم بسيط في الجانب
    if st.sidebar.button("🔌 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.rerun()

    # الواجهة الأمامية
    IMAGE_URL = "https://archive.challenge.ma/wp-content/uploads/2022/04/shutterstock_275763713-2-800x400-1.jpg"
    st.image(IMAGE_URL, use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>Ajustement des alarmes ECO74</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-top: -15px;'>Système de gestion et d'ajustement des rapports techniques</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar (Paramètres)
    with st.sidebar:
        st.header("⚙️ Configuration")
        target_date = st.date_input("Date de travail", datetime.now())
        st.divider()
        
        st.subheader("🛠️ Cas Spécial")
        selected_wtgs = st.multiselect("Turbines concernées", [f"WTG{str(i).zfill(2)}" for i in range(1, 62)])
        
        c1, c2 = st.columns(2)
        with c1:
            cs_start_h = st.time_input("Début", time(8, 0, 0))
        with c2:
            cs_end_h = st.time_input("Fin", time(17, 0, 0))

        cs_resp = st.selectbox("Responsable", ["EEM", "WTG", "ONEE"])
        cs_impact = st.selectbox("Nature", ["Déclenchement", "Bridage", "Inspection Générale", "Coupure"])
        
        st.divider()
        st.subheader("📋 Base de Données")
        base_file = st.file_uploader("Fichier Base (.xlsx)", type=["xlsx"])

    # معالجة ملف القاعدة
    dict_alarme = {}
    if base_file:
        try:
            df_base = pd.read_excel(base_file)
            df_base.columns = [str(c).strip() for c in df_base.columns]
            for _, row in df_base.iterrows():
                code = str(row['cod alarm']).strip()
                resp = str(row['responsable']).strip()
                pri = 1 if "EEM" in resp.upper() else 2 if "CORRMAINT" in resp.upper() else 3 if "MANUALSTOP" in resp.upper() else 4
                dict_alarme[code] = {'resp': resp, 'pri': pri}
            st.sidebar.success(f"✅ {len(dict_alarme)} Codes chargés")
        except Exception as e:
            st.sidebar.error(f"Erreur: {e}")

    # رفع الجرنال في المنتصف
    st.subheader("📂 Traitement du Journal")
    uploaded_file = st.file_uploader("Glissez-déposez le fichier Journal Système ici", type=["xlsx"])

    if uploaded_file:
        try:
            with st.spinner('Analyse en cours...'):
                raw_df = pd.read_excel(uploaded_file, header=None)
                header_row_index = None
                for i, row in raw_df.iterrows():
                    if row.astype(str).str.contains('WTG0', case=False).any():
                        header_row_index = i
                        break
                
                if header_row_index is not None:
                    df = pd.read_excel(uploaded_file, skiprows=header_row_index)
                    df = df.dropna(how='all', axis=1).iloc[:, :5]
                    df.columns = ['WTG', 'Code', 'Text', 'Start', 'End']
                    
                    df['S_DT'] = pd.to_datetime(df['Start'], dayfirst=True)
                    df['E_DT'] = pd.to_datetime(df['End'], dayfirst=True)
                    
                    d_day_start = datetime.combine(target_date, time(0, 0, 0))
                    d_day_end = datetime.combine(target_date, time(23, 59, 59))
                    
                    df = df.dropna(subset=['S_DT', 'E_DT'])
                    df = df[(df['S_DT'] <= d_day_end) & (df['E_DT'] >= d_day_start)].copy()

                    all_events = []
                    for wtg in selected_wtgs:
                        s_cs = datetime.combine(target_date, cs_start_h)
                        e_cs = datetime.combine(target_date, cs_end_h)
                        all_events.append({'WTG': wtg, 'Code': 'CAS_SPEC', 'Text': cs_impact, 'Start': s_cs, 'End': e_cs, 'Resp': cs_resp, 'Impact': cs_impact, 'Pri': 0})

                    for _, row in df.iterrows():
                        s = max(row['S_DT'], d_day_start)
                        e = min(row['E_DT'], d_day_end)
                        if s < e:
                            info = dict_alarme.get(str(row['Code']).strip(), {'resp': 'WTG', 'pri': 4})
                            all_events.append({'WTG': row['WTG'], 'Code': row['Code'], 'Text': row['Text'], 'Start': s, 'End': e, 'Resp': info['resp'], 'Impact': '-', 'Pri': info['pri']})

                    processed_data = []
                    if all_events:
                        events_df = pd.DataFrame(all_events)
                        for wtg, group in events_df.groupby('WTG'):
                            group = group.sort_values(by=['Start', 'Pri'])
                            current_timeline = []
                            for _, ev in group.iterrows():
                                ev_dict = ev.to_dict()
                                if not current_timeline:
                                    current_timeline.append(ev_dict)
                                else:
                                    last = current_timeline[-1]
                                    if ev_dict['Start'] < last['End']:
                                        if ev_dict['Pri'] < last['Pri']: 
                                            old_end = last['End']
                                            last['End'] = ev_dict['Start'] 
                                            current_timeline.append(ev_dict) 
                                            if old_end > ev_dict['End']:
                                                rem = last.copy()
                                                rem['Start'] = ev_dict['End']
                                                rem['End'] = old_end
                                                current_timeline.append(rem)
                                        elif ev_dict['Pri'] == last['Pri']:
                                            last['End'] = max(last['End'], ev_dict['End'])
                                        else: 
                                            if ev_dict['End'] > last['End']:
                                                ev_dict['Start'] = last['End']
                                                current_timeline.append(ev_dict)
                                    else:
                                        current_timeline.append(ev_dict)
                            processed_data.extend(current_timeline)

                    if processed_data:
                        final_df = pd.DataFrame(processed_data)
                        final_df['Durée_Sec'] = (final_df['End'] - final_df['Start']).dt.total_seconds()
                        final_df['Durée_H'] = final_df['Durée_Sec'] / 3600
                        final_df['Start_Str'] = final_df['Start'].dt.strftime('%H:%M:%S')
                        final_df['End_Str'] = final_df['End'].dt.strftime('%H:%M:%S')

                        st.markdown("### 📊 Résultats de l'analyse")
                        st.dataframe(final_df[['WTG', 'Code', 'Text', 'Start_Str', 'End_Str', 'Resp', 'Durée_H']], use_container_width=True)

                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            final_df.to_excel(writer, index=False)
                        
                        st.write("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 TÉLÉCHARGER LE RAPPORT FINAL",
                            data=output.getvalue(),
                            file_name=f"Rapport_ECO74_{target_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        except Exception as e:
            st.error(f"Une erreur est survenue lors du traitement : {e}")

    st.markdown("<br><br><p style='text-align: center; color: #94a3b8; font-size: 11px;'>© 2026 ECO74 System | Design & Development by Nazih Said</p>", unsafe_allow_html=True)
