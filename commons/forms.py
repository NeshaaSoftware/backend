from django import forms


class BigNumberInput(forms.NumberInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs["style"] = attrs.get("style", "") + "font-size: 1.2em; min-width: 140px;"
        super().__init__(*args, **kwargs)


class FinancialNumberFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if isinstance(field.widget, forms.NumberInput):
                field.widget = BigNumberInput(attrs=field.widget.attrs)
