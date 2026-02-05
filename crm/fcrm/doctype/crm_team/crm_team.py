import frappe
from frappe.model.document import Document

class CRMTeam(Document):
	def validate(self):
		"""Validate team configuration"""
		if not self.department:
			frappe.throw("Department is required")
	
	def on_update(self):
		"""Clear cache when team is updated"""
		frappe.cache().delete_key("user_departments")
