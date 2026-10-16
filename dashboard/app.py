from html import escape
from pathlib import Path
import base64
import itertools
import sqlite3
import math
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

_ST_VERSION = tuple(int(p) for p in st.__version__.split(".")[:2] if p.isdigit())
STRETCH = {"width": "stretch"} if _ST_VERSION >= (1, 50) else {"use_container_width": True}
# ============================================================
# IPL CRICKET ANALYTICS — Neobrutalist admin portal (v6)
# Cream canvas, 2px black outlines, hard offset shadows.
# Every number from SQL via query()/scalar(). ipl.db untouched.
# Overview: 3 KPIs + 5 charts. Match: 3 KPIs + 5 charts + table.
# Exactly two tabs: Overview, Match Analysis.
# ============================================================
ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
# DB lives next to app.py (dashboard/ipl.db), canonical copy in data/raw/ipl.db.
# Check candidates in order so the dashboard works regardless of run location.
_DB_CANDIDATES = [
    APP_DIR / "ipl.db",
    ROOT / "data" / "raw" / "ipl.db",
    ROOT / "ipl.db",
]
DB_PATH = next((p for p in _DB_CANDIDATES if p.exists()), _DB_CANDIDATES[0])
STYLE_PATH = APP_DIR / "style.css"
ANIM_PATH = APP_DIR / "cricket_anim.html"


def _asset_path(name: str) -> Path:
    """Assets live in dashboard/assets/; fall back to ROOT/assets/ if moved."""
    primary = APP_DIR / "assets" / name
    if primary.exists():
        return primary
    return ROOT / "assets" / name


BAT_PATH = _asset_path("cricket_bat.png")
BALL_PATH = _asset_path("cricket_ball.png")
STADIUM_PATH = _asset_path("cricket_stadium.png")
st.set_page_config(page_title="IPL Cricket Analytics", page_icon="🏏", layout="wide",
                   initial_sidebar_state="collapsed")
RED = "#FF4545"
BLUE = "#4D63F5"
YELLOW = "#FFD426"
MINT = "#7BE0B2"
PALETTE = ["#4D63F5", "#FF4545", "#111111", "#159B66", "#B47B19", "#7BE0B2"]
# ------------------------------------------------------------
if STYLE_PATH.exists():
    st.markdown(f"<style>\n{STYLE_PATH.read_text(encoding='utf-8')}\n</style>",
                unsafe_allow_html=True)
# ------------------------------------------------------------
# Data access — analytics computed in SQLite; SQRT on every connection
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _run_query(sql: str, params: tuple, db_mtime: float) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        connection.create_function("SQRT", 1, math.sqrt)
        return pd.read_sql_query(sql, connection, params=params)

def query(sql: str, params=()) -> pd.DataFrame:
    return _run_query(sql, tuple(params), DB_PATH.stat().st_mtime)

def scalar(sql: str, params=(), default=0):
    result = query(sql, params)
    if result.empty or result.iloc[0, 0] is None:
        return default
    return result.iloc[0, 0]
# ------------------------------------------------------------
# Navigation + toolbar actions (all real, all SQL-backed)
# ------------------------------------------------------------
def goto(page: str):
    st.session_state["page"] = page
    st.query_params["page"] = page

def toggle_side():
    st.session_state["side_open"] = not st.session_state.get("side_open", True)

def season_report_csv() -> bytes:
    df = query("""
        WITH inn AS (
            SELECT match_id, SUM(total_runs) AS runs FROM deliveries
            WHERE innings = 1 AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id
        ), six AS (
            SELECT match_id, COUNT(*) AS s FROM deliveries
            WHERE batter_runs = 6 AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id
        )
        SELECT m.season AS season, COUNT(*) AS matches,
               ROUND(AVG(i.runs), 1) AS avg_first_innings,
               COALESCE(SUM(s.s), 0) AS sixes
        FROM matches m LEFT JOIN inn i ON i.match_id = m.match_id
                       LEFT JOIN six s ON s.match_id = m.match_id
        WHERE m.season IS NOT NULL
        GROUP BY m.season ORDER BY MIN(m.match_date)
    """)
    return df.to_csv(index=False).encode("utf-8")
# ------------------------------------------------------------
# Reusable components
# ------------------------------------------------------------
def page_head(eyebrow: str, title: str, sub: str):
    st.markdown(f'<div class="eyebrow">{escape(eyebrow)}</div>'
                f'<h1 class="page-title">{escape(title)}</h1>'
                f'<div class="page-sub">{escape(sub)}</div>', unsafe_allow_html=True)

def kpi_cards(items):
    """items: (tile color, label, value, support). Exactly three per row."""
    cards = "".join(
        f'<div class="kpi"><span class="kpi-tile" style="background:{tile}"></span>'
        f'<span class="kpi-txt"><span class="kpi-label">{escape(label)}</span>'
        f'<span class="kpi-value">{escape(str(value))}</span>'
        f'<span class="kpi-support">{escape(support)}</span></span></div>'
        for tile, label, value, support in items)
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)

