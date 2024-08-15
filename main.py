import argparse
import asyncio
from aiohttp import web
import random

from helper import read_file_content_as_bytes

# # Define the file content you want to match
FILE_CONTENT_PATH = "resource/file_content.txt"
expected_content = b""

# Initialize a global counter
request_count = 0
total_200_responses = 0
total_400_responses = 0
max_200_responses = 0
max_400_responses = 0
expected_total_request = 0
number_request_not_correct_content = 0


async def handle_post(request):
    global request_count
    global number_request_not_correct_content
    global total_200_responses
    global total_400_responses
    try:
        # Increment the request counter
        request_count += 1

        # Read the request body
        data = await request.read()

        # Compare the body with the expected content
        list_available_response = []
        if total_200_responses + 1 <= max_200_responses:
            list_available_response.append(200)
        if total_400_responses + 1 <= max_400_responses:
            list_available_response.append(400)
        response_code = random.choice(list_available_response)
        if response_code == 200:
            total_200_responses += 1
        elif response_code == 400:
            total_400_responses += 1

        if data != expected_content:
            number_request_not_correct_content += 1
            print(f"Failed/Total: {number_request_not_correct_content}/{request_count}, received content {data}")
        return web.Response(status=response_code, text=f"Request count: {request_count}")
    except Exception as e:
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_get(request):
    global request_count
    global number_request_not_correct_content
    try:
        return web.json_response(
            {
                "actual_total_request": request_count,
                "actual_request": number_request_not_correct_content,
                "expected_total_request": expected_total_request,
                "number_response_400": max_400_responses
            }
        )
    except Exception as e:
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_put_reset(request):
    global request_count
    global number_request_not_correct_content
    global max_200_responses
    global max_400_responses
    global expected_total_request
    try:
        request_count = 0
        number_request_not_correct_content = 0
        expected_total_request = 0
        body_config = await request.json()
        expected_total_request = int(body_config["total_request"])
        failed_percent = int(body_config["failed_percent"])
        max_400_responses = int(failed_percent / 100 * expected_total_request)
        max_200_responses = expected_total_request - max_400_responses
        print(
            f"Set expected total request = {expected_total_request}, failed_percent = {failed_percent}"
        )
        return web.Response(status=200, text=f"Update success.")
    except Exception as e:
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def handle_put_update_expected_file_content(request):
    global expected_content
    try:
        with open(FILE_CONTENT_PATH, 'wb') as f:
            while True:
                chunk = await request.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)
        expected_content = read_file_content_as_bytes(FILE_CONTENT_PATH)
        print("Update expected file content success.")
        return web.Response(status=200, text=f"Update file content success.")
    except Exception as e:
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")


async def create_app():
    app = web.Application()
    app.add_routes([web.post('/', handle_post)])
    app.add_routes([web.get('/', handle_get)])
    app.add_routes(
        [
            web.put('/', handle_put_reset),
            web.put('/file_content', handle_put_update_expected_file_content),
        ]
    )
    return app


if __name__ == '__main__':
    hansol_app = asyncio.run(create_app())
    web.run_app(hansol_app, host='0.0.0.0', port=8080)
