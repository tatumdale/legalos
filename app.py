#!/usr/bin/env python3
"""AD Legal OS -- Flask Application, port 5050"""
import os
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, g, render_template, request, redirect, url_for, jsonify, flash, send_file
import csv
import io
import sys
sys.path.insert(0, str(Path(__file__).parent))
from drive_helpers import get_matter_documents, get_or_create_matter_folder

BASE_DIR = Path.home() / '.openclaw' / 'workspace-ad-shared'
DB_PATH  = BASE_DIR / 'db' / 'ad_matters.db'
FIRM_CONFIG = BASE_DIR / 'firm_config.json'
BASE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.urandom(32)

# =============================================================================
# BRIEFING INTERVIEW — Question Templates
# =============================================================================

CORE_BRIEFING_QUESTIONS = [
    {'id': 'jurisdiction', 'label': 'Jurisdiction', 'type': 'select', 'required': True,
     'options': ['England and Wales', 'Scotland', 'Northern Ireland', 'Other'],
     'default': 'England and Wales'},
    {'id': 'client_type', 'label': 'Client Type', 'type': 'select', 'required': True,
     'options': ['Startup', 'SME', 'Large Corporate', 'Individual', 'Public Sector']},
    {'id': 'counterparty', 'label': 'Counterparty', 'type': 'text', 'required': False,
     'placeholder': 'Name of counterparty (if known)'},
    {'id': 'deal_value_band', 'label': 'Deal Value Band', 'type': 'select', 'required': True,
     'options': ['Under £10K', '£10K–£100K', '£100K–£1M', 'Over £1M', 'Undisclosed']},
    {'id': 'deadline', 'label': 'Deadline', 'type': 'date', 'required': False},
    {'id': 'risk_appetite', 'label': 'Risk Appetite', 'type': 'radio', 'required': True,
     'options': ['Conservative', 'Balanced', 'Commercial']},
]

CONDITIONAL_QUESTIONS = {
    'Contract Review': [
        {'id': 'contract_type', 'label': 'Contract Type', 'type': 'select', 'required': True,
         'options': ['Service Agreement', 'Supply Agreement', 'Licence', 'Lease', 'NDA', 'Other']},
        {'id': 'contract_duration', 'label': 'Contract Duration', 'type': 'text', 'required': False,
         'placeholder': 'e.g. 12 months, indefinite'},
        {'id': 'known_problem_areas', 'label': 'Known Problem Areas', 'type': 'textarea', 'required': False,
         'placeholder': 'Any specific clauses or issues you want reviewed'},
        {'id': 'negotiation_expected', 'label': 'Negotiation Expected?', 'type': 'radio', 'required': True,
         'options': ['Yes', 'No', 'Possibly']},
    ],
    'Company Formation': [
        {'id': 'structure', 'label': 'Company Structure', 'type': 'select', 'required': True,
         'options': ['Private Limited (Ltd)', 'LLP', 'PLC', 'CIC', 'Other']},
        {'id': 'incorporation_jurisdiction', 'label': 'Incorporation Jurisdiction', 'type': 'select', 'required': True,
         'options': ['England and Wales', 'Scotland', 'Northern Ireland', 'Other']},
        {'id': 'num_directors', 'label': 'Number of Directors', 'type': 'number', 'required': True,
         'placeholder': 'e.g. 2'},
        {'id': 'num_shareholders', 'label': 'Number of Shareholders', 'type': 'number', 'required': True,
         'placeholder': 'e.g. 2'},
        {'id': 'specific_requirements', 'label': 'Specific Requirements', 'type': 'textarea', 'required': False,
         'placeholder': 'Articles amendments, shareholder agreements, etc.'},
    ],
    'Employment': [
        {'id': 'employee_level', 'label': 'Employee Level', 'type': 'select', 'required': True,
         'options': ['Junior', 'Mid-level', 'Senior', 'Director / C-suite']},
        {'id': 'equity_incentives', 'label': 'Equity / Incentive Schemes?', 'type': 'radio', 'required': True,
         'options': ['Yes', 'No', 'Under consideration']},
        {'id': 'restrictive_covenants_scope', 'label': 'Restrictive Covenants Scope', 'type': 'textarea', 'required': False,
         'placeholder': 'Non-compete, non-solicit, gardening leave details'},
    ],
    'M&A': [
        {'id': 'deal_type', 'label': 'Deal Type', 'type': 'select', 'required': True,
         'options': ['Share Purchase', 'Asset Purchase', 'Merger', 'Management Buyout', 'Other']},
        {'id': 'deal_stage', 'label': 'Deal Stage', 'type': 'select', 'required': True,
         'options': ['Pre-LOI', 'LOI Signed', 'Due Diligence', 'Negotiation', 'Completion']},
        {'id': 'target_jurisdiction', 'label': 'Target Jurisdiction', 'type': 'select', 'required': True,
         'options': ['England and Wales', 'Scotland', 'Northern Ireland', 'EU', 'International']},
    ],
}

def get_briefing_questions(matter_type):
    questions = list(CORE_BRIEFING_QUESTIONS)
    conditional = CONDITIONAL_QUESTIONS.get(matter_type, [])
    questions.extend(conditional)
    return questions

def format_briefing_summary(briefing_json):
    if not briefing_json:
        return ''
    try:
        answers = json.loads(briefing_json) if isinstance(briefing_json, str) else briefing_json
    except (json.JSONDecodeError, TypeError):
        return ''
    lines = ['## Briefing Summary\n']
    label_map = {}
    for q in CORE_BRIEFING_QUESTIONS:
        label_map[q['id']] = q['label']
    for qlist in CONDITIONAL_QUESTIONS.values():
        for q in qlist:
            label_map[q['id']] = q['label']
    for key, value in answers.items():
        if value:
            label = label_map.get(key, key.replace('_', ' ').title())
            lines.append(f'**{label}:** {value}')
    return '\n'.join(lines)


def init_briefing_schema(db):
    for col, typedef in [('briefing', 'TEXT'),
                         ('briefing_status', "TEXT DEFAULT 'not_required'"),
                         ('briefing_completed_at', 'TEXT')]:
        try:
            db.execute(f'ALTER TABLE matters ADD COLUMN {col} {typedef}')
        except Exception:
            pass
    db.execute('''CREATE TABLE IF NOT EXISTS matter_type_config (
        id TEXT PRIMARY KEY,
        practice_area TEXT NOT NULL,
        service_line TEXT,
        tier INTEGER DEFAULT 1,
        briefing_behaviour TEXT DEFAULT 'recommended',
        briefing_template_json TEXT,
        verification_enabled INTEGER DEFAULT 0,
        verification_max_loops INTEGER DEFAULT 2,
        verification_criteria_json TEXT,
        updated_at TEXT
    )''')
    existing = db.execute('SELECT COUNT(*) FROM matter_type_config').fetchone()[0]
    if existing == 0:
        now = datetime.now().isoformat()
        defaults = [
            ('mtc-001', 'Corporate', 'Company Formation', 1, 'recommended', now),
            ('mtc-002', 'Corporate', 'M&A', 1, 'recommended', now),
            ('mtc-003', 'Corporate', 'Shareholders', 1, 'recommended', now),
            ('mtc-004', 'Employment', 'Employment Contracts', 1, 'recommended', now),
            ('mtc-005', 'Employment', 'Settlement Agreements', 1, 'recommended', now),
            ('mtc-006', 'Dispute Resolution', 'Commercial Dispute', 1, 'recommended', now),
            ('mtc-007', 'Data Protection', 'GDPR Compliance Audit', 1, 'recommended', now),
            ('mtc-008', 'Commercial Property', 'Lease Review', 1, 'recommended', now),
        ]
        for row in defaults:
            db.execute('INSERT OR IGNORE INTO matter_type_config (id, practice_area, service_line, tier, briefing_behaviour, updated_at) VALUES (?,?,?,?,?,?)', row)

    # --- Verification tables (Sprint 3) ---
    db.execute('''CREATE TABLE IF NOT EXISTS verification_log (
        id TEXT PRIMARY KEY,
        matter_id TEXT REFERENCES matters(id),
        agent_id TEXT,
        loop_number INTEGER,
        passed INTEGER,
        checks_json TEXT,
        revision_prompt TEXT,
        created_at TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS verification_criteria (
        id TEXT PRIMARY KEY,
        practice_area TEXT NOT NULL,
        service_line TEXT,
        tier INTEGER DEFAULT 2,
        criterion TEXT NOT NULL,
        description TEXT,
        enabled INTEGER DEFAULT 1,
        updated_at TEXT
    )''')
    for col, typedef in [('sub_status', 'TEXT')]:
        try:
            db.execute(f'ALTER TABLE matters ADD COLUMN {col} {typedef}')
        except Exception:
            pass

    vc_count = db.execute('SELECT COUNT(*) FROM verification_criteria').fetchone()[0]
    if vc_count == 0:
        now = datetime.now().isoformat()
        vc_defaults = [
            ('vc-001', 'Contract Review', 'Reviewing', 2, 'Governing law and jurisdiction clause present', None),
            ('vc-002', 'Contract Review', 'Reviewing', 2, 'Termination rights identified and quantified', None),
            ('vc-003', 'Contract Review', 'Reviewing', 2, 'Limitation of liability cap discussed or justified', None),
            ('vc-004', 'Contract Review', 'Reviewing', 2, 'Payment and penalty clauses flagged', None),
            ('vc-005', 'Contract Review', 'Reviewing', 2, 'Exclusion clauses assessed under UCTA reasonableness test', None),
            ('vc-006', 'Contract Review', 'Reviewing', 2, 'Risk rating applied (RED/AMBER/GREEN)', None),
            ('vc-007', 'Contract Drafting', 'Drafting', 2, 'All required sections present (parties, definitions, obligations, payment, termination, liability, confidentiality, IP, force majeure, dispute resolution)', None),
            ('vc-008', 'Contract Drafting', 'Drafting', 2, 'Definitions section complete and consistent with usage', None),
            ('vc-009', 'Contract Drafting', 'Drafting', 2, 'Governing law and jurisdiction clause present', None),
            ('vc-010', 'Contract Drafting', 'Drafting', 2, 'No internal contradictions detected', None),
            ('vc-011', 'Contract Drafting', 'Drafting', 2, 'Risk allocation appropriate to matter tier', None),
            ('vc-012', 'Company Formation', 'Formation', 1, 'Articles of Association match selected structure', None),
            ('vc-013', 'Company Formation', 'Formation', 1, 'Director appointment details complete', None),
            ('vc-014', 'Company Formation', 'Formation', 1, 'Shareholder structure matches instructions', None),
            ('vc-015', 'Company Formation', 'Formation', 1, 'Companies House filing requirements identified', None),
            ('vc-016', 'Company Formation', 'Formation', 2, 'All Tier 1 criteria met', None),
            ('vc-017', 'Company Formation', 'Formation', 2, 'Shareholder agreement provisions complete', None),
            ('vc-018', 'Company Formation', 'Formation', 2, 'Pre-emption rights included', None),
            ('vc-019', 'Company Formation', 'Formation', 2, 'Director duties documented', None),
            ('vc-020', 'Employment', 'Contracts', 2, 'IR35 status assessed and documented', None),
            ('vc-021', 'Employment', 'Contracts', 2, 'Restrictive covenants reasonable and enforceable', None),
            ('vc-022', 'Employment', 'Contracts', 2, 'Garden leave clause present if applicable', None),
            ('vc-023', 'Employment', 'Contracts', 2, 'Settlement agreement standard paragraphs included', None),
            ('vc-024', 'Employment', 'Tribunal Claim', 2, 'ACAS early conciliation reference obtained or exemption stated', None),
            ('vc-025', 'Employment', 'Tribunal Claim', 2, 'ET1 claim form content complete', None),
            ('vc-026', 'Employment', 'Tribunal Claim', 2, 'Respondent details correctly identified', None),
            ('vc-027', 'Employment', 'Tribunal Claim', 2, 'Compensation basis identified and quantified', None),
            ('vc-028', 'Employment', 'Tribunal Claim', 2, 'Discrimination/breach claims properly particularised', None),
        ]
        for row in vc_defaults:
            db.execute('INSERT OR IGNORE INTO verification_criteria (id, practice_area, service_line, tier, criterion, description, enabled, updated_at) VALUES (?,?,?,?,?,?,1,?)',
                       (row[0], row[1], row[2], row[3], row[4], row[5], now))

    db.commit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        init_briefing_schema(g.db)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

