import subprocess
from celery import shared_task
from video_app.models import Video, VideoQuality


@shared_task
def proccess_video(video_id):
    video = Video.objects.get(id=video_id)
    resolutions = ["360p", "480p", "720p", "1080p"]
    for res in resolutions:
        output_path = f"media/videos/processed/{video.id}_{res}.mp4"
        if res == "360":
            resolution = "640x360"
        elif res == "480":
            resolution = "854x480"
        elif res == "720":
            resolution = "1280x720"
        elif res == "1080":
            resolution = "1920x1080"

        command = [
            "ffmpeg",
            "-i",
            video.original_file.path,
            "-vf",
            f"scale={resolution}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            output_path,
        ]
        subprocess.run(command)
        VideoQuality.objects.create(video=video, resolution=res, file_path=output_path)
    video.processed = True
    video.save()
