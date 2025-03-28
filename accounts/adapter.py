from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Used to overwrite the default adapter class which only saves the default user attributes.
    Without this address and profile_photo attributes wont be saved.
    """
    def save_user(self, request, user, form, commit=False):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data
        user.address = data.get('address')
        user.profile_photo=data.get('profile_photo')
        user.save()
        return user