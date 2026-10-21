import os
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = os.environ.get("DATA_DIR", "/app/data")

# ─────────────────────────────────────────────────────────────
# PALETTE PROFESSIONNELLE (inspirée des dashboards d'entreprise)
# ─────────────────────────────────────────────────────────────
NOIR_DOUX     = "#1a1a2e"   # texte principal
GRIS_ARDOISE  = "#4a5568"   # texte secondaire
GRIS_CLAIR    = "#a0aec0"   # texte tertiaire
BORDURE       = "#e2e8f0"   # bordures subtiles
FOND_PAGE     = "#f8fafc"   # fond principal très clair
FOND_CARTE    = "#ffffff"   # cartes blanches

# Couleur d'accent principale (bleu corporate sobre)
PRIMAIRE      = "#1e3a8a"   # bleu marine profond
PRIMAIRE_MED  = "#2563eb"   # bleu moyen
PRIMAIRE_CLAIR= "#93c5fd"   # bleu clair

# Couleurs sémantiques
SUCCES        = "#059669"   # vert sobre
DANGER        = "#dc2626"   # rouge sobre
AVERTISSEMENT = "#d97706"   # orange sobre
INFO          = "#0891b2"   # cyan sobre

COULEURS = {"negatif": DANGER, "positif": SUCCES}

# Palette séquentielle pour les graphiques
PALETTE_SEQ = ["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e3a8a"]