def panel(title: str, sub: str):
    st.markdown(f'<div class="panel-title">{escape(title)}</div>'
                f'<div class="panel-sub">{escape(sub)}</div>', unsafe_allow_html=True)

def chart_head(title: str, sub: str, key: str, options: list) -> str:
    """Chart header: title left, compact functional dropdown right. Returns the choice."""
    t, d = st.columns([3.2, 1.6], gap="small")
    with t:
        panel(title, sub)
    with d:
        st.markdown('<label class="fld">VIEW</label>', unsafe_allow_html=True)
        return st.selectbox(title, options, key=f"{key}_view", label_visibility="collapsed")

def inn_filter(choice: str):
    """SQL fragment narrowing one chart to a single innings (Both = no filter)."""
    n = {"Both innings": None, "First innings": 1, "Second innings": 2}[choice]
    return (" AND innings = ?", (n,)) if n else ("", ())

_anim_uid = itertools.count(1)

@st.cache_data(show_spinner=False)
def _anim_fragment(bat_mtime: float, ball_mtime: float, frag_mtime: float) -> str | None:
    """Animation fragment with PNGs embedded as data URIs; None if assets are missing.

    File mtimes are cache keys so adding or swapping the PNGs refreshes the output.
    """
    try:
        bat = base64.b64encode(BAT_PATH.read_bytes()).decode("ascii")
        ball = base64.b64encode(BALL_PATH.read_bytes()).decode("ascii")
    except OSError:
        return None
    return (ANIM_PATH.read_text(encoding="utf-8")
            .replace("__BAT__", f"data:image/png;base64,{bat}")
            .replace("__BALL__", f"data:image/png;base64,{ball}"))

def cricket_animation() -> bool:
    """Render the batting loop in an isolated iframe beside the heading.

    Returns False (rendering nothing) when the PNG assets are absent, so the
    layout falls back to the plain heading with zero visual change.
    """
    if not (BAT_PATH.is_file() and BALL_PATH.is_file()):
        return False
    frag = _anim_fragment(BAT_PATH.stat().st_mtime, BALL_PATH.stat().st_mtime,
                          ANIM_PATH.stat().st_mtime)
    if frag is None:
        return False
    components.html(frag.replace("__UID__", f"u{next(_anim_uid)}"), height=246,
                    scrolling=False)
    return True

@st.cache_data(show_spinner=False)
def _stadium_css(mtime: float) -> str:
    """Fixed full-viewport stadium layer (one rule, both tabs). Empty if asset missing."""
    try:
        img = base64.b64encode(STADIUM_PATH.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return (
        "<style>[data-testid='stAppViewContainer']{background:#F7F6F2;}"
        "[data-testid='stAppViewContainer']::before{content:'';position:fixed;inset:0;"
        "z-index:0;pointer-events:none;"
        "background:linear-gradient(rgba(247,246,242,0.72),rgba(247,246,242,0.72)),"
        f"url(data:image/png;base64,{img}) center center/cover no-repeat;}}"
        "[data-testid='stAppViewContainer']>*{position:relative;z-index:1;}"
        "@media (max-width:650px){[data-testid='stAppViewContainer']::before{"
        "background-position:center 32%;}}</style>"
    )

@st.fragment
def _head_with_animation(eyebrow: str, title: str, sub: str):
    """Shared heading row for both tabs: title left, batting loop right.

    One implementation — Overview and Match Analysis reuse it. Rendered as a
    fragment so filter reruns never remount the animation iframe.
    """
    if BAT_PATH.is_file() and BALL_PATH.is_file():
        h1, h2 = st.columns([3, 1.5], gap="medium")
        with h1:
            page_head(eyebrow, title, sub)
        with h2:
            cricket_animation()
    else:
        page_head(eyebrow, title, sub)
# ------------------------------------------------------------
# Plotly theme — white, black text, light gray grid
# ------------------------------------------------------------
def style_fig(fig, height: int, show_legend: bool):
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", color="#111111", size=12),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    title_text=""),
        hoverlabel=dict(bgcolor="#111111", font_color="#FFFFFF"))
    fig.update_xaxes(showgrid=True, gridcolor="#E7E5DF", linecolor="#111111",
                     zerolinecolor="#111111", tickfont=dict(color="#595959", size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#E7E5DF", linecolor="#111111",
                     zerolinecolor="#111111", tickfont=dict(color="#595959", size=11))
    return fig

def chart(df, x, y, key, kind="Bar", color=None, height=300, ref_line=None, y_range=None,
          text_col=None, x_title="", y_title="", x_categorical=False):
    if df.empty:
        st.markdown('<div class="empty">No data for this selection.</div>', unsafe_allow_html=True)
        return
    data = df.copy()
    if kind in ("Line", "Area"):
        mk = px.line if kind == "Line" else px.area
        fig = mk(data, x=x, y=y, markers=True, color=color,
                 color_discrete_sequence=PALETTE, line_shape="linear")
        fig.update_traces(line_width=3, marker_size=7, marker_line_width=1.5,
                          marker_line_color="#111111")
    elif kind == "HBar":
        fig = px.bar(data, x=y, y=x, orientation="h", color=color,
                     color_discrete_sequence=PALETTE, barmode="group", text=text_col or y)
        fig.update_traces(textposition="outside", cliponaxis=False)
    else:
        fig = px.bar(data, x=x, y=y, color=color, color_discrete_sequence=PALETTE,
                     barmode="group", text=text_col or (y if kind == "Labeled" else None))
        if kind == "Labeled":
            fig.update_traces(textposition="outside", cliponaxis=False)
    horizontal = kind == "HBar"
    if y_range and not horizontal:
        fig.update_yaxes(range=list(y_range))
    if ref_line:
        add = fig.add_vline if horizontal else fig.add_hline
        add(**{"x" if horizontal else "y": ref_line[0]}, line_dash="dash", line_color="#F04444",
            annotation_text=ref_line[1], annotation_position="top left")
    if x_title or y_title:
        if horizontal:
            fig.update_yaxes(title_text=x_title)
            fig.update_xaxes(title_text=y_title)
        else:
            fig.update_xaxes(title_text=x_title)
            fig.update_yaxes(title_text=y_title)
    if x_categorical and not horizontal:
        # Season labels look numeric ("2019"…) so Plotly would sniff a linear
        # axis and stretch gaps for missing seasons. Pin to the observed
        # categories in query order: equal spacing, no invented seasons.
        fig.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=data[x].astype(str).tolist(),
        )
    style_fig(fig, height, show_legend=color is not None)
    st.plotly_chart(fig, **STRETCH, config={"displayModeBar": False, "displaylogo": False},
                    key=f"{key}_plot")

