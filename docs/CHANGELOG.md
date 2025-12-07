# CampusKubo - Changelog

All notable changes to this project will be documented in this file.

---

## [0.3.0] - 2025-12-06 (Enimedez)

### Added
- **Database Module** (`storage/db.py`)
  - Complete SQLite database implementation with migrations
  - User management with secure password hashing
  - User profile updates with email validation
  - Listing management (CRUD operations)
  - Reservation system
  - Password reset tokens
  - Activity logging
  - Reports management
  - Admin utilities
  - Model-compatible adapter functions
  - Foreign key constraints and data integrity

- **Documentation**
  - `docs/CHANGELOG.md` - Version tracking and team contribution guide
  - Simplified versioning format for student team collaboration

### Changed
- **README.md** - Updated with project information and setup instructions

---

## [0.2.0] - 2025-12-02 (Enimedez)

### Added
- **Python Module Placeholders**
  - `.py` placeholder files added to all project folders:
    - **Components (9)**: footer, listing_card, login_form, navbar, notification_banner, reservation_form, search_filter, searchbar, signup_form
    - **Models (4)**: listing, notification, reservation, user
    - **Services (6)**: auth_service, gmaps_service, listing_service, notification_service, reservation_service, user_service
    - **State (2)**: app_state, session_state
    - **Storage (3)**: db, file_storage, seed_data
    - **Views (10)**: admin_dashboard_view, home_view, listing_detail_view, login_view, pm_dashboard_view, pm_profile_view, reservation_view, signup_view, user_profile_view
    - Organized modularity structure for scalable development

---

## [0.1.0] - 2025-12-01 (Enimedez)

### Added
- **Project Structure**
  - Folder structure setup for organized modularity
  - Placeholder `.py` files in all core directories:
    - `app/` - Main application
    - `app/views/` - View/page components
    - `app/components/` - Reusable UI components
    - `app/services/` - Business logic services
    - `app/models/` - Data models
    - `app/state/` - State management
    - `app/storage/` - Data persistence
    - `app/tests/` - Test suite
  - Root configuration files:
    - `README.md` - Project documentation
    - `requirements.txt` - Python dependencies
    - `.gitignore` - Git ignore rules

---

## Version Format

Simple versioning for team project:
- **0.1.0** - First major feature release
- **0.1.1** - Bug fixes and small improvements
- **0.2.0** - Next major feature added
- **0.2.1** - More bug fixes
- And so on...

### Categories

- **Added** - New features and functionality
- **Changed** - Changes in existing functionality
- **Fixed** - Bug fixes and corrections
- **Removed** - Removed features or functionality
- **Deprecated** - Features that will be removed in future versions
- **Security** - Security-related fixes or changes

---

## How to Update This Changelog

When making new commits or releases:

1. **Create a new version section** with date in `YYYY-MM-DD` format
2. **Include your name** in the version line (e.g., `[0.2.1] - 2025-12-10 (YourName)`)
3. **Organize by categories**: Added, Changed, Fixed, Removed
4. **Be specific**: Include file paths and descriptions
5. **Use format**: `[0.X.Y] - YYYY-MM-DD (Developer Name)`

### Example Entry Format

```markdown
## [0.2.1] - 2025-12-10 (TeamMemberName)

### Added
- New search filter functionality (`views/search_view.py`)
- Price range filtering for listings
- Location-based search

### Changed
- Updated listing card styling
- Improved search performance

### Fixed
- Search result pagination issue
- Filter validation bug

### Removed
- Legacy search implementation
```

---

**Last Updated**: December 6, 2025
**Repository**: [campusKubo-Boarding-Bedspace-Finder-for-Students](https://github.com/ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students)
