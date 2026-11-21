from enum import Enum


class TipoCargo(str, Enum):
    DIRECTIVO = "Directivo"
    ESTRATEGICO = "Estratégico"
    OPERATIVO = "Operativo"


class TipoGenero(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"


class Empleado:
    def __init__(self, nombre, apellidos, cargo, genero, salario_dia,
                 dias_trabajados, otros_ingresos, pagos_salud, aporte_pensiones):
        if not nombre.strip() or not apellidos.strip():
            raise ValueError("El nombre y los apellidos son obligatorios.")
        if not 1 <= dias_trabajados <= 31:
            raise ValueError("Los días trabajados deben estar entre 1 y 31.")
        if any(valor < 0 for valor in (
            salario_dia, otros_ingresos, pagos_salud, aporte_pensiones
        )):
            raise ValueError("Los valores monetarios no pueden ser negativos.")

        self.nombre = nombre
        self.apellidos = apellidos
        self.cargo = TipoCargo(cargo)
        self.genero = TipoGenero(genero)
        self.salario_dia = salario_dia
        self.dias_trabajados = dias_trabajados
        self.otros_ingresos = otros_ingresos
        self.pagos_salud = pagos_salud
        self.aporte_pensiones = aporte_pensiones

    def calcular_nomina(self):
        return (self.dias_trabajados * self.salario_dia
                + self.otros_ingresos - self.pagos_salud
                - self.aporte_pensiones)


class ListaEmpleados:
    def __init__(self):
        self.lista = []

    def agregar_empleado(self, empleado):
        self.lista.append(empleado)

    def calcular_total_nomina(self):
        return sum(e.calcular_nomina() for e in self.lista)

    def obtener_matriz(self):
        return [(e.nombre, e.apellidos, e.calcular_nomina())
                for e in self.lista]

    def convertir_texto(self):
        bloques = []
        for e in self.lista:
            bloques.append(
                f"Nombre: {e.nombre}\n"
                f"Apellidos: {e.apellidos}\n"
                f"Cargo: {e.cargo.value}\n"
                f"Género: {e.genero.value}\n"
                f"Salario por día: ${e.salario_dia:,.2f}\n"
                f"Días trabajados: {e.dias_trabajados}\n"
                f"Otros ingresos: ${e.otros_ingresos:,.2f}\n"
                f"Pagos por salud: ${e.pagos_salud:,.2f}\n"
                f"Aporte pensiones: ${e.aporte_pensiones:,.2f}\n"
                f"Salario mensual: ${e.calcular_nomina():,.2f}"
            )
        bloques.append(f"TOTAL NÓMINA: ${self.calcular_total_nomina():,.2f}")
        return "\n\n".join(bloques)


if __name__ == "__main__":
    empleados = ListaEmpleados()
    empleado1 = Empleado(
        "Ana", "Gómez", TipoCargo.OPERATIVO, TipoGenero.FEMENINO,
        100000, 20, 200000, 80000, 80000
    )
    empleados.agregar_empleado(empleado1)
    print(empleados.convertir_texto())
