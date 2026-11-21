"""Actividad 5 - Ejercicio 8.5: Gestión de un hotel (interfaz gráfica).

Adaptación a Python/Tkinter del ejercicio del libro de Leonardo Bermón Angarita.
Ejecutar en esta carpeta con: python interfaz.py

Las reservas se conservan en memoria mientras la aplicación permanece abierta.
No se necesita instalar paquetes adicionales.
"""

from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from modelos import Hotel, Huesped


FORMATO_FECHA = "%Y-%m-%d"


def dinero(valor):
    """Muestra precios en pesos colombianos, sin decimales."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def leer_fecha(texto):
    """Convierte una fecha estrictamente en formato AAAA-MM-DD."""
    texto = texto.strip()
    try:
        fecha = datetime.strptime(texto, FORMATO_FECHA).date()
    except ValueError as error:
        raise ValueError("Escribe una fecha válida en formato AAAA-MM-DD (ejemplo: 2026-11-20).") from error
    # strptime admite algunos números sin cero inicial; aquí exigimos el formato indicado.
    if fecha.strftime(FORMATO_FECHA) != texto:
        raise ValueError("Usa exactamente el formato AAAA-MM-DD (ejemplo: 2026-11-20).")
    return fecha


class VentanaPrincipal(tk.Tk):
    """Menú principal y estado general de las habitaciones."""

    def __init__(self):
        super().__init__()
        self.hotel = Hotel()
        self.title("Hotel - Ejercicio 8.5")
        self.geometry("540x380")
        self.minsize(500, 340)

        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 17, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 10))
        estilo.configure("Accion.TButton", padding=(14, 11), font=("Segoe UI", 10))
        estilo.configure("TLabel", font=("Segoe UI", 10))
        estilo.configure("TButton", padding=(9, 6))
        estilo.configure("Treeview", rowheight=27, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        menu_barra = tk.Menu(self)
        menu_gestion = tk.Menu(menu_barra, tearoff=False)
        menu_gestion.add_command(label="Consultar habitaciones", command=self.abrir_habitaciones)
        menu_gestion.add_command(label="Salida de huéspedes", command=self.abrir_salida)
        menu_barra.add_cascade(label="Gestión del hotel", menu=menu_gestion)
        self.config(menu=menu_barra)

        marco = ttk.Frame(self, padding=30)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="SISTEMA DE GESTIÓN HOTELERA", style="Titulo.TLabel").pack(pady=(10, 4))
        ttk.Label(
            marco,
            text="Ejercicio 8.5 · Programación Orientada a Objetos",
            style="Subtitulo.TLabel",
        ).pack(pady=(0, 25))

        ttk.Button(
            marco, text="Consultar habitaciones / Registrar ingreso",
            command=self.abrir_habitaciones, style="Accion.TButton"
        ).pack(fill="x", pady=7)
        ttk.Button(
            marco, text="Salida de huéspedes", command=self.abrir_salida,
            style="Accion.TButton"
        ).pack(fill="x", pady=7)

        ttk.Separator(marco).pack(fill="x", pady=(28, 15))
        self.estado = ttk.Label(marco, text="")
        self.estado.pack()
        ttk.Label(marco, text="Habitaciones 1–5: $120.000/día  ·  6–10: $160.000/día").pack(pady=9)
        self.actualizar_estado()

    def actualizar_estado(self):
        disponibles = sum(h.disponible for h in self.hotel.habitaciones)
        self.estado.configure(
            text=f"Habitaciones disponibles: {disponibles}     |     Ocupadas: {10 - disponibles}"
        )

    def abrir_habitaciones(self):
        VentanaHabitaciones(self, self.hotel)

    def abrir_salida(self):
        numero = simpledialog.askinteger(
            "Salida de huéspedes", "Número de habitación a entregar (1 a 10):",
            parent=self, minvalue=1, maxvalue=10
        )
        if numero is None:
            return
        habitacion = self.hotel.buscar_habitacion(numero)
        if habitacion.disponible:
            messagebox.showerror(
                "Habitación desocupada",
                f"La habitación {numero} está disponible. No existe un huésped para registrar salida.",
                parent=self,
            )
            return
        VentanaSalida(self, self.hotel, numero)


class VentanaHabitaciones(tk.Toplevel):
    """Consulta la disponibilidad y permite elegir una habitación para ocupar."""

    def __init__(self, principal, hotel):
        super().__init__(principal)
        self.principal = principal
        self.hotel = hotel
        self.title("Consultar habitaciones")
        self.geometry("680x525")
        self.minsize(570, 475)
        self.transient(principal)

        marco = ttk.Frame(self, padding=20)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="HABITACIONES DEL HOTEL", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", pady=(0, 8)
        )
        ttk.Label(
            marco, text="Selecciona una habitación disponible para registrar el ingreso."
        ).pack(anchor="w", pady=(0, 14))

        columnas = ("numero", "tarifa", "estado")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        self.tabla.heading("numero", text="HABITACIÓN")
        self.tabla.heading("tarifa", text="PRECIO POR DÍA")
        self.tabla.heading("estado", text="ESTADO")
        self.tabla.column("numero", width=140, anchor="center")
        self.tabla.column("tarifa", width=195, anchor="center")
        self.tabla.column("estado", width=185, anchor="center")
        self.tabla.tag_configure("ocupada", foreground="#A73535")
        self.tabla.tag_configure("libre", foreground="#236A44")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccion_tabla)
        self.tabla.bind("<Double-1>", lambda _evento: self.seleccionar_habitacion())

        controles = ttk.Frame(marco)
        controles.pack(fill="x", pady=(14, 0))
        ttk.Label(controles, text="N.º habitación:").pack(side="left")
        self.numero = tk.StringVar(value="1")
        self.selector = tk.Spinbox(
            controles, from_=1, to=10, width=5, textvariable=self.numero, justify="center"
        )
        self.selector.pack(side="left", padx=(8, 15))
        ttk.Button(controles, text="Registrar ingreso", command=self.seleccionar_habitacion).pack(
            side="left", padx=(0, 9)
        )
        ttk.Button(controles, text="Actualizar", command=self.mostrar_disponibilidad).pack(
            side="left"
        )
        ttk.Button(controles, text="Cerrar", command=self.destroy).pack(side="right")
        self.mostrar_disponibilidad()

    def mostrar_disponibilidad(self):
        actual = self.numero.get()
        self.tabla.delete(*self.tabla.get_children())
        for habitacion in self.hotel.habitaciones:
            etiqueta = "Disponible" if habitacion.disponible else "No disponible"
            self.tabla.insert(
                "", "end", iid=str(habitacion.numero),
                values=(habitacion.numero, dinero(habitacion.precio_dia), etiqueta),
                tags=("libre" if habitacion.disponible else "ocupada",)
            )
        if actual.isdigit() and 1 <= int(actual) <= 10:
            self.tabla.selection_set(actual)
            self.tabla.see(actual)
        self.principal.actualizar_estado()

    def _seleccion_tabla(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            self.numero.set(seleccion[0])

    def seleccionar_habitacion(self):
        try:
            numero = int(self.numero.get())
            habitacion = self.hotel.buscar_habitacion(numero)
        except (ValueError, TypeError):
            messagebox.showerror("Número incorrecto", "Selecciona un número de habitación entre 1 y 10.", parent=self)
            return
        if not habitacion.disponible:
            messagebox.showerror(
                "Habitación ocupada", f"La habitación {numero} no está disponible.", parent=self
            )
            return
        VentanaIngreso(self, self.hotel, numero, al_registrar=self.mostrar_disponibilidad)


class VentanaIngreso(tk.Toplevel):
    """Formulario de ingreso con campos obligatorios y validación de fecha."""

    def __init__(self, principal, hotel, numero_habitacion, al_registrar):
        super().__init__(principal)
        self.hotel = hotel
        self.habitacion = hotel.buscar_habitacion(numero_habitacion)
        self.al_registrar = al_registrar
        self.huesped_pendiente = None
        self.title(f"Ingreso de huésped - Habitación {numero_habitacion}")
        self.geometry("460x360")
        self.resizable(False, False)
        self.transient(principal)

        marco = ttk.Frame(self, padding=24)
        marco.pack(fill="both", expand=True)
        ttk.Label(
            marco, text=f"REGISTRO DE INGRESO · HABITACIÓN {numero_habitacion}",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 17))
        ttk.Label(marco, text=f"Tarifa diaria: {dinero(self.habitacion.precio_dia)}").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        self.entradas = {}
        campos = [
            ("fecha_ingreso", "Fecha de ingreso (AAAA-MM-DD):", date.today().isoformat()),
            ("nombres", "Nombres:", ""),
            ("apellidos", "Apellidos:", ""),
            ("documento", "Documento de identidad:", ""),
        ]
        for fila, (clave, etiqueta, predeterminado) in enumerate(campos, start=2):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=8)
            entrada = ttk.Entry(marco, width=22)
            entrada.insert(0, predeterminado)
            entrada.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=8)
            self.entradas[clave] = entrada

        botones = ttk.Frame(marco)
        botones.grid(row=6, column=0, columnspan=2, pady=(25, 0))
        ttk.Button(botones, text="Aceptar / Registrar ingreso", command=self.registrar_ingreso).pack(
            side="left", padx=(0, 9)
        )
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left")
        marco.columnconfigure(1, weight=1)
        self.entradas["nombres"].focus_set()

    def validar_datos(self):
        try:
            fecha_ingreso = leer_fecha(self.entradas["fecha_ingreso"].get())
            self.huesped_pendiente = Huesped(
                self.entradas["nombres"].get(),
                self.entradas["apellidos"].get(),
                self.entradas["documento"].get(),
                fecha_ingreso,
            )
            return True
        except ValueError as error:
            messagebox.showerror("Datos incorrectos", str(error), parent=self)
            return False

    def registrar_ingreso(self):
        if not self.validar_datos():
            return
        try:
            self.habitacion.asignar_huesped(self.huesped_pendiente)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error), parent=self)
            self.al_registrar()
            return
        huesped = self.huesped_pendiente
        messagebox.showinfo(
            "Ingreso registrado",
            f"Se registró correctamente a {huesped.nombres} {huesped.apellidos}.\n"
            f"Habitación: {self.habitacion.numero}\n"
            f"Fecha de ingreso: {huesped.fecha_ingreso:%Y-%m-%d}\n"
            "La habitación figura ahora como No disponible.",
            parent=self,
        )
        self.al_registrar()
        self.destroy()


class VentanaSalida(tk.Toplevel):
    """Calcula el alojamiento y confirma la salida solo después de validar."""

    def __init__(self, principal, hotel, numero_habitacion):
        super().__init__(principal)
        self.principal = principal
        self.hotel = hotel
        self.habitacion = hotel.buscar_habitacion(numero_habitacion)
        self.huesped = self.habitacion.huesped
        self.fecha_validada = None

        self.title(f"Salida de huéspedes - Habitación {numero_habitacion}")
        self.geometry("470x420")
        self.resizable(False, False)
        self.transient(principal)

        marco = ttk.Frame(self, padding=25)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="REGISTRO DE SALIDA", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", pady=(0, 16)
        )
        ttk.Label(marco, text=f"Habitación: {self.habitacion.numero}").pack(anchor="w", pady=4)
        ttk.Label(marco, text=f"Huésped: {self.huesped.nombres} {self.huesped.apellidos}").pack(
            anchor="w", pady=4
        )
        ttk.Label(marco, text=f"Fecha de ingreso: {self.huesped.fecha_ingreso:%Y-%m-%d}").pack(
            anchor="w", pady=4
        )
        ttk.Label(marco, text=f"Tarifa diaria: {dinero(self.habitacion.precio_dia)}").pack(
            anchor="w", pady=4
        )

        ttk.Separator(marco).pack(fill="x", pady=13)
        ttk.Label(marco, text="Fecha de salida (AAAA-MM-DD):").pack(anchor="w", pady=(0, 6))
        self.fecha_salida_var = tk.StringVar(value=date.today().isoformat())
        self.fecha_salida_var.trace_add("write", self._cambio_fecha)
        ttk.Entry(marco, textvariable=self.fecha_salida_var, width=24).pack(anchor="w")
        ttk.Button(marco, text="Calcular", command=self.calcular_pago).pack(
            anchor="w", pady=(13, 15)
        )

        self.etiqueta_dias = ttk.Label(marco, text="Cantidad de días: —")
        self.etiqueta_dias.pack(anchor="w", pady=4)
        self.etiqueta_total = ttk.Label(marco, text="Total a pagar: —", font=("Segoe UI", 12, "bold"))
        self.etiqueta_total.pack(anchor="w", pady=4)

        pie = ttk.Frame(marco)
        pie.pack(fill="x", pady=(19, 0))
        self.boton_registrar = ttk.Button(pie, text="Registrar salida", command=self.registrar_salida)
        self.boton_registrar.state(["disabled"])
        self.boton_registrar.pack(side="left")
        ttk.Button(pie, text="Cancelar", command=self.destroy).pack(side="right")

    def _cambio_fecha(self, *_args):
        # Si se edita la fecha después de calcular, hay que calcular de nuevo.
        self.fecha_validada = None
        if hasattr(self, "boton_registrar"):
            self.boton_registrar.state(["disabled"])
            self.etiqueta_dias.configure(text="Cantidad de días: —")
            self.etiqueta_total.configure(text="Total a pagar: —")

    def validar_fecha_salida(self):
        try:
            fecha = leer_fecha(self.fecha_salida_var.get())
            if fecha <= self.huesped.fecha_ingreso:
                raise ValueError("La fecha de salida debe ser posterior a la fecha de ingreso.")
            return True
        except ValueError as error:
            messagebox.showerror("Fecha incorrecta", str(error), parent=self)
            return False

    def calcular_pago(self):
        self.fecha_validada = None
        self.boton_registrar.state(["disabled"])
        if not self.validar_fecha_salida():
            return None
        fecha = leer_fecha(self.fecha_salida_var.get())

        # El cálculo no registra la salida ni modifica permanentemente los datos.
        anterior = self.huesped.fecha_salida
        try:
            self.huesped.fecha_salida = fecha
            dias = self.huesped.obtener_dias_alojamiento()
        except ValueError as error:
            messagebox.showerror("No se pudo calcular", str(error), parent=self)
            return None
        finally:
            self.huesped.fecha_salida = anterior

        total = dias * self.habitacion.precio_dia
        self.etiqueta_dias.configure(text=f"Cantidad de días: {dias}")
        self.etiqueta_total.configure(text=f"Total a pagar: {dinero(total)}")
        self.fecha_validada = fecha
        self.boton_registrar.state(["!disabled"])
        return total

    def registrar_salida(self):
        if self.fecha_validada is None or self.fecha_salida_var.get() != self.fecha_validada.isoformat():
            messagebox.showerror("Falta calcular", "Primero calcula el total con la fecha de salida válida.", parent=self)
            return
        if self.habitacion.disponible or self.habitacion.huesped is not self.huesped:
            messagebox.showerror("Habitación actualizada", "La habitación ya no tiene el mismo huésped.", parent=self)
            self._cambio_fecha()
            return
        try:
            self.huesped.fecha_salida = self.fecha_validada
            dias = self.huesped.obtener_dias_alojamiento()
            total = dias * self.habitacion.precio_dia
            self.habitacion.liberar()
        except ValueError as error:
            messagebox.showerror("Error al registrar", str(error), parent=self)
            return

        messagebox.showinfo(
            "Salida registrada",
            f"Salida de {self.huesped.nombres} {self.huesped.apellidos} confirmada.\n"
            f"Días de alojamiento: {dias}\n"
            f"Total a pagar: {dinero(total)}\n"
            f"Habitación {self.habitacion.numero}: Disponible.",
            parent=self,
        )
        self.principal.actualizar_estado()
        self.destroy()


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()
