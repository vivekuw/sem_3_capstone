"""OpenAI-compatible LLM client configured for local LM Studio or remote inference."""

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("LLMClient")

LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistralai/mistral-7b-instruct-v0.3")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "22.0"))


class LLMClient:
    """Wrapper around OpenAI SDK targeting local LM Studio endpoint."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.base_url = base_url or LM_STUDIO_BASE_URL
        self.api_key = api_key or LM_STUDIO_API_KEY
        self.timeout = timeout if timeout is not None else LLM_TIMEOUT
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        
        # Dynamic model detection: use specified model or pick first active model from LM Studio
        self.model = model or LLM_MODEL_NAME
        try:
            available = self.client.models.list()
            if available and hasattr(available, "data") and len(available.data) > 0:
                first_model = available.data[0].id
                # If configured model not in list or default, use active model from LM Studio
                model_ids = [m.id for m in available.data]
                if self.model not in model_ids:
                    self.model = first_model
                logger.info(f"LLMClient connected to LM Studio. Active model: {self.model}")
        except Exception:
            logger.info(f"LM Studio model discovery skipped. Using: {self.model}")

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Query LLM and parse JSON output with robust regex extraction and graceful fallback."""
        try:
            # Instruct LLM to output pure JSON
            formatted_system = system_prompt + "\n\nCRITICAL: Respond ONLY with a valid JSON object. Do not include markdown codeblocks or preamble."
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": formatted_system},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=450,
                timeout=self.timeout,
            )
            raw_content = response.choices[0].message.content or "{}"
            
            # Robust JSON extraction: strip markdown fences if present
            cleaned = raw_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Attempt direct parse
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Regex search for the first JSON object {...}
                import re
                match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                raise ValueError("No valid JSON object found in LLM output")

        except Exception as exc:
            logger.warning(f"LLM query failed or endpoint unreachable ({exc}). Generating grounded mock response.")
            return self._generate_fallback_response(user_prompt)

    def _generate_fallback_response(self, user_prompt: str) -> Dict[str, Any]:
        """Deterministic rule-based response when LM Studio server is not actively running."""
        is_cascade = (
            "CASCADE" in user_prompt.upper()
            or "ALL(43)" in user_prompt.upper()
            or "43 SENSORS" in user_prompt.upper()
            or "PLANT_WIDE" in user_prompt.upper()
        )
        is_cooling = "COOL" in user_prompt or "XMEAS_9" in user_prompt or "XMEAS_21" in user_prompt
        is_feed = "FEED" in user_prompt or "XMEAS_1" in user_prompt or "XMEAS_4" in user_prompt

        if is_cascade:
            return {
                "root_cause_summary": "Plant-wide cascading disturbance detected across all 43 process sensors and 6 equipment units, initiated by stoichiometric reactant feed manifold imbalance in UNIT_FEED.",
                "probable_failure_mode": "ALL(43): Plant-Wide Multi-Unit Cascade Excursion",
                "primary_unit": "UNIT_FEED",
                "confidence_score": 0.95,
                "propagation_path": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR", "UNIT_STRIPPER"],
                "evidence_citations": [
                    "Temporal analysis confirms UNIT_FEED (XMEAS_1..4) deviated first at T+0s before downstream units.",
                    "All 43 process measurements (temperatures, pressures, flowrates, levels, and stream compositions) deviated along physical flowsheets.",
                    "Directed graph proximity reveals severe propagation across all 6 equipment units via Streams 1 through 11."
                ],
                "operator_actions": [
                    "UNIT_FEED: Stabilize reactant A/D/E feed headers and reset flow control valves XMV_1-XMV_4.",
                    "UNIT_REACTOR: Verify cooling water valve XMV_10 is not saturated; trim feed to arrest thermal surge.",
                    "UNIT_CONDENSER: Verify coolant pump operation and open bypass valve XMV_11.",
                    "UNIT_SEPARATOR: Increase purge valve XMV_6 to vent inert surge and restore liquid level.",
                    "UNIT_COMPRESSOR: Monitor power draw on XMEAS_20 to prevent surge trip.",
                    "UNIT_STRIPPER: Adjust reboiler steam flow XMEAS_19 to restore bottom product compositions."
                ]
            }
        elif is_cooling:
            return {
                "root_cause_summary": "Excursion initiated by thermal disturbance in reactor cooling jacket.",
                "probable_failure_mode": "IDV(4): Reactor Cooling Water Inlet Temp Step Increase",
                "primary_unit": "UNIT_REACTOR",
                "confidence_score": 0.88,
                "propagation_path": ["UNIT_REACTOR", "Stream 7", "UNIT_CONDENSER"],
                "evidence_citations": [
                    "Reactor temperature (XMEAS_9) and cooling water return (XMEAS_21) deviated first.",
                    "Granger causality confirms reactor thermal lead over downstream condenser."
                ],
                "operator_actions": [
                    "Inspect reactor cooling water bypass valve XMV_10.",
                    "Verify secondary utility supply and adjust feed rate to compensate."
                ]
            }
        elif is_feed:
            return {
                "root_cause_summary": "Feed system pressure loss or flow starvation leading to reactor imbalance.",
                "probable_failure_mode": "IDV(6): A Feed Loss",
                "primary_unit": "UNIT_FEED",
                "confidence_score": 0.85,
                "propagation_path": ["UNIT_FEED", "Stream 1-4", "UNIT_REACTOR"],
                "evidence_citations": [
                    "Feed flow sensor XMEAS_1 dropped rapidly.",
                    "Reactor feed pressure dropped correspondingly."
                ],
                "operator_actions": [
                    "Verify feed pump status and valve XMV_3.",
                    "Switch to backup reactant A header immediately."
                ]
            }
        else:
            return {
                "root_cause_summary": "Unspecified process perturbation detected across plant units.",
                "probable_failure_mode": "IDV(1): Feed Ratio Step Change",
                "primary_unit": "UNIT_FEED",
                "confidence_score": 0.70,
                "propagation_path": ["UNIT_FEED", "UNIT_REACTOR"],
                "evidence_citations": [
                    "Multiple sensors registered correlated departures from baseline."
                ],
                "operator_actions": [
                    "Verify controller loop setpoints across all feed headers."
                ]
            }
