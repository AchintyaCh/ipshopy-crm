#!/usr/bin/env python3
"""
Test script for Interakt text message functionality.
Run this from bench console: bench --site ipshopy.localhost console
Then: exec(open('test_text_message_backend.py').read())
"""

import frappe

print("=" * 60)
print("🧪 TESTING INTERAKT TEXT MESSAGE BACKEND")
print("=" * 60)

# Test 1: Check if functions exist
print("\n1️⃣  Checking if API functions exist...")
try:
    from crm.integrations.interakt.api import send_text_message_to_lead, get_whatsapp_messages
    print("✅ Functions imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n⚠️  Please restart bench: bench restart")
    exit()

# Test 2: Get a test lead
print("\n2️⃣  Finding a test lead...")
lead = frappe.get_all(
    "CRM Lead",
    filters={"mobile_no": ["!=", ""]},
    fields=["name", "first_name", "last_name", "mobile_no"],
    limit=1
)

if not lead:
    print("❌ No leads with phone numbers found")
    exit()

lead = lead[0]
print(f"✅ Found lead: {lead.name} - {lead.first_name} {lead.last_name} | {lead.mobile_no}")

# Test 3: Send a text message
print(f"\n3️⃣  Sending text message to {lead.name}...")
try:
    result = send_text_message_to_lead(
        reference_doctype="CRM Lead",
        reference_docname=lead.name,
        message_text="Hello! This is a test message from Frappe CRM. 👋"
    )
    
    print(f"📊 Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Message ID: {result.get('message_id')}")
    if result.get('error'):
        print(f"   Error: {result.get('error')}")
    
    if result.get('success'):
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Retrieve messages
print(f"\n4️⃣  Retrieving WhatsApp messages for {lead.name}...")
try:
    messages = get_whatsapp_messages(
        reference_doctype="CRM Lead",
        reference_docname=lead.name
    )
    
    print(f"📊 Found {len(messages)} message(s):")
    for msg in messages:
        msg_type = "Template" if msg.get('template_name') else "Text"
        content = msg.get('template_name') or msg.get('message_content', '')[:50]
        print(f"   - {msg.name}: {msg_type} | {msg.status} | {content}")
    
    if messages:
        print("✅ Messages retrieved successfully!")
    else:
        print("⚠️  No messages found (might be logging issue)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ BACKEND TEST COMPLETE")
print("=" * 60)
print("\n💡 Next steps:")
print("   1. Check if message was sent to WhatsApp")
print("   2. Verify message appears in CRM WhatsApp Message list")
print("   3. If working, proceed with frontend development")
