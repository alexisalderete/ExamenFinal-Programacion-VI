from flet import *
import flet as ft
# Importa el conector de MySQL para que funcione la base de datos
import mysql.connector

# Conexión a la base de datos MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    db="appFlet"
)
# cursor para ejecutar comandos SQL en la base de datos
cursor = mydb.cursor()

#colores
color_fondo = '#001f33' 
color_fondo_appbar = '#00131F'
color_primario = '#2485F5'
#color_fondo_appbar = '#003556'

def main(page: ft.Page):
    page.theme = ft.Theme(
        font_family="Poppins"  # Nombre de la fuente registrada
    )
    
    # Registrar los archivos de fuente
    page.fonts = {
        "Poppins": "fonts/Poppins/Poppins-Regular.ttf",  # Ruta a la fuente regular
        "SF": "fonts/SF/SFPRODISPLAYREGULAR.OTF"
    }
    
    # Configura el título de la ventana de la aplicación
    page.title = "Engineer Education"
    # Establece el ancho de la ventana
    page.window.width = 400
    # Establece la altura de la ventana
    page.window.height = 680
    # Variable para almacenar el nombre del usuario actual
    usuario_actual = ""
    

    # Campo de texto para el nombre de usuario en la interfaz de usuario
    nombretxt = TextField(
        label="Nombre de usuario",# Etiqueta del campo de texto
        bgcolor= color_fondo,# Color de fondo negro
        color="white",# Color del texto blanco
        border_color="grey",# Color del borde gris
        border_radius=15# Bordes redondeados
    )
    
    # Campo de texto para la contraseña
    clavetxt = TextField(
        label="Contraseña",# Etiqueta del campo de texto
        bgcolor= color_fondo,# Color de fondo negro
        color="white",# Color del texto blanco
        border_color="grey",# Color del borde gris

        password=True,# Ocultar el texto como contraseña
        can_reveal_password=True,# Permite mostrar/ocultar contraseña
        border_radius=15# Bordes redondeados
    )
    
    #logo
    logo = ft.Image(src="/logo.png", width=250, height=250)
    logo_usuario = ft.Image(src="/usuario.png", width=150, height=150)
    
    def tipo_usuario(usuario_actual, cursor):
        """
        Verifica el tipo de usuario actual.
        :param usuario_actual: Nombre del usuario actual.
        :param cursor: Cursor de la base de datos.
        :return: El tipo de usuario ('Docente', 'Alumno', 'Administrador') o None si no se encuentra.
        """
        cursor.execute("SELECT usu_tipo FROM usuarios WHERE usu_nombre = %s", (usuario_actual,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

        
    # Función para crear el AppBar con un título dado
    def crear_appbar(titulo):
        
        tipo = tipo_usuario(usuario_actual, cursor)
        
        return ft.AppBar(
            title=ft.Text(titulo, size=18),  # Título del AppBar
            center_title=False,  # No centrar el título
            bgcolor=color_fondo_appbar,  # Color de fondo del AppBar
            actions=[  # Acciones en el AppBar
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text=usuario_actual, icon=icons.ACCOUNT_CIRCLE, on_click=lambda _: page.go("/")),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(text="Inicio", icon=icons.HOME_ROUNDED, on_click=lambda _: page.go("/")),
                        
                        # Solo mostrar "Cargar calificaciones" si el usuario es docente
                        *(
                            [
                                ft.PopupMenuItem(text="Cargar calificaciones", icon=icons.NOTE_ADD_OUTLINED, on_click=lambda _: page.go("/cargar_calificacion"))
                            ]if tipo == "Docente" or tipo == "Administrador" else [
                                ft.PopupMenuItem(text="Calificaciones", icon=icons.TASK_OUTLINED, on_click=lambda _: page.go("/calificacion")),
                            ]
                        ),
                        ft.PopupMenuItem(text="Registrar estudiante", icon=icons.PERSON_ADD_ROUNDED, on_click=lambda _: page.go("/registro")),
                        ft.PopupMenuItem(
                            text="Cerrar sesión",
                            icon=icons.LOGOUT,
                            on_click=lambda _: (set_usuario_actual_vacio(), page.go("/login"))
                        ),
                    ],
                    bgcolor=color_fondo_appbar,
                ),
            ],
        )

    def set_usuario_actual_vacio():
        nonlocal usuario_actual
        usuario_actual = ""
        
    # Función para mostrar un cuadro de alerta
    def mostrar_alerta(titulo, mensaje):
        alerta = ft.AlertDialog(
            modal=True,# Cuadro de diálogo modal
            title=ft.Text(titulo),# Título del cuadro de alerta
            content=ft.Text(mensaje),# Mensaje del cuadro de alerta
            actions=[ft.TextButton("Aceptar", on_click=lambda _: page.close(alerta))],
            actions_alignment=ft.MainAxisAlignment.END,  # Alineación de los botones
        )
        #page.dialog = alerta
        page.overlay.append(alerta)# Añade la alerta a la superposición
        alerta.open = True# Abre el cuadro de alerta
        page.update()
    
    # Función para manejar la autenticación
    def iniciar_sesion(e):
        nonlocal usuario_actual
        # Obtiene el nombre de usuario y contraseña ingresados
        username, password = nombretxt.value, clavetxt.value
            
        # Verifica que se ingresaron ambos campos
        if username and password:
            # Consulta SQL para verificar si el usuario y contraseña existen
            cursor.execute("SELECT * FROM usuarios WHERE usu_nombre = %s AND usu_clave = %s", (username, password))
            # Si la consulta devuelve un resultado, el usuario existe
            if cursor.fetchone():
                usuario_actual = username        # Guarda el usuario actual
                page.go("/")                     # Redirige a la página principal
                nombretxt.value, clavetxt.value = "", ""  # Limpia los campos de entrada
            else:
                mostrar_alerta("Error inesperado", "Nombre de usuario o contraseña incorrectos.")
        else:
            mostrar_alerta("Error inesperado", "Debes ingresar el nombre de usuario y la contraseña.")
            
        page.update()  # Actualiza la interfaz de usuario
    # Función para registrar un nuevo usuario
    def registrar_usuario(e):
        nonlocal usuario_actual
        # Obtiene el nombre de usuario y contraseña ingresados
        nuevo_usuario = nombre_registro.value
        nueva_clave = clave_registro.value
        nueva_clave_confirmar = clave_registro_confirmar.value

        # Verifica que se ingresaron ambos campos
        if nuevo_usuario and nueva_clave and nueva_clave_confirmar:
            # Consulta SQL para verificar si el usuario ya existe
            cursor.execute("SELECT * FROM usuarios WHERE usu_nombre = %s", (nuevo_usuario,))
            if cursor.fetchone():  # Si existe un resultado, el usuario ya está registrado
                mostrar_alerta("Error inesperado", "El usuario ya existe.")
            elif nueva_clave != nueva_clave_confirmar:
                mostrar_alerta("Error inesperado", "Las contraseñas son distintas.")
            else:
                # Inserta el nuevo usuario en la base de datos
                cursor.execute("INSERT INTO usuarios (usu_nombre, usu_clave, usu_tipo, usu_estado) VALUES (%s, %s, 'Estudiante', 'Activo')", (nuevo_usuario, nueva_clave))
                mydb.commit()# Confirma la transacción
                usuario_actual = nuevo_usuario# Guarda el usuario actual
                page.go("/")# Redirige a la página principal
                nombre_registro.value = ""
                clave_registro.value = ""
        else:
            mostrar_alerta("Error inesperado", "Debes llenar todos los campos.")
        page.update()
        
        
    def listar_calificaciones():
        nonlocal usuario_actual
        cursor.execute(
            "SELECT * FROM calificaciones "
            "INNER JOIN materias ON calificaciones.idmaterias = materias.idmaterias "
            "INNER JOIN usuarios ON calificaciones.idusuarios = usuarios.idusuarios "
            "WHERE usuarios.usu_nombre = %s", 
            (usuario_actual,)
        )
        resultados = cursor.fetchall()
        columnas = [columna[0] for columna in cursor.description]
        filas = [dict(zip(columnas, fila)) for fila in resultados]

        # Función para determinar el valor final basado en el rango
        def calcular_nota_final(total):
            if total <= 59:
                return 1
            if 60 <= total <= 69:
                return 2
            elif 70 <= total <= 79:
                return 3
            elif 80 <= total <= 90:
                return 4
            elif 91 <= total <= 100:
                return 5
            else:
                return 0  # En caso de que no cumpla con ningún rango

        tabla = DataTable(
        columns=[
            DataColumn(Text("Materia", size=14)),  # Texto más pequeño
            DataColumn(Text("PP", size=14)),
            DataColumn(Text("SP", size=14)),
            DataColumn(Text("TP", size=14)),
            DataColumn(Text("EF", size=14)),
            DataColumn(Text("Total", size=14)),
            DataColumn(Text("C. Final", size=14)),
        ],
        rows=[
            DataRow(
                cells=[
                    DataCell(Text(fila['materias_nombre'], size=14)),  # Texto reducido
                    DataCell(Text(fila['calificaciones_primer_parcial'], size=14)),
                    DataCell(Text(fila['calificaciones_segundo_parcial'], size=14)),
                    DataCell(Text(fila['calificaciones_trabajo_practico'], size=14)),
                    DataCell(Text(fila['calificaciones_examen_final'], size=14)),
                    DataCell(Text(
                        float(fila['calificaciones_primer_parcial']) +
                        float(fila['calificaciones_segundo_parcial']) +
                        float(fila['calificaciones_trabajo_practico']) +
                        float(fila['calificaciones_examen_final']),
                        size=14
                    )),
                    DataCell(Text(
                        str(calcular_nota_final(
                            float(fila['calificaciones_primer_parcial']) +
                            float(fila['calificaciones_segundo_parcial']) +
                            float(fila['calificaciones_trabajo_practico']) +
                            float(fila['calificaciones_examen_final']
                        ))),
                        size=14
                    )),
                ]
            ) for fila in filas
        ],
        column_spacing=16,  # Reduce el espaciado entre columnas
        )

        return tabla
    
    
    tabla_contenedor = Container()
    def cargar_calificaciones():
        tipo = tipo_usuario(usuario_actual, cursor)
        cursor.execute(
            "SELECT * FROM calificaciones "
            "INNER JOIN materias ON calificaciones.idmaterias = materias.idmaterias "
            "INNER JOIN usuarios ON calificaciones.idusuarios = usuarios.idusuarios"
        )
        resultados = cursor.fetchall()
        columnas = [columna[0] for columna in cursor.description]
        filas = [dict(zip(columnas, fila)) for fila in resultados]

        def calcular_nota_final(total):
            if total <= 59:
                return 1
            elif 60 <= total <= 69:
                return 2
            elif 70 <= total <= 79:
                return 3
            elif 80 <= total <= 90:
                return 4
            elif 91 <= total <= 100:
                return 5
            return 0

        # Construir columnas dinámicamente
        columnas_tabla = [
            DataColumn(Text("E", size=10)),
            DataColumn(Text("M", size=10)),
            DataColumn(Text("PP", size=10)),
            DataColumn(Text("SP", size=10)),
            DataColumn(Text("TP", size=10)),
            DataColumn(Text("EF", size=10)),
            DataColumn(Text("Total", size=10)),
            DataColumn(Text("C. F", size=10)),
        ]

        # Agregar columna de "Acciones" solo si el usuario es administrador
        if tipo == "Administrador":
            columnas_tabla.append(DataColumn(Text("Acciones", size=10)))

        # Construir filas dinámicamente
        filas_tabla = [
            DataRow(
                cells=[
                    DataCell(Text(fila['usu_nombre'], size=10)),
                    DataCell(Text(fila['materias_nombre'], size=10)),
                    DataCell(Text(fila['calificaciones_primer_parcial'], size=10)),
                    DataCell(Text(fila['calificaciones_segundo_parcial'], size=10)),
                    DataCell(Text(fila['calificaciones_trabajo_practico'], size=10)),
                    DataCell(Text(fila['calificaciones_examen_final'], size=10)),
                    DataCell(Text(
                        float(fila['calificaciones_primer_parcial']) +
                        float(fila['calificaciones_segundo_parcial']) +
                        float(fila['calificaciones_trabajo_practico']) +
                        float(fila['calificaciones_examen_final']), size=10
                    )),
                    DataCell(Text(str(calcular_nota_final(
                        float(fila['calificaciones_primer_parcial']) +
                        float(fila['calificaciones_segundo_parcial']) +
                        float(fila['calificaciones_trabajo_practico']) +
                        float(fila['calificaciones_examen_final']
                    ))), size=10)),
                    # Agregar celda de "Acciones" solo si el usuario es administrador
                    *(
                        [DataCell(
                            Row([
                                Container(
                                    content=IconButton(
                                        "edit",
                                        icon_color="blue",
                                        data=fila,
                                        icon_size=18,
                                        on_click=editar_calificaciones,
                                        padding=0
                                    ),
                                ),
                                Container(
                                    content=IconButton(
                                        "delete",
                                        icon_color="red",
                                        data=fila,
                                        icon_size=18,
                                        on_click=eliminar_calificaciones,
                                        padding=0
                                    ),
                                ),
                            ], spacing=0)  # Reduce el espacio entre los íconos
                        )] if tipo == "Administrador" else []
                    ),
                ]
            ) for fila in filas
        ]

        # Crear tabla
        tabla = DataTable(
            columns=columnas_tabla,
            rows=filas_tabla,
            column_spacing=16,  # Ajusta el espaciado entre columnas si es necesario
        )
        
        tabla_contenedor.content = tabla
        page.update()


        
    def eliminar_calificaciones(e):
        sql = "DELETE FROM calificaciones WHERE idcalificaciones = %s"
        val = (e.control.data['idcalificaciones'],)
        cursor.execute(sql, val)
        mydb.commit()
        cargar_calificaciones()
        
        
    
    
    
    
    #----------------------------- inicio agregar calificaciones -----------------------
    # Inputs para ingresar datos nuevos
    txt_id_estudiante = TextField(label="ID estudiante", keyboard_type="number", width=250)
    txt_id_materia = TextField(label="ID Materia", keyboard_type="number", width=250)
    txt_pp = TextField(label="Primer parcial", keyboard_type="number", width=250)
    txt_sp = TextField(label="Segundo parcial", keyboard_type="number", width=250)
    txt_tp = TextField(label="Trabajo práctico", keyboard_type="number", width=250)
    txt_ef = TextField(label="Examen Final", keyboard_type="number", width=250)
    
    def agregar_calificaciones(e):
        
        def guardar_calificaciones(e): 
            # Validar campos
            if not txt_pp.value or not txt_pp.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Primer Parcial debe ser un número válido.")
                return
            if not txt_sp.value or not txt_sp.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Segundo Parcial debe ser un número válido.")
                return
            if not txt_tp.value or not txt_tp.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Trabajo Práctico debe ser un número válido.")
                return
            if not txt_ef.value or not txt_ef.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Examen Final debe ser un número válido.")
                return
            if not txt_id_materia.value or not txt_id_materia.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Materia debe ser un número válido.")
                return
            if not txt_id_estudiante.value or not txt_id_estudiante.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Estudiante debe ser un número válido.")
                return
            
            # Validación del rango total
            total = float(txt_pp.value) + float(txt_sp.value) + float(txt_tp.value) + float(txt_ef.value)
            if total < 0 or total > 100:
                mostrar_alerta("Error de Validación", "Rango no válido.")
                return
            
            
            #verificar si existe materia
            cursor.execute("SELECT * FROM materias WHERE idmaterias = %s", (txt_id_materia.value,))
            if not cursor.fetchone():  # Si existe un resultado, el usuario ya está registrado
                mostrar_alerta("Error inesperado", "La materia no existe.")
                return
            
            #verificar si existe el estudiante
            cursor.execute("SELECT * FROM usuarios WHERE idusuarios = %s", (txt_id_estudiante.value,))
            if not cursor.fetchone():  # Si existe un resultado, el usuario ya está registrado
                mostrar_alerta("Error inesperado", "El estudiante no existe.")
                return
            
            # Proceder con la inserción en la base de datos
            sql = """
                INSERT INTO calificaciones (
                    calificaciones_primer_parcial, calificaciones_segundo_parcial, 
                    calificaciones_trabajo_practico, calificaciones_examen_final, 
                    idmaterias, idusuarios
                ) VALUES (%s, %s, %s, %s, %s, %s);
            """
            val = (
                txt_pp.value, txt_sp.value, txt_tp.value, txt_ef.value,
                txt_id_materia.value, txt_id_estudiante.value
            )
            cursor.execute(sql, val)
            mydb.commit()

            # Cerrar el formulario y recargar la tabla
            formulario.open = False
            cargar_calificaciones()
            txt_pp.value = txt_sp.value = txt_tp.value = txt_ef.value = txt_id_materia.value = txt_id_estudiante.value = ""  # Limpiar
            page.update()



        # Modificar el formulario para integrar la validación
        formulario = AlertDialog(
            title=Text("Agregar Calificaciones"),
            content=Column([
                txt_pp, txt_sp, txt_tp, txt_ef, txt_id_materia, txt_id_estudiante,
            ]),
            actions=[
                TextButton("Guardar", on_click=guardar_calificaciones),
                TextButton("Cancelar", on_click=lambda e: cerrar_formulario_agregar(e)),
            ],
            bgcolor=color_fondo
        )
        page.overlay.append(formulario)
        formulario.open = True
        page.update()
        
        def cerrar_formulario_agregar(e):
            formulario.open = False  # Cerrar el formulario
            page.update()  # Actualizar la página
            
    #----------------------------- FIN agregar calificaciones -----------------------
    
        
        
    #----------------------------- inicio ediar calificaciones -----------------------
    # Inputs para editar datos de una calificación existente
    txt_pp_edit = TextField(label="Primer parcial", keyboard_type="number", width=250)
    txt_sp_edit = TextField(label="Segundo parcial", keyboard_type="number", width=250)
    txt_tp_edit = TextField(label="Trabajo práctico", keyboard_type="number", width=250)
    txt_ef_edit = TextField(label="Examen Final", keyboard_type="number", width=250)

    # Función para mostrar el formulario de edición
    def editar_calificaciones(e):
        fila = e.control.data  # Datos de la fila seleccionada

        # Rellenar los campos con los valores actuales
        txt_pp_edit.value = fila['calificaciones_primer_parcial']
        txt_sp_edit.value = fila['calificaciones_segundo_parcial']
        txt_tp_edit.value = fila['calificaciones_trabajo_practico']
        txt_ef_edit.value = fila['calificaciones_examen_final']

        # Guardar los cambios
        def guardar_edicion(e):
            # Validaciones
            if not txt_pp_edit.value or not txt_pp_edit.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Primer Parcial debe ser un número válido.")
                return
            if not txt_sp_edit.value or not txt_sp_edit.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Segundo Parcial debe ser un número válido.")
                return
            if not txt_tp_edit.value or not txt_tp_edit.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Trabajo Práctico debe ser un número válido.")
                return
            if not txt_ef_edit.value or not txt_ef_edit.value.isdigit():
                mostrar_alerta("Error de Validación", "El campo Examen Final debe ser un número válido.")
                return
            
            # Validación del rango total
            total = float(txt_pp_edit.value) + float(txt_sp_edit.value) + float(txt_tp_edit.value) + float(txt_ef_edit.value)
            if total < 0 or total > 100:
                mostrar_alerta("Error de Validación", "Rango no válido.")
                return

            # Si todas las validaciones pasan, se guarda la información
            sql = """
            UPDATE calificaciones 
            SET calificaciones_primer_parcial = %s, 
                calificaciones_segundo_parcial = %s, 
                calificaciones_trabajo_practico = %s, 
                calificaciones_examen_final = %s 
            WHERE idcalificaciones = %s
            """
            val = (
                txt_pp_edit.value,
                txt_sp_edit.value,
                txt_tp_edit.value,
                txt_ef_edit.value,
                fila['idcalificaciones'],  # ID de la calificación a editar
            )
            cursor.execute(sql, val)
            mydb.commit()

            formulario_editar.open = False  # Cerrar el formulario
            cargar_calificaciones()  # Recargar la tabla actualizada
            page.update()

        # Crear y mostrar el diálogo de edición
        formulario_editar = AlertDialog(
            title=Text("Editar Calificación"),
            content=Column([txt_pp_edit, txt_sp_edit, txt_tp_edit, txt_ef_edit]),
            actions=[
                TextButton("Guardar", on_click=guardar_edicion),
                TextButton("Cancelar", on_click=lambda e: cerrar_formulario_editar(e)),
            ],
            bgcolor=color_fondo
        )
        page.overlay.append(formulario_editar)
        formulario_editar.open = True
        page.update()

        # Función para cerrar el formulario editar
        def cerrar_formulario_editar(e):
            formulario_editar.open = False  # Cerrar el formulario
            page.update()  # Actualizar la página
            
    #----------------------------- FIN editar calificaciones -----------------------
        
        


    # Contenedor con elementos UI para el login
    contenedor_login = Container(
        content=Column(
            [
                logo_usuario,
                
                ft.Divider(height=10, color=color_fondo),
                Text("Iniciar sesión", size=24, weight="bold", color="white"),
                nombretxt, clavetxt,                
                ft.Divider(height=10, color=color_fondo),
                ElevatedButton(text="Iniciar sesión",bgcolor=color_primario, color="white", width=page.window.width * 0.8, height=35, on_click=iniciar_sesion),
                ft.Divider(height=5, color=color_fondo),
                Container(
                    content=Text("¿No tienes una cuenta?", size=14, color="grey", text_align="center"),
                    on_click=lambda _: page.go("/registro"),
                ),
            ],
            alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=10,
        ),
        bgcolor=color_fondo, border_radius=10, alignment=alignment.center, padding=20, width=380, height=600,
    )
    # Campos de texto para el registro
    nombre_registro = TextField(label="Nombre de usuario", bgcolor=color_fondo, color="white",border_color="grey", border_radius=15)
    clave_registro = TextField(label="Contraseña", bgcolor=color_fondo, color="white", password=True, can_reveal_password=True,border_color="grey", border_radius=15)
    clave_registro_confirmar = TextField(label="Confirmar contraseña", bgcolor=color_fondo, color="white", password=True, can_reveal_password=True,border_color="grey", border_radius=15)
    # Contenedor con elementos UI para el registro
    contenedor_registro = Container(
        content=Column(
            [
                logo_usuario,
                
                ft.Divider(height=10, color=color_fondo),
                Text("Registrar estudiante", size=24, weight="bold", color="white"),
                nombre_registro, 
                clave_registro,
                clave_registro_confirmar,
                ft.Divider(height=10, color=color_fondo),
                ElevatedButton(text="Registrar",bgcolor=color_primario, color="white", width=page.window.width * 0.8, height=35, on_click=registrar_usuario),
                
                Container(
                    content=Text("¿Ya tienes una cuenta?", size=14, color="grey", text_align="center"),
                    on_click=lambda _: page.go("/login"),
                ),
            ],
            alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=10,
        ),
        bgcolor=color_fondo, border_radius=10, alignment=alignment.center, padding=20, width=380, height=600,
    )
    
    contenedor_inicio = Container(content=Column([logo,],),)
    # Función para cambiar la vista según la ruta
    def route_change(route):
        page.views.clear() # Limpia las vistas actuales
        
        tipo = tipo_usuario(usuario_actual, cursor)
        page.views.append(
            ft.View(
                "/",
                [   
                    crear_appbar("Engineer Education"),
                    contenedor_inicio,
                    
                    # Mostrar el tipo de usuario
                    *(
                        [
                            Text(f"Tipo de usuario: Docente", size=16, color="white"),
                        ] if tipo == "Docente" else [
                            Text(f"Tipo de usuario: Estudiante", size=16, color="white"),
                        ] if tipo == "Estudiante" else [
                            Text(f"Tipo de usuario: Administrador", size=16, color="white"),
                        ]
                    ),
                    
                    
                    Text(f"¡Bienvenido {usuario_actual}!", size=24, color="white"),
                    
                    *(
                            [
                                ft.ElevatedButton("Cargar calificacioes",
                                    bgcolor=color_primario, 
                                    color="white", 
                                    width=250, 
                                    height=35, icon=icons.NOTE_ADD_OUTLINED, 
                                    on_click=lambda _: page.go("/cargar_calificacion")),
                            ]if tipo == "Docente" or tipo == "Administrador" else [
                            ft.ElevatedButton("Ver calificación", 
                                    bgcolor=color_primario, 
                                    color="white", 
                                    width=250, 
                                    height=35, icon=icons.TASK_OUTLINED, 
                                    on_click=lambda _: page.go("/calificacion")),
                            ]
                    ),
                    
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                bgcolor= color_fondo
            )
        )
        if page.route == "/calificacion":
            # Vista de calificación
            page.views.append(
                ft.View(
                    "/calificacion",
                    [
                        crear_appbar("Calificaciones"),
                        listar_calificaciones(),
                        ft.ElevatedButton("Ir al Inicio", icon=icons.HOME_ROUNDED, bgcolor=color_primario, color="white", width=200, height=35,  on_click=lambda _: page.go("/"))
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    bgcolor=color_fondo
                )
            )
        elif page.route == "/cargar_calificacion":
            cargar_calificaciones()
            # Vista de calificación
            page.views.append(
                ft.View(
                    "/cargar_calificacion",
                    [
                        crear_appbar("Calificaciones"),
                        ft.ElevatedButton("Nueva calificación", icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED, bgcolor=color_primario, color="white", width=250, height=35,  on_click=agregar_calificaciones),
                        tabla_contenedor,
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    bgcolor=color_fondo
                )
            )
        elif page.route == "/login":
            # Vista de login
            page.views.append(
                ft.View(
                    "/login",
                    [
                        contenedor_login
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                )
            )
        elif page.route == "/registro" and usuario_actual != "":
            # Vista de registro
            page.views.append(
                ft.View(
                    "/registro",
                    [
                        crear_appbar("Calificaciones"),
                        contenedor_registro
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                )
            )
        elif page.route == "/registro":
            # Vista de registro
            page.views.append(
                ft.View(
                    "/registro",
                    [
                        contenedor_registro
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                )
            )
        page.update()  # Actualiza la vista


    # Configura la navegación y ruta inicial
    def view_pop(view):
        if len(page.views) > 1:  # Verifica que hay vistas en la pila
            page.views.pop()  # Elimina la vista actual
            top_view = page.views[-1]  # Obtiene la vista anterior
            page.go(top_view.route)  # Navega a la ruta de la vista anterior
        else:
            page.go("/")
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    #page.on_route_change, page.on_view_pop = route_change, lambda _: page.views.pop() or page.go(page.views[-1].route)
    page.go("/login")  # Establece la página inicial en login
ft.app(target=main, assets_dir="img")
