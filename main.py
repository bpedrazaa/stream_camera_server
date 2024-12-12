import asyncio
import base64
import cv2
import json
import logging
import os
import time
import websockets

logging.basicConfig(level=logging.INFO)

HOST = "0.0.0.0"
PORT = 6001
stream_urls = None

camera_streams = os.environ.get("CAMERA_STREAMS", None)
if camera_streams is not None:
    rtsp_urls = camera_streams.split(",")
    stream_urls = {}
    for i in range(len(rtsp_urls)):
        stream_urls[f"/stream{i+1}"] = rtsp_urls[i]


def open_stream(rtsp_url, retries=3, timeout=5):
    cap = None
    for _ in range(retries):
        cap = cv2.VideoCapture(rtsp_url)
        if cap.isOpened():
            return cap

        logging.error(f"Error: Unable to open RTSP stream at {rtsp_url}")
        time.sleep(timeout)  # Wait before retrying
    return None


# Common function to handle video streaming
async def stream_video(websocket, rtsp_url):
    cap = open_stream(rtsp_url)

    if cap is not None:
        frame_rate_target = 1 / 30  # (30 FPS)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # End of stream

                # Resize and encode the frame as JPEG
                # target_size = (640, 360)
                # frame = cv2.resize(frame, target_size)

                # Process frame
                _, buffer = cv2.imencode(".jpg", frame)
                frame_data = base64.b64encode(buffer).decode("utf-8")

                # Prepare the json message
                message = {"frame": frame_data}

                # Send the JPEG frame over WebSocket
                await websocket.send(json.dumps(message))

                await asyncio.sleep(
                    frame_rate_target
                )  # Sleep to match the target frame rate1

        except Exception as e:
            logging.error(f"Error: {e}")

        finally:
            cap.release()


async def handler(websocket):
    try:
        if stream_urls:
            path = websocket.request.path
            if path in (stream_urls.keys()):
                rtsp_url = stream_urls.get(path)
                await stream_video(websocket, rtsp_url)

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error("Connection Closed Error: ", e)

    except websockets.exceptions.ProtocolError as e:
        logging.error("Protocol Error: ", e)

    except websockets.exceptions.InvalidHandshake as e:
        logging.error("Invalid Handshake:", e)

    except EOFError as e:
        logging.error("EOF Error: ", e)

    finally:
        await websocket.close()


# WebSocket server to handle connections and route to the correct path handler
async def main():
    print(f"Available stream paths: {' | '.join(stream_urls.keys())}")
    # Start the WebSocket server
    async with websockets.serve(
        handler, HOST, PORT, compression="deflate", ping_interval=None
    ):
        logging.info("WebSocket server initialized")
        await asyncio.Future()  # run forever


# Run the WebSocket server
if __name__ == "__main__":
    asyncio.run(main())
