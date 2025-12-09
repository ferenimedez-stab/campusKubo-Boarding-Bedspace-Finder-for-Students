"""Reusable CampusKubo logo component."""

import flet as ft


def Logo(size: int = 22, color: str | None = None, with_icon: bool = False, subtitle: str | None = None) -> ft.Control:
    """Return a logo control used across the app.

    - `size`: base text size for the brand name
    - `color`: text color (defaults to a dark color)
    - `with_icon`: when True, include a home icon and a two-line layout (brand + subtitle)
    - `subtitle`: optional smaller text shown under the brand (used in dashboard header)
    """
    color = color or "#1A1A1A"

    if with_icon:
        column_controls = [ft.Text("CampusKubo", size=size, weight=ft.FontWeight.BOLD, color=color)]
        if subtitle:
            column_controls.append(ft.Text(subtitle, size=max(12, int(size * 0.55)), color=ft.Colors.BLACK))

        return ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.HOME, size=int(size * 1.2), color="#0078FF"),
                ft.Column(spacing=0, controls=column_controls),
            ],
        )

    # Default: single-line textual logo, preserving the house emoji used on home pages
    return ft.Text(" C🏠mpusKubo", size=size, weight=ft.FontWeight.BOLD, color=color)
