import sys
import os
from datetime import date, datetime, timedelta
import importlib
 
# Ensure the project root is on the path so `plans/` is always findable
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
 
 
def load_plan(month_key: str):
    """Load a plan by key e.g. 'may_2026'. Returns PLAN dict or None."""
    try:
        module = importlib.import_module(f"plans.{month_key}")
        return module.PLAN
    except (ModuleNotFoundError, AttributeError):
        return None
 
 
def get_current_plan():
    """Auto-detect which plan to load based on today's date."""
    today = date.today()
    key = today.strftime("%b_%Y").lower()
    plan = load_plan(key)
    if plan:
        return plan
    # Fallback — try previous month (e.g. if we're in early May, April plan still relevant)
    prev = (today.replace(day=1) - timedelta(days=1))
    fallback_key = prev.strftime("%b_%Y").lower()
    return load_plan(fallback_key)
 
 
def get_week_for_date(plan, target_date=None):
    """Return the week dict from a plan that contains target_date."""
    if target_date is None:
        target_date = date.today()
    for week in plan["weeks"]:
        start = datetime.strptime(week["start"], "%Y-%m-%d").date()
        end = start + timedelta(days=6)
        if start <= target_date <= end:
            return week
    return None
 
 
def get_todays_session(plan, target_date=None):
    """Return today's session dict or None if rest day."""
    if target_date is None:
        target_date = date.today()
    week = get_week_for_date(plan, target_date)
    if not week:
        return None, None
    day_name = target_date.strftime("%A")
    session = week["sessions"].get(day_name)
    return week, session
 
 
def get_week_summary(plan, target_date=None):
    """Return all sessions for the current week with day labels."""
    if target_date is None:
        target_date = date.today()
    week = get_week_for_date(plan, target_date)
    if not week:
        return None
    start = datetime.strptime(week["start"], "%Y-%m-%d").date()
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        day_name = d.strftime("%A")
        session = week["sessions"].get(day_name)
        days.append({
            "date": d,
            "day": day_name,
            "session": session,
            "is_today": d == target_date,
        })
    return week, days
 
 
SESSION_COLOURS = {
    "Threshold": "#E65100",
    "Intervals":  "#B71C1C",
    "Easy":       "#2E7D32",
    "Long":       "#0D47A1",
    "Race Pace":  "#4A148C",
    "Rest":       "#9E9E9E",
}