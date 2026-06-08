# Copyright (c) 2026, mehmehsloth and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# Reject snippets larger than this (raw characters). Basic abuse guard.
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # ~2 MB


class Snippet(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		burn_after_read: DF.Check
		content: DF.Code
		edit_token: DF.Data | None
		expires_on: DF.Datetime | None
		language: DF.Link | None
		secret_key: DF.Data | None
		title: DF.Data | None
		view_count: DF.Int
		visibility: DF.Literal["Public", "Unlisted", "Private"]
	# end: auto-generated types

	def before_insert(self) -> None:
		# Share/access tokens are generated server-side and never accepted from the client.
		self.secret_key = frappe.generate_hash(length=32)
		self.edit_token = frappe.generate_hash(length=32)

	def validate(self) -> None:
		if not self.title:
			self.title = "Untitled"
		if not self.language:
			self.language = "plaintext"
		if self.content and len(self.content) > MAX_CONTENT_LENGTH:
			frappe.throw(
				_("Snippet content is too large (max {0} MB).").format(MAX_CONTENT_LENGTH // (1024 * 1024)),
				frappe.ValidationError,
			)

	def is_expired(self) -> bool:
		return bool(self.expires_on) and frappe.utils.get_datetime(self.expires_on) < frappe.utils.now_datetime()
