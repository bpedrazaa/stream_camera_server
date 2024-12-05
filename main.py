from websockets.asyncio.server import serve
import asyncio
import ffmpeg


async def stream_handler(websocket):
    rtsp_url = "rtsp://admin:Pass1234@192.168.3.250/cam/realmonitor?channel=1&subtype=1"

    # FFmpeg process setup to capture RTSP stream and transcode to mpegts (with mpeg1video codec)
    process = (
        ffmpeg.input(rtsp_url)
        .output(
            "pipe:1",
            format="mpegts",
            vcodec="mpeg1video",
            acodec="mp2",
            s="640x360",
            r=30,
            b="700k",
            audio_bitrate="64k",
            ar="44100",
            ac=1,
            vf="fps=30",
        )
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    try:
        while True:
            # Read data from FFmpeg stdout
            data = process.stdout.read(4096)
            if not data:
                break

            # Send the data to the WebSocket
            await websocket.send(data)

    except Exception as e:
        print(f"Error streaming data: {e}")

    finally:
        process.stdout.close()
        process.stderr.close()
        await websocket.close()


async def main():
    print("Starting websocket stream")
    async with serve(stream_handler, "0.0.0.0", 6001):
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
