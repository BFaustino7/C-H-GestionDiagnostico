from django.http import JsonResponse

def api_success(data=None):
    response = {'status': 'success'}
    if data:
        response.update(data)
    return JsonResponse(response)

def api_error(errors=None, message=None, status=400):
    response = {'status': 'error'}
    if errors:
        response['errors'] = errors
    if message:
        response['message'] = message
    return JsonResponse(response, status=status)