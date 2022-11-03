@staticmethod
def connect_to_cloud_sql():
    from google.appengine.api import app_identity
    import MySQLdb
    app_identity_sql_instance_dict = {"devnpfieldapp": "devnpfieldapp:us-west1:devcloudsql", "devnpfieldapp2": "devnpfieldapp2:us-west1:dev2cloudsql", "npfieldapp": "npfieldapp:us-west1:cloudsqlprod"}
    pass_file = GCSLockedFile("/ApplicationSettings/cloud_sql_password.txt")
    passwordd = pass_file.read()
    pass_file.unlock()
    app_id = app_identity.get_application_id()
    
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', app_identity_sql_instance_dict[app_id])

                        #user=CLOUDSQL_USER, below
        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user="root",
            passwd=passwordd)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db
