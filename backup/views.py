"""
Backup & Restore views.

GET  /api/backup/   → streams backup_YYYY-MM-DD.zip
POST /api/restore/  → accepts the same zip and restores everything

ZIP layout:
    db_dump.json       ← Django dumpdata (all models, natural keys)
    qr_codes/
        Alice_Smith_qr_code.png
        ...
"""

from datetime import date
import io
import logging
import os
import zipfile

from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

QR_CODES_DIR = os.path.join(settings.MEDIA_ROOT, "qr_codes")


class BackupView(APIView):
    """
    GET /api/backup/
    Downloads a ZIP file containing:
      - db_dump.json  (full dumpdata with natural keys)
      - qr_codes/*.png
    """

    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request):
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            # ── 1. Database dump ───────────────────────────────────────────
            db_buffer = io.StringIO()
            call_command(
                "dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "--indent=2",
                exclude=["contenttypes", "auth.permission"],
                stdout=db_buffer,
            )
            zf.writestr("db_dump.json", db_buffer.getvalue())
            logger.info("Backup: DB dump written to zip")

            # ── 2. QR code images ──────────────────────────────────────────
            qr_count = 0
            if os.path.isdir(QR_CODES_DIR):
                for filename in os.listdir(QR_CODES_DIR):
                    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                        full_path = os.path.join(QR_CODES_DIR, filename)
                        zf.write(full_path, arcname=f"qr_codes/{filename}")
                        qr_count += 1

            logger.info("Backup: %d QR images added to zip", qr_count)

        buffer.seek(0)
        filename = f"backup_{date.today()}.zip"
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class RestoreView(APIView):
    """
    POST /api/restore/
    Body: multipart/form-data  →  file=<backup_YYYY-MM-DD.zip>

    Process:
      1. Validate the zip contains db_dump.json
      2. Flush all app data (preserving contenttypes & auth)
      3. Load db_dump.json via loaddata
      4. Overwrite media/qr_codes/ with images from the zip
    """

    parser_classes = [MultiPartParser]

    def post(self, request):
        # ── Secret token check ────────────────────────────────────────────
        # Since no admin account exists during a fresh restore, we use an env-based
        # token instead of JWT. Set RESTORE_SECRET in your .env and pass it as
        # the X-Restore-Token header.
        expected_secret = getattr(settings, "RESTORE_SECRET", "")
        provided_secret = request.headers.get("X-Restore-Token", "")
        if not expected_secret or provided_secret != expected_secret:
            logger.warning("RestoreView: rejected request with invalid or missing token")
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file uploaded. Send the backup zip as 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        if not uploaded_file.name.endswith(".zip"):
            return Response({"error": "Uploaded file must be a .zip archive."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zip_bytes = io.BytesIO(uploaded_file.read())

            with zipfile.ZipFile(zip_bytes, "r") as zf:
                names = zf.namelist()

                # Validate the zip has what we expect
                if "db_dump.json" not in names:
                    return Response(
                        {"error": "Invalid backup: db_dump.json not found in zip."}, status=status.HTTP_400_BAD_REQUEST
                    )

                # ── 1. Flush existing app data ─────────────────────────────
                # Preserve contenttypes and auth.permission so Django stays healthy
                call_command(
                    "flush",
                    "--no-input",
                    "--database=default",
                )
                logger.info("Restore: DB flushed")

                # ── 2. Load database fixture ───────────────────────────────
                fixture_bytes = zf.read("db_dump.json")
                # loaddata needs a real file; write to a temp location

                # loaddata needs a real file; write to a temp location
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="wb") as tmp:
                    tmp.write(fixture_bytes)
                    tmp_path = tmp.name

                try:
                    call_command("loaddata", tmp_path)
                    logger.info("Restore: fixture loaded from %s", tmp_path)
                finally:
                    os.unlink(tmp_path)  # always clean up

                # ── 3. Restore QR code images ──────────────────────────────
                os.makedirs(QR_CODES_DIR, exist_ok=True)
                qr_count = 0
                for name in names:
                    if name.startswith("qr_codes/") and not name.endswith("/"):
                        filename = os.path.basename(name)
                        dest_path = os.path.join(QR_CODES_DIR, filename)
                        with open(dest_path, "wb") as out:
                            out.write(zf.read(name))
                        qr_count += 1

                logger.info("Restore: %d QR images restored", qr_count)

        except zipfile.BadZipFile:
            return Response({"error": "Uploaded file is not a valid zip archive."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.error("Restore failed: %s", exc, exc_info=True)
            return Response({"error": f"Restore failed: {exc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "status": "success",
                "message": "Database and QR codes restored successfully.",
                "qr_codes_restored": qr_count,
            }
        )
