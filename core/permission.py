from models.user import User
def has_permission(user: User, permissions: str) -> bool:
    if not user.permissions:
        return False
    return permissions in user.permissions.split(",")
