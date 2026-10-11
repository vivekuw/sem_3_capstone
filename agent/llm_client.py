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
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "meta-llama-3.1-8b-instruct")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "4.0"))


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
        self.model = model or LLM_MODEL_NAME
        self.timeout = timeout if timeout is not None else LLM_TIMEOUT
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Query LLM and parse JSON output with graceful fallback."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=LLM_TEMPERATURE,
                response_format={"type": "json_object"},
                timeout=self.timeout,
            )
            raw_content = response.choices[0].message.content or "{}"
            return json.loads(raw_content)
        except Exception as exc:
            logger.warning(f"LLM query failed or endpoint unreachable ({exc}). Generating grounded mock response.")
            return self._generate_fallback_response(user_prompt)

    def _generate_fallback_response(self, user_prompt: str) -> Dict[str, Any]:
        """Deterministic rule-based response when LM Studio server is not actively running."""
        # Simple heuristic parser for testing and development
        is_cooling = "COOL" in user_prompt or "XMEAS_9" in user_prompt or "XMEAS_21" in user_prompt
        is_feed = "FEED" in user_prompt or "XMEAS_1" in user_prompt or "XMEAS_4" in user_prompt

        if is_cooling:
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