def swiss_table(df, cols: list, pom: str):
    """cols: (field, header). POTM badge is presentational; data is SQL."""
    if df.empty:
        st.markdown('<div class="empty">No player data recorded for this match.</div>',
                    unsafe_allow_html=True)
        return
    head = "".join(f"<th>{escape(h)}</th>" for _, h in cols)
    body = ""
    for _, row in df.iterrows():
        nm = str(row["player"])
        badge = ' <span class="potm">POTM</span>' if nm == pom else ""
        cells = "".join(f"<td>{escape('' if pd.isna(row[f]) else str(row[f]))}</td>"
                        for f, _ in cols)
        body += f"<tr><td class='pn'><strong>{escape(nm)}</strong>{badge}</td>{cells}</tr>"
    st.markdown(f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Player</th>{head}'
                f"</tr></thead><tbody>{body}</tbody></table></div>", unsafe_allow_html=True)
# ------------------------------------------------------------
# Sidebar + toolbar
# ------------------------------------------------------------
def sidebar(active: str, counts: dict):
    open_ = st.session_state.get("side_open", True)
    if not open_:
        st.markdown('<div class="rail-on"></div>', unsafe_allow_html=True)
        st.button("›", key="side_toggle", help="Expand sidebar",
                  on_click=toggle_side)
        return
    with st.container(border=True):
        brow, tcol = st.columns([5, 1.2], gap="small")
        with brow:
            st.markdown(
                '<div class="brand"><span class="brand-tile">C</span>'
                '<span><span class="brand-name">IPL ANALYTICS</span>'
                '<span class="brand-sub">CRICKET DATA PORTAL</span></span></div>'
                '<div class="nav-group">MAIN</div>', unsafe_allow_html=True)
        with tcol:
            st.button("‹", key="side_toggle", help="Collapse sidebar",
                      on_click=toggle_side)
        cur_is_overview = (active == "Overview")
        st.button("◫  Overview", key="nav_overview",
                  type="primary" if cur_is_overview else "secondary",
                  on_click=goto, args=("Overview",), **STRETCH)
        st.button("○  Match Analysis", key="nav_match",
                  type="primary" if not cur_is_overview else "secondary",
                  on_click=goto, args=("Match",), **STRETCH)
        st.markdown(
            '<div class="nav-group">DATA</div>'
            f'<div class="nav-stat"><span>Seasons</span><b>{counts["seasons"]}</b></div>'
            f'<div class="nav-stat"><span>Teams</span><b>{counts["teams"]}</b></div>'
            f'<div class="nav-stat"><span>Players</span><b>{counts["players"]:,}</b></div>'
            '<div class="nav-group">DATABASE</div>'
            f'<div class="nav-stat"><span>Matches</span><b>{counts["matches"]:,}</b></div>'
            f'<div class="nav-stat"><span>Balls</span><b>{counts["balls"]:,}</b></div>',
            unsafe_allow_html=True)
        st.markdown('<div class="export-gap"></div>', unsafe_allow_html=True)
        st.download_button("⭳ Export report", season_report_csv(),
                           file_name="ipl_season_report.csv", mime="text/csv", key="side_export",
                           help="Download per-season matches, average score and sixes.",
                           **STRETCH)

