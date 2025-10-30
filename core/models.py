from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

	def __str__(self):
		return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)

class Asistencia(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	fecha_hora = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user.username} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"

	class Meta:
		unique_together = ('user', 'fecha_hora')
from django.db import models

# Create your models here.