DEFAULT_FIRM_CONFIG = {
    'sra_number': 'PENDING', 'firm_name': 'Acme Dale Legal Services',
    'pi_insurer': 'PENDING', 'pi_policy': 'PENDING',
    'colp_name': 'PENDING', 'cofa_name': 'PENDING',
    'registered_address': 'PENDING',
    'complaints_email': 'complaints@acmedale.co.uk',
    'website_url': 'https://acmedale.co.uk',
    'pricing_url': 'https://acmedale.co.uk/pricing'
}

def get_firm_config():
    if FIRM_CONFIG.exists():
        try:
            with open(FIRM_CONFIG) as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_FIRM_CONFIG.copy()

def save_firm_config(cfg):
    with open(FIRM_CONFIG, 'w') as f:
        json.dump(cfg, f, indent=2)

STATUS_LABELS = {
    'prospect':'Prospect','conflict_check':'Conflict Check','kyc_pending':'KYC Pending',
    'aml_pending':'AML Pending','onboarding':'Onboarding','active':'Active',
    'in_progress':'In Progress','in_review':'In Review','on_hold':'On Hold',
    'completed':'Completed','closed':'Closed','intake':'Intake',
    'enquiry_received':'Enquiry Received','review_intent':'Pending Review',
    'matter_opened':'Matter Opened','drafting':'Drafting',
    'statement_letter_sent':'Statement Sent','closing_checklist':'Closing',
}
PHASE_LABELS = {'intake':'Intake','planning':'Planning','execution':'Execution','completion':'Completion','archive':'Archive'}

def status_class(s):
    m={'prospect':'status-amber','conflict_check':'status-blue','kyc_pending':'status-amber',
       'aml_pending':'status-amber','onboarding':'status-blue','active':'status-teal',
       'in_progress':'status-teal','in_review':'status-blue','on_hold':'status-muted',
       'completed':'status-teal','closed':'status-muted','intake':'status-amber'}
    return m.get(s,'status-muted')

def phase_class(p):
    m={'intake':'phase-intake','planning':'phase-setup','execution':'phase-active',
       'completion':'phase-closure','archive':'phase-archive'}
    return m.get(p,'phase-intake')

def hitl_class(s):
    m={'active':'hitl-active','resolved':'hitl-resolved','na':'hitl-na'}
    return m.get(s,'hitl-active')

HITL_LABELS={
    'active':'Human review required',
    'resolved':'Review complete',
    'na':'Auto-approved',
}
matter_status_class = status_class  # alias for dashboard template

def format_currency(n): return 'GBP' + str(round(n/100, 2)) if n else 'GBP0.00'

def format_datetime(s):
    if not s:
        return '-'
    try:
        if isinstance(s, datetime):
            return s.strftime('%d %b %Y %H:%M')
        dt = datetime.fromisoformat(s.replace('Z','+00:00'))
        return dt.strftime('%d %b %Y %H:%M')
    except Exception:
        return str(s)

def gen_ref(practice_area, created_at):
    prefix_map={'Corporate':'AC','Employment':'EM','Commercial':'CM',
                'Dispute Resolution':'DR','IP':'IP','Data Privacy':'DP',
                'Commercial Property':'CP','Financial Services':'FS'}
    prefix=prefix_map.get(practice_area,'AD')
    year=created_at[:4] if created_at else datetime.now().strftime('%Y')
    db=get_db()
    row=db.execute('SELECT COUNT(*) as n FROM matters WHERE practice_area=? AND ref LIKE ?',
                   (practice_area, prefix+'/'+year+'/%')).fetchone()
    n=(row['n'] if row else 0)+1
    return prefix+'/'+year+'/'+str(n).zfill(4)

def matter_compliance_score(db, matter_id):
    row=db.execute('SELECT * FROM compliance_checks WHERE matter_id=?',(matter_id,)).fetchone()
    if row:
        fields=['client_care_letter_sent','ai_disclosure_included','fee_estimate_provided',
                'sra_registration_disclosed','insurance_disclosed','complaints_procedure_included',
                'data_privacy_notice_attached','human_review_approved']
        passed=sum(1 for f in fields if row[f])
        return passed, len(fields)
    return 0,0

@app.context_processor
def inject_globals():
    return dict(STATUS_LABELS=STATUS_LABELS, status_class=status_class,
                PHASE_LABELS=PHASE_LABELS, phase_class=phase_class,
                format_datetime=format_datetime, format_currency=format_currency,
                matter_compliance_score=matter_compliance_score,
                matter_status_class=matter_status_class, hitl_class=hitl_class, HITL_LABELS=HITL_LABELS,
                format_briefing_summary=format_briefing_summary,
                db=get_db, cfg=get_firm_config())

app.context_processor(inject_globals)


@app.route('/health')
def health():
    return jsonify({'status':'ok','db':str(DB_PATH),'db_exists':DB_PATH.exists(),
                    'firm':get_firm_config()['firm_name'],'port':5050})

@app.route('/')
def dashboard():
    db = get_db()
    cfg = get_firm_config()
    intake_count=db.execute("SELECT COUNT(*) FROM matters WHERE phase='intake'").fetchone()[0]
    open_count=db.execute("SELECT COUNT(*) FROM matters WHERE phase NOT IN ('archive','closure')").fetchone()[0]
    active_count=open_count
    total_matters=db.execute('SELECT COUNT(*) FROM matters').fetchone()[0]
    in_review=db.execute("SELECT COUNT(*) FROM matters WHERE status='in_review'").fetchone()[0]
    passed=db.execute('SELECT COUNT(*) FROM compliance_checks WHERE all_checks_passed=1').fetchone()[0]
    compliance_pct=int(100*passed/total_matters) if total_matters else 0
    today=datetime.now().strftime('%Y-%m-%d')
    tokens_today=db.execute('SELECT COALESCE(SUM(tokens_used),0) FROM audit_log WHERE date(created_at)=?',(today,)).fetchone()[0]
    cost_today=db.execute('SELECT COALESCE(SUM(cost_usd),0) FROM audit_log WHERE date(created_at)=?',(today,)).fetchone()[0]
    recent=db.execute('SELECT al.*, m.ref, m.client_name FROM audit_log al LEFT JOIN matters m ON al.matter_id=m.id ORDER BY al.created_at DESC LIMIT 15').fetchall()
    active_matters=db.execute("SELECT * FROM matters WHERE phase NOT IN ('archive','closure') ORDER BY created_at DESC LIMIT 20").fetchall()
    compliance_scores={}
    for m in active_matters:
        pc,tc=matter_compliance_score(db,m['id'])
        compliance_scores[m['id']]=(pc,tc)
    return render_template('dashboard.html',cfg=cfg,open_count=open_count,intake_count=intake_count,
        active_count=active_count,in_review_count=in_review,review_count=in_review,
        tokens_today=tokens_today,cost_today=cost_today,recent=recent,active=active_matters,
        compliance_pct=compliance_pct,total_matters=total_matters,compliance_scores=compliance_scores,passed=passed)

@app.route('/matters')
def matters():
    db = get_db()
    cfg = get_firm_config()
    fs = request.args.get('status', '')
    fp = request.args.get('phase', '')
    fpa = request.args.get('practice_area', '')
    bf = request.args.get('briefing_filter', '')
    vf = request.args.get('verification_filter', '')
    q = 'SELECT * FROM matters WHERE 1=1'
    args = []
    if fs:
        q += ' AND status=?'
        args.append(fs)
    if fp:
        q += ' AND phase=?'
        args.append(fp)
    if fpa:
        q += ' AND practice_area=?'
        args.append(fpa)
    if bf == 'incomplete':
        q += " AND briefing_status IN ('pending', 'draft')"
    if vf == 'failed':
        q += " AND sub_status = 'verification_failed'"
    q+=' ORDER BY created_at DESC'
    all_matters=db.execute(q,args).fetchall()
    # Pre-fetch verification status for each matter
    verification_statuses = {}
    for m in all_matters:
        vlog = db.execute(
            'SELECT COUNT(*) as cnt, MAX(CAST(passed AS INTEGER)) as last_pass FROM verification_log WHERE matter_id = ?',
            (m['id'],)
        ).fetchone()
        if vlog and vlog['cnt'] > 0:
            verification_statuses[m['id']] = {
                'count': vlog['cnt'],
                'last_pass': bool(vlog['last_pass']) if vlog['last_pass'] is not None else None
            }
    pas=[r['practice_area'] for r in db.execute('SELECT DISTINCT practice_area FROM matters') if r['practice_area']]
    return render_template('matters.html',cfg=cfg,matters=all_matters,filter_status=fs,filter_phase=fp,filter_pa=fpa,
                           briefing_filter=bf,verification_filter=vf,practice_areas=pas,
                           verification_statuses=verification_statuses)