# ------------------------------------------------------------
# Overview
# ------------------------------------------------------------
def draw_overview():
    _head_with_animation("IPL CRICKET ANALYTICS", "Overview",
                           "Explore IPL scoring trends, chasing performance, and match outcomes.")
    seasons_df = query("SELECT season FROM matches WHERE season IS NOT NULL "
                       "GROUP BY season ORDER BY MIN(match_date)")
    season_options = seasons_df["season"].astype(str).tolist()
    teams_df = query("SELECT team FROM (SELECT team1 AS team FROM matches UNION "
                     "SELECT team2 AS team FROM matches) WHERE team IS NOT NULL ORDER BY team")
    with st.container(border=True):
        f1, f2 = st.columns(2, gap="medium")
        with f1:
            st.markdown('<label class="fld">SEASON</label>', unsafe_allow_html=True)
            f_season = st.selectbox("Season", ["All seasons"] + season_options, key="ov_season",
                                    label_visibility="collapsed")
        with f2:
            st.markdown('<label class="fld">TEAM</label>', unsafe_allow_html=True)
            f_team = st.selectbox("Team", ["All teams"] + teams_df["team"].astype(str).tolist(),
                                  key="ov_team", label_visibility="collapsed")
    total_matches = int(scalar("SELECT COUNT(DISTINCT match_id) FROM matches"))
    total_runs = int(scalar("SELECT COALESCE(SUM(total_runs),0) FROM deliveries"))
    season_count = int(scalar("SELECT COUNT(DISTINCT season) FROM matches WHERE season IS NOT NULL"))
    chase = query("""
        WITH completed AS (
            SELECT CASE WHEN m.match_winner = i2.batting_team THEN 1.0 ELSE 0.0 END AS won
            FROM matches m
            JOIN (SELECT match_id FROM deliveries WHERE innings = 1
                  AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id) i1
              ON i1.match_id = m.match_id
            JOIN (SELECT match_id, batting_team FROM deliveries WHERE innings = 2
                  AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id, batting_team) i2
              ON i2.match_id = m.match_id
            WHERE m.match_winner IS NOT NULL
        ), stats AS (SELECT COUNT(*) AS n, AVG(won) AS p FROM completed)
        SELECT n, ROUND(100.0 * p, 1) AS rate,
               ROUND(100.0 * (p - 1.96 * SQRT(p * (1.0 - p) / n)), 1) AS lo,
               ROUND(100.0 * (p + 1.96 * SQRT(p * (1.0 - p) / n)), 1) AS hi,
               ROUND((p - 0.5) / SQRT(0.25 / n), 2) AS z
        FROM stats
    """).iloc[0]
    kpi_cards([
        (RED, "TOTAL MATCHES", f"{total_matches:,}", f"{season_count} seasons covered"),
        (YELLOW, "TOTAL RUNS", f"{total_runs:,}", "Every delivery on record"),
        (BLUE, "CHASE WIN RATE", f"{float(chase['rate']):.1f}%",
         f"95% CI {float(chase['lo']):.1f}–{float(chase['hi']):.1f}% · z {float(chase['z']):.2f}"),
    ])
    filt, params = "", []
    if f_season != "All seasons":
        filt += " AND m.season = ?"
        params.append(f_season)
    if f_team != "All teams":
        filt += " AND (m.team1 = ? OR m.team2 = ?)"
        params.extend([f_team, f_team])
    left, right = st.columns([2, 1], gap="medium")
    with left:
        with st.container(border=True):
            trend_view = chart_head("Average First-Innings Score",
                                    "How scoring has changed across IPL seasons.", "ov_trend",
                                    ["All seasons", "Last 5 seasons", "Last 10 seasons"])
            scoped = query(f"""
                SELECT m.season AS s FROM matches m
                WHERE m.season IS NOT NULL {filt}
                GROUP BY m.season ORDER BY MIN(m.match_date)
            """, tuple(params))["s"].astype(str).tolist()
            take = {"All seasons": None, "Last 5 seasons": 5, "Last 10 seasons": 10}[trend_view]
            window = scoped[-take:] if take else scoped
            marks = ",".join("?" for _ in window) or "NULL"
            avg_scores = query(f"""
                SELECT m.season, ROUND(AVG(i.runs), 1) AS avg_score
                FROM matches m JOIN (
                    SELECT match_id, SUM(total_runs) AS runs FROM deliveries
                    WHERE innings = 1 AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id
                ) i ON i.match_id = m.match_id
                WHERE m.season IS NOT NULL {filt} AND m.season IN ({marks})
                GROUP BY m.season ORDER BY MIN(m.match_date)
            """, tuple(params) + tuple(window))
            avg_scores["season"] = avg_scores["season"].astype(str)
            chart(avg_scores, "season", "avg_score", "ov_trend", kind="Line", height=330,
                  x_title="Season", y_title="Average runs", x_categorical=True)
        with st.container(border=True):
            chase_view = chart_head("Chase Win Rate by Target",
                                    "Win percentage by first-innings band.", "ov_chase",
                                    ["All targets", "Targets below 160", "Targets 160 and above"])
            band_cond = {"All targets": "",
                         "Targets below 160": "WHERE target < 160",
                         "Targets 160 and above": "WHERE target >= 160"}[chase_view]
            bands = query(f"""
                WITH base AS (
                    SELECT t.runs AS target,
                           CASE WHEN m.match_winner = c.team THEN 1.0 ELSE 0.0 END AS won
                    FROM (SELECT match_id, SUM(total_runs) AS runs FROM deliveries
                          WHERE innings = 1 AND COALESCE(is_super_over, 0) = 0 GROUP BY match_id) t
                    JOIN matches m ON m.match_id = t.match_id
                    JOIN (SELECT match_id, batting_team AS team FROM deliveries
                          WHERE innings = 2 AND COALESCE(is_super_over, 0) = 0
                          GROUP BY match_id, batting_team) c ON c.match_id = t.match_id
                    WHERE m.match_winner IS NOT NULL
                )
                SELECT CASE WHEN target < 140 THEN 'Below 140'
                            WHEN target < 160 THEN '140–159'
                            WHEN target < 180 THEN '160–179'
                            WHEN target < 200 THEN '180–199' ELSE '200+' END AS band,
                       COUNT(*) AS n, ROUND(AVG(won) * 100, 1) AS rate
                FROM base {band_cond} GROUP BY band
                ORDER BY CASE band WHEN 'Below 140' THEN 1 WHEN '140–159' THEN 2
                         WHEN '160–179' THEN 3 WHEN '180–199' THEN 4 ELSE 5 END
            """)
            if not bands.empty:
                chart(bands, "band", "rate", "ov_chase", kind="Labeled", height=300,
                      ref_line=(50, "50%"), y_range=(0, max(100, float(bands["rate"].max()) + 20)),
                      text_col="n", x_title="First-innings total", y_title="Chase win rate (%)")
            else:
                st.markdown('<div class="empty">No chases in this target range.</div>',
                            unsafe_allow_html=True)
    with right:
        with st.container(border=True):
            six_view = chart_head("Sixes by Season", "Counts from delivery-level data.", "ov_sixes",
                                  ["All seasons", "Last 5 seasons", "Last 10 seasons"])
            take = {"All seasons": None, "Last 5 seasons": 5, "Last 10 seasons": 10}[six_view]
            six_window = scoped[-take:] if take else scoped
            six_marks = ",".join("?" for _ in six_window) or "NULL"
            sixes = query(f"""
                SELECT m.season, COUNT(*) AS sixes FROM deliveries d
                JOIN matches m ON m.match_id = d.match_id
                WHERE d.batter_runs = 6 AND COALESCE(d.is_super_over, 0) = 0 {filt}
                  AND m.season IN ({six_marks})
                GROUP BY m.season ORDER BY MIN(m.match_date)
            """, tuple(params) + tuple(six_window))
            sixes["season"] = sixes["season"].astype(str)
            chart(sixes, "season", "sixes", "ov_sixes", kind="Bar", height=240,
                  x_title="Season", y_title="Sixes")
        with st.container(border=True):
            wins_view = chart_head("Victory Types", "Wins by runs against wins by wickets.",
                                   "ov_wins", ["All outcomes", "By runs", "By wickets"])
            wins_cond = {"All outcomes": "",
                         "By runs": "AND COALESCE(win_by_runs, 0) > 0",
                         "By wickets": "AND COALESCE(win_by_wickets, 0) > 0"}[wins_view]
            wins = query(f"""
                SELECT CASE WHEN COALESCE(win_by_runs, 0) > 0 THEN 'By runs'
                            WHEN COALESCE(win_by_wickets, 0) > 0 THEN 'By wickets'
                            ELSE 'Other' END AS outcome, COUNT(*) AS n
                FROM matches WHERE match_winner IS NOT NULL {wins_cond} GROUP BY outcome
            """)
            chart(wins, "outcome", "n", "ov_wins", kind="Labeled", height=240,
                  x_title="", y_title="Matches")
        with st.container(border=True):
            margin_view = chart_head("Winning Margins", "Distribution of victory margins.",
                                     "ov_margin", ["All margins", "Wins by runs", "Wins by wickets"])
            margin_cond = {"All margins": "",
                           "Wins by runs": "AND COALESCE(win_by_runs, 0) > 0",
                           "Wins by wickets": "AND COALESCE(win_by_wickets, 0) > 0"}[margin_view]
            margins = query(f"""
                SELECT CASE WHEN win_by_runs BETWEEN 1 AND 10 THEN '1–10 runs'
                            WHEN win_by_runs BETWEEN 11 AND 25 THEN '11–25 runs'
                            WHEN win_by_runs > 25 THEN '26+ runs'
                            WHEN win_by_wickets BETWEEN 1 AND 3 THEN '1–3 wkts'
                            WHEN win_by_wickets BETWEEN 4 AND 6 THEN '4–6 wkts'
                            WHEN win_by_wickets BETWEEN 7 AND 10 THEN '7–10 wkts'
                            ELSE 'Other' END AS margin, COUNT(*) AS n
                FROM matches WHERE match_winner IS NOT NULL {margin_cond} GROUP BY margin
                ORDER BY CASE margin WHEN '1–10 runs' THEN 1 WHEN '11–25 runs' THEN 2
                         WHEN '26+ runs' THEN 3 WHEN '1–3 wkts' THEN 4
                         WHEN '4–6 wkts' THEN 5 WHEN '7–10 wkts' THEN 6 ELSE 7 END
            """)
            chart(margins, "margin", "n", "ov_margin", kind="HBar", height=280,
                  x_title="Margin", y_title="Matches")
