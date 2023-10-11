from django.shortcuts import redirect


def error_decorator(func):
    def wrapper(*args, **kwargs):
        # try:
        #     return func(*args, **kwargs)
        # except Exception as E:
        #     print(E)
        #     return redirect("something-went-wrong")
        return func(*args, **kwargs)

    return wrapper
