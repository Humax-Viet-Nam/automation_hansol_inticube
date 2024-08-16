import asyncio
import random
from aiohttp import web
from aiohttp_swagger import setup_swagger
from collections import defaultdict

from helper import read_file_config
from path_manage import config_file

# Global Variables
expected_content = b""
request_stats = defaultdict(int, {
    "request_count": 0,
    "total_200_responses": 0,
    "total_400_responses": 0,
    "number_request_not_correct_content": 0,
    "expected_total_request": 0
})
max_responses = {"200": 0, "400": 0}
lock = asyncio.Lock()


async def handle_post(request):
    """
    ---
    description: Handle POST request to compare file content.
    tags:
    - POST
    produces:
    - text/plain
    responses:
        "200":
            description: Successful response with request count.
        "400":
            description: Unsuccessful response.
        "500":
            description: Internal Server Error.
    """
    try:
        # Read the request body outside the lock to reduce lock contention
        data = await request.read()

        async with lock:
            # Track the number of requests
            request_stats["request_count"] += 1

            # Determine the available response codes
            available_responses = []
            if request_stats["total_200_responses"] < max_responses["200"]:
                available_responses.append(200)
            if request_stats["total_400_responses"] < max_responses["400"]:
                available_responses.append(400)

            if not available_responses:
                response_code = 200  # Default to 200 if all limits are exhausted
            else:
                response_code = random.choice(available_responses)

            # Update statistics based on the chosen response
            if response_code == 200:
                request_stats["total_200_responses"] += 1
            elif response_code == 400:
                request_stats["total_400_responses"] += 1

            # Check if content matches the expected content
            if data != expected_content:
                request_stats["number_request_not_correct_content"] += 1
                print(
                    f"Failed/Total: "
                    f"{request_stats['number_request_not_correct_content']}/{request_stats['request_count']}, "
                    f"received content: {data}"
                )

        return web.Response(status=response_code, text=f"Request count: {request_stats['request_count']}")
    except Exception as e:
        print(str(e))
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_get(request):
    """
    ---
    description: Retrieve request statistics.
    tags:
    - GET
    produces:
    - application/json
    responses:
        "200":
            description: Successful response with statistics.
        "500":
            description: Internal Server Error.
    """
    try:
        # Fetch stats without locking
        stats_snapshot = dict(request_stats)
        return web.json_response(stats_snapshot)
    except Exception as e:
        print(str(e))
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_put_reset(request):
    """
    ---
    description: Reset the request statistics and configure expected values.
    tags:
    - PUT
    consumes:
    - application/json
    produces:
    - text/plain
    parameters:
    - in: body
      name: body
      description: JSON with total request and failed percent.
      required: true
      schema:
        type: object
        properties:
          total_request:
            type: integer
          failed_percent:
            type: integer
    responses:
        "200":
            description: Successful reset.
        "500":
            description: Internal Server Error.
    """
    try:
        body_config = await request.json()

        async with lock:
            # Reset the request statistics
            request_stats.clear()
            # Configure the expected total requests and response distribution
            total_requests = int(body_config["total_request"])
            failed_percent = int(body_config["failed_percent"])

            max_responses["400"] = int(failed_percent / 100 * total_requests)
            max_responses["200"] = total_requests - max_responses["400"]

            request_stats["expected_total_request"] = total_requests
            request_stats["request_count"] = 0
            request_stats["total_200_responses"] = 0
            request_stats["total_400_responses"] = 0
            request_stats["number_request_not_correct_content"] = 0
            print(f"Set expected total request = {total_requests}, failed_percent = {failed_percent}")

        return web.Response(status=200, text="Update success.")
    except Exception as e:
        print(str(e))
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_put_update_expected_file_content(request):
    """
    ---
    description: Update the expected file content.
    tags:
    - PUT
    consumes:
    - application/octet-stream
    produces:
    - text/plain
    responses:
        "200":
            description: Successful content update.
        "500":
            description: Internal Server Error.
    """
    global expected_content
    try:
        expected_content = await request.read()
        print(f"Set expected file content success: {expected_content}")
        return web.Response(status=200, text="Update file content success.")
    except Exception as e:
        print(str(e))
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def create_app():
    app = web.Application()
    app.add_routes([
        web.post('/file', handle_post),
        web.get('/stats', handle_get),
        web.put('/reset_stats', handle_put_reset),
        web.put('/file_content', handle_put_update_expected_file_content)
    ])
    setup_swagger(app)  # Set up Swagger documentation
    return app

if __name__ == '__main__':
    hansol_app = asyncio.run(create_app())
    config_dict = read_file_config(config_file)
    web.run_app(hansol_app, host='0.0.0.0', port=int(config_dict["SERVER"]["port"]))
