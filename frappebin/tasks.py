# Copyright (c) 2026, mehmehsloth and contributors
# For license information, please see license.txt

import frappe


def delete_expired_snippets() -> None:
	"""Hourly job: remove snippets whose expiry has passed."""
	expired = frappe.get_all(
		"Snippet",
		filters=[
			["expires_on", "is", "set"],
			["expires_on", "<", frappe.utils.now_datetime()],
		],
		pluck="name",
	)
	for name in expired:
		frappe.delete_doc("Snippet", name, ignore_permissions=True, force=True)

	if expired:
		frappe.db.commit()
