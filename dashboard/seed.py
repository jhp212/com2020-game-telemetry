from database.main import *
from database.constants import *
from database.models import *
from database.schemas import *
from datetime import datetime, timedelta
import random


def seed():
    db = SessionLocal()

    try:




        # Seed telemetry rows
        base_time = datetime.now() - timedelta(minutes=60)

        allowed_types = [
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

        def generate_telemetry_data(telemetry_type):
            if telemetry_type == "stage_end":
                return {
                    "enemy_defeated": random.randint(1, 50),
                    "damage_taken": random.randint(1, 2000),
                    "tower_spawn": random.randint(1, 200),
                    "tower_upgrade": random.randint(9, 20),
                    "money_spent": random.randint(3500, 10000)
                }

            if telemetry_type == "enemy_defeated":
                return {
                    "enemy_id": random.randint(1, 500),
                }

            if telemetry_type == "tower_spawn":
                return {
                    "tower_id": random.choice(["1", "2", "3"]),
                    
                }

            if telemetry_type == "tower_upgrade":
                return {
                    "tower_type": random.choice(["square", "triangle", "star"]),
                    "upgrade_level": random.randint(2, 5),
                    "upgrade_cost": random.randint(150, 600)
                }

            if telemetry_type == "stage_start":
                return {
                    "stage_difficulty": random.choice(["easy", "normal", "hard"]),
                    "starting_money": random.randint(1000, 3000)
                }
                
            if telemetry_type == "money_spent":
                return {
                    "amount": random.randint(-10, 100000)
                    
                }
                
            if telemetry_type == "damage_taken":
                return {
                    "amount": random.randint(1, 200)
                    
                }

            return {}
        
        for i in range(2000):
            telemetry_type = random.choice(allowed_types)
            t = Telemetry(
                user_id = random.randint(1, 10000),
                stage_id = random.randint(1, 5),
                telemetry_type = telemetry_type,
                dateTime = base_time + timedelta(seconds=i * 10),
                data= generate_telemetry_data(telemetry_type)
            )
            db.add(t)

        db.commit()
        
    
        

    finally:
        db.close()

if __name__ == "__main__":
    seed()
