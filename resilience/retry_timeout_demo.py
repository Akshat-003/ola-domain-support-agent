import asyncio
import random
import time


# Retry configuration
MAX_ATTEMPTS = 3
INITIAL_INTERVAL = 1
MAX_INTERVAL = 4
JITTER = 0.2


# Simulate an operation that temporarily fails
attempt_count = 0


async def unreliable_operation():

    global attempt_count
    attempt_count += 1

    print(f"Attempt {attempt_count}")

    if attempt_count < 3:
        raise ConnectionError("Temporary service failure")

    return "Operation completed successfully!"


# Exponential backoff retry
async def retry_operation():

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:
            result = await unreliable_operation()
            print(result)
            return result

        except ConnectionError as error:

            print("Error:", error)

            if attempt == MAX_ATTEMPTS:
                print("All retry attempts failed.")
                raise

            delay = min(
                INITIAL_INTERVAL * (2 ** (attempt - 1)),
                MAX_INTERVAL
            )

            delay += random.uniform(0, JITTER)

            print(f"Retrying after {delay:.2f} seconds...")
            await asyncio.sleep(delay)


# Simulate a slow node
async def slow_node():

    print("\nSlow node started...")
    await asyncio.sleep(3)

    return "Slow node completed"


# Per-node timeout
async def test_node_timeout():

    print("\n--- PER-NODE TIMEOUT TEST ---")

    try:
        result = await asyncio.wait_for(
            slow_node(),
            timeout=1
        )

        print(result)

    except asyncio.TimeoutError:
        print("Node timed out after 1 second!")


# Simulate a workflow
async def workflow():

    print("\nWorkflow started...")

    await asyncio.sleep(2)
    print("Workflow step 1 completed")

    await asyncio.sleep(2)
    print("Workflow step 2 completed")

    return "Workflow completed"


# Global timeout
async def test_global_timeout():

    print("\n--- GLOBAL TIMEOUT TEST ---")

    try:
        result = await asyncio.wait_for(
            workflow(),
            timeout=3
        )

        print(result)

    except asyncio.TimeoutError:
        print("Global workflow timeout after 3 seconds!")


async def main():

    print("\n--- RETRY TEST ---")

    await retry_operation()

    await test_node_timeout()

    await test_global_timeout()


if __name__ == "__main__":
    asyncio.run(main())