# campusKubo - Boarding & Bedspace Finder for Students

A cross-platform application built with Flet that connects students seeking affordable accommodations with property managers offering boarding houses, bedspaces, and apartments within the Rinconada area.

---

## 📋 Overview

**campusKubo** helps students find and reserve accommodations while enabling property managers to list and manage their properties efficiently.

### For Tenants
- Search and filter available boarding houses and bedspaces by price, amenities, location, and availability
- View detailed property information, images, and availability status
- Reserve rooms with real-time notifications for confirmation and updates
- (Optional) Pay via GCash/PayMaya
- (Optional) Leave reviews and ratings

### For Property Managers
- Add, edit, or delete listings
- Upload property images and set amenities
- Update availability status (Available, Reserved, Occupied)
- Manage tenant reservations

### For Admins
- Approve or reject listings before publication
- Manage users (Tenants and Property Managers)
- Generate summary reports

---

## ✨ Features

### Core Features
- **Secure Authentication**: Register and login with email/password
- **Guest Browsing**: View listings without signing in
- **Advanced Search & Filtering**: Filter by price, amenities, room type, location, and availability
- **Reservation System**: Book rooms with automatic availability updates
- **Real-time Notifications**: Get updates on reservations, payments, and rent reminders
- **Property Manager Verification**: Ensure trusted listings through document verification
- **Admin Dashboard**: Comprehensive user and listing management

### Optional Features
- Payment integration (GCash, PayMaya)
- Reviews and ratings system
- In-app messaging between tenants and property managers
- Google Maps integration for property location
- Google Calendar sync for rent reminders
- Reporting system for suspicious activities

---

## 🏗️ Technology Stack

- **Framework**: Flet (Python + Flutter rendering)
- **Language**: Python 3.11+
- **Database**: SQL-based (MySQL/PostgreSQL)
- **Target Platforms**: Desktop, Web, Mobile (Android/iOS)
- **APIs**: Google Maps API, Google Calendar API (optional)
- **Payment**: GCash, PayMaya integration (optional)

---

## 📁 Project Structure

```
campusKubo/
├── app/
│   ├── main.py              # Entry point of the application
│   ├── views/               # Page and view components
│   ├── components/          # Reusable widgets and UI elements
│   ├── services/            # Data access, APIs, emerging tech integration
│   ├── models/              # Data classes and DTOs
│   ├── state/               # State management controllers
│   ├── storage/             # Persistence helpers (SQLite, JSON, etc.)
│   ├── tests/               # Unit and integration tests
│   └── assets/              # Images, icons, and static assets
├── docs/                    # Documentation, ERD, architecture diagrams
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students.git
   cd campusKubo-Boarding-Bedspace-Finder-for-Students
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to app folder and run**
   ```bash
   cd app
   python main.py
   ```

The application will launch in your default browser or as a desktop app depending on your platform configuration.

---

## 🤝 How to Contribute

To keep our `main` branch stable and organized, please follow this Git workflow:

### 1. Fork the Repository
Click the **Fork** button at the top-right of this repository to create your own copy.

### 2. Clone Your Fork
```bash
git clone https://github.com/<your-username>/campusKubo-Boarding-Bedspace-Finder-for-Students.git
cd campusKubo-Boarding-Bedspace-Finder-for-Students
```

### 3. Add Upstream Remote
```bash
git remote add upstream https://github.com/ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students.git
```

### 4. Create a Feature Branch
Always create a new branch for each feature or fix:
```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - for new features (e.g., `feature/search-filter`)
- `fix/` - for bug fixes (e.g., `fix/login-error`)
- `docs/` - for documentation (e.g., `docs/update-readme`)

### 5. Make Your Changes
- Implement your feature, bug fix, or documentation update
- Write clear, descriptive commit messages
- Test your changes before committing

### 6. Commit Your Changes
```bash
git add .
git commit -m "Add search filter by price feature"
```

### 7. Keep Your Branch Updated
Before pushing, sync with upstream:
```bash
git fetch upstream
git rebase upstream/main
```

### 8. Push Your Branch
```bash
git push origin feature/your-feature-name
```

### 9. Open a Pull Request
1. Go to your fork on GitHub
2. Click **New Pull Request**
3. Set base repository to `ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students.git`
4. Set base branch to `main` and compare branch to your feature branch
5. Add a clear title and description of your changes
6. Submit the PR

### 10. Review & Merge
- Team members will review your PR
- Address any requested changes
- Once approved, it will be merged into `main`

### 🔑 Important Notes
- **Never push directly to `main`**
- Keep your fork synced regularly:
```bash
git remote add upstream https://github.com/ferenimedez-stab/campusKubo-Boarding-Bedspace-Finder-for-Students.git
git checkout main
git pull upstream main
git push origin main
```
- Write meaningful commit messages
- Test your code before creating a PR
- Follow the existing code style and structure

---

## 🧪 Testing

Run tests using:
```bash
cd app
python -m pytest tests/
```

Minimum testing requirements:
- At least 3 unit tests for core logic
- At least 2 functional/integration tests
- Manual exploratory test checklist in documentation

---

## 📚 Documentation

Detailed documentation can be found in the `/docs` folder:
- Software Requirements Specification (SRS)
- Architecture diagrams
- Data model (ERD)
- API documentation
- Testing strategy
- Team roles and contribution matrix

---

## 👥 Team

**BoardGirls Team**
- Product Lead / Vision & Feature Prioritization
- UI/UX & Accessibility Designer
- Lead Developer (Flet Architecture)
- Data & Integration Engineer
- QA / Test Coordinator
- Documentation & Release Manager

---

## 📄 License

This project is developed for academic purposes as part of CCCS 106 (Application Development and Emerging Technologies) and CS 3110 (Software Engineering) joint collaboration.

---

## 🙏 Acknowledgements

- Developed by **BoardGirls** team
- Built with [Flet Framework](https://flet.dev/)
- Inspired by student accommodation platforms
- Special thanks to our instructors and collaborators

---

## 📞 Support

For questions or issues:
1. Check existing issues in the repository
2. Create a new issue with a clear description
3. Contact the team through the course channels

---

**Last Updated**: December 7, 2025

**Version**: v2.6.0