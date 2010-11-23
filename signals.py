from django.dispatch import Signal

blog_update = Signal(providing_args=["instance"])
forum_update = Signal(providing_args=["instance"])
thread_update = Signal(providing_args=["instance"])