@app.route('/matters/gdrive')
def matters_gdrive():
    """Show Drive Documents — lists all matters with their Drive folders."""
    db = get_db()
    cfg = get_firm_config()
    fs = request.args.get('status', '')
    fp = request.args.get('phase', '')
    q = 'SELECT * FROM matters WHERE 1=1'
    args = []
    if fs:
        q += ' AND status=?'
        args.append(fs)
    if fp:
        q += ' AND phase=?'
        args.append(fp)
    q += ' ORDER BY updated_at DESC'
    matters_list = db.execute(q, args).fetchall()
    drive_info = {}
    for m in matters_list:
        mid = m['id']
        fid = m['drive_folder_id'] if m['drive_folder_id'] else None
        if fid:
            drive_info[mid] = {
                'folder_id': fid,
                'folder_url': f'https://drive.google.com/drive/folders/{fid}',
                'matter_url': f'/matter/{mid}/gdrive'
            }
        else:
            drive_info[mid] = {'folder_id': None, 'folder_url': '', 'matter_url': f'/matter/{mid}/gdrive'}
    return render_template('matters_gdrive.html', cfg=cfg, matters=matters_list,
                          drive_info=drive_info, filter_status=fs, filter_phase=fp)

@app.route('/matter/<matter_id>', methods=['GET','POST'])
def matter_detail(matter_id):
    db = get_db()
    cfg = get_firm_config()
    if request.method=='POST':
        action = request.form.get('action')
        notes = request.form.get('notes', '')
        reviewer = 'Tatum Bisley (via Legal OS)'
        now = datetime.now().isoformat()
        if action=='approve':
            matter=db.execute('SELECT * FROM matters WHERE id=?',(matter_id,)).fetchone()
            cp = matter['phase'] if matter else 'active'
            cs = matter['status'] if matter else 'in_progress'
            ns_map={'in_review':'in_progress','kyc_pending':'aml_pending','aml_pending':'onboarding','onboarding':'in_progress'}
            ns=ns_map.get(cs,'in_progress')
            if cs == 'onboarding' and cp == 'intake':
                cp = 'planning'
            db.execute('UPDATE matters SET status=?, phase=?, notes=?, updated_at=? WHERE id=?',(ns,cp,notes,now,matter_id))
            db.execute('UPDATE compliance_checklist SET human_review_approved=1, human_review_approved_by=?, human_review_approved_at=? WHERE matter_id=?',(reviewer,now,matter_id))
            flash('Approved.','success')
        elif action=='reject':
            db.execute("UPDATE matters SET phase='intake', status='prospect', notes=?, updated_at=? WHERE id=?",(f'REJECTED: {notes}',now,matter_id))
            flash('Returned to intake.','warning')
        elif action=='set_status':
            ns = request.form.get('new_status', '')
            np = request.form.get('new_phase', '')
            if ns:
                db.execute('UPDATE matters SET status=?, updated_at=? WHERE id=?', (ns, now, matter_id))
            if np:
                db.execute('UPDATE matters SET phase=?, updated_at=? WHERE id=?', (np, now, matter_id))
            flash('Status updated.','info')
        else:
            db.execute('UPDATE matters SET notes=?, updated_at=? WHERE id=?',(notes,now,matter_id))
            flash('Notes saved.','info')
        db.execute('INSERT INTO audit_log (id,matter_id,agent_id,action_type,detail,human_override,human_reviewer,created_at) VALUES (?,?,?,?,?,1,?,?)',
                   (str(uuid.uuid4()),matter_id,'AD-Review',f'matter_action:{action}',notes,reviewer,now))
        db.commit()
        return redirect(url_for('matter_detail',matter_id=matter_id))
    matter=db.execute('SELECT * FROM matters WHERE id=?',(matter_id,)).fetchone()
    if not matter:
        flash('Matter not found.', 'error')
        return redirect(url_for('matters'))
    matter = dict(matter)
    audit=db.execute('SELECT * FROM audit_log WHERE matter_id=? ORDER BY created_at ASC',(matter_id,)).fetchall()
    checklist=db.execute('SELECT * FROM compliance_checklist WHERE matter_id=?',(matter_id,)).fetchone()
    compliance_chk=db.execute('SELECT * FROM compliance_checks WHERE matter_id=?',(matter_id,)).fetchone()
    conflict=db.execute('SELECT * FROM conflict_log WHERE matter_id=? ORDER BY created_at ASC',(matter_id,)).fetchall()
    total_tokens=sum(a['tokens_used'] or 0 for a in audit)
    total_cost=sum(a['cost_usd'] or 0 for a in audit)
    # Get or create Drive folder URL for the matter
    drive_folder_url = ''
    if matter.get('drive_folder_id'):
        drive_folder_url = f"https://drive.google.com/drive/folders/{matter['drive_folder_id']}"
    else:
        fid, link = get_or_create_matter_folder(dict(matter))
        if fid:
            db.execute('UPDATE matters SET drive_folder_id=? WHERE id=?', (fid, matter_id))
            db.commit()
            matter = dict(db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone())
            drive_folder_url = f"https://drive.google.com/drive/folders/{fid}"

    # Verification status
    vlog = db.execute(
        'SELECT COUNT(*) as cnt, MAX(CAST(passed AS INTEGER)) as last_pass FROM verification_log WHERE matter_id = ?',
        (matter_id,)
    ).fetchone()
    verification_status = None
    if vlog and vlog['cnt'] > 0:
        verification_status = {
            'count': vlog['cnt'],
            'last_pass': bool(vlog['last_pass']) if vlog['last_pass'] is not None else None
        }

    return render_template('matter_detail.html',cfg=cfg,matter=matter,audit=audit,checklist=checklist,
        compliance_checks=compliance_chk,conflict=conflict,total_tokens=total_tokens,total_cost=total_cost,
        flash=flash,drive_folder_url=drive_folder_url,verification_status=verification_status)

@app.route('/matter/<id>')
def matter_by_id(id): return redirect(url_for('matter_detail',matter_id=id))

@app.route('/matter/<matter_id>/gdrive')
def matter_gdrive(matter_id):
    db = get_db()
    cfg = get_firm_config()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    if not matter:
        flash('Matter not found.', 'error')
        return redirect(url_for('matters'))
    matter = dict(matter)

    # Get or create Drive folder URL
    drive_folder_url = ''
    if matter.get('drive_folder_id'):
        drive_folder_url = f"https://drive.google.com/drive/folders/{matter['drive_folder_id']}"
    else:
        fid, link = get_or_create_matter_folder(matter)
        if fid:
            db.execute('UPDATE matters SET drive_folder_id=? WHERE id=?', (fid, matter_id))
            db.commit()
            matter['drive_folder_id'] = fid
            drive_folder_url = f"https://drive.google.com/drive/folders/{fid}"

    return render_template('matter_gdrive.html', cfg=cfg, matter=matter,
                           drive_folder_url=drive_folder_url)

@app.route('/audit')
def audit():
    db = get_db()
    cfg = get_firm_config()
    fa = request.args.get('agent', '')
    fat = request.args.get('action_type', '')
    fm = request.args.get('matter_id', '')
    q = 'SELECT al.*, m.ref, m.client_name FROM audit_log al LEFT JOIN matters m ON al.matter_id=m.id WHERE 1=1'
    args = []
    if fa:
        q += ' AND al.agent_id=?'
        args.append(fa)
    if fat:
        q += ' AND al.action_type=?'
        args.append(fat)
    if fm:
        q += ' AND al.matter_id=?'
        args.append(fm)
    q+=' ORDER BY al.created_at DESC LIMIT 500'
    entries=db.execute(q,args).fetchall()
    agents=[r['agent_id'] for r in db.execute('SELECT DISTINCT agent_id FROM audit_log')]
    action_types=[r['action_type'] for r in db.execute('SELECT DISTINCT action_type FROM audit_log')]
    return render_template('audit.html',cfg=cfg,entries=entries,agents=agents,action_types=action_types,filter_agent=fa,filter_action=fat,filter_matter=fm)

@app.route('/audit/export')
def audit_export():
    db=get_db()
    entries=db.execute('SELECT al.*, m.ref, m.client_name FROM audit_log al LEFT JOIN matters m ON al.matter_id=m.id ORDER BY al.created_at DESC').fetchall()
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['Time','Ref','Client','Agent','Action','Detail','Tokens','Cost USD','Model','Confidence','Human Override','Reviewer'])
    for e in entries:
        w.writerow([e['created_at'],e['ref'],e['client_name'],e['agent_id'],e['action_type'],e['detail'],e['tokens_used'],e['cost_usd'],e['model_used'],e['confidence_score'],e['human_override'],e['human_reviewer']])
    return send_file(io.BytesIO(si.getvalue().encode()),mimetype='text/csv',as_attachment=True,download_name='audit_log_'+datetime.now().strftime('%Y%m%d')+'.csv')

@app.route('/agents')
def agents():
    cfg = get_firm_config()
    db = get_db()
    ws=[('AD-Intake', str(Path.home() / '.openclaw' / 'workspace-ad-intake')),
        ('AD-Review', str(Path.home() / '.openclaw' / 'workspace-ad-review')),
        ('AD-Corporate', str(Path.home() / '.openclaw' / 'workspace-ad-corporate')),
        ('AD-Drafting', str(Path.home() / '.openclaw' / 'workspace-ad-drafting')),
        ('AD-Research', str(Path.home() / '.openclaw' / 'workspace-ad-research')),
        ('AD-Verify', str(Path(__file__).parent))]
    agent_list=[]
    for name,wp in ws:
        sp=Path(wp)/'SOUL.md'
        soul=sp.read_text() if sp.exists() else ''
        wc=len(soul.split())
        la=db.execute('SELECT MAX(updated_at) FROM matters WHERE id IN (SELECT matter_id FROM audit_log WHERE agent_id=?)',(name,)).fetchone()[0]
        at=db.execute('SELECT COUNT(*) FROM matters WHERE phase NOT IN ("archive","closure") AND id IN (SELECT matter_id FROM audit_log WHERE agent_id=?)',(name,)).fetchone()[0]
        agent_list.append({'name':name,'soul_path':str(sp),'soul':soul,'word_count':wc,'last_active':format_datetime(la) if la else 'Never','active_tasks':at})
    return render_template('agents.html',cfg=cfg,agents=agent_list)



