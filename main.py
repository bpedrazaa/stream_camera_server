import asyncio
import cv2
import logging
import os
import signal
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

                # Encode
                _, jpeg_frame = cv2.imencode(".jpg", frame)
                jpeg_data = jpeg_frame.tobytes()

                # Send the JPEG frame over WebSocket
                await websocket.send(jpeg_data)

                await asyncio.sleep(
                    frame_rate_target
                )  # Sleep to match the target frame rate

        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            cap.release()


# WebSocket server to handle connections and route to the correct path handler
async def main():
    print(stream_urls)

    async def handler(websocket):
        if stream_urls:
            path = websocket.request.path
            rtsp_url = stream_urls.get(path)
            await stream_video(websocket, rtsp_url)
        else:
            await websocket.close()

    # Start the WebSocket server
    async with websockets.serve(handler, HOST, PORT, compression="deflate"):
        logging.info(f"WebSocket server listening on ws://{HOST}:{PORT}")
        await asyncio.Future()  # run forever


def shutdown_handler(signum, frame):
    logging.info("Shutting down gracefully...")
    # Cancel any active tasks and clean up resources
    asyncio.get_event_loop().stop()


# Run the WebSocket server
if __name__ == "__main__":
    asyncio.run(main())
    signal.signal(signal.SIGINT, shutdown_handler)
