from django_elasticsearch_dsl import Index, Document

from files.models import Channel

channel_index = Index('channels')
channel_index.settings(
    number_of_shards=3,
    number_of_replicas=1
)


@channel_index.doc_type
class ChannelDocument(Document):
    class Django:
        model = Channel
        fields = ["id", 'name', 'description', 'keywords']
