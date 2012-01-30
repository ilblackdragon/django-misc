def useful_constants(request):
    """
    This workaround useful if you want use {% if var == None %}, because
    {% if not var %} First {% else %} Second {% endif %} will show the result:
    var = None  =>  First
    var = False =>  First
    var = True  =>  True
    """
    return {'True': True, 'False': False, 'None': None}
