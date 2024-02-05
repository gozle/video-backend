from django.db import models


class Like(models.Model):
    video = models.ForeignKey("files.Video", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="liked_videos")

    created_at = models.DateTimeField(auto_now_add=True)
