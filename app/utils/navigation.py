def go_home(page):
    """Navigate to a role-aware home route without clearing session."""
    role = page.session.get("role") if hasattr(page, "session") else None
    if role == "admin":
        page.go("/admin")
    elif role == "pm":
        page.go("/pm")
    elif role == "tenant":
        page.go("/tenant")
    else:
        page.go("/")
