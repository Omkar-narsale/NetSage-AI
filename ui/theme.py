"""
NetSage AI Theme Loader (Phase 7 UI Redesign).
Injects ui/styles.css and Ctrl+K Command Palette JavaScript into Streamlit.
"""

import os
import streamlit as st
import streamlit.components.v1 as components


def load_theme():
    """Injects ui/styles.css into the current Streamlit app page."""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def inject_command_palette_script():
    """
    Injects lightweight JavaScript for Ctrl + K command palette search shortcut.
    """
    js_code = """
    <script>
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = parent.document.querySelector('input[type="text"]');
            if (searchInput) {
                searchInput.focus();
            } else {
                alert('NetSage AI Command Palette (Ctrl+K): Use sidebar filters or search input.');
            }
        }
    });
    </script>
    """
    components.html(js_code, height=0, width=0)
