#Importacion de la libreria de tkinter
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from abc import ABC, abstractmethod
from datetime import datetime

#Excepciones e identificador de errores
#Excepcion padre, Agrupa los errores por categorias
class SoftwareFJError(Exception):
#Valida que los datos ingresados cumplan con las condiciones
class ValidationError(SoftwareFJError):
    pass
#Para no duplicar los clientes en el sistema
class DuplicateCustomerError(SoftwareFJError):
    pass
#Validar si el cliente existe o no
class CustomerNotFoundError(SoftwareFJError):
    pass
#Evita reservar un servicio que no existe
class ServiceNotFoundError(SoftwareFJError):
    pass
#Evita reservar un servicio no disponible
class ServiceUnavailableError(SoftwareFJError):
    pass
#Errores en el proceso de la reserva
class ReservationError(SoftwareFJError):
    pass
#Realizar operaciones no permitidas
class InvalidStateError(ReservationError):
    pass
    
#Clase Padre
class Home (ABC):
    def __init__(self, home_id):
        #Verifica que el identador sea valido
        if not isinstance(home_id, str) or not home_id.strip():
            raise ValueError("The home ID cannot be empty.")
        #Guardamos la informacion
        self.__id = home_id.strip()

    #Permite acceder como un atributo normal
    @property
    def id(self):
        return self.__id

    #Las clases hijas ejecutan la accion   
    @abstractmethod
    def describe(self):
        pass
        
#Clase hija
#Clientes
class Customer(Home):
    def __init__(self, customer_id, full_name, email, phone):
        super().__init__(customer_id)
        self.__full_name = ""
        self.__email = ""
        self.__phone = ""
        self.full_name = full_name
        self.email = email
        self.phone = phone

    #Validar nombre del cte
    @property
    def full_name(self):
            return self.__full_name

    #Validacion de datos ingresados sea en texto 
    #Que no tenga espacios innecesarios
    @full_name.setter
    def full_name(self, value):
            if not isinstance(value, str) or len(value.strip()) < 3:
                raise ValidationError("Customer name must contain at least 3 characters.")
            #Almacena informacion
            self.__full_name = value.strip()

    #Validar conrreo electronico
    @property
    def email(self):
            return self.__email

    #Validar correo este correctamente escrito
    #Verificar que el correo cumpla con la estructura basica 
    @email.setter
    def email(self, value):
        if not isinstance(value, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value.strip()):
            raise ValidationError("Enter a valid email address.")
        #Almacena informacion
        self.__email = value.strip().lower()

    #Validar numero de telefono 
    @property
    def phone(self):
        return self.__phone

    #Estructura del numero de telefono
    #Numeros del 1 al 9 y maximo 10 caracteres
    @phone.setter
    def phone(self, value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{7,10}", value.strip()):
            raise ValidationError("Phone must contain 7–10 valid characters.")
        #Almacena informacion
        self.__phone = value.strip()

    #Contruye al cte
    def describe(self):
        return f"{self.id} - {self.full_name} ({self.email})"

    #Muestra la informacion del cte
    def __str__(self):
        return self.describe()

#Clase hija
#Servicios
class Service(Home):
    def __init__(self, service_id, name, base_price, available=True):
        super().__init__(service_id)
        #Validador del nombre
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Service name is required.")
        #Validador del precio
        if isinstance(base_price, bool) or not isinstance(base_price, (int, float)) or base_price < 0:
            raise ValidationError("Base price must be a non-negative number.")
        #Guarda la informacion
        self._name = name.strip()
        self._base_price = float(base_price)
        self._available = bool(available)

    #Valida nombre
    @property
    def name(self):
        return self._name

    #Valida el precio
    @property
    def base_price(self):
        return self._base_price
    
    #Valida la disponibilidad
    @property
    def available(self):
        return self._available

    #Actualiza la disponibilidad del servicio
    def set_availability(self, value):
        if not isinstance(value, bool):
            raise ValidationError("Availability must be True or False.")
        #Guarda la informcaion
        self._available = value

    #Calcula el precio segun el servicio seleccionado
    @abstractmethod
    def calculate_cost(self, *args, tax_rate=0.0, discount=0.0):
        pass

    #Calcula los parametros segun el servicio seleccionado
    @abstractmethod
    def validate_parameters(self, *args):
        pass

    #Organiza y construye la informacion
    @abstractmethod
    def describe(self):
        pass

    #Calcular el precio final
    def _final_price(self, subtotal, tax_rate, discount):

        #Valida los impuestos
        if not 0 <= tax_rate <= 1:
            raise ValidationError("Tax rate must be between 0 and 1.")
        
        #Valida los descuentos
        if not 0 <= discount <= 1:
            raise ValidationError("Discount must be between 0 and 1.")
        
        #Calcula el precio final
        total = subtotal * (1 - discount) * (1 + tax_rate)
        if total < 0:
            raise ValidationError("Calculated total cannot be negative.")
        #Redondear el resultado
        return round(total, 2)



