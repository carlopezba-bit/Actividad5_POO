"""Interfaz gráfica del ejercicio 8.4 - Cuadros de diálogo (Nómina).

Adaptación a Python/Tkinter del ejercicio del libro de Leonardo Bermón Angarita.
Ejecutar con: python interfaz.py
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from modelos import Empleado, ListaEmpleados, TipoCargo, TipoGenero


def moneda(valor):
    """Presenta una cantidad en pesos con dos decimales."""
    return f"${valor:,.2f}"


class VentanaAgregarEmpleado(tk.Toplevel):
    """Cuadro de diálogo para registrar un empleado."""

    def __init__(self, principal, lista_empleados):
        super().__init__(principal)
        self.principal = principal
        self.lista_empleados = lista_empleados
        self.title("Agregar empleado")
        self.resizable(False, False)
        self.transient(principal)
        self.grab_set()

        marco = ttk.Frame(self, padding=20)
        marco.grid(row=0, column=0)

        self.campos = {}
        etiquetas = [
            ("nombre", "Nombre:"),
            ("apellidos", "Apellidos:"),
            ("salario_dia", "Salario por día:"),
            ("otros_ingresos", "Otros ingresos:"),
            ("pagos_salud", "Pagos por salud:"),
            ("aporte_pensiones", "Aporte pensiones:"),
        ]

        ttk.Label(marco, text="DATOS DEL EMPLEADO", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )
        fila = 1
        for clave, etiqueta in etiquetas[:2]:
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=5)
            entrada = ttk.Entry(marco, width=30)
            entrada.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=5)
            self.campos[clave] = entrada
            fila += 1

        ttk.Label(marco, text="Cargo:").grid(row=fila, column=0, sticky="w", pady=5)
        self.cargo = ttk.Combobox(
            marco, state="readonly", width=27, values=[cargo.value for cargo in TipoCargo]
        )
        self.cargo.set(TipoCargo.OPERATIVO.value)
        self.cargo.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=5)
        fila += 1

        ttk.Label(marco, text="Género:").grid(row=fila, column=0, sticky="w", pady=5)
        self.genero = tk.StringVar(value=TipoGenero.FEMENINO.value)
        grupo_genero = ttk.Frame(marco)
        grupo_genero.grid(row=fila, column=1, sticky="w", padx=(12, 0), pady=5)
        for genero in TipoGenero:
            ttk.Radiobutton(
                grupo_genero, text=genero.value, variable=self.genero, value=genero.value
            ).pack(side="left", padx=(0, 10))
        fila += 1

        clave, etiqueta = etiquetas[2]
        ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=5)
        entrada = ttk.Entry(marco, width=30)
        entrada.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=5)
        self.campos[clave] = entrada
        fila += 1

        ttk.Label(marco, text="Días trabajados:").grid(
            row=fila, column=0, sticky="w", pady=5
        )
        self.dias = tk.Spinbox(marco, from_=1, to=31, width=8)
        self.dias.grid(row=fila, column=1, sticky="w", padx=(12, 0), pady=5)
        fila += 1

        for clave, etiqueta in etiquetas[3:]:
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=5)
            entrada = ttk.Entry(marco, width=30)
            entrada.insert(0, "0")
            entrada.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=5)
            self.campos[clave] = entrada
            fila += 1

        botones = ttk.Frame(marco)
        botones.grid(row=fila, column=0, columnspan=2, pady=(18, 0))
        ttk.Button(botones, text="Agregar", command=self.agregar_empleado).pack(
            side="left", padx=6
        )
        ttk.Button(botones, text="Borrar", command=self.limpiar_campos).pack(
            side="left", padx=6
        )
        ttk.Button(botones, text="Cerrar", command=self.destroy).pack(
            side="left", padx=6
        )

        self.campos["nombre"].focus_set()

    def agregar_empleado(self):
        """Valida los campos y añade el empleado a la lista compartida."""
        try:
            nuevo = Empleado(
                nombre=self.campos["nombre"].get().strip(),
                apellidos=self.campos["apellidos"].get().strip(),
                cargo=self.cargo.get(),
                genero=self.genero.get(),
                salario_dia=float(self.campos["salario_dia"].get().strip()),
                dias_trabajados=int(self.dias.get()),
                otros_ingresos=float(self.campos["otros_ingresos"].get().strip()),
                pagos_salud=float(self.campos["pagos_salud"].get().strip()),
                aporte_pensiones=float(self.campos["aporte_pensiones"].get().strip()),
            )
        except ValueError as error:
            messagebox.showerror(
                "Datos inválidos",
                f"Revisa los campos. Escribe valores numéricos sin símbolos.\n\n{error}",
                parent=self,
            )
            return

        self.lista_empleados.agregar_empleado(nuevo)
        self.principal.actualizar_contador()
        messagebox.showinfo(
            "Empleado agregado",
            f"{nuevo.nombre} {nuevo.apellidos} se agregó correctamente.\n"
            f"Salario mensual: {moneda(nuevo.calcular_nomina())}",
            parent=self,
        )
        self.limpiar_campos()

    def limpiar_campos(self):
        """Limpia las entradas para añadir un nuevo empleado."""
        for clave, entrada in self.campos.items():
            entrada.delete(0, tk.END)
            if clave in ("otros_ingresos", "pagos_salud", "aporte_pensiones"):
                entrada.insert(0, "0")
        self.cargo.set(TipoCargo.OPERATIVO.value)
        self.genero.set(TipoGenero.FEMENINO.value)
        self.dias.delete(0, tk.END)
        self.dias.insert(0, "1")
        self.campos["nombre"].focus_set()


class VentanaNomina(tk.Toplevel):
    """Consulta de los empleados en tabla y total mensual de nómina."""

    def __init__(self, principal, lista_empleados):
        super().__init__(principal)
        self.title("Nómina de empleados")
        self.geometry("650x350")
        self.minsize(580, 280)

        marco = ttk.Frame(self, padding=18)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="NÓMINA DE EMPLEADOS", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(0, 12)
        )

        columnas = ("nombre", "apellidos", "sueldo")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=9)
        tabla.heading("nombre", text="NOMBRE")
        tabla.heading("apellidos", text="APELLIDOS")
        tabla.heading("sueldo", text="SUELDO MENSUAL")
        tabla.column("nombre", width=160, anchor="w")
        tabla.column("apellidos", width=160, anchor="w")
        tabla.column("sueldo", width=180, anchor="e")

        desplazamiento = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=desplazamiento.set)
        tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="left", fill="y")

        # Se llena la tabla con los datos que proporciona modelos.py.
        for nombre, apellidos, sueldo in lista_empleados.obtener_matriz():
            tabla.insert("", tk.END, values=(nombre, apellidos, moneda(sueldo)))

        pie = ttk.Frame(self, padding=(18, 0, 18, 18))
        pie.pack(fill="x")
        ttk.Label(
            pie,
            text="Total nómina mensual: " + moneda(lista_empleados.calcular_total_nomina()),
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="e")


class VentanaPrincipal(tk.Tk):
    """Ventana inicial con el menú de opciones indicado en el libro."""

    def __init__(self):
        super().__init__()
        self.title("Nómina - Ejercicio 8.4")
        self.geometry("440x320")
        self.resizable(False, False)
        self.empleados = ListaEmpleados()

        barra = tk.Menu(self)
        opciones = tk.Menu(barra, tearoff=False)
        opciones.add_command(label="Agregar empleado", command=self.abrir_agregar)
        opciones.add_command(label="Calcular nómina", command=self.abrir_nomina)
        opciones.add_command(label="Guardar archivo", command=self.guardar_archivo)
        barra.add_cascade(label="Menú", menu=opciones)
        self.config(menu=barra)

        marco = ttk.Frame(self, padding=25)
        marco.pack(fill="both", expand=True)
        ttk.Label(
            marco, text="SISTEMA DE NÓMINA", font=("Segoe UI", 15, "bold")
        ).pack(pady=(8, 9))
        ttk.Label(marco, text="Ejercicio 8.4 · Programación Orientada a Objetos").pack(
            pady=(0, 18)
        )

        ttk.Button(marco, text="Agregar empleado", command=self.abrir_agregar).pack(
            fill="x", pady=4
        )
        ttk.Button(marco, text="Calcular nómina", command=self.abrir_nomina).pack(
            fill="x", pady=4
        )
        ttk.Button(marco, text="Guardar archivo", command=self.guardar_archivo).pack(
            fill="x", pady=4
        )
        self.contador = ttk.Label(marco, text="Empleados registrados: 0")
        self.contador.pack(pady=(17, 0))

    def actualizar_contador(self):
        self.contador.configure(
            text=f"Empleados registrados: {len(self.empleados.lista)}"
        )

    def abrir_agregar(self):
        VentanaAgregarEmpleado(self, self.empleados)

    def abrir_nomina(self):
        VentanaNomina(self, self.empleados)

    def guardar_archivo(self):
        """Pide una carpeta y crea en ella el archivo Nómina.txt."""
        if not self.empleados.lista:
            messagebox.showwarning(
                "Sin empleados", "Primero debes registrar al menos un empleado.",
                parent=self,
            )
            return

        carpeta = filedialog.askdirectory(
            parent=self, title="Selecciona la carpeta donde guardar Nómina.txt"
        )
        if not carpeta:
            return
        archivo = Path(carpeta) / "Nómina.txt"
        if archivo.exists() and not messagebox.askyesno(
            "Reemplazar archivo",
            "El archivo Nómina.txt ya existe en esa carpeta. ¿Deseas reemplazarlo?",
            parent=self,
        ):
            return

        try:
            archivo.write_text(self.empleados.convertir_texto(), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error), parent=self)
        else:
            messagebox.showinfo(
                "Archivo guardado", f"Se guardó correctamente:\n{archivo}", parent=self
            )


if __name__ == "__main__":
    aplicacion = VentanaPrincipal()
    aplicacion.mainloop()
