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
    {
        "id": "anantapur_lepakshi_temple",
        "name": "Lepakshi Veerabhadra Temple",
        "city": "Anantapur",
        "country": "India",
        "category": "Cultural Site",
        "description": "Architectural marvel from the 16th century Vijayanagara Empire, famous for its miraculous Hanging Pillar, intricate ceiling frescoes, and magnificent monolithic Nandi bull.",
        "rating": 4.8,
        "price_tier": "Free",
        "tags": ["temple", "historic", "architecture", "heritage", "anantapur"],
    },
    {
        "id": "anantapur_penukonda_fort",
        "name": "Penukonda Fort & Gagan Mahal",
        "city": "Anantapur",
        "country": "India",
        "category": "Historic Landmark",
        "description": "Historic hill fort and royal citadel that served as the second capital of the Vijayanagara Kingdom, featuring Babayya Dargah and Gagan Mahal palace.",
        "rating": 4.6,
        "price_tier": "Free",
        "tags": ["fort", "historic", "panoramic views", "anantapur"],
    },
    {
        "id": "anantapur_iskcon_temple",
        "name": "ISKCON Temple Anantapur",
        "city": "Anantapur",
        "country": "India",
        "category": "Religious Site",
        "description": "Stunning chariot-shaped temple complex situated at Somuladoddi, dedicated to Lord Krishna with serene gardens and peaceful spiritual ambiance.",
        "rating": 4.7,
        "price_tier": "Free",
        "tags": ["spiritual", "architecture", "gardens", "anantapur"],
    },
    {
        "id": "anantapur_clock_tower",
        "name": "Anantapur Clock Tower",
        "city": "Anantapur",
        "country": "India",
        "category": "Landmark",
        "description": "Historic clock tower built during the Indian independence era, serving as the central heritage symbol and vibrant hub of Anantapur town.",
        "rating": 4.5,
        "price_tier": "Free",
        "tags": ["heritage", "city center", "iconic", "anantapur"],
    },
    {
        "id": "anantapur_hotel_annapurna",
        "name": "Hotel Annapurna & Rayalaseema Mess",
        "city": "Anantapur",
        "country": "India",
        "category": "Dining",
        "description": "Top-rated local dining destination renowned for authentic spicy Rayalaseema Thalis served on traditional banana leaves, ragi sangati, and authentic Andhra delicacies.",
        "rating": 4.8,
        "price_tier": "$",
        "tags": ["dining", "restaurant", "andhra meals", "rayalaseema", "anantapur"],
    },
    {
        "id": "anantapur_surya_restaurant",
        "name": "Surya Family Restaurant",
        "city": "Anantapur",
        "country": "India",
        "category": "Dining",
        "description": "Popular family dining spot offering flavorful Hyderabadi Biryani, tandoori starters, and North & South Indian dishes.",
        "rating": 4.6,
        "price_tier": "$$",
        "tags": ["dining", "biryani", "family dining", "anantapur"],
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
