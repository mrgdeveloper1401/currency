from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from django.urls import reverse


class BlogCategory(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        # verbose_name = 'Blog Category'
        # verbose_name_plural = 'Blog Categories'
        db_table = 'blog_category'


class BlogTag(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'blog_tag'


class BlogPost(CreateMixin, UpdateMixin, SoftDeleteMixin):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=300)
    cover_image = models.ForeignKey("catalog_app.Image", on_delete=models.PROTECT, related_name="image_blog_post")
    author = models.ForeignKey("account_app.User", on_delete=models.PROTECT, related_name='author_blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name="blog_posts")
    tags = models.ManyToManyField(BlogTag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-published_at',)
        db_table = 'blog_post'


class BlogComment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey("account_app.User", on_delete=models.PROTECT, related_name="blog_comment")
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='replies')

    def __str__(self):
        return f"Comment by {self.name or self.user.username} on {self.post.title}"

    class Meta:
        ordering = ('created_at',)
        db_table = 'blog_comment'


class BlogView(CreateMixin, UpdateMixin, SoftDeleteMixin):
    post = models.ForeignKey(BlogPost, on_delete=models.DO_NOTHING, related_name='post_views')
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey("account_app.User", on_delete=models.DO_NOTHING, related_name='blogviews')

    class Meta:
        db_table = 'blog_view'