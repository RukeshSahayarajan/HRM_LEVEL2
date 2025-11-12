"""
Test Groq API Connection and Rate Limits
Run this BEFORE processing resumes to verify everything works
"""

import time
from groq import Groq

# Your API key
GROQ_API_KEY = "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"


def test_single_call():
    """Test a single API call"""
    print("\n" + "=" * 60)
    print("TEST 1: Single API Call")
    print("=" * 60)

    try:
        client = Groq(api_key=GROQ_API_KEY)

        print("📞 Making API call...")
        start = time.time()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Hello World' in JSON format"}
            ],
            temperature=0.3,
            max_tokens=100
        )

        elapsed = time.time() - start
        print(f"✅ SUCCESS! Response time: {elapsed:.2f}s")
        print(f"📄 Response: {response.choices[0].message.content[:200]}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_rapid_calls():
    """Test multiple rapid calls to trigger rate limit"""
    print("\n" + "=" * 60)
    print("TEST 2: Rapid Fire Test (Finding Rate Limit)")
    print("=" * 60)
    print("⚠️  This will intentionally trigger rate limits!\n")

    client = Groq(api_key=GROQ_API_KEY)
    success_count = 0
    fail_count = 0

    for i in range(10):
        try:
            print(f"Call {i + 1}/10...", end=" ")

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": f"Return JSON: {{\"number\": {i + 1}}}"}
                ],
                temperature=0.3,
                max_tokens=50
            )

            success_count += 1
            print("✅")

            # No delay - intentionally rapid

        except Exception as e:
            fail_count += 1
            error_msg = str(e)

            if "rate" in error_msg.lower() or "429" in error_msg:
                print(f"⚠️  RATE LIMIT HIT after {success_count} calls!")
                print(f"📊 Result: {success_count} succeeded, {fail_count} rate limited")
                return success_count
            else:
                print(f"❌ Error: {error_msg[:100]}")

    print(f"\n📊 Result: {success_count} succeeded, {fail_count} failed")
    return success_count


def test_with_delays():
    """Test with proper delays"""
    print("\n" + "=" * 60)
    print("TEST 3: With 5-Second Delays (Should Work)")
    print("=" * 60)

    client = Groq(api_key=GROQ_API_KEY)
    success_count = 0

    for i in range(5):
        try:
            print(f"Call {i + 1}/5 (waiting 5s before call)...", end=" ")

            if i > 0:
                time.sleep(5)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": f"Return JSON: {{\"test\": {i + 1}}}"}
                ],
                temperature=0.3,
                max_tokens=50
            )

            success_count += 1
            print("✅")

        except Exception as e:
            print(f"❌ {str(e)[:100]}")

    print(f"\n📊 Result: {success_count}/5 succeeded with 5s delays")
    return success_count == 5


def check_api_key_status():
    """Check if API key is valid and active"""
    print("\n" + "=" * 60)
    print("TEST 0: API Key Status Check")
    print("=" * 60)

    try:
        client = Groq(api_key=GROQ_API_KEY)

        # Try to make a very simple call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )

        print("✅ API Key is VALID and ACTIVE")
        print(f"✅ Model access confirmed: llama-3.3-70b-versatile")
        return True

    except Exception as e:
        error_msg = str(e)
        print(f"❌ API Key Issue Detected!")
        print(f"Error: {error_msg}")

        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            print("\n🔧 SOLUTION: Your API key might be invalid or expired")
            print("   1. Go to https://console.groq.com/keys")
            print("   2. Generate a NEW API key")
            print("   3. Update your .env file")
        elif "rate" in error_msg.lower():
            print("\n🔧 SOLUTION: Your API key might be temporarily rate limited")
            print("   1. Wait 5-10 minutes")
            print("   2. Or create a new API key")

        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 GROQ API COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"API Key: {GROQ_API_KEY[:20]}...{GROQ_API_KEY[-10:]}")
    print("=" * 60)

    # Test 0: Check API key
    if not check_api_key_status():
        print("\n❌ API key check failed. Fix the API key issue first!")
        return

    time.sleep(2)

    # Test 1: Single call
    if not test_single_call():
        print("\n❌ Basic API call failed. Cannot proceed.")
        return

    time.sleep(3)

    # Test 2: Find rate limit threshold
    max_calls = test_rapid_calls()

    time.sleep(5)

    # Test 3: Test with delays
    test_with_delays()

    # Final recommendations
    print("\n" + "=" * 60)
    print("📋 RECOMMENDATIONS BASED ON TESTS")
    print("=" * 60)

    if max_calls >= 5:
        print(f"✅ Your API allows ~{max_calls} rapid calls before rate limiting")
        print(f"✅ Using 5-second delays should work reliably")
        print(f"💡 Safe batch size: 5-10 resumes with delays")
    else:
        print(f"⚠️  Only {max_calls} rapid calls allowed before rate limit")
        print(f"⚠️  You may need longer delays (7-10 seconds)")
        print(f"💡 Safe batch size: 3-5 resumes with long delays")

    print("\n🎯 RECOMMENDED SETTINGS FOR YOUR SYSTEM:")
    print(f"   MIN_DELAY_BETWEEN_CALLS = 6.0  # seconds")
    print(f"   BATCH_SIZE = 5  # resumes per batch")
    print(f"   BATCH_PAUSE = 60  # seconds between batches")
    print("=" * 60)


if __name__ == "__main__":
    main()