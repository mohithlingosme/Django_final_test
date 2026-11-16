from django import forms


class ExamSubmissionForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in questions:
            self.fields[self.field_name(question.pk)] = forms.ChoiceField(
                label=question.text,
                choices=[
                    (str(choice.pk), choice.text)
                    for choice in question.choices.all()
                ],
                widget=forms.RadioSelect,
                required=True,
            )

    @staticmethod
    def field_name(question_id):
        return f"question_{question_id}"
