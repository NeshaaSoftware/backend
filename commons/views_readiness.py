from django.http import JsonResponse


def readiness_probe(request):
    return JsonResponse({"status": "ok"})
