
# SQLite3 Manager

[![License](https://img.shields.io/badge/license-BSD-blue.svg)](LICENSE)

Este proyecto proporciona una librería para gestionar bases de datos **SQLite3** de manera sencilla y estandarizada. Incluye funcionalidades útiles para manejar bases de datos SQLite.

## Características

- Conexión y desconexión a bases de datos SQLite.
- Listar tablas y columnas de una base de datos.
- Ejecutar consultas personalizadas.
- Insertar, actualizar y eliminar registros.
- Crear y modificar tablas dinámicamente.
- Soporte para Python 3.10 en adelante.

## Requisitos

- Python 3.10 o superior.
- SQLite3 instalado en el sistema.

## Instalación

Puedes instalar la librería directamente desde PyPI utilizando `pip`:

```bash
pip install sqlite3-manager
```

Si deseas clonar el repositorio y usar la versión de desarrollo:

```bash
git clone https://github.com/SurivZ/sqlite3-manager.git
cd sqlite3-manager
pip install .
```

## Uso

### Ejemplo detallado con explicación

1. **Crear una instancia y conectarse a la base de datos**  
   Usamos el método `connect()` para establecer una conexión con la base de datos.

   ```python
   from sqlite3_manager import Connect
   conn = Connect('mi_base_de_datos.db')
   conn.connect()
   ```

2. **Crear una tabla**  
   Creamos una tabla llamada `users` con campos para ID, nombre, edad y correo electrónico usando `create_table()`.

   ```python
   conn.create_table('users', {
       'id': 'INTEGER PRIMARY KEY',
       'name': 'TEXT',
       'age': 'INTEGER',
       'email': 'TEXT'
   })
   ```

3. **Insertar datos**  
   Usamos el método `insert()` para insertar un solo registro:

   ```python
   conn.insert('users', {'name': 'John Doe', 'age': 30, 'email': 'john@example.com'})
   ```

   También podemos insertar múltiples registros a la vez con `bulk_insert()`:

   ```python
   conn.bulk_insert('users', [
       {'name': 'Jane Doe', 'age': 25, 'email': 'jane@example.com'},
       {'name': 'Alice', 'age': 28, 'email': 'alice@example.com'}
   ])
   ```

4. **Leer todos los registros de la tabla**  
   Leemos todos los registros de la tabla `users` con el método `read_table()`:

   ```python
   users = conn.read_table('users')
   print(users) # [(1, 'John Doe', 30, 'john@example.com'), (2, 'Jane Doe', 25, 'jane@example.com'), (3, 'Alice', 28, 'alice@example.com')]
   ```

5. **Buscar registros**  
   Buscamos registros que cumplan con una condición específica usando el método `search()`:

   ```python
   search_result = conn.search('users', {'name': 'Alice'})
   print(search_result) # [(3, 'Alice', 28, 'alice@example.com')]
   ```

6. **Actualizar un registro**  
   Modificamos el correo electrónico de un usuario utilizando `update()`:

   ```python
   conn.update('users', {'email': 'john.new@example.com'}, {'name': 'John Doe'})
   ```

7. **Listar tablas y columnas**  
   Obtenemos una lista de las tablas disponibles en la base de datos con `list_table_names()`:

   ```python
   tables = conn.list_table_names()
   print(tables)  # ['users']
   ```

   También podemos obtener los nombres de las columnas de una tabla usando `get_column_names()`:

   ```python
   columns = conn.get_column_names('users')
   print(columns)  # ['id', 'name', 'age', 'email']
   ```

8. **Modificar la estructura de la tabla**  
   Añadimos una columna nueva a la tabla `users` con `add_column()`:

   ```python
   conn.add_column('users', 'created_at', 'TEXT')
   ```

   Y podemos eliminar una columna de la tabla con `drop_column()`:

   ```python
   conn.drop_column('users', 'created_at')
   ```

9. **Eliminar registros**  
   Podemos borrar registros que cumplan con una condición usando `delete()`:

   ```python
   conn.delete('users', {'name': 'Alice'})
   ```

10. **Ejecutar una consulta personalizada**  
    Ejecutamos una consulta SQL personalizada con el método `custom_query()`:

    ```python
    custom_query_result = conn.custom_query('SELECT * FROM users WHERE age > 25')
    print(custom_query_result)  # [(1, 'John Doe', 30, 'john.new@example.com')]
    ```

11. **Eliminar una tabla**  
    Si necesitamos eliminar una tabla por completo, podemos hacerlo con `drop_table()`:

    ```python
    conn.drop_table('users')
    ```

12. **Cerrar la conexión**  
    Finalmente, cerramos la conexión con el método `close()`:

    ```python
    conn.close()
    ```

Este ejemplo muestra cómo puedes gestionar una base de datos SQLite utilizando todos los métodos de la clase `Connect`.

## Instrucciones para contribuciones

Si deseas contribuir a este proyecto, sigue los pasos a continuación:

1. Haz un **fork** del repositorio.
2. Clona tu fork localmente:
   ```bash
   git clone https://github.com/tu-usuario/sqlite3-manager.git
   ```
3. Crea una rama para tu contribución:
   ```bash
   git checkout -b nombre-de-tu-rama
   ```
4. Realiza tus cambios y haz un commit con un buen mensaje descriptivo:
   ```bash
   git commit -m "Descripción de los cambios"
   ```
5. Haz push de tus cambios a tu fork:
   ```bash
   git push origin nombre-de-tu-rama
   ```
6. Crea un **pull request** en el repositorio original.

## Contacto

Si tienes preguntas o sugerencias, siéntete libre de abrir un **issue** o contactarme a través de [franklinserrano23@email.com](mailto:franklinserrano23@email.com).

---

**Licencia:** Este proyecto está licenciado bajo la licencia BSD.