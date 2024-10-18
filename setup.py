from setuptools import setup, find_packages

setup(
    name='PySQLiteDBConnection',
    version='1.0.9b',
    author='SurivZ',
    author_email='franklinserrano23@email.com',
    description='Este paquete proporciona una clase `Connect` para gestionar bases de datos SQLite3 de manera sencilla y estandarizada.',
    long_description="""# Py-SQLite-DB-Connection `v1.0.9b`

Este paquete proporciona una clase `Connect` para gestionar conexiones y operaciones CRUD en bases de datos SQLite3 de manera sencilla y estandarizada, ahora con la capacidad de crear, modificar y eliminar tablas.

## Instalación

Puedes instalar el paquete utilizando pip:

```bash
pip install PySQLiteDBConnection
```

## Ejemplo de uso

### Importar el paquete

```Python
from PySQLiteDBConnection import Connect
```

### Crear una instancia de la clase Connect

```Python
database = Connect('path/to/your/database.db')
```

### Establecer conexión a la base de datos

```Python
database.connect()
```
El método `connect` devuelve un booleano que representa el estado de la operación, en este caso, de la conexión con la base de datos, por lo que también puede guardarse en una variable para usarse más adelante en caso de ser requerido.
```Python
connected = database.connect()
```

### Mostrar información sobre la base de datos

```Python
print(database)
```

### Leer todos los registros de una tabla

```Python
table_data = database.read_table('table_name')
```

### Insertar datos en una tabla

```Python
database.insert_into_table('table_name', {
    'column1': 'value1', 
    'column2': 'value2',
})
```
El método `insert_into_table` también devuelve un booleano que representa el estado de la operación.
```Python
inserted = database.insert_into_table('table_name', {
    'column1': 'value1', 
    'column2': 'value2',
})
```

### Actualizar registros en una tabla

```Python
database.update_record('table_name', {'column1': 'new_value'}, {'column2': 'value2'})
```
El método `update_record` también devuelve un booleano que representa el estado de la operación.
```Python
updated = database.update_record('table_name', {'column1': 'new_value'}, {'column2': 'value2'})
```

### Eliminar registros de una tabla

```Python
database.delete_record('table_name', {'column1': 'value1'})
```
El método `delete_record` también devuelve un booleano que representa el estado de la operación.
```Python
deleted = database.delete_record('table_name', {'column1': 'value1'})
```

#### Crear una tabla nueva

```Python
database.create_table('users', {
    'id': 'INTEGER PRIMARY KEY',
    'name': 'TEXT',
    'age': 'INTEGER'
})
```
El método `create_table` también devuelve un booleano que representa el estado de la operación.
```Python
created = database.create_table('users', {
    'id': 'INTEGER PRIMARY KEY',
    'name': 'TEXT',
    'age': 'INTEGER'
})
```

#### Agregar una columna nueva a una tabla existente

```Python
database.alter_table_add_column('users', 'email', 'TEXT')
```
El método `alter_table_add_column` también devuelve un booleano que representa el estado de la operación.
```Python
added_column = database.alter_table_add_column('users', 'email', 'TEXT')
```

#### Eliminar una tabla

```Python
database.drop_table('users')
```
El método `drop_table` también devuelve un booleano que representa el estado de la operación.
```Python
dropped = database.drop_table('users')
```

### Cerrar la conexión con la base de datos

```Python
database.close()
```

### Obtener estado de la conexión con la base de datos

Esta es otra forma de ver el estado de la conexión con la base de datos para el caso de que no se guarde el resultado del método `connect`.
```Python
print(f'Status: {database.get_status()}')
```

### **Nuevo en `v1.0.9`: Parámetro `raise_exceptions`**

Se agregó el parámetro `raise_exceptions` (por defecto en `False`) al constructor de la clase `Connect` para darle la opción al usuario de levantar o no las excepciones que puedan llegar a ocurrir.


```Python
database = Connect('path/to/your/database.db', raise_exceptions=True)
```


## Contribución

¡Las contribuciones son bienvenidas! Si encuentras algún error o tienes sugerencias para mejoras, siéntete libre de abrir un issue o enviar un pull request.
""",
    long_description_content_type='text/markdown',
    url='https://github.com/SurivZ/Py-SQLite-DB-Connection',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'connect=PySQLiteDBConnection.cli:main',
            'hola=PySQLiteDBConnection.cli:main',
        ],
    },
)
