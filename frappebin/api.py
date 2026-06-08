# Copyright (c) 2026, mehmehsloth and contributors
# For license information, please see license.txt
#
# Public API for Frappebin snippets.
#
# Security model:
#   - All access control lives here (not in DocType permissions). DocType perms stay
#     locked to System Manager; these methods read/write with ignore_permissions after
#     running their own checks.
#   - secret_key / edit_token are generated server-side (see snippet.py) and never
#     accepted as authoritative input for writes other than proving ownership.
#   - Unlisted/Private misses return 404 (not 403) so existence is not leaked.

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

SNIPPET = "Snippet"

# Fields safe to return to any viewer who passed the access check.
# NOTE: `owner` is deliberately excluded — it is the creator's User ID (email) and
# must not be disclosed to viewers. Ownership is conveyed via the `is_owner` flag.
PUBLIC_FIELDS = (
	"name",
	"title",
	"content",
	"language",
	"visibility",
	"view_count",
	"expires_on",
	"burn_after_read",
	"creation",
	"modified",
)

# Fields a client is allowed to set/change.
WRITABLE_FIELDS = ("title", "content", "language", "visibility", "expires_on", "burn_after_read")


def _not_found() -> None:
	frappe.throw(_("Snippet not found."), frappe.DoesNotExistError)


def _get_doc(name: str):
	if not frappe.db.exists(SNIPPET, name):
		_not_found()
	return frappe.get_doc(SNIPPET, name)


def _is_authenticated_owner(doc) -> bool:
	user = frappe.session.user
	return user and user != "Guest" and doc.owner == user


def _check_view_access(doc, key: str | None) -> bool:
	"""Return True if the requester may view this snippet."""
	if doc.visibility == "Public":
		return True
	if _is_authenticated_owner(doc):
		return True
	# Unlisted and Private both require the secret key for non-owners.
	import hmac

	return bool(key) and bool(doc.secret_key) and hmac.compare_digest(str(key), str(doc.secret_key))


def _serialize(doc, *, is_owner: bool) -> dict:
	data = {f: doc.get(f) for f in PUBLIC_FIELDS}
	data["is_owner"] = is_owner
	# Resolve the highlighter alias for the frontend.
	data["highlight_alias"] = (
		frappe.db.get_value("Snippet Language", doc.language, "highlight_alias") or "plaintext"
	)
	return data


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="frappebin_create", limit=20, seconds=60, ip_based=True)
def create_snippet(
	content: str,
	title: str | None = None,
	language: str = "plaintext",
	visibility: str = "Unlisted",
	expires_on: str | None = None,
	burn_after_read: int = 0,
) -> dict:
	"""Create a snippet. Open to guests. Returns the new name plus owner-only tokens."""
	if visibility not in ("Public", "Unlisted", "Private"):
		frappe.throw(_("Invalid visibility."), frappe.ValidationError)

	doc = frappe.new_doc(SNIPPET)
	doc.update(
		{
			"title": title,
			"content": content,
			"language": language,
			"visibility": visibility,
			"expires_on": expires_on,
			"burn_after_read": int(burn_after_read or 0),
		}
	)
	doc.insert(ignore_permissions=True)

	return {
		"name": doc.name,
		"secret_key": doc.secret_key,
		"edit_token": doc.edit_token,
		"visibility": doc.visibility,
	}


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(key="frappebin_view", limit=120, seconds=60, ip_based=True)
def get_snippet(name: str, key: str | None = None) -> dict:
	"""Fetch a snippet for viewing, enforcing the visibility gate."""
	doc = _get_doc(name)

	# Expired snippets are treated as gone (and cleaned up opportunistically).
	if doc.is_expired():
		doc.delete(ignore_permissions=True)
		frappe.db.commit()
		_not_found()

	if not _check_view_access(doc, key):
		_not_found()

	is_owner = _is_authenticated_owner(doc)
	data = _serialize(doc, is_owner=is_owner)

	# Burn-after-read: a successful guest/non-owner view consumes the snippet.
	if doc.burn_after_read and not is_owner:
		doc.delete(ignore_permissions=True)
		frappe.db.commit()
		data["burned"] = True
		return data

	# Best-effort view counter; never block the read on it.
	frappe.db.set_value(SNIPPET, doc.name, "view_count", (doc.view_count or 0) + 1, update_modified=False)
	frappe.db.commit()
	return data


def _authorize_edit(doc, edit_token: str | None) -> None:
	if _is_authenticated_owner(doc):
		return
	if edit_token and doc.edit_token and edit_token == doc.edit_token:
		return
	frappe.throw(_("You are not allowed to modify this snippet."), frappe.PermissionError)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="frappebin_update", limit=60, seconds=60, ip_based=True)
def update_snippet(name: str, edit_token: str | None = None, **fields: object) -> dict:
	"""Update a snippet. Allowed for the authenticated owner or a matching edit_token."""
	doc = _get_doc(name)
	_authorize_edit(doc, edit_token)

	for field in WRITABLE_FIELDS:
		if field in fields:
			doc.set(field, fields[field])

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name, "visibility": doc.visibility}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="frappebin_delete", limit=60, seconds=60, ip_based=True)
def delete_snippet(name: str, edit_token: str | None = None) -> dict:
	"""Delete a snippet. Allowed for the authenticated owner or a matching edit_token."""
	doc = _get_doc(name)
	_authorize_edit(doc, edit_token)
	doc.delete(ignore_permissions=True)
	frappe.db.commit()
	return {"deleted": name}


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
@rate_limit(key="frappebin_raw", limit=120, seconds=60, ip_based=True)
def get_raw(name: str, key: str | None = None) -> None:
	"""Return the raw snippet body as text/plain (curl/wget friendly)."""
	doc = _get_doc(name)

	if doc.is_expired():
		doc.delete(ignore_permissions=True)
		frappe.db.commit()
		_not_found()

	if not _check_view_access(doc, key):
		_not_found()

	extension = frappe.db.get_value("Snippet Language", doc.language, "file_extension") or "txt"

	frappe.local.response["type"] = "download"
	frappe.local.response["filecontent"] = (doc.content or "").encode("utf-8")
	frappe.local.response["content_type"] = "text/plain"
	frappe.local.response["display_content_as"] = "inline"
	frappe.local.response["filename"] = f"{doc.name}.{extension}"


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def get_languages() -> list[dict]:
	"""List available languages for the create/edit form (guest-accessible)."""
	return frappe.get_all(
		"Snippet Language",
		fields=["name as value", "language_name as label", "highlight_alias", "file_extension"],
		order_by="language_name asc",
	)
