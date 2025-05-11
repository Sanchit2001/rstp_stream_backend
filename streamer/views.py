from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import subprocess
import asyncio
import hashlib
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

async def process_rtsp_stream(rtsp_url, stream_id):
    channel_layer = get_channel_layer()
    group_name = f"stream_{stream_id}"
    try:
        process = await asyncio.create_subprocess_shell(
            f'ffmpeg -i "{rtsp_url}" -f mjpeg -',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        while True:
            frame_bytes = await process.stdout.read(4096)  # Adjust buffer size as needed
            if not frame_bytes:
                break
            # Simulate encoding to base64 for now
            import base64
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            await channel_layer.group_send(
                group_name,
                {"type": "stream.frame", "frame": frame_base64}
            )
    except Exception as e:
        print(f"Error processing {rtsp_url} ({stream_id}): {e}")
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()

@csrf_exempt
def add_rtsp_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rtsp_url = data.get('url')
            if rtsp_url:
                stream_id = hashlib.sha256(rtsp_url.encode()).hexdigest()[:10]
                # Execute the asynchronous function synchronously using async_to_sync
                async_to_sync(process_rtsp_stream)(rtsp_url, str(stream_id))
                return JsonResponse({'status': 'stream added', 'stream_id': str(stream_id)})
            else:
                return JsonResponse({'error': 'Missing RTSP URL'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)