# ============================================================
# S. F WORKS
# DEFAULT MARKETPLACE CATEGORIES
# ============================================================

from extensions import db
from models.category import Category


DEFAULT_CATEGORIES = [

    {
        "name": "Electrician",
        "slug": "electrician",
        "description": "Electrical installation, repair and maintenance services.",
        "icon": "⚡"
    },

    {
        "name": "Plumber",
        "slug": "plumber",
        "description": "Plumbing, pipe repair, water and drainage services.",
        "icon": "🔧"
    },

    {
        "name": "Carpenter",
        "slug": "carpenter",
        "description": "Furniture, woodwork, doors and carpentry services.",
        "icon": "🪚"
    },

    {
        "name": "Painter",
        "slug": "painter",
        "description": "Interior, exterior and decorative painting services.",
        "icon": "🎨"
    },

    {
        "name": "Cleaning",
        "slug": "cleaning",
        "description": "Home, office, deep cleaning and housekeeping services.",
        "icon": "🧹"
    },

    {
        "name": "AC Repair & Service",
        "slug": "ac-repair-service",
        "description": "Air conditioner repair, installation and maintenance.",
        "icon": "❄️"
    },

    {
        "name": "Appliance Repair",
        "slug": "appliance-repair",
        "description": "Repair and maintenance of household appliances.",
        "icon": "🔌"
    },

    {
        "name": "Construction",
        "slug": "construction",
        "description": "Construction, renovation and building services.",
        "icon": "🏗️"
    },

    {
        "name": "Driver",
        "slug": "driver",
        "description": "Professional drivers and transportation services.",
        "icon": "🚗"
    },

    {
        "name": "Gardening",
        "slug": "gardening",
        "description": "Gardening, landscaping and plant maintenance.",
        "icon": "🌿"
    },

    {
        "name": "Beauty & Salon",
        "slug": "beauty-salon",
        "description": "Beauty, salon, makeup and personal grooming services.",
        "icon": "💇"
    },

    {
        "name": "Home Moving",
        "slug": "home-moving",
        "description": "Packing, loading, transportation and moving services.",
        "icon": "📦"
    },

    {
        "name": "Computer & IT",
        "slug": "computer-it",
        "description": "Computer repair, software, networking and IT services.",
        "icon": "💻"
    },

    {
        "name": "Mobile Repair",
        "slug": "mobile-repair",
        "description": "Smartphone and mobile device repair services.",
        "icon": "📱"
    },

    {
        "name": "Security",
        "slug": "security",
        "description": "Security guards and security-related services.",
        "icon": "🛡️"
    },

    {
        "name": "Other",
        "slug": "other",
        "description": "For jobs that do not fit into the available categories.",
        "icon": "✦"
    }

]


def ensure_default_categories():
    """
    Creates missing default categories.

    Existing categories are never deleted.
    Existing category IDs remain unchanged.
    """

    created = 0

    for item in DEFAULT_CATEGORIES:

        category = Category.query.filter_by(
            slug=item["slug"]
        ).first()

        if category:
            continue

        category = Category(
            name=item["name"],
            slug=item["slug"],
            description=item["description"],
            icon=item["icon"],
            image=None,
            is_active=True
        )

        db.session.add(category)

        created += 1

    if created:
        db.session.commit()

    return created
