import csv
import io
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from users.bulk.ingest.serializers import UserBulkIngestSerializer


class UserBulkIngestViewSet(viewsets.GenericViewSet):
    serializer_class = UserBulkIngestSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @action(
        detail=False,
        methods=["post"],
        url_path="csv",
    )
    def ingest_csv(self, request):
        requesting_user = request.user

        has_import_permission = (
            requesting_user.role
            and requesting_user.role.has_permissions(["create_user", "update_user"])
        )

        if not has_import_permission:
            return Response(
                {"detail": "You do not have permission to bulk ingest users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"detail": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return Response(
                {"detail": "Uploaded file is not a valid UTF-8 encoded text file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_file = io.StringIO(decoded_file)

        try:
            dialect = csv.Sniffer().sniff(decoded_file[:1024])
            csv_file.seek(0)
            reader = csv.DictReader(csv_file, dialect=dialect)
        except csv.Error:
            return Response(
                {"detail": "Uploaded file does not appear to be a valid CSV."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        required_columns = {"name", "email", "role"}
        if not required_columns.issubset(reader.fieldnames):
            return Response(
                {"detail": "CSV must include these columns: name, email, role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary = {
            "total_rows": 0,
            "created": 0,
            "updated": 0,
            "validation_errors": 0,
            "db_errors": 0,
            "errors": [],
        }

        created_users = []
        updated_users = []

        # Do not count the CSV headers row as a row
        for row_num, row in enumerate(reader, start=1):
            summary["total_rows"] += 1

            serializer_context = self.get_serializer_context()

            serializer = self.get_serializer(data=row, context=serializer_context)
            if not serializer.is_valid():
                summary["validation_errors"] += 1
                summary["errors"].append({"row": row_num, "errors": serializer.errors})
                continue

            try:
                user = serializer.save()
                operation = serializer.context.get("operation", None)
                serializer_context.update({"operation": operation})
                serialized_user = self.get_serializer(
                    user, context=serializer_context
                ).data

                if operation == "create":
                    created_users.append(serialized_user)
                    summary["created"] += 1
                elif operation == "update":
                    updated_users.append(serialized_user)
                    summary["updated"] += 1
            except Exception as e:
                summary["db_errors"] += 1
                summary["errors"].append({"row": row_num, "errors": [str(e)]})

        response_data = {
            "summary": summary,
            "users": {"created": created_users, "updated": updated_users},
        }

        return Response(response_data)
