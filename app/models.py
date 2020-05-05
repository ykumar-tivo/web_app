from app import db, declarative_base

class ReportTable(db.Model):
    __tablename__ = 'report_table'
    __bind_key__   = 'db'
    sk = db.Column(db.String(100), primary_key = True)
    sk_entity_type = db.Column(db.String(30))
    gid1 = db.Column(db.String(30))
    gid1_entity_type = db.Column(db.String(30))
    lsh_score1 = db.Column(db.Numeric(5, 4))
    gid2 = db.Column(db.String(30))
    gid2_entity_type = db.Column(db.String(30))
    lsh_score2 = db.Column(db.Numeric(5, 4))
    gid3 = db.Column(db.String(30))
    gid3_entity_type = db.Column(db.String(30))
    lsh_score3 = db.Column(db.Numeric(5, 4))
    gid4 = db.Column(db.String(30))
    gid4_entity_type = db.Column(db.String(30))
    lsh_score4 = db.Column(db.Numeric(5, 4))
    gid5 = db.Column(db.String(30))
    gid5_entity_type = db.Column(db.String(30))
    lsh_score5 = db.Column(db.Numeric(5, 4))
