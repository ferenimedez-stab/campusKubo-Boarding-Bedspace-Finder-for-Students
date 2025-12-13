# Code Documentation

## README with Quick Start

# campusKubo - Boarding Bedspace Finder for Students

A comprehensive web application built with Flet (Python) for connecting students with boarding house owners and property managers.

## Features

### Core Features
- **Role-based Authentication**: Admin, Property Manager, and Tenant roles
- **Property Listings**: Create and manage boarding house listings
- **Reservation System**: Book and manage reservations
- **Payment Processing**: Secure payment handling
- **Notifications**: Email and in-app notifications
- **Admin Dashboard**: Comprehensive analytics and management
- **Rating & Reviews**: User feedback system
- **Advanced Search**: Filter by price, location, amenities
- **Responsive Design**: Works on desktop and mobile
- **Security**: Secure authentication and data protection
- **Image Upload**: Property photo management

### Enhanced Features
- **Analytics**: Detailed reporting and insights


## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students.git
   cd campusKubo-Boarding-Bedspace-Finder-for-Students
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app/main.py
   ```

5. **Access the application**
   Open your browser to `http://localhost:8550`

## Project Structure

```
campusKubo/
├── app/
│   ├── main.py              # Application entry point
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   ├── views/               # UI components
│   ├── storage/             # Database and files
│   └── config/              # Configuration
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── requirements.txt         # Dependencies
```

## Usage

### For Students (Tenants)
1. Register as a tenant
2. Browse available properties
3. Make reservations
4. Manage bookings

### For Property Managers
1. Register and get approved
2. Create property listings
3. Manage reservations
4. Track earnings

### For Administrators
1. Manage users and approvals
2. Monitor system analytics
3. Generate reports
4. Configure system settings

## API Reference

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Property Endpoints
- `GET /properties` - List properties
- `POST /properties` - Create property
- `GET /properties/{id}` - Get property details
- `PUT /properties/{id}` - Update property

### Reservation Endpoints
- `GET /reservations` - List user reservations
- `POST /reservations` - Create reservation
- `PUT /reservations/{id}` - Update reservation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@campuskubo.com or create an issue on GitHub.

---

## Requirements

```
flet==0.21.2
bcrypt==4.1.2
python-dotenv==1.0.0
requests==2.31.0
pillow==10.1.0
```

## Inline Docstrings for Core Services

### AuthService (`app/services/auth_service.py`)

