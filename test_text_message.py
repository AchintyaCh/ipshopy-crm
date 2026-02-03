"""
Test script for sending text messages via Interakt
Run from bench console to test before building frontend
"""

import frappe

def test_send_text_message():
	"""Test sending a text message to a lead"""
	print("\n" + "="*60)
	print("🧪 TESTING TEXT MESSAGE SENDING")
	print("="*60 + "\n")
	
	# Test lead
	lead_name = "CRM-LEAD-2026-00004"  # Krishna Salve
	message_text = "Hello! This is a test message from ipshopy CRM. 🎉"
	
	print(f"📤 Sending text message to {lead_name}...")
	print(f"📝 Message: {message_text}\n")
	
	try:
		from crm.integrations.interakt.api import send_text_message_to_lead
		
		result = send_text_message_to_lead(
			reference_doctype="CRM Lead",
			reference_docname=lead_name,
			message_text=message_text,
		)
		
		print(f"📊 Result:")
		print(f"   Success: {result.get('success')}")
		print(f"   Message ID: {result.get('message_id')}")
		print(f"   Error: {result.get('error')}")
		
		if result.get('success'):
			print(f"\n✅ Message sent successfully!")
			
			# Check if logged
			count = frappe.db.count("CRM WhatsApp Message")
			print(f"\n📊 Total messages in DB: {count}")
			
			# Get the message
			messages = frappe.get_all(
				"CRM WhatsApp Message",
				filters={"message_id": result.get('message_id')},
				fields=["name", "phone_number", "status", "message_content"],
			)
			
			if messages:
				msg = messages[0]
				print(f"\n✅ Message logged:")
				print(f"   Name: {msg.name}")
				print(f"   Phone: {msg.phone_number}")
				print(f"   Status: {msg.status}")
				print(f"   Content: {msg.message_content[:50]}...")
		else:
			print(f"\n❌ Failed to send message!")
			print(f"   Error: {result.get('error')}")
	
	except Exception as e:
		print(f"\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
	
	print("\n" + "="*60)
	print("✅ TEST COMPLETE")
	print("="*60 + "\n")


def test_get_messages():
	"""Test getting messages for a lead"""
	print("\n" + "="*60)
	print("🔍 TESTING GET MESSAGES")
	print("="*60 + "\n")
	
	lead_name = "CRM-LEAD-2026-00004"
	
	try:
		from crm.integrations.interakt.api import get_whatsapp_messages
		
		messages = get_whatsapp_messages(
			reference_doctype="CRM Lead",
			reference_docname=lead_name,
		)
		
		print(f"📊 Found {len(messages)} message(s) for {lead_name}:\n")
		
		for msg in messages:
			print(f"   📧 {msg.name}")
			print(f"      Status: {msg.status}")
			print(f"      Direction: {msg.direction}")
			print(f"      Template: {msg.template_name or 'Text Message'}")
			if msg.message_content:
				print(f"      Content: {msg.message_content[:50]}...")
			print(f"      Created: {msg.creation}")
			print()
	
	except Exception as e:
		print(f"❌ Error: {e}")
		import traceback
		traceback.print_exc()
	
	print("="*60 + "\n")


if __name__ == "__main__":
	# Run tests
	test_send_text_message()
	test_get_messages()
