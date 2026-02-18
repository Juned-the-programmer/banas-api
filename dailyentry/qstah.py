from .task import verify_and_commit_pending_entries, bulk_import_daily_entries
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# Verify Pending Daily Entries
@api_view(["POST"])
@permission_classes([AllowAny])
def task_verify_pending_daily_entries(request):
    """
    QStash callback: Verify and commit pending daily entries.
    Payload: { args: [[{id, customer, coolers, date_added}, ...]] }
    """
    try:
        args = request.data.get("args", [])
        entries = args[0] if args else []
        if not entries:
            return Response({"error": "Missing entries"}, status=status.HTTP_400_BAD_REQUEST)

        verify_and_commit_pending_entries.__wrapped__(entries)
        logger.info(f"task_verify_pending: processed {len(entries)} entries")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"task_verify_pending failed: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Bulk Import Daily Entries
@api_view(["POST"])
@permission_classes([AllowAny])
def task_bulk_import_daily_entries(request):
    """
    QStash callback: Bulk import daily entries from admin.
    Payload: { args: [[{customer, cooler}, ...]] }
    """
    try:
        args = request.data.get("args", [])
        entries = args[0] if args else []
        if not entries:
            return Response({"error": "Missing entries"}, status=status.HTTP_400_BAD_REQUEST)

        bulk_import_daily_entries.__wrapped__(entries)
        logger.info(f"task_bulk_import: imported {len(entries)} entries")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"task_bulk_import failed: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)