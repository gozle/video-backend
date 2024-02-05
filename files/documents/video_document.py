from django_elasticsearch_dsl import Index, Document
from files.models import Video

video_index = Index('video_films')
video_index.settings(
    number_of_shards=3,
    number_of_replicas=1
)

@video_index.doc_type
class VideoDocument(Document):
    class Django:
        model = Video
        fields = ["id", 'title', "description", 'm3u8']
