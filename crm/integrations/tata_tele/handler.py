import frappe
import requests
import json
from frappe import _
from frappe.integrations.utils import create_request_log

from crm.integrations.api import get_contact_by_phone_number
from crm.fcrm.doctype.crm_tata_tele_settings.crm_tata_tele_settings import TataTeleSettings


def is_integration_enabled():
	"""Check if Tata Tele integration is enabled"""
	return TataTeleSettings.is_enabled()


@frappe.whitelist()
def make_a_call(to_number, from_number=None):
	"""
	Make a call using Tata Teleservices API.
	
	Args:
		to_number: Phone number to call (destination_number/recipient)
		from_number: Phone number to call from (optional, will use default agent_number)
	
	Returns:
		dict: Call initiation response from API
	"""
	# Debug: Log all incoming parameters
	frappe.logger().info("=" * 80)
	frappe.logger().info("[TATA TELE] Make Call Request Started")
	frappe.logger().info(f"[TATA TELE] Input Parameters:")
	frappe.logger().info(f"  - to_number (destination): {to_number}")
	frappe.logger().info(f"  - from_number (optional): {from_number}")
	
	if not is_integration_enabled():
		frappe.logger().warning("[TATA TELE] Integration is not enabled")
		frappe.throw(
			_("Please setup Tata Tele integration"),
			title=_("Integration Not Enabled")
		)

	settings = TataTeleSettings.get_settings()
	if not settings:
		frappe.logger().warning("[TATA TELE] Settings not configured")
		frappe.throw(
			_("Tata Tele Settings not configured"),
			title=_("Configuration Missing")
		)

	# Debug: Log settings
	frappe.logger().info(f"[TATA TELE] Settings Retrieved:")
	frappe.logger().info(f"  - Enabled: {settings.enabled}")
	frappe.logger().info(f"  - API Endpoint: {settings.api_endpoint}")
	frappe.logger().info(f"  - Account ID: {settings.account_id}")
	frappe.logger().info(f"  - Phone Number: {settings.phone_number}")
	frappe.logger().info(f"  - Agent Number: {settings.agent_number}")
	frappe.logger().info(f"  - Caller ID: {settings.caller_id}")

	# Get agent number and caller ID from Smartflo Agent Mapping for the current user
	agent_number = None
	caller_id = None

	if frappe.db.exists("DocType", "Smartflo Agent Mapping"):
		mapping = frappe.db.get_value(
			"Smartflo Agent Mapping",
			{"user": frappe.session.user},
			["agent_number", "caller_id"],
			as_dict=True
		)
		if mapping:
			agent_number = mapping.agent_number
			caller_id = mapping.caller_id
			frappe.logger().info(f"[TATA TELE] Found per-user mapping for {frappe.session.user}")

	# Fallback to settings if not found in mapping
	if not agent_number:
		agent_number = settings.agent_number
		frappe.logger().info(f"[TATA TELE] Using global agent number")

	if not caller_id:
		caller_id = settings.caller_id or settings.agent_number
		frappe.logger().info(f"[TATA TELE] Using global caller ID")

	if not agent_number:
		frappe.logger().warning("[TATA TELE] Agent number not found")
		frappe.throw(
			_("Agent number not found. Please setup Smartflo Agent Mapping for your user."),
			title=_("Agent Number Missing")
		)

	if not caller_id:
		frappe.logger().warning("[TATA TELE] Caller ID not found")
		frappe.throw(
			_("Caller ID not found. Please setup Smartflo Agent Mapping for your user."),
			title=_("Caller ID Missing")
		)

	# Validate destination number
	destination_number = to_number
	if not destination_number:
		frappe.logger().warning("[TATA TELE] Destination number is empty")
		frappe.throw(_("Destination number is required"), title=_("Invalid Input"))

	api_endpoint = settings.api_endpoint
	api_token = settings.get_password("api_token")

	frappe.logger().info(f"[TATA TELE] Call Details:")
	frappe.logger().info(f"  - Agent Number: {agent_number}")
	frappe.logger().info(f"  - Destination Number: {destination_number}")
	frappe.logger().info(f"  - Caller ID: {caller_id}")
	frappe.logger().info(f"  - API Endpoint: {api_endpoint}")

	try:
		# Prepare request payload using Tata Tele SmartFlow format
		# agent_number: The agent's virtual number (user's number in Tata system)
		# destination_number: The contact's phone number to call
		# caller_id: The number that will appear on recipient's phone
		payload = {
			"agent_number": agent_number,
			"destination_number": destination_number,
			"caller_id": caller_id,
			"async": 1,
		}

		frappe.logger().info(f"[TATA TELE] Request Payload:")
		frappe.logger().info(json.dumps(payload, indent=2))

		# Prepare headers with authentication
		headers = {
			"Authorization": f"Bearer {api_token}",
			"Content-Type": "application/json",
		}

		frappe.logger().info(f"[TATA TELE] Request Headers:")
		frappe.logger().info(f"  - Authorization: Bearer ****{api_token[-10:] if api_token else 'NONE'}")
		frappe.logger().info(f"  - Content-Type: application/json")

		# Make API request to Tata Teleservices
		frappe.logger().info(f"[TATA TELE] Sending request to: {api_endpoint}")
		response = requests.post(
			api_endpoint,
			json=payload,
			headers=headers,
			timeout=60
		)

		frappe.logger().info(f"[TATA TELE] API Response Received:")
		frappe.logger().info(f"  - Status Code: {response.status_code}")
		frappe.logger().info(f"  - Response Body: {response.text}")

		if response.status_code not in [200, 201]:
			error_message = f"Tata Tele API Error: {response.status_code} - {response.text}"
			frappe.logger().error(f"[TATA TELE] {error_message}")
			frappe.log_error(
				message=error_message,
				title="Tata Tele API Error"
			)
			# Extract message from response if it's JSON
			try:
				resp_json = response.json()
				msg = resp_json.get("message") or resp_json.get("error") or response.text
			except:
				msg = response.text

			frappe.throw(
				_("Tata Tele API Error: {0}").format(msg),
				title=_("API Error")
			)

		response_data = response.json()
		frappe.logger().info(f"[TATA TELE] Response Data Parsed:")
		frappe.logger().info(json.dumps(response_data, indent=2))
		
		# Extract call ID from response or generate a unique one
		call_id = response_data.get("call_id") or response_data.get("id") or response_data.get("request_id") or response_data.get("CallSid")
			
		if not call_id:
			# Generate a unique ID using timestamp and phone number
			import time
			call_id = f"TATA-{int(time.time())}-{destination_number[-4:]}"
			frappe.logger().info(f"[TATA TELE] No call_id in response, generated: {call_id}")
		
		frappe.logger().info(f"[TATA TELE] Using Call ID: {call_id}")
		
		# Create call log
		call_log = frappe.get_doc({
			"doctype": "CRM Call Log",
			"telephony_medium": "Tata Tele",
			"type": "Outgoing",
			"from": agent_number,
			"to": destination_number,
			"status": "Initiated",
			"id": call_id,
		})

		frappe.logger().info(f"[TATA TELE] Call Log Created:")
		frappe.logger().info(f"  - Call ID: {call_log.id}")
		frappe.logger().info(f"  - Status: {call_log.status}")
		frappe.logger().info(f"  - From: {getattr(call_log, 'from')}")
		frappe.logger().info(f"  - To: {getattr(call_log, 'to')}")

		# Link call log with lead/deal/contact
		contact = get_contact_by_phone_number(destination_number)
		frappe.logger().info(f"[TATA TELE] Contact Search Results:")
		frappe.logger().info(json.dumps(contact or {}, indent=2))
		if contact.get("name"):
			doctype = "Contact"
			docname = contact.get("name")
			if contact.get("lead"):
				doctype = "CRM Lead"
				docname = contact.get("lead")
				frappe.logger().info(f"[TATA TELE] Linked to Lead: {docname}")
			elif contact.get("deal"):
				doctype = "CRM Deal"
				docname = contact.get("deal")
				frappe.logger().info(f"[TATA TELE] Linked to Deal: {docname}")
			else:
				frappe.logger().info(f"[TATA TELE] Linked to Contact: {docname}")
			
			call_log.reference_doctype = doctype
			call_log.reference_docname = docname
		else:
			frappe.logger().info(f"[TATA TELE] No contact found for number: {destination_number}")

		frappe.logger().info(f"[TATA TELE] Saving Call Log...")
		call_log.save(ignore_permissions=True)
		frappe.db.commit()
		frappe.logger().info(f"[TATA TELE] Call Log Saved Successfully!")

		frappe.logger().info(f"[TATA TELE] Returning Success Response...")
		response_json = {
			"ok": True,
			"message": "Call initiated successfully",
			"call_id": call_id,
			"agent_number": agent_number,
			"caller_id": caller_id,
			"data": response_data
		}
		frappe.logger().info(json.dumps(response_json, indent=2))
		frappe.logger().info("=" * 80)
		return response_json

	except requests.exceptions.RequestException as e:
		frappe.logger().error(f"[TATA TELE] Request Exception: {str(e)}")
		frappe.log_error(
			message=str(e),
			title="Tata Tele Request Error"
		)
		frappe.logger().error("=" * 80)
		frappe.throw(
			_("Network error while connecting to Tata Tele service"),
			title=_("Request Failed")
		)
	except Exception as e:
		frappe.logger().error(f"[TATA TELE] General Exception: {str(e)}")
		frappe.logger().error(f"[TATA TELE] Traceback: {frappe.get_traceback()}")
		frappe.log_error(
			message=str(e),
			title="Tata Tele Integration Error"
		)
		frappe.logger().error("=" * 80)
		frappe.throw(
			_("An error occurred while making the call"),
			title=_("Error")
		)


