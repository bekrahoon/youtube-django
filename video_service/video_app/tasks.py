import os
import subprocess
from celery import shared_task
from video_app.models import Video, VideoQuality


@shared_task
def proccess_video(video_id, resolution):
    video = Video.objects.get(id=video_id)
    output_dir = "media/videos/processed/"
    output_path = os.path.join(output_dir, f"{video.id}_{resolution}.mp4")

    # Сопоставление разрешений
    resolution_map = {
        "360p": "640x360",
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
    }

    if resolution not in resolution_map:
        raise ValueError("Invalid resolution")

    # Создание директории, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video.file.path,
        "-vf",
        f"scale={resolution_map[resolution]}",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        output_path,
    ]

    subprocess.run(command)
    VideoQuality.objects.create(
        video=video, resolution=resolution, file_path=output_path
    )
    video.processed = True
    video.save()
