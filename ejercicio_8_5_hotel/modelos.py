"""Ejercicio 8.5 - Gestión de contenidos: hotel.

Adaptación a Python del ejercicio de Leonardo Bermón Angarita.
Contiene solamente las clases del modelo; la GUI se hará con Tkinter.
"""

from datetime import date


class Huesped:
    """Datos de la persona alojada y duración de su estancia."""

    def __init__(self, nombres, apellidos, documento_identidad, fecha_ingreso):
        nombres = str(nombres).strip()
        apellidos = str(apellidos).strip()
        documento_identidad = str(documento_identidad).strip()

        if not nombres or not apellidos or not documento_identidad:
            raise ValueError("Nombre, apellidos y documento son obligatorios.")
        if not documento_identidad.isdigit():
            raise ValueError("El documento de identidad debe contener solo números.")
        if not isinstance(fecha_ingreso, date):
            raise ValueError("La fecha de ingreso debe ser una fecha válida.")

        self.nombres = nombres
        self.apellidos = apellidos
        self.documento_identidad = documento_identidad
        self.fecha_ingreso = fecha_ingreso
        self.fecha_salida = None

    def obtener_dias_alojamiento(self):
        """Retorna días transcurridos; la salida debe ser posterior al ingreso."""
        if self.fecha_salida is None:
            raise ValueError("Primero debes indicar la fecha de salida.")
        if not isinstance(self.fecha_salida, date):
            raise ValueError("La fecha de salida debe ser una fecha válida.")
        if self.fecha_salida <= self.fecha_ingreso:
            raise ValueError("La fecha de salida debe ser posterior a la de ingreso.")
        return (self.fecha_salida - self.fecha_ingreso).days


class Habitacion:
    """Habitación individual, con tarifa diaria y ocupación."""

    def __init__(self, numero, precio_dia):
        if not isinstance(numero, int) or not 1 <= numero <= 10:
            raise ValueError("El número de habitación debe estar entre 1 y 10.")
        if precio_dia <= 0:
            raise ValueError("El precio diario debe ser mayor que cero.")

        self.numero = numero
        self.precio_dia = precio_dia
        self.disponible = True
        self.huesped = None

    def asignar_huesped(self, huesped):
        """Ocupa la habitación únicamente cuando está disponible."""
        if not self.disponible:
            raise ValueError(f"La habitación {self.numero} ya está ocupada.")
        if not isinstance(huesped, Huesped):
            raise ValueError("Debes proporcionar un huésped válido.")
        self.huesped = huesped
        self.disponible = False

    def liberar(self):
        """Deja la habitación disponible después de registrar la salida."""
        if self.disponible:
            raise ValueError(f"La habitación {self.numero} ya está disponible.")
        self.huesped = None
        self.disponible = True


class Hotel:
    """Hotel con diez habitaciones y dos tarifas fijas."""

    def __init__(self):
        self.habitaciones = [
            Habitacion(numero, 120000 if numero <= 5 else 160000)
            for numero in range(1, 11)
        ]

    def buscar_habitacion(self, numero):
        """Busca por número o informa si este está fuera del rango."""
        if not isinstance(numero, int) or not 1 <= numero <= 10:
            raise ValueError("El número de habitación debe estar entre 1 y 10.")
        return self.habitaciones[numero - 1]

    def buscar_fecha_ingreso(self, numero):
        """Retorna la fecha de ingreso, o None si está desocupada."""
        habitacion = self.buscar_habitacion(numero)
        if habitacion.huesped is None:
            return None
        return habitacion.huesped.fecha_ingreso

    def esta_ocupada(self, numero):
        """Indica si una habitación se encuentra ocupada."""
        return not self.buscar_habitacion(numero).disponible


if __name__ == "__main__":
    print("=== HOTEL: EJERCICIO 8.5 ===")
    hotel = Hotel()

    print("\nESTADO INICIAL DE LAS HABITACIONES:")
    for habitacion in hotel.habitaciones:
        estado = "Disponible" if habitacion.disponible else "No disponible"
        print(f"Habitación {habitacion.numero:2d}: {estado:13s} "
              f"| Tarifa diaria: ${habitacion.precio_dia:,.0f}")

    print("\nREGISTRO DE INGRESO:")
    habitacion = hotel.buscar_habitacion(3)
    ana = Huesped("Ana", "Gómez", "123456789", date(2026, 11, 20))
    habitacion.asignar_huesped(ana)
    print(f"Huésped: {ana.nombres} {ana.apellidos}")
    print(f"Habitación: {habitacion.numero}")
    print(f"Fecha de ingreso: {hotel.buscar_fecha_ingreso(3)}")
    print(f"Estado: {'No disponible' if hotel.esta_ocupada(3) else 'Disponible'}")

    print("\nPRUEBA DE HABITACIÓN OCUPADA:")
    try:
        habitacion.asignar_huesped(
            Huesped("Luis", "Pérez", "987654321", date(2026, 11, 21))
        )
    except ValueError as error:
        print(f"Validación correcta: {error}")

    print("\nCÁLCULO Y REGISTRO DE SALIDA:")
    ana.fecha_salida = date(2026, 11, 23)
    dias = ana.obtener_dias_alojamiento()
    total = dias * habitacion.precio_dia
    print(f"Fecha de salida: {ana.fecha_salida}")
    print(f"Días de alojamiento: {dias}")
    print(f"Total a pagar: ${total:,.0f}")
    habitacion.liberar()
    print(f"Estado final habitación 3: "
          f"{'No disponible' if hotel.esta_ocupada(3) else 'Disponible'}")