@app.route('/skills', methods=['GET','POST'])
def skills():
    cfg = get_firm_config()
    db = get_db()
    now = datetime.now().isoformat()
    if db.execute('SELECT COUNT(*) FROM legal_skills').fetchone()[0]==0:
        defaults=[('sk-001','Corporate','Company Formation [draft]','Standard new limited company incorporation.','New client enquiry','[]',1,now,'General','All','Drafting','company-formation'),
                  ('sk-002','Corporate','M+A Due Diligence [draft]','Due diligence for acquisitions.','Client proposes acquisition','[]',0,now,'General','Tier 2','Due Diligence','ma-due-diligence')]
        for s in defaults:
            db.execute('INSERT OR IGNORE INTO legal_skills (id,practice_area,name,description,trigger,steps,automated,created_at,matter_type,tier,service_line,slug) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',s)
        db.commit()
    if request.method=='POST':
        sid=request.form.get('skill_id')
        if sid:
            db.execute('UPDATE legal_skills SET name=?, description=?, trigger=?, steps=? WHERE id=?',
                       (request.form.get('name',''),request.form.get('description',''),request.form.get('trigger',''),request.form.get('steps',''),sid))
            db.commit()
            flash('Skill updated.','success')
            return redirect(url_for('skills'))
    all_skills=db.execute('SELECT * FROM legal_skills ORDER BY practice_area, name').fetchall()
    pas=sorted(set(r['practice_area'] for r in all_skills if r['practice_area']))
    import json as _json
    sba={}
    for pa in pas:
        sba[pa]=[]
        for s in all_skills:
            if s['practice_area']==pa:
                d=dict(s)
                try:
                    d['steps_list'] = _json.loads(d['steps']) if d['steps'] else []
                except Exception:
                    d['steps_list'] = []
                sba[pa].append(d)
    return render_template('skills.html',cfg=cfg,skills_by_area=sba,practice_areas=pas,flash=flash)

