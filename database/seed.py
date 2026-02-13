from datetime import datetime, timedelta
import random

from database.main import SessionLocal, Telemetry, Parameters, DecisionLog

def seed():
    db = SessionLocal()

    try:
        params = [
            ("enemy_damage", 12.5),
            ("enemy_health", 100.0),
            ("player_speed", 6.2),
            ("spawn_rate", 1.4),
        ]
        
        # deleting child tables first to avoid errors during seeding
        db.query(DecisionLog).delete()
        db.query(Telemetry).delete()
        db.query(Parameters).delete()
        db.commit()


        for name, value in params:
            existing = db.query(Parameters).filter(Parameters.name == name).first()
            if existing:
                existing.value = value # type: ignore (safe to ignore as we checked for existence)
            else:
                db.add(Parameters(name=name, value=value))

        # Seed telemetry rows
        base_time = datetime.now() - timedelta(minutes=60)

        allowed_types = ["stage_start", "stage_end", "enemy_defeated", "damage_taken", "tower_spawn","tower_upgrade","money_spent"] 

        def generate_telemetry_data(telemetry_type):
            if telemetry_type == "stage_end":
                return {
                    "enemy_defeated": random.randint(1, 20),
                    "damage_taken": random.randint(1, 200),
                    "tower_spawn": random.randint(1, 200),
                    "tower_upgrade": random.randint(9, 20),
                    "money_spent": random.randint(3500, 10000)
                }

            if telemetry_type == "enemy_defeated":
                return {
                    "enemy_id": random.randint(1, 500),
                    "enemy_type": random.choice(["small", "medium", "big"]),
                    "enemy_health": random.randint(50, 500),
                }

            if telemetry_type == "tower_spawn":
                return {
                    "tower_type": random.choice(["square", "triangle", "star"]),
                    "tower_cost": random.randint(100, 800),
                    "xPos": random.randint(0, 15),
                    "yPos": random.randint(0, 15)
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
                    "amount": random.randint(1000, 10000)
                    
                }
                
            if telemetry_type == "damage_taken":
                return {
                    "amount": random.randint(1, 100)
                    
                }

            return {}
        
        for i in range(300):
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
