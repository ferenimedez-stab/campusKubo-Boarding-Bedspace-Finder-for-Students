# app/components/admin_stats_card.py
import flet as ft


class AdminStatsCard:
    def __init__(self, title, value, icon=None, trend_value=None, trend_up=True, color="#0078FF", on_click=None, width: int = 220, height: int = 140):
        """Reusable admin KPI card.

        Args:
            title (str): Card title.
            value (int|str): Main numeric value to display.
            icon (ft.Icon | any): Either an `ft.Icon` instance or an Icons enum to render.
            trend_value (int|None): Optional percentage to show as trend.
            trend_up (bool): True if trend is positive (up arrow), False for down.
            color (str): Primary color for icon/background (hex or named).
            on_click (callable|None): Optional tap handler.
            width (int): Card width in pixels.
            height (int): Card height in pixels.
        """
        self.title = title
        self.value = value
        self.icon = icon
        self.trend_value = trend_value
        self.trend_up = trend_up
        self.color = color
        self.on_click = on_click
        self.width = width
        self.height = height

    def _build_icon(self):
        # Accept either an ft.Icon or an icon constant
        if isinstance(self.icon, ft.Icon):
            ic = self.icon
        else:
            try:
                ic = ft.Icon(self.icon if self.icon is not None else ft.Icons.INFO, size=24, color=self.color)
            except Exception:
                ic = ft.Icon(ft.Icons.INFO, size=24, color=self.color)

        return ft.Container(
            bgcolor=f"{self.color}15",
            padding=10,
            border_radius=8,
            content=ic
        )

    def build(self):
        trend_row = ft.Row(spacing=6, controls=[])
        if self.trend_value is not None:
            trend_icon = ft.Icons.TRENDING_UP if self.trend_up else ft.Icons.TRENDING_DOWN
            trend_color = "#4CAF50" if self.trend_up else "#F44336"
            trend_row.controls.extend([
                ft.Icon(trend_icon, size=16, color=trend_color),
                ft.Text(f"{self.trend_value}%", size=12, color=trend_color)
            ])

        # Top row: title and chevron
        right_row = ft.Row(controls=[ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=ft.Colors.GREY)])

        content = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(controls=[self._build_icon(), ft.Container(width=8), ft.Column(controls=[ft.Text(self.title, size=13, color=ft.Colors.BLACK)])]),
                        right_row,
                    ]
                ),
                ft.Text(str(self.value), size=28, weight=ft.FontWeight.BOLD, color="#1a1a2e"),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(""), trend_row])
            ]
        )

        inner = ft.Container(
            bgcolor="white",
            padding=20,
            width=self.width,
            height=self.height,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#00000015"),
            border=ft.border.all(1, "#E0E0E0"),
            content=content,
        )

        if self.on_click:
            return ft.GestureDetector(content=inner, on_tap=self.on_click, mouse_cursor=ft.MouseCursor.CLICK)

        return inner

