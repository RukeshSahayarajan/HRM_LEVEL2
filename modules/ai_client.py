# ============================================================
# FILE: modules/ai_client.py - OPTIMIZED FOR YOUR API KEY
# ============================================================
"""
Groq AI Client Module - Optimized based on test results
Your API can handle 10 rapid calls, so we use conservative settings
"""

import json
import time
import random
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Global tracking
_last_api_call_time = 0
_api_call_count = 0
_minute_start_time = time.time()

# OPTIMIZED SETTINGS (based on your test showing 10 rapid calls work)
MIN_DELAY_BETWEEN_CALLS = 4.0  # 4 seconds (15 calls/minute = safe)
MAX_RETRIES = 4
INITIAL_RETRY_DELAY = 15
CALLS_PER_MINUTE_LIMIT = 20  # Conservative: 20 out of 30 available


def _reset_minute_counter():
    """Reset the per-minute call counter"""
    global _api_call_count, _minute_start_time
    current_time = time.time()

    if current_time - _minute_start_time >= 60:
        _api_call_count = 0
        _minute_start_time = current_time
        print("🔄 Rate limit counter reset")


def _wait_for_rate_limit():
    """
    Smart rate limiting with per-minute tracking
    """
    global _last_api_call_time, _api_call_count, _minute_start_time

    _reset_minute_counter()

    # Check if we've hit the per-minute limit
    if _api_call_count >= CALLS_PER_MINUTE_LIMIT:
        time_elapsed = time.time() - _minute_start_time
        time_remaining = 60 - time_elapsed

        if time_remaining > 0:
            print(f"⏸️  Minute limit reached ({CALLS_PER_MINUTE_LIMIT} calls). Cooling down {time_remaining:.0f}s...")
            time.sleep(time_remaining + 2)
            _api_call_count = 0
            _minute_start_time = time.time()

    # Minimum delay between calls
    current_time = time.time()
    time_since_last_call = current_time - _last_api_call_time

    if time_since_last_call < MIN_DELAY_BETWEEN_CALLS:
        wait_time = MIN_DELAY_BETWEEN_CALLS - time_since_last_call
        if wait_time > 0.5:  # Only show if meaningful wait
            print(f"⏳ Cooldown: {wait_time:.1f}s...")
        time.sleep(wait_time)

    _last_api_call_time = time.time()
    _api_call_count += 1

    if _api_call_count % 5 == 0:  # Show every 5 calls
        print(f"📊 API Calls this minute: {_api_call_count}/{CALLS_PER_MINUTE_LIMIT}")


def generate_content(prompt, max_retries=MAX_RETRIES):
    """
    Generate content using Groq AI with smart rate limiting

    Args:
        prompt: Text prompt to send to AI
        max_retries: Number of retry attempts

    Returns:
        str: AI response text
    """
    # Wait before making the call
    _wait_for_rate_limit()

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt + 1}/{max_retries}")

            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at parsing and analyzing documents. Always return valid JSON without markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4096,
                top_p=1,
                stream=False
            )

            response = completion.choices[0].message.content
            return response

        except Exception as e:
            error_msg = str(e).lower()

            # Check if it's a rate limit error
            if any(keyword in error_msg for keyword in ["rate", "limit", "429", "quota"]):
                if attempt < max_retries - 1:
                    # Exponential backoff: 15s, 30s, 60s, 120s
                    wait_time = INITIAL_RETRY_DELAY * (2 ** attempt) + random.uniform(2, 8)
                    print(f"⚠️  RATE LIMIT! Waiting {wait_time:.0f}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)

                    # Reset minute counter after long wait
                    global _api_call_count, _minute_start_time
                    _api_call_count = 0
                    _minute_start_time = time.time()

                    continue
                else:
                    raise Exception(
                        f"❌ Rate limit exceeded after {max_retries} attempts.\n"
                        f"⏰ Wait 2-3 minutes, then try again.\n"
                        f"💡 Or process fewer resumes at once (5 max recommended)."
                    )

            # Timeout errors
            elif "timeout" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"⚠️  Timeout. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"❌ Timeout after {max_retries} attempts")

            # Other errors - don't retry
            else:
                raise Exception(f"❌ Groq API error: {str(e)}")

    raise Exception(f"❌ Failed after {max_retries} attempts")


def clean_json_response(text):
    """Clean and extract JSON from AI response"""
    if not text:
        return text

    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
        elif len(parts) == 2:
            text = parts[1]

    text = text.strip()

    if text.startswith("json"):
        text = text[4:].strip()

    return text


def parse_json_response(text):
    """Parse JSON response from AI"""
    try:
        cleaned_text = clean_json_response(text)
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"Response preview: {text[:300] if text else 'Empty'}")

        # Try to find JSON in the text
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass

        return None


def get_ai_info():
    """Get information about current AI setup"""
    return {
        "provider": "Groq",
        "model": GROQ_MODEL,
        "effective_rpm": CALLS_PER_MINUTE_LIMIT,
        "min_delay": MIN_DELAY_BETWEEN_CALLS,
        "max_retries": MAX_RETRIES
    }


def reset_rate_limiter():
    """Manually reset rate limiter"""
    global _api_call_count, _minute_start_time, _last_api_call_time
    _api_call_count = 0
    _minute_start_time = time.time()
    _last_api_call_time = 0
    print("🔄 Rate limiter manually reset!")