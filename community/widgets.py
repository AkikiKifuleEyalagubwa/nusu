from django.forms.widgets import Input

class MultipleFileInput(Input):
    input_type = 'file'
    template_name = 'django/forms/widgets/file.html'
    needs_multipart_form = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs['multiple'] = 'multiple'
        super().__init__(attrs)