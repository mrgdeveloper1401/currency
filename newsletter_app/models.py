from django.db import models
from account_app.models import User
from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class NewsletterCategory(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Newsletter Category'
        verbose_name_plural = 'Newsletter Categories'
        db_table = 'newsletter_category'


class NewsletterSubscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='newsletter_subscriptions')
    category = models.ForeignKey(NewsletterCategory, on_delete=models.PROTECT, related_name='newsletter_category')
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'category')
        db_table = 'newsletter_subscription'


class Newsletter(CreateMixin, UpdateMixin, SoftDeleteMixin):
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    SENT = 'sent'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SCHEDULED, 'Scheduled'),
        (SENT, 'Sent'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(NewsletterCategory, on_delete=models.PROTECT, related_name="newsletters")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_newsletters')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'newsletter'


class NewsletterRecipient(CreateMixin, UpdateMixin, SoftDeleteMixin):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    is_opened = models.BooleanField(default=False)

    class Meta:
        db_table = 'newsletter_recipient'
