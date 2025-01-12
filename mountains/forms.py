from django import forms
from .models import *

class ReviewCreationForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='태그 선택',
    )

    def clean_tags(self):
        selected_tags = self.cleaned_data.get('tags', [])
        if len(selected_tags) > 3:
            raise forms.ValidationError("태그는 3개까지 선택할 수 있습니다.")

        return selected_tags

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].widget.attrs['onclick'] = "limitCheckboxSelections(this, 3)"
    class Meta:
        model = Review
        fields = ['content', 'image', 'tags']