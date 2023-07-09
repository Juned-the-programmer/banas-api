from django.db import models
import uuid

# Create your models here.
class Route(models.Model):
    route_name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    addedby = models.CharField(max_length=100,null=True, blank=True)
    updatedby = models.CharField(max_length=100, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4 , unique=True , primary_key=True , editable=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_added = timezone.now()
        
        self.date_updated = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.route_name)