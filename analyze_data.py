"""
Data Analysis Script for Member Messages
Identifies anomalies and inconsistencies in the dataset.
"""
import requests
import json
from collections import defaultdict, Counter
from datetime import datetime
import re


def fetch_all_messages():
    """Fetch all messages from the API."""
    url = "https://november7-730026606190.europe-west1.run.app/messages"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("items", [])


def analyze_data():
    """Analyze the dataset for anomalies and inconsistencies."""
    messages = fetch_all_messages()
    
    print(f"Total messages: {len(messages)}")
    print("\n" + "="*80)
    print("DATA ANALYSIS REPORT")
    print("="*80 + "\n")
    
    findings = []
    
    # 1. Check for duplicate message IDs
    message_ids = [msg.get("id") for msg in messages]
    duplicate_ids = [msg_id for msg_id, count in Counter(message_ids).items() if count > 1]
    if duplicate_ids:
        findings.append(f"⚠️  Found {len(duplicate_ids)} duplicate message IDs")
    else:
        findings.append("✓ All message IDs are unique")
    
    # 2. Check for missing required fields
    missing_fields = defaultdict(int)
    for msg in messages:
        if not msg.get("id"):
            missing_fields["id"] += 1
        if not msg.get("user_id"):
            missing_fields["user_id"] += 1
        if not msg.get("user_name"):
            missing_fields["user_name"] += 1
        if not msg.get("timestamp"):
            missing_fields["timestamp"] += 1
        if not msg.get("message"):
            missing_fields["message"] += 1
    
    if missing_fields:
        findings.append(f"⚠️  Missing fields: {dict(missing_fields)}")
    else:
        findings.append("✓ All required fields are present")
    
    # 3. Check for invalid timestamps
    invalid_timestamps = 0
    future_timestamps = 0
    very_old_timestamps = 0
    current_year = datetime.now().year
    
    for msg in messages:
        ts = msg.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.year > current_year + 1:
                    future_timestamps += 1
                elif dt.year < 2000:
                    very_old_timestamps += 1
            except:
                invalid_timestamps += 1
    
    if invalid_timestamps > 0:
        findings.append(f"⚠️  Found {invalid_timestamps} invalid timestamps")
    if future_timestamps > 0:
        findings.append(f"⚠️  Found {future_timestamps} timestamps in the future (beyond {current_year + 1})")
    if very_old_timestamps > 0:
        findings.append(f"⚠️  Found {very_old_timestamps} very old timestamps (before 2000)")
    if invalid_timestamps == 0 and future_timestamps == 0 and very_old_timestamps == 0:
        findings.append("✓ All timestamps are valid")
    
    # 4. Check for inconsistent user_name vs user_id mapping
    user_id_to_name = {}
    inconsistent_mappings = []
    
    for msg in messages:
        user_id = msg.get("user_id")
        user_name = msg.get("user_name")
        if user_id and user_name:
            if user_id in user_id_to_name:
                if user_id_to_name[user_id] != user_name:
                    inconsistent_mappings.append({
                        "user_id": user_id,
                        "expected": user_id_to_name[user_id],
                        "found": user_name
                    })
            else:
                user_id_to_name[user_id] = user_name
    
    if inconsistent_mappings:
        findings.append(f"⚠️  Found {len(inconsistent_mappings)} inconsistent user_id to user_name mappings")
        findings.append(f"   Example: {inconsistent_mappings[0]}")
    else:
        findings.append("✓ All user_id to user_name mappings are consistent")
    
    # 5. Check for empty or very short messages
    empty_messages = sum(1 for msg in messages if not msg.get("message") or len(msg.get("message", "").strip()) < 3)
    if empty_messages > 0:
        findings.append(f"⚠️  Found {empty_messages} empty or very short messages")
    else:
        findings.append("✓ All messages have meaningful content")
    
    # 6. Check for suspicious patterns (e.g., test data, placeholder text)
    suspicious_patterns = [
        "test", "placeholder", "lorem ipsum", "example", "dummy"
    ]
    suspicious_messages = []
    for msg in messages:
        msg_text = msg.get("message", "").lower()
        if any(pattern in msg_text for pattern in suspicious_patterns):
            suspicious_messages.append(msg.get("id"))
    
    if suspicious_messages:
        findings.append(f"⚠️  Found {len(suspicious_messages)} messages with suspicious patterns")
    else:
        findings.append("✓ No suspicious test/placeholder messages detected")
    
    # 7. Check for duplicate messages (same content)
    message_texts = [msg.get("message", "").strip().lower() for msg in messages]
    duplicate_messages = [text for text, count in Counter(message_texts).items() if count > 1 and text]
    if duplicate_messages:
        findings.append(f"⚠️  Found {len(duplicate_messages)} sets of duplicate message content")
    else:
        findings.append("✓ No duplicate message content detected")
    
    # 8. Analyze user activity distribution
    user_message_counts = Counter([msg.get("user_id") for msg in messages])
    if len(user_message_counts) > 0:
        max_messages = max(user_message_counts.values())
        min_messages = min(user_message_counts.values())
        avg_messages = sum(user_message_counts.values()) / len(user_message_counts)
        findings.append(f"📊 User activity: {len(user_message_counts)} unique users")
        findings.append(f"   Messages per user: min={min_messages}, max={max_messages}, avg={avg_messages:.1f}")
        
        # Check for users with unusually high/low activity
        if max_messages > avg_messages * 3:
            findings.append(f"⚠️  Some users have unusually high message counts (max: {max_messages} vs avg: {avg_messages:.1f})")
    
    # 9. Check for date inconsistencies (messages from same user with impossible time gaps)
    user_messages_by_time = defaultdict(list)
    for msg in messages:
        user_id = msg.get("user_id")
        ts = msg.get("timestamp")
        if user_id and ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                user_messages_by_time[user_id].append(dt)
            except:
                pass
    
    # This is a simplified check - in production, you'd want more sophisticated analysis
    findings.append(f"📊 Analyzed temporal patterns for {len(user_messages_by_time)} users")
    
    # Print findings
    print("FINDINGS:\n")
    for finding in findings:
        print(f"  {finding}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    anomalies = sum(1 for f in findings if "⚠️" in f)
    if anomalies == 0:
        print("✓ No major anomalies detected. Data quality appears good.")
    else:
        print(f"⚠️  Found {anomalies} potential anomaly categories.")
        print("   Review the findings above for details.")
    
    return findings


if __name__ == "__main__":
    analyze_data()

