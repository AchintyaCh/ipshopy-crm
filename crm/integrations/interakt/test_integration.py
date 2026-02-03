"""
Test script for Interakt integration.
Run this from bench console to test the integration.

Usage:
    bench --site your-site.localhost console
    >>> from crm.integrations.interakt.test_integration import test_integration
    >>> test_integration()
"""

import frappe


def test_integration():
	"""Test the Interakt integration setup."""
	print("\n" + "="*60)
	print("🧪 INTERAKT INTEGRATION TEST")
	print("="*60 + "\n")
	
	# Test 1: Check if DocTypes exist
	print("1️⃣  Checking DocTypes...")
	doctypes = [
		"CRM Interakt Settings",
		"CRM WhatsApp Message",
		"CRM Telephony Agent",
	]
	
	for doctype in doctypes:
		if frappe.db.exists("DocType", doctype):
			print(f"   ✅ {doctype} exists")
		else:
			print(f"   ❌ {doctype} NOT FOUND")
			return
	
	# Test 2: Check if Interakt is enabled
	print("\n2️⃣  Checking Interakt Settings...")
	try:
		settings = frappe.get_single("CRM Interakt Settings")
		if settings.enabled:
			print(f"   ✅ Interakt is ENABLED")
			print(f"   📱 Default Country Code: {settings.default_country_code}")
			print(f"   🔑 API Key: {'*' * 20} (configured)")
			print(f"   📧 Auto-send welcome: {'Yes' if settings.send_welcome_on_lead_create else 'No'}")
		else:
			print(f"   ⚠️  Interakt is DISABLED")
			print(f"   💡 Enable it in CRM Interakt Settings")
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")
		return
	
	# Test 3: Check webhook URL
	print("\n3️⃣  Checking Webhook Configuration...")
	if settings.webhook_url:
		print(f"   ✅ Webhook URL: {settings.webhook_url}")
		print(f"   💡 Configure this URL in your Interakt dashboard")
	else:
		print(f"   ⚠️  Webhook URL not generated")
	
	# Test 4: Check if any messages exist
	print("\n4️⃣  Checking Message Logs...")
	message_count = frappe.db.count("CRM WhatsApp Message")
	print(f"   📊 Total messages: {message_count}")
	
	if message_count > 0:
		recent_messages = frappe.get_all(
			"CRM WhatsApp Message",
			fields=["name", "phone_number", "status", "template_name", "creation"],
			order_by="creation desc",
			limit=5,
		)
		print(f"\n   Recent messages:")
		for msg in recent_messages:
			print(f"   - {msg.name}: {msg.phone_number} | {msg.status} | {msg.template_name}")
	
	# Test 5: Check telephony agents
	print("\n5️⃣  Checking Telephony Agents...")
	agents = frappe.get_all(
		"CRM Telephony Agent",
		fields=["user", "interakt", "interakt_whatsapp_number"],
		filters={"interakt": 1},
	)
	
	if agents:
		print(f"   ✅ {len(agents)} agent(s) configured for Interakt:")
		for agent in agents:
			print(f"   - {agent.user}: {agent.interakt_whatsapp_number}")
	else:
		print(f"   ⚠️  No agents configured for Interakt")
		print(f"   💡 Configure in CRM Telephony Agent")
	
	# Test 6: Test API connection (if enabled)
	if settings.enabled and settings.api_key:
		print("\n6️⃣  Testing API Connection...")
		try:
			from crm.integrations.interakt.interakt_handler import Interakt
			interakt = Interakt.connect()
			if interakt:
				print(f"   ✅ API connection successful")
				print(f"   🔗 Base URL: {interakt.base_url}")
			else:
				print(f"   ❌ Failed to connect to Interakt")
		except Exception as e:
			print(f"   ❌ Error: {str(e)}")
	
	print("\n" + "="*60)
	print("✅ TEST COMPLETE")
	print("="*60 + "\n")
	
	# Provide next steps
	print("📋 NEXT STEPS:")
	if not settings.enabled:
		print("   1. Enable Interakt in CRM Interakt Settings")
		print("   2. Add your API key")
		print("   3. Run this test again")
	elif not agents:
		print("   1. Configure Telephony Agent for your user")
		print("   2. Add WhatsApp number")
		print("   3. Create a test lead")
	else:
		print("   1. Create a test lead with a phone number")
		print("   2. Check CRM WhatsApp Message list")
		print("   3. Verify message received on WhatsApp")
	
	print("\n")


def test_send_message(lead_name):
	"""
	Test sending a message to a specific lead.
	
	Usage:
	    >>> test_send_message("LEAD-00001")
	"""
	print(f"\n🚀 Testing message send to {lead_name}...\n")
	
	try:
		from crm.integrations.interakt.api import send_welcome_message_to_lead
		
		result = send_welcome_message_to_lead(lead_name)
		
		if result.get("success"):
			print(f"✅ Message sent successfully!")
			print(f"📧 Message ID: {result.get('message_id')}")
			print(f"\n💡 Check CRM WhatsApp Message list to see the log")
		else:
			print(f"❌ Failed to send message")
			print(f"Error: {result.get('error')}")
	
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()


def create_test_lead():
	"""
	Create a test lead for testing.
	
	Usage:
	    >>> create_test_lead()
	"""
	print("\n🧪 Creating test lead...\n")
	
	try:
		lead = frappe.new_doc("CRM Lead")
		lead.first_name = "Test"
		lead.last_name = "User"
		lead.mobile_no = "9876543210"  # Change this to your test number
		lead.email = "test@example.com"
		lead.status = "New"
		lead.insert(ignore_permissions=True)
		
		print(f"✅ Test lead created: {lead.name}")
		print(f"📱 Phone: {lead.mobile_no}")
		print(f"\n💡 If auto-send is enabled, message will be sent automatically")
		print(f"💡 Check CRM WhatsApp Message list in a few seconds")
		
		return lead.name
	
	except Exception as e:
		print(f"❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()


if __name__ == "__main__":
	test_integration()