```python
class AuthService:
    """Handles user authentication for campusKubo"""

    ALLOWED_ROLES = ["tenant", "pm"]
    PASSWORD_MIN_LENGTH = 8

    PASSWORD_REQUIREMENTS = [
        ("length", lambda p, min_len=PASSWORD_MIN_LENGTH: len(p) >= min_len,
         f"At least {PASSWORD_MIN_LENGTH} characters"),
        ("digit", lambda p: any(c.isdigit() for c in p), "One number"),
        ("uppercase", lambda p: any(c.isupper() for c in p), "One uppercase letter"),
        ("special", lambda p: any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in p),
         "One special character"),
    ]

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.

        Args:
            email (str): Email address to validate

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Please enter a valid email address"
        return True, "Valid"

    def validate_password(self, password: str) -> Tuple[bool, str, list]:
        """
        Validate password meets security requirements.

        Args:
            password (str): Password to validate

        Returns:
            Tuple[bool, str, list]: (is_valid, message, requirements_status)
        """
        if not password:
            return False, "Password is required", []

        status = []
        for req_name, req_func, req_label in self.PASSWORD_REQUIREMENTS:
            is_met = req_func(password)
            status.append({
                "name": req_name,
                "label": req_label,
                "met": is_met
            })

        all_met = all(s["met"] for s in status)
        if not all_met:
            failed = [s["label"] for s in status if not s["met"]]
            return False, f"Password must have: {', '.join(failed)}", status

        return True, "Password is valid", status

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password (str): Plain text password

        Returns:
            str: Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password (str): Plain text password
            hashed (str): Hashed password

        Returns:
            bool: True if password matches
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### UserService (`app/services/user_service.py`)

```python
class UserService:
    """Handles user-related operations"""

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id (int): User ID to retrieve

        Returns:
            Optional[User]: User object or None
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, email, full_name, role FROM users WHERE id = ?",
            (user_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return User.from_db_row(row)

        return None

    @staticmethod
    def get_user_full(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Return the full DB row for a user as a dict.

        Args:
            user_id (int): User ID to retrieve

        Returns:
            Optional[Dict[str, Any]]: User data dictionary or None
        """
        return db_get_user_by_id(user_id)

    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> bool:
        """
        Update user profile information.

        Args:
            user_id (int): User ID to update
            **kwargs: Profile fields to update

        Returns:
            bool: True if update successful
        """
        return db_update_user_profile(user_id, **kwargs)
```

### ListingService (`app/services/listing_service.py`)

```python
class ListingService:
    """Handles property listing operations"""

    @staticmethod
    def get_all_listings(owner_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all listings, optionally filtered by owner.

        Args:
            owner_id (Optional[int]): Filter by owner ID

        Returns:
            List[Dict[str, Any]]: List of listing dictionaries
        """
        return db_get_all_listings(owner_id)

    @staticmethod
    def create_listing(owner_id: int, **listing_data) -> Optional[int]:
        """
        Create a new property listing.

        Args:
            owner_id (int): Owner user ID
            **listing_data: Listing information

        Returns:
            Optional[int]: New listing ID or None
        """
        return db_create_listing(owner_id, **listing_data)

    @staticmethod
    def update_listing(listing_id: int, **updates) -> bool:
        """
        Update listing information.

        Args:
            listing_id (int): Listing ID to update
            **updates: Fields to update

        Returns:
            bool: True if update successful
        """
        return db_update_listing(listing_id, **updates)

    @staticmethod
    def check_availability(listing_id: int, start_date: str, end_date: str) -> bool:
        """
        Check if a listing is available for the given dates.

        Args:
            listing_id (int): Listing ID to check
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)

        Returns:
            bool: True if available
        """
        # Implementation checks for conflicting reservations
        return True  # Placeholder
```

### ReservationService (`app/services/reservation_service.py`)

```python
class ReservationService:
    """Handles reservation operations"""

    @staticmethod
    def create_reservation(tenant_id: int, listing_id: int,
                          start_date: str, end_date: str) -> Optional[int]:
        """
        Create a new reservation.

        Args:
            tenant_id (int): Tenant user ID
            listing_id (int): Listing ID
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)

        Returns:
            Optional[int]: New reservation ID or None
        """
        return db_create_reservation(tenant_id, listing_id, start_date, end_date)

    @staticmethod
    def get_reservations_for_user(user_id: int) -> List[Dict[str, Any]]:
        """
        Get all reservations for a user.

        Args:
            user_id (int): User ID

        Returns:
            List[Dict[str, Any]]: List of reservation dictionaries
        """
        return db_get_reservations_for_user(user_id)

    @staticmethod
    def update_reservation_status(reservation_id: int, status: str) -> bool:
        """
        Update reservation status.

        Args:
            reservation_id (int): Reservation ID
            status (str): New status

        Returns:
            bool: True if update successful
        """
        return db_update_reservation_status(reservation_id, status)
```

### AdminService (`app/services/admin_service.py`)

```python
class AdminService:
    """Handles administrative operations"""

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        return {
            'total_tenants': db_get_user_count_by_role('tenant'),
            'total_pms': db_get_user_count_by_role('pm'),
            'total_listings': db_get_listing_count(),
            'approved_listings': db_get_listing_count(status='approved'),
            'pending_listings': db_get_listing_count(status='pending'),
            'total_reservations': db_get_reservation_count(),
            'total_reports': db_get_report_count(),
            'total_payments': db_get_payment_total()
        }

    @staticmethod
    def get_pending_pm_count() -> int:
        """
        Get count of pending PM verifications.

        Returns:
            int: Number of pending PMs
        """
        return db_get_pending_pm_count()

    @staticmethod
    def approve_pm(pm_id: int) -> bool:
        """
        Approve a property manager.

        Args:
            pm_id (int): PM user ID

        Returns:
            bool: True if approval successful
        """
        return db_update_user_role(pm_id, 'pm')

    @staticmethod
    def compute_trend(current: float, previous: float) -> Tuple[float, bool]:
        """
        Compute trend percentage and direction.

        Args:
            current (float): Current value
            previous (float): Previous value

        Returns:
            Tuple[float, bool]: (percentage_change, is_increasing)
        """
        if previous == 0:
            return (0.0, current > 0)
        trend = ((current - previous) / previous) * 100
        return (round(trend, 1), trend >= 0)
```