st.set_page_config(
    page_title="Dashboard — Analyse de tweets",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS PROFESSIONNEL
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    /* Reset & base */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {NOIR_DOUX};
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
    }}
    .stApp {{
        background: {FOND_PAGE};
    }}
    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}

    /* ─────────── SIDEBAR ─────────── */
    [data-testid="stSidebar"] {{
        background: {NOIR_DOUX};
        border-right: 1px solid #2d3748;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
    }}
    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
    }}

    /* Radio navigation */
    [data-testid="stSidebar"] .stRadio > label {{
        color: #718096 !important;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
        gap: 2px;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        padding: 9px 14px;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        color: #a0aec0 !important;
        transition: all 0.15s ease;
        border-left: 2px solid transparent;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        background: rgba(255, 255, 255, 0.04);
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {{
        background: rgba(37, 99, 235, 0.15);
        border-left: 2px solid {PRIMAIRE_MED};
        color: #ffffff !important;
        font-weight: 600;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
        display: none;
    }}

    /* Bouton sidebar */
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent;
        border: 1px solid #2d3748;
        color: #a0aec0;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 0.8rem;
        font-weight: 500;
        width: 100%;
        transition: all 0.15s ease;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {PRIMAIRE_MED};
        border-color: {PRIMAIRE_MED};
        color: #ffffff;
    }}

    /* ─────────── TITRES ─────────── */
    h1 {{
        color: {NOIR_DOUX};
        font-weight: 700;
        font-size: 1.75rem;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem;
    }}
    h2 {{
        color: {NOIR_DOUX};
        font-weight: 600;
        font-size: 1.25rem;
        letter-spacing: -0.015em;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }}
    h3 {{
        color: {GRIS_ARDOISE};
        font-weight: 600;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ─────────── CARTES KPI ─────────── */
    [data-testid="stMetric"] {{
        background: {FOND_CARTE};
        border: 1px solid {BORDURE};
        border-radius: 8px;
        padding: 18px 20px;
        transition: border-color 0.15s ease;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }}
    [data-testid="stMetric"]:hover {{
        border-color: {PRIMAIRE_CLAIR};
    }}
    [data-testid="stMetricLabel"] {{
        color: {GRIS_ARDOISE} !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    [data-testid="stMetricValue"] {{
        color: {NOIR_DOUX} !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
        letter-spacing: -0.02em;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.75rem !important;
    }}

    /* ─────────── GRAPHIQUES ─────────── */
    [data-testid="stPlotlyChart"] {{
        background: {FOND_CARTE};
        border: 1px solid {BORDURE};
        border-radius: 8px;
        padding: 8px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }}

    /* ─────────── DATAFRAMES ─────────── */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDURE};
        border-radius: 8px;
        overflow: hidden;
        background: {FOND_CARTE};
    }}

    /* ─────────── ONGLETS ─────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: transparent;
        border-bottom: 1px solid {BORDURE};
        padding: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 0;
        padding: 10px 18px;
        font-weight: 500;
        font-size: 0.875rem;
        color: {GRIS_ARDOISE};
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.15s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {PRIMAIRE_MED};
    }}
    .stTabs [aria-selected="true"] {{
        background: transparent;
        color: {PRIMAIRE} !important;
        border-bottom: 2px solid {PRIMAIRE};
        font-weight: 600;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none;
    }}

    /* ─────────── ALERTES ─────────── */
    [data-testid="stAlert"] {{
        border-radius: 8px;
        border: 1px solid {BORDURE};
        border-left: 3px solid {INFO};
        background: {FOND_CARTE};
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        padding: 12px 16px;
    }}

    /* ─────────── INPUTS ─────────── */
    .stTextInput > div > div > input {{
        border-radius: 6px;
        border: 1px solid {BORDURE};
        padding: 8px 12px;
        font-size: 0.875rem;
        background: {FOND_CARTE};
        transition: all 0.15s ease;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {PRIMAIRE_MED};
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}
    .stMultiSelect > div > div {{
        border-radius: 6px;
        border: 1px solid {BORDURE};
        background: {FOND_CARTE};
    }}

    /* ─────────── CAPTIONS ─────────── */
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {GRIS_CLAIR};
        font-size: 0.75rem;
        font-weight: 400;
        line-height: 1.5;
    }}

    /* ─────────── SÉPARATEUR ─────────── */
    hr {{
        border: none;
        border-top: 1px solid {BORDURE};
        margin: 1.25rem 0;
    }}

    /* ─────────── BADGE / PILL ─────────── */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}
    .badge-positif {{ background: #d1fae5; color: {SUCCES}; }}
    .badge-negatif {{ background: #fee2e2; color: {DANGER}; }}

    /* ─────────── SCROLLBAR ─────────── */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: {GRIS_CLAIR};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: {GRIS_ARDOISE}; }}

    /* ─────────── HEADER PAGE ─────────── */
    .page-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1rem;
        border-bottom: 1px solid {BORDURE};
        margin-bottom: 1.5rem;
    }}
    .page-header h1 {{
        margin: 0;
        font-size: 1.5rem;
    }}
    .page-header .meta {{
        font-size: 0.75rem;
        color: {GRIS_CLAIR};
        text-align: right;
        line-height: 1.6;
    }}
    .page-header .meta strong {{
        color: {GRIS_ARDOISE};
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des donnees...")
def charger(nom):
    chemin = os.path.join(DATA, nom + ".csv")
    if not os.path.exists(chemin):
        return None
    return pd.read_csv(chemin, encoding="utf-8-sig")


def requis(nom):
    df = charger(nom)
    if df is None:
        st.error("Fichier manquant : %s.csv dans %s. Cette partie ne peut pas etre affichee." % (nom, DATA))
    return df


def nb(n):
    return "{:,}".format(int(n)).replace(",", " ")


def kpis():
    df = charger("kpis")
    return dict(zip(df["metrique"], df["valeur"])) if df is not None else {}


def recherche(df, colonne, cle):
    q = st.text_input("Rechercher", key=cle, placeholder="Tapez une partie du nom")
    return df[df[colonne].astype(str).str.contains(q, case=False, na=False)] if q else df


def base_layout(fig, hauteur=380, titre=None):
    """Layout Plotly sobre et professionnel."""
    fig.update_layout(
        height=hauteur,
        margin=dict(l=24, r=24, t=48 if titre else 24, b=24),
        paper_bgcolor=FOND_CARTE,
        plot_bgcolor=FOND_CARTE,
        font=dict(family="Inter, sans-serif", size=12, color=GRIS_ARDOISE),
        title=dict(
            text=titre,
            font=dict(size=13, color=NOIR_DOUX, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            pad=dict(l=4, b=12),
        ) if titre else None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=GRIS_ARDOISE),
        ),
        xaxis=dict(
            gridcolor="#f1f5f9",
            linecolor=BORDURE,
            zeroline=False,
            tickfont=dict(size=11, color=GRIS_ARDOISE),
            title_font=dict(size=11, color=GRIS_CLAIR),
        ),
        yaxis=dict(
            gridcolor="#f1f5f9",
            linecolor=BORDURE,
            zeroline=False,
            tickfont=dict(size=11, color=GRIS_ARDOISE),
            title_font=dict(size=11, color=GRIS_CLAIR),
        ),
        hoverlabel=dict(
            bgcolor=NOIR_DOUX,
            font_size=12,
            font_family="Inter, sans-serif",
            font_color="#ffffff",
            bordercolor=NOIR_DOUX,
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
fichiers = [os.path.join(DATA, f) for f in os.listdir(DATA)] if os.path.isdir(DATA) else []
maj = max((os.path.getmtime(f) for f in fichiers), default=None)

st.sidebar.markdown(
    f"""
    <div style="padding: 0 0 24px 0; border-bottom: 1px solid #2d3748; margin-bottom: 20px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; background:{PRIMAIRE_MED}; border-radius:6px;
                        display:flex; align-items:center; justify-content:center; font-size:16px;">
                📈
            </div>
            <div>
                <div style="font-size:0.95rem; font-weight:700; color:#ffffff; line-height:1.2;">
                    Tweets Analytics
                </div>
                <div style="font-size:0.7rem; color:#718096; letter-spacing:0.04em; text-transform:uppercase;">
                    Dashboard v2.0
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "NAVIGATION",
    ["Vue d'ensemble", "Sentiments", "Hashtags et mentions", "Utilisateurs", "Analyse temporelle", "Qualite des donnees"],
)

if st.sidebar.button("↻  Actualiser les donnees"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(
    f"""
    <div style="margin-top:32px; padding-top:16px; border-top:1px solid #2d3748;
                font-size:0.7rem; color:#718096; line-height:1.7;">
        <div style="color:#a0aec0; font-weight:600; letter-spacing:0.06em;
                    text-transform:uppercase; font-size:0.65rem; margin-bottom:8px;">
            Dernière mise à jour
        </div>
        <div style="color:#ffffff; font-family:'IBM Plex Mono', monospace; font-size:0.75rem;">
            {datetime.datetime.fromtimestamp(maj).strftime("%d/%m/%Y · %H:%M") if maj else "—"}
        </div>
        <div style="margin-top:12px; color:#718096;">
            Source : résultats Spark (HDFS)<br>
            Échantillon : 10 000 tweets
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1>{page}</h1>
        <div class="meta">
            <div><strong>Source</strong> · Sentiment140</div>
            <div>Échantillon · 10 000 tweets</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

K = kpis()

# ─────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────
if page == "Vue d'ensemble":
    s = requis("sentiments")
    if s is not None:
        total, pos = int(s["count"].sum()), int(s.loc[s["label"] == "positif", "count"].sum())
        neg = total - pos

        c = st.columns(3)
        c[0].metric("Tweets analysés", nb(total))
        c[1].metric("Positifs", nb(pos), delta="%.1f %%" % (pos / total * 100), delta_color="normal")
        c[2].metric("Négatifs", nb(neg), delta="%.1f %%" % (neg / total * 100), delta_color="inverse")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        c = st.columns(2)
        if "longueur_moyenne" in K:
            c[0].metric("Longueur moyenne (caractères)", K["longueur_moyenne"])
        if "utilisateurs_distincts" in K:
            c[1].metric("Utilisateurs distincts", nb(K["utilisateurs_distincts"]))

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        fig = px.pie(
            s, names="label", values="count", hole=0.65,
            color="label", color_discrete_map=COULEURS,
        )
        fig.update_traces(
            textinfo="percent",
            textfont=dict(size=14, family="IBM Plex Mono", color="#ffffff"),
            marker=dict(line=dict(color=FOND_CARTE, width=3)),
            hovertemplate="<b>%{label}</b><br>%{value:,} tweets<br>%{percent}<extra></extra>",
        )
        fig = base_layout(fig, hauteur=400)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=12)),
            annotations=[dict(
                text=f"<b>{nb(total)}</b><br><span style='font-size:10px;color:{GRIS_CLAIR}'>TWEETS</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=22, color=NOIR_DOUX, family="IBM Plex Mono"),
            )],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Sentiment 0 = négatif, 4 = positif (convention de Sentiment140).")


elif page == "Sentiments":
    s, t = requis("sentiments"), requis("stats_par_sentiment")
    if s is not None:
        s = s.assign(pourcentage=(s["count"] / s["count"].sum() * 100).round(1))
        fig = px.bar(
            s, x="label", y="count", color="label",
            color_discrete_map=COULEURS,
            text=s.apply(lambda r: f"{nb(r['count'])}  ·  {r['pourcentage']}%", axis=1),
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=11, color=GRIS_ARDOISE, family="IBM Plex Mono"),
            marker=dict(line=dict(color=FOND_CARTE, width=1)),
            width=0.45,
            hovertemplate="<b>%{x}</b><br>%{y:,} tweets<extra></extra>",
        )
        fig = base_layout(fig, hauteur=400)
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title=None, tickfont=dict(size=13, color=NOIR_DOUX, family="Inter"))
        fig.update_yaxes(title=None)
        st.plotly_chart(fig, use_container_width=True)

    if t is not None:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        choix = st.multiselect("Filtrer par sentiment", list(t["label"]), default=list(t["label"]))
        t_f = t[t["label"].isin(choix)]
        c = st.columns(3)
        for col, champ, titre in [
            (c[0], "longueur_moy", "Longueur moyenne"),
            (c[1], "mentions_moy", "Mentions / tweet"),
            (c[2], "part_avec_lien", "Part avec lien"),
        ]:
            fig = px.bar(
                t_f, x="label", y=champ, color="label",
                color_discrete_map=COULEURS,
                labels={"label": "", champ: ""},
            )
            fig.update_traces(
                marker=dict(line=dict(color=FOND_CARTE, width=1)),
                width=0.5,
                hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
            )
            fig = base_layout(fig, hauteur=280, titre=titre)
            fig.update_layout(showlegend=False)
            fig.update_xaxes(tickfont=dict(size=12, color=NOIR_DOUX, family="Inter"))
            col.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.dataframe(t_f, hide_index=True, use_container_width=True)
        st.caption("Écarts observés sur 10 000 tweets, sans test statistique.")