def parse_skill_file(slug):
    """Read and parse a skill's SKILL.md into sections."""
    import re
    base = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.join(base, 'skills', slug)
    md_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(md_path):
        return '', []
    with open(md_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    sections = []
    parts = re.split(r'(?m)^## ', raw)
    for part in parts[1:]:
        lines = part.split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if title:
            sections.append({'title': title, 'body': body})
    return raw, sections

@app.route('/skills/<slug>')
def skill_detail(slug):
    cfg = get_firm_config()
    db = get_db()
    skill=db.execute('SELECT * FROM legal_skills WHERE slug=?',(slug,)).fetchone()
    if not skill:
        skill = db.execute('SELECT * FROM legal_skills WHERE id=?', (slug,)).fetchone()
    if not skill:
        flash('Skill not found.', 'error')
        return redirect(url_for('skills'))
    ss_rows=db.execute('SELECT ss.* FROM skill_steps ss JOIN legal_skills ls ON ls.id=ss.skill_id WHERE ls.slug=? OR ls.id=? ORDER BY ss.step_order',(slug,slug)).fetchall()
    mts=[r['matter_type'] for r in db.execute('SELECT DISTINCT matter_type FROM matters WHERE matter_type IS NOT NULL') if r['matter_type']]
    skill_file, skill_file_sections = parse_skill_file(slug)
    return render_template('skill_detail.html',cfg=cfg,skill=dict(skill),skill_file_sections=skill_file_sections,
        steps=[dict(r) for r in ss_rows],steps_html='',skill_file=skill_file,matter_types=mts,
        STATUS_LABELS=STATUS_LABELS,status_class=status_class,format_datetime=format_datetime)

@app.route('/intake', methods=['GET','POST'])
def intake():
    cfg = get_firm_config()
    db = get_db()
    if request.method=='POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        mt = request.form.get('matter_type', '').strip()
        desc = request.form.get('description', '').strip()
        rs = request.form.get('referral_source', '').strip()
        if not name or not email or not mt or not desc:
            return render_template('intake.html',cfg=cfg,error='Please fill in all required fields.')
        now_str = datetime.now().isoformat()
        mid = str(uuid.uuid4())
        ref = gen_ref(mt, now_str)
        db.execute('INSERT INTO matters (id,client_name,client_email,practice_area,matter_type,ref,phase,status,summary,notes,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   (mid,name,email,mt,mt,ref,'intake','prospect',desc[:500],rs,now_str,now_str))
        db.commit()
        return redirect(url_for('intake_success',client_name=name,ref=ref))
    return render_template('intake.html',cfg=cfg)

@app.route('/client_intake', methods=['GET','POST'])
def client_intake(): return redirect(url_for('intake'))

@app.route('/intake/success', methods=['GET','POST'])
def intake_success():
    cfg=get_firm_config()
    return render_template('intake_success.html',cfg=cfg,
        client_name=request.args.get('client_name',''),ref=request.args.get('ref',''))

@app.route('/precedents')
def precedents():
    cfg = get_firm_config()
    db = get_db()
    q = request.args.get('q', '').strip()
    paf = request.args.get('practice_area', '').strip()
    args = []
    conds = ['1=1']
    if q:
        conds.append('(p.ref LIKE ? OR m.client_name LIKE ? OR p.summary LIKE ? OR p.matter_type LIKE ?)')
        pat = '%' + q + '%'
        args.extend([pat] * 4)
    if paf:
        conds.append('p.practice_area = ?')
        args.append(paf)
    where=' AND '.join(conds)
    rows=db.execute('SELECT p.*, m.client_name, m.ref as matter_ref FROM precedents p LEFT JOIN matters m ON m.id=p.matter_id WHERE '+where+' ORDER BY p.completed_at DESC',args).fetchall()
    pas=[r['practice_area'] for r in db.execute('SELECT DISTINCT practice_area FROM precedents WHERE practice_area IS NOT NULL') if r['practice_area']]
    return render_template('precedents.html',cfg=cfg,precedents=[dict(r) for r in rows],search=q,pa_filter=paf,practice_areas=pas)

@app.route('/precedent_detail/<matter_id>')
def precedent_detail(matter_id):
    cfg = get_firm_config()
    db = get_db()
    p=db.execute('SELECT p.*, m.client_name, m.ref as matter_ref FROM precedents p LEFT JOIN matters m ON m.id=p.matter_id WHERE p.matter_id=?',(matter_id,)).fetchone()
    if not p:
        flash('Precedent not found.', 'error')
        return redirect(url_for('precedents'))
    return render_template('precedent_detail.html',cfg=cfg,precedent=dict(p))

# CRM routes
@app.route('/crm')
def crm_dashboard():
    cfg = get_firm_config()
    db = get_db()
    total_mrr=db.execute("SELECT COALESCE(SUM(mrr_value),0) FROM crm_company_products WHERE status='active'").fetchone()[0] or 0
    total_arr=db.execute("SELECT COALESCE(SUM(arr_value),0) FROM crm_company_products WHERE status='active'").fetchone()[0] or 0
    active_clients=db.execute("SELECT COUNT(DISTINCT company_id) FROM crm_company_products WHERE status='active'").fetchone()[0] or 0
    ra=db.execute("SELECT a.*, c.first_name||' '||COALESCE(c.last_name,'') AS contact_name, co.company_name FROM crm_activities a LEFT JOIN crm_contacts c ON c.id=a.contact_id LEFT JOIN crm_companies co ON co.id=a.company_id ORDER BY a.activity_date DESC LIMIT 10").fetchall()
    pl_rows=db.execute('SELECT * FROM crm_pipelines').fetchall()
    ps={}
    for r in pl_rows:
        s=r['stage']
        if s not in ps:
            ps[s] = 0
        ps[s]+=1
    pbs={}
    for s in ['enquiry','qualified','proposal','negotiation','converted','lost']:
        rows=[r for r in pl_rows if r['stage']==s]
        pbs[s]={'n':len(rows),'weighted':sum(r['estimated_value']*r['conversion_probability']//100 for r in rows)}
    pm={}
    for r in db.execute("SELECT p.category, SUM(cp.mrr_value) as total FROM crm_company_products cp JOIN crm_products p ON p.id=cp.product_id WHERE cp.status='active' GROUP BY p.category").fetchall():
        if r['category']:
            pm[r['category']] = r['total'] or 0
    segs=db.execute("SELECT market_segment, COUNT(*) as n FROM crm_companies WHERE status='active' GROUP BY market_segment").fetchall()
    return render_template('crm_dashboard.html',cfg=cfg,total_mrr=total_mrr,total_arr=total_arr,active_clients=active_clients,
        recent_activities=[dict(r) for r in ra],pipeline_stats=ps,pipeline_by_stage=pbs,product_mix=pm,
        segments=[dict(r) for r in segs],format_currency=format_currency,format_datetime=format_datetime)

@app.route('/crm/contacts')
def crm_contacts():
    cfg = get_firm_config()
    db = get_db()
    q = request.args.get('q', '').strip()
    sf = request.args.get('status', '').strip()
    rf = request.args.get('role', '').strip()
    args = []
    conds = ['1=1']
    if q:
        conds.append("(c.first_name LIKE ? OR c.last_name LIKE ? OR c.email LIKE ?)")
        pat = '%' + q + '%'
        args.extend([pat] * 3)
    if sf:
        conds.append('c.status = ?')
        args.append(sf)
    if rf:
        conds.append('c.role = ?')
        args.append(rf)
    where=' AND '.join(conds)
    contacts=db.execute('SELECT c.*, co.company_name FROM crm_contacts c LEFT JOIN crm_companies co ON co.id=c.company_id WHERE '+where+' ORDER BY c.created_at DESC',args).fetchall()
    return render_template('crm_contacts.html',cfg=cfg,contacts=[dict(r) for r in contacts],q=q,status_filter=sf,role_filter=rf,format_datetime=format_datetime)

@app.route('/crm/contacts/<contact_id>')
def crm_contact_detail(contact_id):
    cfg = get_firm_config()
    db = get_db()
    contact=db.execute('SELECT c.*, co.company_name FROM crm_contacts c LEFT JOIN crm_companies co ON co.id=c.company_id WHERE c.id=?',(contact_id,)).fetchone()
    if not contact:
        flash('Contact not found.', 'error')
        return redirect(url_for('crm_contacts'))
    acts=db.execute('SELECT a.*, co.company_name FROM crm_activities a LEFT JOIN crm_companies co ON co.id=a.company_id WHERE a.contact_id=? ORDER BY a.activity_date DESC',(contact_id,)).fetchall()
    cps=[]
    if contact['company_id']:
        cps=db.execute('SELECT cp.*, p.name as product_name, p.category FROM crm_company_products cp JOIN crm_products p ON p.id=cp.product_id WHERE cp.contact_id=? OR cp.company_id=?',(contact_id,contact['company_id'])).fetchall()
    pl=db.execute('SELECT pl.*, p.name as product_name FROM crm_pipelines pl LEFT JOIN crm_products p ON p.id=pl.product_id WHERE pl.contact_id=?',(contact_id,)).fetchall()
    company=None
    if contact['company_id']:
        row=db.execute('SELECT * FROM crm_companies WHERE id=?',(contact['company_id'],)).fetchone()
        company=dict(row) if row else None
    return render_template('crm_contact_detail.html',cfg=cfg,contact=dict(contact),company=company,
        activities=[dict(r) for r in acts],cps=[dict(r) for r in cps],pipelines=[dict(r) for r in pl],
        format_datetime=format_datetime,format_currency=format_currency)

@app.route('/crm/contacts/new', methods=['POST'])
def crm_new_contact():
    db = get_db()
    data = request.get_json() or {}
    if not data.get('first_name') or not data.get('email'):
        return jsonify({'error': 'First name and email required'}), 400
    now = datetime.now().isoformat()
    cid = str(uuid.uuid4())
    db.execute('INSERT INTO crm_contacts (id,company_id,first_name,last_name,email,phone,mobile,role,is_key_decision_maker,source,referred_by,status,marketing_consent,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
               (cid,data.get('company_id') or None,data.get('first_name','').strip(),data.get('last_name','').strip(),
                data.get('email','').strip(),data.get('phone','').strip(),data.get('mobile','').strip(),
                data.get('role','Other'),1 if data.get('is_key_decision_maker') else 0,
                data.get('source','inbound_email'),data.get('referred_by','').strip(),
                data.get('status','lead'),1 if data.get('marketing_consent') else 0,now,now))
    db.commit()
    return jsonify({'id': cid})

@app.route('/crm/companies')
def crm_companies():
    cfg = get_firm_config()
    db = get_db()
    q = request.args.get('q', '').strip()
    args = []
    conds = ['1=1']
    if q:
        conds.append('(company_name LIKE ? OR company_number LIKE ?)')
        pat = '%' + q + '%'
        args.extend([pat] * 2)
    where=' AND '.join(conds)
    companies=db.execute("SELECT c.*, (SELECT COUNT(*) FROM crm_contacts WHERE company_id=c.id) AS contact_count, (SELECT COUNT(*) FROM crm_company_products WHERE company_id=c.id AND status='active') AS active_products FROM crm_companies c WHERE "+where+" ORDER BY c.created_at DESC",args).fetchall()
    return render_template('crm_companies.html',cfg=cfg,companies=[dict(r) for r in companies],q=q,format_datetime=format_datetime)

@app.route('/crm/companies/<company_id>')
def crm_company_detail(company_id):
    cfg = get_firm_config()
    db = get_db()
    company=db.execute('SELECT * FROM crm_companies WHERE id=?',(company_id,)).fetchone()
    if not company:
        flash('Company not found.', 'error')
        return redirect(url_for('crm_companies'))
    dirs=db.execute('SELECT * FROM crm_directors WHERE company_id=?',(company_id,)).fetchall()
    contacts=db.execute('SELECT * FROM crm_contacts WHERE company_id=?',(company_id,)).fetchall()
    cps=db.execute('SELECT cp.*, p.name as product_name, p.category FROM crm_company_products cp JOIN crm_products p ON p.id=cp.product_id WHERE cp.company_id=?',(company_id,)).fetchall()
    pl=db.execute("SELECT pl.*, p.name as product_name, c.first_name||' '||COALESCE(c.last_name,'') AS contact_name FROM crm_pipelines pl LEFT JOIN crm_products p ON p.id=pl.product_id LEFT JOIN crm_contacts c ON c.id=pl.contact_id WHERE pl.company_id=?",(company_id,)).fetchall()
    matters=db.execute('SELECT * FROM matters WHERE client_id IN (SELECT id FROM clients WHERE company_name=?) ORDER BY created_at DESC',(company['company_name'],)).fetchall()
    return render_template('crm_company_detail.html',cfg=cfg,company=dict(company),directors=[dict(r) for r in dirs],
        contacts=[dict(r) for r in contacts],cps=[dict(r) for r in cps],pipelines=[dict(r) for r in pl],
        matters=[dict(r) for r in matters],format_datetime=format_datetime,format_currency=format_currency)

@app.route('/crm/companies/new', methods=['POST'])
def crm_new_company():
    db = get_db()
    data = request.get_json() or {}
    if not data.get('company_name'):
        return jsonify({'error': 'Company name required'}), 400
    now = datetime.now().isoformat()
    coid = str(uuid.uuid4())
    db.execute('INSERT INTO crm_companies (id,org_type,company_name,company_number,registered_address,size,industry,website,market_segment,status,source,notes,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
               (coid,data.get('org_type','law_firm'),data.get('company_name','').strip(),data.get('company_number','').strip(),
                data.get('registered_address','').strip(),data.get('size','small'),data.get('industry','').strip(),
                data.get('website','').strip(),data.get('market_segment','law_firm'),data.get('status','prospect'),
                data.get('source','inbound_email'),data.get('notes','').strip(),now,now))
    db.commit()
    return jsonify({'id': coid})

@app.route('/crm/pipeline')
def crm_pipeline():
    cfg = get_firm_config()
    db = get_db()
    stages=['enquiry','qualified','proposal','negotiation','converted','lost']
    rows=db.execute("SELECT pl.*, c.first_name||' '||COALESCE(c.last_name,'') AS contact_name, co.company_name, p.name AS product_name FROM crm_pipelines pl LEFT JOIN crm_contacts c ON c.id=pl.contact_id LEFT JOIN crm_companies co ON co.id=pl.company_id LEFT JOIN crm_products p ON p.id=pl.product_id").fetchall()
    pbs={s:[] for s in stages}
    for row in rows:
        s=row['stage'] or 'enquiry'
        if s in pbs:
            pbs[s].append(dict(row))
        else:
            pbs.setdefault(s, []).append(dict(row))
    tw=sum(r['estimated_value']*r['conversion_probability']//100 for r in rows)
    return render_template('crm_pipeline.html',cfg=cfg,stages=stages,pipeline_by_stage=pbs,total_weighted=tw,
        format_currency=format_currency,format_datetime=format_datetime)

@app.route('/crm/products')
def crm_products():
    cfg = get_firm_config()
    db = get_db()
    products=db.execute('SELECT * FROM crm_products ORDER BY name').fetchall()
    return render_template('crm_products.html',cfg=cfg,products=[dict(r) for r in products],format_currency=format_currency)

@app.route('/crm/products/new', methods=['POST'])
def crm_new_product():
    db = get_db()
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'Product name required'}), 400
    now = datetime.now().isoformat()
    pid = str(uuid.uuid4())
    slug=data.get('name','').lower().replace(' ','-').replace('/','-')[:60]
    db.execute('INSERT INTO crm_products (id,name,slug,description,category,delivery_type,tier_name,tier_price_monthly,tier_price_transaction,usage_limit_per_month,automation_ratio,practice_area,matter_type,target_client_size,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
               (pid,data.get('name','').strip(),slug,data.get('description','').strip(),data.get('category','automated'),
                data.get('delivery_type','per_transaction'),data.get('tier_name','').strip(),
                int(data.get('tier_price_monthly') or 0),int(data.get('tier_price_transaction') or 0),
                int(data.get('usage_limit_per_month') or 0),int(data.get('automation_ratio') or 100),
                data.get('practice_area','').strip(),'',data.get('target_client_size','small'),
                data.get('status','active'),now,now))
    db.commit()
    return jsonify({'id': pid})

@app.route('/crm/activities')
def crm_activities():
    cfg = get_firm_config()
    db = get_db()
    activities=db.execute("SELECT a.*, c.first_name||' '||COALESCE(c.last_name,'') AS contact_name, co.company_name FROM crm_activities a LEFT JOIN crm_contacts c ON c.id=a.contact_id LEFT JOIN crm_companies co ON co.id=a.company_id ORDER BY a.activity_date DESC LIMIT 100").fetchall()
    return render_template('crm_activities.html',cfg=cfg,activities=[dict(r) for r in activities],format_datetime=format_datetime)

@app.route('/compliance', methods=['GET','POST'])
def compliance():
    db = get_db()
    cfg = get_firm_config()
    if request.method=='POST':
        cfg.update({'sra_number':request.form.get('sra_number',''),'firm_name':request.form.get('firm_name',''),
                    'pi_insurer':request.form.get('pi_insurer',''),'pi_policy':request.form.get('pi_policy',''),
                    'colp_name':request.form.get('colp_name',''),'cofa_name':request.form.get('cofa_name',''),
                    'registered_address':request.form.get('registered_address',''),
                    'complaints_email':request.form.get('complaints_email',''),
                    'website_url':request.form.get('website_url',''),'pricing_url':request.form.get('pricing_url','')})
        save_firm_config(cfg)
        flash('Firm configuration saved.', 'success')
        return redirect(url_for('compliance'))
    total=db.execute('SELECT COUNT(*) FROM matters').fetchone()[0]
    pn=db.execute('SELECT COUNT(*) FROM compliance_checks WHERE all_checks_passed=1').fetchone()[0]
    po=db.execute('SELECT COUNT(*) FROM compliance_checklist WHERE all_checks_passed=1').fetchone()[0]
    passed=max(pn,po)
    cf=db.execute("SELECT COUNT(*) FROM conflict_log WHERE result='flagged'").fetchone()[0]
    pr=db.execute("SELECT COUNT(*) FROM matters WHERE status='in_review'").fetchone()[0]
    cl=db.execute('SELECT cl.*, m.ref FROM conflict_log cl LEFT JOIN matters m ON cl.matter_id=m.id ORDER BY cl.created_at DESC LIMIT 20').fetchall()
    ac=db.execute('SELECT agent_id, SUM(tokens_used) as tokens, SUM(cost_usd) as cost FROM audit_log GROUP BY agent_id ORDER BY cost DESC').fetchall()
    return render_template('compliance.html',cfg=cfg,total=total,passed=passed,conflict_flags=cf,
        pending_review=pr,conflict_log=[dict(r) for r in cl],agent_costs=[dict(r) for r in ac])

@app.route('/settings/<tab>', methods=['GET','POST'])
@app.route('/settings', methods=['GET','POST'], defaults={'tab':'firm'})
def settings(tab):
    db = get_db()
    cfg = get_firm_config()
    if request.method=='POST':
        at=request.form.get('tab',tab)
        if at=='practice_areas':
            n = request.form.get('name', '').strip()
            sl = request.form.get('slug', '').strip()
            de = request.form.get('description', '').strip()
            if n and sl:
                db.execute('INSERT OR REPLACE INTO practice_areas (id,name,slug,description) VALUES (?,?,?,?)', (str(uuid.uuid4()), n, sl, de))
                db.commit()
                flash("Practice area '" + n + "' saved.", 'success')
            return redirect(url_for('settings',tab='practice_areas'))
        elif at=='matter_types':
            n = request.form.get('name', '').strip()
            sl = request.form.get('slug', '').strip()
            pa = request.form.get('practice_area_slug', '').strip()
            fe = request.form.get('fee_estimate', '').strip()
            ae = request.form.get('ai_effort', 'medium').strip()
            dp = request.form.get('delivery_pattern', '').strip()
            if n and sl and pa:
                db.execute('INSERT OR REPLACE INTO matter_types (id,practice_area_slug,name,slug,ai_effort,delivery_pattern,fee_estimate) VALUES (?,?,?,?,?,?,?)', (str(uuid.uuid4()), pa, n, sl, ae, dp, fe))
                db.commit()
                flash("Matter type '" + n + "' saved.", 'success')
            return redirect(url_for('settings',tab='matter_types'))
    pas=db.execute('SELECT * FROM practice_areas ORDER BY name').fetchall()
    mts=db.execute('SELECT * FROM matter_types ORDER BY practice_area_slug, name').fetchall()
    return render_template('settings.html',cfg=cfg,tab=tab,practice_areas=pas,matter_types=mts,flash=flash)

@app.route('/seed', methods=['GET','POST'])
def seed():
    cfg = get_firm_config()
    db = get_db()
    _now_unused = datetime.now().isoformat()
    force = request.args.get('force') == 'true'
    confirmed = force or request.form.get('confirm_seed')
    if request.method == 'GET' and not force:
        cm = db.execute('SELECT COUNT(*) FROM matters').fetchone()[0]
        return render_template('seed_confirm.html', cfg=cfg, current_matters=cm)
    if request.method == 'POST' and not confirmed:
        cm = db.execute('SELECT COUNT(*) FROM matters').fetchone()[0]
        return render_template('seed_confirm.html', cfg=cfg, current_matters=cm)
    pas=[('pa-001','Corporate','corporate','Company law, M&A, shareholder matters'),('pa-002','Employment','employment','Employment contracts, tribunal claims, policies'),('pa-003','Dispute Resolution','dispute-resolution','Commercial disputes, litigation'),('pa-004','Commercial Property','commercial-property','Lease agreements, transactions'),('pa-005','Data Protection','data-protection','GDPR compliance, breach response')]
    for row in pas:
        db.execute('INSERT OR IGNORE INTO practice_areas (id,name,slug,description) VALUES (?,?,?,?)', row)
    mts=[('mt-001','corporate','Company Formation','company-formation','high','discrete','GBP500-800 + VAT'),('mt-002','corporate','M+A','mergers-acquisitions','medium','transactional','GBP2000-8000 + VAT'),('mt-003','corporate','Shareholders','shareholders','high','advisory','GBP800-1500 + VAT'),('mt-004','employment','Employment Contracts','employment-contracts','high','discrete','GBP400-700 + VAT'),('mt-005','employment','Settlement Agreements','settlement-agreements','high','discrete','GBP600-1200 + VAT'),('mt-006','dispute-resolution','Commercial Dispute','commercial-dispute','low','case','GBP3000-15000 + VAT'),('mt-007','data-protection','GDPR Compliance Audit','gdpr-audit','high','compliance','GBP1000-3000 + VAT'),('mt-008','commercial-property','Lease Review','lease-review','high','discrete','GBP500-1000 + VAT')]
    for row in mts:
        db.execute('INSERT OR IGNORE INTO matter_types (id,practice_area_slug,name,slug,ai_effort,delivery_pattern,fee_estimate) VALUES (?,?,?,?,?,?,?)', row)
    db.commit()
    return jsonify({'status': 'ok', 'message': 'Seed data loaded'})


# =============================================================================
# BRIEFING INTERVIEW ROUTES
# =============================================================================

@app.route('/matter/<matter_id>/briefing', methods=['GET'])
def matter_briefing(matter_id):
    db = get_db()
    cfg = get_firm_config()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    if not matter:
        flash('Matter not found.', 'error')
        return redirect(url_for('matters'))
    matter = dict(matter)
    questions = get_briefing_questions(matter.get('matter_type', ''))
    existing = {}
    if matter.get('briefing'):
        try:
            existing = json.loads(matter['briefing'])
        except (json.JSONDecodeError, TypeError):
            pass
    step = int(request.args.get('step', 1))
    per_step = 5
    total_steps = (len(questions) + per_step - 1) // per_step
    step = max(1, min(step, total_steps))
    return render_template('briefing_wizard.html', cfg=cfg, matter=matter,
        questions=questions, existing=existing, step=step, total_steps=total_steps,
        per_step=per_step)


@app.route('/matter/<matter_id>/briefing', methods=['POST'])
def matter_briefing_post(matter_id):
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    if not matter:
        flash('Matter not found.', 'error')
        return redirect(url_for('matters'))
    matter = dict(matter)
    action = request.form.get('action', 'save_draft')
    answers = {}
    for key, value in request.form.items():
        if key.startswith('q_'):
            answers[key[2:]] = value.strip()
    now = datetime.now().isoformat()
    briefing_json = json.dumps(answers)
    if action == 'confirm':
        summary_text = format_briefing_summary(answers)
        existing_notes = matter.get('notes') or ''
        updated_notes = (existing_notes + '\n\n---\n' + summary_text).strip() if existing_notes else summary_text
        db.execute('UPDATE matters SET briefing=?, briefing_status=?, briefing_completed_at=?, notes=?, updated_at=? WHERE id=?',
                   (briefing_json, 'complete', now, updated_notes, now, matter_id))
        db.execute('INSERT INTO audit_log (id,matter_id,agent_id,action_type,detail,human_override,human_reviewer,created_at) VALUES (?,?,?,?,?,1,?,?)',
                   (str(uuid.uuid4()), matter_id, 'AD-Intake', 'briefing_confirmed',
                    f'Briefing interview completed with {len(answers)} answers',
                    'Fee Earner (via Legal OS)', now))
        db.commit()
        flash('Briefing confirmed and saved.', 'success')
        return redirect(url_for('matter_detail', matter_id=matter_id))
    else:
        db.execute('UPDATE matters SET briefing=?, briefing_status=?, updated_at=? WHERE id=?',
                   (briefing_json, 'draft', now, matter_id))
        db.commit()
        flash('Briefing draft saved.', 'info')
        return redirect(url_for('matter_briefing', matter_id=matter_id))


# =============================================================================
# BRIEFING — API + Skip
# =============================================================================

@app.route('/api/matters/<matter_id>/briefing', methods=['GET'])
def api_matter_briefing(matter_id):
    db = get_db()
    matter = db.execute(
        "SELECT briefing, briefing_status FROM matters WHERE id = ?",
        (matter_id,)).fetchone()
    if not matter or not matter['briefing']:
        return jsonify({"error": "No briefing found"}), 404
    try:
        data = json.loads(matter['briefing'])
    except (json.JSONDecodeError, TypeError):
        return jsonify({"error": "Invalid briefing data"}), 500
    return jsonify({
        "matter_id": matter_id,
        "status": matter['briefing_status'],
        "briefing": data
    })


@app.route('/matter/<matter_id>/briefing/skip', methods=['POST'])
def matter_briefing_skip(matter_id):
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("A reason is required to skip briefing", "error")
        return redirect(url_for("matter_briefing", matter_id=matter_id))
    db = get_db()
    now = datetime.now().isoformat()
    db.execute(
        "UPDATE matters SET briefing_status = 'skipped', briefing = ?, updated_at = ? WHERE id = ?",
        (json.dumps({"_skip_reason": reason}), now, matter_id))
    db.execute(
        "INSERT INTO audit_log (id, matter_id, agent_id, action_type, detail, human_override, human_reviewer, created_at) "
        "VALUES (?, ?, 'AD-Intake', 'briefing_skipped', ?, 1, 'Fee Earner (via Legal OS)', ?)",
        (str(uuid.uuid4()), matter_id, json.dumps({"reason": reason}), now))
    db.commit()
    flash("Briefing skipped", "info")
    return redirect(url_for("matter_detail", matter_id=matter_id))


# =============================================================================
# VERIFICATION LOOP ROUTES (Sprint 3)
# =============================================================================

@app.route('/matter/<matter_id>/verification-log')
def matter_verification_log(matter_id):
    db = get_db()
    cfg = get_firm_config()
    matter = db.execute('SELECT * FROM matters WHERE id = ?', (matter_id,)).fetchone()
    if not matter:
        flash('Matter not found', 'error')
        return redirect(url_for('matters'))
    logs = db.execute(
        'SELECT * FROM verification_log WHERE matter_id = ? ORDER BY loop_number ASC, created_at DESC',
        (matter_id,)
    ).fetchall()
    max_loops = 2
    return render_template('verification_log.html', cfg=cfg, matter=matter, logs=logs, max_loops=max_loops)


@app.route('/matter/<matter_id>/verify', methods=['POST'])
def matter_run_verify(matter_id):
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id = ?', (matter_id,)).fetchone()
    if not matter:
        flash('Matter not found', 'error')
        return redirect(url_for('matters'))

    existing = db.execute(
        'SELECT COUNT(*) FROM verification_log WHERE matter_id = ?', (matter_id,)
    ).fetchone()[0]
    loop_number = existing + 1

    matter_dict = dict(matter)
    pa = matter_dict.get('practice_area', '') or ''
    mt = matter_dict.get('matter_type', '') or ''

    criteria_rows = db.execute(
        'SELECT * FROM verification_criteria WHERE practice_area = ? AND enabled = 1',
        (pa,)
    ).fetchall()
    if not criteria_rows:
        criteria_rows = db.execute(
            'SELECT * FROM verification_criteria WHERE practice_area = ? AND enabled = 1',
            (mt,)
        ).fetchall()

    if not criteria_rows:
        flash('No verification criteria found for practice area "' + pa + '"', 'error')
        return redirect(url_for('matter_detail', matter_id=matter_id))

    has_output = bool(matter_dict.get('notes') or matter_dict.get('summary'))

    checks = []
    all_passed = True
    for r in criteria_rows:
        check_passed = 1 if has_output else 0
        if not check_passed:
            all_passed = False
        checks.append({
            'criterion': r['criterion'],
            'passed': check_passed,
            'note': 'Output present — requires AD-Verify agent review' if has_output else 'No output found on matter'
        })

    passed = 1 if all_passed and has_output else 0

    revision_prompt = None
    if not passed:
        revision_prompt = 'No output found on this matter. Please produce the required document or analysis before this matter can proceed.' if not has_output else 'One or more verification checks failed. Review the checks and revise the output accordingly.'

    now = datetime.now().isoformat()
    db.execute(
        'INSERT INTO verification_log (id, matter_id, agent_id, loop_number, passed, checks_json, revision_prompt, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (str(uuid.uuid4()), matter_id, 'AD-Verify', loop_number, passed, json.dumps(checks), revision_prompt, now)
    )

    max_loops = 2
    if not passed and loop_number >= max_loops:
        db.execute('UPDATE matters SET sub_status = ? WHERE id = ?', ('verification_failed', matter_id))

    db.commit()

    if passed:
        flash('Verification passed — all checks OK', 'success')
    else:
        flash('Verification failed — ' + str(len([c for c in checks if not c['passed']])) + ' checks failed. Loop ' + str(loop_number) + '/' + str(max_loops), 'error')

    return redirect(url_for('matter_verification_log', matter_id=matter_id))


@app.route('/matter/<matter_id>/verification-clear', methods=['POST'])
def matter_verification_clear(matter_id):
    db = get_db()
    db.execute("UPDATE matters SET sub_status = NULL WHERE id = ?", (matter_id,))
    db.commit()
    flash('Verification failed status cleared.', 'success')
    return redirect(url_for('matter_detail', matter_id=matter_id))


# =============================================================================
# SETTINGS — Engagement / Briefing Configuration
# =============================================================================

@app.route('/settings/engagement', methods=['GET', 'POST'])
def settings_engagement():
    db = get_db()
    cfg = get_firm_config()
    if request.method == 'POST':
        form_tab = request.form.get('form_tab', 'briefing')
        if form_tab == 'briefing':
            for key in request.form:
                if key.startswith('behaviour_'):
                    config_id = key[len('behaviour_'):]
                    new_val = request.form[key]
                    db.execute(
                        'UPDATE matter_type_config SET briefing_behaviour = ?, updated_at = ? WHERE id = ?',
                        (new_val, datetime.now().isoformat(), config_id))
            db.commit()
            flash('Briefing configuration saved.', 'success')
        elif form_tab == 'verification_toggle':
            now = datetime.now().isoformat()
            for key in request.form:
                if key.startswith('vc_enabled_'):
                    vc_id = key[len('vc_enabled_'):]
                    db.execute('UPDATE verification_criteria SET enabled = 1, updated_at = ? WHERE id = ?', (now, vc_id))
            all_ids = [r['id'] for r in db.execute('SELECT id FROM verification_criteria').fetchall()]
            for vc_id in all_ids:
                if 'vc_enabled_' + vc_id not in request.form:
                    db.execute('UPDATE verification_criteria SET enabled = 0, updated_at = ? WHERE id = ?', (now, vc_id))
            db.commit()
            flash('Verification criteria updated.', 'success')
        elif form_tab == 'verification_add':
            pa = request.form.get('new_pa', '').strip()
            sl = request.form.get('new_sl', '').strip()
            tier = int(request.form.get('new_tier', 2))
            crit = request.form.get('new_criterion', '').strip()
            desc = request.form.get('new_description', '').strip()
            if pa and crit:
                now = datetime.now().isoformat()
                db.execute(
                    'INSERT INTO verification_criteria (id, practice_area, service_line, tier, criterion, description, enabled, updated_at) VALUES (?,?,?,?,?,?,1,?)',
                    (str(uuid.uuid4()), pa, sl or None, tier, crit, desc or None, now))
                db.commit()
                flash('Criterion added.', 'success')
            else:
                flash('Practice area and criterion text are required.', 'error')
        return redirect(url_for('settings_engagement'))
    rows = db.execute(
        'SELECT * FROM matter_type_config ORDER BY practice_area, service_line').fetchall()
    vc_rows = db.execute(
        'SELECT * FROM verification_criteria ORDER BY practice_area, tier, criterion').fetchall()
    vc_by_area = {}
    for r in vc_rows:
        pa = r['practice_area']
        if pa not in vc_by_area:
            vc_by_area[pa] = []
        vc_by_area[pa].append(dict(r))
    return render_template('settings_engagement.html', cfg=cfg, configs=[dict(r) for r in rows],
                           vc_by_area=vc_by_area)


# =============================================================================
# API ROUTES — AD Legal OS
# =============================================================================

# ---------- Skills API ----------

@app.route('/api/skills', methods=['GET'])
def api_skills_list():
    db = get_db()
    skills = db.execute('SELECT * FROM legal_skills ORDER BY practice_area, name').fetchall()
    return jsonify([dict(s) for s in skills])


@app.route('/api/skills/<slug>', methods=['GET'])
def api_skills_get(slug):
    db = get_db()
    skill = db.execute('SELECT * FROM legal_skills WHERE slug=?', (slug,)).fetchone()
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404
    return jsonify(dict(skill))


@app.route('/api/skills', methods=['POST'])
def api_skills_create():
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    db = get_db()
    sid = str(uuid.uuid4())
    slug_val = data.get('slug') or data['name'].lower().replace(' ', '-').replace('/', '-')[:60]
    db.execute(
        'INSERT INTO legal_skills (id, slug, name, description, trigger, steps, automated, matter_type, tier, service_line, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (sid, slug_val, data['name'], data.get('description', ''),
         data.get('trigger', ''), data.get('steps', ''),
         1 if data.get('automated') else 0,
         data.get('matter_type', 'General'),
         data.get('tier', 'All'),
         data.get('service_line', ''),
         datetime.now().isoformat()))
    db.commit()
    return jsonify({'id': sid, 'slug': slug_val}), 201


@app.route('/api/skills/<slug>', methods=['PUT'])
def api_skills_update(slug):
    data = request.get_json() or {}
    db = get_db()
    skill = db.execute('SELECT * FROM legal_skills WHERE slug=?', (slug,)).fetchone()
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404
    skill_dict = dict(skill)
    db.execute(
        'UPDATE legal_skills SET name=?, description=?, trigger=?, steps=?, automated=?, matter_type=?, tier=?, service_line=? WHERE slug=?',
        (data.get('name', skill_dict.get('name', skill['name'])),
         data.get('description', skill_dict.get('description', '')),
         data.get('trigger', skill_dict.get('trigger', '')),
         data.get('steps', skill_dict.get('steps', '')),
         1 if data.get('automated') else 0,
         data.get('matter_type', skill_dict.get('matter_type', 'General')),
         data.get('tier', skill_dict.get('tier', 'All')),
         data.get('service_line', skill_dict.get('service_line', '')),
         slug))
    db.commit()
    return jsonify({'status': 'ok'})


@app.route('/api/skills/<slug>/active', methods=['PATCH'])
def api_skills_toggle_active(slug):
    db = get_db()
    try:
        db.execute("ALTER TABLE legal_skills ADD COLUMN is_active INTEGER DEFAULT 1")
        db.commit()
    except Exception:
        pass
    skill = db.execute('SELECT * FROM legal_skills WHERE slug=?', (slug,)).fetchone()
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404
    current = dict(skill).get('is_active', 1)
    new_active = 0 if current else 1
    db.execute('UPDATE legal_skills SET is_active=? WHERE slug=?', (new_active, slug))
    db.commit()
    return jsonify({'is_active': new_active})


# ---------- Dashboard API ----------

@app.route('/api/deadlines', methods=['GET'])
def api_deadlines():
    import datetime as dt
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    future_dt = datetime.now() + dt.timedelta(days=30)
    future = future_dt.strftime('%Y-%m-%d')
    rows = db.execute(
        'SELECT d.*, m.ref, m.client_name FROM deadlines d LEFT JOIN matters m ON d.matter_id=m.id WHERE d.deadline_date BETWEEN ? AND ? AND (d.status IS NULL OR d.status != "completed") ORDER BY d.deadline_date ASC',
        (today, future)).fetchall()
    return jsonify([dict(r) for r in rows])


# ---------- Matter API ----------

@app.route('/api/matters/<matter_id>/documents', methods=['GET'])
def api_matter_documents(matter_id):
    db = get_db()
    db_docs = db.execute(
        'SELECT * FROM documents WHERE matter_id=? ORDER BY created_at DESC', (matter_id,)).fetchall()

    # Also fetch Drive documents and merge
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    drive_docs = []
    if matter:
        drive_docs, _ = get_matter_documents(dict(matter))

    # Build merged list — DB docs first, then Drive docs with a 'gdrive' flag
    result = []
    # Normalize DB docs
    for d in db_docs:
        doc = dict(d)
        doc['gdrive'] = False
        result.append(doc)
    # Normalize Drive docs to match the DB doc field schema used by the frontend table
    for gd in drive_docs:
        result.append({
            'id': gd['id'],
            'name': gd['name'],
            'doc_type': gd['type'],
        'created_at': gd['created_time'] or gd['modified_time'],
            'modified_at': gd['modified_time'],
            'size': gd['size'],
            'size_bytes': gd['size_bytes'],
            'uploaded_by': 'Google Drive',
            'version': 1,
            'drive_web_link': gd['web_view_link'],
            'gdrive': True,
            'is_drive': True,
            'source': gd.get('source', 'Upload'),
            'mime_type': gd.get('mime_type', ''),
        })

    return jsonify({'documents': result, 'count': len(result), 'gdrive_count': len(drive_docs)})


@app.route('/api/matters/<matter_id>/gdrive', methods=['GET'])
def api_matter_gdrive(matter_id):
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    if not matter:
        return jsonify({'error': 'Matter not found'}), 404

    docs, folder_url = get_matter_documents(dict(matter))

    # Update matter's drive_folder_id in DB for future use
    if docs:
        folder_id = docs[0]['drive_folder_id'] if docs else None
        if folder_id:
            db.execute('UPDATE matters SET drive_folder_id=? WHERE id=?', (folder_id, matter_id))
            db.commit()

    return jsonify({
        'folder_url': folder_url,
        'documents': docs,
        'count': len(docs)
    })


@app.route('/api/matters/<matter_id>/documents', methods=['POST'])
def api_matter_upload_document(matter_id):
    data = request.get_json() or {}
    fname = data.get('filename', 'uploaded_file')
    did = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO documents (id, matter_id, doc_type, name, mime_type, size, uploaded_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)',
        (did, matter_id, data.get('type', 'other'), fname,
         data.get('content_type', 'application/octet-stream'),
         data.get('size', 0), 'system', now, now))
    db.commit()
    return jsonify({'id': did, 'name': fname}), 201


@app.route('/api/matters/<matter_id>/documents/from-template', methods=['POST'])
def api_matter_document_from_template(matter_id):
    data = request.get_json() or {}
    tid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO documents (id, matter_id, doc_type, name, description, created_at, updated_at) VALUES (?,?,?,?,?,?,?)',
        (tid, matter_id, 'generated',
         data.get('template_name', 'Template Document'),
         data.get('description', 'Generated from template'), now, now))
    db.commit()
    return jsonify({'id': tid, 'status': 'draft'}), 201


