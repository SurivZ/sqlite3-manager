import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme
from InquirerPy import inquirer
from PySQLiteDBConnection import Connect

# Configuración del estilo de consola
theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "bold red"
})

console = Console(theme=theme)

# Estado global de la conexión
db_connection = None

def connect_to_db():
    """Función para conectarse a la base de datos"""
    global db_connection

    db_path = Prompt.ask("[cyan]Introduce la ruta de la base de datos[/cyan]")
    db_connection = Connect(db_path)

    if db_connection.connect():
        console.print(f"[success]Conexión a la base de datos {db_path} exitosa[/success]")
    else:
        console.print("[error]Error al conectar con la base de datos[/error]")

def disconnect_db():
    """Función para desconectar la base de datos"""
    global db_connection

    if db_connection:
        db_connection.close()
        db_connection = None
        console.print("[success]Desconectado de la base de datos correctamente[/success]")
    else:
        console.print("[warning]No hay ninguna conexión activa[/warning]")

def view_tables():
    """Función para listar las tablas en la base de datos"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = db_connection.execute_custom_query(tables_query)

    if tables:
        console.print(f"[info]Tablas disponibles: {', '.join(table[0] for table in tables)}[/info]") # type: ignore
    else:
        console.print("[warning]No se encontraron tablas en la base de datos.[/warning]")

def read_table():
    """Función para leer una tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla a leer[/cyan]")
    rows = db_connection.read_table(table_name)

    if rows:
        console.print(f"[info]Registros de la tabla {table_name}:[/info]")
        for row in rows:
            console.print(row)
    else:
        console.print("[warning]No se encontraron registros o hubo un error.[/warning]")

def insert_into_table():
    """Función para insertar datos en una tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla[/cyan]")
    data = {}

    while True:
        column_name = Prompt.ask("[cyan]Introduce el nombre de la columna (deja en blanco para terminar)[/cyan]")
        if not column_name:
            break
        value = Prompt.ask(f"[cyan]Introduce el valor para la columna '{column_name}'[/cyan]")
        data[column_name] = value

    if db_connection.insert_into_table(table_name, data):
        console.print(f"[success]Datos insertados en la tabla {table_name}[/success]")
    else:
        console.print("[error]Hubo un error al insertar los datos[/error]")

def update_record():
    """Función para actualizar un registro en una tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla[/cyan]")
    data = {}
    condition = {}

    console.print("[info]Introduce los valores a actualizar:")
    while True:
        column_name = Prompt.ask("[cyan]Introduce el nombre de la columna a actualizar (deja en blanco para terminar)[/cyan]")
        if not column_name:
            break
        value = Prompt.ask(f"[cyan]Introduce el nuevo valor para la columna '{column_name}'[/cyan]")
        data[column_name] = value

    console.print("[info]Introduce la condición para filtrar los registros a actualizar:")
    while True:
        column_name = Prompt.ask("[cyan]Introduce el nombre de la columna de la condición (deja en blanco para terminar)[/cyan]")
        if not column_name:
            break
        value = Prompt.ask(f"[cyan]Introduce el valor para la condición de la columna '{column_name}'[/cyan]")
        condition[column_name] = value

    if db_connection.update_record(table_name, data, condition):
        console.print(f"[success]Registros actualizados en la tabla {table_name}[/success]")
    else:
        console.print("[error]Hubo un error al actualizar los datos[/error]")

def delete_record():
    """Función para eliminar un registro en una tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla[/cyan]")
    condition = {}

    console.print("[info]Introduce la condición para filtrar los registros a eliminar:")
    while True:
        column_name = Prompt.ask("[cyan]Introduce el nombre de la columna de la condición (deja en blanco para terminar)[/cyan]")
        if not column_name:
            break
        value = Prompt.ask(f"[cyan]Introduce el valor para la condición de la columna '{column_name}'[/cyan]")
        condition[column_name] = value

    if db_connection.delete_record(table_name, condition):
        console.print(f"[success]Registros eliminados de la tabla {table_name}[/success]")
    else:
        console.print("[error]Hubo un error al eliminar los datos[/error]")

def create_table():
    """Función para crear una nueva tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la nueva tabla[/cyan]")
    columns = {}

    console.print("[info]Introduce las columnas y sus tipos (INTEGER, TEXT, etc.):")
    while True:
        column_name = Prompt.ask("[cyan]Introduce el nombre de la columna (deja en blanco para terminar)[/cyan]")
        if not column_name:
            break
        column_type = Prompt.ask(f"[cyan]Introduce el tipo de dato para la columna '{column_name}'[/cyan]")
        columns[column_name] = column_type

    if db_connection.create_table(table_name, columns):
        console.print(f"[success]Tabla {table_name} creada exitosamente[/success]")
    else:
        console.print("[error]Hubo un error al crear la tabla[/error]")

