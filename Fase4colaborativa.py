#Importacion de la libreria de tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from pathlib import Path

#Excepciones e identificador de errores
#Excepcion padre, Agrupa los errores por categorias
class SoftwareFJError(Exception):
    """Base exception for application errors."""
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

#Subclase 
#Alquiler de salas
class RoomService(Service):
    def __init__(self, service_id, name, hourly_rate, capacity):
        super().__init__(service_id, name, hourly_rate)
        self.capacity = capacity

    #Parametro del servicio
    #Horas contratadas y cantidad de asistentes
    def validate_parameters(self, hours, attendees=1):

        #Valida la cantidad de horas contratadas sean mayor a 0
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or hours <= 0:
            raise ValidationError("Hours must be greater than zero.")

        #Valida la cantidad de asistentes sea mayor o igual a 1
        if isinstance(attendees, bool) or not isinstance(attendees, int) or attendees < 1:
            raise ValidationError("Attendees must be a positive integer.")

        #Valida que los asistentes no superen la capacidad de la sala
        if attendees > self.capacity:
            raise ValidationError(f"Room capacity exceeded (maximum {self.capacity}).")

    #Calcula el costo
    def calculate_cost(self, *args, tax_rate=0.0, discount=0.0):

        #Valida cantidad de horas y asistentes
        if len(args) not in (1, 2):
            raise ValidationError("Room cost expects hours and optional attendees.")
        hours = args[0]
        attendees = args[1] if len(args) == 2 else 1
        self.validate_parameters(hours, attendees)
        return self._final_price(self.base_price * hours, tax_rate, discount)

    def describe(self):
        return f"Room: {self.name} | {self.base_price:.2f}/hour | capacity: {self.capacity}"

