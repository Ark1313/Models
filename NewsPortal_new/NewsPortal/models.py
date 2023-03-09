from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    a_username = models.OneToOneField(User, on_delete=models.CASCADE)
    rate_user = models.IntegerField(default=0)

    def update_rate(self):   # изменяет рейтинг
        sum_rate_post = Post.objects.filter(p_author_id__a_username_id__id=self.a_username_id).aggregate(ra=Sum('p_rate')).get('ra')
        sum_rate_coment = Comment.objects.filter(com_auth_id=self.a_username_id).aggregate(ra=Sum('c_rate')).get('ra')
        sum_rate_coment_post = (Comment.objects.filter(
            com_post_id__p_author_id__a_username_id__id=self.a_username_id
        ).exclude(
            com_auth_id=self.a_username_id
        ).aggregate(ra=Sum('c_rate')).get('ra'))
        self.rate_user = sum_rate_post * 3 + sum_rate_coment + sum_rate_coment_post
        self.save()
    # sum_rate_post - суммарный рейтинг каждой статьи автора ;
    # sum_rate_coment - суммарный рейтинг всех комментариев автора;
    # sum_rate_coment_post - суммарный рейтинг всех комментариев к статьям автора.

class Category(models.Model):
    category = models.CharField(max_length=20, unique=True)  # Уникальное поле категорий
    cat_post = models.ManyToManyField('Post', through='PostCategory')   # связь многие ко многим со Статьей


class Post(models.Model):
    choise = [
        ('Post', 'Статья'),
        ('News', 'Новость'),
    ]
    p_category = models.ManyToManyField('Category', through='PostCategory')     # связь многие ко многим с Категорией
    p_author = models.ForeignKey(Author, on_delete=models.CASCADE)  # связь один ко многим с Автором
    p_name = models.CharField(max_length=50, null=True)    # заголовок статьи
    p_post = models.TextField()   # текст статьи
    p_create_date = models.DateTimeField(auto_now_add=True)     # дата время добавления
    p_update_date = models.DateTimeField(auto_now=True)     # дата время обновления
    p_rate = models.IntegerField(default=0)    # рейтинг статьи
    p_type = models.CharField(max_length=20, choices=choise, default='Post')
    # выбор статья или новость (по умолчанию Статья)

    def like(self):   # повышает лайк
        self.p_rate += 1
        self.save()

    def dislike(self):  # понижает лайк
        self.p_rate -= 1
        self.save()

    def preview(self):  # предварительный просмотр статьи (первые 124 символа и ...)
        # previev1 = Post.objects.filter(p_author=self.pk).p_name
        # previev2 = Post.objects.filter(p_author=self.pk).p_post
        previev1 = self.p_name
        previev2 = self.p_post

        if len(previev2) > 124:
            previev2 = f"{previev2[:124]}..."
        previev = f"Название: {previev1}\nНачало статьи: {previev2}"
        print(previev)

    def best(self):
        a = Author.objects.filter(id=self.p_author_id).get().a_username_id
        aut = User.objects.filter(id=a).get().username
        print(f"Дата созадния:{self.p_create_date}, Автор: {aut}, Название статьи: {self.p_name}")
        self.preview()



class PostCategory(models.Model):
    pc_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    pc_category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    c_post = models.TextField()  # текст коментария
    c_create_date = models.DateTimeField(auto_now_add=True)     # дата время добавления коментария
    c_rate = models.IntegerField(default=0)     # рейтинг коментария
    com_post = models.ForeignKey(Post, on_delete=models.CASCADE)    # связь со статьей
    com_auth = models.ForeignKey(User, on_delete=models.CASCADE)  # связь с Юзером

    def like(self):
        self.c_rate += 1
        self.save()

    def dislike(self):
        self.c_rate -= 1
        self.save()
