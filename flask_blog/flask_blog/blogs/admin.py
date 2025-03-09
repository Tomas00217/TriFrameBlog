from flask_blog.admin import AdminModelView
from flask_wtf.file import FileField, FileAllowed

class BlogPostAdminView(AdminModelView):
    column_list = ("title", "author", "tags", "created_at")
    
    form_columns = ("title", "author", "tags", "content", "image", "created_at")
    
    column_formatters = {
        "tags": lambda v, c, m, p: ", ".join([tag.name for tag in m.tags])
    }

    form_overrides = {
        'image': FileField
    }
    
    form_args = {
        'image': {
            'label': 'Image',
            'validators': [FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')]
        }
    }

    def __init__(self, model, session, blog_service, **kwargs):
        """
        Initialize with the blog service
        """
        self.blog_service = blog_service
        super(BlogPostAdminView, self).__init__(model, session, **kwargs)

    def on_model_change(self, form, model, is_created):
        if model.content:
            model.content = self.blog_service.clean_content(model.content)

        file = form.image.data
        if file and hasattr(file, 'filename') and file.filename:
            model.image = self.blog_service.upload_image(file)
        
        super(BlogPostAdminView, self).on_model_change(form, model, is_created)