# ------------------------------------------------------------
# Match
# ------------------------------------------------------------
def draw_match():
    _head_with_animation("MATCH CENTRE", "Match Analysis",
                         "Explore innings scoring, player performance, and match statistics.")
    seasons = query("SELECT season FROM matches WHERE season IS NOT NULL GROUP BY season "
                    "ORDER BY MIN(match_date)")
    season_options = seasons["season"].astype(str).tolist()
    if not season_options:
        st.error("No seasons found in the matches table.")
        return
    f_season = st.session_state.get("mt_season", season_options[0])
    teams = query("SELECT team FROM (SELECT team1 AS team FROM matches WHERE season = ? "
                  "UNION SELECT team2 AS team FROM matches WHERE season = ?) "
                  "WHERE team IS NOT NULL ORDER BY team", (f_season, f_season))
    with st.container(border=True):
        f1, f2, f3 = st.columns([1, 1.2, 2.6], gap="medium")
        with f1:
            st.markdown('<label class="fld">SEASON</label>', unsafe_allow_html=True)
            f_season = st.selectbox("Season", season_options, key="mt_season",
                                    label_visibility="collapsed")
        with f2:
            st.markdown('<label class="fld">TEAM</label>', unsafe_allow_html=True)
            f_team = st.selectbox("Team", ["All teams"] + teams["team"].astype(str).tolist(),
                                  key="mt_team", label_visibility="collapsed")
        sql = ("SELECT match_id, match_date, team1, team2, venue, match_winner, win_by_runs, "
               "win_by_wickets, result, toss_winner, toss_decision, player_of_match "
               "FROM matches WHERE season = ?")
        params: list = [f_season]
        if f_team != "All teams":
            sql += " AND (team1 = ? OR team2 = ?)"
            params.extend([f_team, f_team])
        sql += " ORDER BY match_date, match_id"
        match_list = query(sql, tuple(params))
        if match_list.empty:
            st.markdown('<div class="empty">No matches for this season and team.</div>',
                        unsafe_allow_html=True)
            return
        labels = [f"{r['match_date']} · {r['team1']} vs {r['team2']} · ID {int(r['match_id'])}"
                  for _, r in match_list.iterrows()]
        ids = [int(r["match_id"]) for _, r in match_list.iterrows()]
        with f3:
            st.markdown('<label class="fld">MATCH</label>', unsafe_allow_html=True)
            pick = st.selectbox("Match", labels, key="mt_choice", label_visibility="collapsed",
                                help="All panels below follow this match.")
    match_id = ids[labels.index(pick)]
    match = query("SELECT * FROM matches WHERE match_id = ?", (match_id,)).iloc[0]
    inn = query("""
        SELECT innings, MAX(batting_team) AS side, SUM(total_runs) AS runs,
               SUM(CASE WHEN is_wicket = 1 AND COALESCE(wicket_kind, '') NOT IN
                   ('retired hurt', 'obstructing the field', 'retired out')
                   THEN 1 ELSE 0 END) AS wkts
        FROM deliveries WHERE match_id = ? AND innings IN (1, 2)
          AND COALESCE(is_super_over, 0) = 0 GROUP BY innings ORDER BY innings
    """, (match_id,))
    scored = {int(r["innings"]): (int(r["runs"] or 0), int(r["wkts"] or 0))
              for _, r in inn.iterrows()}
    side = {1: str(match["team1"]), 2: str(match["team2"])}
    for _, r in inn.iterrows():
        if pd.notna(r["side"]):
            side[int(r["innings"])] = str(r["side"])
    r1, w1 = scored.get(1, (None, None))
    r2, w2 = scored.get(2, (None, None))
    winner = str(match["match_winner"]) if pd.notna(match["match_winner"]) else "No result"
    if pd.notna(match["win_by_runs"]) and float(match["win_by_runs"]) > 0:
        margin = f"Won by {int(match['win_by_runs'])} runs"
    elif pd.notna(match["win_by_wickets"]) and float(match["win_by_wickets"]) > 0:
        margin = f"Won by {int(match['win_by_wickets'])} wickets"
    else:
        margin = str(match["result"]) if pd.notna(match["result"]) else "Result unavailable"
    fmt = lambda r, w: f"{r}/{w}" if r is not None else "N/A"
    venue = str(match["venue"]) if pd.notna(match["venue"]) else "Venue unavailable"
    kpi_cards([
        (RED, "MATCH RESULT", winner, margin),
        (MINT, "FIRST INNINGS", fmt(r1, w1),
         f"{side[1]} · {w1 if w1 is not None else '—'} wkts lost"),
        (BLUE, "SECOND INNINGS", fmt(r2, w2),
         f"{side[2]} · {w2 if w2 is not None else '—'} wkts lost"),
    ])
    left, right = st.columns([2, 1], gap="medium")
    with left:
        with st.container(border=True):
            prog_view = chart_head("Innings Scoring Progression",
                                   f"{side[1]} vs {side[2]} · {venue} · over by over.", "mt_prog",
                                   ["Both innings", "First innings", "Second innings"])
            inn_cond, inn_params = inn_filter(prog_view)
            overs = query(f"""
                SELECT innings, over_number + 1 AS over, SUM(total_runs) AS runs FROM deliveries
                WHERE match_id = ? AND innings IN (1, 2) AND COALESCE(is_super_over, 0) = 0
                {inn_cond}
                GROUP BY innings, over_number ORDER BY over_number, innings
            """, (match_id,) + inn_params)
            overs["side"] = overs["innings"].map(side)
            chart(overs, "over", "runs", "mt_prog", kind="Line", color="side", height=340,
                  x_title="Over", y_title="Runs")
        with st.container(border=True):
            bound_view = chart_head("Fours and Sixes",
                                    "Boundaries from batter-run data, by innings.", "mt_bound",
                                    ["Both innings", "First innings", "Second innings"])
            b_cond, b_params = inn_filter(bound_view)
            bound = query(f"""
                SELECT innings,
                       SUM(CASE WHEN batter_runs = 4 THEN 1 ELSE 0 END) AS fours,
                       SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) AS sixes
                FROM deliveries WHERE match_id = ? AND innings IN (1, 2)
                  AND COALESCE(is_super_over, 0) = 0 {b_cond}
                GROUP BY innings ORDER BY innings
            """, (match_id,) + b_params)
            if not bound.empty:
                bound["side"] = bound["innings"].map(side)
                long = bound.melt(id_vars="side", value_vars=["fours", "sixes"],
                                  var_name="type", value_name="n")
                chart(long, "type", "n", "mt_bound", color="side", height=280,
                      x_title="", y_title="Count")
        with st.container(border=True):
            panel("Player Performance", "Runs, balls, boundaries and bowling — ★ is official POTM.")
            pom = str(match["player_of_match"]) if pd.notna(match["player_of_match"]) else ""
            players = query("""
                WITH bat AS (
                    SELECT batter AS p, SUM(batter_runs) AS runs,
                           SUM(CASE WHEN is_wide_ball = 0 THEN 1 ELSE 0 END) AS balls,
                           SUM(CASE WHEN batter_runs = 4 THEN 1 ELSE 0 END) AS fours,
                           SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) AS sixes
                    FROM deliveries WHERE match_id = ? AND innings IN (1, 2)
                      AND COALESCE(is_super_over, 0) = 0 GROUP BY batter
                ), bowl AS (
                    SELECT bowler AS p,
                           SUM(CASE WHEN is_wicket = 1 AND COALESCE(wicket_kind, '') NOT IN
                               ('run out', 'retired hurt', 'retired out', 'obstructing the field')
                               THEN 1 ELSE 0 END) AS wkts,
                           SUM(total_runs) AS conceded,
                           SUM(CASE WHEN is_wide_ball = 0 AND is_no_ball = 0 THEN 1 ELSE 0 END) AS balls
                    FROM deliveries WHERE match_id = ? AND innings IN (1, 2)
                      AND COALESCE(is_super_over, 0) = 0 GROUP BY bowler
                ), roster AS (SELECT p FROM bat UNION SELECT p FROM bowl)
                SELECT r.p AS player, COALESCE(b.runs, 0) AS runs, COALESCE(b.balls, 0) AS balls,
                       COALESCE(b.fours, 0) AS fours, COALESCE(b.sixes, 0) AS sixes,
                       COALESCE(w.wkts, 0) AS wkts, COALESCE(w.conceded, 0) AS conceded,
                       CASE WHEN COALESCE(w.balls, 0) > 0
                            THEN CAST(COALESCE(w.balls, 0) / 6 AS INTEGER) || '.' ||
                                 (COALESCE(w.balls, 0) % 6) ELSE '—' END AS overs
                FROM roster r LEFT JOIN bat b ON b.p = r.p LEFT JOIN bowl w ON w.p = r.p
                ORDER BY runs DESC, wkts DESC, player ASC
            """, (match_id, match_id))
            swiss_table(players, [("runs", "R"), ("balls", "B"), ("fours", "4s"), ("sixes", "6s"),
                                  ("wkts", "W"), ("overs", "Ov"), ("conceded", "Runs c.")], pom)
    with right:
        with st.container(border=True):
            phase_view = chart_head("Runs by Phase", "Powerplay 1–6 · middle 7–15 · death 16+.",
                                    "mt_phase", ["Both innings", "First innings", "Second innings"])
            p_cond, p_params = inn_filter(phase_view)
            phases = query(f"""
                SELECT innings,
                       CASE WHEN over_number <= 6 THEN 'Powerplay'
                            WHEN over_number <= 15 THEN 'Middle' ELSE 'Death' END AS phase,
                       SUM(total_runs) AS runs FROM deliveries
                WHERE match_id = ? AND innings IN (1, 2) AND COALESCE(is_super_over, 0) = 0
                {p_cond}
                GROUP BY innings, phase
                ORDER BY CASE phase WHEN 'Powerplay' THEN 1 WHEN 'Middle' THEN 2 ELSE 3 END,
                         innings
            """, (match_id,) + p_params)
            if not phases.empty:
                phases["side"] = phases["innings"].map(side)
                chart(phases, "phase", "runs", "mt_phase", color="side", height=240,
                      x_title="", y_title="Runs")
        with st.container(border=True):
            toss_view = chart_head("Toss Decision and Match Outcome",
                                   f"Season {f_season} context.", "mt_toss",
                                   ["Both outcomes", "Bat-first wins", "Chase wins"])
            toss = query("""
                SELECT COALESCE(toss_decision, 'Unknown') AS decision,
                       SUM(CASE WHEN COALESCE(win_by_runs, 0) > 0 THEN 1 ELSE 0 END) AS bat_wins,
                       SUM(CASE WHEN COALESCE(win_by_wickets, 0) > 0 THEN 1 ELSE 0 END) AS chase_wins
                FROM matches WHERE season = ? GROUP BY decision
            """, (f_season,))
            if not toss.empty:
                toss_long = toss.melt(id_vars="decision", value_vars=["bat_wins", "chase_wins"],
                                      var_name="outcome", value_name="n")
                toss_long["outcome"] = toss_long["outcome"].map(
                    {"bat_wins": "Bat-first wins", "chase_wins": "Chase wins"})
                if toss_view != "Both outcomes":
                    keep = {"Bat-first wins": ["Bat-first wins"],
                            "Chase wins": ["Chase wins"]}[toss_view]
                    toss_long = toss_long[toss_long["outcome"].isin(keep)]
                chart(toss_long, "decision", "n", "mt_toss", color="outcome", height=240,
                      x_title="Toss call", y_title="Matches")
            tw = str(match["toss_winner"]) if pd.notna(match["toss_winner"]) else "Unknown"
            td = str(match["toss_decision"]) if pd.notna(match["toss_decision"]) else "?"
            st.markdown(f'<div class="callout">This match: <b>{escape(tw)}</b> chose to '
                        f'<b>{escape(td)}</b>.</div>', unsafe_allow_html=True)
        with st.container(border=True):
            wk_view = chart_head("Wickets Lost by Over", "Dismissals per over, each innings.",
                                 "mt_wkts", ["Both innings", "First innings", "Second innings"])
            w_cond, w_params = inn_filter(wk_view)
            wkts = query(f"""
                SELECT innings, over_number + 1 AS over, COUNT(*) AS n FROM deliveries
                WHERE match_id = ? AND innings IN (1, 2) AND COALESCE(is_super_over, 0) = 0
                  AND is_wicket = 1 AND COALESCE(wicket_kind, '') NOT IN
                      ('retired hurt', 'obstructing the field', 'retired out')
                {w_cond}
                GROUP BY innings, over_number ORDER BY over_number
            """, (match_id,) + w_params)
            if not wkts.empty:
                wkts["side"] = wkts["innings"].map(side)
                chart(wkts, "over", "n", "mt_wkts", color="side", height=240,
                      x_title="Over", y_title="Wickets")
