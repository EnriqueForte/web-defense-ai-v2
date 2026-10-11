"""Published narrative uses validated facts/advice, never free model prose."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence
from agents.structured_reporting import compose, render_markdown
from dashboard.services.structured_publication import publish

ID = 'a' * 32


def line(target):
    return f'192.0.2.1 - - [10/Oct/2026:12:00:00 +0000] "GET {target} HTTP/1.1" 200 1'


def payloads(prepared, pattern='sql_injection', state='requires_investigation'):
    detection = {'schema_version':'1', 'analysis_id':ID, 'candidates':[{
        'candidate_id':'c_1', 'pattern':pattern,
        'evidence_ids':[item.evidence_id for item in prepared.bundle.items],
        'reason':'Untrusted description: SUBSTRING was exploited'}]}
    classification = {'schema_version':'1', 'analysis_id':ID, 'classifications':[{
        'candidate_id':'c_1', 'severity':'low' if state=='probable_false_positive' else 'unknown',
        'state':state, 'reason':'Untrusted explanation'}]}
    narrative = {'schema_version':'1', 'analysis_id':ID,
        'summary':'SUBSTRING confirmed exploitation of the whole site',
        'recommendations':[{'candidate_id':'c_1','text':'Multiple requests containing SQL patterns'}]}
    return detection, classification, narrative


class GroundedNarrativeTests(TestCase):
    def test_valid_but_unsupported_model_prose_cannot_enter_published_narrative(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT'), ID)
        result, markdown=compose(prepared, *payloads(prepared), model='offline', prompt_version='test')
        self.assertEqual(result['narrative_source'],'python_validated_facts')
        self.assertEqual(result['narrative_policy_version'],'grounded-narrative-1')
        self.assertEqual(result['quality'],'semantic_evaluation_pending')
        self.assertNotIn('SUBSTRING',markdown)
        self.assertNotIn('confirmed exploitation',markdown)
        self.assertNotIn('Multiple requests',markdown)
        self.assertIn('Se clasificó 1 grupo',markdown)
        self.assertIn('SQLi: 1',markdown)
        self.assertIn('Requiere investigación: 1',markdown)
        self.assertIn('consultas parametrizadas',markdown)
        self.assertEqual(len(result['narrative']['recommendations']),1)

    def test_changing_model_prose_and_reasons_does_not_change_final_narrative(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT'), ID)
        detection, classification, narrative=payloads(prepared)
        first, _=compose(prepared,detection,classification,narrative,model='offline',prompt_version='test')
        narrative['summary']='Different invented detail'
        narrative['recommendations']=[]
        detection['candidates'][0]['reason']='Different unsupported candidate reason'
        classification['classifications'][0]['reason']='Different untrusted classification reason'
        second, _=compose(prepared,detection,classification,narrative,model='offline',prompt_version='test')
        self.assertEqual(first['narrative'],second['narrative'])

    def test_measures_follow_each_validated_pattern_including_uncertainty(self):
        cases=[('sql_injection',line('/?q=UNION+SELECT'),'consultas parametrizadas'),
               ('xss',line('/?q=%3Cscript%3Ex%3C/script%3E'),'codificación de salida'),
               ('path_traversal',line('/?file=../etc/passwd'),'directorio autorizado'),
               ('command_injection',line('/?host=x%3Bwhoami'),'lista permitida'),
               ('brute_force','\n'.join(line('/vulnerabilities/brute/?username=test&password=x') for _ in range(5)),
                'autenticación multifactor'),
               ('other','uninterpretable synthetic request','Verificar formato')]
        for pattern,text,measure in cases:
            with self.subTest(pattern=pattern):
                prepared=prepare_evidence(text, ID)
                result, _=compose(prepared,*payloads(prepared,pattern),model='offline',prompt_version='test')
                recommendation=result['narrative']['recommendations'][0]
                self.assertEqual(recommendation['candidate_id'],'c_1')
                self.assertIn(measure,recommendation['text'])
                self.assertIn('Correlacionar',recommendation['text'])

    def test_false_positive_keeps_low_state_and_requires_review_before_controls(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT'), ID)
        result, _=compose(prepared,*payloads(prepared,state='probable_false_positive'),model='offline',prompt_version='test')
        self.assertEqual(result['counts']['low'],1)
        self.assertIn('Posible falso positivo: 1',result['narrative']['summary'])
        self.assertIn('antes de cambiar controles',result['narrative']['recommendations'][0]['text'])

    def test_summary_preserves_scope_and_warns_about_partial_indicator_coverage(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT')+'\n'+line('/?q=%3Cscript%3Ex%3C/script%3E')+
                                  '\n'+line('/index.html'),ID,max_items=2)
        detection,classification,narrative=payloads(prepared)
        detection['candidates'][0]['evidence_ids']=[prepared.bundle.items[0].evidence_id]
        result, _=compose(prepared,detection,classification,narrative,model='offline',prompt_version='test')
        self.assertIn('2 líneas seleccionadas de 3; se omitieron 1',result['narrative']['summary'])
        self.assertIn('Queda 1 referencia de patrón observado',result['narrative']['summary'])
        self.assertEqual(len(result['findings']),1)
        self.assertEqual(len(result['narrative']['recommendations']),1)

    def test_original_narrative_contract_still_blocks_publication_and_keeps_pointer(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT'),ID)
        detection,classification,narrative=payloads(prepared)
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            publish(root,prepared,detection,classification,narrative,model='offline',prompt_version='test')
            before=(root/'current.json').read_bytes()
            for change in ({'summary':''},{'recommendations':[{'candidate_id':'c_foreign','text':'Use parameters'}]},
                           {'summary':'\ud800'}):
                with self.subTest(change=list(change)):
                    invalid=deepcopy(narrative); invalid.update(change)
                    with self.assertRaises(ContractError):
                        publish(root,prepared,detection,classification,invalid,model='offline',prompt_version='test')
                    self.assertEqual((root/'current.json').read_bytes(),before)

    def test_historical_narrative_is_not_rebuilt_or_rewritten_by_renderer(self):
        prepared=prepare_evidence(line('/?q=UNION+SELECT'),ID)
        result, _=compose(prepared,*payloads(prepared),model='offline',prompt_version='test')
        result['report_format_version']='structured-report-3'
        result['narrative_source']='llm_contract_validated_semantics_pending'
        result['narrative']=payloads(prepared)[2]
        before=json.dumps(result,sort_keys=True)
        self.assertIn('SUBSTRING',render_markdown(result))
        self.assertEqual(json.dumps(result,sort_keys=True),before)
