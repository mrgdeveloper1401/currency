from django.db import models
from django.utils.text import slugify
import os

from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin


def image_upload_path(instance, filename):
    """Generate upload path based on model name and image title."""
    base_filename, file_extension = os.path.splitext(filename)
    return f"catalog/images/{slugify(instance.title)}/{slugify(base_filename)}{file_extension}"


class Image(CreateMixin, UpdateMixin, SoftDeleteMixin):
    # فیلدهای اصلی
    title = models.CharField(
        max_length=200,
        # verbose_name="عنوان تصویر",
        # help_text="عنوان توصیفی برای تصویر (ضروری)"
    )
    image_file = models.ImageField(
        upload_to=image_upload_path,
        # verbose_name="فایل تصویر",
        # help_text="فرمت‌های پشتیبانی: JPG, PNG, WebP",
        width_field="image_width",
        height_field="image_height"
    )
    image_width = models.PositiveIntegerField(editable=False, null=True)
    image_height = models.PositiveIntegerField(editable=False, null=True)

    # متادیتا
    # alt_text = models.CharField(
    #     max_length=200,
    #     blank=True,
    #     verbose_name="متن جایگزین (Alt)",
    #     help_text="برای دسترسی‌پذیری و SEO"
    # )
    caption = models.TextField(
        blank=True,
        # verbose_name="توضیح تصویر",
        # help_text="توضیح اختیاری درباره تصویر"
    )

    # دسته‌بندی و تگ‌ها
    # category = models.ForeignKey(
    #     'Category',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="دسته‌بندی"
    # )
    # tags = models.ManyToManyField(
    #     'Tag',
    #     blank=True,
    #     verbose_name="تگ‌ها"
    # )

    # مدیریت فایل
    file_size = models.PositiveIntegerField(
        editable=False,
        null=True,
        # verbose_name="حجم فایل (بایت)"
    )
    file_format = models.CharField(
        max_length=10,
        editable=False,
        # verbose_name="فرمت فایل"
    )

    # فعال/غیرفعال
    is_active = models.BooleanField(
        default=True,
        # verbose_name="فعال",
        # help_text="نمایش/عدم نمایش تصویر در سایت"
    )

    class Meta:
        # verbose_name = "تصویر"
        # verbose_name_plural = "تصاویر"
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """محاسبه خودکار فرمت، حجم فایل و ابعاد تصویر قبل از ذخیره."""
        if self.image_file:
            self.file_size = self.image_file.size
            self.file_format = os.path.splitext(self.image_file.name)[1][1:].upper()
        super().save(*args, **kwargs)


# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)


# class Tag(models.Model):
#     name = models.CharField(max_length=50)
#     slug = models.SlugField(unique=True)