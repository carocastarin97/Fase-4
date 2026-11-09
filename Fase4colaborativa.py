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