@app.route('/api/matters/<matter_id>/drive-folder', methods=['POST'])
def api_matter_drive_folder(matter_id):
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    folder_name = f"{matter['ref']} - {matter['client_name']}" if matter else matter_id
    return jsonify({
        'folder_id': f'drive_{matter_id[:8]}',
        'folder_name': folder_name,
        'drive_web_link': f'https://drive.google.com/drive/folders/fake_{matter_id[:8]}',
        'status': 'created'
    })


@app.route('/api/matters/<matter_id>/communications', methods=['GET'])
def api_matter_communications(matter_id):
    db = get_db()
    comms = db.execute(
        'SELECT * FROM communications WHERE matter_id=? ORDER BY created_at DESC', (matter_id,)).fetchall()
    return jsonify([dict(c) for c in comms])


@app.route('/api/matters/<matter_id>/communications', methods=['POST'])
def api_matter_add_communication(matter_id):
    data = request.get_json() or {}
    cid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO communications (id, matter_id, action_type, direction, detail, agent_id, created_at) VALUES (?,?,?,?,?,?,?)',
        (cid, matter_id, data.get('action_type', 'email'),
         data.get('direction', 'outbound'),
         data.get('detail', ''),
         data.get('agent_id', 'system'), now))
    db.commit()
    return jsonify({'id': cid}), 201


