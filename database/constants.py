ALLOWED_TELEMETRY_TYPES = [
    "stage_start",
    "stage_end",
    "stage_fail",
    "stage_quit",
    "enemy_defeated",
    "damage_taken",
    "tower_spawn",
    "tower_upgrade",
    "money_spent",
    "boss_start",
    "boss_fail",
    "boss_defeated",
]

DEFAULT_PARAMETERS = [
    {"name": "enemy_damage_multiplier", "value": 1.0},
    {"name": "enemy_speed_multiplier", "value": 1.0},
    {"name": "money_earned_multiplier", "value": 1.0},
    {"name": "easy_health_multiplier", "value": 1.0},
    {"name": "medium_health_multiplier", "value": 1.0},
    {"name": "hard_health_multiplier", "value": 1.0},
    {"name": "triangle_radius_multiplier", "value": 1.0},
    {"name": "star_radius_multiplier", "value": 1.0},
]

DEFAULT_USERS = [
    {"username": "testadmin", "password": "Adminpass1!", "is_admin": 1},
    {"username": "testplayer", "password": "Playerpass1!", "is_admin": 0}
]