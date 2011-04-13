from .utils import custom_spaceless

class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = custom_spaceless(response.content)
        return response
