# Copyright 2026 Google LLC
# Seed script for Travel Concierge Firestore collection

from google.cloud import firestore

# Hardcode the project ID as required to avoid project number resolution issues on Agent Platform
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-02-0922e3426e99"

db = firestore.Client(project=FIRESTORE_PROJECT_ID)

SEED_DESTINATIONS = [
    {
        "id": "sf_golden_gate",
        "name": "Golden Gate Bridge & Park",
        "city": "San Francisco",
        "country": "USA",
        "category": "Landmark",
        "description": "Iconic red suspension bridge offering stunning bay views and expansive parklands with museums and botanical gardens.",
        "rating": 4.9,
        "price_tier": "Free",
        "tags": ["scenic", "outdoors", "iconic", "family-friendly"],
    },
    {
        "id": "ny_central_park",
        "name": "Central Park",
        "city": "New York",
        "country": "USA",
        "category": "Park",
        "description": "843-acre urban oasis in Manhattan featuring walking paths, lakes, ice rinks, and historic monuments.",
        "rating": 4.8,
        "price_tier": "Free",
        "tags": ["nature", "outdoors", "walking", "sightseeing"],
    },
    {
        "id": "tokyo_shibuya_sky",
        "name": "Shibuya Sky",
        "city": "Tokyo",
        "country": "Japan",
        "category": "Observation Deck",
        "description": "Open-air rooftop observatory atop Shibuya Scramble Square with 360-degree panoramic views of Tokyo.",
        "rating": 4.7,
        "price_tier": "$$",
        "tags": ["skyline", "views", "photography", "modern"],
    },
    {
        "id": "paris_eiffel_tower",
        "name": "Eiffel Tower",
        "city": "Paris",
        "country": "France",
        "category": "Landmark",
        "description": "Wrought-iron lattice tower on the Champ de Mars, offering dining, observation decks, and evening light shows.",
        "rating": 4.8,
        "price_tier": "$$$",
        "tags": ["romantic", "iconic", "views", "dining"],
    },
    {
        "id": "kyoto_fushimi_inari",
        "name": "Fushimi Inari Shrine",
        "city": "Kyoto",
        "country": "Japan",
        "category": "Cultural Site",
        "description": "Famous Shinto shrine renowned for thousands of vermilion torii gates straddling hiking trails up Mount Inari.",
        "rating": 4.9,
        "price_tier": "Free",
        "tags": ["culture", "hiking", "historic", "scenic"],
    },
]

def seed_database():
    print(f"Seeding Firestore collection 'destinations' in project '{FIRESTORE_PROJECT_ID}'...")
    collection_ref = db.collection("destinations")
    for dest in SEED_DESTINATIONS:
        doc_id = dest["id"]
        collection_ref.document(doc_id).set(dest)
        print(f"  ✓ Seeded: {dest['name']} ({doc_id})")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
