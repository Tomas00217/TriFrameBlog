from flask_blog.blogs.models import Tag
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField, SelectMultipleField, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class BlogPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    tags = MultiCheckboxField("Tags", coerce=int)
    image = FileField("Image", validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!")])
    content = TextAreaField("Content")

    def __init__(self, tag_service, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_tags = tag_service.get_all()
        self.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    def validate_tags(self, field):
            """
            Ensure at least one tag is selected.
            """
            if not field.data or len(field.data) == 0:
                raise ValidationError("Please select at least one tag.")