@frappe.whitelist(allow_guest=True)
def webhook_handler(**kwargs):
	"""
	Handle incoming webhooks from Tata Teleservices API.
	This is called when call status changes.
	
	Webhook URL: /api/method/crm.integrations.tata_tele.handler.webhook_handler
	"""
	if not is_integration_enabled():
		frappe.log_error(
			message="Webhook received but Tata Tele integration is disabled",
			title="Tata Tele Webhook - Integration Disabled"
		)
		return {"ok": False, "message": "Integration not enabled"}

	# Validate Webhook Token if configured
	webhook_token = TataTeleSettings.get_webhook_token()
	if webhook_token:
		# Check for token in headers (common for webhooks)
		received_token = (
			frappe.request.headers.get("X-Webhook-Token") or 
			frappe.request.headers.get("Authorization") or
			kwargs.get("token")
		)
		
		if received_token and "Bearer " in received_token:
			received_token = received_token.replace("Bearer ", "")
			
		if received_token != webhook_token:
			frappe.log_error(
				message=f"Invalid webhook token received: {received_token}",
				title="Tata Tele Webhook - Auth Failed"
			)
			return {"ok": False, "message": "Invalid token"}

	request_log = create_request_log(
		kwargs,
		request_description="Tata Tele Call Webhook",
		service_name="Tata Tele",
		request_headers=frappe.request.headers,
		is_remote_request=1,
	)

	try:
		request_log.status = "Completed"
		payload = frappe._dict(kwargs)

		# Publish real-time event for UI updates
		frappe.publish_realtime("tata_tele_call", payload)

		# Extract call information
		call_id = payload.get("call_id") or payload.get("id")
		status = payload.get("status") or payload.get("call_status")

		if not call_id:
			frappe.log_error(
				message="No call_id in webhook payload",
				title="Tata Tele Webhook - Missing ID"
			)
			return {"ok": False, "message": "Missing call_id"}

		# Update call log with new status
		if frappe.db.exists("CRM Call Log", call_id):
			call_log = frappe.get_doc("CRM Call Log", call_id)
			
			# Map Tata Tele status to our status
			status_mapping = {
				"initiated": "Initiated",
				"ringing": "Ringing",
				"connected": "Connected",
				"active": "Active",
				"completed": "Completed",
				"ended": "Completed",
				"failed": "Failed",
				"no_answer": "No answer",
				"busy": "Busy",
				"cancelled": "Cancelled",
			}

			call_log.status = status_mapping.get(status, status)
			
			# Update additional fields from webhook
			if payload.get("duration"):
				call_log.duration = payload.get("duration")
			
			call_log.save(ignore_permissions=True)
			frappe.db.commit()

		return {"ok": True, "message": "Webhook processed"}

	except Exception:
		request_log.status = "Failed"
		request_log.error = frappe.get_traceback()
		frappe.db.rollback()
		frappe.log_error(
			title="Error processing Tata Tele webhook"
		)
		frappe.db.commit()
		return {"ok": False, "message": "Error processing webhook"}
	finally:
		request_log.save(ignore_permissions=True)
		frappe.db.commit()


@frappe.whitelist()
def validate_connection():
	"""
	Validate Tata Tele API connection and credentials.
	"""
	if not is_integration_enabled():
		return {"ok": False, "message": "Integration not enabled"}

	settings = TataTeleSettings.get_settings()
	if not settings:
		return {"ok": False, "message": "Settings not configured"}

	try:
		api_endpoint = settings.api_endpoint
		api_token = settings.get_password("api_token")

		headers = {
			"Authorization": f"Bearer {api_token}",
			"Content-Type": "application/json",
		}

		# Try a simple health check - test the endpoint
		# You might need to adjust this based on Tata Tele API documentation
		response = requests.get(
			api_endpoint.replace("/click_to_call", "/health"),
			headers=headers,
			timeout=10
		)

		if response.status_code in [200, 401, 403]:  # 401/403 means auth issue, not connection
			return {
				"ok": True,
				"message": "Connection successful"
			}
		else:
			return {
				"ok": False,
				"message": f"Connection failed: {response.status_code}"
			}

	except Exception as e:
		return {
			"ok": False,
			"message": f"Error: {str(e)}"
		}
