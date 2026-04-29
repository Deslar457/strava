import streamlit as st
import time
from datetime import date, datetime

from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.plan_loader import (
    get_current_plan, get_todays_session, get_week_summary, SESSION_COLOURS
)
from utils.visualisations import (
    plot_monthly_distance,
    plot_progression,
    plot_pace_vs_hr,
    plot_fitness_freshness,
    plot_long_run_progression,
    plot_pace_zones,
    calculate_workloads,
    get_personal_records,
    get_form_status,
    get_ctl_delta,
    predict_race_times,
    predict_10k_rf,
    estimate_threshold_hr,
    format_time,
)

# ── Colour maps ───────────────────────────────────────────────────────────────
FORM_COLOURS = {
    "green": "#2ecc71",
    "amber": "#f39c12",
    "red":   "#e74c3c"
}

SESSION_BADGE_COLOURS = {
    "Threshold": ("🟠", "#E65100"),
    "Intervals":  ("🔴", "#B71C1C"),
    "Easy":       ("🟢", "#2E7D32"),
    "Long":       ("🔵", "#0D47A1"),
    "Race Pace":  ("🟣", "#4A148C"),
    "Rest":       ("⚪", "#9E9E9E"),
}


def session_badge(session_type):
    emoji, _ = SESSION_BADGE_COLOURS.get(session_type, ("⚪", "#9E9E9E"))
    return emoji


def divider(label):
    st.markdown(f"### {label}")
    st.markdown("---")


@st.cache_data(ttl=300)
def load_data():
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
    activities = fetch_activities(access_token, start_date)
    return activities