#Subclase
#Alquiler de equipos
class EquipmentService(Service):
    def __init__(self, service_id, name, daily_rate, quantity_available):
        super().__init__(service_id, name, daily_rate)
        if not isinstance(quantity_available, int) or quantity_available < 1:
            raise ValidationError("Equipment quantity must be a positive integer.")
        self.quantity_available = quantity_available

    #Parametro del servicio
    #Dias contratados y cantidad de asistentes
    def validate_parameters(self, days, quantity=1):
        if isinstance(days, bool) or not isinstance(days, int) or days < 1:
            raise ValidationError("Days must be a positive integer.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValidationError("Quantity must be a positive integer.")
        if quantity > self.quantity_available:
            raise ValidationError("Requested equipment quantity is unavailable.")

    #Calcula el costo
    def calculate_cost(self, *args, tax_rate=0.0, discount=0.0):
        if len(args) not in (1, 2):
            raise ValidationError("Equipment cost expects days and optional quantity.")
        days = args[0]
        quantity = args[1] if len(args) == 2 else 1
        self.validate_parameters(days, quantity)
        return self._final_price(self.base_price * days * quantity, tax_rate, discount)

    def describe(self):
        return f"Equipment: {self.name} | {self.base_price:.2f}/day | available: {self.quantity_available}"

#Subclase
#Servicios de consultoria
class ConsultingService(Service):
    def __init__(self, service_id, name, hourly_rate, specialist):
        super().__init__(service_id, name, hourly_rate)
        if not isinstance(specialist, str) or not specialist.strip():
            raise ValidationError("A specialist name is required.")
        self.specialist = specialist.strip()

    #Parametro del servicio
    #Horas contratados 
    def validate_parameters(self, hours, remote=False):
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or hours <= 0:
            raise ValidationError("Consulting hours must be greater than zero.")
        if not isinstance(remote, bool):
            raise ValidationError("Remote must be True or False.")

    #Calcula el costo
    def calculate_cost(self, *args, tax_rate=0.0, discount=0.0):
        if len(args) not in (1, 2):
            raise ValidationError("Consulting cost expects hours and optional remote flag.")
        hours = args[0]
        remote = args[1] if len(args) == 2 else False
        self.validate_parameters(hours, remote)
        subtotal = self.base_price * hours
        if remote:
            subtotal *= 0.95
        return self._final_price(subtotal, tax_rate, discount)

    def describe(self):
        return f"Consulting: {self.name} | {self.base_price:.2f}/hour | specialist: {self.specialist}"

#Clase hija
#Reservaciones
class Reservation(Home):
    #Estado de la reservacion
    VALID_STATES = {"PENDING", "CONFIRMED", "CANCELLED"}

    def __init__(self, reservation_id, customer, service, duration, parameters=()):
        super().__init__(reservation_id)
        #Validar la existencia del cliente
        if not isinstance(customer, Customer):
            raise ReservationError("A valid customer object is required.")
        #Validar el servicio seleccionado
        if not isinstance(service, Service):
            raise ReservationError("A valid service object is required.")
        #Validar los parametros, por hora, dias y asistentes
        if not isinstance(parameters, (tuple, list)):
            raise ReservationError("Service parameters must be a list or tuple.")
        #Validar la duracion de la reserva
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration <= 0:
            raise ReservationError("Duration must be greater than zero.")
        self.customer = customer
        self.service = service
        self.duration = duration
        self.parameters = tuple(parameters)
        self._state = "PENDING"
        self.created_at = datetime.now()
        self.total = None

    #consultar estado de la reserva
    @property
    def state(self):
        return self._state

    #Confirmacion de la reserva
    def confirm(self, tax_rate=0.0, discount=0.0):
        #Validar estado de la reserva y evitar dobles confirmaciones
        if self._state != "PENDING":
            raise InvalidStateError("Only pending reservations can be confirmed.")
        #Validar la disponibilidad del servicio
        if not self.service.available:
            raise ServiceUnavailableError("The selected service is currently unavailable.")
        #calculo del costo
        try:
            self.total = self.service.calculate_cost(
                *self.parameters, tax_rate=tax_rate, discount=discount)

        #Si ocurre un error se ejecutara la excepcion
        #Se guardara en logs
        except Exception as error:
            logger.exception("Reservation cost calculation failed: %s", self.id)
            raise ReservationError("Reservation could not be confirmed due to a cost error.") from error

        #Cambia el estado de la reserva 
        #Registrar en el log la reservacion      
        else:
            self._state = "CONFIRMED"
            logger.info("Reservation %s confirmed. Total: %.2f", self.id, self.total)
            return self.total
        #Registra la confimacion final
        finally:
            logger.info("Confirmation attempt finished for reservation %s", self.id)

    #cancelacion de reserva
    def cancel(self):
        #Validar si ya esta cancelada
        if self._state == "CANCELLED":
            raise InvalidStateError("Reservation is already cancelled.")
        self._state = "CANCELLED"
        logger.info("Reservation %s cancelled.", self.id)

    def describe(self):
        return f"{self.id} | {self.customer.full_name} | {self.service.name} | {self.state} | {self.total}"

    def __str__(self):
        return self.describe()


LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name="SoftwareFJ"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        file_handler = logging.FileHandler(LOG_DIR / "software_fj.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

logger = get_logger()

#clase Administradora
#Guardar informacion
class ManagementSystem:
    def __init__(self):
        self._customers = []
        self._services = []
        self._reservations = []
        self._load_default_services()

    #consultar clientes
    @property
    def customers(self):
        return tuple(self._customers)

    #consultar servicio
    @property
    def services(self):
        return tuple(self._services)

    #consultar reservacion
    @property
    def reservations(self):
        return tuple(self._reservations)

    #Habilitar servicios
    def _load_default_services(self):
        self._services.extend([
            RoomService("S001", "Conference Room", 50000, 20),
            EquipmentService("S002", "Projector", 35000, 10),
            ConsultingService("S003", "Software Consulting", 80000, "Senior Consultant")])

    #Registrar cte
    def add_customer(self, customer_id, full_name, email, phone):
        #Verificar exitencia del cte
        try:
            if any(c.id == customer_id.strip() for c in self._customers):
                raise DuplicateCustomerError("Customer ID already exists.")
            customer = Customer(customer_id, full_name, email, phone)
            self._customers.append(customer)
        #Guarada los errores
        #Datos o atribuos incorrectos
        except (AttributeError, TypeError) as error:
            logger.exception("Invalid or missing customer parameters.")
            raise ValidationError("Customer information is incomplete or invalid.") from error
        except Exception:
            logger.exception("Customer registration failed.")
            raise
        #Registro del cte
        else:
            logger.info("Customer registered: %s", customer.id)
            return customer
        finally:
            logger.info("Customer registration operation completed.")

    #Buscar cte
    def get_customer(self, customer_id):
        for customer in self._customers:
            if customer.id == customer_id:
                return customer
        #si el cte no existe ejecuta el error
        raise CustomerNotFoundError(f"Customer '{customer_id}' was not found.")

    #Eliminar un cte
    def remove_customer(self, customer_id):
        customer = self.get_customer(customer_id)
        #Validar que el cte tenga reservas confirmadas
        if any(r.customer.id == customer_id and r.state == "CONFIRMED" for r in self._reservations):
            #Genera error si el cte cuenta con reserva confirmada
            raise ReservationError("Cannot remove a customer with confirmed reservations.")
        #Si no tiene reserva confirmada lo elimina de la lista y guara la informacion
        self._customers.remove(customer)
        logger.info("Customer removed: %s", customer_id)

    #Buscar un servicio
    def get_service(self, service_id):
        for service in self._services:
            if service.id == service_id:
                return service
        raise ServiceNotFoundError(f"Service '{service_id}' was not found.")

    #Crear reservaciones
    def add_reservation(self, reservation_id, customer_id, service_id, duration, *parameters):
        #evitar duplicacion de la reserva con mismo ID
        if any(r.id == reservation_id for r in self._reservations):
            raise ReservationError("Reservation ID already exists.")
        #buscar el cte
        customer = self.get_customer(customer_id)
        #buscar el servicio
        service = self.get_service(service_id)
        #crear la reserva
        reservation = Reservation(reservation_id, customer, service, duration, parameters)
        #guardar la reserva
        self._reservations.append(reservation)
        #registar la informacion 
        logger.info("Reservation created: %s", reservation_id)
        return reservation

    #Buscar reserva
    def find_reservation(self, reservation_id):
        for reservation in self._reservations:
            if reservation.id == reservation_id:
                return reservation
        raise ReservationError(f"Reservation '{reservation_id}' was not found.")

    #Cancelar reserva
    def cancel_reservation(self, reservation_id):
        self.find_reservation(reservation_id).cancel()

    #Historico de informacion
    def summary(self):
        return {
            #Muestra la cantidad de ctes, servicios, reservaciones hay
            #muestra la cantidad de reservas confirmadad
            "customers": len(self._customers),
            "services": len(self._services),
            "reservations": len(self._reservations),
            "confirmed": sum(r.state == "CONFIRMED" for r in self._reservations)}

#Interface
class SoftwareFJApp:
    def __init__(self, root):
        self.root = root
        #self.root.configure(bg="#EBA1EB")
        self.root.title("Software FJ - Management System")
        self.root.geometry("1000x650")
        self.root.minsize(850, 550)
        self.system = ManagementSystem()
        self._build_ui()
        self.refresh_all()

    #Estilo 
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    # Fondo general de las pestañas
        style.configure("TNotebook", background="#FBF9FC",borderwidth=0)

    # Fondo del contenido de las pestañas
        style.configure("TFrame",background="#FBF9FC")
        style.configure("TLabelframe",background="#FBF9FC")
        style.configure("TLabelframe.Label",background="#FBF9FC",foreground="#3F0344",
            font=("Times New Roman", 14, "bold"))
        style.configure("TLabel",background="#FBF9FC",foreground="#3F0344",
            font=("Times New Roman", 11, "bold"))

    # Pestañas normales
        style.configure("TNotebook.Tab",background="#770381",foreground="#FFFFFF",
        font=("Times New Roman", 12, "bold"),padding=(20, 10),borderwidth=0)

    # Pestaña seleccionada y efecto al pasar el mouse
        style.map( "TNotebook.Tab",background=[("selected", "#AB0DB9"),
        ("active", "#E97B15")],foreground=[("selected", "#FFFFFF"),
        ("active", "#FFFFFF")])

    #Botones
        style.configure("AddCustomer.TButton",background="#3F0344",foreground="#FFFFFF",
            font=("Times New Roman", 11, "bold"),padding=(15, 8),borderwidth=0)
        style.map("AddCustomer.TButton",background=[("active", "#E97B15"),
            ("pressed", "#AB0DB9")],foreground=[("active", "#FFFFFF"),("pressed", "#FFFFFF")])
        style.configure("DeleteCustomer.TButton",background="#3F0344",foreground="#FFFFFF",
            font=("Times New Roman", 11, "bold"),padding=(15, 8),borderwidth=0)
        style.map("DeleteCustomer.TButton",background=[("active", "#E97B15"),
            ("pressed", "#3F0344")],foreground=[("active", "#FFFFFF"),("pressed", "#FFFFFF")])
        style.configure("Create.TButton",background="#3F0344",foreground="#FFFFFF",
            font=("Times New Roman", 11, "bold"),padding=(15, 8),borderwidth=0)
        style.map("Create.TButton",background=[("active", "#E97B15"),
            ("pressed", "#AB0DB9")],foreground=[("active", "#FFFFFF"),("pressed", "#FFFFFF")])
        style.configure("Confirm.TButton",background="#3F0344",foreground="#FFFFFF",
            font=("Times New Roman", 11, "bold"),padding=(15, 8),borderwidth=0)
        style.map("Confirm.TButton",background=[("active", "#E97B15"),
            ("pressed", "#AB0DB9")],foreground=[("active", "#FFFFFF")])
        style.configure("Cancel.TButton",background="#3F0344",foreground="#FFFFFF",
            font=("Times New Roman", 11, "bold"),padding=(15, 8),borderwidth=0)
        style.map("Cancel.TButton",background=[("active", "#E97B15"),
            ("pressed", "#AB0DB9")],foreground=[("active", "#FFFFFF")])


    #titulo
    def _build_ui(self):
        header = tk.Frame(self.root, bg="#3F0344", height=85)
        header.pack(fill="x")
        tk.Label(header, text="Software FJ", font=("Times New Roman", 22, "bold"),
                 fg="white", bg="#3F0344").pack(anchor="center", padx=22, pady=(13, 0))
        tk.Label(header, text="Management System", font=("Times New Roman", 12,"italic"),
                 fg="#DCE6F2", bg="#3F0344").pack(anchor="center", padx=24)

        #Creacion de pestañas y contenido
        self.configure_styles()
        tabs = ttk.Notebook(self.root)
        tabs.pack(fill="both", expand=True, padx=15, pady=15)
        self.customer_tab = ttk.Frame(tabs, padding=12)
        self.reservation_tab = ttk.Frame(tabs, padding=12)
        self.service_tab = ttk.Frame(tabs, padding=12)
        tabs.add(self.customer_tab, text="Customers")
        tabs.add(self.service_tab, text="Services")
        tabs.add(self.reservation_tab, text="Reservations")
        self._build_customers()
        self._build_services()
        self._build_reservations()

    #Pestaña clientes
    def _build_customers(self):
        form = ttk.LabelFrame(self.customer_tab, text="Register customer", padding=10)
        form.pack(fill="x")
       
        self.customer_fields = {}
        labels = [("Customer ID", "id"), ("Full name", "name"),
                  ("Email", "email"), ("Phone", "phone")]
        for col, (label, key) in enumerate(labels):
            ttk.Label(form,text=label,foreground="#3F0344",font=("Times New Roman", 11, "bold")
                ).grid(row=0, column=col, sticky="w", padx=5)
            entry = ttk.Entry(form, width=23)
            entry.grid(row=1, column=col, padx=5, pady=5, sticky="ew")
            self.customer_fields[key] = entry

        #Boton crear cte
        ttk.Button(form,text="Add customer",command=self.add_customer,style="AddCustomer.TButton"
            ).grid(row=1, column=4, padx=8, pady=5)
        #Tabla visualizar ctes registrados
        self.customer_tree = self._make_tree(self.customer_tab, ("id", "name", "email", "phone"),
                                             ("Customer ID", "Full name", "Email", "Phone"))
        #Boton eliminar cte
        ttk.Button(self.customer_tab,text="Delete selected customer",command=self.delete_customer,
            style="DeleteCustomer.TButton").pack(anchor="e", pady=8)

    #Tabla servicios disponibles
    def _build_services(self):
        self.service_tree = self._make_tree(self.service_tab, ("id", "name", "description"),
                                            ("Service ID", "Service name", "Description"))
        ttk.Label(self.service_tab, text="Default services are loaded in memory when the application starts.",
                  foreground="#555").pack(anchor="w", pady=8)

    #Registrar reserva
    def _build_reservations(self):
        form = ttk.LabelFrame(self.reservation_tab, text="Create reservation", padding=10)
        form.pack(fill="x")
        self.res_fields = {}
        fields = [("Reservation ID", "id"), ("Customer ID", "customer"),
                  ("Service ID", "service"), ("Duration", "duration"),
                  ("Extra parameter", "extra")]
        for col, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=col, sticky="w", padx=4)
            entry = ttk.Entry(form, width=18)
            entry.grid(row=1, column=col, padx=4, pady=5)
            self.res_fields[key] = entry

        #Boton crear reserva
        ttk.Button(form,text="Create",command=self.add_reservation,style="Create.TButton"
            ).grid(row=1, column=5, padx=8, pady=5, sticky="w")
        actions = ttk.Frame(self.reservation_tab)
        actions.pack(fill="x", pady=8)
        #Boton confirmar reserva
        ttk.Button(actions,text="Confirm selected",command=self.confirm_reservation,style="Confirm.TButton"
            ).pack(side="left", padx=4)
        # Botón cancelar reserva
        ttk.Button(actions,text="Cancel selected",command=self.cancel_reservation,style="Cancel.TButton"
            ).pack(side="left", padx=4)
        #Tabla de reservas
        self.res_tree = self._make_tree(self.reservation_tab,
            ("id", "customer", "service", "duration", "state", "total"),
            ("Reservation ID", "Customer", "Service", "Duration", "State", "Total"))

    #Tabla
    def _make_tree(self, parent, columns, headings):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=12)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=13)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=140, anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    #control y captura de errores
    def _safe_action(self, action):
        try:
            action()
        except SoftwareFJError as error:
            logger.exception("Application operation rejected.")
            messagebox.showerror("Operation error", str(error))
        except (ValueError, TypeError, IndexError) as error:
            logger.exception("Invalid input.")
            messagebox.showerror("Invalid input", str(error))
        except Exception as error:
            logger.exception("Unexpected application error.")
            messagebox.showerror("Unexpected error", "The operation failed. The application is still running.")
        finally:
            self.refresh_all()

    #Registro de ctes
    def add_customer(self):
        def action():
            f = self.customer_fields
            self.system.add_customer(f["id"].get(), f["name"].get(), f["email"].get(), f["phone"].get())
            for entry in f.values(): entry.delete(0, "end")
            messagebox.showinfo("Success", "Customer registered successfully.")
        self._safe_action(action)

    #Eliminar ctes
    def delete_customer(self):
        def action():
            selected = self.customer_tree.selection()
            if not selected: raise ValueError("Select a customer first.")
            customer_id = self.customer_tree.item(selected[0], "values")[0]
            self.system.remove_customer(customer_id)
            messagebox.showinfo("Success", "Customer deleted.")
        self._safe_action(action)

    #Registro de reservas
    def add_reservation(self):
        def action():
            f = self.res_fields
            rid, cid, sid = f["id"].get(), f["customer"].get(), f["service"].get()
            duration = float(f["duration"].get())
            service = self.system.get_service(sid)
            extra_text = f["extra"].get().strip()
            if service.__class__.__name__ == "RoomService":
                params = (int(extra_text or "1"),)
            elif service.__class__.__name__ == "EquipmentService":
                params = (int(extra_text or "1"),)
            else:
                params = (extra_text.lower() in ("yes", "true", "1"),)
            reservation = self.system.add_reservation(rid, cid, sid, duration, *params)
            messagebox.showinfo("Success", f"Reservation {reservation.id} created as PENDING.")
            for entry in f.values(): entry.delete(0, "end")
        self._safe_action(action)

    #Confirmar reserva
    def confirm_reservation(self):
        def action():
            selected = self.res_tree.selection()
            if not selected: raise ValueError("Select a reservation first.")
            rid = self.res_tree.item(selected[0], "values")[0]
            total = self.system.find_reservation(rid).confirm(tax_rate=0.19)
            messagebox.showinfo("Confirmed", f"Reservation confirmed. Total: ${total:,.2f}")
        self._safe_action(action)

    #Cancelar reserva
    def cancel_reservation(self):
        def action():
            selected = self.res_tree.selection()
            if not selected: raise ValueError("Select a reservation first.")
            rid = self.res_tree.item(selected[0], "values")[0]
            self.system.cancel_reservation(rid)
            messagebox.showinfo("Cancelled", "Reservation cancelled.")
        self._safe_action(action)

    #Actualizar inforacion 
    def refresh_all(self):
        if not hasattr(self, "customer_tree"): return
        for tree in (self.customer_tree, self.service_tree, self.res_tree):
            for item in tree.get_children(): tree.delete(item)
        for c in self.system.customers:
            self.customer_tree.insert("", "end", values=(c.id, c.full_name, c.email, c.phone))
        for s in self.system.services:
            self.service_tree.insert("", "end", values=(s.id, s.name, s.describe()))
        for r in self.system.reservations:
            self.res_tree.insert("", "end", values=(r.id, r.customer.full_name, r.service.name,
                        r.duration, r.state, r.total if r.total is not None else "-"))

def main():
    try:
        root = tk.Tk()
        SoftwareFJApp(root)
        logger.info("Software FJ application started.")
        root.mainloop()
    except Exception:
        logger.exception("Fatal startup error.")
        raise
    finally:
        logger.info("Software FJ application closed.")

if __name__ == "__main__":
    main()

   
