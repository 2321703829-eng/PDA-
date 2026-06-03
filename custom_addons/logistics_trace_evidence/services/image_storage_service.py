import base64
import binascii
import mimetypes
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from urllib.parse import urlparse
from uuid import uuid4

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import config


class LogisticsEvidenceImageStorage:
    _ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    _ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
    }

    def __init__(self, env):
        self.env = env
        self.config = env["ir.config_parameter"].sudo()

    def _default_storage_root(self):
        data_dir = config.get("data_dir")
        if data_dir:
            return str(Path(data_dir) / "logistics_trace_images")
        return str(Path.home() / ".local" / "share" / "Odoo" / "logistics_trace_images")

    def get_storage_root(self):
        root = self.config.get_param("logistics_trace_evidence.image_storage_root", default="") or ""
        root = root.strip()
        return Path(root or self._default_storage_root())

    def _get_storage_root(self):
        return self.get_storage_root()

    def _get_public_base_url(self):
        base_url = self.config.get_param("logistics_trace_evidence.image_public_base_url", default="") or ""
        base_url = base_url.strip().rstrip("/")
        if base_url:
            return base_url
        return (self.config.get_param("web.base.url", default="") or "").strip().rstrip("/")

    def ensure_storage_ready(self):
        storage_root = self.get_storage_root()
        storage_root.mkdir(parents=True, exist_ok=True)
        if not storage_root.exists() or not storage_root.is_dir():
            raise UserError(_("Image storage root is invalid: %s") % storage_root)
        return storage_root

    def _sanitize_file_name(self, file_name):
        safe_name = Path(file_name or "").name.strip()
        if not safe_name:
            raise UserError(_("Image file name is required."))
        return safe_name

    def _validate_file(self, *, file_name, content, content_type):
        safe_name = self._sanitize_file_name(file_name)
        extension = Path(safe_name).suffix.lower()
        if extension not in self._ALLOWED_EXTENSIONS:
            raise UserError(_("Unsupported image extension: %s") % extension)
        if content_type not in self._ALLOWED_CONTENT_TYPES:
            raise UserError(_("Unsupported image content type: %s") % content_type)
        if not content:
            raise UserError(_("Image content is empty."))
        return safe_name, extension

    @staticmethod
    def _build_access_key():
        return f"img_{token_hex(12)}{uuid4().hex[:8]}"

    @staticmethod
    def _build_stored_file_name(extension):
        return f"{uuid4().hex}{extension}"

    def _build_relative_path(self, stored_file_name):
        return str(Path(datetime.now().strftime("%Y/%m/%d")) / stored_file_name)

    def upload_image(self, *, file_name, content, content_type):
        safe_name, extension = self._validate_file(
            file_name=file_name,
            content=content,
            content_type=content_type,
        )
        storage_root = self.ensure_storage_ready()
        image_access_key = self._build_access_key()
        stored_file_name = self._build_stored_file_name(extension)
        relative_path = self._build_relative_path(stored_file_name)
        absolute_path = storage_root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return {
            "image_access_key": image_access_key,
            "file_name": stored_file_name,
            "original_file_name": safe_name,
            "file_ext": extension,
            "storage_provider": "local",
            "storage_bucket": False,
            "storage_relative_path": relative_path.replace("\\", "/"),
            "storage_status": "active",
            "content_type": content_type,
            "content_length": len(content),
        }

    def import_existing_image(self, *, image_access_key, file_name, content, content_type):
        safe_name, extension = self._validate_file(
            file_name=file_name,
            content=content,
            content_type=content_type,
        )
        storage_root = self.ensure_storage_ready()
        stored_file_name = self._build_stored_file_name(extension)
        relative_path = self._build_relative_path(stored_file_name)
        absolute_path = storage_root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return {
            "image_access_key": (image_access_key or "").strip() or self._build_access_key(),
            "file_name": stored_file_name,
            "original_file_name": safe_name,
            "file_ext": extension,
            "storage_provider": "local",
            "storage_bucket": False,
            "storage_relative_path": relative_path.replace("\\", "/"),
            "storage_status": "active",
            "content_type": content_type,
            "content_length": len(content),
        }

    def _resolve_storage_path(self, relative_path):
        storage_root = self.get_storage_root().resolve()
        candidate = storage_root / (relative_path or "")
        try:
            resolved = candidate.resolve(strict=False)
        except OSError as error:
            raise UserError(_("Invalid image storage path: %s") % error) from error
        try:
            resolved.relative_to(storage_root)
        except ValueError as error:
            raise UserError(_("Image storage path is outside storage root.")) from error
        return resolved

    def _get_absolute_path(self, image_record):
        relative_path = (image_record.storage_relative_path or "").strip()
        if not relative_path:
            raise UserError(_("Image storage path is missing."))
        return self._resolve_storage_path(relative_path)

    def sync_image_meta(self, image_record):
        if image_record.storage_provider == "legacy_url":
            return {
                "storage_status": "active",
            }
        absolute_path = self._get_absolute_path(image_record)
        if not absolute_path.exists():
            return {
                "storage_status": "missing",
            }
        content_type = image_record.mime_type or mimetypes.guess_type(
            image_record.source_filename or image_record.stored_file_name or ""
        )[0]
        return {
            "source_filename": image_record.source_filename or image_record.stored_file_name or absolute_path.name,
            "stored_file_name": image_record.stored_file_name or absolute_path.name,
            "file_ext": image_record.file_ext or absolute_path.suffix.lower(),
            "mime_type": content_type,
            "file_size": absolute_path.stat().st_size,
            "storage_provider": image_record.storage_provider or "local",
            "storage_bucket": False,
            "storage_relative_path": image_record.storage_relative_path,
            "storage_status": "active",
        }

    def sync_evidence_meta(self, evidence_record):
        values = self.sync_image_meta(evidence_record)
        if "storage_status" in values and "state" not in values:
            values["state"] = "available" if values["storage_status"] == "active" else values["storage_status"]
        return values

    def read_image(self, image_record):
        if image_record.storage_provider == "legacy_url":
            return self.read_legacy_image(
                image_record.source_filename or image_record.stored_file_name or image_record.image_access_key,
                image_record.legacy_full_url,
                image_record.legacy_preview_url,
            )
        absolute_path = self._get_absolute_path(image_record)
        if not absolute_path.exists():
            image_record.sudo().write({"storage_status": "missing"})
            raise UserError(_("Image file does not exist on server storage."))
        content = absolute_path.read_bytes()
        content_type = image_record.mime_type or mimetypes.guess_type(
            image_record.source_filename or image_record.stored_file_name or ""
        )[0]
        return {
            "file_name": image_record.source_filename or image_record.stored_file_name or absolute_path.name,
            "content_type": content_type or "application/octet-stream",
            "content_length": len(content),
            "content": content,
        }

    def read_legacy_image(self, file_name, full_url, preview_url):
        data_payload = self._read_legacy_data_url(file_name, full_url or preview_url)
        if data_payload:
            return data_payload
        local_path = self._resolve_legacy_local_path(full_url or preview_url)
        if not local_path or not local_path.exists():
            raise UserError(_("Legacy image file does not exist on local storage."))
        content = local_path.read_bytes()
        content_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
        return {
            "file_name": Path(file_name or local_path.name).name,
            "content_type": content_type,
            "content_length": len(content),
            "content": content,
        }

    def _read_legacy_data_url(self, file_name, raw_url):
        value = (raw_url or "").strip()
        if not value.startswith("data:"):
            return False
        header, separator, encoded = value.partition(",")
        if not separator:
            raise UserError(_("Legacy image data URL is invalid."))
        meta = header[5:]
        meta_parts = [part for part in meta.split(";") if part]
        content_type = meta_parts[0] if meta_parts else "application/octet-stream"
        is_base64 = any(part.lower() == "base64" for part in meta_parts[1:])
        if not is_base64:
            raise UserError(_("Legacy image data URL must be base64 encoded."))
        try:
            content = base64.b64decode(encoded)
        except (binascii.Error, ValueError) as error:
            raise UserError(_("Legacy image data URL is not valid base64 content.")) from error
        safe_name = Path(file_name or "evidence_image").name or "evidence_image"
        if not Path(safe_name).suffix:
            extension = mimetypes.guess_extension(content_type or "") or ".bin"
            safe_name = f"{safe_name}{extension}"
        return {
            "file_name": safe_name,
            "content_type": content_type or "application/octet-stream",
            "content_length": len(content),
            "content": content,
        }

    def _resolve_legacy_local_path(self, raw_url):
        value = (raw_url or "").strip()
        if not value:
            return False
        if value.startswith("file:///"):
            return Path(value.replace("file:///", "", 1))
        if value.startswith("file://"):
            return Path(value.replace("file://", "", 1))
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https"):
            return False
        if value.startswith("/"):
            path = Path(value)
            if path.exists():
                return path
            return False
        candidate = Path(value)
        if candidate.is_absolute():
            return candidate
        return False

    def build_preview_url(self, image_access_key):
        if not image_access_key:
            return False
        path = f"/logistics_trace/evidence-images/{image_access_key}"
        base_url = self._get_public_base_url()
        return f"{base_url}{path}" if base_url else path

    def build_download_url(self, image_access_key):
        if not image_access_key:
            return False
        return f"/logistics_trace/evidence-images/{image_access_key}?download=true"

    def build_full_url(self, image_access_key):
        return self.build_preview_url(image_access_key)
