"""
Playwright UI tests for Disaster Dash 
===========================================
Covers three distinct behaviours:
  1. Filter behaviour => selecting all countries updates the filter strip
  2. Edge case        => deselecting all disaster types shows "None"
  3. Aggregation      => changing the bar-chart statistic is reflected in the strip

Run (app must already be running on port 8000):
    pytest tests/test_playwright.py --headed    # watch it in the browser
    pytest tests/test_playwright.py             # headless
"""

import os
import pytest
from playwright.sync_api import Page, expect

APP_URL = os.getenv("APP_URL", "http://localhost:8000")
TIMEOUT = 10_000  # ms – time for Shiny reactive outputs to settle


@pytest.fixture()
def dash(page: Page):
    """Load the dashboard and wait for the filter strip to render with content."""
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(APP_URL)
    page.wait_for_selector("#page-header", timeout=TIMEOUT)
    # Wait until Shiny's reactive graph has rendered the filter strip with content
    page.wait_for_function(
        "document.querySelector('#filter-strip') && document.querySelector('#filter-strip').innerText.trim().length > 0",
        timeout=TIMEOUT,
    )
    return page


# ── Test 1: Filter behaviour ──────────────────────────────────────────────────
def test_select_all_countries_updates_filter_strip(dash: Page):
    """
    Clicking '✓ All' for countries should cause the filter strip to display
    'All Countries' instead of the default three-country selection.
    """
    dash.locator("#sel_all_c").click()
    # Give Shiny's reactive graph time to process the button event
    dash.wait_for_timeout(2_000)
    strip = dash.locator("#filter-strip")
    expect(strip).to_contain_text("All Countries", timeout=TIMEOUT)


# ── Test 2: Edge case ─────────────────────────────────────────────────────────
def test_deselect_all_disaster_types_shows_none(dash: Page):
    """
    Clicking '✕ None' for disaster types should cause the filter strip to
    display 'None' under the Disasters label — an empty-selection edge case.
    """
    dash.locator("#desel_all_d").click()
    dash.wait_for_timeout(2_000)
    strip = dash.locator("#filter-strip")
    expect(strip).to_contain_text("None", timeout=TIMEOUT)


# ── Test 3: Aggregation correctness ──────────────────────────────────────────
def test_changing_summary_stat_updates_filter_strip(dash: Page):
    """
    Switching the Bar Chart Statistic from 'Total Sum' to 'Average' should be
    immediately reflected in the active-filter strip, confirming the reactive
    aggregation input is wired up correctly.
    """
    select = dash.locator("#summary_stat")
    select.select_option("mean")
    # Explicitly fire a change event in case Shiny's listener needs it
    select.dispatch_event("change")
    dash.wait_for_timeout(2_000)
    strip = dash.locator("#filter-strip")
    expect(strip).to_contain_text("Average", timeout=TIMEOUT)