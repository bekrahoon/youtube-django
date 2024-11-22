import os
import subprocess
from celery import shared_task
from video_app.models import Video, VideoQuality
from django.core.exceptions import ObjectDoesNotExist


@shared_task
def proccess_video(video_id, resolution):
    try:
        video = Video.objects.get(id=video_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Video with ID {video_id} does not exist.")

    output_dir = "media/videos/"
    output_path = os.path.join(output_dir, f"{video.id}_{resolution}.mp4")

    # Сопоставление разрешений
    resolution_map = {
        "360p": "640x360",
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
    }

    if resolution not in resolution_map:
        raise ValueError(f"Invalid resolution: {resolution}")

    # Создание директории, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    command = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        video.file.path,
        "-vf",
        f"scale={resolution_map[resolution]}",
        "-preset",
        "slow",
        "-c:v",
        "libx264",
        "-strict",
        "experimental",
        "-c:a",
        "aac",
        "-crf",
        "20",
        "-maxrate",
        "500k",
        "-bufsize",
        "500k",
        "-r",
        "28",
        "-f",
        "mp4",
        output_path,
        "-y",
    ]

    # Выполнение команды ffmpeg
    result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    # Log stdout and stderr
    print(result.stdout.decode("utf-8"))
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.decode('utf-8')}")

    # Проверка создания выходного файла
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"File not created: {output_path}")

    # Сохранение данных о видео
    VideoQuality.objects.create(
        video=video, resolution=resolution, file_path=output_path
    )
    video.processed = True
    video.save()
