from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o colecionador possa modificar sua coleção.
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer solicitação
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissões de escrita são permitidas apenas para o colecionador
        return obj.colecionador == request.user