def alter_table_add_column():
    """Función para agregar una columna a una tabla existente"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla a modificar[/cyan]")
    column_name = Prompt.ask("[cyan]Introduce el nombre de la nueva columna[/cyan]")
    column_type = Prompt.ask(f"[cyan]Introduce el tipo de dato de la columna '{column_name}'[/cyan]")

    if db_connection.alter_table_add_column(table_name, column_name, column_type):
        console.print(f"[success]Columna {column_name} añadida exitosamente a la tabla {table_name}[/success]")
    else:
        console.print("[error]Hubo un error al agregar la columna[/error]")

def drop_table():
    """Función para eliminar una tabla"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    table_name = Prompt.ask("[cyan]Introduce el nombre de la tabla a eliminar[/cyan]")

    if db_connection.drop_table(table_name):
        console.print(f"[success]Tabla {table_name} eliminada exitosamente[/success]")
    else:
        console.print("[error]Hubo un error al eliminar la tabla[/error]")

def execute_custom_query():
    """Función para ejecutar una consulta SQL personalizada"""
    global db_connection

    if not db_connection or not db_connection.get_status():
        console.print("[warning]Debes conectarte primero a una base de datos[/warning]")
        return

    query = Prompt.ask("[cyan]Introduce la consulta SQL a ejecutar[/cyan]")
    result = db_connection.execute_custom_query(query)

    if result:
        console.print(f"[info]Resultado de la consulta:[/info]")
        for row in result:
            console.print(row)
    else:
        console.print("[warning]No se encontraron resultados o hubo un error en la consulta.[/warning]")

def main_menu():
    """Muestra el menú principal"""
    global db_connection

    while True:
        menu_options = inquirer.select( # type: ignore
            message="Seleccione una opción:",
            choices=[
                {"name": "Conectar a base de datos", "value": "connect", "disabled": db_connection is not None},
                {"name": "Desconectar de la base de datos", "value": "disconnect", "disabled": db_connection is None},
                {"name": "Ver tablas en la base de datos", "value": "view_tables", "disabled": db_connection is None},
                {"name": "Leer tabla", "value": "read_table", "disabled": db_connection is None},
                {"name": "Insertar en tabla", "value": "insert_table", "disabled": db_connection is None},
                {"name": "Actualizar registro", "value": "update_record", "disabled": db_connection is None},
                {"name": "Eliminar registro", "value": "delete_record", "disabled": db_connection is None},
                {"name": "Crear nueva tabla", "value": "create_table", "disabled": db_connection is None},
                {"name": "Agregar columna a tabla", "value": "alter_table", "disabled": db_connection is None},
                {"name": "Eliminar tabla", "value": "drop_table", "disabled": db_connection is None},
                {"name": "Ejecutar consulta SQL personalizada", "value": "execute_query", "disabled": db_connection is None},
                {"name": "Salir", "value": "exit"}
            ],
        ).execute()

        if menu_options == "connect":
            if db_connection and db_connection.get_status():
                console.print("[warning]Ya estás conectado a una base de datos. Desconéctate primero para conectarte a otra.[/warning]")
            else:
                connect_to_db()

        elif menu_options == "disconnect":
            disconnect_db()

        elif menu_options == "view_tables":
            view_tables()

        elif menu_options == "read_table":
            read_table()

        elif menu_options == "insert_table":
            insert_into_table()

        elif menu_options == "update_record":
            update_record()

        elif menu_options == "delete_record":
            delete_record()

        elif menu_options == "create_table":
            create_table()

        elif menu_options == "alter_table":
            alter_table_add_column()

        elif menu_options == "drop_table":
            drop_table()

        elif menu_options == "execute_query":
            execute_custom_query()

        elif menu_options == "exit":
            if db_connection:
                disconnect_db()
            console.print("¡Adiós!")
            sys.exit(0)

if __name__ == "__main__":
    main_menu()