@app.route('/api/matters/<matter_id>/time', methods=['GET'])
def api_matter_time(matter_id):
    db = get_db()
    entries = db.execute(
        'SELECT * FROM time_entries WHERE matter_id=? ORDER BY created_at DESC', (matter_id,)).fetchall()
    return jsonify([dict(e) for e in entries])


@app.route('/api/matters/<matter_id>/time', methods=['POST'])
def api_matter_add_time(matter_id):
    data = request.get_json() or {}
    tid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO time_entries (id, matter_id, description, duration_minutes, entry_date, billing_status, created_at) VALUES (?,?,?,?,?,?,?)',
        (tid, matter_id, data.get('description', ''),
         data.get('duration', 0),
         data.get('date', now[:10]),
         'unbilled', now))
    db.commit()
    return jsonify({'id': tid}), 201


@app.route('/api/matters/<matter_id>/disbursements', methods=['GET'])
def api_matter_disbursements(matter_id):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM disbursements WHERE matter_id=? ORDER BY created_at DESC', (matter_id,)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/matters/<matter_id>/disbursements', methods=['POST'])
def api_matter_add_disbursement(matter_id):
    data = request.get_json() or {}
    did = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO disbursements (id, matter_id, description, amount, disbursement_type, created_at) VALUES (?,?,?,?,?,?)',
        (did, matter_id, data.get('description', ''),
         data.get('amount', 0),
         data.get('type', 'general'), now))
    db.commit()
    return jsonify({'id': did}), 201


