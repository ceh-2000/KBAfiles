import functions_framework

# Register an HTTP function with the Functions Framework
@functions_framework.http
def my_http_function(request):
  if request.method == 'OPTIONS':
    # Allows GET requests from any origin with the Content-Type
    # header and caches preflight response for an 3600s
    headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '3600'
    }

    return ('', 204, headers)

  # This code will process each non-file field in the form
  fields = {}
  data = request.form.to_dict()
  for field in data:
      fields[field] = data[field]
      return('Processed field: %s' % field)

  # Return an HTTP response
  return 'OK'