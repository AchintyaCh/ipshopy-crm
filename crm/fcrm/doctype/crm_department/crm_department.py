import frappe
from frappe.model.document import Document

class CRMDepartment(Document):
	def validate(self):
		"""Validate department configuration"""
		if not self.route_name:
			frappe.throw("Route Name is required")
		
		# Generate URL-friendly department slug
		if not hasattr(self, 'department_slug') or not self.department_slug:
			self.department_slug = frappe.scrub(self.department_name)
	
	def on_update(self):
		"""Clear cache when department is updated"""
		frappe.cache().delete_key("user_departments")
