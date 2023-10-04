from app import app
from flaskext.mysql import MySQL

ssl_config = {
    'ssl': {
        'cert': '../restful-api-vms/DigiCertGlobalRootCA.crt.pem'  #path to the CA certificate
    }
}
mysql = MySQL(ssl=ssl_config)
app.config['MYSQL_DATABASE_DRIVER'] = '{MySQL ODBC 8.0 Unicode Driver}'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'postman'
app.config['MYSQL_DATABASE_PASSWORD'] = 'simple@123'
app.config['MYSQL_DATABASE_DB'] = 'vmsdb'
app.config['MYSQL_DATABASE_HOST'] = 'vms-server.mysql.database.azure.com'
app.config['MYSQL_DATABASE_SSL'] = 'ssl_config'

mysql.init_app(app)