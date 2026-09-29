
# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    skills_to_teach = models.ManyToManyField(
        Skill,
        related_name="teachers",
        blank=True
    )

    skills_to_learn = models.ManyToManyField(
        Skill,
        related_name="learners",
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class ExchangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"


    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )

    receiver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="received_requests"
    )

    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("sender", "receiver"),
                condition=models.Q(status="Pending"),
                name="unique_pending_exchange_request",
            ),
            models.CheckConstraint(
                condition=~models.Q(sender=models.F("receiver")),
                name="prevent_self_exchange_request",
            ),
        ]