elif page == "Hashtags et mentions":
    onglets = st.tabs(["Hashtags", "Mentions"])
    for onglet, nom, col in [(onglets[0], "top_hashtags", "hashtag"), (onglets[1], "top_mentions", "mention")]:
        with onglet:
            d = requis(nom)
            if d is not None:
                d = recherche(d, col, "q_" + nom).sort_values("count", ascending=True)
                fig = go.Figure(go.Bar(
                    x=d["count"],
                    y=d[col],
                    orientation="h",
                    marker=dict(
                        color=d["count"],
                        colorscale=[[0, "#dbeafe"], [1, PRIMAIRE]],
                        line=dict(color=FOND_CARTE, width=0),
                    ),
                    text=d["count"],
                    textposition="outside",
                    textfont=dict(size=11, color=GRIS_ARDOISE, family="IBM Plex Mono"),
                    hovertemplate="<b>%{y}</b><br>%{x:,} occurrences<extra></extra>",
                ))
                fig = base_layout(fig, hauteur=max(360, len(d) * 38))
                fig.update_layout(showlegend=False, bargap=0.35)
                fig.update_xaxes(title=None, showgrid=True)
                fig.update_yaxes(title=None, tickfont=dict(size=12, color=NOIR_DOUX, family="Inter"))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(d.sort_values("count", ascending=False), hide_index=True, use_container_width=True)
    st.caption("Top 10 uniquement. Les hashtags sont rares (environ 2,7 % des tweets) : classement fragile.")


