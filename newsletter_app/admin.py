from django.contrib import admin
from .models import NewsletterCategory, NewsletterSubscription, Newsletter, NewsletterRecipient


@admin.register(NewsletterCategory)
class NewsletterCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    # prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'category')
    search_fields = ('user__username', 'user__email', 'category__name')
    raw_id_fields = ('user',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    list_per_page = 20

class NewsletterRecipientInline(admin.TabularInline):
    model = NewsletterRecipient
    extra = 0
    readonly_fields = ('sent_at', 'opened_at', 'is_opened')
    can_delete = False
    max_num = 0


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'scheduled_time', 'sent_time', 'created_by')
    list_filter = ('status', 'category')
    search_fields = ('title', 'content')
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at', 'sent_time')
    inlines = [NewsletterRecipientInline]
    actions = ('send_newsletter',)
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category', 'status')
        }),
        ('Scheduling', {
            'fields': ('scheduled_time',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'sent_time'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def send_newsletter(self, request, queryset):
        for newsletter in queryset:
            if newsletter.status == Newsletter.DRAFT:
                newsletter.status = Newsletter.SCHEDULED
                newsletter.save()
                self.message_user(request, f"Newsletter '{newsletter.title}' scheduled for sending.")
    send_newsletter.short_description = "Send selected newsletters"


@admin.register(NewsletterRecipient)
class NewsletterRecipientAdmin(admin.ModelAdmin):
    list_display = ('newsletter', 'user', 'sent_at', 'is_opened', 'opened_at')
    list_filter = ('is_opened', 'newsletter__category')
    search_fields = ('user__username', 'user__email', 'newsletter__title')
    raw_id_fields = ('user', 'newsletter')
    readonly_fields = ('sent_at', 'opened_at', 'is_opened')
    list_per_page = 20
