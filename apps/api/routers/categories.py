from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.auth import get_current_user, AuthenticatedUser
from core.categories import category_registry, DEFAULT_DOMAIN_CATEGORIES, DEFAULT_APP_CATEGORIES

router = APIRouter(prefix="/api/categories", tags=["Domain & App Categories"])

class ConfigureCategoryRequest(BaseModel):
    item_name: str
    category: str # productive, communication, social_media, entertainment, neutral
    is_domain: bool = True

@router.get("")
def get_categories(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Retrieves default and custom domain/app category mappings.
    """
    user_domains = category_registry.user_domain_categories.get(user.user_id, {})
    user_apps = category_registry.user_app_categories.get(user.user_id, {})

    combined_domains = {**DEFAULT_DOMAIN_CATEGORIES, **user_domains}
    combined_apps = {**DEFAULT_APP_CATEGORIES, **user_apps}

    return {
        "user_id": user.user_id,
        "domain_categories": combined_domains,
        "app_categories": combined_apps,
        "custom_domain_overrides": user_domains,
        "custom_app_overrides": user_apps
    }

@router.post("")
def configure_category(
    data: ConfigureCategoryRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Configures domain or app category mapping for authenticated user.
    Prevents hardcoding good/bad websites universally.
    """
    category_registry.set_custom_category(
        user_id=user.user_id,
        item_name=data.item_name,
        category=data.category,
        is_domain=data.is_domain
    )

    return {
        "status": "configured",
        "item_name": data.item_name,
        "assigned_category": data.category,
        "is_domain": data.is_domain
    }
