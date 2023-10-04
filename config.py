from app import app
from flaskext.mysql import MySQL
import os

ssl_config = {
    'ssl': {
        'cert': '../restful-api-vms/DigiCertGlobalRootCA.crt.pem'  #path to the CA certificate
    }
}
mysql = MySQL(ssl=ssl_config)
app.config['MYSQL_DATABASE_DRIVER'] = '{MySQL ODBC 8.0 Unicode Driver}'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = os.environ.get('postman')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('simple@123')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('vmsdb')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('vms-server.mysql.database.azure.com')
# app.config['MYSQL_DATABASE_SSL'] = 'ssl_config'

# Check if SSL is required
if os.environ.get('MYSQL_USE_SSL') == 'True':
    ssl_config = {
        'ssl': {
            'cert': '../restful-api-vms/DigiCertGlobalRootCA.crt.pem'  # Path to the CA certificate
        }
    }
    app.config['MYSQL_DATABASE_SSL'] = ssl_config

mysql.init_app(app)