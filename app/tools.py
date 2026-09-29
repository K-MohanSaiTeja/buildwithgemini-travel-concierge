import json
import os
import time
import urllib.parse
import urllib.request

from google import genai
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types as genai_types

# CRITICAL: Project ID and Storage Bucket Name are explicitly hardcoded for Agent Platform compatibility
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-02-0922e3426e99"
GCS_BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-02-0922e3426e99"

db = firestore.Client(project=FIRESTORE_PROJECT_ID)


def search_destinations(city: str = "", category: str = "") -> list[dict]:
    """Search the travel destinations database by city or category.

    Args:
        city: Optional city name to filter by (e.g. "San Francisco", "New York", "Tokyo", "Paris", "Kyoto").
        category: Optional category filter (e.g. "Landmark", "Park", "Observation Deck", "Cultural Site").

    Returns:
        A list of matching destination dictionaries.
    """
    collection_ref = db.collection("destinations")
    docs = collection_ref.stream()

    results = []
    city_lower = city.strip().lower()
    category_lower = category.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        match_city = not city_lower or city_lower in data.get("city", "").lower()
        match_category = not category_lower or category_lower in data.get("category", "").lower()

        if match_city and match_category:
            results.append(data)

    return results


def get_destination_details(destination_id: str) -> dict:
    """Retrieve full details for a specific travel destination by ID.

    Args:
        destination_id: The document ID of the destination (e.g. "sf_golden_gate", "ny_central_park").

    Returns:
        A dictionary containing destination details or an error dictionary if not found.
    """
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    return {"error": f"Destination '{destination_id}' not found."}


def add_destination(
    name: str,
    city: str,
    country: str,
    category: str,
    description: str,
    price_tier: str = "$$",
    rating: float = 4.5,
) -> dict:
    """Add a new travel destination or venue to the database.

    Args:
        name: Name of the landmark, hotel, or activity.
        city: City where the destination is located.
        country: Country where the destination is located.
        category: Category (e.g. "Landmark", "Park", "Museum", "Dining", "Hotel").
        description: Detailed description of the destination.
        price_tier: Price level ("Free", "$", "$$", "$$$", "$$$$"). Defaults to "$$".
        rating: Rating score out of 5.0 (e.g. 4.8). Defaults to 4.5.

    Returns:
        A dictionary confirmation of the added destination.
    """
    doc_id = f"{city.lower().replace(' ', '_')}_{name.lower().replace(' ', '_')}"[:30]
    doc_data = {
        "id": doc_id,
        "name": name,
        "city": city,
        "country": country,
        "category": category,
        "description": description,
        "price_tier": price_tier,
        "rating": rating,
        "tags": [category.lower(), city.lower()],
    }

    db.collection("destinations").document(doc_id).set(doc_data)
    return {"status": "success", "message": f"Successfully added destination '{name}'", "destination": doc_data}


def calculate_trip_budget(
    daily_accommodation: float,
    daily_meals: float,
    daily_activities: float,
    duration_days: int = 1,
    num_travelers: int = 1,
    currency: str = "USD",
) -> dict:
    """Calculate total and per-person trip budget breakdown.

    Args:
        daily_accommodation: Estimated daily hotel or lodging cost per room.
        daily_meals: Estimated daily food and dining cost per person.
        daily_activities: Estimated daily excursion or activity cost per person.
        duration_days: Total duration of the trip in days (default 1).
        num_travelers: Total number of people traveling (default 1).
        currency: Preferred currency code, e.g. "USD", "EUR", "JPY" (default "USD").

    Returns:
        A dictionary with itemized totals, overall total cost, and per-person cost.
    """
    total_accommodation = daily_accommodation * duration_days
    total_meals = daily_meals * duration_days * num_travelers
    total_activities = daily_activities * duration_days * num_travelers
    total_cost = total_accommodation + total_meals + total_activities
    per_person_cost = total_cost / max(1, num_travelers)

    return {
        "currency": currency.upper(),
        "duration_days": duration_days,
        "num_travelers": num_travelers,
        "breakdown": {
            "accommodation": round(total_accommodation, 2),
            "meals": round(total_meals, 2),
            "activities": round(total_activities, 2),
        },
        "total_cost": round(total_cost, 2),
        "per_person_cost": round(per_person_cost, 2),
    }


def get_exchange_rates(base_currency: str = "USD", target_currencies: str = "EUR,JPY,GBP") -> dict:
    """Fetch real-time foreign exchange rates for travel budgeting and currency conversion.

    Args:
        base_currency: Base currency code (e.g. "USD", "EUR", "GBP", "CAD"). Defaults to "USD".
        target_currencies: Comma-separated target currency codes (e.g. "EUR,JPY,GBP"). Defaults to "EUR,JPY,GBP".

    Returns:
        A dictionary with the base currency, date, and live exchange rates.
    """
    base = base_currency.strip().upper()
    targets = target_currencies.strip().upper()

    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")
    api_url = f"https://api.frankfurter.app/latest?from={base}&to={targets}"
    if api_key:
        api_url += f"&apikey={api_key}"

    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "TravelConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return {
                "status": "success",
                "base": data.get("base", base),
                "date": data.get("date", ""),
                "rates": data.get("rates", {}),
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch exchange rates: {str(e)}"}