# ------------------------------------------------------------
def main():
    if not DB_PATH.exists():
        searched = "\n".join(f" - {p}" for p in _DB_CANDIDATES)
        st.error(f"Database not found. Looked in:\n{searched}")
        st.stop()
    if STADIUM_PATH.is_file():
        st.markdown(_stadium_css(STADIUM_PATH.stat().st_mtime), unsafe_allow_html=True)
    if "page" not in st.session_state:
        requested = st.query_params.get("page", "Overview")
        st.session_state["page"] = requested if requested in ("Overview", "Match") else "Overview"
    counts = {
        "matches": int(scalar("SELECT COUNT(DISTINCT match_id) FROM matches")),
        "balls": int(scalar("SELECT COUNT(*) FROM deliveries")),
        "seasons": int(scalar("SELECT COUNT(DISTINCT season) FROM matches WHERE season IS NOT NULL")),
        "teams": int(scalar("SELECT COUNT(*) FROM teams")),
        "players": int(scalar("SELECT COUNT(*) FROM players")),
    }
    if st.session_state.get("side_open", True):
        nav_col, main_col = st.columns([1.7, 5.3], gap="medium")
    else:
        nav_col, main_col = st.columns([0.25, 5.75], gap="medium")
    with nav_col:
        sidebar(st.session_state["page"], counts)
    with main_col:
        if st.session_state["page"] == "Overview":
            draw_overview()
        else:
            draw_match()
    st.markdown('<div class="footer">IPL Cricket Analytics · figures computed in SQLite '
                "from ball-by-ball data</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
