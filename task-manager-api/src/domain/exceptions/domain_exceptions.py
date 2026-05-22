class DomainException(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class UserNotFoundError(DomainException):
    def __init__(self) -> None:
        super().__init__("Usuario no encontrado", "USER_NOT_FOUND")


class DuplicateEmailError(DomainException):
    def __init__(self) -> None:
        super().__init__("El correo electrónico ya está registrado", "DUPLICATE_EMAIL")


class InvalidCredentialsError(DomainException):
    def __init__(self) -> None:
        super().__init__("Correo electrónico o contraseña inválidos", "INVALID_CREDENTIALS")


class ProjectNotFoundError(DomainException):
    def __init__(self) -> None:
        super().__init__("Proyecto no encontrado", "PROJECT_NOT_FOUND")


class TaskNotFoundError(DomainException):
    def __init__(self) -> None:
        super().__init__("Tarea no encontrada", "TASK_NOT_FOUND")


class NotProjectOwnerError(DomainException):
    def __init__(self) -> None:
        super().__init__("Solo el propietario del proyecto puede realizar esta acción", "NOT_PROJECT_OWNER")


class NotProjectMemberError(DomainException):
    def __init__(self) -> None:
        super().__init__("El usuario no es miembro de este proyecto", "NOT_PROJECT_MEMBER")


class ArchivedProjectError(DomainException):
    def __init__(self) -> None:
        super().__init__("No se pueden modificar tareas en un proyecto archivado", "ARCHIVED_PROJECT")


class TaskAccessDeniedError(DomainException):
    def __init__(self) -> None:
        super().__init__("Solo puedes modificar tus propias tareas", "TASK_ACCESS_DENIED")


class InvalidAssignmentError(DomainException):
    def __init__(self) -> None:
        super().__init__("La tarea solo puede asignarse a un miembro del proyecto", "INVALID_ASSIGNMENT")


class CannotAssignTaskError(DomainException):
    def __init__(self) -> None:
        super().__init__("Solo el propietario puede asignar tareas a otros miembros", "CANNOT_ASSIGN_TASK")


class CannotRemoveOwnerError(DomainException):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar al propietario del proyecto", "CANNOT_REMOVE_OWNER")
