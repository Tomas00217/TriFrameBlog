from accounts.models import EmailUser
from blogs.models import BlogPost, Tag
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

def create_blog(title: str, content: str, author: EmailUser):
    """
    Create a blog with the given `title`, `content`, and `author`.
    """
    return BlogPost.objects.create(title=title, content=content, author=author)

def create_tag(name: str):
    """
    Create a tag with the given `name`.
    """
    return Tag.objects.create(name=name)

class BlogIndexViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")

        self.tag1 = create_tag(name="Food")
        self.tag2 = create_tag(name="Science")

        _ = create_blog("Blog1 title", "Content 1", self.user)
        self.blog2 = create_blog("Blog2 title", "Content 2", self.user)
        self.blog3 = create_blog("Blog3 title", "Content 3", self.user)
        self.blog4 = create_blog("Blog4 title", "Content 4", self.user)

    def test_index_status_200(self):
        """
        Index page returns 200 status code.
        """
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_contains_latest_three_blogs(self):
        """
        The index page contains only the latest three blogs.
        """
        response = self.client.get(reverse("index"))
        self.assertQuerySetEqual(
            response.context["blogs"],
            [self.blog4, self.blog3, self.blog2],
        )

    def test_index_contains_all_tags(self):
        """
        The index page contains all available tags.
        """
        response = self.client.get(reverse("index"))
        self.assertQuerySetEqual(
            response.context["tags"],
            [self.tag1, self.tag2],
            ordered=False
        )

class BlogListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")

        self.tag1 = create_tag(name="Food")

        self.blog1 = create_blog("Blog1 title search", "Content 1", self.user)
        self.blog1.tags.add(self.tag1)
        self.blog2 = create_blog("Blog2 title", "Content 2", self.user)
        self.blog3 = create_blog("Blog3 title", "Content 3", self.user)
        self.blog4 = create_blog("Blog4 title search", "Content 4", self.user)
        self.blog4.tags.add(self.tag1)
        self.blog5 = create_blog("Blog5 title", "Content 5", self.user)
        self.blog6 = create_blog("Blog6 title", "Content 6", self.user)
        self.blog7 = create_blog("Blog7 title", "Content 7", self.user)

    def test_status_200(self):
        """
        Blogs page returns 200 status code.
        """
        response = self.client.get(reverse("blogs"))
        self.assertEqual(response.status_code, 200)

    def test_blogs_page_default(self):
        """
        Accessing the blogs page by default shows 6 blogs at most.
        """
        response = self.client.get(reverse("blogs"))
        self.assertIn("blogs", response.context)
        self.assertEqual(len(response.context["blogs"]), 6)

    def test_blogs_page_second(self):
        """
        Accessing the blogs page next page shows the next blogs.
        """
        response = self.client.get(reverse("blogs") + "?page=2")
        self.assertIn("blogs", response.context)
        self.assertEqual(len(response.context["blogs"]), 1)

    def test_blogs_filter_by_tag(self):
        """
        Filtering blogs by a tag returns only the blogs associated with that tag.
        """
        self.blog1.tags.add(self.tag1)
        response = self.client.get(reverse("blogs") + f"?tag={self.tag1.slug}")
        self.assertQuerySetEqual(
            response.context["blogs"],
            [self.blog1, self.blog4],
            ordered=False
        )

    def test_blogs_search_function(self):
        """
        Searching for a blog by title returns the correct results.
        """
        response = self.client.get(reverse("blogs") + "?search=search")
        self.assertQuerySetEqual(
            response.context["blogs"],
            [self.blog1, self.blog4],
            ordered=False
        )

class BlogDetailViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.tag = create_tag("Food")
        self.blog1 = create_blog("Blog1 title", "Content", self.user)
        self.blog1.tags.add(self.tag)
        self.blog2 = create_blog("Blog2 title", "Content", self.user)
        self.blog2.tags.add(self.tag)
        self.blog3 = create_blog("Blog3 title", "Content", self.user)

    def test_detail_view_status_200(self):
        """
        Detail page returns 200 status code for a valid blog.
        """
        response = self.client.get(reverse("detail", args=[self.blog1.id]))
        self.assertEqual(response.status_code, 200)

    def test_detail_invalid_blog_404(self):
        """
        Detail page returns 404 status code for non-existing blog.
        """
        response = self.client.get(reverse("detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_contains_related_blogs(self):
        """
        Detail page shows related blogs by tags.
        """
        response = self.client.get(reverse("detail", args=[self.blog1.id]))
        self.assertQuerySetEqual(
            response.context["related_blogs"],
            [self.blog2],
        )

class MyBlogsViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.other_user = get_user_model().objects.create_user(email="other@example.com", password="password")

        self.blog1 = create_blog("Blog1 title", "Content", self.user)
        self.blog2 = create_blog("Blog2 title", "Content", self.other_user)

    def test_my_blogs_view_requires_login(self):
        """
        Unauthenticated user is redirected to login.
        """
        response = self.client.get(reverse("my_blogs"))
        self.assertRedirects(response, "/accounts/login/?next=/blogs/my")

    def test_my_blogs_view_shows_only_user_blogs(self):
        """
        Shows only blogs that belong to the user.
        """
        self.client.login(email="user@example.com", password="password")
        response = self.client.get(reverse("my_blogs"))
        self.assertQuerySetEqual(
            response.context["blogs"],
            [self.blog1],
        )

class BlogCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.tag = create_tag("Food")

    def test_create_blog_requires_login(self):
        """
        Unauthenticated user is redirected to login.
        """
        response = self.client.get(reverse("create"))
        self.assertRedirects(response, "/accounts/login/?next=/blogs/create")

    def test_create_blog_success(self):
        """
        Authenticated user can create new blog.
        """
        self.client.login(email="user@example.com", password="password")
        response = self.client.post(reverse("create"), {
            "title": "New Blog",
            "content": "Blog content",
            "tags": [self.tag.id]
        })
        self.assertEqual(BlogPost.objects.count(), 1)
        new_blog = BlogPost.objects.get(title="New Blog")
        self.assertRedirects(response, reverse("detail", args=[new_blog.id]))

class BlogEditViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.other_user = get_user_model().objects.create_user(email="other@example.com", password="password")

        self.tag1 = create_tag("Food")
        self.tag2 = create_tag("Tech")

        self.blog = create_blog("Blog1 title", "Content", self.user)
        self.blog.tags.add(self.tag1)

    def test_edit_blog_requires_login(self):
        """
        Unauthenticated user is redirected to login.
        """
        response = self.client.get(reverse("edit", args=[self.blog.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/blogs/{self.blog.id}/edit")

    def test_edit_blog_permission_denied(self):
        """
        Authenticated user can edit only his own blogs, otherwise 403 status code is returned.
        """
        self.client.login(email="other@example.com", password="password")
        response = self.client.post(reverse("edit", args=[self.blog.id]), {
            "title": "Updated Blog",
            "content": "Updated content",
            "tags": [self.tag2.id]
        })
        self.assertEqual(response.status_code, 403)

    def test_edit_blog_success(self):
        """
        Authenticated user can edit his own blogs.
        """
        self.client.login(email="user@example.com", password="password")
        response = self.client.post(reverse("edit", args=[self.blog.id]), {
            "title": "Updated Blog",
            "content": "Updated content",
            "tags": [self.tag1.id, self.tag2.id]
        })
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, "Updated Blog")
        self.assertEqual(set(self.blog.tags.all()), {self.tag1, self.tag2})
        self.assertRedirects(response, reverse("detail", args=[self.blog.id]))

class BlogDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.other_user = get_user_model().objects.create_user(email="other@example.com", password="password")

        self.blog = create_blog("First Blog", "Content", self.user)

    def test_delete_blog_requires_login(self):
        """
        Unauthenticated user is redirected to login.
        """
        response = self.client.get(reverse("delete", args=[self.blog.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/blogs/{self.blog.id}/delete")

    def test_delete_blog_permission_denied(self):
        """
        Authenticated user can delete only his own blogs, otherwise 403 status code is returned.
        """
        self.client.login(email="other@example.com", password="password")
        response = self.client.post(reverse("delete", args=[self.blog.id]))
        self.assertEqual(response.status_code, 403)

    def test_delete_blog_success(self):
        """
        Authenticated user can delete his own blogs.
        """
        self.client.login(email="user@example.com", password="password")
        response = self.client.post(reverse("delete", args=[self.blog.id]))
        self.assertEqual(BlogPost.objects.count(), 0)
        self.assertRedirects(response, reverse("my_blogs"))