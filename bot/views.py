from django.http import JsonResponse


def empty_page(request):
    return JsonResponse([{'text': 'empty page'}], safe=False)
