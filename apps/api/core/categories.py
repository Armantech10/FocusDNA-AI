from typing import Dict, Any

DEFAULT_DOMAIN_CATEGORIES: Dict[str, str] = {
    "github.com": "productive",
    "gitlab.com": "productive",
    "stackoverflow.com": "productive",
    "docs.python.org": "productive",
    "developer.mozilla.org": "productive",
    "notion.so": "productive",
    "figma.com": "productive",
    "twitter.com": "social_media",
    "x.com": "social_media",
    "facebook.com": "social_media",
    "instagram.com": "social_media",
    "tiktok.com": "social_media",
    "reddit.com": "social_media",
    "youtube.com": "entertainment",
    "netflix.com": "entertainment",
    "twitch.tv": "entertainment",
}

DEFAULT_APP_CATEGORIES: Dict[str, str] = {
    "visual studio code": "productive",
    "code": "productive",
    "cursor": "productive",
    "terminal": "productive",
    "iterm": "productive",
    "pycharm": "productive",
    "xcode": "productive",
    "slack": "communication",
    "discord": "communication",
    "telegram": "communication",
    "whatsapp": "communication",
    "messages": "communication",
    "steam": "entertainment",
    "spotify": "entertainment",
}

class CategoryRegistry:
    def __init__(self):
        self.user_domain_categories: Dict[str, Dict[str, str]] = {}
        self.user_app_categories: Dict[str, Dict[str, str]] = {}

    def get_domain_category(self, user_id: str, domain: str) -> str:
        if not domain:
            return "neutral"
        clean_domain = domain.lower().strip()
        
        # Check custom user mapping first
        user_map = self.user_domain_categories.get(user_id, {})
        if clean_domain in user_map:
            return user_map[clean_domain]

        # Check subdomains / default dictionary
        for d, cat in DEFAULT_DOMAIN_CATEGORIES.items():
            if d in clean_domain:
                return cat

        return "neutral"

    def get_app_category(self, user_id: str, app_name: str) -> str:
        if not app_name:
            return "neutral"
        clean_app = app_name.lower().strip()

        user_map = self.user_app_categories.get(user_id, {})
        if clean_app in user_map:
            return user_map[clean_app]

        for a, cat in DEFAULT_APP_CATEGORIES.items():
            if a in clean_app:
                return cat

        return "neutral"

    def set_custom_category(self, user_id: str, item_name: str, category: str, is_domain: bool = True):
        clean_name = item_name.lower().strip()
        valid_categories = {"productive", "communication", "social_media", "entertainment", "neutral"}
        if category not in valid_categories:
            category = "neutral"

        if is_domain:
            if user_id not in self.user_domain_categories:
                self.user_domain_categories[user_id] = {}
            self.user_domain_categories[user_id][clean_name] = category
        else:
            if user_id not in self.user_app_categories:
                self.user_app_categories[user_id] = {}
            self.user_app_categories[user_id][clean_name] = category

category_registry = CategoryRegistry()
