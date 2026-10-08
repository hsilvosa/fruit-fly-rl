import sys
import pytest
from fly_rl.cli import main


def test_scene_selection_dispatches_explicit_controller_without_training(monkeypatch):
    import fly_rl.visualization.viewer as viewer
    seen=[]
    monkeypatch.setattr(viewer,'run',lambda args:seen.append(args))
    monkeypatch.setattr(sys,'argv',['fly-rl','demo','--architecture-scene','apartment','--situation','1'])
    main()
    assert seen[0].controller=='observed-map'
    assert seen[0].architecture_scene=='apartment' and seen[0].situation==1


@pytest.mark.parametrize('extra',[['--situation','999'],['--checkpoint','runs/dense-policy.zip'],['--map-profile','maze']])
def test_incompatible_architecture_options_rejected_before_loading_brain(monkeypatch,extra):
    monkeypatch.setattr(sys,'argv',['fly-rl','demo','--architecture-scene','office-floor']+extra)
    with pytest.raises(SystemExit):main()
