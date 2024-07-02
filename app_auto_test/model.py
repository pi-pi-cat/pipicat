from tortoise import fields
from tortoise.models import Model


class CaseModel(Model):
    id = fields.IntField(pk=True)
    case_id = fields.IntField()
    predicted_runtime = fields.FloatField()
    actual_runtime = fields.FloatField(null=True)
    queue_level = fields.IntField()
    result_dir = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20)

    class Meta:
        table = "cases"
