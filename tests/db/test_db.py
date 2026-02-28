from database.models import Parameters, DecisionLog

#tests that a parameter can be created and retreived by it's pk (name) 
def test_parameter_PK(db_session):
    p = Parameters(name="enemy1_health", value=5.0)
    db_session.add(p)
    db_session.commit()

    loaded = db_session.query(Parameters).filter_by(name="enemy1_health").first()
    assert loaded is not None
    assert loaded.value == 5.0

#tests the relationship between DecisionLog and Parameter
def test_decisionlog_relationship(db_session):
    p = Parameters(name="enemy1_damage", value=1.0)
    db_session.add(p)
    db_session.commit()

    d = DecisionLog(parameter_name="enemy1_damage", stage_id=1, change="+1", rationale="too weak")
    db_session.add(d)
    db_session.commit()

    loaded = db_session.query(DecisionLog).first()
    assert loaded is not None
    assert loaded.parameter.name == "enemy1_damage"
