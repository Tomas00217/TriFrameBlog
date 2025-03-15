from starlette_wtf import StarletteForm
from wtforms import FileField, StringField, TextAreaField, SelectMultipleField, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length

def file_extension_allowed(form, field):
    if not field.data or not field.data.filename:
        return

    allowed_extensions = {"jpg", "jpeg", "png"}

    filename = field.data.filename.lower()
    if "." not in filename or filename.rsplit(".", 1)[1] not in allowed_extensions:
        raise ValidationError("Invalid file type. Only JPG, PNG, and JPEG allowed.")

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class BlogPostForm(StarletteForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    tags = MultiCheckboxField("Tags", coerce=int)
    image = FileField("Image", validators=[file_extension_allowed])
    content = TextAreaField("Content")

    def __init__(self, all_tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    def validate_tags(self, field):
            """
            Ensure at least one tag is selected.
            """
            if not field.data or len(field.data) == 0:
                raise ValidationError("Please select at least one tag.")

class DeleteBlogPostForm(StarletteForm):
    pass