@app.route('/api/matters/<matter_id>/invoices', methods=['GET'])
def api_matter_invoices(matter_id):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM invoices WHERE matter_id=? ORDER BY created_at DESC', (matter_id,)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/matters/<matter_id>/invoices', methods=['POST'])
def api_matter_create_invoice(matter_id):
    data = request.get_json() or {}
    iid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    inv_num = f"INV-{datetime.now().strftime('%Y%m%d%H%M')}"
    db.execute(
        'INSERT INTO invoices (id, matter_id, client_name, client_email, invoice_number, status, total_amount, created_at) VALUES (?,?,?,?,?,?,?,?)',
        (iid, matter_id,
         matter['client_name'] if matter else '',
         matter['client_email'] if matter else '',
         inv_num, 'draft',
         data.get('total_amount', 0), now))
    db.commit()
    return jsonify({'id': iid, 'invoice_number': inv_num, 'status': 'draft'}), 201


@app.route('/api/matters/<matter_id>/research', methods=['POST'])
def api_matter_research(matter_id):
    data = request.get_json() or {}
    db = get_db()
    db.execute(
        'INSERT INTO communications (id, matter_id, action_type, direction, detail, agent_id, created_at) VALUES (?,?,?,?,?,?,?)',
        (str(uuid.uuid4()), matter_id, 'research',
         'internal',
         f"Research query: {data.get('query', 'No query provided')}",
         'system', datetime.now().isoformat()))
    db.commit()
    return jsonify({'status': 'research_requested', 'matter_id': matter_id})


@app.route('/api/matters/<matter_id>/deadlines', methods=['GET'])
def api_matter_deadlines(matter_id):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM deadlines WHERE matter_id=? ORDER BY deadline_date ASC', (matter_id,)).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/matters/<matter_id>/deadlines', methods=['POST'])
def api_matter_add_deadline(matter_id):
    data = request.get_json() or {}
    did = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db = get_db()
    db.execute(
        'INSERT INTO deadlines (id, matter_id, description, deadline_date, deadline_type, status, created_at) VALUES (?,?,?,?,?,?,?)',
        (did, matter_id, data.get('description', ''),
         data.get('deadline_date', ''),
         data.get('deadline_type', 'other'),
         'pending', now))
    db.commit()
    return jsonify({'id': did}), 201


@app.route('/api/matters/<matter_id>/conflict-check', methods=['POST'])
def api_matter_conflict_check(matter_id):
    db = get_db()
    matter = db.execute('SELECT * FROM matters WHERE id=?', (matter_id,)).fetchone()
    if not matter:
        return jsonify({'error': 'Matter not found'}), 404
    results = []
    client_name = dict(matter).get('client_name', '')
    if client_name:
        existing = db.execute(
            'SELECT id, ref, client_name FROM matters WHERE id!=? AND client_name LIKE ?',
            (matter_id, f'%{client_name[:10]}%')).fetchall()
        for e in existing:
            results.append({
                'type': 'client_name',
                'matter_ref': e['ref'],
                'client': e['client_name']
            })
    cid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    db.execute(
        'INSERT INTO conflict_log (id, matter_id, new_client_name, check_type, result, created_at) VALUES (?,?,?,?,?,?)',
        (cid, matter_id, client_name, 'internal',
         'clear' if not results else 'potential_conflict', now))
    db.commit()
    return jsonify({
        'status': 'clear' if not results else 'flagged',
        'conflicts': results
    })


@app.route('/api/matters/<matter_id>/conflict-resolve', methods=['POST'])
def api_matter_conflict_resolve(matter_id):
    data = request.get_json() or {}
    resolution = data.get('resolution', 'waived')
    db = get_db()
    db.execute(
        'UPDATE conflict_log SET resolution=? WHERE matter_id=?',
        (resolution, matter_id))
    db.commit()
    return jsonify({'status': 'resolved', 'resolution': resolution})


@app.route('/api/matters/<matter_id>/precedent', methods=['GET'])
def api_matter_precedent(matter_id):
    db = get_db()
    p = db.execute(
        'SELECT * FROM precedents WHERE matter_id=? ORDER BY completed_at DESC LIMIT 1', (matter_id,)).fetchone()
    if not p:
        return jsonify({'error': 'No precedent found'}), 404
    return jsonify(dict(p))


# ---------- Document API ----------

@app.route('/api/documents/<doc_id>/share', methods=['POST', 'PATCH'])
def api_document_share(doc_id):
    data = request.get_json() or {}
    share_method = data.get('method', 'email')
    recipient = data.get('recipient', '')
    db = get_db()
    db.execute(
        'UPDATE documents SET drive_web_link=? WHERE id=?',
        (f'{share_method}:{recipient}', doc_id))
    db.commit()
    return jsonify({'status': 'shared', 'method': share_method, 'recipient': recipient})


# ---------- CRM Pipeline API ----------

@app.route('/api/crm/pipeline/<pipeline_id>/stage', methods=['POST'])
def api_crm_pipeline_stage(pipeline_id):
    data = request.get_json() or {}
    new_stage = data.get('stage', '')
    if not new_stage:
        return jsonify({'error': 'Stage required'}), 400
    db = get_db()
    db.execute(
        'UPDATE crm_pipelines SET stage=?, updated_at=? WHERE id=?',
        (new_stage, datetime.now().isoformat(), pipeline_id))
    db.commit()
    return jsonify({'status': 'ok', 'stage': new_stage})


if __name__=='__main__':
    print('AD Legal OS starting on port 5050...')
    print('DB: '+str(DB_PATH))
    print('Firm: '+get_firm_config()['firm_name'])
    app.run(host='0.0.0.0', port=5050, debug=True)
