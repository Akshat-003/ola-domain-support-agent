import asyncio
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    project_root = Path(__file__).resolve().parent.parent

    transport = StdioTransport(
        command="python",
        args=["-m", "mcp_tools.server"],
        cwd=str(project_root)
    )

    async with Client(transport) as client:
        print("Connected to Ola Support MCP Server!")

        tools = await client.list_tools()

        print("\nAvailable MCP Tools:")
        for tool in tools:
            print("-", tool.name)

        for ticket_id in ["OLA-1001", "OLA-1002"]:
            print(f"\nChecking ticket: {ticket_id}")

            result = await client.call_tool(
                "get_ticket_status",
                {"record_id": ticket_id}
            )

            print("Ticket Details:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())