def _get_maps_api_key() -> str:
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not key and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("GOOGLE_MAPS_API_KEY="):
                    key = line.strip().split("=", 1)[1].strip('"\': ')
                    break
    return key


def geocode_address(address: str) -> dict:
    """Geocode a street address, city, or landmark into geographic coordinates (latitude and longitude).

    Args:
        address: The address or place name to geocode (e.g., "1600 Amphitheatre Pkwy, Mountain View, CA" or "Eiffel Tower, Paris").

    Returns:
        A dictionary containing the formatted address, latitude, and longitude.
    """
    api_key = _get_maps_api_key()
    if not api_key:
        return {"status": "error", "message": "GOOGLE_MAPS_API_KEY environment variable is not configured."}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "OK" and data.get("results"):
                first_result = data["results"][0]
                location = first_result.get("geometry", {}).get("location", {})
                return {
                    "status": "success",
                    "formatted_address": first_result.get("formatted_address", address),
                    "location": {
                        "latitude": location.get("lat"),
                        "longitude": location.get("lng"),
                    },
                }
            return {"status": "error", "message": f"Geocoding failed with status: {data.get('status')}"}
    except Exception as e:
        return {"status": "error", "message": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
    max_results: int = 5,
) -> dict:
    """Search for nearby places (restaurants, hotels, attractions, etc.) using Google Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g. "restaurant", "hotel", "tourist_attraction", "museum", "cafe").
        radius_meters: Search radius in meters (default 1000.0).
        max_results: Maximum number of results to return (1 to 20, default 5).

    Returns:
        A dictionary containing a list of nearby places with name, formatted address, location, and types.
    """
    api_key = _get_maps_api_key()
    if not api_key:
        return {"status": "error", "message": "GOOGLE_MAPS_API_KEY environment variable is not configured."}

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }
    body = {
        "includedTypes": [place_type],
        "maxResultCount": min(max(1, max_results), 20),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius_meters,
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            places_raw = data.get("places", [])
            results = []
            for item in places_raw:
                results.append({
                    "name": item.get("displayName", {}).get("text", ""),
                    "address": item.get("formattedAddress", ""),
                    "location": item.get("location", {}),
                    "types": item.get("types", []),
                })
            return {"status": "success", "count": len(results), "places": results}
    except Exception as e:
        return {"status": "error", "message": f"Places search request failed: {str(e)}"}


async def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generate a destination image or postcard using gemini-3.1-flash-lite-image in the global region.

    Args:
        prompt: Descriptive prompt for the travel image to generate (e.g. "A scenic postcard of the Eiffel Tower at sunset in Paris").
        tool_context: Injected runtime context to save the image as a UI artifact.

    Returns:
        A dictionary with the prompt, generated artifact filename, and public GCS URL.
    """
    try:
        genai_client = genai.Client(
            vertexai=True,
            project="qwiklabs-gcp-02-0922e3426e99",
            location="global",
        )
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            ),
        )

        part = response.candidates[0].content.parts[0]
        image_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "image/jpeg"
        ext = "png" if "png" in mime_type else "jpg"

        timestamp = int(time.time())
        filename = f"destination_{timestamp}.{ext}"

        # 1. Save artifact for Playground UI using tool_context.save_artifact
        artifact_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same image bytes directly to GCS public bucket and return public URL
        storage_client = storage.Client(project="qwiklabs-gcp-02-0922e3426e99")
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "prompt": prompt,
            "filename": filename,
            "image_url": public_url,
        }
    except Exception as e:
        return {"status": "error", "message": f"Image generation failed: {str(e)}"}


async def generate_destination_video(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generate a short travel video preview using Google's Omni model (gemini-omni-flash-preview) in global region.

    Args:
        prompt: Descriptive prompt for the travel video to generate (e.g. "A short scenic video of Golden Gate Bridge in San Francisco").
        tool_context: Injected runtime context to save the video as a UI artifact.

    Returns:
        A dictionary with prompt, generated artifact filename, and public GCS URL.
    """
    try:
        genai_client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )
        try:
            response = genai_client.models.generate_content(
                model="gemini-omni-flash-preview",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["VIDEO"]
                ),
            )
            part = response.candidates[0].content.parts[0]
            video_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "video/mp4"
            ext = "mp4"
        except Exception:
            return await generate_destination_image(prompt=prompt, tool_context=tool_context)

        timestamp = int(time.time())
        filename = f"destination_video_{timestamp}.{ext}"

        # 1. Save artifact for Playground UI using tool_context.save_artifact
        artifact_part = genai_types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same video bytes directly to public GCS bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "prompt": prompt,
            "filename": filename,
            "video_url": public_url,
        }
    except Exception as e:
        return {"status": "error", "message": f"Video generation failed: {str(e)}"}

