from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from titles.models import Title

User = get_user_model()


class FeedBackModel(models.Model):
    """Абстрактная модель для обратной связи от пользователей."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации")
    text = models.TextField(verbose_name="Текст")

    class Meta:
        abstract = True


class Review(FeedBackModel):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение')

    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка"
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)

        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review_for_title',
                violation_error_message=(
                    'Уже добавлен ваш отзыв к этому произведению.'
                )
            ),
            models.CheckConstraint(
                condition=Q(score__lte=10) & Q(score__gte=1),
                violation_error_message='Поставьте оценку от 1 до 10.',
                name='check_score_value')
        ]

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'


class Comment(FeedBackModel):
    """Модель комментария к отзыву."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв')

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'комментарий к отзыву "{self.review.text[:20]}"'
