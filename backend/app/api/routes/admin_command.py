from fastapi import APIRouter

from app.schemas.admin_command import AdminCommandRequest, AdminCommandResponse

router = APIRouter(prefix="/api/admin-command", tags=["admin-command"])


@router.post("", response_model=AdminCommandResponse)
def parse_admin_command(payload: AdminCommandRequest) -> AdminCommandResponse:
    return AdminCommandResponse(
        intent="not_implemented",
        summary="Admin command parser is not implemented yet.",
        data=[],
        suggested_actions=["Build admin_query_parser prompt and customer search execution"],
    )
