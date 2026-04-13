import mimetypes
from datetime import datetime
from pathlib import Path
from secrets import token_hex
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

    def _get_storage_root(self):
        root = self.config.get_param("logistics_trace_evidence.image_storage_root", default="") or ""
        root = root.strip()
        return Path(root or self._default_storage_root())

    def _get_public_base_url(self):
        base_url = self.config.get_param("logistics_trace_evidence.image_public_base_url", default="") or ""
        base_url = base_url.strip().rstrip("/")
        if base_url:
            return base_url
        return (self.config.get_param("web.base.url", default="") or "").strip().rstrip("/")

    def ensure_storage_ready(self):
        storage_root = self._get_storage_root()
        storage_root.mkdir(parents=True, exist_ok=True)
        if not storage_root.exists() or not storage_root.is_dir():
            raise UserError(_("Image storage root is invalid: %s") % storage_root)
        return {"storage_root": str(storage_root)}

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
        self.ensure_storage_ready()
        image_access_key = self._build_access_key()
        stored_file_name = self._build_stored_file_name(extension)
        relative_path = self._build_relative_path(stored_file_name)
        absolute_path = self._get_storage_root() / relative_path
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

    def _get_absolute_path(self, image_record):
        relative_path = (image_record.storage_relative_path or "").strip()
        if not relative_path:
            raise UserError(_("Image storage path is missing."))
        return self._get_storage_root() / relative_path

    def sync_image_meta(self, image_record):
        absolute_path = self._get_absolute_path(image_record)
        if not absolute_path.exists():
            return {
                "storage_status": "missing",
            }

        content_type = image_record.mime_type or mimetypes.guess_type(
            image_record.source_filename or image_record.stored_file_name or ""
        )[0]
        return {
            "source_filename": image_record.source_filename or image_record.stored_file_name,
            "stored_file_name": image_record.stored_file_name or absolute_path.name,
            "file_ext": image_record.file_ext or absolute_path.suffix.lower(),
            "mime_type": content_type,
            "file_size": absolute_path.stat().st_size,
            "storage_provider": image_record.storage_provider or "local",
            "storage_bucket": False,
            "storage_relative_path": image_record.storage_relative_path,
            "storage_status": "active",
        }

    def read_image(self, image_record):
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

    def build_preview_url(self, image_access_key):
        base_url = self._get_public_base_url()
        if not base_url:
            return False
        return f"{base_url}/logistics_trace/evidence-images/{image_access_key}"

    def build_download_url(self, image_access_key):
        base_url = self._get_public_base_url()
        if not base_url:
            return False
        return f"{base_url}/logistics_trace/evidence-images/{image_access_key}?download=true"
