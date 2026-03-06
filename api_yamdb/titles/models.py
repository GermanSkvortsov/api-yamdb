"""Модели для категорий, жанров и произведений."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


MAX_LENGTH = 256


def validate_year(value):
    """Проверка, что год не больше текущего."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год {value} не может быть больше текущего ({current_year})'
        )


class Category(models.Model):
    """Модель для хранения категорий произведений."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для хранения жанров произведений."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для хранения произведений."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name
