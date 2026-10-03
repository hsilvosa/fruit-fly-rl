import json
from types import SimpleNamespace
import numpy as np
import pytest
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.recordings.shutdown import finalize_session,run_application

@pytest.mark.parametrize('failure',[RuntimeError('window closed'),KeyboardInterrupt()])
def test_preview_failure_does_not_prevent_record_flush(tmp_path,failure):
    recorder=FlightRecorder(tmp_path/'runs',{})
    recorder.buffer=[{'step':np.int64(1),'reward':np.float32(.1)}]
    def capture():
        assert recorder.closed
        raise failure
    report=tmp_path/'demo.json'
    finalize_session(recorder,{'status':'closed'},capture,report)
    manifest=json.loads((recorder.path/'manifest.json').read_text())
    assert manifest['status']=='closed' and manifest['transition_count']==1
    assert 'preview_warning' in manifest['summary']
    assert json.loads(report.read_text())['status']=='closed'

def test_ctrl_c_is_clean_and_skips_graphics(capsys):
    calls=[]
    class App:
        env=SimpleNamespace(close=lambda:calls.append('env-close'))
        finished=False
        def run(self): raise KeyboardInterrupt()
        def finish(self,**kwargs):
            if self.finished: return
            assert kwargs=={'exit_reason':'ctrl-c','capture':False}
            self.finished=True;calls.append('save-records')
        def destroy(self): calls.append('destroy')
    run_application(App())
    assert calls==['save-records','env-close','destroy']
    assert 'Traceback' not in capsys.readouterr().out
