# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_destination,
    calculate_trip_budget,
    find_nearby_places,
    generate_destination_image,
    generate_destination_video,
    geocode_address,
    get_destination_details,
    get_exchange_rates,
    search_destinations,
)

MEMORY_BANK_ID = "7346441916566732800"

memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-02-0922e3426e99",
    location="us-east1",
    agent_engine_id=MEMORY_BANK_ID,
)


async def generate_memories_callback(callback_context: CallbackContext):
    if getattr(callback_context._invocation_context, "memory_service", None) is not None:
        await callback_context.add_session_to_memory()
    return None


def _get_agent_engine_resource_name() -> str:
    metadata_path = "deployment_metadata.json"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                data = json.load(f)
                res_id = data.get("remote_agent_runtime_id")
                if res_id:
                    return res_id
        except Exception:
            pass
    return "projects/1043598016361/locations/us-east1/reasoningEngines/7346441916566732800"


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_get_agent_engine_resource_name()
)


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a personal Travel Concierge assistant. You remember the user's travel preferences, "
        "dietary restrictions, food & medical allergies, and past trips across sessions. ALWAYS retrieve and "
        "strictly respect all recorded user allergies from memory. Never suggest meals, restaurants, or experiences "
        "that contain or trigger the user's known allergies. You help travelers discover destinations, generate "
        "travel postcards, destination images, and short travel preview videos, geocode locations, find nearby attractions and restaurants, lookup "
        "landmark details, search destination catalogs, calculate trip budgets, fetch real-time exchange rates, "
        "run Python calculations in a secure code execution sandbox, and add new places to their travel registry. "
        "CRITICAL MEDIA DIRECTIVE: You possess full capabilities to generate videos and images using your tools `generate_destination_video` and `generate_destination_image`. "
        "NEVER refuse video or image requests, and NEVER claim 'I cannot generate videos' or 'I am unable to generate videos'. "
        "When the user asks to generate a video or short clip, ALWAYS IMMEDIATELY call the `generate_destination_video` tool. "
        "When the user asks to generate an image, postcard, or photo, ALWAYS IMMEDIATELY call the `generate_destination_image` tool."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        search_destinations,
        get_destination_details,
        add_destination,
        calculate_trip_budget,
        get_exchange_rates,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
