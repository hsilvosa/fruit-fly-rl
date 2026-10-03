"""Close flight records before attempting optional graphics operations."""
import json
import signal
from pathlib import Path

def finalize_session(recorder,summary,capture_preview,report):
    if recorder is not None:
        recorder.close(summary)
    if capture_preview is not None:
        try:
            if capture_preview() is False:
                summary['preview_warning']='Preview was not updated; flight records were saved.'
        except (Exception,KeyboardInterrupt) as exc:
            summary['preview_warning']=f'Preview was not updated: {type(exc).__name__}: {exc}'
    if recorder is not None:
        recorder.update_summary(summary)
    report=Path(report);report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(summary,indent=2),encoding='utf8')

def run_application(app):
    previous_signal=None
    try:
        app.run()
    except KeyboardInterrupt:
        # A second Ctrl+C must not interrupt the small final buffered write.
        previous_signal=signal.signal(signal.SIGINT,signal.SIG_IGN)
        print('Closing the demo and saving flight records...',flush=True)
        app.finish(exit_reason='ctrl-c',capture=False)
    except Exception as exc:
        app.finish(str(exc));raise
    finally:
        try:
            app.finish()
        finally:
            try:
                app.env.close()
            finally:
                try: app.destroy()
                finally:
                    if previous_signal is not None: signal.signal(signal.SIGINT,previous_signal)