def main():
    st.set_page_config(
        page_title="Derrick Running Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
        <div style='padding: 8px 0 4px 0'>
            <span style='font-size:0.85em; color:#888; letter-spacing:2px; text-transform:uppercase'>
                Running Dashboard
            </span><br>
            <span style='font-size:2em; font-weight:700'>Running Dashboard</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    with st.spinner("Loading Strava data..."):
        activities = load_data()

    if not activities:
        st.warning("No activities found. Check your Strava connection.")
        return

    df = process_activities(activities)

    # ── Pre-compute shared values ─────────────────────────────────────────────
    _, lthr = estimate_threshold_hr(df)
    form = get_form_status(df)
    acute, chronic, acwr = calculate_workloads(df)
    ctl_delta = get_ctl_delta(df, days=28)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Form Banner
    # ═══════════════════════════════════════════════════════════════════════════
    colour = FORM_COLOURS[form["colour"]]
    delta_str = f"CTL {'+' if ctl_delta and ctl_delta > 0 else ''}{ctl_delta} vs 4 weeks ago" if ctl_delta else ""
    st.markdown(
        f"""
        <div style="background-color:{colour}22; border-left:4px solid {colour};
             padding:12px 16px; border-radius:6px; margin:12px 0 20px 0;">
            <strong style="color:{colour}; font-size:1.1em">{form['status']}</strong>
            &nbsp;·&nbsp; {form['advice']}
            &nbsp;·&nbsp; TSB: <strong>{form['TSB']}</strong>
            &nbsp;·&nbsp; CTL: <strong>{form['CTL']}</strong>
            &nbsp;·&nbsp; ATL: <strong>{form['ATL']}</strong>
            {'&nbsp;·&nbsp; <em>' + delta_str + '</em>' if delta_str else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Load Metrics
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Training Load")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Acute Load (7d)", f"{acute:.1f} km")
    c2.metric("Chronic Load (28d)", f"{chronic:.1f} km")
    acwr_delta = "⚠️ Injury risk" if acwr > 1.5 else ("✅ Optimal" if acwr <= 1.3 else "")
    c3.metric("ACWR", f"{acwr:.2f}", delta=acwr_delta,
              help="Acute:Chronic Workload Ratio. 1.0–1.3 optimal. >1.5 elevated injury risk.")
    c4.metric("LTHR (estimated)", f"{lthr} bpm" if lthr else "—",
              help="Estimated from hardest sustained efforts ≥6km, ≥25min, top 15% HR.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Today's Session + This Week
    # ═══════════════════════════════════════════════════════════════════════════
    plan = get_current_plan()

    st.markdown("### Training Plan")

    if plan:
        today = date.today()
        week_data, days = get_week_summary(plan, today) or (None, None)
        _, todays_session = get_todays_session(plan, today)

        col_today, col_week = st.columns([1, 2])

        with col_today:
            st.markdown(f"**{plan['month']} — {plan['phase']}**")
            st.caption(plan.get("goal", ""))
            if todays_session:
                emoji = session_badge(todays_session["type"])
                st.markdown(
                    f"""
                    <div style='border:1px solid #ddd; border-radius:8px; padding:14px; margin-top:8px'>
                        <div style='font-size:0.75em; color:#888; text-transform:uppercase; letter-spacing:1px'>
                            Today — {today.strftime("%A %d %b")}
                        </div>
                        <div style='font-size:1.3em; font-weight:700; margin:4px 0'>
                            {emoji} {todays_session['type']} — {todays_session['distance']}k
                        </div>
                        <div style='font-size:0.9em; color:#555'>
                            {todays_session['detail']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='border:1px solid #ddd; border-radius:8px; padding:14px; margin-top:8px'>
                        <div style='font-size:0.75em; color:#888; text-transform:uppercase; letter-spacing:1px'>
                            Today — {today.strftime("%A %d %b")}
                        </div>
                        <div style='font-size:1.2em; font-weight:600; margin:4px 0; color:#888'>
                            ⚪ Rest Day
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_week:
            if week_data and days:
                planned_km = week_data["total"]

                # Actual km this week from Strava
                week_start = datetime.strptime(week_data["start"], "%Y-%m-%d")
                actual_km = df[df["Date"] >= week_start]["Distance (km)"].sum()

                st.markdown(f"**Week {week_data['week']} — Planned: {planned_km}k · Actual so far: {actual_km:.1f}k**")

                # Progress bar
                pct = min(actual_km / planned_km, 1.0) if planned_km > 0 else 0
                bar_colour = "#2ecc71" if pct >= 1.0 else "#f39c12" if pct >= 0.5 else "#e74c3c"
                st.markdown(
                    f"""
                    <div style='background:#eee; border-radius:4px; height:8px; margin:6px 0 12px 0'>
                        <div style='background:{bar_colour}; width:{pct*100:.0f}%; height:8px; border-radius:4px'></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                for day_info in days:
                    s = day_info["session"]
                    is_today = day_info["is_today"]
                    day_label = day_info["date"].strftime("%a %d")
                    bold = "font-weight:700" if is_today else ""
                    prefix = "👉 " if is_today else "&nbsp;&nbsp;&nbsp;&nbsp;"

                    if s:
                        emoji = session_badge(s["type"])
                        line = f"{prefix}<span style='{bold}'>{day_label}: {emoji} {s['type']} — {s['distance']}k</span>"
                    else:
                        line = f"{prefix}<span style='{bold}; color:#aaa'>{day_label}: Rest</span>"

                    st.markdown(f"<div style='margin:2px 0'>{line}</div>", unsafe_allow_html=True)
    else:
        st.info("No plan loaded for this month. Add a plan file to the `plans/` folder.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Fitness & Freshness
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Fitness & Freshness")
    st.caption("CTL = fitness (42-day load). ATL = fatigue (7-day load). TSB = form (CTL − ATL). LTHR dynamically estimated from your data.")
    st.pyplot(plot_fitness_freshness(df))

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Pace Zone Distribution
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Effort Zone Distribution")
    st.caption("Monthly volume split by effort zone. Easy = >4:45/km · Moderate/Threshold = 4:17–4:45/km · Hard = <4:17/km")
    threshold_pace = 4.417
    fig_zones = plot_pace_zones(df, threshold_pace=threshold_pace)
    if fig_zones:
        st.pyplot(fig_zones)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — LTHR Detail
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Lactate Threshold HR")
    st.caption("Estimated from hardest sustained efforts (≥6km, ≥25min, top 15% HR). True LTHR requires a lab test.")

    top5, lthr_val = estimate_threshold_hr(df)
    if lthr_val:
        col_lt1, col_lt2 = st.columns([1, 3])
        with col_lt1:
            st.metric("Estimated LTHR", f"{lthr_val} bpm")
            st.caption("Used in TSS / CTL / ATL calculations above")
        with col_lt2:
            st.dataframe(top5, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough qualifying runs to estimate LTHR yet.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Personal Records
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Personal Records")
    prs = get_personal_records(df)
    if prs is not None:
        st.dataframe(prs, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough data for personal records yet.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 8 — Race Predictions
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Race Time Predictions")
    col_rf, col_riegel = st.columns(2)

    with col_rf:
        st.markdown("**Random Forest — 10K**")
        st.caption("Trained on your actual 10K efforts. Needs 5+ runs. Reflects current fitness, not peak.")
        result = predict_10k_rf(df)
        if isinstance(result, dict):
            st.metric("Predicted 10K", result["Predicted Time"])
            st.caption(f"MAE ±{result['MAE (±min)']} min · {result['Training Runs']} training runs")
            if result.get("Below PB"):
                st.warning(
                    f"⚠️ Prediction ({result['Predicted Time']}) is slower than your PB ({result['PB']}). "
                    f"This reflects current training load, not your ceiling."
                )
        else:
            st.warning(result[1] if isinstance(result, tuple) else result)

    with col_riegel:
        st.markdown("**Riegel Formula — All Distances**")
        st.caption("Projected from recent pace/HR efficiency (last 8 weeks). Lower than PB = current fitness is below peak.")
        preds = predict_race_times(df)
        if preds:
            for dist, t in preds.items():
                st.metric(dist, t)
        else:
            st.warning("Not enough recent data for predictions.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 9 — Volume Charts
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Monthly Distance")
    st.pyplot(plot_monthly_distance(df))

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 10 — Long Run Progression
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Long Run Progression")
    st.caption("All runs ≥10km. Distance bars, pace line. Your most important session for half marathon prep.")
    fig_lr = plot_long_run_progression(df)
    if fig_lr:
        st.pyplot(fig_lr)
    else:
        st.info("No long runs (≥10km) found yet.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 11 — Drill-Down Charts
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Distance Drill-Down")
    col_prog, col_hr = st.columns(2)

    with col_prog:
        st.markdown("**Progression**")
        d = st.selectbox("Distance (km)", [5, 6, 7, 10], key="prog_dist")
        fig = plot_progression(df, d - 0.1, d + 0.1)
        if fig:
            st.pyplot(fig)
        else:
            st.info(f"No runs found near {d}km.")

    with col_hr:
        st.markdown("**Pace vs Heart Rate**")
        d_hr = st.selectbox("Distance (km)", [5, 6, 7, 8, 10], key="hr_dist")
        fig_hr = plot_pace_vs_hr(df, d_hr - 0.1, d_hr + 0.1)
        if fig_hr:
            st.pyplot(fig_hr)
        else:
            st.info(f"No runs found near {d_hr}km.")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#aaa; font-size:0.8em'>"
        "Derrick Running Dashboard · "
        f"Last updated {datetime.now().strftime('%d %b %Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
