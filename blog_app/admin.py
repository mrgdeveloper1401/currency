from django.contrib import admin
from django.utils.html import format_html
from .models import BlogCategory, BlogTag, BlogPost, BlogComment, BlogView


class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

admin.site.register(BlogTag, BlogTagAdmin)


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(BlogCategory, BlogCategoryAdmin)


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ('user', 'name', 'email', 'content', 'created_at')
    can_delete = False
    show_change_link = True


class BlogViewInline(admin.TabularInline):
    model = BlogView
    extra = 0
    readonly_fields = ('ip_address', 'user',)
    can_delete = False
    max_num = 0


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'category', 'published_at', 'is_featured', 'view_count')
    list_filter = ('status', 'category', 'is_featured', 'published_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'view_count', 'cover_image_preview')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = [BlogCommentInline, BlogViewInline]
    actions = ['publish_posts', 'unpublish_posts', 'feature_posts', 'unfeature_posts']
    date_hierarchy = 'published_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'excerpt', 'cover_image', 'cover_image_preview')
        }),
        ('Metadata', {
            'fields': ('author', 'category', 'tags', 'status', 'is_featured')
        }),
        ('Dates', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.cover_image.url)
        return "-"
    cover_image_preview.short_description = 'Cover Preview'

    def view_count(self, obj):
        return obj.views
    view_count.short_description = 'Views'

    def publish_posts(self, request, queryset):
        updated = queryset.update(status=BlogPost.PUBLISHED, published_at=timezone.now())
        self.message_user(request, f'{updated} posts published successfully.')
    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status=BlogPost.DRAFT, published_at=None)
        self.message_user(request, f'{updated} posts unpublished.')
    unpublish_posts.short_description = "Unpublish selected posts"

    def feature_posts(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts marked as featured.')
    feature_posts.short_description = "Feature selected posts"

    def unfeature_posts(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts unmarked as featured.')
    unfeature_posts.short_description = "Unfeature selected posts"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'post', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'post__title', 'user__username', 'name', 'email')
    raw_id_fields = ('post', 'user', 'parent')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        updated = queryset.update(status=BlogComment.APPROVED)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = "Approve selected comments"

    def reject_comments(self, request, queryset):
        updated = queryset.update(status=BlogComment.REJECTED)
        self.message_user(request, f'{updated} comments rejected.')
    reject_comments.short_description = "Reject selected comments"


@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'ip_address', 'user__username')
    raw_id_fields = ('post', 'user')
    readonly_fields = ('created_at',)
