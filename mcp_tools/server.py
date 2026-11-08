from fastmcp import FastMCP
from agent.ticket_lookup import check_support_ticket_status

mcp = FastMCP("Ola Support Ticket Server")


@mcp.tool()
def get_ticket_status(record_id: str) -> dict:
    """Retrieve the status and escalation details of a support ticket."""
    return check_support_ticket_status(record_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")