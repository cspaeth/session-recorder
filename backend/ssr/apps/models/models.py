from django.db import models
from django.db.models import CASCADE, SET_NULL


class Session(models.Model):
    name = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=30)
    next_take_number = models.IntegerField(default=1)
    next_take_name = models.CharField(default="", max_length=255)
    project_file = models.CharField(null=True, max_length=1024)
    active_take = models.ForeignKey('Take', related_name='+', null=True, on_delete=SET_NULL)

    def to_dict(self):
        result = {
            'name': self.name,
            'next_take': {
                'number': self.next_take_number,
                'name': self.next_take_name,
            },
            'takes': [],
            'active_take': self.active_take and self.active_take.number or None
        }

        for take in self.takes.all():
            result['takes'].append({
                'number': take.number,
                'name': take.name,
                'length': take.length,
                'started_at': '12:31'
            })
        return result


class Take(models.Model):
    session = models.ForeignKey(Session, related_name="takes", on_delete=CASCADE)
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    location = models.FloatField()
    length = models.FloatField(null=True)