elif page == "Utilisateurs":
    u = requis("top_utilisateurs")
    if u is not None:
        u = recherche(u, u.columns[0], "q_users").sort_values("count", ascending=True)
        fig = go.Figure(go.Bar(
            x=u["count"],
            y=u[u.columns[0]],
            orientation="h",
            marker=dict(
                color=u["count"],
                colorscale=[[0, "#e0e7ff"], [1, PRIMAIRE]],
                line=dict(color=FOND_CARTE, width=0),
            ),
            text=u["count"],
            textposition="outside",
            textfont=dict(size=11, color=GRIS_ARDOISE, family="IBM Plex Mono"),
            hovertemplate="<b>%{y}</b><br>%{x:,} tweets<extra></extra>",
        ))
        fig = base_layout(fig, hauteur=max(360, len(u) * 38))
        fig.update_layout(showlegend=False, bargap=0.35)
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None, tickfont=dict(size=12, color=NOIR_DOUX, family="Inter"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(u.sort_values("count", ascending=False), hide_index=True, use_container_width=True)
        st.caption("Top 10 : plusieurs utilisateurs ont le même nombre de tweets, l'ordre entre ex aequo est arbitraire.")


elif page == "Analyse temporelle":
    h = requis("repartition_heure")
    if h is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=h["heure"], y=h["count"],
            mode="lines+markers",
            line=dict(color=PRIMAIRE_MED, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=7, color=FOND_CARTE, line=dict(color=PRIMAIRE_MED, width=2)),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.08)",
            hovertemplate="<b>%{x}h</b><br>%{y:,} tweets<extra></extra>",
            name="",
        ))
        fig = base_layout(fig, hauteur=420)
        fig.update_xaxes(dtick=1, title="Heure de la journée")
        fig.update_yaxes(title="Nombre de tweets")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.dataframe(h, hide_index=True, use_container_width=True)
        st.info(
            "Heure lue dans la colonne date. Le suffixe de fuseau (PDT) a été retiré à la conversion : "
            "les heures sont celles des données d'origine, sans conversion de fuseau."
        )
        if "dates_non_converties" in K:
            st.caption("Dates non converties : %s" % K["dates_non_converties"])


elif page == "Qualite des donnees":
    q = charger("qualite_colonnes")
    if not K and q is None:
        st.error("Aucun fichier de qualité disponible (kpis.csv, qualite_colonnes.csv).")
    else:
        c = st.columns(3)
        if "lignes" in K:
            c[0].metric("Lignes", nb(K["lignes"]))
        if q is not None:
            c[1].metric("Valeurs nulles", nb(q["nulls"].sum()))
            c[2].metric("Chaînes vides", nb(q["vides"].sum()))

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        c = st.columns(3)
        for col, cle, titre in [
            (c[0], "doublons_complets", "Doublons complets"),
            (c[1], "tweet_id_distincts", "tweet_id distincts"),
            (c[2], "doublons_tweet_id", "Doublons sur tweet_id"),
        ]:
            if cle in K:
                col.metric(titre, nb(K[cle]))

        if q is not None:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.subheader("Détail par colonne")
            st.dataframe(q, hide_index=True, use_container_width=True)