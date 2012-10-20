import json

from rayage_ws import messageHandler

the_world = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder'},
    { 'id': 'AF', 'name': 'Africa', 'type': 'continent', 'population':'900 million', 'area': '30,221,532 sq km', 'timezone': '-1 UTC to +4 UTC', 'parent': 'admin_modules'},
        { 'id': 'EG', 'name': 'Egypt', 'type': 'country', 'parent': 'AF' },
        { 'id': 'KE', 'name': 'Kenya', 'type': 'country', 'parent': 'AF' },
            { 'id': 'Nairobi', 'name': 'Nairobi', 'type': 'city', 'parent': 'KE' },
            { 'id': 'Mombasa', 'name': 'Mombasa', 'type': 'city', 'parent': 'KE' },
        { 'id': 'SD', 'name': 'Sudan', 'type': 'country', 'parent': 'AF' },
            { 'id': 'Khartoum', 'name': 'Khartoum', 'type': 'city', 'parent': 'SD' },
    { 'id': 'AS', 'name': 'Asia', 'type': 'continent', 'parent': 'admin_modules' },
        { 'id': 'CN', 'name': 'China', 'type': 'country', 'parent': 'AS' },
        { 'id': 'IN', 'name': 'India', 'type': 'country', 'parent': 'AS' },
        { 'id': 'RU', 'name': 'Russia', 'type': 'country', 'parent': 'AS' },
        { 'id': 'MN', 'name': 'Mongolia', 'type': 'country', 'parent': 'AS' },
    { 'id': 'OC', 'name': 'Oceania', 'type': 'continent', 'population':'21 million', 'parent': 'admin_modules'},
    { 'id': 'EU', 'name': 'Europe', 'type': 'continent', 'parent': 'admin_modules' },
        { 'id': 'DE', 'name': 'Germany', 'type': 'country', 'parent': 'EU' },
        { 'id': 'FR', 'name': 'France', 'type': 'country', 'parent': 'EU' },
        { 'id': 'ES', 'name': 'Spain', 'type': 'country', 'parent': 'EU' },
        { 'id': 'IT', 'name': 'Italy', 'type': 'country', 'parent': 'EU' },
    { 'id': 'NA', 'name': 'North America', 'type': 'continent', 'parent': 'admin_modules' },
    { 'id': 'SA', 'name': 'South America', 'type': 'continent', 'parent': 'admin_modules' }
]

@messageHandler("admin_module_tree_request")
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """                                
    result_message = {'type': 'admin_module_tree',
                      'modules': the_world}
                      
    socket_connection.write_message(json.dumps(result_message))

